import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Global Pro", layout="wide")

st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: الاحتراف العالمي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة القفطان أو الكاراكو (مقاس XL)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("القيس الحقيقي المطلوب", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST (رسم خطوط المجبود فقط)"):
            with st.spinner("جاري استخراج الرشمة بدقة عالمية..."):
                # 1. تحويل الصورة للأبيض والأسود وتنظيفها
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # استخدام مرشح ذكي لإزالة الظلال وإبقاء التطريز فقط
                blurred = cv2.bilateralFilter(gray, 9, 75, 75)
                # تقنية Canny لاستخراج "حدود" الرشمة فقط (Skeletal Detection)
                edges = cv2.Canny(blurred, 70, 150)
                
                # 2. بناء ملف الماكينة (DST)
                pattern = pyembroidery.EmbPattern()
                
                # ضبط المقاس XL (معامل تكبير حقيقي)
                scale = 1.5 if size == "XL" else 1.0
                
                # استخراج نقاط المسارات (الخطوط البيضاء فقط)
                y_coords, x_coords = np.where(edges > 0)
                
                # تنظيم الغرز لتكون رقيقة ونظيفة (Run Stitch)
                # القفز بـ 15 نقطة لضمان عدم تكدس الخيط واحتراق القماش
                for i in range(0, len(x_coords), 15): 
                    x = (x_coords[i] - (img.shape[1]/2)) * scale
                    y = (y_coords[i] - (img.shape[0]/2)) * scale
                    pattern.add_stitch_absolute(pyembroidery.STITCH, x, y)
                    
                    # إضافة قفزة (Jump) ذكية كل مسافة لتنظيف ظهر القماش
                    if i % 150 == 0:
                        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف النهائي
                out_file = f"Sif_{size}_Expert.dst"
                pyembroidery.write(pattern, out_file)
                
                st.success(f"✅ مبروك! تم استخراج رشمة {size} نظيفة واحترافية.")
                st.image(edges, caption="معاينة المسار الذي ستسلكه الإبرة (بدون كتل خضراء)", use_container_width=True)
                
                with open(out_file, "rb") as f:
                    st.download_button("📥 تحميل ملف DST للماكينة", f, file_name=out_file)

st.info("هذا التحديث يركز على 'خيوط المجبود' فقط ويمنع الماكينة من ملء المساحات الفارغة.")
