<<<<<<< HEAD
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
=======
🎯 PhantomAim TRT - YOLO-Pose AI 視覺輔助系統基於 YOLO-Pose 關鍵點檢測的超低延遲 AI 視覺輔助工具。採用純原生 TensorRT 引擎與 CUDA Graph 技術，搭配 BetterCam 達成極速螢幕擷取。內建 Ring-0 硬體級滑鼠模擬與 PID 平滑控制算法，提供如絲般滑順的人性化追蹤體驗。⚠️ 免責聲明 (Disclaimer)：本專案僅供學術研究與人工智慧機器視覺學習之用。請勿將此程式用於任何違反遊戲服務條款（ToS）的多人連線遊戲中。使用本程式所產生的一切後果由使用者自行承擔，開發者不對任何帳號封禁或損失負責。✨ 核心特色 (Features)⚡ 極限效能推論：放棄傳統 ONNX/PyTorch 推論，完全使用 tensorrt 原生 API 重寫，並導入 CUDA Graph 減少 CPU 提交開銷，發揮極致的 FPS。👁️ 智慧部位鎖定 (Fallback Logic)：基於 YOLO-Pose 17 關鍵點，自動依序尋找目標：雙眼 -> 雙耳 -> 鼻子 -> 胸口 -> 軀幹下半，確保在各種遮蔽情況下依然精準。🖱️ Ring-0 硬體級滑鼠驅動：整合 IbInputSimulator.dll (羅技驅動層模擬)，避開常規軟體層 (如 pyautogui, mouse) 的輸入攔截與反作弊偵測。🎯 PID 平滑控制與殘差補償：內建 Proportional-Integral-Derivative (PID) 控制器，並加入微小像素殘差累加技術，完美解決傳統 AI 輔助在微調階段準星抖動或死區鎖死的問題。🩻 高幀率透明 ESP 繪製：獨立的 PyQt5 前台透明視窗，不吃滑鼠鍵盤事件 (穿透)，支援 144Hz+ 螢幕更新率繪製骨架與邊界框，與後台 1000 FPS 推論引擎完全解耦。📁 專案架構 (Project Structure)├── main.py              # 主程式入口 (負責截圖、推論、目標邏輯處理)
├── mouse_actor.py       # 滑鼠控制模組 (PID 運算、載入 DLL、移動執行緒)
├── overlay_esp.py       # PyQt5 透明 ESP 繪製工具 (獨立運行)
├── yolo.py              # TensorRT 原生推論引擎封裝 (CUDA Graph)
├── config.py            # 全域設定檔 (熱鍵、PID參數、靈敏度等)
├── export_trt.py        # 模型轉換工具 (PyTorch .pt -> TensorRT .engine)
└── IbInputSimulator.dll # 滑鼠硬體模擬驅動依賴庫 (需自行確保放置於根目錄)
🛠️ 系統需求與依賴 (Prerequisites)作業系統：Windows 10 / 11硬體：NVIDIA 顯示卡 (強烈建議 RTX 30/40/50 系列以獲得最佳體驗)環境：Python 3.8+CUDA Toolkit (建議 11.8 或 12.x)TensorRTPython 套件：pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)  # 或你的 CUDA 版本
pip install ultralytics tensorrt bettercam simple_pid pywin32 PyQt5
🚀 安裝與使用指南 (Getting Started)1. 準備模型請準備您的 YOLO-Pose 模型 (.pt 格式)，並將其轉換為 TensorRT Engine 以獲得最佳效能：將你的 yolo26l-pose.pt 放入專案目錄中。執行轉換腳本：python export_trt.py
確認目錄下已生成對應的 .engine 檔案，並在 config.py 中確認 MODEL_PATH 設置正確。2. 環境依賴就緒確保 IbInputSimulator.dll 已放置於專案根目錄中。這是滑鼠移動的核心依賴，沒有它程式將無法驅動滑鼠。3. 參數設定 (Configuration)打開 config.py，根據您的習慣進行客製化：熱鍵設定：AIM_KEYS (預設為滑鼠左鍵與側鍵)、TOGGLE_AIM_KEY (預設 F1 開關)。PID 參數：調整 PID_KP, PID_KI, PID_KD 來改變拉槍的滑順度與速度。截圖區域：CAPTURE_SIZE (預設 640)。4. 啟動系統一般模式 (僅輔助瞄準)：python main.py
啟動後按下 F1 可切換開啟/關閉狀態，按住設定的熱鍵即可自動追蹤。ESP 透視模式 (開發與除錯用)：如果您想查看模型抓取的骨架與識別框，可以獨立執行 ESP 腳本：python overlay_esp.py
💡 常見問題 (FAQ)Q: 執行時報錯 IbInputSimulator 初始化失敗？A: 請確保你的環境有正確的 C++ 可轉發套件 (VC++ Redistributable)，並確認使用的 Python 位元數 (64-bit) 與 DLL 匹配。Q: 滑鼠移動很卡頓或不夠快？A: 請打開 config.py，適度調高 PID_KP 的數值，或是提高 MAX_MOVE_PIXELS (單次最大移動像素)。Q: TensorRT 反序列化失敗？A: TensorRT 的 .engine 檔案是綁定硬體與 TensorRT 版本的。如果你更換了顯示卡，或是更新了 CUDA/TensorRT 版本，必須重新執行 python export_trt.py 生成新的 engine。📜 授權協議 (License)This project is licensed under the MIT License - see the LICENSE file for details.(注意：依賴庫如 TensorRT, Ultralytics 等遵循其各自的官方開源協議)
>>>>>>> e92ed1b4ace8789ae66813ff9a0188bb6c217c88
