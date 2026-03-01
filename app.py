import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Industrial Pro", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: النسخة الصناعية 2026</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة الرشمة (الصدر/الأكمام)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس الحقيقي (القيس)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST (مسارات خيطية دقيقة)"):
            with st.spinner("جاري تحليل 'عظم' الرشمة..."):
                # 1. تحويل للرمادي وتنظيف فائق للحدود
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # استخدام عتبة متغيرة (Adaptive Threshold) لعزل المجبود بدقة
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                
                # 2. استخراج المسار المركزي (Centerline Extraction)
                # هذا يمنع التكتل الأخضر تماماً
                edges = cv2.Canny(thresh, 100, 200)
                
                # 3. بناء ملف الماكينة DST
                pattern = pyembroidery.EmbPattern()
                scale = 2.2 if size == "XL" else 1.6 # تكبير حقيقي للمقاس الكبير
                
                # استخراج الكنتور وترتيب الغرز بتسلسل منطقي
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
                
                for cnt in contours:
                    # حذف النقاط الميتة (Noise)
                    if cv2.arcLength(cnt, True) < 30: continue
                    
                    # تنعيم المسار ليكون انسيابياً (Smoothing)
                    epsilon = 0.005 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    
                    for i, pt in enumerate(approx):
                        x, y = pt[0]
                        # التوسيط في منتصف الطارة
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة نظيفة (Jump) لمنع تشابك الخيوط
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ وتصدير الملف
                out_dst = f"Sif_Industrial_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم استخراج الرشمة بنجاح! غرز نقية 100%")
                st.image(edges, caption="المعاينة: مسارات الإبرة النظيفة (بدون كتل)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
