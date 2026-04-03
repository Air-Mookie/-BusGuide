package com.hyeonsu.busguide.presentation.main

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.hyeonsu.busguide.domain.model.Preset
import com.hyeonsu.busguide.domain.model.QueryRequest
import com.hyeonsu.busguide.domain.model.QueryResponse
import com.hyeonsu.busguide.domain.repository.BusGuideRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

/** 메인 화면 ViewModel — 음성 질의, 프리셋 로드, 세션 관리 */
@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: BusGuideRepository,
) : ViewModel() {

    data class UiState(
        val isLoading: Boolean = false,
        val presets: List<Preset> = emptyList(),
        val currentStation: String = "정류장 확인 중...",
        val currentStationId: String = "",
        val response: QueryResponse? = null,
        val error: String? = null,
    )

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState

    private var sessionId: String = UUID.randomUUID().toString()

    init { loadPresets() }

    /** 서버에서 프리셋 목록 로드 */
    private fun loadPresets() {
        viewModelScope.launch {
            repository.getPresets("busan").onSuccess { response ->
                _uiState.value = _uiState.value.copy(presets = response.presets)
            }
        }
    }

    /** 현재 정류장 설정 (GPS에서 호출) */
    fun setCurrentStation(id: String, name: String) {
        _uiState.value = _uiState.value.copy(currentStation = name, currentStationId = id)
    }

    /** 음성 질의 전송 — 프리셋 버튼도 이 함수 사용 */
    fun sendQuery(text: String) {
        val stationId = _uiState.value.currentStationId
        if (stationId.isEmpty()) {
            _uiState.value = _uiState.value.copy(error = "정류장 위치를 확인하고 있어요. 잠시만 기다려주세요.")
            return
        }
        _uiState.value = _uiState.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            val request = QueryRequest(text = text, stationId = stationId, sessionId = sessionId)
            repository.sendQuery(request)
                .onSuccess { response -> _uiState.value = _uiState.value.copy(isLoading = false, response = response) }
                .onFailure { _uiState.value = _uiState.value.copy(isLoading = false, error = "인터넷 연결을 확인해주세요") }
        }
    }

    /** 응답 초기화 */
    fun clearResponse() { _uiState.value = _uiState.value.copy(response = null, error = null) }
}
