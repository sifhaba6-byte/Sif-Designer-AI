import streamlit as st
import cv2
import numpy as np
import pyembroidery

# واجهة احترافية تليق بمشروع استثماري
st.set_page_config(page_title="Sif Pro Embroidery Engine", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>💎 Sif Designer AI: النسخة الاستثمارية</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة الرشمة الأصلية", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="الصورة الأصلية", use_container_width=True)

    with col2:
        size = st.selectbox("اختر القيس الحقيقي", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد الرشمة (نظام الخيوط المتصلة)"):
            with st.spinner("جاري بناء المسارات الاحترافية..."):
                # 1. معالجة متقدمة لعزل الرسمة عن الخلفية
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # تنظيف الصورة من "الضجيج" الذي يسبب الكتل الخضراء
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                edges = cv2.Canny(blur, 50, 150)
                
                # 2. تحويل الحواف إلى مسارات إبرة متسلسلة
                pattern = pyembroidery.EmbPattern()
                # معامل XL لضمان مقاس الصدر الكامل
                scale = 2.5 if size == "XL" else 1.8 
                
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
                
                for cnt in contours:
                    if cv2.arcLength(cnt, True) < 25: continue # تجاهل الشوائب
                    
                    # تحسين انسيابية الخيط (Smoothing)
                    epsilon = 0.01 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    
                    for pt in approx:
                        x, y = pt[0]
                        # التوسيط الدقيق في الطارة (Hoop)
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # أمر القفز (Jump) لضمان نظافة التطريز من الخلف
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف بصيغة DST العالمية
                out_dst = f"Sif_Masterpiece_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success("✅ الرشمة جاهزة للماكينة: مسارات خيطية نقية!")
                # عرض المعاينة الشعاعية (يجب أن تظهر خطوطاً رقيقة)
                st.image(edges, caption="معاينة مسار الإبرة الحقيقي (بدون تكتل)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
