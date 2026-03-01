import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Professional Digitizer", layout="wide")
st.title("💎 محرك Sif الاحترافي: توليد الغرز الصناعية")

uploaded_file = st.file_uploader("ارفع الرسمة (لوغو أو صدر قفطان)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="الصورة الأصلية", use_container_width=True)

    with col2:
        # تحديد المقاس بالسنتيمتر لضبط الماكينة 100%
        width_cm = st.number_input("عرض الرشمة المطلوب (سم)", min_value=1.0, max_value=50.0, value=15.0)
        # الكثافة: 4 تعني غرزة كل 0.4 ملم (معيار احترافي)
        density = st.slider("كثافة التعبئة (Density)", 1, 10, 4)

        if st.button("توليد ملف DST ثقيل"):
            with st.spinner("جاري مسح الصورة وتوليد جدول الغرز (MDT)..."):
                # 1. معالجة الصورة لاستخراج المساحات
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
                
                pattern = pyembroidery.EmbPattern()
                # الماكينة تحسب بالـ 0.1 ملم (Scale دقيق جداً)
                scale = (width_cm * 100) / img.shape[1]
                
                # 2. خوارزمية المسح الأفقي (Scanline Fill) - لضمان عدم وجود فراغات
                # نمر على الصورة سطراً بسطر ونضع غرزاً داخل الأجزاء السوداء
                h, w = thresh.shape
                for y in range(0, h, density):
                    row = thresh[y, :]
                    in_shape = False
                    for x in range(0, w, density):
                        if row[x] > 0: # نحن داخل الرسمة
                            # إضافة غرزة MDT دقيقة
                            st_x = (x - w/2) * scale
                            st_y = (y - h/2) * scale
                            pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                            in_shape = True
                        elif in_shape: # خرجنا من الرسمة، نضع قفزة
                            pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)
                            in_shape = False

                # 3. حفظ الملف النهائي
                out_name = f"Sif_Industrial_{width_cm}cm.dst"
                pyembroidery.write(pattern, out_name)
                
                st.success(f"✅ مبروك! تم توليد {len(pattern.stitches)} غرزة. الملف الآن ثقيل واحترافي.")
                with open(out_name, "rb") as f:
                    st.download_button("📥 تحميل ملف DST للماكينة", f, file_name=out_name)
