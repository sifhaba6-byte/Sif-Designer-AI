import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Pro", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: نظام الرشمة الاحترافي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة الصدر أو الأكمام", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس (القيس)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد DST (خيوط المجبود فقط)"):
            with st.spinner("جاري استخراج المسارات..."):
                # 1. تحويل الصورة لرمادي وتنظيفها من الظلال
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # استخدام عتبة ذكية لعزل التطريز عن القماش
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
                
                # 2. استخراج الهيكل (Skeleton) - سر المهنة لعدم التكتل
                kernel = np.ones((3,3), np.uint8)
                skeleton = cv2.erode(thresh, kernel, iterations=1)
                edges = cv2.Canny(skeleton, 50, 150)
                
                # 3. تحويل المسارات لغرز (DST)
                pattern = pyembroidery.EmbPattern()
                scale = 1.8 if size == "XL" else 1.3
                
                # استخراج النقاط وترتيبها (Path Finding)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    if len(cnt) < 5: continue
                    for i, pt in enumerate(cnt):
                        x, y = pt[0]
                        # تحويل المقاس وتوسيط الرشمة في الطارة
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة (Jump) لضمان عدم وجود خيوط عرضية
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف
                out_dst = f"Sif_Final_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم! الرشمة الآن عبارة عن خيوط منظمة.")
                st.image(edges, caption="هذه هي الرشمة التي ستطرزها الماكينة (خيوط نقية)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
