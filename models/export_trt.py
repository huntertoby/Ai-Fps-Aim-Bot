from ultralytics import YOLO


def export_to_tensorrt():
    print("⏳ 開始將 YOLO 模型轉換為 TensorRT Engine...")

    # 載入你原本的 PyTorch 模型
    model = YOLO("yolo26l-pose.pt")

    # 執行輸出
    model.export(
        format="engine",
        imgsz=640,  # 鎖定輸入尺寸為 640x640
        dynamic=False,  # 關閉動態 Batch Size (靜態尺寸推論最快)
        # simplify=True,  # 簡化 ONNX 結構，減少冗餘節點
        workspace=8,  # 允許 TensorRT 使用高達 8GB VRAM 來尋找最佳 Kernel
        device="0"  # 指定在第一張顯卡上進行最佳化
    )

    print("✅ 轉換完成！你應該會看到一個 yolo26m-pose.engine 檔案。")


if __name__ == "__main__":
    export_to_tensorrt()