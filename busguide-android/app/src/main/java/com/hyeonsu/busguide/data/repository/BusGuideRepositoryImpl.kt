package com.hyeonsu.busguide.data.repository

import com.hyeonsu.busguide.data.remote.BusGuideApi
import com.hyeonsu.busguide.domain.model.*
import com.hyeonsu.busguide.domain.repository.BusGuideRepository
import javax.inject.Inject

/** Repository 구현체 — API 호출을 Result로 감싸서 에러 처리 */
class BusGuideRepositoryImpl @Inject constructor(
    private val api: BusGuideApi,
) : BusGuideRepository {
    override suspend fun sendQuery(request: QueryRequest): Result<QueryResponse> =
        runCatching { api.sendQuery(request) }
    override suspend fun getNearestStation(lat: Double, lng: Double): Result<Station> =
        runCatching { api.getNearestStation(lat, lng) }
    override suspend fun getPresets(region: String): Result<PresetResponse> =
        runCatching { api.getPresets(region) }
}
