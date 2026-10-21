import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from PIL import Image

# 1. تعريف الـ app في البداية
app = FastAPI(title="NovaCore مساعد حل الواجبات الذكي")

# 2. تفعيل الـ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. ربط مجلد الملفات الاستاتيكية (لقراءة الصورة من مجلد static في المشروع)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. الـ handler لشغل Vercel
handler = app

# سحب المفتاح الأساسي كخيار افتراضي
DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# الواجهة البنفسجية الزجاجية
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaCore Studio | مساعد الواجبات الذكي</title>
    <meta name="monetag" content="942542734552006594c5d7ca3ed92da5">
    <script src="https://quge5.com/88/tag.min.js" data-zone="299598" async data-cfasync="false"></script>
    <script src="https://5gvci.com/act/files/tag.min.js?z=12087130" data-cfasync="false" async></script>
    <script>(function(s){s.dataset.zone='12087151',s.src='https://n6wxm.com/vignette.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>
    <!-- أيقونة المتصفح في التبويب -->
    <link rel="icon" type="image/png" href="/static/logo.png">
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
        .logo-img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 12px;
            border: 2px solid rgba(192, 132, 252, 0.4);
            box-shadow: 0 0 15px rgba(192, 132, 252, 0.3);
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
            margin-bottom: 25px;
            font-size: 1.05rem;
        }

        .api-section {
            background: rgba(15, 10, 30, 0.4);
            border: 1px solid rgba(192, 132, 252, 0.2);
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 25px;
            text-align: right;
        }
        .api-link {
            color: #c084fc;
            font-weight: 600;
            font-size: 0.95rem;
            text-decoration: underline;
            cursor: pointer;
            display: inline-block;
            margin-bottom: 10px;
            transition: color 0.3s ease;
        }
        .api-link:hover {
            color: #f472b6;
        }
        .api-input-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .api-input {
            flex: 1;
            min-width: 200px;
            background: rgba(10, 7, 24, 0.6);
            border: 1px solid rgba(192, 132, 252, 0.3);
            border-radius: 12px;
            padding: 10px 15px;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
        }
        .api-input:focus {
            border-color: #c084fc;
        }
        .api-save-btn {
            background: linear-gradient(135deg, #10b981, #059669);
            color: #fff;
            border: none;
            padding: 10px 18px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .api-save-btn:hover {
            opacity: 0.9;
        }
        .api-clear-btn {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
            padding: 10px 15px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .api-clear-btn:hover {
            background: rgba(239, 68, 68, 0.4);
        }

        .upload-section {
            border: 2px dashed rgba(192, 132, 252, 0.3);
            border-radius: 20px;
            padding: 25px 20px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(15, 10, 30, 0.3);
            margin-bottom: 20px;
            box-shadow: inset 0 4px 10px rgba(0,0,0,0.2);
        }
        .upload-section:hover {
            border-color: #c084fc;
            background: rgba(192, 132, 252, 0.07);
            transform: scale(1.01);
        }
        #fileInput {
            display: none;
        }
        .upload-icon {
            font-size: 2rem;
            margin-bottom: 8px;
            display: inline-block;
        }
        .upload-label {
            cursor: pointer;
            display: block;
            font-size: 1.1rem;
            color: #e2e8f0;
            font-weight: 600;
        }
        .upload-label span {
            display: block;
            margin-top: 5px;
            font-size: 0.85rem;
            color: #74718a;
            font-weight: 400;
        }
        
        .text-input-section {
            margin-bottom: 20px;
            text-align: right;
        }
        .text-input-section label {
            display: block;
            margin-bottom: 8px;
            color: #c084fc;
            font-weight: 600;
            font-size: 0.95rem;
        }
        textarea {
            width: 100%;
            background: rgba(15, 10, 30, 0.5);
            border: 1px solid rgba(192, 132, 252, 0.3);
            border-radius: 16px;
            padding: 15px;
            color: #f8fafc;
            font-size: 1.05rem;
            resize: vertical;
            min-height: 100px;
            outline: none;
            transition: all 0.3s ease;
        }
        textarea:focus {
            border-color: #c084fc;
            box-shadow: 0 0 10px rgba(192, 132, 252, 0.2);
        }

        .actions-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }
        .action-btn {
            background: rgba(192, 132, 252, 0.1);
            border: 1px solid rgba(192, 132, 252, 0.3);
            color: #f8fafc;
            padding: 14px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .action-btn:hover {
            background: rgba(192, 132, 252, 0.2);
            border-color: #c084fc;
        }
        .btn {
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: #ffffff;
            border: none;
            padding: 16px 32px;
            font-size: 1.15rem;
            font-weight: 600;
            border-radius: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(168, 85, 247, 0.3);
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(168, 85, 247, 0.5);
            background: linear-gradient(135deg, #4f46e5, #9333ea);
        }
        .btn:disabled {
            background: #2e2a47;
            box-shadow: none;
            cursor: not-allowed;
            transform: none;
            color: #64748b;
        }
        
        #cameraModal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(5, 3, 15, 0.85);
            backdrop-filter: blur(10px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .camera-box {
            background: #140d2b;
            border: 1px solid rgba(192, 132, 252, 0.3);
            padding: 25px;
            border-radius: 24px;
            text-align: center;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 25px 50px rgba(0,0,0,0.6);
        }
        video {
            width: 100%;
            max-height: 350px;
            border-radius: 14px;
            background: #000;
            object-fit: cover;
            margin-bottom: 15px;
        }
        .cam-controls {
            display: flex;
            gap: 10px;
        }

        .result-section {
            margin-top: 40px;
            text-align: right;
            display: none;
            animation: fadeIn 0.6s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: #c084fc;
        }
        .result-box {
            background: rgba(10, 7, 24, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 18px;
            padding: 30px;
            color: #ffffff;
            font-size: 1.1rem;
            line-height: 1.9;
            box-shadow: inset 0 4px 12px rgba(0,0,0,0.4);
        }
        .result-box h1, .result-box h2, .result-box h3 {
            color: #c084fc;
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: 700;
        }
        .result-box p { margin-bottom: 12px; color: #f1f5f9; }
        .result-box ul, .result-box ol { margin-right: 25px; margin-bottom: 15px; }
        .result-box li { margin-bottom: 6px; }
        .result-box strong { color: #f472b6; font-weight: 700; }
        
        .loading {
            display: none;
            margin: 25px 0;
            font-size: 1.15rem;
            color: #f472b6;
            font-weight: 600;
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255,255,255,0.1);
            border-top-color: #c084fc;
            border-radius: 50%;
            margin: 15px auto;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>

<div class="container">
    <!-- اللوجو الخاص بالموقع -->
    <img src="/static/logo.png" alt="Logo" class="logo-img" onerror="this.style.display='none'">
    <div class="brand">NovaCore Studio</div>
    <h1>مساعد حل الواجبات</h1>
    <p class="subtitle">اكتب سؤالك، ارفع صورته، أو التقطه بالكاميرا وسيحله الذكاء الاصطناعي فوراً</p>
    
    <div class="api-section">
        <a href="https://aistudio.google.com/app/apikey" target="_blank" class="api-link">
            🔗 اضغط هنا لإنشاء مفتاح API جديد من جوجل (للمحاولات المجانية)
        </a>
        <div class="api-input-group">
            <input type="password" id="customApiKey" class="api-input" placeholder="الصق مفتاح الـ API هنا...">
            <button type="button" class="api-save-btn" onclick="saveApiKey()">أضف المفتاح ⚡</button>
            <button type="button" class="api-clear-btn" onclick="clearApiKey()">حذف المفتاح 🗑️</button>
        </div>
    </div>

    <div class="text-input-section">
        <label for="questionText">💬 اكتب رسالتك أو سؤالك هنا:</label>
        <textarea id="questionText" placeholder="اكتب سؤالك التفصيلي أو اطلب شرح مسألة معينة..."></textarea>
    </div>

    <div class="upload-section" onclick="document.getElementById('fileInput').click()">
        <span class="upload-icon">🔮</span>
        <label class="upload-label">
            اضغط هنا لإرفاق صورة (اختياري)
            <span id="fileNameDisplay">يدعم الامتدادات البصرية (PNG, JPG, JPEG)</span>
        </label>
        <input type="file" id="fileInput" accept="image/*" onchange="updateFileName(this)">
    </div>

    <div class="actions-grid">
        <button type="button" class="action-btn" onclick="openCameraModal()">
            📷 فتح الكاميرا للتصوير
        </button>
        <button type="button" class="action-btn" onclick="document.getElementById('fileInput').click()">
            📁 استعراض الملفات
        </button>
    </div>
    
    <button class="btn" id="solveBtn" onclick="uploadAndSolve()">إرسال السؤال وحله ✨</button>
    
    <div class="loading" id="loadingArea">
        <div class="spinner"></div>
        <span>جاري تحليل السؤال وصياغة الحل النموذجي...</span>
    </div>
    
    <div class="result-section" id="resultSection">
        <div class="result-title">✨ الحل المنسق والشرح:</div>
        <div class="result-box" id="resultBox"></div>
    </div>
</div>

<div id="cameraModal">
    <div class="camera-box">
        <h3 style="color: #c084fc; margin-bottom: 15px;">وجه الكاميرا نحو السؤال 📸</h3>
        <video id="cameraStream" autoplay playsinline></video>
        <canvas id="snapshotCanvas" style="display:none;"></canvas>
        <div class="cam-controls">
            <button type="button" class="btn" onclick="takeSnapshot()" style="background: linear-gradient(135deg, #22c55e, #16a34a);">التقاط الصورة 📸</button>
            <button type="button" class="action-btn" onclick="closeCameraModal()" style="background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.4);">إغلاق</button>
        </div>
    </div>
</div>

<script>
    let mediaStream = null;

    window.onload = function() {
        const savedKey = localStorage.getItem('user_gemini_api_key');
        if(savedKey) {
            document.getElementById('customApiKey').value = savedKey;
        }
    }

    function saveApiKey() {
        const keyVal = document.getElementById('customApiKey').value.trim();
        if(!keyVal) {
            clearApiKey();
            return;
        }
        localStorage.setItem('user_gemini_api_key', keyVal);
        alert('تم حفظ المفتاح بنجاح! المحاولات الجديدة هتشتغل بيه فوراً 🚀');
    }

    function clearApiKey() {
        localStorage.removeItem('user_gemini_api_key');
        document.getElementById('customApiKey').value = '';
        alert('تم حذف المفتاح المخصص! الموقع هيرجع يستخدم المفتاح الافتراضي للسيرفر 🔄');
    }

    function updateFileName(input) {
        const display = document.getElementById('fileNameDisplay');
        if(input.files && input.files[0]) {
            display.innerText = "الملف الجاهز: " + input.files[0].name;
            display.style.color = "#c084fc";
        } else {
            display.innerText = "يدعم الامتدادات البصرية (PNG, JPG, JPEG)";
            display.style.color = "#74718a";
        }
    }

    async function openCameraModal() {
        const modal = document.getElementById('cameraModal');
        const video = document.getElementById('cameraStream');
        modal.style.display = "flex";
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
            video.srcObject = mediaStream;
        } catch (err) {
            alert("عذراً، لا يمكن الوصول للكاميرا. تأكد من إعطاء الصلاحية للمتصفح.");
            closeCameraModal();
        }
    }

    function closeCameraModal() {
        const modal = document.getElementById('cameraModal');
        modal.style.display = "none";
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
    }

    function takeSnapshot() {
        const video = document.getElementById('cameraStream');
        const canvas = document.getElementById('snapshotCanvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(blob => {
            const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            document.getElementById('fileInput').files = dataTransfer.files;
            updateFileName(document.getElementById('fileInput'));
            closeCameraModal();
        }, 'image/jpeg');
    }

    async function uploadAndSolve() {
        const fileInput = document.getElementById('fileInput');
        const questionText = document.getElementById('questionText').value.trim();
        const customKey = localStorage.getItem('user_gemini_api_key') || '';
        const solveBtn = document.getElementById('solveBtn');
        const loadingArea = document.getElementById('loadingArea');
        const resultSection = document.getElementById('resultSection');
        const resultBox = document.getElementById('resultBox');
        
        if(!questionText && (!fileInput.files || !fileInput.files[0])) {
            alert('برجاء كتابة سؤالك أو إرفاق/تصوير صورة على الأقل يا فنان!');
            return;
        }
        
        const formData = new FormData();
        formData.append("text", questionText);
        if(fileInput.files && fileInput.files[0]) {
            formData.append("file", fileInput.files[0]);
        }
        
        solveBtn.disabled = true;
        loadingArea.style.display = "block";
        resultSection.style.display = "none";
        
        const headers = {};
        if(customKey) {
            headers['x-custom-api-key'] = customKey;
        }
        
        try {
            const response = await fetch('/solve', {
                method: 'POST',
                headers: headers,
                body: formData
            });
            
            const data = await response.json();
            
            if(response.ok) {
                resultBox.innerHTML = marked.parse(data.solution);
                resultSection.style.display = "block";
            } else {
                alert("خطأ من السيرفر: " + (data.detail || "مشكلة غير معروفة"));
            }
        } catch (error) {
            alert("فشل الاتصال، تأكد من تشغيل السيرفر أو الرفع السليم على Vercel");
        } finally {
            solveBtn.disabled = false;
            loadingArea.style.display = "none";
        }
    }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTML_TEMPLATE

@app.post("/solve")
async def solve_homework(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    x_custom_api_key: Optional[str] = Header(None)
):
    if not text and not file:
        raise HTTPException(status_code=400, detail="يرجى إرسال نص السؤال أو صورة واحدة على الأقل.")
    
    try:
        active_key = x_custom_api_key if (x_custom_api_key and x_custom_api_key.strip()) else DEFAULT_GEMINI_KEY
        if not active_key:
            raise HTTPException(status_code=400, detail="مفتاح الـ API غير موجود. يرجى إدخال مفتاح صالح.")
        
        active_client = genai.Client(api_key=active_key)
        contents = []
        
        if file and file.filename:
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="الملف المرفوع يجب أن يكون صورة.")
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            contents.append(image)
        
        base_prompt = (
            "أنت معلم خبير ومساعد أكاديمي متميز. "
            "قم بالإجابة على السؤال أو تحليل المرفقات المقدمة بدقة، "
            "ثم قدم الحل الصحيح والنموذجي خطوة بخطوة مع الشرح المفصل باللغة العربية واللهجة المصرية الشعبية الأصلية. "
            "استخدم عناوين فرعية ونقاط واضحة وتنسيق Markdown غني (مثل استخدام النجوم للتأكيد) "
            "ليكون النص جذاباً وسهل القراءة والفهم."
        )
        
        if text:
            full_prompt = f"{base_prompt}\n\nسؤال الطالب أو نصه:\n{text}"
            contents.append(full_prompt)
        else:
            contents.append(base_prompt)
        
        response = active_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents
        )
        
        return {
            "status": "success",
            "solution": response.text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء معالجة الطلب: {str(e)}")
