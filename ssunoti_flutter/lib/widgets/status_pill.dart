import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../theme/tokens.dart';

/// 상태 배지. Linear `status-badge` 를 확장했다.
///
/// **배경은 상태와 무관하게 항상 `surface2` 다.** 상태는 좌측 6px 점의
/// 색으로만 말한다. 색을 면적으로 쓰면 어두운 캔버스 위에 색 덩어리가 생겨
/// 제목이 묻힌다 — DESIGN.md 2·4절.
class StatusPill extends StatelessWidget {
  const StatusPill({
    super.key,
    required this.label,
    this.dotColor,
    this.icon,
    this.useNumericFont = false,
  });

  final String label;

  /// 상태 점 색. null 이면 점을 그리지 않는다(분류 배지).
  final Color? dotColor;

  /// 색에만 의존하지 않기 위한 아이콘. 경고 계열에는 반드시 넣는다.
  /// 근거: DESIGN.md 7절 — 색약 사용자와 흑백 화면에서도 읽혀야 한다.
  final IconData? icon;

  /// 숫자가 주인 배지(인원수, D-day)는 JetBrains Mono 를 쓴다.
  final bool useNumericFont;

  @override
  Widget build(BuildContext context) {
    final textStyle = useNumericFont
        ? AppTheme.numeric()
        : Theme.of(context).textTheme.labelSmall;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: SsuSpace.xs, vertical: 3),
      decoration: BoxDecoration(
        color: SsuColors.surface2,
        borderRadius: BorderRadius.circular(SsuRadius.pill),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (dotColor != null) ...[
            Container(
              width: SsuLayout.statusDot,
              height: SsuLayout.statusDot,
              decoration: BoxDecoration(
                color: dotColor,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: SsuSpace.sm - 6),
          ],
          if (icon != null) ...[
            Icon(icon, size: 12, color: SsuColors.inkMuted),
            const SizedBox(width: SsuSpace.xxs),
          ],
          Text(label, style: textStyle),
        ],
      ),
    );
  }
}

/// 정보 카드. Linear `feature-card`.
///
/// `surface1` + `1px hairline` + `radius 12`. 그림자를 쓰지 않는다 —
/// 깊이는 표면 사다리와 실선으로만 만든다.
class InfoBox extends StatelessWidget {
  const InfoBox({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(SsuSpace.lg - 4),
      decoration: BoxDecoration(
        color: SsuColors.surface1,
        border: Border.all(color: SsuColors.hairline),
        borderRadius: BorderRadius.circular(SsuRadius.lg),
      ),
      child: child,
    );
  }
}
