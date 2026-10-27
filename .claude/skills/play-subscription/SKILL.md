---
name: play-subscription
description: Google Play 앱(TWA)으로 올린 웹앱에서 월 구독 결제를 받는 방법 — Digital Goods API + PaymentRequest 결제, 서버 함수가 Google 에 직접 확인·구매 확정(3일 안 안 하면 자동 환불), 구독 1개 = 계정 1개, 구독 복원·자동 갱신 다시 확인, 앱 자체 무료 체험과 체험 중 구독(다음 결제일 미루기), 해지·계정 삭제 안내. 유료 기능·PRO·구독·결제·무료 체험을 만들거나 "결제가 안 돼요" 일 때 사용한다.
---

# Play 월 구독

> 바디샷(2026-10 기준)에서 실제로 출시해 본 방법이다. Google API 는 버전이 바뀌니(아래 "기한" 참고) 만들 때 공식 문서를 확인한다. 결제는 `plan-gate` 대상 — 계획서 승인 뒤 만든다.

## 1. 전체 흐름
```
[앱] getDigitalGoodsService("https://play.google.com/billing")
  → new PaymentRequest([{ supportedMethods: "https://play.google.com/billing", data: { sku } }]).show()
  → 받은 purchaseToken 을 서버 함수로
[서버 함수 play-verify] 로그인 확인 → Google Play 개발자 API 로 토큰 조회 → 구매 확정(acknowledge) → 구독 표에 저장
[앱] 결과로 PRO 열기 · resp.complete("success"|"fail")
```
- 구독 상태는 **계정 기준으로 서버 표**에 둔다. 그래야 웹에서 로그인해도 PRO 가 된다. 기기에는 마지막 확인 결과만 캐시.
- **결제 확인은 반드시 서버에서.** 앱이 받은 토큰을 그대로 믿으면 조작할 수 있다.

## 2. 준비 (사용자가 직접)
- Play Console 에 구독 상품(예: `앱_pro_monthly`)과 가격
- Google Cloud 서비스 계정 → Play Console 에서 권한 → JSON 키를 Supabase **Edge Functions → Secrets** 에 `GOOGLE_PLAY_SA_JSON` 으로 (저장소·채팅에 쓰지 않기)
- TWA 앱에 결제 권한(PWABuilder 에서 Play Billing 켜기) — 이게 없는 예전 AAB 에서는 `getDigitalGoodsService` 가 없다 (`pwa-release`)

## 3. 서버 함수 (`play-verify`) 핵심
- 서비스 계정 키로 JWT(RS256) 를 만들어 `oauth2.googleapis.com/token` 에서 접근 토큰을 받고, 1시간 캐시.
- 조회: `GET …/applications/{패키지}/purchases/subscriptionsv2/tokens/{token}`
  - 404·410·400 → 만료로 표시하고 `pro: false`
  - `lineItems` 에서 **우리 상품 ID** 인지 확인 (다른 상품 토큰 거절)
- PRO 로 보는 상태: `ACTIVE`, `IN_GRACE_PERIOD`(결제 재시도 중), `CANCELED`(해지했지만 기간 남음) — 그리고 만료일이 지금보다 뒤.
- **구매 확정**: `acknowledgementState` 가 `PENDING` 이고 `ACTIVE` 면 `:acknowledge` 호출. **3일 안에 안 하면 Google 이 자동 환불한다.**
- **구독 1개 = 계정 1개**: 같은 토큰이 다른 계정에 이미 있으면 409 "이 구독은 다른 계정에 연결돼 있어요".
- 토큰 없이 부르면 저장된 구독을 Google 에 **다시 확인**(자동 갱신·해지 반영).
- 토큰 길이 제한(예: 4096자), 오류는 한국어 문장, 로그에 이메일 없음.

