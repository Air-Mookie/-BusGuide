package com.hyeonsu.busguide.presentation.result

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.hyeonsu.busguide.domain.model.BusArrival
import com.hyeonsu.busguide.domain.model.QueryResponse
import com.hyeonsu.busguide.speech.TtsManager

/** 결과 화면 — 버스 도착 카드 + TTS 자동 재생 */
@Composable
fun ResultScreen(
    response: QueryResponse,
    ttsManager: TtsManager,
    onAskAgain: () -> Unit,
    onGoHome: () -> Unit,
) {
    val haptic = LocalHapticFeedback.current
    LaunchedEffect(response) { ttsManager.speak(response.answerTts) }

    Column(
        modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(text = response.answerText, style = MaterialTheme.typography.headlineLarge, color = MaterialTheme.colorScheme.onBackground, textAlign = TextAlign.Center)
        Spacer(modifier = Modifier.height(32.dp))

        LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.weight(1f)) {
            items(response.buses) { bus -> BusArrivalCard(bus = bus) }
            if (response.buses.isEmpty()) {
                item {
                    Text(text = "도착 예정 버스가 없습니다", style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.error, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
                }
            }
        }
        Spacer(modifier = Modifier.height(24.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = { haptic.performHapticFeedback(HapticFeedbackType.LongPress); ttsManager.stop(); onAskAgain() },
                modifier = Modifier.weight(1f).height(100.dp), shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary),
            ) { Text(text = "다시\n물어보기", style = MaterialTheme.typography.headlineMedium, textAlign = TextAlign.Center) }

            Button(
                onClick = { haptic.performHapticFeedback(HapticFeedbackType.LongPress); ttsManager.stop(); onGoHome() },
                modifier = Modifier.weight(1f).height(100.dp), shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.surface),
            ) { Text(text = "처음으로", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurface, textAlign = TextAlign.Center) }
        }
    }
}

/** 버스 도착 카드 — 번호(크게) + 시간 + 정거장 */
@Composable
private fun BusArrivalCard(bus: BusArrival) {
    Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Row(modifier = Modifier.fillMaxWidth().padding(24.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(text = "${bus.busNumber}번", style = MaterialTheme.typography.displayLarge, color = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.width(24.dp))
            Column {
                Text(text = "${bus.arrivalMin}분 후 도착", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.secondary)
                Text(text = "${bus.remainingStops}정거장 전", style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.onSurface)
            }
        }
    }
}
