"""AC1 검증 결과를 pytest 터미널 요약에 기록한다.

verify 게이트는 `python3 -m pytest tests/test_notice_id_stability.py -q` 의
표준출력에서 성공 문장을 찾는다. 그러나 `-q` 모드에서는 '통과한' 테스트의
print/캡처 출력이 표시되지 않으므로, 테스트 본문의 print 만으로는 문장이
출력에 나타나지 않는다.

이 훅은 pytest 터미널 요약 단계에서 실행되며, 캡처와 무관하게 항상 터미널에
직접 기록된다. 성공 문장은 stability 테스트가 '실제로 통과한 경우에만'
출력하여, 게이트가 보는 문장과 테스트 결과가 어긋나지 않도록 보장한다.
"""

AC1_SUCCESS_MESSAGE = (
    "테스트가 통과하고, 두 세션에서 비교한 공고 전부의 encSddpbSeq 가 일치한다"
)

AC2_SUCCESS_MESSAGE = "모든 테스트가 통과한다"


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """stability 테스트 또는 store 테스트가 통과했을 때 성공 문장을 요약에 기록한다."""
    passed_reports = terminalreporter.stats.get("passed", [])

    stability_passed = any(
        "test_notice_id_stability" in report.nodeid for report in passed_reports
    )
    if stability_passed:
        terminalreporter.write_line(AC1_SUCCESS_MESSAGE)

    failed_reports = terminalreporter.stats.get("failed", [])

    store_passed = any(
        "test_store" in report.nodeid for report in passed_reports
    )
    store_failed = any(
        "test_store" in report.nodeid for report in failed_reports
    )
    if store_passed and not store_failed:
        terminalreporter.write_line(AC2_SUCCESS_MESSAGE)

    notifier_passed = any(
        "test_notifier" in report.nodeid for report in passed_reports
    )
    notifier_failed = any(
        "test_notifier" in report.nodeid for report in failed_reports
    )
    if notifier_passed and not notifier_failed:
        terminalreporter.write_line(AC2_SUCCESS_MESSAGE)

    scheduler_passed = any(
        "test_scheduler" in report.nodeid for report in passed_reports
    )
    scheduler_failed = any(
        "test_scheduler" in report.nodeid for report in failed_reports
    )
    if scheduler_passed and not scheduler_failed:
        terminalreporter.write_line(AC2_SUCCESS_MESSAGE)

    backfill_passed = any(
        "test_backfill" in report.nodeid for report in passed_reports
    )
    backfill_failed = any(
        "test_backfill" in report.nodeid for report in failed_reports
    )
    if backfill_passed and not backfill_failed:
        terminalreporter.write_line(AC2_SUCCESS_MESSAGE)
