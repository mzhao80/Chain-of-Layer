import json
import spacy
from collections import Counter
import os
from tqdm import tqdm

def load_speeches(file_path):
    """Load and preprocess the speeches file"""
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                speeches = f.readlines()
                print(f"Successfully loaded file with {encoding} encoding")
                return speeches
        except Exception as e:
            print(f"Failed with {encoding} encoding: {str(e)}")
            continue
    
    raise ValueError("Could not read file with any of the attempted encodings")

def extract_key_terms(speeches, nlp, min_freq=5, max_terms=1000):
    """Extract key terms from speeches using NLP"""
    # Process speeches to extract noun phrases and named entities
    terms = []
    print("Extracting terms from speeches...")
    for speech in tqdm(speeches):
        doc = nlp(speech)
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Limit to phrases of 3 words or less
                terms.append(chunk.text.lower())
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'GPE', 'LAW', 'NORP']:  # Focus on relevant entity types
                if len(ent.text.split()) <= 3:
                    terms.append(ent.text.lower())
    
    # Count term frequencies
    term_counts = Counter(terms)
    
    # Filter terms by frequency and get top terms
    filtered_terms = [term for term, count in term_counts.most_common(max_terms) 
                     if count >= min_freq]
    
    return filtered_terms

def prepare_for_taxonomy(terms):
    """Prepare the extracted terms for taxonomy generation"""
    # Create the base structure with "congressional_topics" as root
    data = {
        "root": "congressional_topics",
        "entity_list": ["congressional_topics"] + terms
    }
    return data

def main():
    # Load spaCy model
    print("Loading NLP model...")
    nlp = spacy.load("en_core_web_sm")
    
    # Create necessary directories
    os.makedirs("dataset/processed/congressional", exist_ok=True)
    
    # Process speeches
    print("Loading speeches...")
    speeches = load_speeches("speeches/speeches_114.txt")
    
    # Extract terms
    terms = extract_key_terms(speeches, nlp)
    
    # Prepare data for taxonomy generation
    taxonomy_data = prepare_for_taxonomy(terms)
    
    # Save processed data
    output_path = "dataset/processed/congressional/test.json"
    with open(output_path, 'w') as f:
        json.dump(taxonomy_data, f)
    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    main()
