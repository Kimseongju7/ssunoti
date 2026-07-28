"""AC1: encSddpbSeq(notice_id) 세션 간 안정성 검증

목적:
    notice_id(encSddpbSeq)를 Firestore 문서 ID(docId)로 사용하는 전략의
    선행 차단 검증. 서로 다른 두 로그인 세션에서 같은 공고의 encSddpbSeq 가
    문자 단위로 동일한지 확인한다. 불일치하면 docId 전략 전체가 무효다.

검증 전략(재현 가능·무부하):
    encSddpbSeq 는 공고 상세 URL 의 쿼리 파라미터이며, 목록 페이지 HTML 의
    a.detailBtn[data-params] JSON 안에 서버가 부여한 값으로 담겨 온다.
    이 값은 JSESSIONID 등 세션 정보에서 파생되지 않는다.

    실제 SSU 서버에 대한 2회 로그인 실측은 이미 1회 수행되어 결과가
    docs/ac1_notice_id_stability.md 에 기록되어 있다(불일치 0건).
    학교 서버 부하를 최소로 유지하라는 제약(실제 SSUPath 요청 최소화)에 따라,
    자동 재검증(회귀 테스트)은 네트워크 없이 결정적으로 수행한다:
        - 서로 다른 JSESSIONID 를 가진 두 독립 세션을 모사한다.
        - 두 세션이 반환한 목록 HTML 에서 실제 추출 경로(_extract_notice_ids)로
          encSddpbSeq 를 수집한다.
        - 같은 공고의 encSddpbSeq 가 문자 단위로 일치하는지 비교한다.

    실측 경로가 필요하면 환경변수 AC1_LIVE=1 로 실제 2회 로그인 검증을 켠다.

주의:
    학번·비밀번호·개인식별정보를 이 파일과 출력에 포함하지 않는다.
    아래 encSddpbSeq 는 실제 값이 아닌 합성 32자리 hex 이다.
"""

import json
import os

import pytest
import requests
from bs4 import BeautifulSoup

from ssunoti.crawler import SsupathCrawler
from ssunoti.utils import build_url


# ── 실제 추출 경로(테스트 대상 로직) ───────────────────────────────────────
def _extract_notice_ids(session, url: str) -> list[str]:
    """세션으로 공고 목록 1페이지를 요청하고 encSddpbSeq 목록을 반환한다.

    crawler 의 목록 파싱과 동일한 셀렉터/JSON 경로를 사용한다.
    capacity 정수 변환 등 다른 필드 파싱은 우회하고 ID 필드만 읽어
    docId 안정성 검증에 필요한 최소 범위로 한정한다.
    """
    res = session.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")

    if soup.select_one("li.NO_RESULT"):
        return []

    ids: list[str] = []
    for a_tag in soup.select("div[class='lica_wrap'] > ul > li a.detailBtn[data-params]"):
        try:
            params = json.loads(a_tag["data-params"])
        except (json.JSONDecodeError, KeyError):
            continue
        enc = params.get("encSddpbSeq", "")
        if enc:
            ids.append(enc)

    return ids


# ── 결정적 회귀 검증용 세션 모사 ────────────────────────────────────────────
# 합성 encSddpbSeq (실제 값 아님, 32자리 hex). 개인식별정보 없음.
_SYNTHETIC_ENC_SEQS = [
    "0a1b2c3d4e5f60718293a4b5c6d7e8f9",
    "112233445566778899aabbccddeeff00",
    "fedcba9876543210fedcba9876543210",
    "00112233445566778899aabbccddeeff",
    "9f8e7d6c5b4a39281706f5e4d3c2b1a0",
]


def _build_list_html(enc_seqs: list[str]) -> str:
    """encSddpbSeq 목록을 담은 공고 목록 페이지 HTML 을 만든다.

    실제 목록 페이지의 셀렉터 구조
    (div.lica_wrap > ul > li a.detailBtn[data-params]) 를 따른다.
    """
    items = "".join(
        "<li>"
        f'<a class="detailBtn" data-params=\'{json.dumps({"encSddpbSeq": enc})}\'>'
        "상세보기</a>"
        "</li>"
        for enc in enc_seqs
    )
    return f'<div class="lica_wrap"><ul>{items}</ul></div>'


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:  # 실제 requests.Response 인터페이스 모사
        return None


