<div align="center">

# 🎯 AI-Powered YOLO-Pose Aim Assist & ESP

🚀 **極致效能的 AI 視覺輔助瞄準與透視系統** 🚀

基於 **YOLO-Pose** 與 **TensorRT** 原生引擎打造，專為頂級算力（如 RTX 5090）設計的極低延遲視覺輔助工具。結合 PID 控制器實現平滑擬真拉槍，並配有 PyQt5 高刷新率透明 ESP 渲染。

</div>

---

## ✨ 核心特色 (Key Features)

- ⚡ **極致推論效能**：拋棄厚重的框架，直接使用 `tensorrt` 原生 API 搭配 **CUDA Graph** 錄製，將 GPU 推論延遲壓榨到極限。
- 🎯 **PID 擬真平滑拉槍**：內建 P/I/D 參數控制，搭配「殘差補償機制」，告別機械式的生硬鎖定，實現如真人般滑順且精準的微調追槍。
- 👁️ **智慧遞減鎖定邏輯 (Fallback Logic)**：優先瞄準眼部，若被遮擋則自動向下遞減尋找耳朵、鼻子、胸口至軀幹，確保目標不丟失。
- 👻 **無邊框透明 ESP 渲染**：基於 PyQt5 打造的 Ring-3 頂層透明視窗，支援 144Hz+ 絲滑重繪骨架與目標框，且完全不干擾滑鼠點擊穿透。
- 🖱️ **Ring-0 驅動級滑鼠控制**：整合 `IbInputSimulator` 羅技底層驅動模擬，有效規避基礎的軟體層滑鼠事件偵測。
- 📸 **極速螢幕擷取**：採用 `BetterCam` (DXGI) 擷取引擎，輕鬆達成 1000 FPS 的取樣率。

---

## 🛠️ 專案架構 (Structure)

```text
📁 Project Root
 ├── main.py            # 主程式：負責螢幕擷取、YOLO 推論與鎖定邏輯計算
 ├── mouse_actor.py     # 鼠標控制：PID 計算與 IbInputSimulator 驅動發送
 ├── overlay_esp.py     # ESP 程式：獨立後台推論與 PyQt5 前台透明骨架渲染
 ├── yolo.py            # 核心引擎：TensorRT 封裝與 CUDA Graph 最佳化
 ├── config.py          # 參數配置：按鍵綁定、PID 參數、信心值、擷取範圍等
 ├── export_trt.py      # 模型轉換：將 PyTorch YOLO 模型轉為 TensorRT Engine
 └── IbInputSimulator.dll # 滑鼠硬體級模擬驅動 (需自備/配置)
```

---

## 📦 快速開始 (Getting Started)

### 1. 環境需求
- **OS**: Windows 10 / 11
- **GPU**: 支援 CUDA 的 NVIDIA 顯示卡 (強烈建議 RTX 30/40/50 系列以獲得最佳體驗)
- **Python**: 3.8+ (建議 3.10)
- **驅動與套件**: CUDA Toolkit, cuDNN, TensorRT

### 2. 安裝依賴
請確保你已經安裝了對應版本的 PyTorch (含 CUDA 支援)，然後安裝其他依賴：
```bash
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu121](https://download.pytorch.org/whl/cu121)
pip install tensorrt ultralytics bettercam simple_pid PyQt5 pywin32 numpy
```

### 3. 準備模型
本專案預設使用 YOLO-Pose 模型。你需要先準備 `.pt` 檔，並轉換為極致效能的 `.engine` 檔：
1. 將你的 YOLO-Pose 模型命名為 `yolo26l-pose.pt` 並放在專案根目錄。
2. 執行轉換腳本（此過程需要幾分鐘，TensorRT 會尋找最佳 kernel）：
```bash
python export_trt.py
```
3. 將產生的 `.engine` 檔案移至 `models/` 資料夾下（或至 `config.py` 修改路徑）。

### 4. 準備滑鼠驅動
請確保 `IbInputSimulator.dll` 放置於 `mouse_actor.py` 同層目錄中，並具備執行權限。

---

## ⚙️ 參數設定 (Configuration)

所有的核心參數都集中在 `config.py` 中，你可以隨時根據手感和硬體效能進行微調：

- **熱鍵設定**：`AIM_KEYS` (觸發瞄準鍵)、`TOGGLE_AIM_KEY` (F1 開關鎖頭)。
- **效能設定**：`CAPTURE_SIZE` (預設 640)、`TARGET_FPS` (BetterCam 擷取張數)。
- **PID 參數**：
  - `PID_KP`: 決定拉槍初始速度 (越大拉越快)。
  - `PID_KI`: 處理靜態誤差，確保精準對齊。
  - `PID_KD`: 預測偏差，減速防過衝 (煞車感)。
- **細節微調**：`HEAD_OFFSET_Y` (準心 Y 軸偏移)、`DEADZONE` (死區防抖)。

---

## 🚀 執行系統 (Usage)

### 啟動瞄準輔助 (Aim Assist)
執行主程式，系統會自動在後台啟動滑鼠控制執行緒與視覺掃描：
```bash
python main.py
```
*提示：執行後可透過終端機監控實時的 抓圖/推論/邏輯 延遲與估算 FPS。*

### 啟動透視渲染 (ESP Overlay)
若需要視覺化的骨架與目標框渲染，請開啟另一個終端機執行：
```bash
python overlay_esp.py
```

---

## ⚠️ 免責聲明 (Disclaimer)

> **Educational Purposes Only** 
> 本專案僅供 **AI 電腦視覺研究、TensorRT 效能最佳化學習與 PID 控制理論** 之學術交流使用。  
> 請勿將本專案用於任何破壞遊戲平衡、違反遊戲服務條款 (ToS) 或非法的商業用途。開發者對使用者濫用本軟體所導致的任何帳號封禁或法律責任概不負責。

---
<div align="center">
<i>Built with ❤️ & Power of AI</i>
</div>