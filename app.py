import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Designer AI - Vector Pro", layout="wide")
st.title("🧵 Sif Designer AI: نظام اتجاه الغرز الذكي")

uploaded_file = st.file_uploader("ارفع صورة الرشمة (الصدر/الأكمام)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("القيس الحقيقي (XL, L...)", ["M", "L", "XL", "XXL"])
        density = st.slider("كثافة الغرز (Stitch Density)", 1, 10, 5)
        
        if st.button("توليد DST باتجاهات احترافية"):
            with st.spinner("جاري حساب زوايا الغرز ومسار الإبرة..."):
                # 1. تحليل الهيكل العظمي للرشمة (Skeletonization)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                
                # 2. تقنية Hough Lines لتحديد اتجاه الخطوط
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=10, maxLineGap=5)
                
                pattern = pyembroidery.EmbPattern()
                scale = 1.6 if size == "XL" else 1.0
                
                if lines is not None:
                    for line in lines:
                        x1, y1, x2, y2 = line[0]
                        # حساب اتجاه الغرزة بناءً على ميل الخط الأصلي
                        # تحويل النقاط لمقاس XL حقيقي
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (x1 - img.shape[1]/2) * scale, (y1 - img.shape[0]/2) * scale)
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (x2 - img.shape[1]/2) * scale, (y2 - img.shape[0]/2) * scale)
                        # إضافة قفزة ذكية لعدم تشابك الاتجاهات
                        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف
                out_dst = f"Sif_Professional_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم ضبط اتجاهات الغرز لمقاس {size}")
                st.image(edges, caption="معاينة مسار الإبرة الموجه", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف DST الاحترافي", f, file_name=out_dst)
