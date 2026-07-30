import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../theme/tokens.dart';

/// SSUPath 의 상태 라벨.
///
/// 원본 `.label_box > span` 을 그대로 옮겼다:
/// `padding: 5px 15px; border-radius: 50px; font-size: 13px; line-height: 1`
/// 글자는 항상 흰색이다 — 예외 없음.
///
/// 학생이 SSUPath 에서 이미 익힌 시각 규칙이라 형태를 바꾸지 않는다.
class StatusPill extends StatelessWidget {
  const StatusPill({
    super.key,
    required this.label,
    required this.background,
    this.icon,
    this.useNumericFont = false,
  });

  final String label;
  final Color background;

  /// 색에만 의존하지 않기 위한 아이콘. 경고 계열에는 반드시 넣는다.
  /// 근거: DESIGN.md 7절 — 색약 사용자와 흑백 화면에서도 읽혀야 한다.
  final IconData? icon;

  /// 숫자가 주인 라벨(인원수, D-day)은 Poppins 600 을 쓴다.
  final bool useNumericFont;

  @override
  Widget build(BuildContext context) {
    final textStyle = useNumericFont
        ? AppTheme.numeric(size: 13)
        : Theme.of(context).textTheme.labelMedium;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 5),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(SsuRadius.pill),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 13, color: Colors.white),
            const SizedBox(width: SsuSpace.xs),
          ],
          Text(label, style: textStyle),
        ],
      ),
    );
  }
}

/// 정보 박스. 원본 `.etc_cont` 를 그대로 옮겼다.
///
/// `padding: 12px 20px; border: 1px solid #E6E6E6; border-radius: 10px;
/// background: #FDFDFD`
class InfoBox extends StatelessWidget {
  const InfoBox({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: SsuSpace.xl,
        vertical: SsuSpace.md,
      ),
      decoration: BoxDecoration(
        color: SsuColors.surfaceSubtle,
        border: Border.all(color: SsuColors.border),
        borderRadius: BorderRadius.circular(SsuRadius.lg),
      ),
      child: child,
    );
  }
}

/// 파선 구분선. 원본 `border-top: 1px dashed #E8E8E8`.
///
/// Flutter 에 파선 Border 가 없어 직접 그린다. 실선으로 바꾸면 원본의
/// 특징적인 질감이 사라진다.
class DashedDivider extends StatelessWidget {
  const DashedDivider({
    super.key,
    this.color = SsuColors.borderSoft,
    this.dashWidth = 3,
    this.dashGap = 3,
  });

  final Color color;
  final double dashWidth;
  final double dashGap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 1,
      width: double.infinity,
      child: CustomPaint(
        painter: _DashedLinePainter(
          color: color,
          dashWidth: dashWidth,
          dashGap: dashGap,
        ),
      ),
    );
  }
}

class _DashedLinePainter extends CustomPainter {
  const _DashedLinePainter({
    required this.color,
    required this.dashWidth,
    required this.dashGap,
  });

  final Color color;
  final double dashWidth;
  final double dashGap;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1;

    var x = 0.0;
    while (x < size.width) {
      canvas.drawLine(Offset(x, 0), Offset(x + dashWidth, 0), paint);
      x += dashWidth + dashGap;
    }
  }

  @override
  bool shouldRepaint(_DashedLinePainter oldDelegate) =>
      oldDelegate.color != color ||
      oldDelegate.dashWidth != dashWidth ||
      oldDelegate.dashGap != dashGap;
}
