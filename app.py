import streamlit as st
import cv2
import numpy as np
import pyembroidery

def generate_pro_dst(img, width_cm):
    # 1. تنظيف الصورة وتحويلها لمسارات هندسية
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    pattern = pyembroidery.EmbPattern()
    # تحويل المقاس لـ 0.1 ملم (وحدة الماكينة العالمية)
    scale = (width_cm * 100) / img.shape[1]
    
    for cnt in contours:
        if cv2.contourArea(cnt) < 50: continue
        
        # استخراج النقاط وعمل تعبئة "ساتان" احترافية
        pts = cnt.reshape(-1, 2)
        mid = len(pts) // 2
        for i in range(0, mid, 2): # خطوة الغرزة (0.4 ملم تقريباً)
            p1, p2 = pts[i], pts[-1-i]
            # إضافة الغرز المتقابلة (هذا هو سر النجاح)
            pattern.add_stitch_absolute(pyembroidery.STITCH, (p1[0]-img.shape[1]/2)*scale, (p1[1]-img.shape[0]/2)*scale)
            pattern.add_stitch_absolute(pyembroidery.STITCH, (p2[0]-img.shape[1]/2)*scale, (p2[1]-img.shape[0]/2)*scale)
        
        pattern.add_stitch_relative(pyembroidery.JUMP, 0, 0) # قفزة نظيفة
    return pattern

# تطبيق Streamlit
st.title("🧵 محرك Sif AI الاحترافي (MDT Pro)")
file = st.file_uploader("ارفع التصميم", type=['jpg', 'png'])
if file:
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
    size = st.number_input("العرض (سم)", value=15.0)
    if st.button("توليد DST بخوارزمية الساتان"):
        pat = generate_pro_dst(img, size)
        pyembroidery.write(pat, "sif_pro.dst")
        st.success(f"النتيجة: {len(pat.stitches)} غرزة! (هكذا نربح)")
        st.download_button("تحميل الملف الاحترافي", open("sif_pro.dst", "rb"), "sif_pro.dst")
