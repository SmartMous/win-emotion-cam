# -*- coding: utf-8 -*-
"""
情绪检测器模块
整合摄像头和模型，提供统一接口
"""
import time
from typing import Optional, Dict, Any
import numpy as np

from .camera import Camera
from .model import EmotionModel, create_model


class EmotionDetector:
    """情绪检测器"""
    
    def __init__(
        self,
        camera_index: int = 0,
        model_backend: str = 'hsemotion',
        fps_limit: int = 5
    ):
        """
        初始化情绪检测器

        Args:
            camera_index: 摄像头索引
            model_backend: 模型后端 ('hsemotion')
            fps_limit: 限制检测帧率，避免过慢
        """
        self.camera = Camera(camera_index=camera_index)
        self.model = create_model(backend=model_backend)
        self.fps_limit = fps_limit
        self._frame_interval = 1.0 / fps_limit if fps_limit > 0 else 0
        self._last_detect_time = 0
        
        # 缓存上一次的结果
        self._last_result: Optional[Dict[str, Any]] = None
    
    def start(self) -> bool:
        """启动检测器，打开摄像头"""
        return self.camera.open()
    
    def detect(self, frame: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        检测单帧图像的情绪
        
        Args:
            frame: 图像帧，如果为 None 则从摄像头读取
            
        Returns:
            检测结果字典
        """
        # 如果没有传入帧，从摄像头读取
        if frame is None:
            frame = self.camera.read()
            if frame is None:
                return {
                    'emotion': None,
                    'emotion_cn': '无法读取摄像头',
                    'confidence': 0.0,
                    'all_emotions': {},
                    'tone': '无法判断',
                    'face_detected': False,
                    'error': 'camera_read_failed'
                }
        
        # 帧率限制
        current_time = time.time()
        if self._frame_interval > 0:
            elapsed = current_time - self._last_detect_time
            if elapsed < self._frame_interval:
                # 返回缓存的结果
                if self._last_result is not None:
                    return self._last_result
        
        # 执行检测
        result = self.model.detect(frame)
        self._last_result = result
        self._last_detect_time = current_time
        
        return result
    
    def run_loop(self, callback=None):
        """
        运行主循环
        
        Args:
            callback: 每帧调用的回调函数，接收 (frame, result) 参数
                     返回 True 可退出循环
        """
        print("=" * 50)
        print("🎥 情绪识别已启动")
        print("📝 按 'q' 或 'Esc' 退出")
        print("=" * 50)
        
        import cv2
        
        while True:
            frame = self.camera.read()
            if frame is None:
                print("❌ 无法读取摄像头画面")
                break
            
            # BGR 转 RGB 用于显示
            display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # 检测情绪
            result = self.detect(frame)
            
            # 在画面上显示结果
            self._draw_result(display_frame, result)
            
            # 显示画面
            cv2.imshow('Emotion Camera', display_frame)
            
            # 调用回调
            if callback:
                if callback(frame, result):
                    break
            
            # 检查退出键 或 窗口被用户点击 X 关闭
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            # 窗口关闭检测（仅当窗口已存在且被关闭时）
            prop = cv2.getWindowProperty('Emotion Camera', cv2.WND_PROP_VISIBLE)
            if prop == 0:
                break
        
        self.stop()
    
    def _draw_result(self, frame, result: Dict[str, Any]):
        """在帧上绘制检测结果（使用 Pillow 支持中文）"""
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np

        _FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
        _FONT_SIZE = 28
        _FONT_SMALL = 20

        # OpenCV BGR -> Pillow RGBA（保留 alpha 通道用于透明背景）
        img_rgb = frame[..., ::-1]
        img = Image.fromarray(img_rgb).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype(_FONT_PATH, _FONT_SIZE)
            font_small = ImageFont.truetype(_FONT_PATH, _FONT_SMALL)
        except OSError:
            font = ImageFont.load_default()
            font_small = font

        if result.get('face_detected'):
            emotion = result.get('emotion_cn', '未知')
            confidence = result.get('confidence', 0)
            tone = result.get('tone', '未知')

            text = f"情绪: {emotion} ({confidence:.1%})"
            tone_text = f"建议语气: {tone}"

            # 半透明背景
            draw.rectangle([(5, 5), (400, 70)], fill=(0, 0, 0, 160))
            draw.text((12, 10), text, font=font, fill=(0, 255, 0, 255))
            draw.text((12, 42), tone_text, font=font_small, fill=(0, 255, 255, 255))
        else:
            draw.rectangle([(5, 5), (220, 40)], fill=(0, 0, 0, 160))
            draw.text((12, 8), "未检测到人脸", font=font, fill=(255, 0, 0, 255))

        # 合成 overlay 到原图，转回 OpenCV BGR
        img = Image.alpha_composite(img, overlay).convert("RGB")
        frame[:] = np.array(img)[..., ::-1]
    
    def stop(self):
        """停止检测器"""
        import cv2
        cv2.destroyAllWindows()
        self.camera.release()
        print("\n👋 情绪识别已退出")


def create_detector(
    camera_index: int = 0,
    model_backend: str = 'hsemotion',
    fps_limit: int = 5
) -> EmotionDetector:
    """创建情绪检测器"""
    return EmotionDetector(
        camera_index=camera_index,
        model_backend=model_backend,
        fps_limit=fps_limit
    )
