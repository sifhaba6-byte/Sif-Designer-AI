import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Global Pro", layout="wide")

st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: الاحتراف العالمي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة القفطان (مقاس XL)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("القيس الحقيقي", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد DST احترافي (مسارات فقط)"):
            # 1. تنظيف الصورة وعزل الحواف بدقة فائقة (Skeletal Detection)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # استخدام مرشح لتقليل الضجيج وإبراز خيوط المجبود
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 100, 200)
            
            # 2. تحويل المسارات إلى غرز ماكينة (DST)
            pattern = pyembroidery.EmbPattern()
            
            # ضبط المقاس XL (التكبير للمقاس الحقيقي)
            scale = 1.4 if size == "XL" else 1.0
            
            # استخراج إحداثيات النقاط (خيوط الرشمة فقط)
            y_coords, x_coords = np.where(edges > 0)
            
            # تنظيم المسار ليكون انسيابياً وليس كتلة
            for i in range(0, len(x_coords), 12): # قفزات ذكية لمنع التكدس
                x = x_coords[i] * scale
                y = y_coords[i] * scale
                pattern.add_stitch_absolute(pyembroidery.STITCH, x, y)
                # إضافة قفزة (Jump) كل مسافة لمنع تشابك الخيوط
                if i % 120 == 0:
                    pattern.add_stitch_relative(pyembroidery.JUMP, 5, 5)

            # الحفظ النهائي
            out_file = f"Sif_Pro_{size}.dst"
            pyembroidery.write(pattern, out_file)
            
            st.success(f"✅ تم استخراج المسارات الاحترافية لمقاس {size}")
            st.image(edges, caption="معاينة المسارات (هذا ما ستطرزه الماكينة)", use_container_width=True)
            
            with open(out_file, "rb") as f:
                st.download_button("📥 تحميل ملف DST الاحترافي", f, file_name=out_file)
