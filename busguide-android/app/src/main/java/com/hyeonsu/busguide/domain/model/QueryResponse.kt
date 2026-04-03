package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** 음성 질의 응답 — 서버 → 앱 */
@Serializable
data class QueryResponse(
    @SerialName("answer_text") val answerText: String,
    @SerialName("answer_tts") val answerTts: String,
    val buses: List<BusArrival>,
    val intent: String,
    val destination: String?,
)
