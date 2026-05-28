# -*- coding: utf-8 -*-
"""
win-emotion-cam 核心情绪识别库
"""
from .detector import EmotionDetector, create_detector
from .model import EmotionModel, create_model
from .camera import Camera, list_cameras
