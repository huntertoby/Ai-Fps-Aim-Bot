import ctypes
import time
import win32api
import math
import os
from simple_pid import PID
import config


class IbMouse:
    def __init__(self):
        dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IbInputSimulator.dll")
        try:
            self.dll = ctypes.WinDLL(dll_path)
        except Exception as e:
            raise RuntimeError(f"❌ 載入失敗: {e}")

        self.dll.IbSendInit.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
        self.dll.IbSendInit.restype = ctypes.c_int
        self.dll.IbSendMouseMove.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.dll.IbSendMouseMove.restype = ctypes.c_bool
        self.dll.IbSendDestroy.argtypes = []

        status = self.dll.IbSendInit(3, 0, None)
        if status != 0:
            raise RuntimeError(f"❌ IbInputSimulator 初始化失敗！錯誤碼: {status}")
        print("✅ IbInputSimulator (羅技 Ring-0 驅動模式) 載入成功！")

    def move_relative(self, dx, dy):
        self.dll.IbSendMouseMove(int(dx), int(dy), 1)

    def destroy(self):
        self.dll.IbSendDestroy()


def mouse_thread_logic(shared_data):
    print("🖱️ PID 擬真平滑拉槍 (含殘差補償) 已啟動...")
    ib_mouse = IbMouse()

    # --- 修正 1：改用 config 讀取 PID 參數 ---
    pid_x = PID(config.PID_KP, config.PID_KI, config.PID_KD, setpoint=0, sample_time=config.PID_SAMPLE_TIME)
    pid_y = PID(config.PID_KP, config.PID_KI, config.PID_KD, setpoint=0, sample_time=config.PID_SAMPLE_TIME)

    # 改用 config 讀取最大移動限制
    max_step = config.MAX_MOVE_PIXELS
    pid_x.output_limits = (-max_step, max_step)
    pid_y.output_limits = (-max_step, max_step)

    was_aiming = False

    # --- 修正 2：準備殘差累加器 ---
    residual_x = 0.0
    residual_y = 0.0

    try:
        while True:
            # 改用 config 讀取休眠時間
            time.sleep(config.MOUSE_THREAD_SLEEP)

            with shared_data["lock"]:
                target = shared_data["target"]
                is_aiming = shared_data["aiming"]
                shared_data["target"] = None

            if not is_aiming or target is None:
                if was_aiming:
                    pid_x.reset()
                    pid_y.reset()
                    residual_x = 0.0
                    residual_y = 0.0
                    was_aiming = False
                continue

            was_aiming = True

            raw_dx, raw_dy = target
            dist = math.hypot(raw_dx, raw_dy)

            # 改用 config 讀取死區大小
            if dist < config.DEADZONE:
                continue

            # 運算移動量 (浮點數)
            move_x = pid_x(-raw_dx)
            move_y = pid_y(-raw_dy)

            # --- 修正 3：累加殘差，解決微調像素消失的問題 ---
            residual_x += move_x
            residual_y += move_y

            # 取出整數部分準備發送
            final_x = int(residual_x)
            final_y = int(residual_y)

            # 把發送出去的整數部分扣掉，留下小數點給下一幀
            residual_x -= final_x
            residual_y -= final_y

            if final_x != 0 or final_y != 0:
                ib_mouse.move_relative(final_x, final_y)

    except KeyboardInterrupt:
        ib_mouse.destroy()