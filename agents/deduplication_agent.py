"""
Deduplication Agent - Identifies duplicate news (TARGET: 95%+ accuracy)
"""
from typing import Dict, List, Tuple
from database.vector_store import VectorStore
from models.embeddings import embedder
from utils.logger import logger
import hashlib

class DeduplicationAgent:
    """
    Agent 2: Finds and eliminates duplicate news articles
    This is CRITICAL - 40% of your marks depend on this!
    """
    
    def __init__(self, vector_store: VectorStore, similarity_threshold: float = 0.90):
        self.vector_store = vector_store
        self.similarity_threshold = similarity_threshold
        self.duplicate_groups = {}
    
    def process(self, article: Dict, existing_articles: List[Dict] = None) -> Dict:
        """
        Check if article is duplicate
        Returns: {
            'is_duplicate': bool,
            'duplicate_of': article_id or None,
            'similarity': float,
            'group_id': str
        }
        """
        try:
            # Create search text
            search_text = f"{article['title']} {article['content']}"
            
            # Method 1: Exact text match (fast check)
            text_hash = self._compute_hash(search_text)
            if text_hash in self.duplicate_groups:
                logger.info(f"✓ Exact duplicate found: {article['title'][:50]}")
                return {
                    'is_duplicate': True,
                    'duplicate_of': self.duplicate_groups[text_hash],
                    'similarity': 1.0,
                    'method': 'exact_match'
                }
            
            # Method 2: Semantic similarity (vector search)
            duplicates = self.vector_store.find_duplicates(article, self.similarity_threshold)
            
            if duplicates:
                best_match = duplicates[0]
                logger.info(f"✓ Semantic duplicate found: {article['title'][:50]} "
                          f"(similarity: {best_match['similarity']:.2f})")
                return {
                    'is_duplicate': True,
                    'duplicate_of': best_match['id'],
                    'similarity': best_match['similarity'],
                    'method': 'semantic_match'
                }
            
            # Method 3: Metadata-based check (title + date)
            if existing_articles:
                metadata_dup = self._check_metadata_duplicates(article, existing_articles)
                if metadata_dup:
                    return metadata_dup
            
            # Not a duplicate
            logger.info(f"✓ Unique article: {article['title'][:50]}")
            return {
                'is_duplicate': False,
                'duplicate_of': None,
                'similarity': 0.0,
                'method': 'unique'
            }
            
        except Exception as e:
            logger.error(f"Error in deduplication: {e}")
            return {
                'is_duplicate': False,
                'duplicate_of': None,
                'similarity': 0.0,
                'method': 'error'
            }
    
    def _compute_hash(self, text: str) -> str:
        """Compute hash for exact matching"""
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _check_metadata_duplicates(self, article: Dict, existing: List[Dict]) -> Dict:
        """Check duplicates based on title similarity and date"""
        article_title = article['title'].lower()
        article_date = article.get('date', '')
        
        for existing_article in existing:
            existing_title = existing_article['title'].lower()
            existing_date = existing_article.get('date', '')
            
            # Check title similarity (Jaccard)
            title_sim = self._jaccard_similarity(article_title, existing_title)
            
            # Same day + similar title = likely duplicate
            if title_sim > 0.7 and article_date == existing_date:
                return {
                    'is_duplicate': True,
                    'duplicate_of': existing_article['id'],
                    'similarity': title_sim,
                    'method': 'metadata_match'
                }
        
        return None
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Compute Jaccard similarity between two texts"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def cluster_duplicates(self, articles: List[Dict]) -> Dict[str, List[str]]:
        """
        Cluster all articles into duplicate groups
        Returns: {group_id: [article_ids]}
        """
        # Use vector store clustering
        clusters = self.vector_store.cluster_articles(articles)
        
        logger.info(f"✓ Found {len(clusters)} unique stories from {len(articles)} articles")
        
        return clusters