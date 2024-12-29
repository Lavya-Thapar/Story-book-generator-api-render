# -*- coding: utf-8 -*-
import sys
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from storygenerator import GeminiStoryGenerator

load_dotenv()

app = FastAPI(
    title="Story Generator API",
    description="API for generating children's stories and corresponding images.",
    version="1.0.0",
)

# Initialize your story generator instance
story_generator = GeminiStoryGenerator(
    api_key="GEMINI_API_KEY",  # Replace with your Gemini API key
    temperature=0.7,
    monster_api_key="MONSTER_API_KEY"

)

class StoryRequest(BaseModel):
    moral_value: str
    character_names: List[str]

class ImageRequest(BaseModel):
    scene_description: str
    characters_involved: List[str]
    character_descriptions: Dict[str, str]
    scene_name: str

@app.post("/generate-story", response_model=Dict[str, Dict[str, str]])
def generate_story(request: StoryRequest):
    try:
        story = story_generator.generate_story(
            moral_value=request.moral_value,
            character_names=request.character_names
        )
        return {
            "title": story["title"],
            "scenes": story["scenes"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-image", response_model=Dict[str, str])
def generate_image(request: ImageRequest):
    try:
        image_path = story_generator.generate_scene_image(
            scene_description=request.scene_description,
            character_descriptions=request.character_descriptions,
            characters_involved=request.characters_involved,
            output_dir="generated_scene_images",
            scene_name=request.scene_name
        )
        return {"image_path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "API is running successfully!"}

