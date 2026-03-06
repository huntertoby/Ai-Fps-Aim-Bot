import torch
import tensorrt as trt
import config

class YoloTRTNativeEngine:
    def __init__(self, engine_path=config.MODEL_PATH):
        self.device = torch.device('cuda:0')
        print(f"⚡ 初始化純原生 TensorRT 引擎 on {torch.cuda.get_device_name(0)}...")

        TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
        trt.init_libnvinfer_plugins(TRT_LOGGER, '')

        with open(engine_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
            first_4_bytes = f.read(4)
            magic_number = int.from_bytes(first_4_bytes, byteorder='little')

            if magic_number > 100000:
                f.seek(0)
                engine_bytes = f.read()
            else:
                _ = f.read(magic_number)
                engine_bytes = f.read()

            self.engine = runtime.deserialize_cuda_engine(engine_bytes)

            if self.engine is None:
                raise RuntimeError("❌ TensorRT 引擎反序列化失敗！")

        self.context = self.engine.create_execution_context()

        self.input_name = self.engine.get_tensor_name(0)
        self.output_name = self.engine.get_tensor_name(1)

        input_shape = self.engine.get_tensor_shape(self.input_name)
        output_shape = self.engine.get_tensor_shape(self.output_name)

        # --- [修正 1] 動態適配 TensorRT 的精度 (解決讀取到雜訊的問題) ---
        def get_torch_dtype(trt_dtype):
            if trt_dtype == trt.DataType.FLOAT: return torch.float32
            elif trt_dtype == trt.DataType.HALF: return torch.float16
            elif trt_dtype == trt.DataType.INT32: return torch.int32
            return torch.float32

        self.in_dtype = get_torch_dtype(self.engine.get_tensor_dtype(self.input_name))
        self.out_dtype = get_torch_dtype(self.engine.get_tensor_dtype(self.output_name))

        print(f"🔹 TRT 輸入維度: {input_shape} | 型態: {self.in_dtype}")
        print(f"🔹 TRT 輸出維度: {output_shape} | 型態: {self.out_dtype}")

        self.CAPTURE_SIZE = config.CAPTURE_SIZE
        self.CONF_THRES = config.CONF_THRESHOLD  # 設為 0.5 確保能抓到
        self.max_det = 100

        self.input_tensor = torch.empty(tuple(input_shape), dtype=self.in_dtype, device=self.device).contiguous()
        self.output_tensor = torch.empty(tuple(output_shape), dtype=self.out_dtype, device=self.device).contiguous()

        self.context.set_tensor_address(self.input_name, self.input_tensor.data_ptr())
        self.context.set_tensor_address(self.output_name, self.output_tensor.data_ptr())

        self.stream = torch.cuda.Stream()
        self.graph = None

        self.pinned_buffer = torch.empty((640, 640, 3), dtype=torch.uint8, pin_memory=True)
        # 輸出 Buffer 統一用 float32，避免繪圖時遇到精度問題
        self.output_buffer = torch.zeros((self.max_det, 57), dtype=torch.float32, device=self.device)

        self._warmup_and_capture()

    def _warmup_and_capture(self):
        print("⚡ 開始 TensorRT + CUDA Graph 錄製...")
        with torch.cuda.stream(self.stream):
            for _ in range(10):
                self.context.execute_async_v3(stream_handle=self.stream.cuda_stream)
        self.stream.synchronize()

        self.graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph, stream=self.stream):
            self.context.execute_async_v3(stream_handle=self.stream.cuda_stream)

        self.stream.synchronize()
        print("✅ CUDA Graph 錄製完畢！")

    def preprocess(self, numpy_img):
        self.pinned_buffer.copy_(torch.from_numpy(numpy_img))
        tensor = self.pinned_buffer.to(self.device, non_blocking=True)
        tensor = tensor.permute(2, 0, 1).to(self.in_dtype) / 255.0

        tensor = tensor.unsqueeze(0)

        self.input_tensor.copy_(tensor)

    def infer(self):
        self.graph.replay()
        return self.output_tensor

    def postprocess(self, raw_output):
        preds = raw_output[0]
        if preds.shape[0] < preds.shape[1]:
            preds = preds.transpose(0, 1)

        # 信心度在 index 4
        scores = preds[:, 4]
        valid_mask = scores > self.CONF_THRES
        valid_preds = preds[valid_mask]

        num_det = valid_preds.shape[0]
        if num_det == 0:
            return []

        if num_det > self.max_det:
            _, topk_indices = torch.topk(valid_preds[:, 4], self.max_det)
            selected_preds = valid_preds[topk_indices]
            num_det = self.max_det
        else:
            selected_preds = valid_preds

        self.output_buffer[:num_det, :57] = selected_preds[:, :57]

        return self.output_buffer[:num_det]