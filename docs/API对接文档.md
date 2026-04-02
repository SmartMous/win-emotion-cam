# win-emotion-cam API 对接文档

本文档面向需要将情绪识别能力集成到自身系统的开发者。

## 概述

win-emotion-cam 提供两种对接方式：
1. **直接调用 Python 模块** - 适合 Python 项目
2. **REST API 调用** - 适合任意编程语言

---

## 对接方式一：Python 模块对接

### 安装

```bash
pip install win-emotion-cam
# 或从源码安装
git clone https://github.com/SmartMous/win-emotion-cam.git
cd win-emotion-cam
pip install -r requirements.txt
```

### 基本使用

```python
from win_emotion_cam import create_detector

# 1. 创建检测器
detector = create_detector(
    camera_index=0,     # 摄像头索引
    model_backend='fer', # 模型: 'fer' 或 'deepface'
    fps_limit=5         # 帧率限制
)

# 2. 启动
if not detector.start():
    print("无法打开摄像头")
    exit(1)

# 3. 检测情绪
result = detector.detect()

# 4. 处理结果
if result['face_detected']:
    print(f"情绪: {result['emotion_cn']}")
    print(f"置信度: {result['confidence']:.1%}")
    print(f"建议语气: {result['tone']}")
else:
    print("未检测到人脸")

# 5. 停止
detector.stop()
```

### 完整示例：实时检测循环

```python
from win_emotion_cam import create_detector
import time

detector = create_detector(fps_limit=3)
detector.start()

print("开始实时检测，按 Ctrl+C 退出")

try:
    while True:
        result = detector.detect()
        
        if result['face_detected']:
            print(f"\r情绪: {result['emotion_cn']} | 置信度: {result['confidence']:.1%} | 语气: {result['tone']}", end='')
        else:
            print("\r未检测到人面...", end='')
        
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("\n退出")
finally:
    detector.stop()
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| emotion | string | 情绪英文名 (如 'happy') |
| emotion_cn | string | 情绪中文名 (如 '开心') |
| confidence | float | 置信度 (0-1) |
| all_emotions | dict | 所有情绪的概率 |
| tone | string | 建议的沟通语气 |
| face_detected | bool | 是否检测到人脸 |

---

## 对接方式二：REST API 对接

### 启动服务

```bash
python api_server.py
```

服务地址: `http://localhost:8000`

### 接口列表

#### 1. 健康检查

**GET** `/health`

```json
{"status": "healthy"}
```

#### 2. 图片情绪检测

**POST** `/detect`

**请求：**
- Content-Type: `multipart/form-data`
- Body: `image` (图片文件)

**cURL 示例：**
```bash
curl -X POST http://localhost:8000/detect \
  -F "image=@/path/to/image.jpg"
```

**Python 示例：**
```python
import requests

url = "http://localhost:8000/detect"
files = {'image': open('test.jpg', 'rb')}

response = requests.post(url, files=files)
result = response.json()

print(result['data']['emotion_cn'])
print(result['data']['tone'])
```

**响应：**
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

**错误响应：**
```json
{
  "code": 1,
  "message": "error",
  "error": "错误信息"
}
```

#### 3. 摄像头实时检测

**GET** `/detect/camera`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "emotion": "neutral",
    "emotion_cn": "中性",
    "confidence": 0.75,
    "all_emotions": {...},
    "tone": "自然、专业",
    "face_detected": true
  }
}
```

---

## 情绪与语气映射表

| 情绪 | 英文 | 中文 | 建议语气 |
|------|------|------|----------|
| 开心 | happy | 开心 | 轻松、热情 |
| 悲伤 | sad | 悲伤 | 温和、耐心、倾听 |
| 愤怒 | angry | 愤怒 | 冷静、平和、避免对抗 |
| 惊讶 | surprised | 惊讶 | 平稳、确认信息 |
| 恐惧 | fearful | 恐惧 | 安抚、温柔、支持 |
| 厌恶 | disgusted | 厌恶 | 尊重、保持距离 |
| 中性 | neutral | 中性 | 自然、专业 |

---

## 对接示例

### Web 前端对接

```javascript
// 上传图片检测情绪
async function detectEmotion(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('http://localhost:8000/detect', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    return result.data;
}

// 使用
const input = document.querySelector('input[type="file"]');
input.addEventListener('change', async (e) => {
    const data = await detectEmotion(e.target.files[0]);
    console.log('情绪:', data.emotion_cn);
    console.log('语气:', data.tone);
});
```

### 小程序对接

```javascript
wx.chooseImage({
    count: 1,
    success: async (res) => {
        const tempFilePath = res.tempFilePaths[0];
        
        wx.uploadFile({
            url: 'http://your-server:8000/detect',
            filePath: tempFilePath,
            name: 'image',
            success: (res) => {
                const data = JSON.parse(res.data);
                console.log('情绪:', data.data.emotion_cn);
            }
        })
    }
})
```

### Java 对接

```java
OkHttpClient client = new OkHttpClient();

MediaType mediaType = MediaType.parse("image/jpeg");
File file = new File("test.jpg");
RequestBody body = RequestBody.create(mediaType, file);

Request request = new Request.Builder()
    .url("http://localhost:8000/detect")
    .post(body)
    .addHeader("Content-Type", "image/jpeg")
    .build();

Response response = client.newCall(request).execute();
System.out.println(response.body().string());
```

---

## 部署建议

### 本地部署

```bash
# 直接运行
python api_server.py

# 或使用 gunicorn (生产环境)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
```

### Docker 部署

```dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "api_server.py"]
```

### 云服务器部署

1. 将服务部署到云服务器
2. 配置安全组开放 8000 端口
3. 使用 Nginx 反向代理
4. 配置域名 SSL 证书

---

## 错误码

| code | 说明 |
|------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

---

## 性能指标

| 指标 | FER | DeepFace |
|------|-----|----------|
| 单帧检测时间 | ~100ms | ~500ms |
| 推荐帧率 | 5-10 FPS | 1-2 FPS |
| 内存占用 | ~500MB | ~1GB |

---

## 技术支持

- GitHub: https://github.com/SmartMous/win-emotion-cam
- 问题反馈: https://github.com/SmartMous/win-emotion-cam/issues
