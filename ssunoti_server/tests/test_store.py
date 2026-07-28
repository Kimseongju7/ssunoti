"""store.py 단위 테스트.

Firestore 는 fake 로 대체한다. 실제 Firebase 프로젝트에 쓰기를 하지 않는다.

검증 항목:
- 동일 공고 집합을 연속 2회 저장해도 문서 수가 늘지 않는다.
- 카운트(applicant_count, waitlist_count)는 최신값으로 갱신된다.
- created_at 은 1회차 값 그대로 보존된다.
- 파생 플래그 필드가 존재하지 않는다.
- '-' 같은 비숫자 입력에서 예외 없이 정규화된다.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from ssunoti.store import NoticeStore


# ── Fake Firestore ────────────────────────────────────────────────────────────

class _FakeSnapshot:
    def __init__(self, data: dict | None) -> None:
        self._data = data
        self.exists = data is not None

    def to_dict(self) -> dict:
        return self._data.copy() if self._data else {}


class _FakeDocRef:
    def __init__(self, collection_store: dict, doc_id: str) -> None:
        self._store = collection_store
        self._doc_id = doc_id

    def get(self) -> _FakeSnapshot:
        return _FakeSnapshot(self._store.get(self._doc_id))

    def set(self, data: dict, merge: bool = False) -> None:
        existing = self._store.get(self._doc_id)
        if merge and existing is not None:
            # merge=True: 기존 필드를 유지하고 새 데이터로 덮어쓴다.
            # created_at 같이 새 데이터에 없는 필드는 기존 값이 보존된다.
            self._store[self._doc_id] = {**existing, **data}
        else:
            self._store[self._doc_id] = data.copy()


class _FakeCollection:
    def __init__(self) -> None:
        self._docs: dict[str, dict] = {}

    def document(self, doc_id: str) -> _FakeDocRef:
        return _FakeDocRef(self._docs, doc_id)

    def all_docs(self) -> dict[str, dict]:
        return dict(self._docs)


class FakeFirestoreClient:
    def __init__(self) -> None:
        self._collections: dict[str, _FakeCollection] = {}

    def collection(self, name: str) -> _FakeCollection:
        if name not in self._collections:
            self._collections[name] = _FakeCollection()
        return self._collections[name]

    def get_docs(self, collection_name: str) -> dict[str, dict]:
        col = self._collections.get(collection_name)
        return col.all_docs() if col else {}


# ── 테스트용 공고 팩토리 ───────────────────────────────────────────────────────

def _make_notice(
    notice_id: str = "0a1b2c3d4e5f60718293a4b5c6d7e8f9",
    title: str = "테스트 공고",
    applicant_count: Any = 5,
    waitlist_count: Any = 2,
    capacity: Any = 30,
    period_end: str = "2026.04.30 23:59",
) -> dict:
    """테스트용 공고 dict 를 생성한다. notice_id 는 합성값 (실계정 정보 미포함)."""
    return {
        "notice_id": notice_id,
        "title": title,
        "summary": "테스트 공고 요약",
        "application_period": {"start": "2026.04.01 00:00", "end": period_end},
        "applicant_count": applicant_count,
        "waitlist_count": waitlist_count,
        "capacity": capacity,
        "status": "모집중",
        "organizer": "테스트 조직",
    }


# ── pytest fixtures ───────────────────────────────────────────────────────────

@pytest.fixture()
def db() -> FakeFirestoreClient:
    return FakeFirestoreClient()


@pytest.fixture()
def store(db: FakeFirestoreClient) -> NoticeStore:
    return NoticeStore(db)


# ── 기본 저장 동작 ────────────────────────────────────────────────────────────

class TestUpsertBasic:
    def test_upsert_creates_document(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """upsert 후 notices 컬렉션에 문서가 생성된다."""
        notice = _make_notice()
        store.upsert(notice)
        docs = db.get_docs("notices")
        assert notice["notice_id"] in docs

    def test_upsert_stores_exactly_nine_fields(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """저장 필드는 notice_id, title, url, content, deadline,
        applicant_count, waitlist_count, capacity, created_at 이다."""
        store.upsert(_make_notice())
        doc = db.get_docs("notices")["0a1b2c3d4e5f60718293a4b5c6d7e8f9"]
        expected_keys = {
            "notice_id", "title", "url", "content", "deadline",
            "applicant_count", "waitlist_count", "capacity", "created_at",
        }
        assert set(doc.keys()) == expected_keys

    def test_upsert_no_derived_flags(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """파생 플래그(is_closing_soon, notified_deadline 등)가 저장되지 않는다."""
        store.upsert(_make_notice())
        doc = db.get_docs("notices")["0a1b2c3d4e5f60718293a4b5c6d7e8f9"]
        derived_flags = {
            "is_closing_soon", "notified_deadline", "is_new", "seen",
            "is_full", "capacity_pct",
        }
        overlapping = derived_flags & set(doc.keys())
        assert not overlapping, f"파생 플래그가 문서에 존재합니다: {overlapping}"

    def test_empty_notice_id_is_skipped(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """notice_id 가 비어 있는 공고는 저장하지 않는다."""
        notice = _make_notice(notice_id="")
        store.upsert(notice)
        docs = db.get_docs("notices")
        assert len(docs) == 0


# ── 멱등성 (Idempotency) ──────────────────────────────────────────────────────

class TestUpsertIdempotency:
    def test_double_save_does_not_increase_document_count(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """동일 공고 집합을 연속 2회 저장해도 문서 수가 늘지 않는다."""
        notices = [
            _make_notice("aaa111aaa111aaa111aaa111aaa11100", "공고 1"),
            _make_notice("bbb222bbb222bbb222bbb222bbb22200", "공고 2"),
        ]
        store.upsert_many(notices)
        count_after_first = len(db.get_docs("notices"))

        store.upsert_many(notices)
        count_after_second = len(db.get_docs("notices"))

        assert count_after_first == count_after_second == 2

    def test_double_save_updates_counts_to_latest(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """2회차 저장에서 카운트(applicant_count, waitlist_count)가 최신값으로 갱신된다."""
        notice_id = "update_test_0000000000000000001"
        notice_v1 = _make_notice(
            notice_id=notice_id, applicant_count=5, waitlist_count=1
        )
        notice_v2 = _make_notice(
            notice_id=notice_id, applicant_count=10, waitlist_count=3
        )

        store.upsert(notice_v1)
        store.upsert(notice_v2)

        doc = db.get_docs("notices")[notice_id]
        assert doc["applicant_count"] == 10
        assert doc["waitlist_count"] == 3

    def test_double_save_preserves_created_at(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """2회차 저장에도 created_at 은 1회차 값 그대로다."""
        notice_id = "created_at_test_00000000000000001"
        notice = _make_notice(notice_id=notice_id)

        store.upsert(notice)
        created_at_first = db.get_docs("notices")[notice_id]["created_at"]

        store.upsert(notice)
        created_at_second = db.get_docs("notices")[notice_id]["created_at"]

        assert created_at_first == created_at_second

    def test_created_at_is_datetime(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """created_at 은 datetime 타입이다."""
        notice = _make_notice()
        store.upsert(notice)
        doc = db.get_docs("notices")["0a1b2c3d4e5f60718293a4b5c6d7e8f9"]
        assert isinstance(doc["created_at"], datetime)


# ── 비숫자 입력 정규화 ────────────────────────────────────────────────────────

class TestNonNumericNormalization:
    def test_dash_applicant_count_becomes_zero(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """applicant_count 가 '-' 이면 0 으로 정규화된다."""
        notice = _make_notice(
            notice_id="norm001norm001norm001norm001n000", applicant_count="-"
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["norm001norm001norm001norm001n000"]
        assert doc["applicant_count"] == 0

    def test_dash_waitlist_count_becomes_zero(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """waitlist_count 가 '-' 이면 0 으로 정규화된다."""
        notice = _make_notice(
            notice_id="norm002norm002norm002norm002n000", waitlist_count="-"
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["norm002norm002norm002norm002n000"]
        assert doc["waitlist_count"] == 0

    def test_dash_capacity_becomes_null(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """capacity 가 '-' 이면 null(None) 로 정규화된다."""
        notice = _make_notice(
            notice_id="norm003norm003norm003norm003n000", capacity="-"
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["norm003norm003norm003norm003n000"]
        assert doc["capacity"] is None

    def test_none_capacity_becomes_null(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """capacity 가 None 이면 null(None) 로 저장된다."""
        notice = _make_notice(
            notice_id="norm004norm004norm004norm004n000", capacity=None
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["norm004norm004norm004norm004n000"]
        assert doc["capacity"] is None

    def test_zero_capacity_is_stored_as_zero(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """capacity=0 은 null 이 아닌 0으로 저장된다 (0명 정원과 미정 구별)."""
        notice = _make_notice(
            notice_id="norm005norm005norm005norm005n000", capacity=0
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["norm005norm005norm005norm005n000"]
        assert doc["capacity"] == 0
        assert doc["capacity"] is not None

    def test_string_number_normalizes_correctly(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """문자열 숫자 '5' 는 int 5 로 변환된다."""
        notice = _make_notice(
            notice_id="norm006norm006norm006norm006n000",
            applicant_count="5",
            waitlist_count="3",
            capacity="20",
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["norm006norm006norm006norm006n000"]
        assert doc["applicant_count"] == 5
        assert doc["waitlist_count"] == 3
        assert doc["capacity"] == 20

    def test_non_numeric_does_not_raise(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """비숫자 입력('-', None 등)에서 예외 없이 정규화된다."""
        notice = _make_notice(
            notice_id="norm007norm007norm007norm007n000",
            applicant_count="-",
            waitlist_count=None,
            capacity="미정",
        )
        # 예외가 발생하지 않아야 한다.
        store.upsert(notice)
        doc = db.get_docs("notices")["norm007norm007norm007norm007n000"]
        assert doc["applicant_count"] == 0
        assert doc["waitlist_count"] == 0
        assert doc["capacity"] is None


# ── 마감 파싱 ─────────────────────────────────────────────────────────────────

class TestDeadlineParsing:
    def test_deadline_parsed_from_application_period_end(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """deadline 은 application_period.end 에서 파싱된 datetime 이다."""
        notice = _make_notice(
            notice_id="deadline001deadline001deadline01",
            period_end="2026.04.30 23:59",
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["deadline001deadline001deadline01"]
        assert isinstance(doc["deadline"], datetime)
        assert doc["deadline"] == datetime(2026, 4, 30, 23, 59)

    def test_empty_period_end_gives_null_deadline(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """application_period.end 가 비어 있으면 deadline 은 None 이다."""
        notice = _make_notice(
            notice_id="deadline002deadline002deadline02",
            period_end="",
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["deadline002deadline002deadline02"]
        assert doc["deadline"] is None

    def test_date_only_format_parsed(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """'2026.04.30' 형식의 날짜도 파싱된다."""
        notice = _make_notice(
            notice_id="deadline003deadline003deadline03",
            period_end="2026.04.30",
        )
        store.upsert(notice)
        doc = db.get_docs("notices")["deadline003deadline003deadline03"]
        assert doc["deadline"] == datetime(2026, 4, 30, 0, 0)


# ── URL 필드 ──────────────────────────────────────────────────────────────────

class TestUrlField:
    def test_url_contains_notice_id(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """url 필드에 notice_id(encSddpbSeq)가 포함된다."""
        notice_id = "urltest001urltest001urltest0001"
        notice = _make_notice(notice_id=notice_id)
        store.upsert(notice)
        doc = db.get_docs("notices")[notice_id]
        assert notice_id in doc["url"]

    def test_url_points_to_ssupath_detail(
        self, store: NoticeStore, db: FakeFirestoreClient
    ) -> None:
        """url 필드는 SSUPath 상세 페이지 URL 이다."""
        notice = _make_notice(notice_id="urltest002urltest002urltest0002")
        store.upsert(notice)
        doc = db.get_docs("notices")["urltest002urltest002urltest0002"]
        assert "path.ssu.ac.kr" in doc["url"]
        assert "findIcmpNsbjtPgmInfo" in doc["url"]
