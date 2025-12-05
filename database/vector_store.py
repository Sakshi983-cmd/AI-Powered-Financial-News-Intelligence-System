"""
Vector Store for Semantic Search and Deduplication
Uses ChromaDB for efficient similarity search
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import numpy as np
from sklearn.cluster import DBSCAN
import hashlib
import json

class VectorStore:
    """Vector database for news articles"""
    
    def __init__(self, persist_directory: str = "chroma_db", 
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize vector store"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="financial_news",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding model (lightweight for laptop)
        self.embedder = SentenceTransformer(embedding_model)
        print(f"✅ Vector store initialized with {self.collection.count()} documents")
    
    def _generate_id(self, text: str) -> str:
        """Generate unique ID from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def add_article(self, article: Dict) -> str:
        """Add article to vector store"""
        article_id = article.get('id', self._generate_id(article['content']))
        
        # Create searchable text (title + content)
        search_text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # Generate embedding
        embedding = self.embedder.encode(search_text).tolist()
        
        # Store in ChromaDB
        self.collection.add(
            ids=[article_id],
            embeddings=[embedding],
            metadatas=[{
                'title': article.get('title', ''),
                'source': article.get('source', ''),
                'date': article.get('date', ''),
                'entities': json.dumps(article.get('entities', [])),
                'sentiment': article.get('sentiment', {}).get('compound', 0.0) if isinstance(article.get('sentiment'), dict) else 0.0
            }],
            documents=[article.get('content', '')]
        )
        
        return article_id
    
    def find_duplicates(self, article: Dict, threshold: float = 0.90) -> List[Dict]:
        """
        Find duplicate articles using semantic similarity
        TARGET: 95%+ accuracy
        """
        search_text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # Generate embedding
        query_embedding = self.embedder.encode(search_text).tolist()
        
        # Search for similar articles
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=10
        )
        
        duplicates = []
        if results['distances'] and results['distances'][0]:
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= threshold and results['ids'][0][i] != article.get('id'):
                    duplicates.append({
                        'id': results['ids'][0][i],
                        'similarity': similarity,
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i]
                    })
        
        return duplicates
    
    def cluster_articles(self, articles: List[Dict], eps: float = 0.15) -> Dict[int, List[str]]:
        """
        Cluster articles using DBSCAN for advanced deduplication
        Returns cluster_id -> [article_ids] mapping
        """
        if not articles:
            return {}
        
        # Generate embeddings for all articles
        texts = [f"{a.get('title', '')} {a.get('content', '')}" for a in articles]
        embeddings = self.embedder.encode(texts)
        
        # Cluster using DBSCAN
        clustering = DBSCAN(eps=eps, min_samples=2, metric='cosine')
        labels = clustering.fit_predict(embeddings)
        
        # Group by cluster
        clusters = {}
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(articles[idx].get('id', f'article_{idx}'))
        
        return clusters
    
    def semantic_search(self, query: str, top_k: int = 10, 
                       filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search articles by semantic similarity
        """
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Build where filter if provided
        where_filter = None
        if filters:
            where_conditions = []
            for key, value in filters.items():
                where_conditions.append({key: {"$eq": value}})
            
            if where_conditions:
                where_filter = {"$and": where_conditions} if len(where_conditions) > 1 else where_conditions[0]
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results
        search_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                search_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i]
                })
        
        return search_results
    
    def hybrid_search(self, query: str, entities: List[str] = None, 
                     top_k: int = 10) -> List[Dict]:
        """
        Hybrid search combining semantic + entity matching
        BETTER than simple semantic search!
        """
        # Semantic search
        semantic_results = self.semantic_search(query, top_k=top_k * 2)
        
        # Re-rank based on entity matches if provided
        if entities:
            for result in semantic_results:
                result_entities = json.loads(result['metadata'].get('entities', '[]'))
                
                # Calculate entity overlap score
                overlap = len(set(entities) & set(result_entities))
                entity_score = overlap / max(len(entities), 1)
                
                # Combine scores (70% semantic + 30% entity)
                result['combined_score'] = (0.7 * result['similarity']) + (0.3 * entity_score)
            
            # Re-sort by combined score
            semantic_results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        
        return semantic_results[:top_k]
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get article by ID"""
        results = self.collection.get(ids=[article_id])
        
        if results['ids']:
            return {
                'id': results['ids'][0],
                'content': results['documents'][0],
                'metadata': results['metadatas'][0]
            }
        
        return None
    
    def delete_article(self, article_id: str):
        """Delete article from vector store"""
        self.collection.delete(ids=[article_id])
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'total_articles': self.collection.count(),
            'collection_name': self.collection.name
        }
    
    def clear(self):
        """Clear all data (for testing)"""
        self.client.delete_collection(name="financial_news")
        self.collection = self.client.create_collection(
            name="financial_news",
            metadata={"hnsw:space": "cosine"}
        )