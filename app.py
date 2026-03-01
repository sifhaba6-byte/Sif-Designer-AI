import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Industrial Investment", layout="wide")
st.title("💰 محرك الاستثمار الصناعي للتطريز")

uploaded_file = st.file_uploader("ارفع اللوغو أو الرشمة (نريد نتيجة 10/10)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="التصميم الأصلي", use_container_width=True)

    with col2:
        # هنا نضبط المقاس بالتدقيق
        width_cm = st.number_input("عرض الرشمة في الماكينة (سم)", value=20.0)
        # الكثافة المصنعية
        density_val = st.select_slider("جودة الطرز", options=["عادية", "احترافية", "ممتازة (ثقيلة)"], value="احترافية")
        
        density_map = {"عادية": 6, "احترافية": 3, "ممتازة (ثقيلة)": 2}
        step = density_map[density_val]

        if st.button("توليد ملف DST استثماري"):
            with st.spinner("جاري بناء الـ MDT وبرمجة الغرز..."):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                
                pattern = pyembroidery.EmbPattern()
                # الماكينة تحسب بـ 0.1 ملم، لذا نضرب في 100
                scale = (width_cm * 100) / img.shape[1]
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 40: continue
                    pts = cnt.reshape(-1, 2)
                    
                    # 1. طبقة التثبيت (Underlay) - باش القماش ما يتكمشش
                    for i in range(0, len(pts), 15):
                        p = pts[i]
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p[0]-img.shape[1]/2)*scale, (p[1]-img.shape[0]/2)*scale)
                    
                    # 2. طبقة الساتان (Satin) - باش تجي الرشمة معمرة ومنظمة
                    mid = len(pts) // 2
                    for i in range(0, mid, step):
                        p1, p2 = pts[i], pts[len(pts)-1-i]
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
                    
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                filename = f"Investment_Pro_{width_cm}cm.dst"
                pyembroidery.write(pattern, filename)
                
                st.success(f"✅ مبروك! الملف فيه {len(pattern.stitches)} غرزة. هذا هو الشغل اللي يربح.")
                with open(filename, "rb") as f:
                    st.download_button("📥 تحميل الملف الجاهز للربح", f, file_name=filename)
