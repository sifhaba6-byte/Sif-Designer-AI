import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Pro Investment V2", layout="wide")
st.title("💰 محرك توليد الرشمات الاحترافية (MDT Pro)")

uploaded_file = st.file_uploader("ارفع التصميم (اللوغو أو الصدر)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="التصميم الأصلي", use_container_width=True)

    with col2:
        # تحديد المقاس بالسنتيمتر بدقة 100%
        target_cm = st.number_input("العرض المطلوب للرشمة (سم)", value=20.0)
        # الكثافة: 0.3 ملم هي قمة الاحتراف للصدر الثقيل
        density = st.slider("كثافة الخيط (ملم) - المقترح 0.3", 0.1, 0.8, 0.3)
        
        if st.button("توليد ملف DST ثقيل (احترافي)"):
            with st.spinner("جاري بناء آلاف الغرز وهندسة المسار..."):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # تنظيف الصورة لعزل الرسمة فقط
                _, thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                
                pattern = pyembroidery.EmbPattern()
                # الماكينة تحسب بـ 0.1 ملم (وحدة دقيقة جداً)
                scale = (target_cm * 100) / img.shape[1]
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 30: continue
                    pts = cnt.reshape(-1, 2)
                    
                    # 1. إضافة غرزة التثبيت (Underlay)
                    for i in range(0, len(pts), 20):
                        p = pts[i]
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p[0]-img.shape[1]/2)*scale, (p[1]-img.shape[0]/2)*scale)
                    
                    # 2. هندسة الساتان (Satin Fill) - التعبئة الحقيقية
                    step = max(1, int(density * 10))
                    mid = len(pts) // 2
                    for i in range(0, mid, step):
                        p1, p2 = pts[i], pts[len(pts)-1-i]
                        # غرز متقاطعة تعطي لمعة وسمك
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
                    
                    pattern.add_
