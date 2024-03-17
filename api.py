# api.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
import requests
from dotenv import load_dotenv
import os
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import nutrition_api
from dogy_companion import ask_dogy
import os
from helpers import encode_image
# Load environment variables from .env file
load_dotenv()

app = FastAPI()

@app.get("/")
async def my_first_get_api():
    return {"message": "First FastAPI example"}

@app.get("/nearby-places/")
async def get_nearby_places(latitude: float, longitude: float, radius: int = 500, place_type: str = 'restaurant'):
    # Use the API key from the environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not found")

    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    keyword = "dog-friendly"

    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "type": place_type,
        "key": api_key,
        "keyword": keyword
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            results = response.json()['results']
            nearby_places = [place['name'] for place in results[:5]] # Get the first 5 places
            return {"nearby_places": nearby_places}
        else:
            return HTTPException(status_code=400, detail="Error fetching data from Google Places API")
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.post("/get-nutrition/")
async def get_nutrition(files: list[UploadFile] = File(...), user_message: Optional[str] = None):
    image_paths = []
    image_contents = []
    for file in files:
        # Save temporary image file
        contents = await file.read()
        base64_image = encode_image(contents, file.content_type)  # Now passing MIME type to encode_image
        image_contents.append({
            "type": "image_url",
            "image_url": {"url": f"data:{file.content_type if file.content_type != 'image/heic' else 'image/jpeg'};base64,{base64_image}"}
        })
        file.file.close()


    if not image_contents:
        raise HTTPException(status_code=400, detail="No images provided")

    try:
        response = nutrition_api.get_nutritional_details(image_contents, user_message=user_message)
        # Clean up: remove temporary files after processing
        for path in image_paths:
            os.remove(path)
        return JSONResponse(content=response)
    except Exception as e:
        # Clean up: remove temporary files in case of an error
        for path in image_paths:
            os.remove(path)
        raise HTTPException(status_code=500, detail=str(e))

#ask dogy
class DogyRequest(BaseModel):
    message: str
    name: str

@app.post('/askdogy/')
async def ask_dogy_endpoint(request: DogyRequest):
    try:
        response = await ask_dogy(request.message, request.name)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
