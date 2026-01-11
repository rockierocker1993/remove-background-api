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
# anime_session = new_session("isnet-anime")
# general_session = new_session("isnet-general-use")

@app.post("/remove-bg/{model_name}")
async def remove_bg(model_name: str, file: UploadFile = File(...)):
    try:
        input_bytes = await file.read()
        if not input_bytes:
            raise HTTPException(status_code=400, detail="Empty file")

        session = new_session(model_name)

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
    
@app.get("/health")
def health():
    return {"status": "ok"}
