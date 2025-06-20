import Foundation
import Speech
#if os(visionOS)
import RealityKit   // visionOS下使用RealityKit
#else
import RealityKit  // iOS下也尽量使用RealityKit
import ARKit       // 保留ARKit以检测语音控制相关权限
#endif

enum VisualInputMode: String, CaseIterable, Identifiable {
    case voice = "Voice Control"
    var id: String { self.rawValue }
}

final class VisualInputManager: NSObject, ObservableObject {
    static let shared = VisualInputManager()
    
    @Published var isActive: Bool = false
    var currentMode: VisualInputMode?

    // Voice control properties
    private var speechRecognizer: SFSpeechRecognizer? = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    
    // Public interface
    func start(mode: VisualInputMode) {
        currentMode = mode
        isActive = true
        // 仅保留语音控制处理
        startSpeechRecognition()
        print("Voice control mode activated")
        printHelpInstructions()
    }
    
    func stop() {
        isActive = false
        stopSpeechRecognition()
        print("Voice control mode deactivated")
        currentMode = nil
    }
    
    // MARK: - Voice Control using Speech Framework
    private func startSpeechRecognition() {
        SFSpeechRecognizer.requestAuthorization { authStatus in
            guard authStatus == .authorized else {
                print("Speech recognition authorization failed")
                return
            }
            DispatchQueue.main.async {
                self.setupAndStartAudioEngine()
                print("Speech recognition started")
            }
        }
    }
    
    private func setupAndStartAudioEngine() {
        recognitionTask?.cancel()
        recognitionTask = nil
        
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        let inputNode = audioEngine.inputNode
        
        guard let recognitionRequest = recognitionRequest else {
            fatalError("Unable to create a speech recognition request")
        }
        recognitionRequest.shouldReportPartialResults = true
        
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                let spokenText = result.bestTranscription.formattedString.lowercased()
                if spokenText.contains("click") {
                    print("Voice command detected: Click action")
                } else if spokenText.contains("hover") {
                    print("Voice command detected: Hover action")
                } else if spokenText.contains("release") {
                    print("Voice command detected: Release action")
                } else {
                    print("Voice command: Unrecognized command -> \(spokenText)")
                }
            }
            if error != nil || (result?.isFinal ?? false) {
                self.audioEngine.stop()
                inputNode.removeTap(onBus: 0)
                self.recognitionRequest = nil
                self.recognitionTask = nil
            }
        }
        
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            self.recognitionRequest?.append(buffer)
        }
        
        do {
            audioEngine.prepare()
            try audioEngine.start()
        } catch {
            print("AudioEngine couldn't start: \(error.localizedDescription)")
        }
    }
    
    private func stopSpeechRecognition() {
        audioEngine.stop()
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        recognitionTask = nil
        print("Speech recognition stopped")
    }
    
    // MARK: - Help Instructions
    private func printHelpInstructions() {
        let helpText = """
        [Visual Input Help / 視覺輸入提示]
        ------------------------------------------
        For optimal experience, please enable the following in your Accessibility settings:
        
        1. Voice Control (語音控制):
           - Open Settings → Accessibility → Voice Control and ensure it is enabled.
           - Use voice commands (e.g., "click", "hover", or "release") to simulate touch actions.
           - 咁樣你就可以用語音指令（例如 "click", "hover" 或 "release"）操控應用程式。
        
        2. Dwell Control (停留控制):
           - Open Settings → Accessibility → Dwell Control and ensure it is enabled.
           - This will allow a prolonged gaze to simulate a tap.
           - 請打開「設定」→「輔助功能」→「停留控制」確保已開啟，咁長時間停留即可以模擬點擊。
        """
        print(helpText)
    }
}

#if !os(visionOS)
import UIKit
extension VisualInputManager {
    // 统一重定向至系统辅助功能设置
    func openAccessibilitySettings() {
        if let url = URL(string: "App-Prefs:root=ACCESSIBILITY") {
            if UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url)
            } else {
                print("Cannot open Accessibility settings")
            }
        }
    }
    
    func openVoiceControlSettings() {
        if let url = URL(string: "App-Prefs:root=ACCESSIBILITY&path=VOICE_CONTROL") {
            if UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url)
            } else {
                print("Cannot open Voice Control settings")
            }
        }
    }
    
    func openDwellControlSettings() {
        if let url = URL(string: "App-Prefs:root=ACCESSIBILITY&path=DWELL_CONTROL") {
            if UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url)
            } else {
                print("Cannot open Dwell Control settings")
            }
        }
    }
}
#else
extension VisualInputManager {
    func openAccessibilitySettings() {
        // visionOS下无法直接跳转，提示用户手动打开设置
        print("请手动打开设置 → 辅助功能，启用语音控制和停留控制。")
    }
    
    func openVoiceControlSettings() {
        print("請手動打開設置 → 輔助功能，啟用語音控制。")
    }
    
    func openDwellControlSettings() {
        print("請手動打開設置 → 輔助功能，啟用停留控制。")
    }
}
#endif
