package com.hyeonsu.busguide.presentation.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/** 시니어 특화 타이포그래피 — 최소 24sp, 핵심 48sp */
val SeniorTypography = Typography(
    displayLarge = TextStyle(fontSize = 48.sp, fontWeight = FontWeight.Bold, lineHeight = 56.sp),
    headlineLarge = TextStyle(fontSize = 36.sp, fontWeight = FontWeight.Bold, lineHeight = 44.sp),
    headlineMedium = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Bold, lineHeight = 40.sp),
    bodyLarge = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Normal, lineHeight = 36.sp),
    bodyMedium = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Normal, lineHeight = 32.sp),
)
