import SwiftUI
import WebKit

// MARK: - Cursor Manager
class CursorManager: ObservableObject {
    @Published var cursorPosition: Int = 0
    @Published var input: String = ""
    
    func setCursorPosition(_ position: Int) {
            cursorPosition = max(0, min(position, input.count))
    }
    
    func insertAtCursor(_ text: String) {
        let before = String(input.prefix(cursorPosition))
        let after = String(input.suffix(input.count - cursorPosition))
        input = before + text + after
        // 更新光标位置
        cursorPosition += text.count
    }
    
    // 添加删除功能
    func deleteBackward() {
        guard cursorPosition > 0 else { return }
        let before = String(input.prefix(cursorPosition - 1))
        let after = String(input.suffix(input.count - cursorPosition))
        input = before + after
        cursorPosition -= 1
    }
    
    // 添加清除功能
    func clear() {
        input = ""
        cursorPosition = 0
    }
    
    // 移动光标
    func moveCursor(offset: Int) {
        let newPosition = cursorPosition + offset
        cursorPosition = max(0, min(newPosition, input.count))
    }
}

// MARK: - Custom Input View
struct CustomInputView: View {
    @ObservedObject var cursorManager: CursorManager
    @State private var showCursor = true
    
    // 用于测量文本宽度的常量
    private let characterWidth: CGFloat = 10.0 // 预估的每个字符宽度
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            ZStack(alignment: .leading) {
                // 透明的背景层，用于捕获点击
                Color.clear
                    .contentShape(Rectangle())
                    .gesture(
                        DragGesture(minimumDistance: 0)
                            .onEnded { value in
                                let xPosition = value.location.x
                                let estimatedPosition = Int(xPosition / characterWidth)
                                // 确保位置在有效范围内
                                cursorManager.cursorPosition = min(max(0, estimatedPosition), cursorManager.input.count)
                            }
                    )
                
                HStack(spacing: 0) {
                    // 光标之前的文本
                    Text(String(cursorManager.input.prefix(cursorManager.cursorPosition)))
                        .font(.system(.body, design: .monospaced))
                        .foregroundColor(.primary)
                    
                    // 闪烁的光标
                    if showCursor {
                        Rectangle()
                            .frame(width: 2, height: 20)
                            .foregroundColor(.blue)
                    }
                    
                    // 光标之后的文本
                    Text(String(cursorManager.input.suffix(cursorManager.input.count - cursorManager.cursorPosition)))
                        .font(.system(.body, design: .monospaced))
                        .foregroundColor(.primary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 4)
            }
        }
        .onAppear {
            // 光标闪烁动画
            Timer.scheduledTimer(withTimeInterval: 0.6, repeats: true) { _ in
                withAnimation {
                    showCursor.toggle()
                }
            }
        }
    }
}

// MARK: - LaTeX Symbols Library
struct LatexSymbols {
    // 数学常数
    struct Constants {
        static let pi = "\\pi"
        static let e = "\\mathrm{e}"
        static let gamma = "\\gamma"
        static let phi = "\\phi"
        static let infinity = "\\infty"
    }
    
    // 小写希腊字母
    struct GreekLower {
        static let alpha = "\\alpha"
        static let beta = "\\beta"
        static let gamma = "\\gamma"
        static let delta = "\\delta"
        static let epsilon = "\\epsilon"
        static let zeta = "\\zeta"
        static let eta = "\\eta"
        static let theta = "\\theta"
        static let iota = "\\iota"
        static let kappa = "\\kappa"
        static let lambda = "\\lambda"
        static let mu = "\\mu"
        static let nu = "\\nu"
        static let xi = "\\xi"
        static let pi = "\\pi"
        static let rho = "\\rho"
        static let sigma = "\\sigma"
        static let tau = "\\tau"
        static let upsilon = "\\upsilon"
        static let phi = "\\phi"
        static let chi = "\\chi"
        static let psi = "\\psi"
        static let omega = "\\omega"
    }
    
