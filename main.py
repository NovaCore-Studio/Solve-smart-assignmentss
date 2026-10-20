import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from PIL import Image

# 1. تعريف الـ app في البداية خالص عشان Vercel يشوفه علطول أول ما يدخل الملف
app = FastAPI(title="NovaCore مساعد حل الواجبات الذكي")

# 2. تفعيل الـ CORS عشان فيرسل يقبل الطلبات من أي مكان وميجيبش أخطاء اتصال في المتصفح
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. الـ handler لازم يكون بيشاور على الـ app بعد تعريفه بالظبط
handler = app

# التعديل الأمني هنا: سحب المفتاح بأمان من الـ Environment Variables في Vercel
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)

# الواجهة البنفسجية الزجاجية مع ميزة فتح الكاميرا المباشرة
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
            padding: 30px 20px;
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
            font-size: 2.2rem;
            margin-bottom: 10px;
            display: inline-block;
        }
        .upload-label {
            cursor: pointer;
            display: block;
            font-size: 1.15rem;
            color: #e2e8f0;
            font-weight: 600;
        }
        .upload-label span {
            display: block;
            margin-top: 6px;
            font-size: 0.9rem;
            color: #74718a;
            font-weight: 400;
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
        
        /* تصميم نافذة الكاميرا المنبثقة */
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
    <div class="brand">NovaCore Studio</div>
    <h1>مساعد حل الواجبات</h1>
    <p class="subtitle">ارفع صورة المسألة أو التقطها بالكاميرا وسيحلها الذكاء الاصطناعي بالتفصيل</p>
    
    <div class="upload-section" onclick="document.getElementById('fileInput').click()">
        <span class="upload-icon">🔮</span>
        <label class="upload-label">
            اضغط هنا لرفع صورة السؤال
            <span id="fileNameDisplay">يدعم الامتدادات البصرية (PNG, JPG, JPEG)</span>
        </label>
        <input type="file" id="fileInput" accept="image/*" onchange="updateFileName(this)">
    </div>

    <!-- أزرار الاختيار الإضافية (كاميرا مباشرة) -->
    <div class="actions-grid">
        <button type="button" class="action-btn" onclick="openCameraModal()">
            📷 افتح الكاميرا للتصوير
        </button>
        <button type="button" class="action-btn" onclick="document.getElementById('fileInput').click()">
            📁 استعراض الملفات
        </button>
    </div>
    
    <button class="btn" id="solveBtn" onclick="uploadAndSolve()">ابدأ الحل الان ✨</button>
    
    <div class="loading" id="loadingArea">
        <div class="spinner"></div>
        <span>جاري فك رموز الصورة واستخراج الحل النموذجي...</span>
    </div>
    
    <div class="result-section" id="resultSection">
        <div class="result-title">✨ الحل المنسق والشرح:</div>
        <div class="result-box" id="resultBox"></div>
    </div>
</div>

<!-- نافذة الكاميرا الحية -->
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

    // فتح الكاميرا
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

    // غلق الكاميرا
    function closeCameraModal() {
        const modal = document.getElementById('cameraModal');
        modal.style.display = "none";
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
    }

    // التقاط الصورة من الفيديو وتحويلها لملف يقرأه الـ input
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
            
            // تحديث النص الظاهر
            updateFileName(document.getElementById('fileInput'));
            closeCameraModal();
        }, 'image/jpeg');
    }

    async function uploadAndSolve() {
        const fileInput = document.getElementById('fileInput');
        const solveBtn = document.getElementById('solveBtn');
        const loadingArea = document.getElementById('loadingArea');
        const resultSection = document.getElementById('resultSection');
        const resultBox = document.getElementById('resultBox');
        
        if(!fileInput.files || !fileInput.files[0]) {
            alert('برجاء إرفاق صورة السؤال أو تصويره بالكاميرا أولاً يا فنان!');
            return;
        }
        
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        
        solveBtn.disabled = true;
        loadingArea.style.display = "block";
        resultSection.style.display = "none";
        
        try {
            const response = await fetch('/solve', {
                method: 'POST',
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
            solveBtn.disabled.disable = false;
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
async def solve_homework(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="الملف المرفوع يجب أن يكون صورة.")
    
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        prompt = (
            "أنت معلم خبير ومساعد أكاديمي متميز. "
            "قم بتحليل الصورة المرفقة واستخراج السؤال أو المسألة منها بدقة، "
            "ثم قدم الحل الصحيح والنموذجي خطوة بخطوة مع الشرح المفصل باللغة العربية واللهجة المصرية الشعبية الاصطناعية . "
            "استخدم عناوين فرعية ونقاط واضحة وتنسيق Markdown غني (مثل استخدام النجوم للتأكيد) "
            "ليكون النص جذاباً وسهل القراءة والفهم."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt]
        )
        
        return {
            "status": "success",
            "solution": response.text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء معالجة الصورة: {str(e)}")
