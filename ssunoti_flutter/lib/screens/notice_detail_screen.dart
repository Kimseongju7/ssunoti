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
            icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border),
            color: isFavorite ? SsuColors.favorite : SsuColors.textFaint,
            tooltip: isFavorite ? '찜 해제' : '찜하기',
            onPressed: () =>
                ref.read(favoriteIdsProvider.notifier).toggle(noticeId),
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints:
              const BoxConstraints(maxWidth: SsuLayout.maxContentWidth),
          child: ListView(
            padding: const EdgeInsets.all(SsuSpace.lg),
            children: [
              Text(
                notice.title,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: notice.isClosed()
                          ? SsuColors.textDisabled
                          : SsuColors.textStrong,
                    ),
              ),
              const SizedBox(height: SsuSpace.md),
              _StatusRow(notice: notice),
              const SizedBox(height: SsuSpace.xxl),
              InfoBox(child: _InfoTable(notice: notice)),
              if (notice.content.isNotEmpty) ...[
                const SizedBox(height: SsuSpace.xxl),
                Text(
                  notice.content,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
              const SizedBox(height: SsuSpace.xxl),
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
    final closed = notice.isClosed();
    return Wrap(
      spacing: SsuSpace.xs,
      runSpacing: SsuSpace.xs,
      children: [
        closed
            ? const StatusPill(label: '종료', background: SsuColors.statusClosed)
            : const StatusPill(label: '모집중', background: SsuColors.statusOpen),
        if (notice.deadline == null)
          const StatusPill(
            label: '상시모집',
            background: SsuColors.statusWaiting,
          ),
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
    final valueStyle = numeric
        ? AppTheme.numeric(
            size: 15,
            color: highlight ? SsuColors.warning : SsuColors.textStrong,
          )
        : Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: highlight ? SsuColors.warning : SsuColors.textStrong,
            );

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SsuSpace.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 88,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          if (highlight) ...[
            const Icon(Icons.alarm, size: 15, color: SsuColors.warning),
            const SizedBox(width: SsuSpace.xs),
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

    return SafeArea(
      child: Container(
        decoration: const BoxDecoration(
          border: Border(top: BorderSide(color: SsuColors.borderSoft)),
        ),
        padding: const EdgeInsets.all(SsuSpace.md),
        child: Center(
          child: ConstrainedBox(
            constraints:
                const BoxConstraints(maxWidth: SsuLayout.maxContentWidth),
            child: DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(SsuRadius.md),
                // 회색이 아니라 브랜드 청록이 섞인 그림자. 원본 값 그대로.
                boxShadow:
                    closed || url.isEmpty ? SsuShadow.none : SsuShadow.brand,
              ),
              child: FilledButton.icon(
                icon: const Icon(Icons.open_in_new, size: 18),
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
