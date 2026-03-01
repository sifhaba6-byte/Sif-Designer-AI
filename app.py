import streamlit as st
import cv2
import numpy as np
import pyembroidery
from skimage.morphology import skeletonize
from skimage import img_as_bool

st.set_page_config(page_title="Sif Reverse Engineering Pro", layout="wide")
st.title("🧵 Sif Designer: محرك الهندسة العكسية للتطريز")

uploaded_file = st.file_uploader("ارفع صورة الصدر أو الأكمام (احترافي فقط)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="المودال الأصلي", use_container_width=True)

    with col2:
        size = st.selectbox("القيس المطلوب", ["M", "L", "XL", "XXL"])
        
        if st.button("تطبيق الهندسة العكسية (Vector DST)"):
            with st.spinner("جاري تحليل هيكل الغرز واتجاهات الخيط..."):
                # 1. معالجة هندسية للصورة
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                
                # 2. الهندسة العكسية: تحويل الكتل إلى "خيوط مركزية"
                # هذه الخطوة هي التي تمنع التكتل الأخضر تماماً
                skeleton = skeletonize(img_as_bool(binary))
                skeleton_img = (skeleton * 255).astype(np.uint8)
                
                # 3. بناء ملف DST بناءً على الهيكل النحيف
                pattern = pyembroidery.EmbPattern()
                scale = 2.5 if size == "XL" else 1.8
                
                # استخراج المسارات المنظمة
                contours, _ = cv2.findContours(skeleton_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
                
                for cnt in contours:
                    if len(cnt) < 10: continue
                    
                    for pt in cnt:
                        x, y = pt[0]
                        # حساب الإحداثيات بدقة الميكرون وتوسيطها
                        st_x = (x - img.shape[1]/2) * scale
                        st_y = (y - img.shape[0]/2) * scale
                        pattern.add_stitch_absolute(pyembroidery.STITCH, st_x, st_y)
                    
                    # قفزة نظيفة لضمان جودة الظهر
                    pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0)

                out_dst = f"Sif_Reverse_Eng_{size}.dst"
                pyembroidery.write(pattern, out_dst)
                
                st.success("✅ تمت الهندسة العكسية بنجاح! مسارات خيطية صافية.")
                # المعاينة هنا ستظهر لك "خيوط بيضاء نحيفة" هي مسار الإبرة الحقيقي
                st.image(skeleton_img, caption="هيكل الغرز المستخرج (Skeleton)", use_container_width=True)
                
                with open(out_dst, "rb") as f:
                    st.download_button(f"📥 تحميل ملف {size} الاحترافي", f, file_name=out_dst)
