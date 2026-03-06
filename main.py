import threading
import bettercam
import time

import win32api

import yolo
import mouse_actor
import config

# 1. 初始化共享數據
shared_data = {
    "target": None,
    "aiming": False,
    "lock": threading.Lock()
}

# 2. 定義 COCO 關鍵點名稱 (YOLO-Pose 標準 17 點)
BODY_PARTS = [
    "鼻子", "左眼", "右眼", "左耳", "右耳",
    "左肩", "右肩", "左肘", "右肘", "左腕", "右腕",
    "左髖", "右髖", "左膝", "右膝", "左踝", "右踝"
]

SKELETON_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4),  # 頭部
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # 上半身手臂
    (5, 11), (6, 12), (11, 12),  # 軀幹
    (11, 13), (13, 15), (12, 14), (14, 16)  # 下半身腿部
]

DEBUG_MODE = False


def battle_ready_run():

    mouse_thread = threading.Thread(target=mouse_actor.mouse_thread_logic, args=(shared_data,), daemon=True)
    mouse_thread.start()

    engine = yolo.YoloTRTNativeEngine(config.MODEL_PATH)

    # 🎯 修改 2：改用 bettercam.create()
    camera = bettercam.create(output_color="RGB", max_buffer_len=512)

    # 讀取 config 中的截圖大小
    capture_size = config.CAPTURE_SIZE
    screen_w, screen_h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    left, top = (screen_w - capture_size) // 2, (screen_h - capture_size) // 2
    region = (left, top, left + capture_size, top + capture_size)

    # 讀取 config 中的 TARGET_FPS
    camera.start(region=region, target_fps=config.TARGET_FPS)

    print("🔥 RTX 5090 實戰系統已就緒 (已啟用 BetterCam 極速引擎)，準備掃描目標並分析延遲...")

    # --- 效能統計變數 ---
    frame_count = 0
    sum_cap_time = 0.0
    sum_infer_time = 0.0
    sum_logic_time = 0.0
    sum_total_time = 0.0

    # 讀取 config 中的預設開關狀態與切換按鍵
    aim_enabled = config.DEFAULT_AIM_ENABLED
    f1_was_pressed = False
    VK_TOGGLE = config.TOGGLE_AIM_KEY

    last_locked_abs_x = None
    last_locked_abs_y = None

    # 預先讀取信心值，減少迴圈內的查表時間
    CONF = config.CONF_THRESHOLD

    try:
        while True:
            loop_start = time.perf_counter()

            t_cap_start = time.perf_counter()
            img_rgb = camera.get_latest_frame()
            if img_rgb is None:
                continue
            t_cap_end = time.perf_counter()

            # ---------------------------
            # 2. 模型推論階段計時
            # ---------------------------
            t_infer_start = time.perf_counter()
            engine.preprocess(img_rgb)
            engine.infer()
            results = engine.postprocess(engine.output_tensor)
            t_infer_end = time.perf_counter()

            # ---------------------------
            # 3. 邏輯判斷與資料更新階段計時
            # ---------------------------
            t_logic_start = time.perf_counter()

            f1_is_pressed = (win32api.GetAsyncKeyState(VK_TOGGLE) & 0x8000) != 0

            if f1_is_pressed and not f1_was_pressed:
                aim_enabled = not aim_enabled
                status_text = "🟢 啟動" if aim_enabled else "🔴 關閉"
                print(f"\n[系統提示] 鎖頭模式已切換為：{status_text}\n")

            f1_was_pressed = f1_is_pressed

            if aim_enabled:
                # 遍歷 config.AIM_KEYS 陣列，只要有任何一個按鍵被按下，is_pressed 就為 True
                is_pressed = any((win32api.GetAsyncKeyState(key) & 0x8000) != 0 for key in config.AIM_KEYS)
            else:
                is_pressed = False

            if aim_enabled and is_pressed and last_locked_abs_x is not None:
                reference_x = last_locked_abs_x
                reference_y = last_locked_abs_y
            else:
                reference_x = capture_size / 2.0
                reference_y = capture_size / 2.0

            best_target = None
            best_abs_x = None
            best_abs_y = None

            if len(results) > 0:

                min_dist_sq = float('inf')
                det_list = results.cpu().numpy()

                for det in det_list:
                    kpts = det[6:57].reshape(17, 3)

                    target_x, target_y = None, None

                    # ==========================================
                    # 🎯 遞減鎖定邏輯 (Fallback Logic)
                    # ==========================================

                    # 1. 眼睛層級
                    if kpts[1][2] > CONF and kpts[2][2] > CONF:
                        target_x, target_y = (kpts[1][0] + kpts[2][0]) / 2.0, (kpts[1][1] + kpts[2][1]) / 2.0
                    elif kpts[1][2] > CONF:
                        target_x, target_y = kpts[1][0], kpts[1][1]
                    elif kpts[2][2] > CONF:
                        target_x, target_y = kpts[2][0], kpts[2][1]

                    # 2. 耳朵層級
                    elif kpts[3][2] > CONF and kpts[4][2] > CONF:
                        target_x, target_y = (kpts[3][0] + kpts[4][0]) / 2.0, (kpts[3][1] + kpts[4][1]) / 2.0
                    elif kpts[3][2] > CONF:
                        target_x, target_y = kpts[3][0], kpts[3][1]
                    elif kpts[4][2] > CONF:
                        target_x, target_y = kpts[4][0], kpts[4][1]

                    # 3. 鼻子
                    elif kpts[0][2] > CONF:
                        target_x, target_y = kpts[0][0], kpts[0][1]

                    # 4. 胸口層級
                    elif kpts[5][2] > CONF and kpts[6][2] > CONF:
                        target_x, target_y = (kpts[5][0] + kpts[6][0]) / 2.0, (kpts[5][1] + kpts[6][1]) / 2.0
                    elif kpts[5][2] > CONF:
                        target_x, target_y = kpts[5][0], kpts[5][1]
                    elif kpts[6][2] > CONF:
                        target_x, target_y = kpts[6][0], kpts[6][1]

                    # 5. 軀幹下半層級
                    elif kpts[11][2] > CONF and kpts[12][2] > CONF:
                        target_x, target_y = (kpts[11][0] + kpts[12][0]) / 2.0, (kpts[11][1] + kpts[12][1]) / 2.0
                    elif kpts[11][2] > CONF:
                        target_x, target_y = kpts[11][0], kpts[11][1]
                    elif kpts[12][2] > CONF:
                        target_x, target_y = kpts[12][0], kpts[12][1]

                    # 距離計算與鎖定
                    if target_x is not None:
                        dist_sq = (target_x - reference_x) ** 2 + (target_y - reference_y) ** 2

                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            # 將寫死的 320 替換為動態中心點 (capture_size / 2)
                            center = capture_size / 2.0
                            best_target = (target_x - center, target_y - center - config.HEAD_OFFSET_Y)
                            best_abs_x = target_x
                            best_abs_y = target_y

            if is_pressed and best_abs_x is not None:
                last_locked_abs_x = best_abs_x
                last_locked_abs_y = best_abs_y
            else:
                last_locked_abs_x = None
                last_locked_abs_y = None

            with shared_data["lock"]:
                shared_data["target"] = best_target
                shared_data["aiming"] = is_pressed

            t_logic_end = time.perf_counter()
            loop_end = t_logic_end  # 單圈結束

            # ---------------------------
            # 結算與輸出
            # ---------------------------
            sum_cap_time += (t_cap_end - t_cap_start)
            sum_infer_time += (t_infer_end - t_infer_start)
            sum_logic_time += (t_logic_end - t_logic_start)
            sum_total_time += (loop_end - loop_start)
            frame_count += 1

            if frame_count >= 60:
                avg_cap = (sum_cap_time / 60) * 1000
                avg_infer = (sum_infer_time / 60) * 1000
                avg_logic = (sum_logic_time / 60) * 1000
                avg_total = (sum_total_time / 60) * 1000
                fps_estimate = 1000.0 / avg_total if avg_total > 0 else 0

                print(
                    f"⏱ 延遲(ms) | 抓圖: {avg_cap:.2f} | 推論: {avg_infer:.2f} | 邏輯: {avg_logic:.2f} | 總計: {avg_total:.2f} | FPS: {fps_estimate:.0f}    ")

                frame_count = 0
                sum_cap_time = sum_infer_time = sum_logic_time = sum_total_time = 0.0

    except KeyboardInterrupt:
        camera.stop()
        print("\n🛑 任務結束。")


if __name__ == "__main__":
    battle_ready_run()