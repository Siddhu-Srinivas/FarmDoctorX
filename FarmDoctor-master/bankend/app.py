from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from answer_generation import generate_answer
from history_routes import router as history_router
from history_db import save_conversation
from weather_advisory_routes import router as weather_router
from prediction_engine import PredictionEngine
import json
import os
import requests
from fastapi.responses import StreamingResponse

app = FastAPI(title="RAG Crop Disease Assistant API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include history routes
app.include_router(history_router)

# Include weather advisory routes
app.include_router(weather_router)

class QueryRequest(BaseModel):
    query: str
    solution_type: str = "Both"
    language: str = "English"

class PredictionRequest(BaseModel):
    cropType: str
    region: str
    soilType: str
    season: str
    temperature: float
    humidity: float
    rainfall: float

class TTSRequest(BaseModel):
    text: str
    language: str

@app.post("/predict")
async def predict_endpoint(prediction_request: PredictionRequest):
    """Generate agricultural predictions based on farm conditions"""
    try:
        engine = PredictionEngine()
        
        # Call prediction methods with the provided parameters
        yield_prediction = engine.predict_yield(
            crop=prediction_request.cropType,
            region=prediction_request.region,
            soil=prediction_request.soilType,
            season=prediction_request.season,
            temperature=prediction_request.temperature,
            humidity=prediction_request.humidity,
            rainfall=prediction_request.rainfall
        )
        
        pest_prediction = engine.predict_pest_risk(
            crop=prediction_request.cropType,
            temperature=prediction_request.temperature,
            humidity=prediction_request.humidity,
            season=prediction_request.season,
            rainfall=prediction_request.rainfall
        )
        
        disease_prediction = engine.predict_disease(
            crop=prediction_request.cropType,
            temperature=prediction_request.temperature,
            humidity=prediction_request.humidity,
            season=prediction_request.season,
            soil=prediction_request.soilType
        )
        
        water_prediction = engine.predict_water_requirement(
            crop=prediction_request.cropType,
            temperature=prediction_request.temperature,
            humidity=prediction_request.humidity,
            rainfall=prediction_request.rainfall,
            season=prediction_request.season
        )
        
        return {
            "cropType": prediction_request.cropType,
            "region": prediction_request.region,
            "season": prediction_request.season,
            "conditions": {
                "temperature": prediction_request.temperature,
                "humidity": prediction_request.humidity,
                "rainfall": prediction_request.rainfall
            },
            "predictions": {
                "yield": yield_prediction,
                "pest_risk": pest_prediction,
                "disease_risk": disease_prediction,
                "water_requirement": water_prediction
            }
        }
    except Exception as e:
        print(f"Error in predict endpoint: {e}")
        return {"error": f"Failed to generate predictions: {str(e)}"}

@app.post("/generate")
async def generate_endpoint(query_request: QueryRequest):
    """Generate answer for the given query and solution type"""
    try:
        if not query_request.query or not query_request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        try:
            # Safely get attributes from the request model
            requested_language = getattr(query_request, 'language', 'English')
            query = getattr(query_request, 'query', '')
            sol_type = getattr(query_request, 'solution_type', 'Both')
            
            answer_text, relevant_docs = generate_answer(
                query=query,
                solution_type=sol_type,
                use_history=True,
                language=requested_language
            )
        except RuntimeError as gen_err:
            # if the error is due to rate limits, return structured error
            err_msg = str(gen_err)
            if "rate limit" in err_msg.lower() or "429" in err_msg:
                return {"error": "Service temporarily unavailable due to model rate limits. Please try again later."}
            # non-rate-limit runtime errors should propagate to outer handler
            raise
        
        # Parse the structured response
        response_data = {
            "query": query,
            "raw_answer": answer_text,
            "solution_type": sol_type,
            "sources_count": len(relevant_docs),
            "language": requested_language
        }
        
        # Save to history database automatically
        try:
            conversation_id = save_conversation(
                question=query,
                answer=answer_text,
                solution_type=sol_type
            )
            response_data["history_id"] = conversation_id
        except Exception as history_error:
            # Log error but don't fail the request
            print(f"Warning: Failed to save to history: {history_error}")
        
        return response_data
    except HTTPException:
        # re-raise so FastAPI handles it (e.g. invalid input)
        raise
    except Exception as e:
        # any unexpected error -> return error payload instead of 500
        print(f"Error in generate endpoint: {e}")
        return {"error": f"Failed to generate answer: {str(e)}"}

@app.post("/api/tts")
async def text_to_speech_endpoint(req: TTSRequest):
    """Generate high-quality audio using ElevenLabs with Turbo v2.5 model for better language detection"""
    print(f"TTS Request Received: Language={req.language}, Text length={len(req.text)}")
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("TTS Error: API key missing")
        raise HTTPException(status_code=500, detail="ElevenLabs API key missing in .env")
    
    # Using 'Aria' (9BWtsYmDHSGjRUXHjx9R) - very strong multilingual capabilities
    voice_id = "9BWtsYmDHSGjRUXHjx9R" 
    
    if req.language == "English":
        voice_id = "EXAVITQu4vr4xnSDxMaL"

    # eleven_turbo_v2_5 is the latest model with much better language detection and quality
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    # Tuning for natural regional flow:
    # We use turbo_v2_5 for better performance and language accuracy
    data = {
        "text": req.text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.35,  # Lower stability = more natural/varied tone
            "similarity_boost": 0.85,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    try:
        print(f"Calling ElevenLabs for {req.language}...")
        response = requests.post(url, json=data, headers=headers, stream=True)
        
        if response.status_code != 200:
            error_msg = response.text
            print(f"ElevenLabs API Error: {response.status_code} - {error_msg}")
            raise HTTPException(status_code=response.status_code, detail=f"ElevenLabs Error: {error_msg}")
            
        print(f"TTS Success: Streaming audio for {req.language}")
        def iter_audio():
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk
                    
        return StreamingResponse(iter_audio(), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Critical Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "RAG Backend Server Running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
