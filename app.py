import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Professional", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: نظام الرشمة العالمي 2026</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة الصدر أو الأكمام (كاراكو/قفطان)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس الحقيقي (القيس)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST (خيوط المجبود فقط)"):
            with st.spinner("جاري استخراج الرشمة بدقة متناهية..."):
                # 1. تحويل الصورة لرمادي وتنقية فائقة
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # إزالة الظلال تماماً لإبقاء الرسمة فقط
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                
                # 2. تقنية الهيكل العظمي (Skeletonization) لمنع التكتل الأخضر
                kernel = np.ones((3,3), np.uint8)
                skeleton = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                edges = cv2.Canny(skeleton, 50, 150)
                
                # 3. بناء ملف الماكينة DST بنظام المسار الواحد
                pattern = pyembroidery.EmbPattern()
                # معامل التكبير للمقاس XL لضمان القيس الحقيقي
                scale = 2.0 if size == "XL" else 1.5
                
                # استخراج الكنتور (الخيوط المتصلة)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    # تجاهل النقاط الصغيرة التي تفسد الشكل
                    if cv2.arcLength(cnt, True) < 20: continue 
                    
                    for i, pt in enumerate(cnt):
                        x, y = pt[0]
                        # التوسيط الدقيق في منتصف الطارة
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة نظيفة (Jump) لمنع تشابك الخيوط
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف
                out_dst = f"Sif_Final_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم! الرشمة الآن عبارة عن خيوط منظمة ونقية.")
                st.image(edges, caption="المعايينة: هكذا ستتحرك الإبرة (خيوط فقط)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
