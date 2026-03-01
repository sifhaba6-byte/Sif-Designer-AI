import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Royal Embroidery", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>👑 Sif Designer: المحرك الاحترافي الشامل</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع الرشمة أو اللوغو (جودة عالية)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="التصميم الأصلي", use_container_width=True)

    with col2:
        # تحديد المقاس الحقيقي بالسنتيمتر
        target_cm = st.number_input("العرض المطلوب للرشمة (بالسنتيمتر)", min_value=5, max_value=50, value=25)
        # تحديد الكثافة (كلما قل الرقم زادت الكثافة)
        density_mm = st.slider("المسافة بين الغرز (ملم) - المقترح 0.4", 0.1, 1.0, 0.4)
        
        if st.button("توليد الرشمة الاحترافية"):
            with st.spinner("جاري الهندسة العكسية للمسارات..."):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                
                # تنظيف الحواف (Dilation/Erosion) لتجنب الغرز العشوائية
                kernel = np.ones((3,3), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
                
                pattern = pyembroidery.EmbPattern()
                # حساب الـ Scale الحقيقي (الماكينة تقيس بالـ 0.1 ملم)
                pixel_width = img.shape[1]
                scale = (target_cm * 100) / pixel_width
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 40: continue
                    
                    # تحويل الكنتور لمصفوفة نقاط
                    points = cnt.reshape(-1, 2)
                    num_points = len(points)
                    
                    # تقنية Satin Stitch: الربط بين النقاط المتقابلة
                    mid = num_points // 2
                    for i in range(0, mid, int(density_mm * 5)):
                        p1 = points[i]
                        p2 = points[num_points - 1 - i]
                        
                        # غرزة zig
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
                        # غرزة zag
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
                    
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                out_filename = f"Sif_Royal_{target_cm}cm.dst"
                pyembroidery.write(pattern, out_filename)
                
                st.success(f"✅ مبروك! الرشمة جاهزة بمقاس {target_cm} سم وبكثافة احترافية.")
                st.image(thresh, caption="خارطة الغرز (Satin Path)", use_container_width=True)
                
                with open(out_filename, "rb") as f:
                    st.download_button(f"📥 تحميل ملف DST (جاهز للماكينة)", f, file_name=out_filename)
