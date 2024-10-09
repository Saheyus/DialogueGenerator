# parser.py
import xml.etree.ElementTree as ET
from typing import Dict, List
from collections import defaultdict
import logging
import sys

from .models import Entity, Location, Dialogue, Fragment, Connection, Feature
from .utils import extract_speaker_from_displayname, xml_to_dict

class AlteirXMLParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.namespace = {'ns': 'http://www.articy.com/schemas/articydraft/4.0/XmlContentExport_FullProject.xsd'}
        self.dialogues: Dict[str, Dialogue] = {}
        self.fragments: Dict[str, Fragment] = {}
        self.connections: List[Connection] = []
        self.entities: Dict[str, Entity] = {}
        self.locations: Dict[str, Location] = {}
        self.flow_fragments: Dict[str, List[str]] = {}
        self.source_to_targets: Dict[str, List[str]] = defaultdict(list)
        self.tree = None
        self.root = None

    def parse(self):
        self.load_xml()
        self.extract_entities()
        self.extract_locations()
        self.extract_flow_fragments()
        self.extract_dialogues()
        self.extract_fragments()
        self.extract_connections()
        self.build_source_to_targets()
        self.identify_starting_fragments()

    def load_xml(self):
        try:
            logging.info(f"Loading and parsing XML file: {self.file_path}")
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
        except ET.ParseError as e:
            logging.error(f"XML parsing error: {e}")
            sys.exit(1)
        except FileNotFoundError:
            logging.error(f"XML file not found: {self.file_path}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error loading XML file: {e}")
            sys.exit(1)

    def extract_entities(self):
        logging.info("Extracting entities (actors)...")
        for entity_elem in self.root.findall('.//ns:Entity', self.namespace):
            entity_id = entity_elem.get('Id')

            # Extract only English display name
            display_name_elem = entity_elem.find('.//ns:DisplayName/ns:LocalizedString[@Lang="en"]', self.namespace)
            display_name = display_name_elem.text.strip() if display_name_elem is not None and display_name_elem.text else "Unnamed"

            # Extract only English text
            text_elem = entity_elem.find('.//ns:Text/ns:LocalizedString[@Lang="en"]', self.namespace)
            text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

            # Extract features ensuring only English strings are kept
            features = self.extract_features(entity_elem)

            # Create the entity object with extracted information
            entity = Entity(
                Id=entity_id,
                DisplayName=display_name,
                Text=text,
                Features=features,
                References=[]  # Adjust if needed
            )

            self.entities[entity_id] = entity
            logging.debug(f"Found entity: ID={entity_id}, Name={display_name}")

    def extract_features(self, entity_elem):
        features = []
        for feature_elem in entity_elem.findall('.//ns:Feature', self.namespace):
            properties = {}
            for prop in feature_elem.findall('.//ns:Properties/ns:*', self.namespace):
                prop_name = prop.get('Name')
                prop_value = self.extract_property_value(prop)
                properties[prop_name] = prop_value
            feature = Feature(Properties=properties)
            features.append(feature)
        return features

    def extract_property_value(self, prop):
        if prop.tag.endswith('Number'):
            try:
                return int(prop.text.strip()) if prop.text else 0
            except ValueError:
                logging.warning(f"Non-numeric value for {prop.get('Name')}")
                return 0
        elif prop.tag.endswith('String'):
            return prop.text.strip() if prop.text else ""
        elif prop.tag.endswith('Enum'):
            return prop.text.strip() if prop.text else ""
        elif prop.tag.endswith('LocalizableText'):
            localized_strings = []
            for ls in prop.findall('.//ns:LocalizedString', self.namespace):
                localized_text = ls.text.strip() if ls.text else ""
                localized_strings.append(localized_text)
            return localized_strings
        else:
            return prop.text.strip() if prop.text else ""

    def extract_locations(self):
        logging.info("Extracting locations...")

        for location_elem in self.root.findall('.//ns:Location', self.namespace):
            location_id = location_elem.get('Id')

            # Attempt to find display name in English
            display_name_elem = location_elem.find('.//ns:DisplayName/ns:LocalizedString[@Lang="en"]', self.namespace)

            # Fallback to French if English is not available
            if display_name_elem is None or not display_name_elem.text.strip():
                display_name_elem = location_elem.find('.//ns:DisplayName/ns:LocalizedString[@Lang="fr"]',
                                                       self.namespace)

            # Use "Sans Nom" if no valid display name is found
            display_name = display_name_elem.text.strip() if display_name_elem is not None and display_name_elem.text else "Sans Nom"

            location_dict = xml_to_dict(location_elem, self.namespace)
            location = Location(
                Id=location_id,
                Name=display_name,
                Data=location_dict
            )
            self.locations[location_id] = location
            logging.debug(f"Found location: ID={location_id}, Name={display_name}")

    def extract_flow_fragments(self):
        logging.info("Associating flow fragments to locations...")
        for flow_fragment_elem in self.root.findall('.//ns:FlowFragment', self.namespace):
            fragment_id = flow_fragment_elem.get('Id')
            location_elems = flow_fragment_elem.findall('.//ns:Reference', self.namespace)
            associated_locations = []
            for loc_ref in location_elems:
                loc_id = loc_ref.get('IdRef')
                # Fix: Access the 'Name' attribute of the Location object
                if loc_id in self.locations:
                    loc_name = self.locations[loc_id].Name
                else:
                    loc_name = 'Unknown'
                if loc_name and loc_name != "Unknown":
                    associated_locations.append(loc_name)
            self.flow_fragments[fragment_id] = associated_locations if associated_locations else ["Unknown"]
            logging.debug(f"FlowFragment ID={fragment_id} associated with locations: {self.flow_fragments[fragment_id]}")

    def extract_dialogues(self):
        logging.info("Extracting dialogues...")
        for dialogue_elem in self.root.findall('.//ns:Dialogue', self.namespace):
            dialogue_id = dialogue_elem.get('Id')
            display_name_elem = dialogue_elem.find('.//ns:DisplayName/ns:LocalizedString[@Lang="en"]', self.namespace)
            display_name = display_name_elem.text.strip() if display_name_elem is not None and display_name_elem.text else "Sans Nom"
            text_elem = dialogue_elem.find('.//ns:Text/ns:LocalizedString[@Lang="en"]', self.namespace)
            text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""
            dialogue = Dialogue(
                Id=dialogue_id,
                DisplayName=display_name,
                Text=text,
                StartingFragments=[]
            )
            self.dialogues[dialogue_id] = dialogue
            logging.debug(f"Found dialogue: ID={dialogue_id}, DisplayName={display_name}")

    def extract_fragments(self):
        logging.info("Extracting dialogue fragments...")
        for fragment_elem in self.root.findall('.//ns:DialogueFragment', self.namespace):
            fragment_id = fragment_elem.get('Id')
            display_name_elem = fragment_elem.find('.//ns:DisplayName', self.namespace)
            display_name = display_name_elem.text.strip() if display_name_elem is not None and display_name_elem.text else "Sans Nom"
            text_elem = fragment_elem.find('.//ns:Text/ns:LocalizedString[@Lang="en"]', self.namespace)
            text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""
            speaker_elem = fragment_elem.find('.//ns:Speaker', self.namespace)
            speaker_ref = speaker_elem.get('IdRef') if speaker_elem is not None else None
            if speaker_ref and speaker_ref in self.entities:
                speaker_name = self.entities[speaker_ref].DisplayName
                logging.debug(f"Found speaker for Fragment ID={fragment_id}: {speaker_name}")
            else:
                speaker_name = extract_speaker_from_displayname(display_name)
                logging.debug(f"Speaker extracted from DisplayName for Fragment ID={fragment_id}: {speaker_name}")
            fragment = Fragment(
                Id=fragment_id,
                DisplayName=display_name,
                Text=text,
                SpeakerId=speaker_ref,
                SpeakerName=speaker_name
            )
            self.fragments[fragment_id] = fragment
            logging.debug(f"Found fragment: ID={fragment_id}, Speaker={speaker_name}")

    def extract_connections(self):
        logging.info("Extracting connections...")
        for connection_elem in self.root.findall('.//ns:Connection', self.namespace):
            source_elem = connection_elem.find('.//ns:Source', self.namespace)
            target_elem = connection_elem.find('.//ns:Target', self.namespace)
            source_id = source_elem.get('IdRef') if source_elem is not None else None
            target_id = target_elem.get('IdRef') if target_elem is not None else None
            connection = Connection(
                Source=source_id,
                Target=target_id
            )
            self.connections.append(connection)
            logging.debug(f"Found connection: Source={source_id}, Target={target_id}")

    def build_source_to_targets(self):
        for conn in self.connections:
            self.source_to_targets[conn.Source].append(conn.Target)

    def identify_starting_fragments(self):
        logging.info("Identifying starting fragments for each dialogue...")
        for dialogue_id, dialogue in self.dialogues.items():
            dialogue_elem = self.root.find(f".//ns:Dialogue[@Id='{dialogue_id}']", self.namespace)
            if dialogue_elem is None:
                logging.warning(f"Dialogue element not found for ID={dialogue_id}")
                continue
            pins = dialogue_elem.findall('.//ns:Pin', self.namespace)
            output_pins = [pin for pin in pins if pin.get('Semantic') == 'Output']
            for pin in output_pins:
                pin_id = pin.get('Id')
                for conn in self.connections:
                    if conn.Source == pin_id:
                        target_fragment_id = conn.Target
                        if target_fragment_id in self.fragments:
                            dialogue.StartingFragments.append(target_fragment_id)
                            logging.debug(f"Dialogue ID={dialogue_id} has starting fragment ID={target_fragment_id}")
                        else:
                            logging.warning(f"Target fragment {target_fragment_id} not found for Dialogue ID={dialogue_id}")

def parse_alteir_xml(file_path):
    parser = AlteirXMLParser(file_path)
    parser.parse()
    return parser  # Return the parser object containing the data
