# -*- coding: utf-8 -*-
"""
API 客户端示例
"""
import requests
import argparse


def detect_via_api(image_path: str, api_url: str = "http://localhost:8000"):
    """
    通过 API 检测图片情绪
    
    Args:
        image_path: 图片路径
        api_url: API 地址
    """
    url = f"{api_url}/detect"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(url, files=files)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        
        if data.get('code') == 0:
            result = data.get('data', {})
            print("\n" + "=" * 40)
            print("📊 情绪识别结果:")
            print(f"   情绪: {result.get('emotion_cn')} ({result.get('emotion')})")
            print(f"   置信度: {result.get('confidence'):.2%}")
            print(f"   建议语气: {result.get('tone')}")
            print(f"   检测到人脸: {result.get('face_detected')}")
            print("=" * 40)
            
            # 显示所有情绪概率
            all_emotions = result.get('all_emotions', {})
            if all_emotions:
                print("\n📈 所有情绪概率:")
                sorted_emotions = sorted(
                    all_emotions.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                for emotion, prob in sorted_emotions:
                    bar = '█' * int(prob * 20)
                    print(f"   {emotion:12s}: {prob:5.1%} {bar}")
        else:
            print(f"❌ 识别失败: {data.get('message')}")
    
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 API 服务: {api_url}")
        print("   请确保已启动 api_server.py")
    except Exception as e:
        print(f"❌ 错误: {e}")


def detect_from_camera(api_url: str = "http://localhost:8000"):
    """
    从实时摄像头检测
    
    Args:
        api_url: API 地址
    """
    url = f"{api_url}/detect/camera"
    
    try:
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            return
        
        data = response.json()
        
        if data.get('code') == 0:
            result = data.get('data', {})
            print("📷 当前情绪:", result.get('emotion_cn'), 
                  f"({result.get('confidence'):.1%})")
            print("💬 建议语气:", result.get('tone'))
        else:
            print(f"❌ 识别失败: {data.get('message')}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")


def main():
    parser = argparse.ArgumentParser(description='API 客户端示例')
    parser.add_argument('image', nargs='?', help='图片路径')
    parser.add_argument('--url', default='http://localhost:8000', help='API 地址')
    parser.add_argument('--camera', action='store_true', help='从摄像头检测')
    
    args = parser.parse_args()
    
    if args.camera:
        detect_from_camera(args.url)
    elif args.image:
        detect_via_api(args.image, args.url)
    else:
        print("用法:")
        print("  检测图片: python api_client.py <图片路径>")
        print("  摄像头检测: python api_client.py --camera")
        print("  指定 API: python api_client.py <图片路径> --url http://localhost:8000")


if __name__ == '__main__':
    main()
