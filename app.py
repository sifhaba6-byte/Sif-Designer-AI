import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Pro - Pure Design Only", layout="wide")
st.title("💎 محرك Sif الاحترافي: عزل الخلفية وتوليد الرشمة")

uploaded_file = st.file_uploader("ارفع الرسمة (لوغو أو صدر قفطان)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="الصورة الأصلية", use_container_width=True)

    with col2:
        width_cm = st.number_input("عرض الرشمة المطلوب (سم)", min_value=1.0, value=15.0)
        density = st.slider("كثافة التعبئة (كلما قل الرقم زاد الثقل)", 1, 10, 3)

        if st.button("توليد ملف DST (الرشمة فقط)"):
            with st.spinner("جاري عزل الخلفية وبناء الغرز..."):
                # 1. تحويل الصورة ومعالجتها لعزل الخلفية تماماً
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # استخدام عتبة ذكية (Otsu) لعزل الخلفية البيضاء آلياً
                _, thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)
                
                # تنظيف الشوائب الصغيرة التي قد تحسبها الماكينة غرزاً
                kernel = np.ones((3,3), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

                pattern = pyembroidery.EmbPattern()
                scale = (width_cm * 100) / img.shape[1]
                
                # 2. خوارزمية المسح الانتقائي (Selective Scanline)
                h, w = thresh.shape
                for y in range(0, h, density):
                    # نحدد فقط النقاط التي تنتمي للرشمة في هذا السطر
                    active_points = np.where(thresh[y, :] > 0)[0]
                    
                    if len(active_points) > 0:
                        in_segment = False
                        for i in range(len(active_points)):
                            x = active_points[i]
                            
                            st_x = (x - w/2) * scale
                            st_y = (y - h/2) * scale
                            pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                            
                            # إذا كانت المسافة بين النقطة الحالية والتالية كبيرة، نضع قفزة
                            if i < len(active_points) - 1:
                                if active_points[i+1] - x > density:
                                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)
                        
                        # قفزة عند نهاية كل سطر للانتقال للسطر التالي بنظافة
                        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # 3. حفظ الملف
                out_name = f"Sif_Pure_Design.dst"
                pyembroidery.write(pattern, out_name)
                
                st.success(f"✅ تم عزل الخلفية! الملف يحتوي على {len(pattern.stitches)} غرزة صافية.")
                st.image(thresh, caption="المساحة التي سيتم تطريزها فقط (اللون الأبيض)", use_container_width=True)
                with open(out_name, "rb") as f:
                    st.download_button("📥 تحميل ملف DST الصافي", f, file_name=out_name)
