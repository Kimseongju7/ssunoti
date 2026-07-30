import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/notice.dart';
import '../providers/favorites_provider.dart';
import '../providers/notices_provider.dart';
import '../theme/app_theme.dart';
import '../theme/tokens.dart';
import '../widgets/status_pill.dart';

final _dateTimeFormat = DateFormat('yyyy.MM.dd HH:mm');

/// 공고 상세.
///
/// notice_id 만 받아 목록 스트림에서 찾는다. 공고 객체를 통째로 넘기면
/// 서버가 값을 갱신해도 이 화면은 옛 값을 계속 보여준다.
class NoticeDetailScreen extends ConsumerWidget {
  const NoticeDetailScreen({super.key, required this.noticeId});

  final String noticeId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notice = ref.watch(noticeByIdProvider(noticeId));
    final isFavorite = ref.watch(isFavoriteProvider(noticeId));

    if (notice == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('공고')),
        body: const Center(child: Text('공고를 찾을 수 없습니다')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('공고 상세'),
        actions: [
          IconButton(
            iconSize: 20,
            icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border),
            // 찜은 주요 상호작용이라 라벤더를 쓴다.
            color: isFavorite ? SsuColors.accent : SsuColors.inkSubtle,
            tooltip: isFavorite ? '찜 해제' : '찜하기',
            onPressed: () =>
                ref.read(favoriteIdsProvider.notifier).toggle(noticeId),
          ),
          const SizedBox(width: SsuSpace.xs),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints:
              const BoxConstraints(maxWidth: SsuLayout.contentWidth),
          child: ListView(
            padding: const EdgeInsets.all(SsuSpace.md),
            children: [
              Text(
                notice.title,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: notice.isClosed() ? SsuColors.inkTertiary : null,
                    ),
              ),
              const SizedBox(height: SsuSpace.sm),
              _StatusRow(notice: notice),
              const SizedBox(height: SsuSpace.lg),
              InfoBox(child: _InfoTable(notice: notice)),
              if (notice.content.isNotEmpty) ...[
                const SizedBox(height: SsuSpace.lg),
                Text(
                  notice.content,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ],
              const SizedBox(height: SsuSpace.xl),
            ],
          ),
        ),
      ),
      bottomNavigationBar: _ApplyBar(notice: notice),
    );
  }
}

class _StatusRow extends StatelessWidget {
  const _StatusRow({required this.notice});

  final Notice notice;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: SsuSpace.xxs,
      runSpacing: SsuSpace.xxs,
      children: [
        notice.isClosed()
            ? const StatusPill(label: '종료', dotColor: SsuColors.tagClosed)
            : const StatusPill(label: '모집중', dotColor: SsuColors.tagOpen),
        if (notice.deadline == null)
          const StatusPill(label: '상시모집', dotColor: SsuColors.tagAlways),
      ],
    );
  }
}

class _InfoTable extends StatelessWidget {
  const _InfoTable({required this.notice});

  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final capacity = notice.capacity;
    final deadline = notice.deadline;

    return Column(
      children: [
        _InfoRow(
          label: '모집 정원',
          // 정원 미상을 0 으로 표시하지 않는다. 근거: ADR-0003
          value: capacity == null ? '미정 또는 무제한' : '$capacity명',
          numeric: capacity != null,
          highlight: notice.isCapacityNearFull() ?? false,
        ),
        _InfoRow(
          label: '신청자',
          value: '${notice.applicantCount}명',
          numeric: true,
        ),
        _InfoRow(
          label: '대기자',
          value: '${notice.waitlistCount}명',
          numeric: true,
        ),
        _InfoRow(
          label: '신청 마감',
          value: deadline == null
              ? '상시모집'
              : '${_dateTimeFormat.format(deadline)}${_suffix(notice)}',
          numeric: deadline != null,
          highlight: notice.isDeadlineNear() ?? false,
        ),
      ],
    );
  }

  String _suffix(Notice notice) {
    final remaining = notice.daysUntilDeadline();
    if (remaining == null) return '';
    if (remaining < 0) return ' (마감됨)';
    if (remaining == 0) return ' (오늘 마감)';
    return ' (D-$remaining)';
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({
    required this.label,
    required this.value,
    this.numeric = false,
    this.highlight = false,
  });

  final String label;
  final String value;
  final bool numeric;

  /// 임박 상태. 색과 함께 아이콘을 붙여 색만으로 말하지 않는다.
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    final color = highlight ? SsuColors.tagWarning : SsuColors.ink;
    final valueStyle = numeric
        ? AppTheme.numeric(size: 13, color: color)
        : Theme.of(context).textTheme.bodyLarge?.copyWith(color: color);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SsuSpace.xs),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          if (highlight) ...[
            const Icon(Icons.alarm, size: 13, color: SsuColors.tagWarning),
            const SizedBox(width: SsuSpace.xxs),
          ],
          Expanded(child: Text(value, style: valueStyle)),
        ],
      ),
    );
  }
}

/// 신청 버튼.
///
/// 앱이 신청을 대행하지 않는다. SSUPath 링크로 보낼 뿐이다 —
/// 사용자 학번·비밀번호를 수집하지 않는다는 설계 결정의 귀결.
class _ApplyBar extends StatelessWidget {
  const _ApplyBar({required this.notice});

  final Notice notice;

  @override
  Widget build(BuildContext context) {
    final closed = notice.isClosed();
    final url = notice.url;

    return DecoratedBox(
      decoration: const BoxDecoration(
        color: SsuColors.canvas,
        border: Border(top: BorderSide(color: SsuColors.hairline)),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.all(SsuSpace.sm),
          child: Center(
            child: ConstrainedBox(
              constraints:
                  const BoxConstraints(maxWidth: SsuLayout.contentWidth),
              child: FilledButton.icon(
                icon: const Icon(Icons.open_in_new, size: 16),
                label: Text(closed ? '모집이 종료되었습니다' : 'SSUPath 에서 신청하기'),
                onPressed:
                    closed || url.isEmpty ? null : () => _open(context, url),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _open(BuildContext context, String url) async {
    final messenger = ScaffoldMessenger.of(context);
    final uri = Uri.tryParse(url);
    if (uri == null) {
      messenger.showSnackBar(const SnackBar(content: Text('잘못된 링크입니다')));
      return;
    }
    final opened = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!opened) {
      messenger.showSnackBar(const SnackBar(content: Text('링크를 열지 못했습니다')));
    }
  }
}
