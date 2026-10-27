---
name: supabase-safe
description: Supabase(로그인·DB·사진 저장)를 개인정보 안전하게 붙이는 방법 — 테이블 설계, RLS 정책 SQL, 비공개 버킷과 서명 URL, anon/service_role 키 구분, 기기 데이터의 서버 이전. 서버 저장·회원 로그인·여러 기기 동기화를 만들 때 사용한다.
---

# Supabase 안전하게 쓰기

## 언제 붙이나
기기 저장만으로 충분하면 붙이지 않는다(ADR-000-3). 붙이는 신호: 여러 기기에서 같은 데이터 / 여러 직원이 공동 사용 / 폰 분실 대비 백업 요구.

## 키 두 가지 (가장 중요)
| 키 | 공개 여부 | 넣는 곳 |
|----|----------|---------|
| anon (publishable) | 공개돼도 됨 — RLS 가 지켜 줌 | `js/config.js` |
| service_role | **절대 공개 금지** — RLS 를 무시함 | 서버(Edge Function) 환경변수·`.env` 에만. 훅이 코드 삽입을 막는다 |

## 테이블 설계 원칙
- 모든 테이블에 `owner_id uuid references auth.users not null default auth.uid()`.
- 삭제는 연쇄: `references members(id) on delete cascade`.
- 기기 ID 와 서버 ID 를 둘 다 보관(`local_id text`) → 이전·중복 방지.
- 시간은 `timestamptz`, 날짜 표시는 화면에서 한국 시간으로.

## RLS 정책 (테이블마다 이 4개)
```sql
alter table members enable row level security;
create policy "본인만 조회" on members for select using (owner_id = auth.uid());
create policy "본인만 추가" on members for insert with check (owner_id = auth.uid());
create policy "본인만 수정" on members for update using (owner_id = auth.uid());
create policy "본인만 삭제" on members for delete using (owner_id = auth.uid());
```
RLS 를 켜지 않은 테이블은 anon 키로 누구나 읽을 수 있다. 배포 전 `privacy-guard` 가 확인한다.

## 사진 저장 (Storage)
- 버킷은 **비공개(private)**. 경로는 `{owner_id}/{member_id}/{uuid}.jpg`.
- 버킷 정책: `(storage.foldername(name))[1] = auth.uid()::text` 로 본인 폴더만.
- 보여줄 때는 `createSignedUrl(path, 60)` — 60초 만료. 공개 URL 을 DB 에 저장하지 않는다.
- 업로드 전 `camera-photo` 스킬로 1600px 축소.

## 로그인
소셜 로그인·인증 메일·계정 삭제는 `login-account` 스킬, 유료 구독은 `play-subscription` 스킬.

## 더 큰 구조
- 기관(센터·병원) 여러 곳이 같이 쓰기·직원 권한 → `multi-org` 스킬 (처음부터 넣어야 싸다)
- 로그인 없는 손님 화면·QR·공유 링크 → `guest-link` 스킬
- 잠금 화면 알림 → `web-push` 스킬

## 운영 (출시 뒤)
- **일시정지 방지**: 무료 플랜은 7일 동안 접속이 없으면 프로젝트를 멈춘다 → GitHub Actions 로 매일 한 번 **공개(anon) 키로** 가벼운 조회(`/rest/v1/표?select=id&limit=1`, RLS 때문에 빈 결과). 비밀키는 쓰지 않는다.
- **고객 문의**: 국외 폼 서비스 대신 앱 서버 표에 받는다. 저장은 로그인 본인만·하루 N건 제한 함수(`security definer`)로, 앱은 읽지 못하고 운영자가 대시보드에서 본다. 보관 기간을 정해 `pg_cron` 으로 지운다. 로그인 안 됨·오프라인일 때만 메일 앱.
- **AI 기능**: AI API 키는 서버 함수 Secrets 에만, 앱은 함수를 부른다. 회원 이름·연락처는 보내지 않는다(측정값·임의 코드만).

## 기기 데이터 → 서버 이전 (첫 로그인 때)
1. IndexedDB 의 회원·측정·사진을 읽는다.
2. 회원 → 측정 → 사진 순서로 올리고, 성공한 것만 `synced: true` 표시.
3. 중단돼도 다시 실행하면 이어서 올라가게(멱등). 완료 전에는 기기 데이터를 지우지 않는다.

## 흔한 실수
- 공개 버킷에 사진 저장 → 주소만 알면 누구나 봄.
- `select *` 에 RLS 없음 → 모든 회원 노출.
- service_role 키를 "테스트니까" 브라우저에 넣음 → 훅이 막지만, 다른 경로로도 넣지 말 것.
- 삭제 시 Storage 파일을 안 지움 → DB 는 비었는데 사진은 남음. 삭제 함수에서 둘 다 지운다.

## 키를 어디에 두나
- `js/config.js`: `export const SUPABASE_URL = "https://xxx.supabase.co"; export const SUPABASE_ANON_KEY = "eyJ…";` — anon 키는 공개용이라 코드에 그대로 둔다(RLS 가 지킴). 훅도 anon 키는 막지 않는다.
- `.env`(gitignore): service_role 키처럼 비밀인 것만. 브라우저 앱은 이 파일을 읽지 못한다 — Edge Function·로컬 스크립트용.
