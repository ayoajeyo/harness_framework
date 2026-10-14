# 아키텍처

## 디렉토리 구조
```
{폴더 구조 (기본값은 mobile-webapp 스킬의 구조. 예:
index.html / manifest.json / sw.js
css/style.css
js/app.js, js/logic/
tests/
icons/)}
```

## 패턴
{사용하는 설계 방식 (예: 화면 코드(js/app.js)와 계산 로직(js/logic/)을 분리. 로직 파일은 화면을 모른다)}

## 데이터 흐름
```
{데이터가 어떻게 흐르는지 (예:
사진 촬영 → 기기(IndexedDB)에 저장 → 측정 계산(js/logic) → 화면 표시 → 리포트(A4) 출력
)}
```

## 저장소
| 데이터 | 저장 위치 | 민감 정보 여부 |
|--------|-----------|---------------|
| {예: 회원 정보} | {예: 기기 localStorage} | {예: 예 — 이름·연락처} |
| {예: 측정 사진} | {예: 기기 IndexedDB} | {예: 예 — 신체 사진} |
