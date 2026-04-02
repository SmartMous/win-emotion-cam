# -*- coding: utf-8 -*-
"""
摄像头捕获模块
"""
import cv2
import numpy as np
from typing import Optional, Generator


class Camera:
    """摄像头捕获类"""
    
    def __init__(self, camera_index: int = 0):
        """
        初始化摄像头
        
        Args:
            camera_index: 摄像头索引，默认 0 (默认摄像头)
        """
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
    
    def open(self) -> bool:
        """打开摄像头"""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            return False
        
        # 设置摄像头参数 (可选)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        return True
    
    def read(self) -> Optional[np.ndarray]:
        """
        读取下一帧
        
        Returns:
            图像帧 (numpy array)，失败返回 None
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # OpenCV 读取的是 BGR，转为 RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    
    def get_frames(self) -> Generator[np.ndarray, None, None]:
        """
        获取视频流生成器
        
        Yields:
            图像帧
        """
        while True:
            frame = self.read()
            if frame is None:
                break
            yield frame
    
    def release(self):
        """释放摄像头资源"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def is_opened(self) -> bool:
        """检查摄像头是否已打开"""
        return self.cap is not None and self.cap.isOpened()
    
    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release()


def list_cameras(max_check: int = 5) -> list:
    """
    列出可用的摄像头
    
    Args:
        max_check: 最大检查的摄像头索引
        
    Returns:
        可用的摄像头索引列表
    """
    available = []
    for i in range(max_check):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return available
