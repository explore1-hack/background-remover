from fastapi import FastAPI , UploadFile , File ,HTTPException,Request
from fastapi.responses import StreamingResponse
from rembg import remove
from PIL import Image
import io
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi .errors import RateLimitExceeded
import os
from fastapi.security import APIKeyHeader



from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="x-api-key")  # this creates the lock button

def verify_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key.")


API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")


app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

@app.get("/")
def health_check():
    return{"status":"ok"}


@app.post("/remove-background/")
@limiter.limit("5/minute")

async def remove_background(request:Request ,file: UploadFile = File(...)):
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key.")

          
    if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
    
    try:
        input_image = await file.read()

        output_image = remove(input_image)
            
        return StreamingResponse(io.BytesIO(output_image), media_type="image/png", headers={"Content-Disposition": "attachment; filename=result.png"})
    except Exception as e:
           raise HTTPException(status_code=500, detail="something went wrong while processing the image.")

