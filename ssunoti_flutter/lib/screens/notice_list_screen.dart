import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/notice.dart';
import '../providers/notices_provider.dart';
import '../theme/tokens.dart';
import '../widgets/notice_card.dart';
import 'notice_detail_screen.dart';

/// 전체 공고 목록. Firestore 스트림을 그대로 그린다.
class NoticeListScreen extends ConsumerWidget {
  const NoticeListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final noticesAsync = ref.watch(noticesProvider);

    return noticesAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => ErrorStateView(message: '$error'),
      data: (_) {
        final notices = ref.watch(openNoticesProvider);
        if (notices.isEmpty) {
          return const EmptyStateView(
            icon: Icons.inbox_outlined,
            message: '모집 중인 공고가 없습니다',
            hint: '새 공고가 등록되면 알림으로 알려드립니다',
          );
        }
        return NoticeListView(notices: notices);
      },
    );
  }
}

/// 공고 목록 뷰. 목록 화면과 찜 화면이 함께 쓴다.
///
/// 카드를 띄우지 않는다. 각 항목이 아래쪽에 파선 구분선을 그린다.
class NoticeListView extends StatelessWidget {
  const NoticeListView({super.key, required this.notices});

  final List<Notice> notices;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: SsuLayout.maxContentWidth),
        child: ListView.builder(
          padding: EdgeInsets.zero,
          itemCount: notices.length,
          itemBuilder: (context, index) {
            final notice = notices[index];
            return NoticeCard(
              notice: notice,
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => NoticeDetailScreen(noticeId: notice.noticeId),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

/// 빈 상태. 목록·찜 화면이 함께 쓴다.
class EmptyStateView extends StatelessWidget {
  const EmptyStateView({
    super.key,
    required this.icon,
    required this.message,
    this.hint,
  });

  final IconData icon;
  final String message;
  final String? hint;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(SsuSpace.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: SsuColors.borderStrong),
            const SizedBox(height: SsuSpace.lg),
            Text(
              message,
              style: Theme.of(context)
                  .textTheme
                  .bodyLarge
                  ?.copyWith(color: SsuColors.textMuted),
            ),
            if (hint != null) ...[
              const SizedBox(height: SsuSpace.sm),
              Text(
                hint!,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// 오류 상태.
///
/// Firestore 규칙이 잠겨 있으면 permission-denied 가 여기로 온다.
/// 원인을 감추지 않고 그대로 보여준다 — 개발 중 진단이 빨라진다.
class ErrorStateView extends StatelessWidget {
  const ErrorStateView({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(SsuSpace.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, size: 48, color: SsuColors.danger),
            const SizedBox(height: SsuSpace.lg),
            Text(
              '공고를 불러오지 못했습니다',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: SsuSpace.sm),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.labelSmall,
            ),
          ],
        ),
      ),
    );
  }
}
