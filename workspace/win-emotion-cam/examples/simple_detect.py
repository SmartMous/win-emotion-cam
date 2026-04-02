# -*- coding: utf-8 -*-
"""
简单示例：单张图片情绪识别
"""
import cv2
from win_emotion_cam import create_detector


def simple_detect():
    """简单识别示例"""
    # 创建检测器
    detector = create_detector(model_backend='fer', fps_limit=1)
    
    # 打开摄像头
    if not detector.start():
        print("❌ 无法打开摄像头")
        return
    
    print("📷 读取摄像头画面...")
    frame = detector.camera.read()
    
    if frame is None:
        print("❌ 无法读取摄像头")
        detector.stop()
        return
    
    # 检测情绪
    print("🔍 检测情绪...")
    result = detector.detect(frame)
    
    # 输出结果
    print("\n" + "=" * 40)
    print("📊 检测结果:")
    print(f"   情绪 (英文): {result.get('emotion')}")
    print(f"   情绪 (中文): {result.get('emotion_cn')}")
    print(f"   置信度: {result.get('confidence'):.2%}")
    print(f"   建议语气: {result.get('tone')}")
    print(f"   检测到人脸: {result.get('face_detected')}")
    print("=" * 40)
    
    if result.get('all_emotions'):
        print("\n📈 所有情绪概率:")
        for emotion, prob in sorted(
            result['all_emotions'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            bar = '█' * int(prob * 20)
            print(f"   {emotion:12s}: {prob:5.1%} {bar}")
    
    detector.stop()


if __name__ == '__main__':
    simple_detect()
