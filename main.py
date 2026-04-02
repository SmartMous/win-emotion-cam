# -*- coding: utf-8 -*-
"""
win-emotion-cam 主程序
实时摄像头情绪识别
"""
import argparse
import sys

from win_emotion_cam import create_detector


def main():
    parser = argparse.ArgumentParser(
        description='Windows 摄像头实时情绪识别'
    )
    parser.add_argument(
        '-c', '--camera',
        type=int,
        default=0,
        help='摄像头索引 (默认: 0)'
    )
    parser.add_argument(
        '-m', '--model',
        type=str,
        default='fer',
        choices=['fer', 'deepface'],
        help='使用的模型后端 (默认: fer)'
    )
    parser.add_argument(
        '-f', '--fps',
        type=int,
        default=5,
        help='检测帧率限制 (默认: 5)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 50)
    print("🦞 win-emotion-cam 情绪识别系统")
    print("=" * 50)
    print(f"📷 摄像头: {args.camera}")
    print(f"🧠 模型: {args.model}")
    print(f"⚡ 检测帧率: {args.fps} FPS")
    print("=" * 50 + "\n")
    
    # 创建并启动检测器
    detector = create_detector(
        camera_index=args.camera,
        model_backend=args.model,
        fps_limit=args.fps
    )
    
    if not detector.start():
        print("❌ 无法打开摄像头，请检查:")
        print("   1. 摄像头是否已连接")
        print("   2. 是否有其他程序占用摄像头")
        sys.exit(1)
    
    # 运行主循环
    detector.run_loop()


if __name__ == '__main__':
    main()
