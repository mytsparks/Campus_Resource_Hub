"""Advanced search using TF-IDF embedding-based retrieval."""
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from src.models import Resource


def build_resource_text(resource: Resource) -> str:
    """Build a combined text representation of a resource for embedding."""
    parts = []
    if resource.title:
        parts.append(resource.title)
    if resource.description:
        parts.append(resource.description)
    if resource.category:
        parts.append(resource.category)
    if resource.location:
        parts.append(resource.location)
    # Add capacity as text for better matching
    if resource.capacity:
        parts.append(f"capacity {resource.capacity}")
    return " ".join(parts).lower()


def search_by_similarity(query_text: str, resources: List[Resource], top_k: int = 50) -> List[Resource]:
    """
    Search resources by semantic similarity using TF-IDF vectorization.
    Uses scikit-learn's TfidfVectorizer for proper text-based similarity matching.
    """
    if not resources or not query_text:
        return resources[:top_k]
    
    # Build text representations
    resource_texts = [build_resource_text(r) for r in resources]
    
    # Combine query with resource texts for TF-IDF
    all_texts = [query_text.lower()] + resource_texts
    
    try:
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=1,
            max_df=0.95
        )
        
        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Query vector is first row, resource vectors are the rest
        query_vector = tfidf_matrix[0:1]
        resource_vectors = tfidf_matrix[1:]
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, resource_vectors).flatten()
        
        # Pair resources with their similarity scores
        scored_resources = list(zip(similarities, resources))
        
        # Sort by similarity (descending) and return top_k
        scored_resources.sort(key=lambda x: x[0], reverse=True)
        
        # Return resources, filtering out very low similarity scores
        threshold = 0.01  # Minimum similarity threshold
        filtered = [r for score, r in scored_resources if score >= threshold]
        
        return filtered[:top_k] if filtered else [r for _, r in scored_resources[:top_k]]
        
    except Exception as e:
        # Fallback to simple keyword matching if TF-IDF fails
        print(f"TF-IDF search error: {e}, falling back to keyword search")
        query_lower = query_text.lower()
        scored = []
        for resource in resources:
            text = build_resource_text(resource)
            # Simple keyword matching score
            score = sum(1 for word in query_lower.split() if word in text) / max(len(query_lower.split()), 1)
            scored.append((score, resource))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]

