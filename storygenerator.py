# story_generator_module.py

from typing import Dict, List
import google.generativeai as genai
from monsterapi import client

class GeminiStoryGenerator:
    def __init__(
        self,
        api_key: str,
        monster_api_key: str,
        temperature: float = 0.7
    ):
        """
        Initialize the story generator with Google's Gemini API and Monster API.

        Args:
            api_key: Google API key for Gemini
            monster_api_key: API key for Monster API
            temperature: Generation temperature (0.0 - 1.0)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.monster_client = client(monster_api_key)
        self.monster_model = 'txt2img'
        self.temperature = temperature

    def _create_story_prompt(self, moral_value: str, character_names: List[str]) -> str:
        """Create a detailed prompt for story generation."""
        prompt = f"""You are a children's story writer. Create a short story for children aged 0-5 years that teaches the moral value of {moral_value}.

Requirements:

- Story should be 150-200 words
- Use simple, clear language suitable for young children
- Include character names: {', '.join(character_names)}
- Create 2-3 scenes that can be clearly visualized
- Include some dialogue but keep it simple
- Add repetitive elements that young children enjoy
- End with a clear but gentle moral lesson
- Avoid any scary or negative elements
- Use descriptive language that can guide illustration

Format the story as follows:
Title: [Story Title]

[Story text with clear paragraph breaks between scenes]

Each scene should be marked with [Scene X] at the start."""
        return prompt

    def _generate_text(self, prompt: str) -> str:
        """Generate text using Gemini."""
        response = self.model.generate_content(prompt, temperature=self.temperature)
        return response.text

    def _validate_content(self, story: str) -> bool:
        """Validate that the story meets child-friendly criteria."""
        if len(story.split()) > 500:  # Approximate word count
            return False
        if "[Scene" not in story:
            return False
        return True

    def generate_story(
        self,
        moral_value: str,
        character_names: List[str],
        max_attempts: int = 3
    ) -> Dict[str, str]:
        """
        Generate a children's story based on the given moral value.

        Args:
            moral_value: The moral lesson to be conveyed
            character_names: List of character names to include
            max_attempts: Maximum number of generation attempts

        Returns:
            Dictionary containing the story title and text, split into scenes
        """
        for attempt in range(max_attempts):
            try:
                prompt = self._create_story_prompt(moral_value, character_names)
                story = self._generate_text(prompt)
                if self._validate_content(story):
                    lines = story.split('\n')
                    title = lines[0].replace('Title:', '').strip()
                    scenes = {}
                    current_scene = None
                    current_text = []

                    for line in lines[1:]:
                        if line.strip().startswith('[Scene'):
                            if current_scene:
                                scenes[current_scene] = '\n'.join(current_text).strip()
                            current_scene = line.strip()
                            current_text = []
                        elif line.strip() and current_scene:
                            current_text.append(line)

                    if current_scene and current_text:
                        scenes[current_scene] = '\n'.join(current_text).strip()

                    return {"title": title, "scenes": scenes, "full_text": story}
            except Exception:
                continue
        raise Exception("Failed to generate a valid story")

    def generate_scene_image(
        self,
        scene_description: str,
        character_descriptions: dict,
        characters_involved: list,
        output_dir: str,
        scene_name: str
    ) -> str:
        """Generate an image for a given scene using the Monster API."""
        full_prompt = ""
        for character_name in characters_involved:
            full_prompt += f"{character_name}: {character_descriptions[character_name]}\n"
        full_prompt += f"Scene: {scene_description}."

        input_data = {
            'prompt': full_prompt,
            'negprompt': 'deformed, bad anatomy, disfigured, poorly drawn face',
            'samples': 1,
            'steps': 50,
            'aspect_ratio': 'square',
            'guidance_scale': 7.5,
            'seed': 2414,
        }
        result = self.monster_client.generate(self.monster_model, input_data)
        return result['output'][0]  # Return the hyperlink of the generated image
