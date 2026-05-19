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
            transform: scale(1.01);
        }
        #fileInput {
            display: none;
        }
        .upload-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
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
            margin-top: 8px;
            font-size: 0.9rem;
            color: #74718a;
            font-weight: 400;
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
    <p class="subtitle">ارفع صورة المسألة وسيحلها الذكاء الاصطناعي بالتفصيل</p>
    
    <div class="upload-section" onclick="document.getElementById('fileInput').click()">
        <span class="upload-icon">🔮</span>
        <label class="upload-label">
            اضغط هنا لرفع صورة السؤال
            <span id="fileNameDisplay">يدعم الامتدادات البصرية (PNG, JPG, JPEG)</span>
        </label>
        <input type="file" id="fileInput" accept="image/*" onchange="updateFileName(this)">
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

<script>
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

    async function uploadAndSolve() {
        const fileInput = document.getElementById('fileInput');
        const solveBtn = document.getElementById('solveBtn');
        const loadingArea = document.getElementById('loadingArea');
        const resultSection = document.getElementById('resultSection');
        const resultBox = document.getElementById('resultBox');
        
        if(!fileInput.files || !fileInput.files[0]) {
            alert('برجاء إرفاق صورة السؤال أولاً يا فنان!');
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
            alert("فشل الاتصال، تأكد من تشغيل السيرفر في الـ CMD");
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
async def solve_homework(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="الملف المرفوع يجب أن يكون صورة.")
    
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        prompt = (
            "أنت معلم خبير ومساعد أكاديمي متميز. "
            "قم بتحليل الصورة المرفقة واستخراج السؤال أو المسألة منها بدقة، "
            "ثم قدم الحل الصحيح والنموذجي خطوة بخطوة مع الشرح المفصل باللغة العربية واللهجة المصرية الشعبية الاصلية . "
            "استخدم عناوين فرعية ونقاط واضحة وتنسيق Markdown غني (مثل استخدام النجوم للتأكيد) "
            "ليكون النص جذاباً وسهل القراءة والفهم."
        )
        
        # تصليح اسم الموديل عشان يشتغل على الـ SDK الجديد بدون Error 404 الشهير
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
