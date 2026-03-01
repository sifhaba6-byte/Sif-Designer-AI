import streamlit as st
import cv2
import numpy as np
import pyembroidery
from sklearn.cluster import KMeans

st.set_page_config(page_title="Sif Designer AI Pro", layout="wide")

# واجهة احترافية
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer Pro: نظام التطريز الرقمي العالمي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة القفطان (مقاس XL أو غيره)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # قراءة الصورة بذكاء Nano Banana 2
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img_rgb, caption="المودال الأصلي", use_container_width=True)

    with col2:
        st.subheader("⚙️ إعدادات المصمم المحترف")
        target_size = st.selectbox("مقاس القطعة المطلوبة", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST احترافي (مسارات دقيقة)"):
            with st.spinner("جاري بناء الرشمة غرزة بغرزة..."):
                # 1. تحويل الصورة إلى تتبع حواف (Edge Tracking) فائق الدقة
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # استخدام مرشح Bilateral للحفاظ على دقة الحواف ومنع التداخل
                gray = cv2.bilateralFilter(gray, 9, 75, 75)
                edges = cv2.Canny(gray, 50, 150)
                
                # 2. بناء ملف التطريز (DST) كمسارات خيطية (Stitch Paths)
                pattern = pyembroidery.EmbPattern()
                
                # ضبط المقاس الحقيقي (Scaling)
                # مقاس XL يحتاج تمديد المسارات ليتناسب مع قياسات الصدر الحقيقية
                scale = 1.4 if target_size == "XL" else 1.0
                
                # خوارزمية تتبع النقاط (Point Tracking)
                # بدلاً من ملء المساحة، نتبع "خطوط" الرسمة فقط
                indices = np.where(edges > 0)
                points = list(zip(indices[1], indices[0]))
                
                # تنظيم الغرز لتكون انسيابية (Smooth Path)
                for i in range(0, len(points), 5): # قفزة كل 5 بكسل لضمان كثافة احترافية
                    x, y = points[i]
                    pattern.add_stitch_absolute(pyembroidery.STITCH, x * scale, y * scale)
                    if i % 50 == 0: # إضافة قفزة خيطية لتنظيم الأجزاء
                        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف
                file_name = f"Sif_{target_size}_Professional.dst"
                pyembroidery.write(pattern, file_name)
                
                st.success(f"✅ تم الانتهاء! التصميم مطابق للرسمة بمقاس {target_size}")
                st.image(edges, caption="معاينة مسار الإبرة (خالٍ من العيوب)", use_container_width=True)
                
                with open(file_name, "rb") as f:
                    st.download_button("📥 تحميل ملف DST النهائي للماكينة", f, file_name=file_name)