    // 大写希腊字母
    struct GreekUpper {
        static let Gamma = "\\Gamma"
        static let Delta = "\\Delta"
        static let Theta = "\\Theta"
        static let Lambda = "\\Lambda"
        static let Xi = "\\Xi"
        static let Pi = "\\Pi"
        static let Sigma = "\\Sigma"
        static let Upsilon = "\\Upsilon"
        static let Phi = "\\Phi"
        static let Psi = "\\Psi"
        static let Omega = "\\Omega"
    }
    
    // 数学运算符
    struct Operators {
        static let pm = "\\pm"
        static let mp = "\\mp"
        static let leq = "\\leq"
        static let geq = "\\geq"
        static let neq = "\\neq"
        static let approx = "\\approx"
        static let equiv = "\\equiv"
    }
    
    // 数学函数
    struct Functions {
        static let sum = "\\sum"
        static let prod = "\\prod"
        static let lim = "\\lim"
        static let int = "\\int"
        static let sqrt = "\\sqrt"
        static let frac = "\\frac"
        static let sin = "\\sin"
        static let cos = "\\cos"
        static let tan = "\\tan"
        static let log = "\\log"
        static let ln = "\\ln"
    }
    
}
//    // 分数转换方法
//        static func createFraction(_ numerator: String, _ denominator: String) -> String {
//            return "\\frac{\(numerator)}{\(denominator)}"
//        }
//        
//        private static func getDivisionPart(in expression: String, before divIndex: String.Index, isBefore: Bool = true) -> String {
//            var result = ""
//            var bracketCount = 0
//            var index = divIndex
//            
//            if isBefore {
//                while index > expression.startIndex {
//                    index = expression.index(before: index)
//                    let char = expression[index]
//                    
//                    if char == "}" { bracketCount += 1 }
//                    if char == "{" { bracketCount -= 1 }
//                    
//                    if bracketCount == 0 && isOperator(String(char)) && char != ")" {
//                        break
//                    }
//                    
//                    result = String(char) + result
//                }
//            } else {
//                index = expression.index(after: index)
//                while index < expression.endIndex {
//                    let char = expression[index]
//                    
//                    if char == "{" { bracketCount += 1 }
//                    if char == "}" { bracketCount -= 1 }
//                    
//                    if bracketCount == 0 && isOperator(String(char)) && char != "(" {
//                        break
//                    }
//                    
//                    result += String(char)
//                    index = expression.index(after: index)
//                }
//            }
//            
//            return result.trimmingCharacters(in: .whitespaces)
//        }
//        
//        // 将除法表达式转换为分数形式
//        static func convertDivisionToFraction(_ expression: String) -> String {
//            var expr = expression.replacingOccurrences(of: " ", with: "")
//            
//            while let divIndex = expr.firstIndex(of: "÷") ?? expr.range(of: "\\div")?.lowerBound {
//                let beforeDiv = getDivisionPart(in: expr, at: divIndex, isBefore: true)
//                let afterDiv = getDivisionPart(in: expr, at: divIndex, isBefore: false)
//                
//                // 计算起始位置
//                let startIndex = expr.index(divIndex, offsetBy: -beforeDiv.count)
//                
//                // 检查是否是 \div 并获取正确的范围
//                let divSymbolLength: Int
//                if let divRange = expr.range(of: "\\div", range: divIndex..<expr.endIndex) {
//                    divSymbolLength = expr.distance(from: divRange.lowerBound, to: divRange.upperBound)
//                } else {
//                    divSymbolLength = 1 // 单个除号的长度
//                }
//                
//                // 计算结束位置
//                let endIndex = expr.index(divIndex, offsetBy: divSymbolLength + afterDiv.count)
//                
//                // 创建分数并替换
//                let fraction = createFraction(beforeDiv, afterDiv)
//                expr.replaceSubrange(startIndex..<endIndex, with: fraction)
//            }
//            
//            return expr
//        }
//        
//        private static func getDivisionPart(in expression: String, at divIndex: String.Index, isBefore: Bool) -> String {
//            var result = ""
//            var bracketCount = 0
//            var index = divIndex
//            
//            if isBefore {
//                while index > expression.startIndex {
//                    index = expression.index(before: index)
//                    let char = expression[index]
//                    
//                    if char == "}" { bracketCount += 1 }
//                    if char == "{" { bracketCount -= 1 }
//                    
//                    if bracketCount == 0 && isOperator(String(char)) && char != ")" {
//                        break
//                    }
//                    
//                    result = String(char) + result
//                }
//            } else {
//                index = expression.index(after: index)
//                while index < expression.endIndex {
//                    let char = expression[index]
//                    
//                    if char == "{" { bracketCount += 1 }
//                    if char == "}" { bracketCount -= 1 }
//                    
//                    if bracketCount == 0 && isOperator(String(char)) && char != "(" {
//                        break
//                    }
//                    
//                    result += String(char)
//                    index = expression.index(after: index)
//                }
//            }
//            
//            return result.trimmingCharacters(in: .whitespaces)
//        }
//        
//        private static func isOperator(_ char: String) -> Bool {
//            let operators = ["+", "-", "×", "÷", "\\div", "\\times"]
//            return operators.contains(char)
//        }
//    }

