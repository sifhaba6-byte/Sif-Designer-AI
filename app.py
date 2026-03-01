import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Smooth Pro", layout="wide")
st.title("🧵 Sif Designer AI: نظام الرشمة الانسيابية")

uploaded_file = st.file_uploader("ارفع صورة المودال (الصدر/الأكمام)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس المطلوب (القيس الحقيقي)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد DST احترافي ومنظم"):
            with st.spinner("جاري تنعيم المسارات وترتيب الغرز..."):
                # 1. معالجة الصورة لاستخراج الخطوط الأساسية فقط
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # تقليل الضجيج (Noise) باش ما تخرجش الغرز مخربشة
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                edges = cv2.Canny(blurred, 50, 150)
                
                # 2. تحويل النقاط إلى "سلاسل متصلة" (Contours)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                pattern = pyembroidery.EmbPattern()
                scale = 1.8 if size == "XL" else 1.2 # تكبير حقيقي للمقاس الكبير
                
                for cnt in contours:
                    # تصفية الأجزاء الصغيرة جداً (النقاط العشوائية)
                    if cv2.contourArea(cnt) < 5: continue 
                    
                    # تنعيم الخط (Approximation) باش تجي الغرزة "دائرية" ومنظمة
                    epsilon = 0.01 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    
                    for i, pt in enumerate(approx):
                        x, y = pt[0]
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة نظيفة (Jump) بين أجزاء الرشمة
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف النهائي
                out_dst = f"Sif_Pro_{size}_Final.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم إنشاء الرشمة بنجاح! الغرز الآن تتبع الخطوط بدقة.")
                st.image(edges, caption="معاينة الهيكل المنظم للرشمة", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
