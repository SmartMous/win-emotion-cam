# win-emotion-cam

Windows 摄像头实时人物情绪识别，支持独立运行和外部 API 调用。

## 功能特点

- 📷 **本地摄像头捕获**：直接调用 Windows 系统摄像头
- 🧠 **本地算力推理**：所有计算在本地完成，无需联网
- 😊 **7种基础情绪识别**：开心、悲伤、愤怒、惊讶、恐惧、厌恶、中性
- 🚀 **独立运行**：可直接启动，实时显示情绪识别结果
- 🔌 **API 接口**：提供 RESTful API，支持外部程序调用
- 📝 **完整中文文档**：详细的安装使用说明

## 支持的情绪类型

| 情绪 | 说明 |
|------|------|
| happy | 开心/愉悦 |
| sad | 悲伤/难过 |
| angry | 愤怒/生气 |
| surprised | 惊讶/意外 |
| fearful | 恐惧/害怕 |
| disgusted | 厌恶/反感 |
| neutral | 中性/平静 |

## 快速开始

### 环境要求

- Windows 10/11
- Python 3.8+
- 摄像头设备

### 安装依赖

```bash
git clone https://github.com/SmartMous/win-emotion-cam.git
cd win-emotion-cam
pip install -r requirements.txt
```

### 独立运行（实时识别）

```bash
python main.py
```

这会打开摄像头窗口，实时显示识别到的情绪和置信度。

### 启动 API 服务

```bash
python api_server.py
```

服务默认启动在 `http://localhost:8000`

### API 调用示例

**发送图片进行情绪识别：**
```bash
curl -X POST http://localhost:8000/detect \
  -F "image=@test.jpg"
```

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "emotion": "happy",
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
    "face_detected": true
  }
}
```

## 项目结构

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
│   └── 开发说明.md           # 开发文档
├── main.py                   # 独立运行入口
├── api_server.py             # API 服务入口
├── requirements.txt          # 依赖列表
└── README.md                # 本文件
```

## 技术栈

- **OpenCV**：摄像头捕获和图像处理
- **DeepFace** / **FER**：情绪识别模型
- **FastAPI**：API 服务框架
- **numpy**：数值计算

## 许可证

MIT License

## 作者

SmartMous
