# Mathion

Mathion is an innovative Vision OS application that integrates a math formula keyboard with advanced visual input control. Users can enter mathematical expressions, see live LaTeX-rendered output, and interact with the app using either voice commands or eye control (through AR face tracking).

## Overview

Mathion combines these major components:
- **Math Keyboard:** A digital keypad that lets you construct complex mathematical formulas with buttons for numbers, operators, and common LaTeX commands. The input is rendered using KaTeX.
- **Visual Input:** Leverages both voice recognition and ARKit-based eye control to simulate touch interactions within the app.
- **Configurable AR Settings:** Customize AR face tracking options such as light estimation and world alignment to enhance eye control accuracy.

## Features

- **Math Keyboard & LaTeX Rendering**
  - Intuitive design with digital clock style input and beautifully rendered output.
  - Export capability for sharing formulas.
  
- **Voice Control**
  - Uses the Speech framework to recognize commands:
    - Say "click" for click action.
    - Say "hover" for hover action.
    - Say "release" for release action.
  - Provides inline help upon activation.

- **Eye Control**
  - Activates AR face tracking with ARKit.
  - Detects subtle gestures:
    - **Nodding** (head pitch > 0.35 rad) simulates a click.
    - **Strong blink** (both eyes blink > 0.8) simulates a release.
    - Otherwise interprets as hover.
  - Supports additional AR configuration options:
    - **Light Estimation:** Toggle for improved ambient lighting.
    - **World Alignment:** Choose between gravity, gravity & heading, or camera alignment.

## VisionOS Support

Some AR features of Mathion are available on visionOS. Note that visionOS introduces new frameworks:
- Instead of using ARKit exclusively, visionOS leverages RealityKit and RealityKit for VisionOS.
- When building for visionOS, ensure your code conditionally imports and uses the appropriate APIs.
- The VisualInputManager employs compile flags (e.g. `#if os(visionOS)`) to switch to RealityKit-related functionality as needed.
- You may need to fine-tune gesture thresholds and tracking mechanisms on visionOS.

Please refer to the platform-specific documentation for RealityKit for VisionOS for details on performance and API differences.

## Architecture

- **MathionApp.swift**  
  Entry point for the SwiftUI app.

- **ContentView.swift**  
  Wraps the main UI with navigation to Options and MathKeyboardView.

- **MathKeyboardView.swift**  
  Implements the custom math keyboard view with LaTeX rendering using a WebKit-based LaTeX view.

- **VisualInputManager.swift**  
  Centralizes voice and eye control logic:
  - Uses the Speech framework for voice commands.
  - Employs ARKit for eye control, utilizing real-time face tracking data.
  - Provides detailed usage instructions with `printHelpInstructions()`.

- **OptionsView.swift**  
  Contains settings to toggle visual input and customize AR options like light estimation and world alignment.

- **RealityKitContent Package**
  - A separate package for integrating RealityKit-based content if needed.

## Requirements

- Xcode 15 or later.
- iOS 16 or later.
- Device supporting ARFaceTracking for eye control.
- Internet access for loading remote KaTeX assets.

## Setup and Installation

1. **Clone or open** the project in Xcode.
2. **Build and run** the `MathionApp` target.
3. **Enable Visual Input:**  
   - Navigate to the Options page via the app toolbar.  
   - Toggle visual input and select your desired control mode (voice or eye).
   - For eye control, adjust AR settings (light estimation and world alignment) as needed.
4. **Permissions:**  
   - Grant microphone access when prompted for voice commands.
   - Ensure your device supports AR face tracking for eye control.

## Usage

- **Math Keyboard Interaction:**
  - Tap buttons to build formulas in the input area.
  - Watch as the formula is rendered in real time.
  - Use the share function to export your formula.
  - Clear the text editor with the "Clear" button.

- **Visual Input Controls:**
  - **Voice Control:**  
    Speak commands like "click," "hover," or "release" to simulate interactions.
  - **Eye Control:**  
    Use natural gestures:
      - **Nod your head** to trigger a click.
      - **Blink strongly** to release.
      - Maintain gaze to simulate hovering.
  - Detailed command instructions are printed to the console when visual input is enabled.

## Known Issues and Future Improvements

- Fine-tuning AR gesture thresholds for more accurate detection.
- Expansion of voice commands for broader functionality.
- Further UI enhancements for even smoother user experience.
- Integration of user feedback for continuous improvement.

## License

Distributed under the MIT License. See the `LICENSE` file for more details.
