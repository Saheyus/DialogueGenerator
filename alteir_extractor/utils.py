# utils.py
def extract_speaker_from_displayname(display_name):
    """
    Extract the speaker's name from the DisplayName if SpeakerId is absent or invalid.
    Assumes that the DisplayName is in the format 'SpeakerName: "Dialogue..."'
    """
    if ':' in display_name:
        return display_name.split(':', 1)[0].strip()
    return "Unknown"

def xml_to_dict(element, namespace):
    """
    Converts an XML element to a recursive dictionary.
    """
    data = {}
    # Add element's attributes
    for key, value in element.attrib.items():
        data[key] = value

    # Process child elements
    for child in element:
        child_data = xml_to_dict(child, namespace)
        tag = child.tag.split('}')[-1]  # Handle namespaces

        # Handle lists of similar elements
        if tag in data:
            if isinstance(data[tag], list):
                data[tag].append(child_data)
            else:
                data[tag] = [data[tag], child_data]
        else:
            data[tag] = child_data

    # Add text if the element has no child elements
    if not list(element):
        text = element.text.strip() if element.text else ""
        if text:
            data = text

    return data
