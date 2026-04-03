package com.hyeonsu.busguide.domain.repository

import com.hyeonsu.busguide.domain.model.*

/** 데이터 접근 계층 인터페이스 */
interface BusGuideRepository {
    suspend fun sendQuery(request: QueryRequest): Result<QueryResponse>
    suspend fun getNearestStation(lat: Double, lng: Double): Result<Station>
    suspend fun getPresets(region: String): Result<PresetResponse>
}
