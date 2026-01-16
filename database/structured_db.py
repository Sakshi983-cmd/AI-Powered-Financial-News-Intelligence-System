"""
Structured Database - SQLite for metadata storage
"""
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
import json

class StructuredDB:
    """SQLite database for structured data"""
    
    def __init__(self, db_path: str = "tradl.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source TEXT,
                date TEXT,
                detected_language TEXT,
                sentiment_label TEXT,
                sentiment_score REAL,
                processed_at TEXT,
                is_duplicate INTEGER DEFAULT 0,
                duplicate_of TEXT
            )
        """)
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT,
                entity_type TEXT,
                entity_name TEXT,
                confidence REAL DEFAULT 1.0,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)
        
        # Impacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS impacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT,
                entity TEXT,
                impact_type TEXT,
                confidence REAL,
                reasoning TEXT,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)
        
        self.conn.commit()
    
    def insert_article(self, article: Dict) -> bool:
        """Insert article metadata"""
        try:
            cursor = self.conn.cursor()
            
            sentiment = article.get('sentiment', {})
            
            cursor.execute("""
                INSERT OR REPLACE INTO articles 
                (id, title, source, date, detected_language, 
                 sentiment_label, sentiment_score, processed_at, is_duplicate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.get('id'),
                article.get('title'),
                article.get('source'),
                article.get('date'),
                article.get('detected_language', 'en'),
                sentiment.get('label', 'neutral') if isinstance(sentiment, dict) else 'neutral',
                sentiment.get('compound', 0.0) if isinstance(sentiment, dict) else 0.0,
                datetime.now().isoformat(),
                0
            ))
            
            # Insert entities
            entities = article.get('entities', {})
            entity_data = []
            article_id = article.get('id')

            for entity_type, entity_list in entities.items():
                if isinstance(entity_list, list):
                    for entity_name in entity_list:
                        entity_data.append((article_id, entity_type, entity_name))

            if entity_data:
                cursor.executemany("""
                    INSERT INTO entities (article_id, entity_type, entity_name)
                    VALUES (?, ?, ?)
                """, entity_data)
            
            self.conn.commit()
            return True
        
        except Exception as e:
            print(f"Error inserting article: {e}")
            return False
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get article by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def search_by_entity(self, entity_name: str) -> List[Dict]:
        """Search articles by entity"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT a.* FROM articles a
            JOIN entities e ON a.id = e.article_id
            WHERE e.entity_name LIKE ?
        """, (f"%{entity_name}%",))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_articles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM articles WHERE is_duplicate = 1")
        duplicates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT entity_name) FROM entities")
        unique_entities = cursor.fetchone()[0]
        
        return {
            'total_articles': total_articles,
            'duplicates': duplicates,
            'unique_articles': total_articles - duplicates,
            'unique_entities': unique_entities
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    db = StructuredDB()
    stats = db.get_stats()
    print(f"Database Stats: {stats}")