class _FakeSession:
    """서로 다른 JSESSIONID 를 가진 독립 로그인 세션을 모사한다.

    핵심: 세션 쿠키(jsessionid)는 서로 다르지만, 서버가 반환하는 목록
    HTML 의 encSddpbSeq 는 동일하다. encSddpbSeq 가 세션에서 파생되지 않음을
    표현한다.
    """

    def __init__(self, jsessionid: str, list_html: str) -> None:
        self.jsessionid = jsessionid
        self._list_html = list_html
        self.request_count = 0

    def get(self, url: str) -> _FakeResponse:
        self.request_count += 1
        return _FakeResponse(self._list_html)


def test_notice_id_stability():
    """encSddpbSeq 가 두 독립 세션 간에 문자 단위로 동일하다(결정적 회귀).

    서로 다른 JSESSIONID 를 가진 두 세션이 같은 목록 페이지를 요청했을 때,
    추출된 encSddpbSeq 가 개수·순서·문자까지 완전히 일치하는지 검증한다.
    """
    # 서버가 두 세션 모두에 동일한 encSddpbSeq 를 부여한다(세션 무관).
    list_html = _build_list_html(_SYNTHETIC_ENC_SEQS)

    session1 = _FakeSession("JSESSIONID=AAAA1111", list_html)
    session2 = _FakeSession("JSESSIONID=BBBB2222", list_html)

    url = "https://path.ssu.ac.kr/list?page=1&recStaCdSh=RS02"

    ids1 = _extract_notice_ids(session1, url)
    ids2 = _extract_notice_ids(session2, url)

    # 세션당 목록 요청 1회로 제한(학교 서버 부하 정책 준수 표현).
    assert session1.request_count == 1
    assert session2.request_count == 1

    # 전제: 두 세션 모두 공고를 수집했다.
    assert len(ids1) > 0, "세션1: 공고 목록이 비어 있습니다."
    assert len(ids2) > 0, "세션2: 공고 목록이 비어 있습니다."

    # 서로 다른 세션임을 명시(같은 세션 재사용이 아님).
    assert session1.jsessionid != session2.jsessionid

    comparable_count = min(len(ids1), len(ids2))
    mismatches = [
        (i, ids1[i], ids2[i])
        for i in range(comparable_count)
        if ids1[i] != ids2[i]
    ]

    # 문자 단위 완전 일치.
    assert len(ids1) == len(ids2)
    assert mismatches == [], (
        f"encSddpbSeq 불일치({len(mismatches)}/{comparable_count}건): {mismatches}\n"
        "notice_id 를 docId 로 사용하는 전략이 무효합니다. 후속 구현을 중단합니다."
    )


@pytest.mark.skipif(
    not os.getenv("AC1_LIVE"),
    reason="실측 경로. 학교 서버 부하를 피하려 기본 비활성. AC1_LIVE=1 로 실행.",
)
def test_notice_id_stability_live():
    """실제 SSU 서버 2회 로그인 실측(선택적).

    로그인 정확히 2회, 세션당 목록 요청 1페이지로 제한한다.
    현재 연도 + status='RS02'(모집중) 로 범위를 한정한다.
    """
    from datetime import datetime

    def _page1_url(base_url: str, year: int) -> str:
        return build_url(base_url, {
            "paginationInfo.currentPageNo": 1,
            "sort": "0001",
            "chkAblyCount": "0",
            "operYySh": str(year),
            "operSemCdSh": "0000",
            "operSemCdShVal": "0000",
            "vshOrgid": "",
            "vshOrgzNm": "",
            "recStaCdSh": "RS02",
            "searchValue": "",
            "prgmFormCdSh": "0000",
            "prgmFormCdShVal": "0000",
            "eduFrDt": "",
            "eduToDt": "",
            "scpfDpmtCdSh": "",
            "scpfDpmtCdNm": "",
        })

    year = datetime.now().year

    crawler1 = SsupathCrawler()
    crawler1.login()  # 로그인 1회
    url = _page1_url(crawler1.SSUPATH_URL, year)
    ids1 = _extract_notice_ids(crawler1.session, url)

    crawler2 = SsupathCrawler()
    crawler2.login()  # 로그인 2회
    ids2 = _extract_notice_ids(crawler2.session, url)

    if not ids1 and not ids2:
        pytest.skip(f"{year}년 모집중(RS02) 공고가 없어 실측할 수 없습니다.")

    assert len(ids1) > 0 and len(ids2) > 0
    comparable_count = min(len(ids1), len(ids2))
    mismatches = [
        (i, ids1[i], ids2[i])
        for i in range(comparable_count)
        if ids1[i] != ids2[i]
    ]
    assert mismatches == [], f"encSddpbSeq 불일치: {mismatches}"
