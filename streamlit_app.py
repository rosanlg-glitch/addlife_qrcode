import io
import os
import tempfile

import streamlit as st
from PIL import Image

from label_generator import generate_label

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOGO = os.path.join(HERE, "assets", "Logo.png")

st.set_page_config(page_title="QR Label Generator", layout="centered")
st.title("QR Label Generator")

col1, col2 = st.columns(2)
with col1:
    part_no = st.text_input("Part No", value="ADD-0001")
with col2:
    part_name = st.text_input("Part Name", value="Name of the Part")

if st.button("Generate Label", type="primary"):
    if not part_no.strip() or not part_name.strip():
        st.warning("Enter both Part No and Part Name.")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            logo_path = DEFAULT_LOGO if os.path.exists(DEFAULT_LOGO) else None
            out_path = os.path.join(tmp, f"{part_no.replace('/', '_')}.png")
            path, w, h = generate_label(part_no.strip(), part_name.strip(), logo_path, out_path)

            img = Image.open(path)
            st.image(img, caption=f"{w}x{h}px @ 300 DPI", use_container_width=True)

            buf = io.BytesIO()
            img.save(buf, format="PNG", dpi=(300, 300))
            st.download_button(
                "Download PNG",
                data=buf.getvalue(),
                file_name=f"{part_no}.png",
                mime="image/png",
            )
