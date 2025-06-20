//
//  ContentView.swift
//  MathVisionPro
//
//  Created by 沈梓僮 on 2025/2/4.
//

import SwiftUI
import RealityKit
import RealityKitContent
import ARKit

struct ContentView: View {
    var body: some View {
        VStack(spacing: 50) {
            Text("Welcome to Math Vision Pro")
                .font(.title)
                .padding()
            
            OptionssView()
        }
        .navigationTitle("MathVisionPro")
    }
}

struct OptionssView: View {
    @State private var showMathKeyboard = false
    
    var body: some View {
        VStack(spacing: 20) {
            Button("Normal Mode (普通模式)") {
                VisualInputManager.shared.openVoiceControlSettings()
                showMathKeyboard = true
            }
            .buttonStyle(.bordered)

            Button("Voice Assistance Control (語音辅助控制)") {
                VisualInputManager.shared.openVoiceControlSettings()
                showMathKeyboard = true
            }
            .buttonStyle(.bordered)
            
            Button("Dwell Assistance Control (视觉辅助控制)") {
                VisualInputManager.shared.openDwellControlSettings()
                showMathKeyboard = true
            }
            .buttonStyle(.bordered)
        }
        .fullScreenCover(isPresented: $showMathKeyboard) {
            MathKeyboardView()
        }
        // 或者使用 sheet 如果你想要模态展示：
        // .sheet(isPresented: $showMathKeyboard) {
        //     MathKeyboardView()
        // }
    }
}

#Preview(windowStyle: .automatic) {
    ContentView()
}
