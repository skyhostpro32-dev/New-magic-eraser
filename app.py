import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="AI Object Remover PRO", layout="wide")

st.title("🔥 AI Object Remover PRO")

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    st.subheader("🖌️ Draw over object to remove")

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",
        stroke_width=20,
        stroke_color="white",
        background_image=image,
        height=image.height,
        width=image.width,
        drawing_mode="freedraw",
        key="canvas",
    )

    if st.button("🚀 Remove Object"):

        if canvas_result.image_data is not None:

            mask = canvas_result.image_data[:, :, 3]  # alpha channel
            mask = (mask > 0).astype("uint8") * 255

            # 🔥 AI Inpainting (OpenCV fallback)
            result = cv2.inpaint(img_np, mask, 3, cv2.INPAINT_TELEA)

            col1, col2 = st.columns(2)

            with col1:
                st.image(image, caption="Original")

            with col2:
                st.image(result, caption="Removed Object")
