"""
Embedding model wrapper
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np

class EmbeddingModel:
    """Wrapper for embedding model with caching"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.cache = {}
    
    def encode(self, texts: Union[str, List[str]], use_cache: bool = True) -> np.ndarray:
        """Generate embeddings with optional caching"""
        if isinstance(texts, str):
            texts = [texts]
            single = True
        else:
            single = False
        
        embeddings = []
        texts_to_encode = []
        indices = []
        
        for i, text in enumerate(texts):
            if use_cache and text in self.cache:
                embeddings.append(self.cache[text])
            else:
                texts_to_encode.append(text)
                indices.append(i)
        
        # Encode uncached texts
        if texts_to_encode:
            new_embeddings = self.model.encode(texts_to_encode)
            for text, emb in zip(texts_to_encode, new_embeddings):
                if use_cache:
                    self.cache[text] = emb
                embeddings.insert(indices[len(embeddings)], emb)
        
        result = np.array(embeddings)
        return result[0] if single else result
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

# Global instance
embedder = EmbeddingModel()