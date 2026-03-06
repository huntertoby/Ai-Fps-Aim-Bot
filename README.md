# 🎯 AI-Powered YOLO-Pose Aim Assist & ESP

🚀 **極致效能的 AI 視覺輔助瞄準與透視系統** 🚀

基於 YOLO-Pose 骨架辨識，結合 **純原生 TensorRT** 與 **CUDA Graphs** 技術，專為榨乾高階 GPU 效能所設計的超低延遲視覺推論專案。內建 Ring-0 級別硬體滑鼠模擬與 PID 平滑演算法，提供如絲般滑順的拉槍體驗。

---

## ✨ 核心特色 (Features)

* ⚡ **極限推論效能**：捨棄傳統 PyTorch 推論，使用純原生 TensorRT API 搭配 CUDA Graph 錄製，將延遲壓到最低。
* 🎯 **動態遞減鎖定邏輯 (Fallback Logic)**：智慧判斷可見部位，確保目標部分遮擋時依然能穩定追蹤。
* 🖱️ **PID 擬真平滑拉槍**：結合 P(比例)、I(積分)、D(微分) 控制器與殘差補償機制，消除指標微幅抖動，實現極致平滑的硬體級 (Ring-0) 滑鼠移動。
* 👁️ **高幀率 ESP 透視**：使用 PyQt5 打造的無邊框、全透明、硬體加速 Overlay，即時渲染骨架連線與部位節點。
* 📸 **極速螢幕擷取**：整合 `bettercam` 引擎，打破傳統 MSS/DXcam 瓶頸，實現千幀級別的畫面獲取。

---

## 🛠️ 系統架構與技術棧 (Tech Stack)

* **物件偵測模型**: YOLO (Ultralytics) - Pose Estimation
* **推論引擎**: NVIDIA TensorRT
* **畫面擷取**: BetterCam
* **硬體輸入模擬**: IbInputSimulator (Logitech Ring-0 Driver)
* **UI / Overlay**: PyQt5
* **控制演算法**: PID Controller (`simple_pid`)

---

## ⚙️ 快速開始 (Quick Start)

### 1. 安裝依賴環境
請確保你的系統已正確安裝 NVIDIA 驅動程式、CUDA Toolkit 與 cuDNN。
```bash
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu121](https://download.pytorch.org/whl/cu121)
pip install ultralytics tensorrt bettercam pyqt5 simple_pid pypiwin32
```

### 2. 轉換 TensorRT 模型
將訓練好的 YOLO-Pose PyTorch 模型 (`.pt`) 轉換為 TensorRT 引擎 (`.engine`)：
```bash
python export_trt.py
```
*預設將會鎖定輸入尺寸為 640x640，並使用靜態推論以獲得最高 FPS。*

### 3. 設定參數 (`config.py`)
打開 `config.py`，根據你的硬體效能與操作習慣調整參數：
* `AIM_KEYS`: 觸發瞄準的熱鍵 (預設為滑鼠左鍵與側鍵)。
* `TOGGLE_AIM_KEY`: 鎖頭模式總開關 (預設 `0x70` 為 F1 鍵)。
* `PID_KP` / `PID_KI` / `PID_KD`: 調整拉槍的速度、微調精準度與煞車力度。
* `DEADZONE`: 設定死區大小，防止準心在目標上微幅抖動。

### 4. 啟動系統
**選項 A：啟動主控與輔助瞄準**
```bash
python main.py
```

**選項 B：啟動 ESP 透視 Overlay**
```bash
python overlay_esp.py
```

---

## 📁 檔案結構 (Directory Structure)

```text
├── config.py           # 系統全域設定檔 (按鍵、PID、影像擷取參數)
├── main.py             # 實戰主程式 (畫面擷取、推論調度、目標邏輯判斷)
├── mouse_actor.py      # 滑鼠控制執行緒 (IbInputSimulator + PID 控制器)
├── overlay_esp.py      # PyQt5 ESP 透視視窗 (後台推論 + 前台渲染)
├── yolo.py             # 封裝 TensorRT Native 推論引擎 (CUDA Graph)
├── export_trt.py       # YOLO .pt 轉 TensorRT .engine 工具
└── IbInputSimulator.dll # Ring-0 硬體輸入模擬動態連結庫
```

---

## ⚠️ 免責聲明 (Disclaimer)

**本專案僅供「學術研究」、「AI 電腦視覺效能測試」與「Python 程式設計學習」使用。**
請勿將本系統應用於任何違反第三方服務條款（TOS）、破壞遊戲公平性或非法的環境中。作者對任何人因使用本專案代碼所導致的任何帳號封禁、法律責任或損害概不負責。下載與使用即代表您同意承擔所有相關風險。