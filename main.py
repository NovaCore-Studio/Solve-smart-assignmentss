import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from PIL import Image

app = FastAPI(title="NovaCore مساعد حل الواجبات الذكي")

# 1. تفعيل الـ CORS عشان فيرسل يقبل الطلبات من أي مكان وميجيبش أخطاء اتصال في المتصفح
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. تعريف الـ handler اللي Vercel بيحتاجه عشان يشغل السيرفر
handler = app

GEMINI_KEY = "AIzaSyBN475Pv_0KDATDe4ROVAwICZJHb8QZXXc"
client = genai.Client(api_key=GEMINI_KEY)

# الواجهة البنفسجية الزجاجية (النسخة السليمة بدون أخطاء)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaCore Studio | مساعد الواجبات الذكي</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * {
            box-sizing: border-box;
            font-family: 'Cairo', sans-serif;
            margin: 0;
            padding: 0;
        }
        body {
            background: linear-gradient(135deg, #0d0b21, #1a1235, #2e114d, #140d2b);
            background-size: 400% 400%;
            animation: gradientBG 12s ease infinite;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 30px 20px;
            color: #f8fafc;
        }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(192, 132, 252, 0.15);
            border-radius: 28px;
            padding: 40px;
            width: 100%;
            max-width: 800px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 2px rgba(255,255,255,0.05);
            text-align: center;
        }
        .brand {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #c084fc;
            font-weight: 700;
            margin-bottom: 5px;
        }
        h1 {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 12px;
            background: linear-gradient(to left, #818cf8, #c084fc, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p.subtitle {
            color: #94a3b8;
            margin-bottom: 35px;
            font-size: 1.05rem;
        }
        .upload-section {
            border: 2px dashed rgba(192, 132, 252, 0.3);
            border-radius: 20px;
            padding: 40px 20px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(15, 10, 30, 0.3);
            margin-bottom: 25px;
            box-shadow: inset 0 4px 10px rgba(0,0,0,0.2);
        }
        .upload-section:hover {
            border-color: #c084fc;
            background: rgba(192, 132, 252, 0.07);
            transform: scale(1.01