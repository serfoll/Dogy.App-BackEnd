from fastapi import FastAPI, HTTPException
import requests
from dotenv import load_dotenv
import os

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
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "type": place_type,
        "key": api_key
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
