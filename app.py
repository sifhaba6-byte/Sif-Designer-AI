import streamlit as st
import cv2
import numpy as np
import pyembroidery
from skimage import morphology

st.set_page_config(page_title="Sif Logo Pro - Vector Engine", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>💎 Sif Designer: محرك الهندسة العكسية للوغو والرشمة</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع اللوغو أو الرشمة (بدقة عالية)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="التصميم الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس الحقيقي (القيس بالـ سم)", ["Logo (5cm)", "Medium (15cm)", "XL (30cm)"])
        
        if st.button("تطبيق الهندسة العكسية (Vectorize)"):
            with st.spinner("جاري استخراج مسارات الإبرة الاحترافية..."):
                # 1. تحويل للرمادي وتنقية فائقة للحواف
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # استخدام عتبة ذكية لعزل اللوغو تماماً عن الخلفية
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                
                # 2. تنحيف الخطوط (Skeletonization) للحصول على مسار واحد نقي
                skeleton = morphology.skeletonize(thresh > 0)
                skeleton_img = (skeleton * 255).astype(np.uint8)
                
                # 3. بناء ملف DST بنظام "الغرزة المتصلة" (Running Stitch)
                pattern = pyembroidery.EmbPattern()
                # تحديد معامل التكبير بناءً على المقاس
                scale_map = {"Logo (5cm)": 0.5, "Medium (15cm)": 1.5, "XL (30cm)": 3.0}
                scale = scale_map[size]
                
                contours, _ = cv2.findContours(skeleton_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
                
                for cnt in contours:
                    if cv2.arcLength(cnt, True) < 10: continue # حذف الشوائب
                    
                    for i, pt in enumerate(cnt):
                        x, y = pt[0]
                        # التوسيط الدقيق (Centering) لضمان عدم خروج الرشمة عن الطارة
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة نظيفة (Jump) بين أجزاء اللوغو لضمان جودة المصنع
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # تصدير ملف DST
                out_dst = f"Sif_Vector_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تمت الهندسة العكسية! الرشمة الآن منظمة 100%")
                # المعاينة تظهر "الهيكل العظمي" للوغو (خيوط فقط)
                st.image(skeleton_img, caption="معاينة مسار الإبرة (بدون تكتل أخضر)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
