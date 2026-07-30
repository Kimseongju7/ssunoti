import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/notice.dart';
import '../providers/favorites_provider.dart';
import '../theme/tokens.dart';
import 'status_pill.dart';

final _dateFormat = DateFormat('yyyy.MM.dd');

/// 공고 목록 행. Linear `changelog-row`.
///
/// `canvas` 배경 + 하단 `1px hairline`. 카드로 띄우지 않는다 —
/// 그림자를 쓰지 않고 실선으로만 구획한다.
class NoticeCard extends StatelessWidget {
  const NoticeCard({super.key, required this.notice, required this.onTap});

  final Notice notice;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final closed = notice.isClosed();

    return DecoratedBox(
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: SsuColors.hairline)),
      ),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: SsuSpace.md,
            vertical: SsuSpace.lg - 4,
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      notice.title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            // 종료 공고는 숨기지 않고 낮춘다.
                            color: closed ? SsuColors.inkTertiary : null,
                          ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: SsuSpace.sm),
                    _BadgeRow(notice: notice),
                  ],
                ),
              ),
              const SizedBox(width: SsuSpace.xs),
              _FavoriteButton(noticeId: notice.noticeId),
            ],
          ),
        ),
      ),
    );
  }
}

/// 공고 하나의 배지 조합.
///
/// 순서는 고정이다 — 상태, 정원, 대기, 마감. 순서가 흔들리면 목록을 훑을 때
/// 같은 정보를 매번 다른 위치에서 찾게 된다.
class _BadgeRow extends StatelessWidget {
  const _BadgeRow({required this.notice});

  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final badges = <Widget>[];
    final closed = notice.isClosed();

    // ① 상태
    badges.add(
      closed
          ? const StatusPill(label: '종료', dotColor: SsuColors.tagClosed)
          : const StatusPill(label: '모집중', dotColor: SsuColors.tagOpen),
    );

    // ② 정원. null 은 "정원 미정" — 0 으로 표시하면 0/0 이 마감으로 읽힌다.
    final capacity = notice.capacity;
    if (capacity == null) {
      badges.add(const StatusPill(label: '정원 미정'));
    } else {
      final nearFull = notice.isCapacityNearFull() ?? false;
      badges.add(
        StatusPill(
          label: '${notice.applicantCount}/$capacity',
          dotColor: nearFull ? SsuColors.tagWarning : null,
          icon: nearFull ? Icons.priority_high : null,
          useNumericFont: true,
        ),
      );
    }

    // ③ 대기자. 있을 때만.
    if (notice.waitlistCount > 0) {
      badges.add(
        StatusPill(
          label: '대기 ${notice.waitlistCount}',
          useNumericFont: true,
        ),
      );
    }

    // ④ 마감. null 은 "상시모집" — "오늘 마감" 으로 표시하지 않는다.
    badges.add(_deadlineBadge(notice));

    return Wrap(
      spacing: SsuSpace.xxs,
      runSpacing: SsuSpace.xxs,
      children: badges,
    );
  }

  Widget _deadlineBadge(Notice notice) {
    final deadline = notice.deadline;
    if (deadline == null) {
      return const StatusPill(label: '상시모집', dotColor: SsuColors.tagAlways);
    }

    final remaining = notice.daysUntilDeadline() ?? 0;
    if (remaining < 0) {
      return const StatusPill(
        label: '마감됨',
        dotColor: SsuColors.tagClosed,
        icon: Icons.lock_outline,
      );
    }

    final near = notice.isDeadlineNear() ?? false;
    // 경고는 색 점 + 텍스트 + 아이콘 세 겹. 색만으로 말하지 않는다.
    return StatusPill(
      label: remaining == 0
          ? '오늘 마감'
          : 'D-$remaining · ${_dateFormat.format(deadline)}',
      dotColor: near ? SsuColors.tagWarning : null,
      icon: near ? Icons.alarm : null,
      useNumericFont: remaining > 0,
    );
  }
}

/// 하트 버튼.
///
/// `isFavoriteProvider` 하나만 구독하므로 찜을 눌러도 목록 전체가 아니라
/// 이 버튼만 다시 그려진다. 터치 영역 44×44.
///
/// 찜은 주요 상호작용이라 라벤더를 쓴다. 분홍 같은 별도 색을 도입하지 않는다.
class _FavoriteButton extends ConsumerWidget {
  const _FavoriteButton({required this.noticeId});

  final String noticeId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isFavorite = ref.watch(isFavoriteProvider(noticeId));
    return SizedBox(
      width: SsuLayout.minTouchTarget,
      height: SsuLayout.minTouchTarget,
      child: IconButton(
        padding: EdgeInsets.zero,
        iconSize: 20,
        icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border),
        color: isFavorite ? SsuColors.accent : SsuColors.inkSubtle,
        tooltip: isFavorite ? '찜 해제' : '찜하기',
        onPressed: () =>
            ref.read(favoriteIdsProvider.notifier).toggle(noticeId),
      ),
    );
  }
}
