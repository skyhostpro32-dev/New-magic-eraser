import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Image Dashboard", layout="wide")

st.title("✨ AI Image Dashboard")

tool = st.sidebar.selectbox(
    "Choose Tool",
    ["✨ Smart Object Remover"]
)

if tool == "✨ Smart Object Remover":

    st.subheader("✨ Click → Remove Object (Smooth Blend)")

    components.html("""
    <html>
    <body style="text-align:center; font-family:Arial;">

    <h3>Upload → Click Object → Remove</h3>

    <input type="file" id="upload"><br><br>

    Brush Size:
    <input type="range" id="brush" min="10" max="80" value="30"><br><br>

    <button id="apply">Apply Remove</button>
    <br><br>

    <canvas id="c" style="border:1px solid #ccc;"></canvas>

    <script>
    const upload = document.getElementById("upload");
    const canvas = document.getElementById("c");
    const ctx = canvas.getContext("2d");
    const apply = document.getElementById("apply");

    let img = new Image();
    let pts = [];

    upload.onchange = e => {
        img.src = URL.createObjectURL(e.target.files[0]);
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
        }
    }

    canvas.onclick = e => {
        let r = canvas.getBoundingClientRect();
        let x = (e.clientX - r.left) * (canvas.width / r.width);
        let y = (e.clientY - r.top) * (canvas.height / r.height);
        let size = parseInt(document.getElementById("brush").value);

        pts.push({x, y, size});

        ctx.fillStyle = "rgba(255,0,0,0.3)";
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
    }

    apply.onclick = () => {
        ctx.drawImage(img, 0, 0);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        pts.forEach(p => {
            const radius = p.size;

            // ✅ Step 1: Get surrounding average color
            let r = 0, g = 0, b = 0, count = 0;

            for (let y = -radius * 2; y <= radius * 2; y++) {
                for (let x = -radius * 2; x <= radius * 2; x++) {

                    const dist = Math.sqrt(x*x + y*y);

                    if (dist > radius && dist < radius * 2.5) {
                        const sx = Math.floor(p.x + x);
                        const sy = Math.floor(p.y + y);

                        if (sx >= 0 && sy >= 0 && sx < canvas.width && sy < canvas.height) {
                            const i = (sy * canvas.width + sx) * 4;
                            r += data[i];
                            g += data[i + 1];
                            b += data[i + 2];
                            count++;
                        }
                    }
                }
            }

            if (count === 0) return;

            r = r / count;
            g = g / count;
            b = b / count;

            // ✅ Step 2: Smooth blended fill
            for (let y = -radius; y <= radius; y++) {
                for (let x = -radius; x <= radius; x++) {

                    const dist = Math.sqrt(x*x + y*y);

                    if (dist <= radius) {
                        const sx = Math.floor(p.x + x);
                        const sy = Math.floor(p.y + y);

                        if (sx >= 0 && sy >= 0 && sx < canvas.width && sy < canvas.height) {
                            const i = (sy * canvas.width + sx) * 4;

                            let alpha = 1 - (dist / radius);
                            alpha = Math.pow(alpha, 1.5);

                            data[i]     = data[i]     * (1 - alpha) + r * alpha;
                            data[i + 1] = data[i + 1] * (1 - alpha) + g * alpha;
                            data[i + 2] = data[i + 2] * (1 - alpha) + b * alpha;

                            // tiny noise
                            data[i]     += Math.random() * 2;
                            data[i + 1] += Math.random() * 2;
                            data[i + 2] += Math.random() * 2;
                        }
                    }
                }
            }
        });

        ctx.putImageData(imageData, 0, 0);
    }
    </script>

    </body>
    </html>
    """, height=720)
