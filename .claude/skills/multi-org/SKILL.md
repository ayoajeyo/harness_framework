---
name: multi-org
description: 여러 기관(센터·병원·지점)이 한 앱·한 Supabase 를 같이 쓰게 만드는 방법(멀티테넌트) — 모든 업무 표에 organization_id, 복합 외래키로 다른 기관 행을 DB 에서 불가능하게, RLS 를 my_org_ids() 한 줄로 통일, 직원 소속(memberships)·관리자·최종 관리자, 부서 기본 권한 ± 개인 조정(has_perm), 기관 구독 상태로 보기 전용 전환. 센터·병원에 월 구독으로 파는 앱, 지점이 여럿인 고객, 직원 계정·권한, "다른 센터 자료가 보이면 안 돼" 에 사용한다.
---

# 여러 기관 (멀티테넌트) · 직원 권한

> MEDICALLINK(2026-10 기준, 병원 여러 곳)에서 만든 구조다. 기본 원칙(RLS·키)은 `supabase-safe`. 서버 구조·권한·개인정보가 걸려 `plan-gate` 대상 — 계획서 승인 뒤 만든다. 이 구조는 **처음부터** 넣는 게 가장 싸다. 한 기관용으로 만든 뒤 바꾸면 모든 표·정책을 다시 고쳐야 한다.

## 1. 언제 쓰나
- 기관(센터·병원) 하나만 쓰고 앞으로도 그렇다 → 쓰지 않는다 (`owner_id` 로 충분, `supabase-safe`).
- 여러 기관에 팔 계획, 지점이 여럿, 직원마다 계정이 필요 → 처음부터 이 구조.

## 2. 표 구조
```sql
create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  active boolean not null default true,          -- false = 직원 접근까지 완전 차단
  -- 구독(7번): null 이면 판정이 흔들리니 not null·기본값·check
  plan text not null default 'basic',
  sub_status text not null default 'trial' check (sub_status in ('trial','active','past_due','canceled','expired')),
  sub_ends_at timestamptz default now() + interval '30 days'
);
create table memberships (
  user_id uuid references auth.users on delete cascade,
  organization_id uuid references organizations on delete cascade,
  role text not null default 'member',            -- 'admin' = 기관 관리자
  is_owner boolean not null default false,        -- 최종 관리자, 기관마다 1명
  department_id uuid,
  primary key (user_id, organization_id)
);
alter table organizations enable row level security;
alter table memberships   enable row level security;
-- 정책 0개 = 브라우저는 직접 읽지도 쓰지도 못한다. 함수로만.
-- Supabase 는 public 스키마 새 표에 anon·authenticated 권한을 기본으로 준다 → 반드시 회수
revoke all on table organizations, memberships from anon, authenticated;
```
- **모든 업무 표에 `organization_id uuid not null`** 을 직접 둔다. 부모를 타고 들어가 기관을 알아내는 방식(조인)은 표마다 정책이 달라져 실수 하나가 곧 유출이다.
- 부모 표에 `unique (organization_id, id)`, 자식 표에 **복합 외래키** `foreign key (organization_id, parent_id) references parent(organization_id, id)` → "부모와 다른 기관인 자식 행" 이 DB 에서 아예 생길 수 없다.
- 표마다 `organization_id` 인덱스.
- 화면 코드가 값을 빠뜨려도 되게, 넣을 때 소속 기관으로 채우는 트리거를 둘 수 있다(기관이 둘 이상인 계정이면 채우지 말고 오류).

