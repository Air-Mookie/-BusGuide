package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.Serializable

/** 자주 가는 곳 프리셋 — 서버에서 로드 (하드코딩 X) */
@Serializable
data class Preset(
    val name: String,
    val icon: String,
)

/** 프리셋 응답 */
@Serializable
data class PresetResponse(
    val label: String,
    val presets: List<Preset>,
)
