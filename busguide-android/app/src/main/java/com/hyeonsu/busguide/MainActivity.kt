package com.hyeonsu.busguide

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.navigation.compose.rememberNavController
import com.hyeonsu.busguide.kiosk.KioskManager
import com.hyeonsu.busguide.presentation.navigation.BusGuideNavGraph
import com.hyeonsu.busguide.presentation.theme.BusGuideTheme
import com.hyeonsu.busguide.speech.SpeechManager
import com.hyeonsu.busguide.speech.TtsManager
import dagger.hilt.android.AndroidEntryPoint

/**
 * BusGuide 메인 액티비티
 * - 음성 매니저(STT/TTS) 초기화
 * - 키오스크 모드 활성화
 * - 네비게이션 설정
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private lateinit var speechManager: SpeechManager
    private lateinit var ttsManager: TtsManager
    private lateinit var kioskManager: KioskManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 음성 매니저 초기화
        speechManager = SpeechManager(this)
        ttsManager = TtsManager(this)
        kioskManager = KioskManager(this)

        // 키오스크 모드 활성화 (전체화면 + 화면 꺼짐 방지)
        kioskManager.enable()

        setContent {
            BusGuideTheme {
                val navController = rememberNavController()
                BusGuideNavGraph(
                    navController = navController,
                    speechManager = speechManager,
                    ttsManager = ttsManager,
                )
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        speechManager.destroy()
        ttsManager.destroy()
    }
}
