# -*- coding: utf-8 -*-
"""
模型管理模块
负责加载和管理情绪识别模型
"""

import os
from typing import Optional, Dict, Any


class EmotionModel:
    """情绪识别模型包装类"""
    
    # 情绪到中文的映射
    EMOTION_MAP = {
        'happy': '开心',
        'sad': '悲伤',
        'angry': '愤怒',
        'surprised': '惊讶',
        'fearful': '恐惧',
        'disgusted': '厌恶',
        'neutral': '中性'
    }
    
    # 情绪到沟通语气的映射
    TONE_MAP = {
        'happy': '轻松、热情',
        'sad': '温和、耐心、倾听',
        'angry': '冷静、平和、避免对抗',
        'surprised': '平稳、确认信息',
        'fearful': '安抚、温柔、支持',
        'disgusted': '尊重、保持距离',
        'neutral': '自然、专业'
    }
    
    def __init__(self, backend: str = 'fer'):
        """
        初始化模型
        
        Args:
            backend: 使用的模型后端，可选 'fer' 或 'deepface'
        """
        self.backend = backend
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        if self.backend == 'fer':
            from fer import FER
            # 使用摄像头，检测所有人脸
            self.model = FER(mtcnn=True)
        elif self.backend == 'deepface':
            from deepface import DeepFace
            self.model = DeepFace
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def detect(self, frame) -> Optional[Dict[str, Any]]:
        """
        检测情绪
        
        Args:
            frame: OpenCV 图像帧 (numpy array)
            
        Returns:
            检测结果字典，包含:
            - emotion: 主要情绪 (英文)
            - emotion_cn: 主要情绪 (中文)
            - confidence: 置信度
            - all_emotions: 所有情绪的概率
            - tone: 建议的沟通语气
            - face_detected: 是否检测到人脸
        """
        import numpy as np
        
        if self.backend == 'fer':
            return self._detect_fer(frame)
        elif self.backend == 'deepface':
            return self._detect_deepface(frame)
    
    def _detect_fer(self, frame) -> Optional[Dict[str, Any]]:
        """使用 FER 库检测情绪"""
        try:
            result = self.model.detect_emotions(frame)
            
            if not result or len(result) == 0:
                return {
                    'emotion': None,
                    'emotion_cn': '未检测到人脸',
                    'confidence': 0.0,
                    'all_emotions': {},
                    'tone': '无法判断',
                    'face_detected': False
                }
            
            # 取第一张人脸
            face = result[0]
            emotions = face['emotions']
            
            # 归一化情绪分数
            total = sum(emotions.values())
            if total > 0:
                emotions = {k: v / total for k, v in emotions.items()}
            
            # 找出最高置信度的情绪
            main_emotion = max(emotions, key=emotions.get)
            confidence = emotions[main_emotion]
            
            return {
                'emotion': main_emotion,
                'emotion_cn': self.EMOTION_MAP.get(main_emotion, main_emotion),
                'confidence': round(confidence, 4),
                'all_emotions': {k: round(v, 4) for k, v in emotions.items()},
                'tone': self.TONE_MAP.get(main_emotion, '自然'),
                'face_detected': True
            }
            
        except Exception as e:
            return {
                'emotion': None,
                'emotion_cn': '检测失败',
                'confidence': 0.0,
                'all_emotions': {},
                'tone': f'错误: {str(e)}',
                'face_detected': False
            }
    
    def _detect_deepface(self, frame) -> Optional[Dict[str, Any]]:
        """使用 DeepFace 库检测情绪"""
        import numpy as np
        import tempfile
        import os
        
        try:
            # DeepFace 需要图片文件，保存临时文件
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                import cv2
                cv2.imwrite(tmp.name, frame)
                tmp_path = tmp.name
            
            # 检测情绪
            result = self.model.analyze(
                img_path=tmp_path,
                actions=['emotion'],
                enforce_detection=True
            )
            
            # 清理临时文件
            os.unlink(tmp_path)
            
            emotions = result[0]['emotion']
            
            # 找出最高置信度的情绪
            main_emotion = max(emotions, key=emotions.get)
            confidence = emotions[main_emotion] / 100.0
            
            return {
                'emotion': main_emotion,
                'emotion_cn': self.EMOTION_MAP.get(main_emotion, main_emotion),
                'confidence': round(confidence, 4),
                'all_emotions': {k: round(v / 100.0, 4) for k, v in emotions.items()},
                'tone': self.TONE_MAP.get(main_emotion, '自然'),
                'face_detected': True
            }
            
        except Exception as e:
            return {
                'emotion': None,
                'emotion_cn': '检测失败',
                'confidence': 0.0,
                'all_emotions': {},
                'tone': f'错误: {str(e)}',
                'face_detected': False
            }


def create_model(backend: str = 'fer') -> EmotionModel:
    """创建情绪识别模型"""
    return EmotionModel(backend=backend)
