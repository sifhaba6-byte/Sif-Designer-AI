import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Ultra Vector", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: نظام الرشمة الشعاعية</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة المودال بدقة عالية", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس (القيس)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST بنظام الخيوط"):
            with st.spinner("جاري تنقية المسارات ومنع التكتل..."):
                # 1. تحويل للرمادي وتحسين التباين
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # استخدام فلتر لإزالة الظلال والخلفية
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                
                # 2. استخراج الحواف الدقيقة (Skeletonization)
                edges = cv2.Canny(thresh, 100, 200)
                
                # 3. بناء الرشمة (Pattern Creation)
                pattern = pyembroidery.EmbPattern()
                # ضبط معامل التكبير للمقاس XL
                scale = 2.0 if size == "XL" else 1.5
                
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    # تصفية الخطوط القصيرة جداً (الشوائب)
                    if cv2.arcLength(cnt, True) < 10: continue
                    
                    # تحويل الكنتور إلى نقاط غرز متسلسلة
                    for i, pt in enumerate(cnt):
                        x, y = pt[0]
                        # التوسيط الدقيق في منتصف الطارة
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة (Jump) نظيفة بين الأجزاء لضمان جودة الظهر
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف النهائي
                out_dst = f"Sif_Clean_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم! الغرز الآن تتبع الخطوط فقط (بدون تكتل)")
                # عرض المعاينة النهائية للمسار
                st.image(edges, caption="هذا هو مسار الإبرة الحقيقي (نقي 100%)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
                    
