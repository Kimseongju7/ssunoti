import 'package:cloud_firestore/cloud_firestore.dart';

/// Firestore `notices` 컬렉션 문서.
///
/// 서버는 원시값만 저장한다. 임박 여부 같은 파생 상태는 문서에 없으며
/// 이 클래스가 읽는 시점에 계산한다.
/// 근거: docs/adr/0001-no-derived-state-in-firestore.md
class Notice {
  const Notice({
    required this.noticeId,
    required this.title,
    required this.url,
    required this.content,
    required this.deadline,
    required this.applicantCount,
    required this.waitlistCount,
    required this.capacity,
    required this.createdAt,
  });

  /// docId 와 동일. SSUPath 상세 URL 의 `encSddpbSeq` (32자 hex).
  final String noticeId;
  final String title;
  final String url;
  final String content;

  /// 신청 마감 시각. 상시모집 등 마감이 없으면 null.
  final DateTime? deadline;

  final int applicantCount;
  final int waitlistCount;

  /// 모집 정원. null 은 무제한 또는 미정을 뜻하며 정원 0명과 다르다.
  /// 근거: docs/adr/0003-capacity-nullable-counts-zero.md
  final int? capacity;

  final DateTime createdAt;

  factory Notice.fromFirestore(
    DocumentSnapshot<Map<String, dynamic>> doc,
  ) {
    final data = doc.data() ?? const <String, dynamic>{};
    return Notice(
      noticeId: data['notice_id'] as String? ?? doc.id,
      title: data['title'] as String? ?? '',
      url: data['url'] as String? ?? '',
      content: data['content'] as String? ?? '',
      deadline: (data['deadline'] as Timestamp?)?.toDate(),
      applicantCount: data['applicant_count'] as int? ?? 0,
      waitlistCount: data['waitlist_count'] as int? ?? 0,
      capacity: data['capacity'] as int?,
      createdAt:
          (data['created_at'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  // ── 파생 값 (저장하지 않고 읽는 시점에 계산) ────────────────────────────

  /// 정원 대비 신청 비율. 정원을 알 수 없으면 null.
  ///
  /// capacity 가 null 이면 0 으로 대체하지 않는다. 0 으로 나누면 마감으로
  /// 오인되기 때문이다.
  double? get fillRatio {
    final total = capacity;
    if (total == null || total <= 0) return null;
    return applicantCount / total;
  }

  /// 정원 임박 여부. 정원 미상이면 판단하지 않는다(null).
  bool? isCapacityNearFull({double threshold = 0.9}) {
    final ratio = fillRatio;
    if (ratio == null) return null;
    return ratio >= threshold;
  }

  /// 마감까지 남은 일수. 마감이 없으면 null. 이미 지났으면 음수.
  int? daysUntilDeadline({DateTime? now}) {
    final due = deadline;
    if (due == null) return null;
    final base = now ?? DateTime.now();
    return due.difference(base).inDays;
  }

  /// 마감 임박 여부. 마감이 없으면 판단하지 않는다(null).
  bool? isDeadlineNear({int withinDays = 3, DateTime? now}) {
    final remaining = daysUntilDeadline(now: now);
    if (remaining == null) return null;
    return remaining >= 0 && remaining <= withinDays;
  }

  /// 마감이 이미 지났는지. 마감이 없으면 false (상시모집은 마감되지 않는다).
  bool isClosed({DateTime? now}) {
    final due = deadline;
    if (due == null) return false;
    return due.isBefore(now ?? DateTime.now());
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Notice && other.noticeId == noticeId;

  @override
  int get hashCode => noticeId.hashCode;
}
