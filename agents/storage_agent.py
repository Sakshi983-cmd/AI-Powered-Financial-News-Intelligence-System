"""
Storage & Indexing Agent - Stores processed articles
"""
from typing import Dict, List
from database.vector_store import VectorStore
from utils.logger import logger
import json

class StorageAgent:
    """
    Agent 5: Store processed articles in vector DB
    """
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.stored_count = 0
    
    def process(self, article: Dict, is_duplicate: bool = False) -> Dict:
        """
        Store article if not duplicate
        """
        try:
            if is_duplicate:
                logger.info(f"⊘ Skipping duplicate: {article['title'][:50]}")
                return {
                    'stored': False,
                    'reason': 'duplicate',
                    'article_id': article.get('id')
                }
            
            # Store in vector database
            article_id = self.vector_store.add_article(article)
            
            self.stored_count += 1
            logger.info(f"✓ Stored article: {article['title'][:50]} (ID: {article_id})")
            
            return {
                'stored': True,
                'article_id': article_id,
                'stored_count': self.stored_count
            }
            
        except Exception as e:
            logger.error(f"Error storing article: {e}")
            return {
                'stored': False,
                'reason': f'error: {str(e)}',
                'article_id': article.get('id')
            }
    
    def batch_store(self, articles: List[Dict], duplicate_flags: List[bool]) -> Dict:
        """Store multiple articles"""
        results = {
            'stored': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for article, is_dup in zip(articles, duplicate_flags):
            result = self.process(article, is_dup)
            
            if result['stored']:
                results['stored'] += 1
            elif result['reason'] == 'duplicate':
                results['skipped'] += 1
            else:
                results['errors'] += 1
        
        logger.info(f"✓ Batch storage: {results['stored']} stored, "
                   f"{results['skipped']} skipped, {results['errors']} errors")
        
        return results
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        vs_stats = self.vector_store.get_stats()
        
        return {
            'total_stored': self.stored_count,
            'total_in_db': vs_stats['total_articles'],
            'collection': vs_stats['collection_name']
        }