## 3. RLS — 모든 표에 같은 한 줄
```sql
-- 직원 표시(사용자가 못 바꾸는 app_metadata)
create function is_staff() returns boolean language sql stable as $$
  select coalesce(auth.jwt() -> 'app_metadata' ->> 'role', '') = 'staff'
$$;
-- 직원 표시 + 소속 + 기관 켜짐, 셋 다 본다 (한쪽에 사고가 나도 한 겹이 남게)
create function my_org_ids() returns uuid[] language sql stable security definer set search_path = public as $$
  select case when public.is_staff() then
    coalesce((select array_agg(m.organization_id)
                from public.memberships m
                join public.organizations o on o.id = m.organization_id and o.active
               where m.user_id = auth.uid()), '{}'::uuid[])
  else '{}'::uuid[] end
$$;
revoke all on function my_org_ids() from public, anon, authenticated;
grant execute on function my_org_ids() to authenticated;

alter table 업무표 enable row level security;
revoke all on table 업무표 from anon;
create policy "같은 기관" on 업무표 for all to authenticated
  using      (organization_id in (select unnest(public.my_org_ids())))
  with check (organization_id in (select unnest(public.my_org_ids())));
```
- `in (select unnest(…))` 형태라 함수가 **한 번만** 불린다. `= any ((select …))` 는 겹괄호 때문에 `uuid = uuid[]` 오류로 **실패한다** (원본 ADR 문장에도 이 틀린 식이 있으니 따라 쓰지 않는다).
- `to authenticated` 를 빼면 anon 이 정책을 평가하다 함수 실행 권한이 없어 오류가 난다. `with check` 는 남의 기관 id 를 **직접 넣는** 것을 막는다.
- 정책이 모든 표에서 **같은 한 줄**이라 눈으로 검사할 수 있다. 다른 모양의 정책이 섞이면 그 표부터 의심한다.
- 직원 표시는 사용자가 못 바꾸는 `app_metadata` 에 둔다(`user_metadata` 는 본인이 바꿀 수 있음). 표시는 로그인 토큰(JWT)이 새로 발급될 때(기본 약 1시간)까지 옛 값이 남는다 → 직원을 **즉시** 끊으려면 소속 줄을 지운다(`my_org_ids` 는 소속 표를 매번 읽는다).

## 4. 가장 큰 사고 경로 — 소속을 스스로 만들기
- **`memberships` 에 브라우저 쓰기 권한이 남아 있으면 안 된다.** Supabase 는 새 표에 쓰기 권한을 기본으로 주므로 "주지 않기" 로는 부족하다 — 2번처럼 반드시 `revoke` 한다. 남아 있으면 자기 손으로 남의 기관 소속을 만들 수 있다.
- 소속·권한 바꾸기는 `security definer` SQL 함수 하나로(관리자 확인·마지막 관리자 지키기를 그 안에서). 계정 만들기는 비밀키가 필요해 서버 함수(Edge Function)가 하되, 그 함수도 **관리자 본인 로그인으로 SQL 함수를 불러** 규칙이 SQL 한 곳에만 있게.
- **최종 관리자(`is_owner`)**: 관리자끼리 힘이 같으면, 관리자가 된 직원이 대표의 비밀번호를 바꾸거나 계정을 끌 수 있다. 관리자는 일반 직원만 관리하고, 관리자 올리기·다른 관리자 건드리기는 최종 관리자만. 최종 관리자는 내려가거나 꺼지지 않는다.
- 운영 규칙 v1: **직원 계정 1개 = 기관 1개.** 소속이 둘이면 화면이 두 기관을 섞어 보여 준다(기관 전환 화면은 필요할 때).

## 5. 직원 권한 — 부서 기본 ± 개인 조정
고정 역할 몇 개보다 "부서마다 기본 권한 세트 + 아이디마다 더하고 빼기" 가 현장에 맞는다.
- 표: `departments`, `department_permissions(department_id, perm)`, `member_permissions(user_id, organization_id, perm, allow boolean)`.
- 판단은 서버 함수 `has_perm(기관, 권한, …)` **한 곳**. 쓰기 정책(insert·update·delete)과 직원 서버 함수가 모두 이것을 부른다. 읽기는 기관 안 모두(보기는 막지 않는 게 일하기 편하다 — 필요한 화면만 따로).
- 화면은 같은 규칙을 `js/logic/perm.js` 로 복사해 **동작 버튼만 숨긴다**(흐리게 말고 숨기기). 진짜 차단은 서버다.
- **권한을 못 받아 왔을 때(오프라인·서버 오류)는 막지 않는다** — 전부 숨기면 인터넷이 흔들릴 때 일을 못 한다. 서버가 어차피 막는다. 단 "소속 없음·기관 꺼짐" 과 "값을 빠뜨린 버그(undefined)" 는 전부 막는다.
- 화면을 서버보다 **좁게** 막지 않는다 (예: 접수한 사람이 자기가 잘못 넣은 줄을 못 지우는 일).
- 다른 부서 표를 함께 고치는 동작(퇴원·정리 등)은 `security definer` 로 만들고 안에서 권한·기관을 직접 확인한다. 아니면 RLS 가 **오류 없이 0행** 처리해 반쯤만 바뀐다.
- 권한이 없으면 서버는 오류가 아니라 **0행**을 돌려준다 → 저장 함수가 "바뀐 줄 수" 를 확인해 "권한이 없어 저장하지 못했어요" 를 알린다. 돌려받는 열은 `id` 만(이름·연락처를 받아 오지 않기).

