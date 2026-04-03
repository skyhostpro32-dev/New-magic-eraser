import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Image Dashboard", layout="wide")

st.title("✨ AI Image Dashboard")

tool = st.sidebar.selectbox(
    "Choose Tool",
    ["✨ Smart Object Remover"]
)

if tool == "✨ Smart Object Remover":

    st.subheader("✨ Click → Remove Object (Pro Blend)")

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

            // ✅ NEW: Directional color sampling (fix blur issue)
            let samples = [];

            const directions = [
                {dx: 0, dy: -radius * 1.5},
                {dx: 0, dy: radius * 1.5},
                {dx: -radius * 1.5, dy: 0},
                {dx: radius * 1.5, dy: 0}
            ];

            directions.forEach(d => {
                let sx = Math.floor(p.x + d.dx);
                let sy = Math.floor(p.y + d.dy);

                if (sx >= 0 && sy >= 0 && sx < canvas.width && sy < canvas.height) {
                    const i = (sy * canvas.width + sx) * 4;
                    samples.push([
                        data[i],
                        data[i + 1],
                        data[i + 2]
                    ]);
                }
            });

            if (samples.length === 0) return;

            let r = 0, g = 0, b = 0;

            samples.forEach(c => {
                r += c[0];
                g += c[1];
                b += c[2];
            });

            r /= samples.length;
            g /= samples.length;
            b /= samples.length;

            // ✅ Smooth blend fill
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

                            // ✅ slight sharpening (fix washed look)
                            data[i]     = Math.min(255, data[i] * 1.05);
                            data[i + 1] = Math.min(255, data[i + 1] * 1.05);
                            data[i + 2] = Math.min(255, data[i + 2] * 1.05);
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
