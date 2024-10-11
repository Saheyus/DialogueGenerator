# generator.py

import os
import json
import openai
import logging
from typing import List, Dict, Any

class DialogueGenerator:
    def __init__(self, api_key: str = None):
        # Set up OpenAI API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set as an environment variable 'OPENAI_API_KEY'")
        openai.api_key = self.api_key

    def generate_next_line(self, dialogue_data: Dict[str, Any], selected_character: str, custom_instruction: str,
                           generation_option: str, selected_model: str = "gpt-4o", language: str = 'en') -> \
            Dict[str, Any]:
        # Load instruction content
        instruction_content = self.get_instruction_content(generation_option)

        # Clean and simplify dialogue and character data
        cleaned_data = self.clean_dialogue_data(dialogue_data)

        # Construct system and user messages
        system_message = self.construct_system_message(instruction_content)
        user_message_content = self.construct_user_message_content(selected_character, cleaned_data, custom_instruction)

        # Define the expected structured output format as JSON Schema
        output_schema = self.define_output_schema()

        # Construct messages for the API
        messages = self.construct_messages(system_message, user_message_content)

        # Print the messages being sent to the API
        self.print_api_message(messages)

        # Send the request to the OpenAI Chat API with structured JSON output
        try:
            response = self.send_openai_request(selected_model, messages, output_schema)

            # Extract the assistant's message
            assistant_message = response.choices[0].message.content
            generated_response = json.loads(assistant_message)
            return generated_response

        except Exception as e:
            logging.error(f"Error during OpenAI API call: {e}")
            logging.error(f"Response: {response}")
            raise e

    def print_api_message(self, messages: List[Dict[str, Any]]) -> None:
        print("\n--- API Request Messages ---")
        for message in messages:
            role = message.get('role', 'N/A')
            content = message.get('content', 'N/A')
            print(f"Role: {role}")
            print(f"Content:\n{content}\n")
        print("--- End of Messages ---\n")

    def get_instruction_content(self, generation_option: str) -> str:
        # Choose the instruction file based on the generation option
        if generation_option == 'alternatives':
            instruction_file = 'instruction_alternatives.txt'
        else:
            instruction_file = 'instruction.txt'

        # Load the corresponding instruction file
        if not os.path.exists(instruction_file):
            raise ValueError(f"Instruction file '{instruction_file}' not found.")

        with open(instruction_file, 'r', encoding='utf-8') as file:
            instruction_content = file.read().strip()

        return instruction_content

    def construct_system_message(self, instruction_content: str) -> Dict[str, str]:
        return {
            "role": "system",
            "content": instruction_content
        }

    def construct_user_message_content(self, selected_character: str, cleaned_data: Dict[str, Any],
                                       custom_instruction: str) -> str:
        return f"""
    Here are the details of the selected character:

    Character name: {selected_character}

    Here are the details of all characters involved:

    {json.dumps(cleaned_data['Characters'], indent=2, ensure_ascii=False)}

    Here's the context of the dialogues:

    {json.dumps(cleaned_data['Dialogues'], indent=2, ensure_ascii=False)}

    Based on this context, generate the next dialogue sequence for character {selected_character}.
    {custom_instruction}
    """

    def define_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "preparation": {
                    "type": "array",
                    "description": "Stage 1: Reflection & Analysis steps",
                    "items": {
                        "type": "string"
                    }
                },
                "dialogue_version_1": {
                    "type": "string",
                    "description": "Stage 2: Dialogue Composition version 1"
                },
                "autocritic": {
                    "type": "object",
                    "description": "Stage 3: Autocritic Feedback",
                    "properties": {
                        "strengths": {
                            "type": "string"
                        },
                        "weaknesses": {
                            "type": "string"
                        }
                    },
                    "required": ["strengths", "weaknesses"],
                    "additionalProperties": False
                },
                "improvement_advice": {
                    "type": "array",
                    "description": "Stage 4: Improvement advice",
                    "items": {
                        "type": "string"
                    }
                },
                "dialogue_version_2": {
                    "type": "string",
                    "description": "Stage 5: Dialogue Composition version 2"
                }
            },
            "required": ["preparation", "dialogue_version_1", "autocritic", "improvement_advice", "dialogue_version_2"],
            "additionalProperties": False
        }

    def construct_messages(self, system_message: Dict[str, str], user_message_content: str) -> List[Dict[str, Any]]:
        return [
            system_message,
            {"role": "user", "content": user_message_content}
        ]

    def send_openai_request(self, selected_model: str, messages: List[Dict[str, Any]],
                            output_schema: Dict[str, Any]) -> Any:
        return openai.chat.completions.create(
            model=selected_model,
            messages=messages,
            max_tokens=10000,
            temperature=0.8,
            response_format={  # Request structured output in JSON schema
                "type": "json_schema",
                "json_schema": {
                    "name": "dialogue_generation_schema",
                    "schema": output_schema,
                    "strict": True  # Enforce strict adherence to the schema
                }
            }
        )

    def clean_dialogue_data(self, dialogue_data):
        """Clean the dialogue data by removing unnecessary fields and keeping only English text."""
        cleaned_data = {}

        # Clean "Dialogues"
        dialogues = dialogue_data.get('Dialogues', [])
        cleaned_dialogues = []
        for dialogue in dialogues:
            cleaned_dialogue = {}
            messages = dialogue.get('Messages', [])
            cleaned_messages = []
            for message in messages:
                # Keep only 'Text' and 'SpeakerName'
                cleaned_message = {
                    'Text': message.get('Text', ''),
                    'SpeakerName': message.get('SpeakerName', 'Unnamed')
                }
                cleaned_messages.append(cleaned_message)
            cleaned_dialogue['Messages'] = cleaned_messages
            cleaned_dialogues.append(cleaned_dialogue)
        cleaned_data['Dialogues'] = cleaned_dialogues

        # Clean "Characters"
        characters = dialogue_data.get('Characters', [])
        cleaned_characters = []
        for character in characters:
            cleaned_character = {}
            cleaned_character['DisplayName'] = character.get('DisplayName', '')
            cleaned_character['Text'] = character.get('Text', '')
            # Process Features
            features = character.get('Features', [])
            cleaned_features = []
            for feature in features:
                properties = feature.get('Properties', {})
                cleaned_properties = {}
                for key, value in properties.items():
                    # If value is a list with both French and English, keep only the English text
                    if isinstance(value, list):
                        if len(value) > 1:
                            # Assume the second item is English
                            cleaned_value = value[1]
                        else:
                            cleaned_value = value[0]
                        cleaned_properties[key] = cleaned_value
                    else:
                        cleaned_properties[key] = value
                cleaned_features.append({'Properties': cleaned_properties})
            cleaned_character['Features'] = cleaned_features
            cleaned_characters.append(cleaned_character)
        cleaned_data['Characters'] = cleaned_characters

        # Include "Locations" if necessary
        if 'Locations' in dialogue_data:
            cleaned_data['Locations'] = dialogue_data['Locations']

        return cleaned_data
