import spacy
from spacy.matcher import Matcher

# Load the English language model for spaCy
nlp = spacy.load("en_core_web_sm")

def summarize_text(text):
    """
    A function to summarize the given text by extracting important sentences.
    This can be customized based on your requirements.
    """
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents][:5]  # For example, take the first 5 sentences
    return sentences

def extract_key_points(text, top_n=5):
    """
    Extract key points from the given text.
    Improved by filtering important sentences based on structure and noun phrases.
    """
    doc = nlp(text)

    # Use a matcher to detect noun phrases and important sentences
    matcher = Matcher(nlp.vocab)
    pattern = [{"POS": "NOUN"}, {"POS": "VERB"}]
    matcher.add("NounPhraseVerb", [pattern])

    matched_sentences = []
    for sent in doc.sents:
        matches = matcher(sent)
        if matches:
            matched_sentences.append(sent.text)

    # If there are no matched sentences, fallback to extracting the first few sentences
    if not matched_sentences:
        matched_sentences = [sent.text for sent in doc.sents][:top_n]

    # Return the top N sentences
    return matched_sentences[:top_n]
