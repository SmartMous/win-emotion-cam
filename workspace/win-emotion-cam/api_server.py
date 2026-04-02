# -*- coding: utf-8 -*-
"""
win-emotion-cam API 服务
提供 RESTful 接口进行情绪识别
"""
import io
import sys
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from win_emotion_cam import create_detector
from win_emotion_cam.camera import Camera


# 创建 FastAPI 应用
app = FastAPI(
    title="win-emotion-cam API",
    description="Windows 摄像头实时情绪识别 API",
    version="1.0.0"
)

# 全局检测器实例
detector = None
camera = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global detector, camera
    print("🚀 初始化情绪识别模型...")
    detector = create_detector(model_backend='fer', fps_limit=2)
    camera = Camera(camera_index=0)
    
    if not camera.open():
        print("⚠️ 警告: 无法打开摄像头")
    else:
        print("✅ 摄像头已就绪")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    global camera
    if camera:
        camera.release()
    print("👋 服务已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "win-emotion-cam API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/detect")
async def detect_emotion(image: UploadFile = File(...)):
    """
    通过上传图片检测情绪
    
    Args:
        image: 图片文件
        
    Returns:
        情绪识别结果
    """
    global detector
    
    if detector is None:
        raise HTTPException(status_code=500, detail="模型未初始化")
    
    try:
        # 读取图片
        contents = await image.read()
        
        # 将字节转换为 numpy 数组
        import numpy as np
        import cv2
        
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="无法解码图片")
        
        # BGR 转 RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 检测情绪
        result = detector.detect(frame)
        
        # 构建响应
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "emotion": result.get('emotion'),
                "emotion_cn": result.get('emotion_cn'),
                "confidence": result.get('confidence'),
                "all_emotions": result.get('all_emotions'),
                "tone": result.get('tone'),
                "face_detected": result.get('face_detected', False)
            }
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 1,
                "message": "error",
                "error": str(e)
            }
        )


@app.get("/detect/camera")
async def detect_from_camera():
    """
    从实时摄像头检测情绪
    
    Returns:
        当前摄像头画面的情绪识别结果
    """
    global detector, camera
    
    if detector is None:
        raise HTTPException(status_code=500, detail="模型未初始化")
    
    if camera is None or not camera.is_opened():
        raise HTTPException(status_code=500, detail="摄像头未打开")
    
    try:
        frame = camera.read()
        
        if frame is None:
            raise HTTPException(status_code=500, detail="无法读取摄像头")
        
        # 检测情绪
        result = detector.detect(frame)
        
        # 构建响应
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "emotion": result.get('emotion'),
                "emotion_cn": result.get('emotion_cn'),
                "confidence": result.get('confidence'),
                "all_emotions": result.get('all_emotions'),
                "tone": result.get('tone'),
                "face_detected": result.get('face_detected', False)
            }
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 1,
                "message": "error",
                "error": str(e)
            }
        )


def main():
    """启动 API 服务"""
    print("\n" + "=" * 50)
    print("🚀 win-emotion-cam API 服务")
    print("=" * 50)
    print("📍 服务地址: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print("=" * 50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
