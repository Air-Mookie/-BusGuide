package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.Serializable

/** 정류장 정보 — GPS 좌표 포함 */
@Serializable
data class Station(
    val id: String,
    val name: String,
    val lat: Double,
    val lng: Double,
)
