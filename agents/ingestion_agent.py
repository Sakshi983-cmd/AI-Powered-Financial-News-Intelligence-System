"""
News Ingestion Agent - Cleans and standardizes raw news
"""
from typing import Dict, List
import re
from datetime import datetime
from utils.logger import logger

class NewsIngestionAgent:
    """
    Agent 1: Ingests and standardizes raw news articles
    """
    
    def __init__(self):
        self.processed_count = 0
    
    def process(self, raw_article: Dict) -> Dict:
        """
        Process raw article into standardized format
        """
        try:
            processed = {
                'id': raw_article.get('id', f"article_{self.processed_count}"),
                'title': self._clean_text(raw_article.get('title', '')),
                'content': self._clean_text(raw_article.get('content', '')),
                'source': raw_article.get('source', 'Unknown'),
                'date': self._parse_date(raw_article.get('date', '')),
                'url': raw_article.get('url', ''),
                'raw_text': raw_article.get('content', ''),
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'word_count': len(raw_article.get('content', '').split())
                }
            }
            
            self.processed_count += 1
            logger.info(f"✓ Ingested article: {processed['title'][:50]}...")
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\'\"]', '', text)
        
        return text.strip()
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat()
                except:
                    continue
            
            # If parsing fails, return current date
            return datetime.now().isoformat()
            
        except:
            return datetime.now().isoformat()
    
    def batch_process(self, articles: List[Dict]) -> List[Dict]:
        """Process multiple articles"""
        processed = []
        for article in articles:
            result = self.process(article)
            if result:
                processed.append(result)
        
        logger.info(f"✓ Batch processed {len(processed)}/{len(articles)} articles")
        return processed