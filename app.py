import streamlit as st
import cv2
import numpy as np
import pyembroidery

# إعدادات الواجهة الاحترافية (Sif Designer Pro 2026)
st.set_page_config(page_title="Sif Designer AI - Expert V3", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🧵 Sif Designer AI: نظام التطريز العالمي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع صورة القفطان أو الكاراكو (تحليل الصدر والأكمام)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("اختر المقاس الحقيقي (القيس)", ["M", "L", "XL", "XXL"])
        
        if st.button("توليد ملف DST احترافي (مسارات دقيقة)"):
            with st.spinner("جاري استخراج الرشمة وتنظيم الغرز..."):
                # 1. تنظيف الصورة وعزل خيوط المجبود فقط
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # تقليل الضجيج لمنع الغرز العشوائية
                clean = cv2.bilateralFilter(gray, 9, 75, 75)
                # استخراج المسارات (Edges)
                edges = cv2.Canny(clean, 50, 150)
                
                # 2. تحويل المسارات إلى سلاسل غرز (Contours)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
                
                pattern = pyembroidery.EmbPattern()
                # معامل التكبير للمقاس XL لضمان القيس الحقيقي
                scale = 1.8 if size == "XL" else 1.3
                
                for cnt in contours:
                    # تجاهل الشوائب الصغيرة جداً
                    if cv2.arcLength(cnt, True) < 15: continue 
                    
                    # تنعيم المسار ليكون انسيابياً (Smoothing)
                    epsilon = 0.01 * cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    
                    for i, pt in enumerate(approx):
                        x, y = pt[0]
                        # حساب الإحداثيات بالنسبة للمركز (توسيط الرشمة)
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # إضافة قفزة (Jump) ذكية بين أجزاء الرشمة لنظافة الظهر
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                # حفظ الملف النهائي بصيغة DST للماكينة
                out_dst = f"Sif_Expert_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم استخراج رشمة {size} بنظام المسارات المنظمة!")
                # عرض المعاينة (يجب أن تكون خطوطاً بيضاء نقية وليس كتل خضراء)
                st.image(edges, caption="معاينة مسار الإبرة (الرشمة الرقمية)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} للماكينة", f, file_name=out_dst)
