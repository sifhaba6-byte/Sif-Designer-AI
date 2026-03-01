import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Order Pro", layout="wide")
st.title("🧵 Sif Designer AI: نظام الغرز المنظمة")

uploaded_file = st.file_uploader("ارفع صورة الرشمة (صدر/أكمام)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس الحقيقي (XL, L...)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد DST منظم (غرز متسلسلة)"):
            with st.spinner("جاري ترتيب مسار الإبرة غرزة بغرزة..."):
                # 1. استخراج الحواف وتنظيفها
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 70, 150)
                
                # 2. البحث عن "الكنتور" (Contours) لتنظيم الحركة
                # هذه أهم خطوة: تجعل الماكينة تتبع 'الخيوط' وليس 'النقاط'
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                pattern = pyembroidery.EmbPattern()
                scale = 1.6 if size == "XL" else 1.0
                
                for cnt in contours:
                    # لكل جزء في الرشمة (وردة، غصن، عقاش)
                    for i, pt in enumerate(cnt):
                        x, y = pt[0]
                        # تحويل الإحداثيات للمركز والمقاس المطلوب
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة ذكية بعد نهاية كل جزء لضمان نظافة الطرز
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف
                out_dst = f"Sif_Ordered_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ مبروك! الغرز الآن منظمة ومسلسلة لمقاس {size}")
                st.image(edges, caption="معاينة المسار المنظم (Contours)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف DST المنظم", f, file_name=out_dst)
