import streamlit as st
import cv2
import numpy as np
import pyembroidery

st.set_page_config(page_title="Sif Engineering Pro 2026", layout="wide")
st.title("🧵 Sif Designer: المحرك الهندسي العكسي (Satin Edition)")

uploaded_file = st.file_uploader("ارفع اللوغو أو الرشمة", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="التصميم الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("المقاس (القيس)", ["Logo (5cm)", "Medium (15cm)", "XL (30cm)"])
        density = st.slider("كثافة الغرز (Stitch Density)", 1, 5, 2)
        
        if st.button("توليد تصميم احترافي (Satin Fill)"):
            with st.spinner("جاري هندسة الغرز المتوازية..."):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                
                # استخراج الحواف الخارجية والداخلية
                contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                pattern = pyembroidery.EmbPattern()
                scale_map = {"Logo (5cm)": 0.8, "Medium (15cm)": 2.0, "XL (30cm)": 4.0}
                scale = scale_map[size]
                
                for cnt in contours:
                    if cv2.contourArea(cnt) < 50: continue
                    
                    # تقنية الغرز المتعرجة (Satin) لملء المسار
                    # بدلاً من خط واحد، سنقوم بعمل غرز متوازية ذهاباً وإياباً
                    points = cnt.reshape(-1, 2)
                    for i in range(0, len(points) - density, density):
                        p1 = points[i]
                        p2 = points[(i + len(points)//2) % len(points)] # نقطة مقابلة
                        
                        # غرزة ذهاب
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
                        # غرزة إياب (تعطي سمك المجبود)
                        pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
                    
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                out_dst = f"Sif_Satin_Pro.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success(f"✅ تم! الملف الآن يحتوي على آلاف الغرز المنظمة.")
                st.image(thresh, caption="معاينة مسارات التعبئة الهندسية", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button("📥 تحميل ملف DST الاحترافي", f, file_name=out_dst)