// MARK: - LaTeX View
struct LaTeXView: UIViewRepresentable {
    let latex: String
    
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.backgroundColor = .clear
        webView.isOpaque = false
        webView.scrollView.isScrollEnabled = false
        return webView
    }
    
    func updateUIView(_ webView: WKWebView, context: Context) {
        // 确保 LaTeX 内容被正确转义
        let escapedLatex = latex.replacingOccurrences(of: "\\", with: "\\\\")
                               .replacingOccurrences(of: "\"", with: "\\\"")
        
        let html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous">
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" crossorigin="anonymous"></script>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background-color: transparent;
                }
                #formula {
                    width: 100%;
                    text-align: center;
                }
                .katex {
                    font-size: 1.5em;
                }
            </style>
        </head>
        <body>
            <div id="formula"></div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    try {
                        katex.render("\(escapedLatex)", document.getElementById('formula'), {
                            displayMode: true,
                            throwOnError: false,
                            strict: false
                        });
                    } catch (e) {
                        document.getElementById('formula').innerHTML = 'Error: ' + e.message;
                    }
                });
            </script>
        </body>
        </html>
        """
        
        webView.loadHTMLString(html, baseURL: nil)
    }
}

// 预览
//struct LaTeXView_Previews: PreviewProvider {
//    static var previews: some View {
//        LaTeXView(latex: "\\frac{1}{2}")
//            .frame(height: 100)
//    }
//}

// MARK: - Symbol Picker View
struct LatexSymbolPickerView: View {
    @Binding var selectedSymbol: String
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    symbolSection(title: "Operators", symbols: [
                        ("±", LatexSymbols.Operators.pm),
                        ("≤", LatexSymbols.Operators.leq),
                        ("≥", LatexSymbols.Operators.geq),
                        ("≠", LatexSymbols.Operators.neq),
                        ("≈", LatexSymbols.Operators.approx),
                        ("≡", LatexSymbols.Operators.equiv)
                    ])
                    
                    symbolSection(title: "Constants", symbols: [
                        ("π", LatexSymbols.Constants.pi),
                        ("e", LatexSymbols.Constants.e),
                        ("γ", LatexSymbols.Constants.gamma),
                        ("φ", LatexSymbols.Constants.phi),
                        ("∞", LatexSymbols.Constants.infinity)
                    ])
                    
                    symbolSection(title: "Functions", symbols: [
                        ("Σ", LatexSymbols.Functions.sum),
                        ("∏", LatexSymbols.Functions.prod),
                        ("lim", LatexSymbols.Functions.lim),
                        ("∫", LatexSymbols.Functions.int),
                        ("√", LatexSymbols.Functions.sqrt),
                        ("sin", LatexSymbols.Functions.sin),
                        ("cos", LatexSymbols.Functions.cos),
                        ("tan", LatexSymbols.Functions.tan),
                        ("log", LatexSymbols.Functions.log),
                        ("ln", LatexSymbols.Functions.ln)
                    ])
                    
                    symbolSection(title: "Greek Lowercase", symbols: [
                        ("α", LatexSymbols.GreekLower.alpha),
                        ("β", LatexSymbols.GreekLower.beta),
                        ("γ", LatexSymbols.GreekLower.gamma),
                        ("δ", LatexSymbols.GreekLower.delta),
                        ("ε", LatexSymbols.GreekLower.epsilon),
                        ("θ", LatexSymbols.GreekLower.theta),
                        ("λ", LatexSymbols.GreekLower.lambda),
                        ("μ", LatexSymbols.GreekLower.mu),
                        ("π", LatexSymbols.GreekLower.pi),
                        ("σ", LatexSymbols.GreekLower.sigma),
                        ("φ", LatexSymbols.GreekLower.phi),
                        ("ω", LatexSymbols.GreekLower.omega)
                    ])
                    
                    symbolSection(title: "Greek Uppercase", symbols: [
                        ("Γ", LatexSymbols.GreekUpper.Gamma),
                        ("Δ", LatexSymbols.GreekUpper.Delta),
                        ("Θ", LatexSymbols.GreekUpper.Theta),
                        ("Λ", LatexSymbols.GreekUpper.Lambda),
                        ("Π", LatexSymbols.GreekUpper.Pi),
                        ("Σ", LatexSymbols.GreekUpper.Sigma),
                        ("Φ", LatexSymbols.GreekUpper.Phi),
                        ("Ω", LatexSymbols.GreekUpper.Omega)
                    ])
                }
                .padding()
            }
            .navigationTitle("Math Symbols")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
    
    private func symbolSection(title: String, symbols: [(String, String)]) -> some View {
        VStack(alignment: .leading) {
            Text(title)
                .font(.headline)
                .padding(.horizontal)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6), spacing: 10) {
                ForEach(symbols, id: \.0) { symbol in
                    Button(action: {
                        selectedSymbol += symbol.1
                    }) {
                        Text(symbol.0)
                            .font(.title3)
                            .frame(width: 44, height: 44)
                            .background(Color.secondary.opacity(0.2))
                            .cornerRadius(8)
                    }
                }
            }
        }
    }
}

// MARK: - Latex Converter
struct LatexConverter {
    static func convertToLatex(_ input: String) -> String {
        // 确保所有数学表达式都在数学模式中
        var latex = input
        
        // 处理基本运算符
        latex = latex.replacingOccurrences(of: "×", with: "\\times ")
        latex = latex.replacingOccurrences(of: "÷", with: "\\div ")
        
        return latex
    }
}

// MARK: - Main View
struct MathKeyboardView: View {
    @StateObject private var cursorManager = CursorManager()
    @State private var showSymbolPicker = false
    @State private var selectedSymbol: String = ""
    
    // 数字键区
    let numberPadKeys: [[String]] = [
        ["1", "2", "3", "+"],
        ["4", "5", "6", "-"],
        ["7", "8", "9", "×"],
        ["0", ".", "÷", "="]
    ]
    
    // 公式键区
    let formulaKeys: [String] = [
        "\\frac{}{}", "\\sqrt{}", "\\pi", "\\sum_{i=1}^n", "\\int_{a}^{b}",
        "x^{}", "\\log", "\\ln", "\\lim_{x \\to \\infty}", "\\infty",
        "\\leq", "\\geq", "\\neq", "\\pm", "\\matrix{a & b \\\\ c & d}"
    ]
    
    // 定义网格布局
    let numberGridColumns: [GridItem] = Array(repeating: GridItem(.flexible(), spacing: 10), count: 4)
    let formulaGridColumns: [GridItem] = Array(repeating: GridItem(.flexible(), spacing: 10), count: 3)
    
    private var convertedLatex: String {
        return LatexConverter.convertToLatex(cursorManager.input)
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // 标题区域
                Text("University-Level Math Formula Keyboard")
                    .font(.title2)
                    .bold()
                    .padding(.top)
                
                HStack {
                    Button(action: {
                        withAnimation {
                            cursorManager.moveCursor(offset: -1)
                        }
                    }) {
                        Image(systemName: "arrow.left")
                            .font(.title2)
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        withAnimation {
                            cursorManager.deleteBackward()
                        }
                    }) {
                        Image(systemName: "delete.backward")
                            .font(.title2)
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        withAnimation {
                            cursorManager.moveCursor(offset: 1)
                        }
                    }) {
                        Image(systemName: "arrow.right")
                            .font(.title2)
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                
                // 输入区（公式输入）
                CustomInputView(cursorManager: cursorManager)
                    .frame(height: 100)
                    .padding(8)
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                
                // 整体Calculator风格容器
                VStack(spacing: 20) {
                    // 数字键盘区域
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Number Pad")
                            .font(.headline)
                        LazyVGrid(columns: numberGridColumns, spacing: 10) {
                            ForEach(numberPadKeys.flatMap { $0 }, id: \.self) { key in
                                Button(action: {
                                    withAnimation(.easeIn(duration: 0.1)) {
                                        cursorManager.insertAtCursor(key)
                                    }
                                }) {
                                    Text(key)
                                        .font(.title2)
                                        .frame(maxWidth: .infinity, minHeight: 60)
                                        .background(Color.blue)
                                        .foregroundColor(.white)
                                        .cornerRadius(8)
                                }
                            }
                        }
                    }
                    
                    // 公式键盘区域
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Formula Keyboard")
                            .font(.headline)
                        LazyVGrid(columns: formulaGridColumns, spacing: 10) {
                            ForEach(formulaKeys, id: \.self) { key in
                                Button(action: {
                                    withAnimation(.easeIn(duration: 0.1)) {
                                        cursorManager.insertAtCursor(key)
                                    }
                                }) {
                                    Text(key)
                                        .font(.footnote)
                                        .padding(8)
                                        .frame(maxWidth: .infinity, minHeight: 50)
                                        .background(Color.green)
                                        .foregroundColor(.white)
                                        .cornerRadius(8)
                                }
                            }
                        }
                    }
                    
                    // 符号选择器按钮
                    Button(action: { showSymbolPicker = true }) {
                        Text("More Symbols")
                            .font(.headline)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()
                .background(RoundedRectangle(cornerRadius: 15).stroke(Color.gray, lineWidth: 2))
                .padding(.horizontal)
                
                // 统一预览区域
                VStack(alignment: .leading, spacing: 10) {
                    Text("Raw Formula:")
                        .font(.headline)
                    Text(cursorManager.input)
                        .font(.body)
                        .padding(8)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color(white: 0.95))
                        .cornerRadius(8)
                    
                    Text("Rendered Formula:")
                        .font(.headline)
                    LaTeXView(latex: convertedLatex)
                        .frame(height: 100)
                        .padding(8)
                        .background(Color(white: 0.95))
                        .cornerRadius(8)
                    
                    ShareLink(item: convertedLatex) {
                        Text("Export Formula")
                            .font(.headline)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(Color.purple)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                
                // 清除按钮
                Button(action: {
                    withAnimation(.easeOut(duration: 0.2)) {
                        cursorManager.input = ""
                        cursorManager.cursorPosition = 0
                    }
                }) {
                    Text("Clear")
                        .font(.title3)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.red.opacity(0.7))
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
            }
            .padding(.horizontal)
        }
        .sheet(isPresented: $showSymbolPicker) {
            LatexSymbolPickerView(selectedSymbol: $selectedSymbol)
        }
        .onChange(of: selectedSymbol) { newValue in
            if !newValue.isEmpty {
                cursorManager.insertAtCursor(newValue)
                selectedSymbol = ""
            }
        }
    }
}

#Preview {
    MathKeyboardView()
}
