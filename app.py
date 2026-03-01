import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Pro MDT Engine", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>💎 Sif Designer: محرك الـ MDT الاحترافي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع الرسمة الأصلية (لوغو أو صدر)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="التصميم الأصلي", use_container_width=True)

    with col2:
        # تحديد العرض بالسنتيمتر لضبط الـ MDT
        target_width_cm = st.number_input("عرض الرشمة المطلوب (سم)", min_value=1.0, max_value=50.0, value=15.0)
        # كثافة الغرز: 0.4 ملم هي المعيار العالمي للجودة
        stitch_spacing = st.slider("المسافة بين الغرز (ملم)", 0.1, 1.0, 0.4)
        
        if st.button("توليد MDT احترافي"):
            with st.spinner("جاري هندسة قائمة الغرز..."):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                
                # استخراج المسارات بدقة عالية
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                
                pattern = pyembroidery.EmbPattern()
                # تحويل البكسل إلى 0.1 ملم (وحدة DST) لضبط المقاس 100%
                scale = (target_width_cm * 100) / img.shape[1]
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 30: continue
                    
                    # تحويل الكنتور إلى "أزواج نقاط" لعمل غرز الساتان (Satin)
                    points = cnt.reshape(-1, 2)
                    n = len(points)
                    step = max(1, int(stitch_spacing * 10)) # التحكم في الكثافة
                    
                    for i in range(0, n // 2, step):
                        p1 = points[i]
                        p2 = points[n - 1 - i]
                        
                        # توليد غرز متقاطعة (MDT مزدوج) ليعطي سمك المجبود
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
                    
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                filename = f"Sif_Master_MDT.dst"
                pyembroidery.write(pattern, filename)
                
                st.success(f"✅ مبروك! تم إنشاء {len(pattern.stitches)} غرزة منظمة.")
                st.image(thresh, caption="مخطط الـ MDT الهندسي", use_container_width=True)
                
                with open(filename, "rb") as f:
                    st.download_button("📥 تحميل ملف DST الاحترافي", f, file_name=filename)
