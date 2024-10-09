# extractor.py
import logging
import json
from .models import Dialogue, Fragment, Entity, Connection
from typing import Set
from dataclasses import asdict  # Import asdict to convert dataclass to dictionary

class DialogueFlowExtractor:
    def __init__(self, parser):
        self.parser = parser
        self.export_data = {
            'Dialogues': [],
            'Characters': [],
            'Locations': []
        }

    def extract_dialogue_flow(self, dialogue_id: str):
        if dialogue_id not in self.parser.dialogues:
            logging.error(f"Dialogue ID={dialogue_id} does not exist.")
            return
        starting_fragments = self.parser.dialogues[dialogue_id].StartingFragments
        if not starting_fragments:
            logging.warning(f"No starting fragments found for Dialogue ID={dialogue_id}.")
        involved_character_ids = set()

        for fragment_id in starting_fragments:
            flow = self.traverse_fragments_forward(fragment_id)
            dialogue_entry = {
                'DialogueId': dialogue_id,
                'DisplayName': self.parser.dialogues[dialogue_id].DisplayName,
                'Messages': flow
            }
            self.export_data['Dialogues'].append(dialogue_entry)
            logging.info(f"Dialogue flow for Dialogue ID={dialogue_id} added.")
            for message in flow:
                if message['SpeakerId']:
                    involved_character_ids.add(message['SpeakerId'])

        # Convert Entity instances to dictionaries before adding to export_data
        for char_id in involved_character_ids:
            if char_id in self.parser.entities:
                entity = self.parser.entities[char_id]
                entity_dict = asdict(entity)
                if entity_dict not in self.export_data['Characters']:
                    self.export_data['Characters'].append(entity_dict)
                    logging.debug(f"Character added: ID={char_id}, Name={entity.DisplayName}")
            else:
                logging.warning(f"Entity ID={char_id} not found.")

    def extract_fragment_flow(self, fragment_id: str):
        if fragment_id not in self.parser.fragments:
            logging.error(f"Fragment ID={fragment_id} does not exist.")
            return
        involved_character_ids = set()
        flow = self.traverse_fragments_backward(fragment_id)
        fragment_entry = {
            'FragmentId': fragment_id,
            'Messages': flow
        }
        self.export_data['Dialogues'].append(fragment_entry)
        logging.info(f"Dialogue flow for Fragment ID={fragment_id} added.")
        for message in flow:
            if message['SpeakerId']:
                involved_character_ids.add(message['SpeakerId'])

        # Convert Entity instances to dictionaries before adding to export_data
        for char_id in involved_character_ids:
            if char_id in self.parser.entities:
                entity = self.parser.entities[char_id]
                entity_dict = asdict(entity)
                if entity_dict not in self.export_data['Characters']:
                    self.export_data['Characters'].append(entity_dict)
                    logging.debug(f"Character added: ID={char_id}, Name={entity.DisplayName}")
            else:
                logging.warning(f"Entity ID={char_id} not found.")

    def traverse_fragments_forward(self, fragment_id, visited=None):
        if visited is None:
            visited = set()
        if fragment_id in visited:
            logging.warning(f"Loop detected at fragment ID={fragment_id}, stopping traversal.")
            return []
        visited.add(fragment_id)
        fragment = self.parser.fragments.get(fragment_id)
        if not fragment:
            logging.warning(f"Fragment ID={fragment_id} not found.")
            return []
        flow = [{
            'FragmentId': fragment_id,
            'Text': fragment.Text,
            'SpeakerId': fragment.SpeakerId,
            'SpeakerName': fragment.SpeakerName
        }]
        for target_id in self.parser.source_to_targets.get(fragment_id, []):
            flow.extend(self.traverse_fragments_forward(target_id, visited))
        return flow

    def traverse_fragments_backward(self, fragment_id, visited=None):
        if visited is None:
            visited = set()
        if fragment_id in visited:
            logging.warning(f"Loop detected at fragment ID={fragment_id}, stopping traversal.")
            return []
        visited.add(fragment_id)
        flow = []
        for conn in self.parser.connections:
            if conn.Target == fragment_id:
                source_id = conn.Source
                if source_id in self.parser.fragments:
                    flow_part = self.traverse_fragments_backward(source_id, visited)
                    flow.extend(flow_part)
        fragment = self.parser.fragments.get(fragment_id)
        if fragment:
            flow.append({
                'FragmentId': fragment_id,
                'Text': fragment.Text,
                'SpeakerId': fragment.SpeakerId,
                'SpeakerName': fragment.SpeakerName
            })
        return flow

def save_to_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Data successfully exported to {output_file}")
    except Exception as e:
        logging.error(f"Error saving JSON file: {e}")
