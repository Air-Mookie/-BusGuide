package com.hyeonsu.busguide.speech

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

/**
 * 음성 출력(TTS) 관리자
 * - 한국어 음성으로 버스 안내 읽어주기
 * - 어르신 맞춤: 느린 속도 + 약간 높은 피치
 */
class TtsManager(context: Context) {
    private var tts: TextToSpeech? = null
    private var isReady = false

    init {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.KOREAN
                tts?.setSpeechRate(0.85f)
                tts?.setPitch(1.05f)
                isReady = true
            }
        }
    }

    /** 텍스트를 음성으로 읽어주기 */
    fun speak(text: String) {
        if (!isReady) return
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "busguide_tts")
    }

    fun stop() { tts?.stop() }
    fun destroy() { tts?.stop(); tts?.shutdown(); tts = null }
}
