"""초기 적재(backfill) 모드 단위 테스트.

검증 항목:
(a) backfill=True 로 실행하면 수집 공고 전량이 Firestore 에 저장되고
    FCM mock 의 send 호출은 정확히 0회이다.
(b) backfill 완료 후 일반 모드(backfill=False)를 실행하면 모든 공고가
    이미 Firestore 에 존재하므로 신규로 판정되지 않아 send 호출이 0회이다.
(c) backfill 반환값은 저장된 공고 수(=수집 공고 수)와 같다.
(d) notice_id 가 비어 있는 공고는 backfill 에서도 저장되지 않는다.
"""
from __future__ import annotations

from typing import Any

import pytest

from ssunoti.notifier import NoticeNotifier
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


# ── Fake FCM messaging ────────────────────────────────────────────────────────


class FakeMessaging:
    """firebase_admin.messaging 모듈 호환 fake."""

    class Message:
        def __init__(
            self,
            notification: Any = None,
            topic: str | None = None,
            token: str | None = None,
            **kwargs: Any,
        ) -> None:
            self.notification = notification
            self.topic = topic
            self.token = token

    class Notification:
        def __init__(self, title: str = "", body: str = "") -> None:
            self.title = title
            self.body = body

    def __init__(self) -> None:
        self.send_calls: list[Any] = []

    def send(self, message: Any) -> str:
        self.send_calls.append(message)
        return f"projects/test/messages/{len(self.send_calls)}"


# ── 테스트용 공고 팩토리 ───────────────────────────────────────────────────────


def _make_notice(
    notice_id: str = "backfill0000000000000000000000a0",
    title: str = "테스트 공고",
) -> dict:
    """테스트용 공고 dict. notice_id 는 합성값 32자 (실계정 정보 미포함)."""
    return {
        "notice_id": notice_id,
        "title": title,
        "summary": "테스트 공고 요약",
        "application_period": {"start": "2026.04.01 00:00", "end": "2026.04.30 23:59"},
        "applicant_count": 10,
        "waitlist_count": 0,
        "capacity": 30,
        "status": "모집중",
    }


def _make_notices(n: int) -> list[dict]:
    """n 개의 고유한 테스트 공고 목록을 생성한다."""
    return [
        _make_notice(
            notice_id=f"bfill{i:027d}",
            title=f"테스트 공고 {i}",
        )
        for i in range(n)
    ]


# ── pytest fixtures ───────────────────────────────────────────────────────────


@pytest.fixture()
def db() -> FakeFirestoreClient:
    return FakeFirestoreClient()


@pytest.fixture()
def store(db: FakeFirestoreClient) -> NoticeStore:
    return NoticeStore(db)


@pytest.fixture()
def messaging() -> FakeMessaging:
    return FakeMessaging()


@pytest.fixture()
def notifier(store: NoticeStore, messaging: FakeMessaging) -> NoticeNotifier:
    return NoticeNotifier(store, messaging)


# ── (a) backfill 모드: 전체 저장, FCM 0회 ────────────────────────────────────


class TestBackfillStoresAllWithoutFcm:
    """(a) backfill=True 로 실행하면 전체 공고가 저장되고 FCM send 는 0회이다."""

    def test_backfill_stores_all_notices(
        self,
        notifier: NoticeNotifier,
        db: FakeFirestoreClient,
    ) -> None:
        """backfill 후 저장된 문서 수가 수집 공고 수와 같다."""
        notices = _make_notices(5)
        notifier.process_new_notices(notices, backfill=True)
        docs = db.get_docs("notices")
        assert len(docs) == 5, f"backfill 후 문서 수가 {len(docs)}이어야 합니다 (기대: 5)"

    def test_backfill_sends_zero_fcm_messages(
        self,
        notifier: NoticeNotifier,
        messaging: FakeMessaging,
    ) -> None:
        """backfill 중 FCM send 호출이 정확히 0회이다."""
        notices = _make_notices(5)
        notifier.process_new_notices(notices, backfill=True)
        assert len(messaging.send_calls) == 0, (
            f"backfill 모드에서 FCM send 가 {len(messaging.send_calls)}회 호출되었습니다 (기대: 0)"
        )

    def test_backfill_returns_stored_count(
        self,
        notifier: NoticeNotifier,
        db: FakeFirestoreClient,
    ) -> None:
        """backfill 반환값이 저장된 공고 수(=수집 공고 수)와 같다."""
        notices = _make_notices(3)
        stored = notifier.process_new_notices(notices, backfill=True)
        docs = db.get_docs("notices")
        assert stored == len(notices) == len(docs) == 3

    def test_backfill_single_notice(
        self,
        notifier: NoticeNotifier,
        db: FakeFirestoreClient,
        messaging: FakeMessaging,
    ) -> None:
        """공고 1건 backfill: 1건 저장, FCM 0회."""
        notice = _make_notice()
        stored = notifier.process_new_notices([notice], backfill=True)
        assert stored == 1
        assert len(db.get_docs("notices")) == 1
        assert len(messaging.send_calls) == 0

    def test_backfill_stores_correct_notice_ids(
        self,
        notifier: NoticeNotifier,
        db: FakeFirestoreClient,
    ) -> None:
        """backfill 후 각 공고의 notice_id 가 문서 키로 존재한다."""
        notices = _make_notices(4)
        notifier.process_new_notices(notices, backfill=True)
        docs = db.get_docs("notices")
        for notice in notices:
            assert notice["notice_id"] in docs, (
                f"notice_id={notice['notice_id']} 가 Firestore 에 없습니다"
            )


