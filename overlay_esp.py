import os
import sys
import time
import threading
import win32api
import bettercam

from yolo import YoloTRTNativeEngine

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor


shared_overlay_data = {
    "detections": [],  # 存放最新的推論結果陣列
    "fps": 0,  # 存放推論端的 FPS
    "lock": threading.Lock()
}

SKELETON_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4),  # 頭部
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # 上半身手臂
    (5, 11), (6, 12), (11, 12),  # 軀幹
    (11, 13), (13, 15), (12, 14), (14, 16)  # 下半身腿部
]

CONF_THRES = 0.4


def inference_thread_logic():
    print("🔥 ESP 後台推論引擎啟動...")
    engine = YoloTRTNativeEngine("models/yolo26l-pose.engine")
    camera = bettercam.create(output_color="RGB", max_buffer_len=512)

    capture_size = 640
    screen_w, screen_h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    left, top = (screen_w - capture_size) // 2, (screen_h - capture_size) // 2
    region = (left, top, left + capture_size, top + capture_size)
    camera.start(region=region, target_fps=1000)

    prev_time = time.perf_counter()

    try:
        while True:
            img_rgb = camera.get_latest_frame()
            if img_rgb is None:
                continue

            engine.preprocess(img_rgb)
            engine.infer()
            results = engine.postprocess(engine.output_tensor)

            # 計算 FPS
            curr_time = time.perf_counter()
            fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time

            # 將結果轉為 NumPy 並更新到共享變數
            det_list = []
            if len(results) > 0:
                det_list = results.cpu().numpy()

            with shared_overlay_data["lock"]:
                shared_overlay_data["detections"] = det_list
                shared_overlay_data["fps"] = int(fps)

    except Exception as e:
        print(f"推論執行緒發生錯誤: {e}")
    finally:
        camera.stop()


# ==========================================
# 3. PyQt5 前台透明視窗 (ESP 渲染)
# ==========================================
class ESPOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 取得螢幕尺寸以置中
        screen_w, screen_h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
        self.capture_size = 640
        left = (screen_w - self.capture_size) // 2
        top = (screen_h - self.capture_size) // 2

        self.setGeometry(left, top, self.capture_size, self.capture_size)
        self.setWindowTitle('YOLO ESP Overlay')

        # 🎯 核心魔法：設定視窗屬性為 透明、無邊框、置頂、穿透滑鼠點擊
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 無邊框
            Qt.WindowStaysOnTopHint |  # 永遠置頂
            Qt.WindowTransparentForInput |  # 忽略所有滑鼠/鍵盤輸入 (穿透)
            Qt.Tool  # 不在工具列顯示圖示
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 背景全透明

        # 設定定時器，每 7 毫秒觸發一次重繪 (約 144 FPS)
        # 注意：這裡的 FPS 是螢幕刷新率，不影響後台推論的 1000 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(7)

    def paintEvent(self, event):
        # 每次觸發 update() 時會執行這裡
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 開啟反鋸齒，線條更平滑

        # 讀取共享資料
        with shared_overlay_data["lock"]:
            detections = shared_overlay_data["detections"]
            fps = shared_overlay_data["fps"]

        # 畫 FPS 資訊 (左上角)
        painter.setPen(QPen(Qt.yellow, 2))
        painter.drawText(10, 20, f"Engine FPS: {fps}")

        if len(detections) == 0:
            return

        for det in detections:
            painter.setBrush(Qt.NoBrush)
            # 1. 繪製邊界框 (綠色)
            x1, y1, x2, y2 = map(int, det[:4])
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)

            # 2. 處理關鍵點
            kpts = det[6:57].reshape(17, 3)

            # 3. 繪製骨架連線 (青色)
            painter.setPen(QPen(Qt.cyan, 2, Qt.SolidLine))
            for connection in SKELETON_CONNECTIONS:
                pt1_idx, pt2_idx = connection
                x1_k, y1_k, conf1 = kpts[pt1_idx]
                x2_k, y2_k, conf2 = kpts[pt2_idx]

                if conf1 > CONF_THRES and conf2 > CONF_THRES:
                    painter.drawLine(int(x1_k), int(y1_k), int(x2_k), int(y2_k))

            # 4. 繪製關鍵點 (紅色，為了覆蓋在線上所以最後畫)
            painter.setPen(QPen(Qt.red, 3))
            painter.setBrush(Qt.red)
            for i in range(17):
                x, y, conf = kpts[i]
                if conf > CONF_THRES:
                    painter.drawEllipse(int(x) - 2, int(y) - 2, 4, 4)


if __name__ == '__main__':
    # 啟動後台推論執行緒 (Daemon 表示主程式關閉時它也會自動關閉)
    infer_thread = threading.Thread(target=inference_thread_logic, daemon=True)
    infer_thread.start()

    # 啟動 PyQt5 應用程式
    app = QApplication(sys.argv)
    overlay = ESPOverlay()
    overlay.show()

    # 進入 UI 事件迴圈
    sys.exit(app.exec_())