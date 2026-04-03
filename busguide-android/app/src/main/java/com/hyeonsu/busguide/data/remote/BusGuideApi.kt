package com.hyeonsu.busguide.data.remote

import com.hyeonsu.busguide.domain.model.*
import retrofit2.http.*

/** BusGuide 서버 API 인터페이스 — Retrofit */
interface BusGuideApi {
    /** 음성 질의 처리 — 핵심 API */
    @POST("query")
    suspend fun sendQuery(@Body request: QueryRequest): QueryResponse

    /** 특정 정류장의 실시간 도착 정보 */
    @GET("bus/arrivals/{stationId}")
    suspend fun getArrivals(@Path("stationId") stationId: String): List<BusArrival>

    /** GPS 좌표로 가장 가까운 정류장 찾기 */
    @GET("bus/nearest-station")
    suspend fun getNearestStation(@Query("lat") lat: Double, @Query("lng") lng: Double): Station

    /** 지역별 자주 가는 곳 프리셋 */
    @GET("presets/{region}")
    suspend fun getPresets(@Path("region") region: String): PresetResponse

    /** 서버 상태 확인 */
    @GET("health")
    suspend fun healthCheck(): Map<String, String>
}
