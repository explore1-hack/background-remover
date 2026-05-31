from fastapi import FastAPI , UploadFile , File ,HTTPException
from fastapi.responses import StreamingResponse
from rembg import remove
from PIL import Image
import io



app = FastAPI()

@app.get("/")
def health_check():
    return{"status":"ok"}


@app.post("/remove-background/")

async def remove_background(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
    
    try:
        input_image = await file.read()

        output_image = remove(input_image)
            
        return StreamingResponse(io.BytesIO(output_image), media_type="image/png", headers={"Content-Disposition": "attachment; filename=result.png"})
    except Exception as e:
           raise HTTPException(status_code=500, detail="something went wrong while processing the image.")