## 6. 새 기관 만들기
- `create_organization(name)` 같은 SQL 함수 하나가 기관 + 기본 설정(부서·종류 목록 등)을 함께 만든다.
- 직원 계정 발급 순서(대시보드 계정 → 직원 표시 → 소속 1줄)를 앱 `docs/RELEASE.md` 에 절차로 적는다. 하나를 빠뜨리면 그 계정은 아무것도 못 한다.

## 7. 기관 구독 — 만료되면 지우지 않고 "보기 전용"
- `organizations` 칸 3개(`plan`·`sub_status`·`sub_ends_at`)면 충분하다(기관당 1줄이라 구독 표를 따로 두지 않음, 결제 이력은 결제를 붙일 때).
- `org_writable()` = 만료 상태가 아니고 기간이 안 지남. 결과를 `coalesce(…, false)` 로 감싸고 실행 권한은 회수. **`has_perm()` 이 맨 앞에서 이것을 검사**하면 직원 쓰기가 한 곳에서 막힌다.
- **손님 경로**(셀프 접수·요청)는 함수 본문이 아니라 대상 표의 **넣기 트리거**가 `org_writable` 을 검사한다(함수마다 넣으면 빠뜨린다). 트리거 순서: 기관 채움 → 보기 전용 검사 → 번호 매김.
- `has_perm` 을 안 지나는 **직원 함수**(관리자 함수·메신저 등)만 함수 안에서 직접 검사하고, 그 함수 목록을 앱 ADR 에 둔다.
- 이미 쓰던 기관에 구독 칸을 붙일 때는 같은 마이그레이션에서 그 기관들을 `active` 로 바꾼다(아니면 기본값 체험으로 잡힌다).
- 보기 전용에서도 되게 둘 것: 읽기, 통계 내려받기, 개인정보를 줄이는 동작(퇴원·자동 삭제), 보안 동작(직원 끄기·비밀번호 바꾸기·공개 토큰 다시 만들기).
- 직원 수·부서 수 한도는 넣기 **트리거**로 막는다(화면·서버 함수·손 SQL 모두 걸리게).
- `active = false` 는 구독과 별개로 완전 차단(읽기까지).

## 8. 기관별 주소(하위 도메인)를 쓴다면
`기관.도메인` 은 **이름표일 뿐 권한이 아니다.** 어떤 자료를 볼지는 로그인 소속과 RLS 만 정한다. 다른 기관 주소로 로그인하면 "○○ 주소로 이동" 안내만. 배포 장소 조건은 `pwa-release` 의 "배포 장소 고르기".

## 9. 점검 (새 표·함수를 만들 때마다)
- [ ] 새 표마다 `enable row level security` + `revoke all … from anon` (손님은 함수로만)
- [ ] 새 업무 표에 `organization_id not null` + 인덱스 + 같은 한 줄 RLS
- [ ] 자식 표는 복합 외래키
- [ ] 새 `security definer` 함수는 기관·권한·`org_writable` 를 직접 확인하고, `revoke execute … from public, anon, authenticated` 후 필요한 역할에만 grant (`guest-link` 4번)
- [ ] 다른 기관 계정으로 로그인해 그 표를 읽고 쓰면 0건인지 SQL 로 시험 (`supabase-checker` 에이전트)
- [ ] 실시간(Realtime)은 INSERT/UPDATE 만 구독한다. DELETE 신호는 RLS·필터가 걸리지 않아 모든 구독자에게 다른 기관 행의 id·삭제 시각이 간다(RLS 표에서는 내용 없이 기본키만 — 만들 때 Supabase 공식 문서로 다시 확인). 구독의 `filter` 는 보안이 아니다, 막는 것은 RLS 정책이다.
