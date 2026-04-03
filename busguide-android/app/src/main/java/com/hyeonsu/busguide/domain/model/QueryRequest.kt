package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** 음성 질의 요청 — 앱 → 서버 */
@Serializable
data class QueryRequest(
    val text: String,
    @SerialName("station_id") val stationId: String,
    @SerialName("session_id") val sessionId: String,
)
