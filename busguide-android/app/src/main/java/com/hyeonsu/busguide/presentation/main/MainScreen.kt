package com.hyeonsu.busguide.presentation.main

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.hyeonsu.busguide.domain.model.Preset
import com.hyeonsu.busguide.speech.SpeechManager

/** 메인 화면 — 큰 "말하기" 버튼 + 자주 가는 곳 프리셋 */
@Composable
fun MainScreen(
    viewModel: MainViewModel = hiltViewModel(),
    speechManager: SpeechManager,
    onNavigateToResult: () -> Unit,
) {
    val uiState by viewModel.uiState.collectAsState()
    val speechState by speechManager.state.collectAsState()
    val haptic = LocalHapticFeedback.current

    // 음성 인식 결과 → 서버 질의
    LaunchedEffect(speechState) {
        if (speechState is SpeechManager.State.Result) {
            viewModel.sendQuery((speechState as SpeechManager.State.Result).text)
            speechManager.reset()
        }
    }

    // 서버 응답 → 결과 화면 이동
    LaunchedEffect(uiState.response) {
        if (uiState.response != null) onNavigateToResult()
    }

    Column(
        modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // 현재 정류장
        Text(
            text = "현재 정류장: ${uiState.currentStation}",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onBackground,
        )
        Spacer(modifier = Modifier.height(24.dp))

        // 안내 문구
        Text(
            text = "어디 가시려고요?",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.onBackground,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(40.dp))

        // 말하기 버튼 — 10cm 원형
        Button(
            onClick = { haptic.performHapticFeedback(HapticFeedbackType.LongPress); speechManager.startListening() },
            modifier = Modifier.size(240.dp),
            shape = CircleShape,
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary),
        ) {
            Text(
                text = if (speechState is SpeechManager.State.Listening) "듣고 있어요..." else "말하기",
                style = MaterialTheme.typography.displayLarge,
                color = MaterialTheme.colorScheme.onPrimary,
            )
        }
        Spacer(modifier = Modifier.height(40.dp))

        // 에러 표시
        uiState.error?.let {
            Text(text = it, style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.error, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(16.dp))
        }

        // 로딩
        if (uiState.isLoading) {
            CircularProgressIndicator(modifier = Modifier.size(60.dp), color = MaterialTheme.colorScheme.primary, strokeWidth = 6.dp)
            Spacer(modifier = Modifier.height(16.dp))
        }

        // 자주 가는 곳
        Text(text = "자주 가는 곳", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onBackground)
        Spacer(modifier = Modifier.height(16.dp))

        LazyVerticalGrid(
            columns = GridCells.Fixed(3),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            items(uiState.presets) { preset ->
                PresetButton(preset = preset, onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    viewModel.sendQuery("${preset.name} 가는 버스")
                })
            }
        }
    }
}

/** 프리셋 버튼 — 최소 120dp x 80dp */
@Composable
private fun PresetButton(preset: Preset, onClick: () -> Unit) {
    Button(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().height(80.dp),
        shape = RoundedCornerShape(16.dp),
        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.surface),
    ) {
        Text(text = preset.name, style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurface)
    }
}
