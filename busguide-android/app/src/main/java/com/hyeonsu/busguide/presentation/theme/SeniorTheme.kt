package com.hyeonsu.busguide.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

/** BusGuide 시니어 테마 — 항상 다크 모드 (고대비 유지) */
private val SeniorColorScheme = darkColorScheme(
    primary = SeniorPrimary,
    onPrimary = SeniorBackground,
    secondary = SeniorSecondary,
    background = SeniorBackground,
    onBackground = SeniorOnBackground,
    surface = SeniorSurface,
    onSurface = SeniorOnSurface,
    error = SeniorError,
)

@Composable
fun BusGuideTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = SeniorColorScheme, typography = SeniorTypography, content = content)
}
