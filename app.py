import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Professional V3", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: المصمم المحترف</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة الصدر أو الأكمام (مقاس XL)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("القيس الحقيقي للرشمة", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST (رسم يدوي رقمي)"):
            with st.spinner("جاري استخراج مسارات المجبود بدقة 2026..."):
                # 1. تحويل الصورة لمسارات دقيقة (Edges) لمنع التكتل الأخضر
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # تنظيف الصورة بمرشح متطور لإبراز خيوط التطريز فقط
                blurred = cv2.bilateralFilter(gray, 9, 75, 75)
                edges = cv2.Canny(blurred, 100, 200) # استخراج الهيكل فقط
                
                # 2. بناء ملف DST الاحترافي
                pattern = pyembroidery.EmbPattern()
                
                # ضبط المقاس XL (معامل تكبير حقيقي للماكينة)
                scale = 1.6 if size == "XL" else 1.0
                
                # استخراج إحداثيات النقاط البيضاء (الرشمة فقط)
                y_coords, x_coords = np.where(edges > 0)
                
                # تنظيم الغرز لتكون انسيابية ونظيفة (Run Stitches)
                # نترك مسافة 15 نقطة بين كل غرزة لمنع حرق القماش
                for i in range(0, len(x_coords), 15): 
                    x = (x_coords[i] - (img.shape[1]/2)) * scale
                    y = (y_coords[i] - (img.shape[0]/2)) * scale
                    pattern.add_stitch_absolute(pyembroidery.STITCH, x, y)
                    
                    # إضافة "قفزة" (Jump) كل 100 غرزة لتنظيف قفا القماش
                    if i % 100 == 0:
                        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف
                out_dst = f"Sif_{size}_Pro_Design.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم استخراج رشمة {size} بنجاح!")
                st.image(edges, caption="خريطة الإبرة (خطوط دقيقة تتبع المجبود)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
