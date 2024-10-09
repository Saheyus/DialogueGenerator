import threading
import logging
import os
import json
import tkinter as tk
import winsound
import time
import pprint

from alteir_extractor.parser import parse_alteir_xml
from alteir_extractor.extractor import DialogueFlowExtractor, save_to_json
from alteir_extractor.generator import DialogueGenerator


class AlteirController:
    def __init__(self, gui):
        self.gui = gui
        self.parser = None
        self.selected_id = None
        self.selected_dialogue = None

    def load_xml(self):
        xml_file = self.gui.get_xml_file_path()
        if not xml_file:
            self.gui.display_error("Error", "Please select an XML file.")
            return
        if not os.path.exists(xml_file):
            self.gui.display_error("Error", f"The file {xml_file} does not exist.")
            return
        try:
            self.parser = parse_alteir_xml(xml_file)
            self.populate_listbox()
            logging.info("XML file loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading XML file: {e}")
            self.gui.display_error("Error", f"Failed to load XML file:\n{e}")

    def populate_listbox(self):
        self.gui.left_frame_ui.clear_listbox()
        self.gui.left_frame_ui.clear_dialogue_ids()
        self.gui.left_frame_ui.clear_fragment_ids()

        self.gui.left_frame_ui.insert_into_listbox(tk.END, "Dialogues:")
        for dialogue_id, dialogue in self.parser.dialogues.items():
            display_text = f"Dialogue ID: {dialogue_id}, DisplayName: {dialogue.DisplayName}"
            self.gui.left_frame_ui.add_dialogue_id(display_text, dialogue_id)
            self.gui.left_frame_ui.insert_into_listbox(tk.END, display_text)

        self.gui.left_frame_ui.insert_into_listbox(tk.END, "")
        self.gui.left_frame_ui.insert_into_listbox(tk.END, "Fragments:")
        for fragment_id, fragment in self.parser.fragments.items():
            display_text = f"Fragment ID: {fragment_id}, DisplayName: {fragment.DisplayName}"
            self.gui.left_frame_ui.add_fragment_id(display_text, fragment_id)
            self.gui.left_frame_ui.insert_into_listbox(tk.END, display_text)

    def get_fragment_text(self, fragment_id):
        """Retrieve the text of the fragment or dialogue with the given ID."""
        if fragment_id in self.parser.dialogues:
            dialogue = self.parser.dialogues[fragment_id]
            # Assuming 'Text' is an attribute of dialogue
            text = dialogue.Text  # Adjust based on your parser's attributes
            return text
        elif fragment_id in self.parser.fragments:
            fragment = self.parser.fragments[fragment_id]
            # Assuming 'Text' is an attribute of fragment
            text = fragment.Text  # Adjust based on your parser's attributes
            return text
        else:
            logging.warning(f"No fragment or dialogue found with ID {fragment_id}")
            return "No text available for the selected fragment."

    def extract(self):
        logging.info("Extraction requested.")
        if not self.selected_id:
            logging.warning("No dialogue or fragment selected for extraction.")
            self.gui.display_error(
                "Error", "Please select a Dialogue or Fragment to extract."
            )
            return

        output_file = self.gui.get_output_file_path()
        if not output_file:
            logging.warning("No output file path specified.")
            self.gui.display_error("Error", "Please specify an output file.")
            return

        try:
            # Start the extraction thread
            logging.info(f"Starting extraction for selected ID: {self.selected_id}")
            extraction_thread = threading.Thread(target=self.run_extraction, args=(output_file,))
            extraction_thread.start()
        except Exception as e:
            logging.error(f"An error occurred during extraction: {e}")
            self.gui.display_error("Extraction Error", str(e))

    def run_extraction(self, output_file):
        try:
            logging.info(f"Starting extraction for selected ID: {self.selected_id}")

            extracted_data = self.extract_dialogue_or_fragment()

            self.include_location_data(extracted_data)

            self.display_extracted_text(extracted_data)

            self.save_extracted_data_to_file(extracted_data, output_file)

            self.validate_output_file(output_file)

            self.confirm_extraction_completion()

        except json.JSONDecodeError as json_error:
            self.handle_extraction_error(output_file, json_error, "JSON")
        except OSError as os_error:
            self.handle_extraction_error(output_file, os_error, "OS")
        except Exception as e:
            self.handle_extraction_error(output_file, e, "unexpected")

    def extract_dialogue_or_fragment(self):
        # Initialize the DialogueFlowExtractor
        flow_extractor = DialogueFlowExtractor(self.parser)

        # Extract dialogue or fragment based on selected ID
        if self.selected_id in self.parser.dialogues:
            logging.info(f"Extracting dialogue flow for Dialogue ID={self.selected_id}...")
            flow_extractor.extract_dialogue_flow(self.selected_id)
        elif self.selected_id in self.parser.fragments:
            logging.info(f"Extracting dialogue flow for Fragment ID={self.selected_id}...")
            flow_extractor.extract_fragment_flow(self.selected_id)
        else:
            logging.error("Selected ID does not match any Dialogue or Fragment.")
            self.gui.display_error("Error", "Selected ID does not match any Dialogue or Fragment.")
            return None

        return flow_extractor.export_data

    def include_location_data(self, extracted_data):
        logging.info("Including extracted locations into export data.")
        locations_data = self.parser.locations  # Assuming locations were previously extracted and stored in parser
        extracted_data['Locations'] = {loc_id: loc.__dict__ for loc_id, loc in locations_data.items()}

    def display_extracted_text(self, extracted_data):
        formatted_text = ""
        for dialogue in extracted_data['Dialogues']:
            for message in dialogue['Messages']:
                speaker_name = message.get('SpeakerName', 'Unnamed')
                text = message['Text']
                formatted_text += f"{speaker_name}: {text}\n\n"

        # Use the main GUI thread to update the text
        self.gui.master.after(0, self.gui.left_frame_ui.display_fragment_text, formatted_text)

    def save_extracted_data_to_file(self, extracted_data, output_file):
        try:
            save_to_json(extracted_data, output_file)
            logging.info(f"Data successfully exported to {output_file}")
        except Exception as e:
            logging.error(f"Error saving data to {output_file}: {e}")
            self.gui.display_error("Error", f"Failed to save data to {output_file}:\n{e}")

    def validate_output_file(self, output_file):
        # Ensure the file exists and contains data before attempting to read it
        if not os.path.exists(output_file):
            logging.error(f"Output file {output_file} does not exist after saving.")
            self.gui.display_error("Error", f"Output file {output_file} does not exist.")
            return

        if os.path.getsize(output_file) == 0:
            logging.error(f"Output file {output_file} is empty after saving.")
            self.gui.display_error("Error", f"Output file {output_file} is empty.")

    def confirm_extraction_completion(self):
        # Play a confirmation sound and populate the character dropdown after extraction
        winsound.MessageBeep()
        logging.info("Populating character dropdown after extraction.")
        self.populate_character_dropdown()

    def handle_extraction_error(self, output_file, error, error_type):
        logging.error(f"{error_type.capitalize()} error when processing {output_file}: {error}")
        self.gui.display_error("Error", f"Failed to process {output_file} due to {error_type} error:\n{error}")

    def populate_character_dropdown(self):
        output_file = self.gui.get_output_file_path()
        if not output_file or not os.path.exists(output_file):
            logging.error("Output file does not exist.")
            return

        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                extracted_data = json.load(f)

            characters_data = extracted_data.get('Characters', [])
            if not characters_data:
                logging.error("No characters found in the extracted data.")
                return

            characters = [char.get('DisplayName', 'Unnamed') for char in characters_data]
            logging.info(f"Characters extracted: {characters}")

            # Update the character dropdown in the main GUI thread
            self.gui.master.after(0, self.gui.right_frame_ui.update_character_dropdown, characters)
            self.gui.master.after(0, self.gui.right_frame_ui.enable_generate_buttons)
        except Exception as e:
            logging.error(f"Error loading characters from output file: {e}")
            self.gui.display_error("Error", f"Failed to load characters:\n{e}")

    def generate_dialogue(self):
        output_file = self.gui.get_output_file_path()
        if not output_file or not os.path.exists(output_file):
            self.gui.display_error(
                "Error", "Please extract dialogue data first to generate the next line."
            )
            return

        selected_character = self.gui.right_frame_ui.get_selected_character()
        if not selected_character:
            self.gui.display_error("Error", "Please select a character.")
            return

        custom_instruction = self.gui.left_frame_ui.get_custom_instruction()

        generation_option = self.gui.right_frame_ui.get_generation_option()

        # Get the selected model
        selected_model = self.gui.right_frame_ui.get_selected_model()

        threading.Thread(
            target=self.run_generation,
            args=(output_file, selected_character, custom_instruction, generation_option, selected_model),
        ).start()

    def run_generation(self, output_file, selected_character, custom_instruction, generation_option, selected_model):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                dialogue_data = json.load(f)

            # Clean the dialogue data
            cleaned_data = self.clean_dialogue_data(dialogue_data)

            # Load the API key from a .txt file
            try:
                with open('api_key.txt', 'r', encoding='utf-8') as key_file:
                    api_key = key_file.read().strip()
            except FileNotFoundError:
                logging.error("API key file missing. Ensure 'api_key.txt' exists.")
                self.gui.display_error("Error", "API key file 'api_key.txt' not found.")
                return
            except Exception as e:
                logging.error(f"Error reading API key: {e}")
                self.gui.display_error("Error", f"An error occurred while reading the API key:\n{e}")
                return

            # Create an instance of DialogueGenerator
            generator = DialogueGenerator(api_key=api_key)

            # Generate the next dialogue or alternatives using AI
            generated_output = generator.generate_next_line(
                cleaned_data, selected_character, custom_instruction, generation_option, selected_model
            )

            # Log the raw API output for verification
            logging.info(f"Raw API output:\n{pprint.pformat(generated_output)}")

            # Extract generated dialogues and feedback
            preparation = generated_output.get(
                'preparation', 'No preparation content available.'
            )

            autocritic_feedback = generated_output.get(
                'autocritic', generated_output.get('context_comparison', 'No autocritic available.')
            )

            improvement_advice = generated_output.get(
                'improvement_advice', generated_output.get('brainstorm', 'No improvement advice available.')
            )

            # Combine autocritic and improvement advice
            combined_feedback = f"Autocritic:\n{autocritic_feedback}\n\nImprovement Advice:\n{improvement_advice}"

            if generation_option == 'continuation':
                dialogue_1 = generated_output.get(
                    'dialogue_version_1', 'Dialogue not generated.'
                )
                dialogue_2 = generated_output.get(
                    'dialogue_version_2', 'Dialogue not generated.'
                )
            elif generation_option == 'alternatives':
                dialogue_1 = generated_output.get(
                    'alternative_1', 'Alternative not generated.'
                )
                dialogue_2 = generated_output.get(
                    'alternative_2', 'Alternative not generated.'
                )
            else:
                logging.error(f"Unknown generation option: {generation_option}")
                self.gui.display_error("Error", f"Unknown generation option: {generation_option}")
                return

            self.gui.right_frame_ui.on_dialogue_generated()

            # Update the interface with the generated texts
            self.gui.master.after(0, self.gui.right_frame_ui.display_preparation_text, preparation)
            self.gui.master.after(0, self.gui.right_frame_ui.display_generated_dialogue, dialogue_1, dialogue_2)
            self.gui.master.after(0, self.gui.right_frame_ui.display_autocritic_feedback, combined_feedback)

        except Exception as e:
            logging.error(f"Unexpected error during dialogue generation: {e}")
            self.gui.display_error(
                "Error", f"An error occurred during dialogue generation:\n{e}"
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

    def save_dialogue(self):
        generated_file = "./NewDialogue.txt"
        try:
            # Determine which dialogue to save based on the selected choice
            choice = self.gui.right_frame_ui.dialogue_choice.get()
            dialogue_to_save = self.gui.right_frame_ui.get_generated_dialogue_text(choice)

            # Save the selected dialogue to a separate file
            with open(generated_file, 'a', encoding='utf-8') as f:
                f.write(dialogue_to_save + '\n')

            self.gui.display_message("Success", f"Dialogue saved to {generated_file}")
        except Exception as e:
            logging.error(f"Unexpected error during dialogue saving: {e}")
            self.gui.display_error(
                "Error", f"An error occurred while saving the dialogue:\n{e}"
            )

    def reroll_dialogue(self):
        self.generate_dialogue()