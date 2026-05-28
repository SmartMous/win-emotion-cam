# -*- coding: utf-8 -*-
"""
模型管理模块
使用 MTCNN 人脸检测 + HSEmotion EfficientNet-B0 情绪识别
"""

import os
from typing import Optional, Dict, Any

import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
import timm


class EmotionModel:
    """情绪识别模型包装类"""

    # HSEmotion 8分类 → 中文映射
    EMOTION_MAP = {
        'Anger': '愤怒',
        'Contempt': '轻蔑',
        'Disgust': '厌恶',
        'Fear': '恐惧',
        'Happiness': '开心',
        'Neutral': '中性',
        'Sadness': '悲伤',
        'Surprise': '惊讶'
    }

    # 英文 key 映射（兼容旧接口）
    EMOTION_KEY_MAP = {
        'Anger': 'angry',
        'Contempt': 'contempt',
        'Disgust': 'disgusted',
        'Fear': 'fearful',
        'Happiness': 'happy',
        'Neutral': 'neutral',
        'Sadness': 'sad',
        'Surprise': 'surprised'
    }

    # 情绪到沟通语气的映射
    TONE_MAP = {
        'angry': '冷静、平和、避免对抗',
        'contempt': '尊重、保持距离',
        'disgusted': '尊重、保持距离',
        'fearful': '安抚、温柔、支持',
        'happy': '轻松、热情',
        'neutral': '自然、专业',
        'sad': '温和、耐心、倾听',
        'surprised': '平稳、确认信息'
    }

    # HSEmotion 分类索引
    IDX_TO_CLASS = {
        0: 'Anger', 1: 'Contempt', 2: 'Disgust', 3: 'Fear',
        4: 'Happiness', 5: 'Neutral', 6: 'Sadness', 7: 'Surprise'
    }

    IMG_SIZE = 224

    def __init__(self, backend: str = 'hsemotion'):
        """
        Args:
            backend: 模型后端，默认 'hsemotion'
        """
        self.backend = backend
        self.device = 'cpu'

        # 预处理
        self._transform = T.Compose([
            T.Resize((self.IMG_SIZE, self.IMG_SIZE)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # 加载人脸检测器
        from facenet_pytorch import MTCNN
        self._face_detector = MTCNN(keep_all=True, device=self.device,
                                     min_face_size=60, thresholds=[0.6, 0.7, 0.7])

        # 加载情绪识别模型
        self._load_model()

    def _load_model(self):
        """加载 HSEmotion EfficientNet-B0 模型"""
        # 模型文件路径（项目 data 目录）
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        model_path = os.path.join(model_dir, 'enet_b0_8_best_afew.pt')

        if not os.path.isfile(model_path):
            raise FileNotFoundError(
                f"模型文件未找到: {model_path}\n"
                "请将 enet_b0_8_best_afew.pt 放到项目的 data/ 目录下"
            )

        # 加载旧版模型并提取权重
        old_model = torch.load(model_path, map_location=self.device)
        state_dict = old_model.state_dict()

        # 提取 classifier 权重（旧模型 classifier 是 Sequential）
        if isinstance(old_model.classifier, torch.nn.Sequential):
            self._classifier_weight = old_model.classifier[0].weight.cpu().data.numpy()
            self._classifier_bias = old_model.classifier[0].bias.cpu().data.numpy()
        else:
            self._classifier_weight = old_model.classifier.weight.cpu().data.numpy()
            self._classifier_bias = old_model.classifier.bias.cpu().data.numpy()

        # 创建新版 EfficientNet-B0 并加载权重
        remapped = {}
        for k, v in state_dict.items():
            if k == 'classifier.0.weight':
                remapped['classifier.weight'] = v
            elif k == 'classifier.0.bias':
                remapped['classifier.bias'] = v
            else:
                remapped[k] = v

        self._model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=8)
        self._model.load_state_dict(remapped, strict=True)
        self._model.classifier = torch.nn.Identity()
        self._model = self._model.to(self.device).eval()

    def detect(self, frame) -> Dict[str, Any]:
        """
        检测情绪

        Args:
            frame: OpenCV 图像帧 (numpy array, RGB)

        Returns:
            检测结果字典
        """
        try:
            # MTCNN 人脸检测
            img_pil = Image.fromarray(frame)
            boxes, probs = self._face_detector.detect(img_pil)

            if boxes is None or len(boxes) == 0:
                return {
                    'emotion': None,
                    'emotion_cn': '未检测到人脸',
                    'confidence': 0.0,
                    'all_emotions': {},
                    'tone': '无法判断',
                    'face_detected': False
                }

            # 取置信度最高的人脸
            if probs is not None:
                best_idx = int(np.argmax(probs))
            else:
                best_idx = 0

            x1, y1, x2, y2 = boxes[best_idx].astype(int)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

            if x2 <= x1 or y2 <= y1:
                return {
                    'emotion': None,
                    'emotion_cn': '未检测到人脸',
                    'confidence': 0.0,
                    'all_emotions': {},
                    'tone': '无法判断',
                    'face_detected': False
                }

            # 裁剪人脸并推理
            face = frame[y1:y2, x1:x2]
            img_tensor = self._transform(Image.fromarray(face)).unsqueeze_(0)

            with torch.no_grad():
                features = self._model(img_tensor.to(self.device))
            features = features.cpu().numpy()

            # 计算各分类分数
            scores = np.dot(features, self._classifier_weight.T) + self._classifier_bias
            scores = scores[0]

            # softmax
            scores_exp = np.exp(scores - np.max(scores))
            probs = scores_exp / scores_exp.sum()

            # 找最高置信度情绪
            best_class_idx = int(np.argmax(probs))
            emotion_en = self.IDX_TO_CLASS[best_class_idx]
            emotion_key = self.EMOTION_KEY_MAP[emotion_en]
            confidence = float(probs[best_class_idx])

            all_emotions = {}
            for i, class_name in self.IDX_TO_CLASS.items():
                key = self.EMOTION_KEY_MAP[class_name]
                all_emotions[key] = round(float(probs[i]), 4)

            return {
                'emotion': emotion_key,
                'emotion_cn': self.EMOTION_MAP[emotion_en],
                'confidence': round(confidence, 4),
                'all_emotions': all_emotions,
                'tone': self.TONE_MAP.get(emotion_key, '自然'),
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


def create_model(backend: str = 'hsemotion') -> EmotionModel:
    """创建情绪识别模型"""
    return EmotionModel(backend=backend)
