"""Advanced search using simple embedding-based retrieval (placeholder for future implementation)."""
from typing import List

from src.models import Resource


def generate_resource_embedding(resource: Resource) -> List[float]:
    """
    Generate a simple embedding for a resource using TF-IDF-like features.
    This is a placeholder for more sophisticated embedding models.
    """
    # Simple feature vector: [title_length, description_length, has_capacity, category_encoded]
    features = [
        len(resource.title or ''),
        len(resource.description or ''),
        1.0 if resource.capacity else 0.0,
        hash(resource.category or '') % 100 / 100.0,  # Simple category encoding
    ]
    return features


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import math
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)


def search_by_similarity(query_text: str, resources: List[Resource], top_k: int = 10) -> List[Resource]:
    """
    Search resources by semantic similarity to query text.
    This is a simplified implementation - can be enhanced with proper embeddings.
    """
    # Generate query embedding (simplified)
    query_features = [
        len(query_text),
        len(query_text) * 0.5,  # Simplified
        0.5,  # Neutral
        hash(query_text.lower()) % 100 / 100.0,
    ]
    
    # Calculate similarity for each resource
    scored_resources = []
    for resource in resources:
        resource_embedding = generate_resource_embedding(resource)
        similarity = cosine_similarity(query_features, resource_embedding)
        scored_resources.append((similarity, resource))
    
    # Sort by similarity and return top_k
    scored_resources.sort(key=lambda x: x[0], reverse=True)
    return [resource for _, resource in scored_resources[:top_k]]

