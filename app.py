import streamlit as st
import cv2
import numpy as np
import pyembroidery

# إعدادات الواجهة الاحترافية
st.set_page_config(page_title="Sif Designer Pro - Professional DST", layout="wide")
st.title("🧵 Sif Designer AI: محول الرشمات العالمي")

uploaded_file = st.file_uploader("ارفع صورة الرشمة (مثل الصدر والأكمام)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="الصورة الأصلية", use_container_width=True)

    with col2:
        size = st.selectbox("اختر المقاس الحقيقي للقطعة", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد تصميم DST احترافي"):
            with st.spinner("جاري استخراج مسارات الإبرة بدقة 2026..."):
                # 1. تحويل الصورة إلى مسارات خيطية (وليس كتل ملونة)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # تنظيف الصورة لإبراز المجبود فقط
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                # استخراج "الهيكل" العظمي للرشمة
                edges = cv2.Canny(blurred, 50, 150)
                
                # 2. إنشاء ملف الماكينة DST
                pattern = pyembroidery.EmbPattern()
                
                # ضبط المقاس الحقيقي (Scaling) للمقاس XL
                scale_factor = 1.5 if size == "XL" else 1.0
                
                # تحويل كل نقطة في المسار إلى غرزة حقيقية
                points = np.column_stack(np.where(edges > 0))
                
                # توزيع الغرز بتباعد احترافي لمنع تكتل الخيط
                for i in range(0, len(points), 10): 
                    x = (points[i][1] - (img.shape[1]/2)) * scale_factor
                    y = (points[i][0] - (img.shape[0]/2)) * scale_factor
                    pattern.add_stitch_absolute(pyembroidery.STITCH, x, y)
                    
                    # إضافة "قفزة" خيطية كل فترة لتنظيم العمل
                    if i % 100 == 0:
                        pattern.add_stitch_relative(pyembroidery.JUMP, 2, 2)

                # حفظ الملف النهائي
                file_dst = f"Sif_Designer_{size}.dst"
                pyembroidery.write(pattern, file_dst)
                
                st.success(f"✅ تم إنشاء ملف DST احترافي بمقاس {size}")
                st.image(edges, caption="معاينة مسار الماكينة (خطوط دقيقة)", use_container_width=True)
                
                with open(file_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=file_dst)
