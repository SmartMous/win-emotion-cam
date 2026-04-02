# win-emotion-cam

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Windows 摄像头实时人物情绪识别 + 沟通语气建议工具。

## 🎯 功能简介

输入摄像头图像，输出人物情绪分类 + 对应沟通语气建议。

| 输入 | 输出 |
|------|------|
| 📷 摄像头实时画面 | 😊 情绪分类 (7种) + 💬 沟通语气建议 |

## ✨ 功能特点

- 📷 **实时识别**：摄像头视频流实时情绪分析
- 🧠 **本地推理**：无需联网，纯本地计算
- 💬 **语气建议**：针对不同情绪给出沟通语气建议
- 🎯 **7种情绪**：开心、悲伤、愤怒、惊讶、恐惧、厌恶、中性
- 🔌 **双模式**：独立运行 + REST API
- 📖 **中文文档**：完整的使用和开发文档

## 📊 情绪与沟通语气映射

| 情绪 | 中文 | 建议语气 |
|------|------|----------|
| happy | 开心 | 轻松、热情 |
| sad | 悲伤 | 温和、耐心、倾听 |
| angry | 愤怒 | 冷静、平和、避免对抗 |
| surprised | 惊讶 | 平稳、确认信息 |
| fearful | 恐惧 | 安抚、温柔、支持 |
| disgusted | 厌恶 | 尊重、保持距离 |
| neutral | 中性 | 自然、专业 |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/SmartMous/win-emotion-cam.git
cd win-emotion-cam
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行

```bash
python main.py
```

会打开摄像头窗口，实时显示：
- 检测到的情绪
- 置信度
- 建议的沟通语气

按 `q` 或 `Esc` 退出。

## 📖 使用方式

### 独立运行模式

```bash
# 默认参数
python main.py

# 指定参数
python main.py -c 0 -m fer -f 5
```

参数说明：
- `-c, --camera`: 摄像头索引，默认 0
- `-m, --model`: 模型后端 (`fer` 或 `deepface`)，默认 fer
- `-f, --fps`: 检测帧率，默认 5

### API 服务模式

```bash
# 启动服务
python api_server.py
```

服务地址：`http://localhost:8000`
API 文档：`http://localhost:8000/docs`

#### API 接口

**POST /detect** - 图片情绪检测

```bash
curl -X POST http://localhost:8000/detect \
  -F "image=@test.jpg"
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "emotion": "happy",
    "emotion_cn": "开心",
    "confidence": 0.89,
    "all_emotions": {
      "happy": 0.89,
      "sad": 0.02,
      "angry": 0.01,
      "surprised": 0.03,
      "fearful": 0.01,
      "disgusted": 0.02,
      "neutral": 0.02
    },
    "tone": "轻松、热情",
    "face_detected": true
  }
}
```

**GET /detect/camera** - 摄像头实时检测

```bash
curl http://localhost:8000/detect/camera
```

### 作为模块调用

```python
from win_emotion_cam import create_detector

# 创建检测器
detector = create_detector(model_backend='fer', fps_limit=5)
detector.start()

# 检测情绪
result = detector.detect()

# 输出结果
print(f"情绪: {result['emotion_cn']}")
print(f"置信度: {result['confidence']:.1%}")
print(f"建议语气: {result['tone']}")

detector.stop()
```

## 📂 项目结构

```
win-emotion-cam/
├── win_emotion_cam/          # 核心库
│   ├── __init__.py           # 包初始化
│   ├── detector.py           # 情绪检测器
│   ├── camera.py             # 摄像头捕获
│   └── model.py              # 模型加载
├── examples/                 # 示例代码
│   ├── simple_detect.py      # 简单识别示例
│   └── api_client.py         # API 调用示例
├── docs/                     # 文档
│   ├── 开发说明.md           # 开发文档
│   └── API对接文档.md       # API 对接说明
├── main.py                   # 独立运行入口
├── api_server.py             # API 服务入口
├── requirements.txt          # 依赖列表
└── README.md                # 本文件
```

## 🛠️ 技术栈

- **Python 3.8+**
- **OpenCV** - 摄像头捕获、图像处理
- **FER** / **DeepFace** - 情绪识别模型
- **FastAPI** - REST API 框架
- **NumPy** - 数值计算

## 📝 文档

- [开发说明](docs/开发说明.md) - 技术架构、模块说明
- [API对接文档](docs/API对接文档.md) - 第三方对接指南

## ⚠️ 注意事项

1. 首次运行需要下载模型，约 100MB
2. 确保光线充足，避免逆光
3. 脸部正对摄像头效果最佳
4. 建议使用 FER 模型（更快），需要高精度时用 DeepFace

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
