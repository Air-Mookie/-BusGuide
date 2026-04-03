package com.hyeonsu.busguide.speech

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 음성 인식(STT) 관리자
 * - Android SpeechRecognizer 래핑
 * - 한국어 음성 → 텍스트 변환
 * - StateFlow로 Compose UI와 연동
 */
class SpeechManager(private val context: Context) {

    /** 음성 인식 상태 */
    sealed class State {
        data object Idle : State()
        data object Listening : State()
        data class Result(val text: String) : State()
        data class Error(val message: String) : State()
    }

    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    private var recognizer: SpeechRecognizer? = null

    /** 음성 인식 시작 — 한국어, 3초 무음 시 자동 종료 */
    fun startListening() {
        recognizer?.destroy()
        recognizer = SpeechRecognizer.createSpeechRecognizer(context)

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ko-KR")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 3000L)
        }

        recognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) { _state.value = State.Listening }
            override fun onResults(results: Bundle?) {
                val text = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull() ?: ""
                _state.value = if (text.isNotEmpty()) State.Result(text) else State.Error("말씀을 못 알아들었어요")
            }
            override fun onError(error: Int) {
                _state.value = State.Error(when (error) {
                    SpeechRecognizer.ERROR_NO_MATCH -> "말씀을 못 알아들었어요"
                    SpeechRecognizer.ERROR_NETWORK -> "인터넷 연결을 확인해주세요"
                    SpeechRecognizer.ERROR_AUDIO -> "마이크에 문제가 있어요"
                    else -> "다시 말씀해주세요"
                })
            }
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
        recognizer?.startListening(intent)
    }

    fun stopListening() { recognizer?.stopListening(); _state.value = State.Idle }
    fun reset() { _state.value = State.Idle }
    fun destroy() { recognizer?.destroy(); recognizer = null }
}
