import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'tokens.dart';

/// DESIGN.md 를 ThemeData 로 옮긴 것.
///
/// SSUPath 는 woff2 만 제공하고 Flutter 는 ttf/otf 를 쓰므로 원본 파일을
/// 그대로 가져올 수 없다. Noto Sans KR·Poppins 둘 다 Google Fonts 에 있어
/// 같은 서체를 쓴다.
abstract final class AppTheme {
  static ThemeData light() {
    const colorScheme = ColorScheme.light(
      primary: SsuColors.navy,
      onPrimary: Colors.white,
      secondary: SsuColors.teal,
      onSecondary: Colors.white,
      tertiary: SsuColors.cyan,
      surface: SsuColors.surface,
      onSurface: SsuColors.textBody,
      error: SsuColors.danger,
      onError: Colors.white,
      outline: SsuColors.border,
      outlineVariant: SsuColors.borderSoft,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: SsuColors.surface,
      dividerColor: SsuColors.borderSoft,
      disabledColor: SsuColors.textFaint,
      hintColor: SsuColors.textFaint,
      textTheme: _textTheme(),

      // 원본은 그림자를 거의 쓰지 않는다. Material 기본 elevation 을 끈다.
      appBarTheme: const AppBarTheme(
        backgroundColor: SsuColors.surface,
        foregroundColor: SsuColors.textStrong,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        shape: Border(
          bottom: BorderSide(color: SsuColors.borderSoft),
        ),
      ),

      cardTheme: const CardThemeData(
        color: SsuColors.surface,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(SsuRadius.lg)),
        ),
      ),

      dividerTheme: const DividerThemeData(
        color: SsuColors.borderSoft,
        thickness: 1,
        space: 1,
      ),

      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: SsuColors.surface,
        elevation: 0,
        height: 64,
        indicatorColor: SsuColors.teal.withValues(alpha: 0.12),
        surfaceTintColor: Colors.transparent,
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(
            color: selected ? SsuColors.navy : SsuColors.textFaint,
            size: 24,
          );
        }),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return GoogleFonts.notoSansKr(
            fontSize: 12,
            fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
            color: selected ? SsuColors.navy : SsuColors.textFaint,
          );
        }),
      ),

      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: SsuColors.navy,
          foregroundColor: Colors.white,
          disabledBackgroundColor: SsuColors.border,
          disabledForegroundColor: SsuColors.textFaint,
          minimumSize: const Size.fromHeight(SsuLayout.minTouchTarget),
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(SsuRadius.md)),
          ),
          textStyle: GoogleFonts.notoSansKr(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: SsuColors.teal,
          side: const BorderSide(color: SsuColors.teal),
          minimumSize: const Size.fromHeight(SsuLayout.minTouchTarget),
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(SsuRadius.md)),
          ),
        ),
      ),

      snackBarTheme: SnackBarThemeData(
        backgroundColor: SsuColors.textStrong,
        contentTextStyle: GoogleFonts.notoSansKr(
          fontSize: 14,
          color: Colors.white,
        ),
        behavior: SnackBarBehavior.floating,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(SsuRadius.md)),
        ),
      ),

      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: SsuColors.teal,
      ),

      splashColor: SsuColors.teal.withValues(alpha: 0.12),
      highlightColor: SsuColors.teal.withValues(alpha: 0.06),
    );
  }

  /// DESIGN.md 3절 타입 스케일.
  ///
  /// 한글은 라틴보다 넓은 행간이 필요하다 — 제목 1.35, 본문 1.6.
  static TextTheme _textTheme() {
    TextStyle body(double size, FontWeight weight, Color color, double height) =>
        GoogleFonts.notoSansKr(
          fontSize: size,
          fontWeight: weight,
          color: color,
          height: height,
        );

    return TextTheme(
      displayLarge: body(24, FontWeight.w600, SsuColors.textStrong, 1.35),
      titleLarge: body(20, FontWeight.w600, SsuColors.textStrong, 1.35),
      titleMedium: body(18, FontWeight.w600, SsuColors.textStrong, 1.35),
      bodyLarge: body(16, FontWeight.w400, SsuColors.textBody, 1.6),
      bodyMedium: body(15, FontWeight.w400, SsuColors.textBody, 1.6),
      // 원본 최다 사용값(287회)이 14px 이다. 실질 기본 크기.
      bodySmall: body(14, FontWeight.w400, SsuColors.textMuted, 1.6),
      labelMedium: body(13, FontWeight.w400, Colors.white, 1.0),
      labelSmall: body(12, FontWeight.w400, SsuColors.textFaint, 1.4),
    );
  }

  /// 숫자·영문 강조용. 인원수, D-day 에 쓴다.
  static TextStyle numeric({
    double size = 13,
    Color color = Colors.white,
    FontWeight weight = FontWeight.w600,
  }) =>
      GoogleFonts.poppins(
        fontSize: size,
        fontWeight: weight,
        color: color,
        height: 1.0,
      );
}