# ── (b) backfill 후 일반 모드: 이미 존재 → send 0회 ─────────────────────────


class TestNormalModeAfterBackfill:
    """(b) backfill 완료 후 일반 모드 실행 시 모든 공고가 기존 문서로 판정되어 send 가 0회이다."""

    def test_normal_mode_after_backfill_sends_zero_fcm(
        self,
        notifier: NoticeNotifier,
        messaging: FakeMessaging,
    ) -> None:
        """backfill 후 일반 모드 실행 시 FCM send 호출 0회."""
        notices = _make_notices(5)

        # backfill: 전체 저장, FCM 0회
        notifier.process_new_notices(notices, backfill=True)
        assert len(messaging.send_calls) == 0

        # 일반 모드: 이미 문서가 존재하므로 신규 없음 → FCM 0회
        notifier.process_new_notices(notices, backfill=False)
        assert len(messaging.send_calls) == 0, (
            f"backfill 후 일반 모드에서 FCM send 가 {len(messaging.send_calls)}회 호출되었습니다 (기대: 0)"
        )

    def test_normal_mode_after_backfill_returns_zero_new(
        self,
        notifier: NoticeNotifier,
    ) -> None:
        """backfill 후 일반 모드는 신규 공고 수 0을 반환한다."""
        notices = _make_notices(3)
        notifier.process_new_notices(notices, backfill=True)
        new_count = notifier.process_new_notices(notices, backfill=False)
        assert new_count == 0, (
            f"backfill 후 일반 모드 신규 공고 수가 {new_count}이어야 합니다 (기대: 0)"
        )

    def test_normal_mode_after_backfill_no_additional_docs(
        self,
        notifier: NoticeNotifier,
        db: FakeFirestoreClient,
    ) -> None:
        """backfill 후 일반 모드를 실행해도 문서 수가 변하지 않는다."""
        notices = _make_notices(4)
        notifier.process_new_notices(notices, backfill=True)
        count_after_backfill = len(db.get_docs("notices"))

        notifier.process_new_notices(notices, backfill=False)
        count_after_normal = len(db.get_docs("notices"))

        assert count_after_backfill == count_after_normal == 4


# ── (c) backfill 반환값 검증 ──────────────────────────────────────────────────


class TestBackfillReturnValue:
    """(c) backfill 반환값은 저장된 공고 수와 일치한다."""

    def test_return_value_matches_notice_count(
        self, notifier: NoticeNotifier
    ) -> None:
        """backfill 반환값이 전달한 공고 수와 같다."""
        notices = _make_notices(7)
        stored = notifier.process_new_notices(notices, backfill=True)
        assert stored == 7

    def test_empty_list_returns_zero(self, notifier: NoticeNotifier) -> None:
        """빈 목록 backfill 은 0을 반환한다."""
        stored = notifier.process_new_notices([], backfill=True)
        assert stored == 0


# ── (d) 빈 notice_id 는 backfill 에서도 저장 안 함 ───────────────────────────


class TestBackfillSkipsEmptyNoticeId:
    """(d) notice_id 가 비어 있는 공고는 backfill 에서도 저장되지 않는다."""

    def test_empty_notice_id_skipped_in_backfill(
        self,
        notifier: NoticeNotifier,
        db: FakeFirestoreClient,
    ) -> None:
        """notice_id='' 인 공고는 backfill 에서 건너뛴다."""
        notices = [
            _make_notice(notice_id=""),  # 빈 ID — 건너뜀
            _make_notice(notice_id="backfill_valid_id_00000000000000"),  # 유효
        ]
        stored = notifier.process_new_notices(notices, backfill=True)
        docs = db.get_docs("notices")
        assert stored == 1
        assert len(docs) == 1
        assert "" not in docs
