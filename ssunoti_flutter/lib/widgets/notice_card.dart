import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/notice.dart';
import '../providers/favorites_provider.dart';

final _dateFormat = DateFormat('yyyy.MM.dd');

/// 목록에 쓰이는 공고 카드.
class NoticeCard extends StatelessWidget {
  const NoticeCard({super.key, required this.notice, required this.onTap});

  final Notice notice;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      notice.title,
                      style: Theme.of(context).textTheme.titleMedium,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    _NoticeBadges(notice: notice),
                  ],
                ),
              ),
              _FavoriteButton(noticeId: notice.noticeId),
            ],
          ),
        ),
      ),
    );
  }
}

/// 정원·마감 배지.
///
/// 정원 미상(capacity == null)과 마감 없음(deadline == null)은 배지를 만들지
/// 않는다. 0 으로 대체하면 "정원 0명" 이나 "오늘 마감" 으로 오인된다.
class _NoticeBadges extends StatelessWidget {
  const _NoticeBadges({required this.notice});

  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final badges = <Widget>[];

    final capacity = notice.capacity;
    if (capacity == null) {
      badges.add(const _Badge(label: '정원 미정', color: Colors.grey));
    } else {
      final nearFull = notice.isCapacityNearFull() ?? false;
      badges.add(
        _Badge(
          label: '${notice.applicantCount}/$capacity',
          color: nearFull ? Colors.deepOrange : Colors.blueGrey,
        ),
      );
    }

    if (notice.waitlistCount > 0) {
      badges.add(
        _Badge(label: '대기 ${notice.waitlistCount}', color: Colors.blueGrey),
      );
    }

    final deadline = notice.deadline;
    if (deadline == null) {
      badges.add(const _Badge(label: '상시모집', color: Colors.teal));
    } else {
      final remaining = notice.daysUntilDeadline() ?? 0;
      badges.add(
        _Badge(
          label: remaining <= 0
              ? '오늘 마감'
              : 'D-$remaining · ${_dateFormat.format(deadline)}',
          color: (notice.isDeadlineNear() ?? false)
              ? Colors.deepOrange
              : Colors.blueGrey,
        ),
      );
    }

    return Wrap(spacing: 6, runSpacing: 6, children: badges);
  }
}

class _Badge extends StatelessWidget {
  const _Badge({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        label,
        style: Theme.of(context)
            .textTheme
            .labelSmall
            ?.copyWith(color: color, fontWeight: FontWeight.w600),
      ),
    );
  }
}

/// 하트 버튼.
///
/// isFavoriteProvider 하나만 구독하므로, 찜을 눌러도 목록 전체가 아니라
/// 이 버튼만 다시 그려진다.
class _FavoriteButton extends ConsumerWidget {
  const _FavoriteButton({required this.noticeId});

  final String noticeId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isFavorite = ref.watch(isFavoriteProvider(noticeId));
    return IconButton(
      icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border),
      color: isFavorite ? Colors.redAccent : null,
      tooltip: isFavorite ? '찜 해제' : '찜하기',
      onPressed: () =>
          ref.read(favoriteIdsProvider.notifier).toggle(noticeId),
    );
  }
}
