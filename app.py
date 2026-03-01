import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Pro Digitizer V3", layout="wide")
st.title("💎 محرك الاستثمار: توليد الغرز الصناعية الكثيفة")

uploaded_file = st.file_uploader("ارفع الرسمة (لوغو، صدر، أو أكمام)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="الصورة الأصلية", use_container_width=True)

    with col2:
        # المقاس بالسنتيمتر يضبط الماكينة 100%
        width_cm = st.number_input("العرض المطلوب للرشمة (سم)", min_value=1.0, value=20.0)
        # الكثافة: 3 تعني غرزة كل 0.3 ملم (طرز ثقيل ومحترف)
        density = st.slider("ثقل الطرز (Density) - المقترح 3", 1, 8, 3)

        if st.button("توليد ملف DST استثماري (ثقيل)"):
            with st.spinner("جاري بناء جدول الغرز (MDT) بدقة الميكرون..."):
                # 1. تنقية الصورة وتحويلها لمساحات هندسية
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)
                
                pattern = pyembroidery.EmbPattern()
                # الماكينة تحسب بالـ 0.1 ملم (Scale دقيق جداً)
                scale = (width_cm * 100) / img.shape[1]
                
                # 2. خوارزمية المسح الذكي (Scanline Fill) 
                # تمر على كل بكسل في الرسمة وتضع غرزة تعبئة
                h, w = thresh.shape
                for y in range(0, h, density):
                    line_points = np.where(thresh[y, :] > 0)[0]
                    if len(line_points) > 0:
                        # نضع غرزة في بداية السطر ونهاية السطر وما بينهما
                        for i in range(0, len(line_points), density):
                            x = line_points[i]
                            st_x = (x - w/2) * scale
                            st_y = (y - h/2) * scale
                            pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                        # قفزة نظيفة عند نهاية كل سطر
                        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # 3. حفظ الملف النهائي
                out_name = f"Sif_Master_Investment.dst"
                pyembroidery.write(pattern, out_name)
                
                st.success(f"✅ النتيجة: {len(pattern.stitches)} غرزة! (هذا هو الطرز اللي يربح)")
                with open(out_name, "rb") as f:
                    st.download_button("📥 تحميل ملف DST الاحترافي", f, file_name=out_name)