## 4. 앱 쪽 함정
- **결제 창에 시간 제한을 걸지 않는다.** 사용자가 카드를 고르는 동안 시간이 지나 "결제 처리 중…" 에서 멈춘 사고가 있었다.
- 결제 실패 안내 끝에 원인 코드(`NotSupportedError` 등)를 짧게 붙인다 — 폰 화면 캡처만으로 원인을 찾을 수 있게.
- `AbortError` = 사용자가 결제 창을 닫음 → 아무 안내 없이 버튼만 되돌린다.
- 토큰을 못 받았거나 확인이 실패하면 "**구독 복원**" 으로 안내: `listPurchases()` 에서 우리 상품을 찾아 다시 서버 확인.
- 앱을 열 때: 서버 표에 구독이 없으면 Play 앱에서는 조용히 복원 시도. 만료가 하루 안으로 다가왔으면 Google 에 다시 확인(6시간에 한 번만).
- 만료 직후 갱신 확인 전까지 몇 시간 여유를 둬서, 갱신된 사람이 잠깐 잠기지 않게.
- 가격은 `getDetails([sku])` 의 값으로 표시 (코드에 가격을 박지 않기).
- 결제 기능이 없는 환경(웹 브라우저, 예전 앱)에서는 구독 버튼 대신 "Play 스토어 앱에서 구독할 수 있어요" 안내.

## 5. 무료 체험
- 앱 자체 체험(가입 후 N일)은 가입 시각 기준으로 계산한다. 기기 시간을 되돌리면 체험 종료로 처리(마지막으로 본 시각을 기억).
- **체험 중에 구독하면** 남은 체험일이 사라지는 문제 → 첫 결제는 그대로 받고, 서버가 처음 확인할 때 **한 번만** Play `defer` 로 다음 결제일을 남은 체험일만큼 미룬다.
  - 남은 체험 = 가입 시각 + N일 − 구독 시작 시각. 하루 미만이면 안 미룸. 구독 시작이 가입보다 앞서면(계정을 다시 만든 경우) 안 미룸.
  - **계정당 한 번**: Google 을 부르기 전에 표의 칸을 `null → -1`(진행 중)로 먼저 차지한다. 동시에 온 요청·저장 실패에도 두 번 미루지 않게. 실패하면 `null` 로 되돌려 다음에 다시 시도, 구독·PRO 는 그대로.
  - 계산은 `js/logic/` 처럼 순수 함수로 떼어 테스트를 먼저 쓴다(TDD).
- Play 의 무료 체험 혜택(offer)은 일수가 고정이고 웹앱 결제창에서 고르는 방법이 확인되지 않아 바디샷은 쓰지 않았다.
- **기한**: `purchases.subscriptions.defer`(v1)는 2028-08-31 종료 예고 → 그 전에 `subscriptionsv2.defer` 로 옮긴다.

## 6. 해지·환불·삭제 안내
- 해지는 **Play 스토어 → 구독** 에서 한다(앱에서 못 함). 앱에 "언제든 해지 가능" + 해지 방법 한 줄.
- 해지해도 남은 기간은 PRO (`CANCELED` + 만료일).
- 계정 삭제 화면·웹 삭제 안내에 "**구독은 계정을 지워도 자동 해지되지 않아요**" (`login-account` 4번).
- 이용약관에 요금·자동 결제·해지·환불(Play 정책 따름)을 적는다.

## 7. 서버 표 (예)
`subs(user_id pk, product_id, purchase_token unique, state, expires_at, auto_renew, trial_deferred_ms, updated_at)` — RLS: 본인 select 만, 쓰기는 서버 함수(관리자 키)만. 새 칸은 `docs/DATA.md` 에 먼저 (`data-migration`).

## 8. 출시 전 점검
- [ ] Play Console **라이선스 테스터** 계정으로 실제 결제 → PRO 열림 → 3일 뒤에도 환불 안 됨(구매 확정 확인)
- [ ] 결제 창 닫기 · 결제 실패 · 구독 복원 · 다른 계정으로 같은 구독
- [ ] 해지 후 남은 기간 PRO, 만료 뒤 잠김
- [ ] 웹 브라우저에서 열었을 때 구독 버튼 대신 안내
- [ ] 이용약관·개인정보처리방침·Play 데이터 보안 양식에 결제 정보 반영
