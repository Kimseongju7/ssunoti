import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/notice.dart';
import '../providers/favorites_provider.dart';
import '../theme/tokens.dart';
import 'status_pill.dart';

final _dateFormat = DateFormat('yyyy.MM.dd');

/// 공고 목록 항목.
///
/// 원본은 카드가 아니라 파선으로 나뉜 목록이다
/// (`.lica_wrap > ul > li` + `border-top: 1px dashed #E8E8E8`).
/// Material `Card` + elevation 을 쓰면 원본과 질감이 어긋난다.
/// 근거: DESIGN.md 4·5절
class NoticeCard extends StatelessWidget {
  const NoticeCard({super.key, required this.notice, required this.onTap});

  final Notice notice;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final closed = notice.isClosed();

    return Column(
      children: [
        InkWell(
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(SsuSpace.lg),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        notice.title,
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  // 종료 공고는 숨기지 않고 흐리게 한다.
                                  color: closed
                                      ? SsuColors.textDisabled
                                      : SsuColors.textStrong,
                                ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: SsuSpace.md),
                      _PillRow(notice: notice),
                    ],
                  ),
                ),
                const SizedBox(width: SsuSpace.sm),
                _FavoriteButton(noticeId: notice.noticeId),
              ],
            ),
          ),
        ),
        const DashedDivider(),
      ],
    );
  }
}

/// 공고 하나의 라벨 조합.
///
/// 라벨 순서는 고정이다 — 상태, 정원, 대기, 마감. 순서가 흔들리면
/// 목록을 훑을 때 같은 정보를 매번 다른 위치에서 찾게 된다.
class _PillRow extends StatelessWidget {
  const _PillRow({required this.notice});

  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final pills = <Widget>[];
    final closed = notice.isClosed();

    // ① 상태
    pills.add(
      closed
          ? const StatusPill(label: '종료', background: SsuColors.statusClosed)
          : const StatusPill(label: '모집중', background: SsuColors.statusOpen),
    );

    // ② 정원. null 은 "정원 미정" — 0 으로 표시하면 0/0 이 되어 마감으로 읽힌다.
    final capacity = notice.capacity;
    if (capacity == null) {
      pills.add(
        const StatusPill(
          label: '정원 미정',
          background: SsuColors.statusNeutral,
        ),
      );
    } else {
      final nearFull = notice.isCapacityNearFull() ?? false;
      pills.add(
        StatusPill(
          label: '${notice.applicantCount}/$capacity',
          background: nearFull ? SsuColors.warning : SsuColors.statusNeutral,
          icon: nearFull ? Icons.priority_high : null,
          useNumericFont: true,
        ),
      );
    }

    // ③ 대기자. 있을 때만.
    if (notice.waitlistCount > 0) {
      pills.add(
        StatusPill(
          label: '대기 ${notice.waitlistCount}',
          background: SsuColors.statusNeutral,
          useNumericFont: true,
        ),
      );
    }

    // ④ 마감. null 은 "상시모집" — "오늘 마감" 으로 표시하지 않는다.
    pills.add(_deadlinePill(notice));

    return Wrap(
      spacing: SsuSpace.xs,
      runSpacing: SsuSpace.xs,
      children: pills,
    );
  }

  Widget _deadlinePill(Notice notice) {
    final deadline = notice.deadline;
    if (deadline == null) {
      return const StatusPill(
        label: '상시모집',
        background: SsuColors.statusWaiting,
      );
    }

    final remaining = notice.daysUntilDeadline() ?? 0;
    if (remaining < 0) {
      return const StatusPill(
        label: '마감됨',
        background: SsuColors.statusClosed,
        icon: Icons.lock_outline,
      );
    }

    final near = notice.isDeadlineNear() ?? false;
    // 경고는 색 + 텍스트 + 아이콘 세 겹. 색만으로 말하지 않는다.
    return StatusPill(
      label: remaining == 0
          ? '오늘 마감'
          : 'D-$remaining · ${_dateFormat.format(deadline)}',
      background: near ? SsuColors.warning : SsuColors.statusNeutral,
      icon: near ? Icons.alarm : null,
      useNumericFont: remaining > 0,
    );
  }
}

/// 하트 버튼.
///
/// `isFavoriteProvider` 하나만 구독하므로 찜을 눌러도 목록 전체가 아니라
/// 이 버튼만 다시 그려진다. 터치 영역은 48×48 을 지킨다.
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
        icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border),
        color: isFavorite ? SsuColors.favorite : SsuColors.textFaint,
        tooltip: isFavorite ? '찜 해제' : '찜하기',
        onPressed: () =>
            ref.read(favoriteIdsProvider.notifier).toggle(noticeId),
      ),
    );
  }
}
