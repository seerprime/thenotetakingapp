import spacy

# Load the English language model for spaCy
nlp = spacy.load("en_core_web_sm")

def extract_key_points(text):
    """
    Extract key points from the given text by identifying sentence boundaries.
    Here, we return the first 5 sentences as key points (you can refine this logic).
    """
    doc = nlp(text)
    key_points = [sent.text for sent in doc.sents][:5]  # Extract the top 5 key points (sentences)
    return key_points
