package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** 버스 도착 정보 — "58번 | 5분 후 | 1정거장 전" */
@Serializable
data class BusArrival(
    @SerialName("bus_number") val busNumber: String,
    @SerialName("arrival_min") val arrivalMin: Int,
    @SerialName("remaining_stops") val remainingStops: Int,
    val destination: String,
)
