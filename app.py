import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Pro - Clean Design", layout="wide")
st.title("💎 محرك Sif الاحترافي: تطريز الرشمة فقط")

uploaded_file = st.file_uploader("ارفع الرسمة (لوغو أو صدر قفطان)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="الصورة الأصلية", use_container_width=True)

    with col2:
        width_cm = st.number_input("عرض الرشمة المطلوب (سم)", min_value=1.0, value=15.0)
        # الكثافة: 3 تعني شغل ثقيل ومحترف
        density = st.slider("ثقل الطرز (Density)", 1, 8, 3)

        if st.button("توليد ملف DST الصافي"):
            with st.spinner("جاري عزل الرشمة وهندسة الغرز..."):
                # 1. تحويل الصورة ومعالجتها لعزل الخلفية تماماً
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # استخدام عتبة ذكية (Otsu) لعزل الخلفية
                # هذا السطر هو الذي يضمن عدم لمس الخلفية
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                
                # تنظيف الشوائب الصغيرة (Noise)
                kernel = np.ones((3,3), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

                pattern = pyembroidery.EmbPattern()
                scale = (width_cm * 100) / img.shape[1]
                
                # 2. خوارزمية المسح الذكي داخل "الكنتور" فقط
                h, w = thresh.shape
                for y in range(0, h, density):
                    # البحث عن النقاط الملونة فقط في هذا السطر
                    line_points = np.where(thresh[y, :] > 0)[0]
                    
                    if len(line_points) > 0:
                        # تقسيم النقاط إلى مجموعات (إذا كانت الرشمة منفصلة)
                        # لضمان وضع قفزة (JUMP) بين الورود المنفصلة
                        for i in range(0, len(line_points), density):
                            x = line_points[i]
                            st_x = (x - w/2) * scale
                            st_y = (y - h/2) * scale
                            pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                            
                            # إذا كان هناك فراغ كبير بين نقطة وأخرى، نضع قفزة
                            if i < len(line_points) - 1:
                                if line_points[i+1] - x > density * 2:
                                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)
                        
                        # قفزة عند نهاية السطر
                        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # 3. حفظ الملف
                out_name = f"Sif_Pure_Design.dst"
                pyembroidery.write(pattern, out_name)
                
                st.success(f"✅ تم العزل بنجاح! الرشمة تحتوي على {len(pattern.stitches)} غرزة صافية.")
                # معاينة لما ستطرزه الماكينة (يجب أن ترى الرشمة بيضاء والخلفية سوداء)
                st.image(thresh, caption="خارطة التطريز (ما تراه الماكينة)", use_container_width=True)
                with open(out_name, "rb") as f:
                    st.download_button("📥 تحميل ملف DST الصافي", f, file_name=out_name)
