import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'tokens.dart';

/// DESIGN.md 를 ThemeData 로 옮긴 것.
///
/// **다크 전용이다.** Linear 는 라이트 모드를 만들지 않는다 — DESIGN.md 7절.
abstract final class AppTheme {
  static ThemeData dark() {
    const colorScheme = ColorScheme.dark(
      primary: SsuColors.accent,
      onPrimary: Colors.white,
      secondary: SsuColors.accent,
      onSecondary: Colors.white,
      surface: SsuColors.canvas,
      onSurface: SsuColors.ink,
      surfaceContainer: SsuColors.surface1,
      surfaceContainerHigh: SsuColors.surface2,
      surfaceContainerHighest: SsuColors.surface3,
      error: SsuColors.tagWarning,
      onError: Colors.black,
      outline: SsuColors.hairline,
      outlineVariant: SsuColors.hairlineTertiary,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: SsuColors.canvas,
      dividerColor: SsuColors.hairline,
      disabledColor: SsuColors.inkTertiary,
      hintColor: SsuColors.inkSubtle,
      textTheme: _textTheme(),

      // 그림자를 쓰지 않는다. 깊이는 표면 사다리와 실선으로만.
      appBarTheme: const AppBarTheme(
        backgroundColor: SsuColors.canvas,
        foregroundColor: SsuColors.ink,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        toolbarHeight: 56,
        shape: Border(bottom: BorderSide(color: SsuColors.hairline)),
      ),

      cardTheme: const CardThemeData(
        color: SsuColors.surface1,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          side: BorderSide(color: SsuColors.hairline),
          borderRadius: BorderRadius.all(Radius.circular(SsuRadius.lg)),
        ),
      ),

      dividerTheme: const DividerThemeData(
        color: SsuColors.hairline,
        thickness: 1,
        space: 1,
      ),

      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: SsuColors.surface3,
        elevation: 0,
        height: 56,
        indicatorColor: SsuColors.accent.withValues(alpha: 0.16),
        surfaceTintColor: Colors.transparent,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(
            color: selected ? SsuColors.ink : SsuColors.inkSubtle,
            size: 20,
          );
        }),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return _latin(
            13,
            selected ? FontWeight.w500 : FontWeight.w400,
            selected ? SsuColors.ink : SsuColors.inkSubtle,
            1.5,
          );
        }),
      ),

      filledButtonTheme: FilledButtonThemeData(
        style: ButtonStyle(
          backgroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.disabled)) {
              return SsuColors.surface2;
            }
            if (states.contains(WidgetState.pressed)) {
              return SsuColors.accentFocus;
            }
            if (states.contains(WidgetState.hovered)) {
              return SsuColors.accentHover;
            }
            return SsuColors.accent;
          }),
          foregroundColor: WidgetStateProperty.resolveWith((states) =>
              states.contains(WidgetState.disabled)
                  ? SsuColors.inkTertiary
                  : Colors.white),
          // 주요 버튼을 pill 로 만들지 않는다. 8px 고정.
          shape: const WidgetStatePropertyAll(
            RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(SsuRadius.md)),
            ),
          ),
          padding: const WidgetStatePropertyAll(
            EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          ),
          minimumSize: const WidgetStatePropertyAll(
            Size.fromHeight(SsuLayout.minTouchTarget),
          ),
          elevation: const WidgetStatePropertyAll(0),
          textStyle: WidgetStatePropertyAll(
            _latin(14, FontWeight.w500, Colors.white, 1.2),
          ),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          backgroundColor: SsuColors.surface1,
          foregroundColor: SsuColors.ink,
          side: const BorderSide(color: SsuColors.hairline),
          minimumSize: const Size.fromHeight(SsuLayout.minTouchTarget),
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(SsuRadius.md)),
          ),
        ),
      ),

      snackBarTheme: SnackBarThemeData(
        backgroundColor: SsuColors.surface2,
        contentTextStyle: _latin(13, FontWeight.w400, SsuColors.ink, 1.5),
        behavior: SnackBarBehavior.floating,
        shape: const RoundedRectangleBorder(
          side: BorderSide(color: SsuColors.hairline),
          borderRadius: BorderRadius.all(Radius.circular(SsuRadius.md)),
        ),
      ),

      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: SsuColors.accent,
      ),

      splashColor: SsuColors.accent.withValues(alpha: 0.10),
      highlightColor: SsuColors.surface1,
    );
  }

  /// Inter + Noto Sans KR 폴백.
  ///
  /// Inter 에는 한글 글리프가 없다. `fontFamilyFallback` 으로 한글만
  /// Noto Sans KR 로 넘긴다 — 라틴·숫자는 Inter 가 그린다.
  static TextStyle _latin(
    double size,
    FontWeight weight,
    Color color,
    double height, [
    double spacing = 0,
  ]) =>
      GoogleFonts.inter(
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: height,
        letterSpacing: spacing,
      ).copyWith(
        fontFamilyFallback: [GoogleFonts.notoSansKr().fontFamily!],
      );

  /// DESIGN.md 3절 타입 스케일.
  ///
  /// 자간은 원본보다 완화했다. Linear 는 디스플레이에 -3.0px 까지 주지만
  /// 한글은 자모 간격이 조밀해 그 정도면 글자가 뭉친다.
  static TextTheme _textTheme() => TextTheme(
        displayMedium: _latin(32, FontWeight.w600, SsuColors.ink, 1.15, -0.6),
        headlineSmall: _latin(24, FontWeight.w600, SsuColors.ink, 1.20, -0.4),
        titleMedium: _latin(17, FontWeight.w500, SsuColors.ink, 1.35, -0.2),
        titleSmall: _latin(16, FontWeight.w400, SsuColors.inkMuted, 1.45),
        bodyLarge: _latin(15, FontWeight.w400, SsuColors.inkMuted, 1.55),
        bodyMedium: _latin(13, FontWeight.w400, SsuColors.inkMuted, 1.50),
        bodySmall: _latin(12, FontWeight.w400, SsuColors.inkSubtle, 1.40),
        labelLarge: _latin(14, FontWeight.w500, SsuColors.ink, 1.20),
        // eyebrow 만 양수 자간. 분류라는 성격을 드러낸다 (원본 규칙).
        labelMedium: _latin(12, FontWeight.w500, SsuColors.inkSubtle, 1.30, 0.4),
        labelSmall: _latin(12, FontWeight.w400, SsuColors.inkMuted, 1.40),
      );

  /// 숫자 강조. 정원, D-day.
  static TextStyle numeric({
    double size = 12,
    Color color = SsuColors.inkMuted,
    FontWeight weight = FontWeight.w500,
  }) =>
      GoogleFonts.jetBrainsMono(
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: 1.0,
      );
}
