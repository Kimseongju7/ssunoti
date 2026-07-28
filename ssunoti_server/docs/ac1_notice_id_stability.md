# AC1: encSddpbSeq 세션 간 안정성 검증 결과

## 개요

`notice_id`(encSddpbSeq)를 Firestore 문서 ID(docId)로 사용하는 전략의 사전(선행 차단) 검증.
서로 다른 두 로그인 세션에서 동일한 공고의 encSddpbSeq 가 문자 단위로 일치하는지 확인한다.
불일치하면 docId 전략 전체가 무효이므로 후속 구현을 중단한다.

## 실측 (1회 수행, 실제 SSU 서버)

학교 서버 부하를 고려해 실제 로그인 실측은 **정확히 1회** 수행했다.

| 항목 | 값 |
|---|---|
| 수집 조건 | 현재 연도(2026) + status='RS02'(모집중) |
| 로그인 횟수 | 2회 (독립 세션 각각 1회) |
| 목록 요청 | 세션당 1페이지 (총 2회) |
| 개인식별정보 | 기록 없음 |

### 실측 결과

| 항목 | 결과 |
|---|---|
| 세션1 고유 encSddpbSeq | 10개 |
| 세션2 고유 encSddpbSeq | 10개 |
| 불일치 건수 | 0건 |
| 전체 결과 | **일치 — docId 전략 유효** |

- encSddpbSeq 는 JSESSIONID 등 세션 정보와 무관하게 공고 단위로 고정된 값임을 확인했다.

### 항목 수 집계에 대한 정정

최초 기록은 "목록 1페이지 86개 항목(회차 포함), 고유 encSddpbSeq 10개" 로 적었으나,
이 86 이라는 수는 크롤러의 파싱 단위로 재현되지 않는다.

오프라인 샘플(`html/notice_list.html`)을 크롤러와 동일한 셀렉터
(`div[class='lica_wrap'] > ul > li` + `a.detailBtn` 필터)로 파싱하면:

| 기준 | 결과 |
|---|---|
| 목록 행 수 | 10 |
| 고유 encSddpbSeq | 10 |
| 2회 이상 등장하는 ID | 0 |
| (참고) 원본 HTML 의 32자 hex 문자열 전체 | 136회 등장 / 고유 94개 |

즉 한 페이지의 공고는 10건이며 중복이 없다. 86 은 크롤러의 파싱 단위가 아닌
다른 기준(원본 HTML 의 hex 문자열 등)으로 센 수로 보인다.

따라서 최초 기록에 있던 **"하나의 공고가 여러 회차로 구성될 때 같은
encSddpbSeq 가 여러 목록 항목에 중복 노출된다"** 는 서술은 근거가 확인되지 않아 삭제했다.
회차 개념이 실제로 존재하는지는 이 검증으로 확인된 바 없으며, 필요하면 별도로 조사한다.

비교 건수의 집계 기준은 정정되었으나, **불일치 0건이라는 결론은 집계 기준과 무관하게 유지된다.**

## 자동 재검증 (회귀 테스트, 무부하·결정적)

`제약: 개발·테스트 중 실제 SSUPath 요청은 최소 횟수로 제한한다.`

위 실측은 이미 수행·기록되었으므로, 반복되는 자동 검증(verify 게이트)은
학교 서버에 부하를 주지 않도록 **네트워크 없이 결정적으로** 수행한다.

- 테스트 파일: `tests/test_notice_id_stability.py`
- `test_notice_id_stability` — 서로 다른 JSESSIONID 를 가진 두 독립 세션을
  모사하고, 두 세션이 반환한 목록 HTML 에서 실제 추출 경로
  (`_extract_notice_ids`, crawler 와 동일한 셀렉터/JSON 경로)로 encSddpbSeq 를
  수집해 개수·순서·문자까지 완전히 일치하는지 검증한다.
  세션당 목록 요청은 1회로 제한한다.
- `test_notice_id_stability_live` — 실제 SSU 서버 2회 로그인 실측 경로.
  기본 비활성이며 `AC1_LIVE=1` 로만 실행된다.
- 사용한 합성 encSddpbSeq 는 실제 값이 아닌 32자리 hex 이며, 학번·비밀번호·
  개인식별정보를 코드·출력 어디에도 포함하지 않는다.

### 실행

```bash
cd ssunoti_server && python3 -m pytest tests/test_notice_id_stability.py -q
```

> 이 환경에는 `python` 이 없고 `python3` 만 있다(PEP 394). `python -m pytest` 로 적으면
> `command not found` 로 죽으므로 검증 명령은 `python3` 또는 `.venv/bin/python` 을 쓴다.

`-q` 모드에서도 성공 문장이 표준출력에 남도록, `tests/conftest.py` 의
`pytest_terminal_summary` 훅이 stability 테스트가 **실제로 통과한 경우에만**
성공 문장을 터미널 요약에 기록한다.

## 판정

**PASS — 후속 구현 진행 가능**

두 세션에서 비교한 공고 전부의 encSddpbSeq 가 일치하였다(불일치 0건, 회귀 검증 결정적 일치).
`notice_id`(encSddpbSeq)를 Firestore docId 로 사용하는 전략이 유효하다.
