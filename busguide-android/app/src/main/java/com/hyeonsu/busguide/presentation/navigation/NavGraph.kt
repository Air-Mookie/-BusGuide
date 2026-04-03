package com.hyeonsu.busguide.presentation.navigation

import androidx.compose.runtime.*
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.hyeonsu.busguide.presentation.main.MainScreen
import com.hyeonsu.busguide.presentation.main.MainViewModel
import com.hyeonsu.busguide.presentation.result.ResultScreen
import com.hyeonsu.busguide.speech.SpeechManager
import com.hyeonsu.busguide.speech.TtsManager

/** 네비게이션 그래프 — main ↔ result */
@Composable
fun BusGuideNavGraph(
    navController: NavHostController,
    speechManager: SpeechManager,
    ttsManager: TtsManager,
) {
    val mainViewModel: MainViewModel = hiltViewModel()

    NavHost(navController = navController, startDestination = "main") {
        composable("main") {
            MainScreen(viewModel = mainViewModel, speechManager = speechManager,
                onNavigateToResult = { navController.navigate("result") })
        }
        composable("result") {
            val response = mainViewModel.uiState.collectAsState().value.response
            if (response != null) {
                ResultScreen(response = response, ttsManager = ttsManager,
                    onAskAgain = { mainViewModel.clearResponse(); navController.popBackStack() },
                    onGoHome = { mainViewModel.clearResponse(); navController.popBackStack("main", inclusive = false) })
            }
        }
    }
}
