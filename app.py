import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif AI Super Engine", layout="wide")
st.title("🚀 Sif AI: محرك التوليد الصناعي (الجيل الخامس)")

uploaded_file = st.file_uploader("ارفع التصميم (JPG/PNG)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="التصميم الأصلي", use_container_width=True)

    with col2:
        width_cm = st.number_input("العرض المطلوب (سم)", value=15.0)
        # كثافة عالية جداً للنتائج الاحترافية
        is_high_quality = st.checkbox("جودة مصنعية (غرز مكثفة)", value=True)
        
        if st.button("توليد ملف DST احترافي"):
            with st.spinner("جاري بناء هندسة الغرز والطبقات..."):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                
                pattern = pyembroidery.EmbPattern()
                scale = (width_cm * 100) / img.shape[1]
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 30: continue
                    pts = cnt.reshape(-1, 2)
                    
                    # 1. إضافة طبقة التثبيت (Underlay) - سر الاحتراف
                    for i in range(0, len(pts), 10): 
                        p = pts[i]
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p[0]-img.shape[1]/2)*scale, (p[1]-img.shape[0]/2)*scale)
                    
                    # 2. إضافة طبقة الساتان (Satin Fill) بكثافة عالية
                    step = 2 if is_high_quality else 5
                    mid = len(pts) // 2
                    for i in range(0, mid, step):
                        p1, p2 = pts[i], pts[len(pts)-1-i]
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
                    
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                out_file = "Sif_Super_Pro.dst"
                pyembroidery.write(pattern, out_file)
                
                st.success(f"النتيجة خارقة: تم توليد {len(pattern.stitches)} غرزة!")
                with open(out_file, "rb") as f:
                    st.download_button("📥 تحميل الملف الجاهز للماكينة", f, file_name=out_file)
