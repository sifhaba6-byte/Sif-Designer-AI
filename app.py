import streamlit as st
import cv2
import numpy as np
import pyembroidery

# واجهة استثمارية احترافية
st.set_page_config(page_title="Sif Pro Embroidery Engine", layout="wide")
st.title("💎 Sif Designer: محرك الهندسة العكسية الاحترافي")

uploaded_file = st.file_uploader("ارفع الرشمة (Image)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        # ضبط المقاس بالـ CM لضمان دقة 100% في الماكينة
        width_cm = st.number_input("العرض الحقيقي (سنتيمتر)", value=25.0)
        # كثافة احترافية (0.4 ملم هي معيار المصانع)
        density = st.slider("كثافة الغرز (Density)", 0.2, 1.0, 0.4)
        
        if st.button("توليد الرشمة بنظام الساتان"):
            with st.spinner("جاري بناء آلاف الغرز الاحترافية..."):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                
                # استخراج المسارات الهندسية
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
                
                pattern = pyembroidery.EmbPattern()
                # حساب معامل التكبير بناءً على السنتيمتر (10 وحدات في ملف DST تساوي 1 ملم)
                scale = (width_cm * 100) / img.shape[1]
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 50: continue
                    
                    # تحويل كل مسار إلى غرز "ساتان" متداخلة لملء الفراغ
                    pts = cnt.reshape(-1, 2)
                    for i in range(0, len(pts)//2, 1):
                        p1, p2 = pts[i], pts[-1-i]
                        
                        # إنشاء غرز متقاربة جداً (High Density) ليعطي ملمس المجبود
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
                    
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                filename = f"Sif_Pro_{width_cm}cm.dst"
                pyembroidery.write(pattern, filename)
                
                st.success(f"✅ تم توليد {len(pattern.stitches)} غرزة بنجاح!")
                st.download_button("📥 تحميل ملف DST الاحترافي", open(filename, "rb"), file_name=filename)
