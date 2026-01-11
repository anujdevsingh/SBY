import json
import os
import re
from pathlib import Path
from typing import List
from functools import lru_cache

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import current_app


def read_pdf(path: Path) -> str:
    """Extract text from PDF file."""
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def clean_text(text: str) -> str:
    """
    Clean text by removing excessive spacing between characters.
    This fixes the PDF extraction issue where Hindi characters have spaces between them.
    """
    # Remove excessive spaces (multiple spaces -> single space)
    text = re.sub(r'\s+', ' ', text)
    
    # For Hindi text: remove ALL spaces between Devanagari characters
    # Devanagari Unicode range: \u0900-\u097F
    # This includes: consonants, vowels, matras, numerals, etc.
    
    # Apply multiple passes to remove all spacing between Devanagari characters
    # Need many iterations because each regex only removes one space at a time
    for _ in range(10):  # Increased iterations for thorough cleaning
        # Remove space between any two Devanagari characters
        text = re.sub(r'([\u0900-\u097F])\s+([\u0900-\u097F])', r'\1\2', text)
        # Remove space between Devanagari and common punctuation
        text = re.sub(r'([\u0900-\u097F])\s+([.,!?;:।])', r'\1\2', text)
        text = re.sub(r'([.,!?;:।])\s+([\u0900-\u097F])', r'\1\2', text)
    
    return text.strip()


def chunk_text(text: str, max_words: int = 150) -> List[str]:
    """Split text into chunks by paragraphs or sentences."""
    # Remove excessive spacing (common in Hindi PDF extraction)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Split by double newlines (paragraphs) or single newlines
    paragraphs = re.split(r'\n\n+|\n', text)
    chunks = []
    
    for para in paragraphs:
        para = para.strip()
        if not para or len(para) < 10:  # Skip very short chunks
            continue
        
        # If paragraph is too long, split by sentences
        if len(para.split()) > max_words:
            sentences = re.split(r'[.!?।]+', para)  # Added Hindi full stop
            current_chunk = ""
            for sent in sentences:
                sent = sent.strip()
                if not sent or len(sent) < 5:
                    continue
                if len((current_chunk + " " + sent).split()) <= max_words:
                    current_chunk = (current_chunk + " " + sent).strip()
                else:
                    if current_chunk and len(current_chunk) > 10:
                        chunks.append(current_chunk)
                    current_chunk = sent
            if current_chunk and len(current_chunk) > 10:
                chunks.append(current_chunk)
        else:
            chunks.append(para)
    
    return chunks


@lru_cache(maxsize=1)
def _load_policy_data():
    """Load policy documents and create TF-IDF index (cached)."""
    policies_dir = Path(current_app.config.get('UPLOAD_FOLDER', '')).parent / 'policies'
    
    if not policies_dir.exists():
        raise FileNotFoundError(f"Policies directory not found: {policies_dir}")
    
    all_chunks = []
    all_metadata = []
    
    # Load all policy documents
    for pdf_file in policies_dir.glob('*.pdf'):
        text = read_pdf(pdf_file)
        text = clean_text(text)  # Clean the text to make it readable
        chunks = chunk_text(text)
        
        for i, chunk in enumerate(chunks):
            cleaned_chunk = clean_text(chunk)  # Clean each chunk too
            all_chunks.append(cleaned_chunk)
            all_metadata.append({
                "text": cleaned_chunk,
                "source": pdf_file.name,
                "ref": f"{pdf_file.name}#chunk-{i}"
            })
    
    # Also support txt/md files
    for text_file in list(policies_dir.glob('*.txt')) + list(policies_dir.glob('*.md')):
        text = text_file.read_text(encoding='utf-8', errors='ignore')
        text = clean_text(text)  # Clean the text
        chunks = chunk_text(text)
        
        for i, chunk in enumerate(chunks):
            cleaned_chunk = clean_text(chunk)
            all_chunks.append(cleaned_chunk)
            all_metadata.append({
                "text": cleaned_chunk,
                "source": text_file.name,
                "ref": f"{text_file.name}#chunk-{i}"
            })
    
    if not all_chunks:
        raise ValueError("No policy documents found in policies directory")
    
    # Create TF-IDF vectorizer with settings that work for both Hindi and English
    vectorizer = TfidfVectorizer(
        max_features=2000,
        ngram_range=(1, 3),  # Increased for better phrase matching
        min_df=1,  # Allow all terms
        max_df=0.85,  # Filter very common terms
        token_pattern=r'(?u)\b\w+\b'  # Unicode word characters for Hindi support
    )
    
    # Fit and transform chunks
    tfidf_matrix = vectorizer.fit_transform(all_chunks)
    
    print(f"Loaded {len(all_chunks)} policy chunks for search")
    
    return vectorizer, tfidf_matrix, all_metadata


def search(query: str, top_k: int = 5) -> List[dict]:
    """
    Search policy documents using TF-IDF similarity.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        
    Returns:
        List of result dictionaries with text, source, ref, and score
    """
    vectorizer, tfidf_matrix, metadata = _load_policy_data()
    
    # Transform query
    query_vec = vectorizer.transform([query])
    
    # Compute cosine similarity
    similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
    
    # Get top-k indices
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    # Build results - return all top-k even with low scores
    results = []
    for idx in top_indices:
        results.append({
            "text": metadata[idx]["text"],
            "source": metadata[idx]["source"],
            "ref": metadata[idx]["ref"],
            "score": float(similarities[idx])
        })
    
    return results
