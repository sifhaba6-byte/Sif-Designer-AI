import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Ultra Pro", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: النسخة الاحترافية العالمية</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة الصدر أو الأكمام بدقة عالية", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس الحقيقي (القيس)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST بنظام المسارات المنظمة"):
            with st.spinner("جاري استخراج الرشمة بنظام Vector..."):
                # 1. تحويل الصورة للأبيض والأسود مع تنظيف فائق
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # إزالة التشويش (Denoising)
                clean = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
                # استخراج الحواف الحادة فقط (Edges)
                edges = cv2.Canny(clean, 50, 150)
                
                # 2. تحويل الحواف إلى "سلاسل" (Contours) - هذه سر المهنة
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
                
                pattern = pyembroidery.EmbPattern()
                scale = 1.7 if size == "XL" else 1.2
                
                for cnt in contours:
                    # تجاهل النقاط الصغيرة التي تفسد الشكل
                    if cv2.arcLength(cnt, True) < 20: continue 
                    
                    # تنعيم الخط (Path Smoothing) ليكون انسيابياً كالحرير
                    epsilon = 0.005 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    
                    for i, pt in enumerate(approx):
                        x, y = pt[0]
                        # حساب الإحداثيات بالنسبة للمركز لضمان توازن الرشمة في الطارة
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة نظيفة (Jump) لمنع تشابك الخيوط خلف القماش
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف النهائي
                out_dst = f"Sif_Final_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ مبروك! الرشمة الآن منظمة 100% لمقاس {size}")
                st.image(edges, caption="معاينة مسار الإبرة (خيوط نقية)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
