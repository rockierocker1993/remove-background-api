from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from rembg import remove, new_session
from io import BytesIO
from PIL import Image, ImageFilter
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

app = FastAPI(title="Background Removal Service")

# Pakai model yang edge-nya lebih bagus
anime_session = new_session("isnet-anime")
general_session = new_session("isnet-general-use")

@app.post("/remove-bg-icon")
async def remove_bg(file: UploadFile = File(...)):
    try:
        input_bytes = await file.read()
        if not input_bytes:
            raise HTTPException(status_code=400, detail="Empty file")

        image_type = detect_image_type(input_bytes)
        session = general_session #if image_type == "anime" else general_session

        # 1️⃣ Remove background
        output_bytes = remove(input_bytes, session=session)

        img = Image.open(BytesIO(output_bytes)).convert("RGBA")
        r, g, b, a = img.split()

        # HARD EDGE for icon
        a = a.point(lambda p: 255 if p > 200 else 0)

        img = Image.merge("RGBA", (r, g, b, a))

        # Auto crop
        img = img.crop(img.getbbox())

        buf = BytesIO()
        img.save(buf, "PNG", optimize=True)
        final_bytes = buf.getvalue()

        return Response(
            content=final_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=\"result.png\"",
                "Content-Length": str(len(final_bytes))
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def detect_image_type(image_bytes: bytes) -> str:
    # Load image
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    img = np.array(image)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]

    # Compute metrics
    sat_mean = np.mean(saturation)
    sat_std = np.std(saturation)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.mean(edges > 0)

    # Heuristic rules
    if sat_mean > 80 and sat_std < 60 and edge_density < 0.15:
        return "anime"

    return "photo"


@app.get("/health")
def health():
    return {"status": "ok"}
