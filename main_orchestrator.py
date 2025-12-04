"""
LangGraph Multi-Agent Orchestrator - MAIN SYSTEM
Coordinates all 7 agents for news processing
"""
from typing import Dict, List, TypedDict
from langgraph.graph import StateGraph, END
from agents.ingestion_agent import NewsIngestionAgent
from agents.deduplication_agent import DeduplicationAgent
from agents.entity_extraction_agent import EntityExtractionAgent
from agents.impact_agent import ImpactAnalysisAgent
from agents.storage_agent import StorageAgent
from agents.query_agent import QueryProcessingAgent
from agents.multilingual_agent import MultilingualAgent
from database.vector_store import VectorStore
from database.knowledge_graph import FinancialKnowledgeGraph
from utils.logger import logger

# Define State
class NewsProcessingState(TypedDict):
    """State that flows through the agent graph"""
    raw_articles: List[Dict]
    processed_articles: List[Dict]
    duplicate_flags: List[bool]
    stored_articles: List[str]
    stats: Dict
    errors: List[str]

class TradlOrchestrator:
    """
    Main orchestrator using LangGraph
    This coordinates all 7 agents!
    """
    
    def __init__(self):
        # Initialize components
        self.vector_store = VectorStore()
        self.knowledge_graph = FinancialKnowledgeGraph()
        
        # Initialize agents
        self.ingestion_agent = NewsIngestionAgent()
        self.multilingual_agent = MultilingualAgent()
        self.deduplication_agent = DeduplicationAgent(self.vector_store)
        self.entity_agent = EntityExtractionAgent()
        self.impact_agent = ImpactAnalysisAgent(self.knowledge_graph)
        self.storage_agent = StorageAgent(self.vector_store)
        self.query_agent = QueryProcessingAgent(self.vector_store, self.knowledge_graph)
        
        # Build LangGraph
        self.graph = self._build_graph()
        
        logger.info("✓ Tradl Orchestrator initialized with 7 agents")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(NewsProcessingState)
        
        # Add nodes (agents)
        workflow.add_node("ingest", self._ingest_node)
        workflow.add_node("translate", self._translate_node)
        workflow.add_node("deduplicate", self._deduplicate_node)
        workflow.add_node("extract_entities", self._entity_node)
        workflow.add_node("analyze_impact", self._impact_node)
        workflow.add_node("store", self._storage_node)
        
        # Define flow
        workflow.set_entry_point("ingest")
        workflow.add_edge("ingest", "translate")
        workflow.add_edge("translate", "deduplicate")
        workflow.add_edge("deduplicate", "extract_entities")
        workflow.add_edge("extract_entities", "analyze_impact")
        workflow.add_edge("analyze_impact", "store")
        workflow.add_edge("store", END)
        
        return workflow.compile()
    
    # Node functions
    def _ingest_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Node 1: Ingest raw articles"""
        logger.info("→ Running Ingestion Agent")
        processed = self.ingestion_agent.batch_process(state['raw_articles'])
        state['processed_articles'] = processed
        return state
    
    def _translate_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Node 2: Translate multilingual articles"""
        logger.info("→ Running Multilingual Agent")
        processed = []
        for article in state['processed_articles']:
            processed_article = self.multilingual_agent.process(article)
            processed.append(processed_article)
        state['processed_articles'] = processed
        return state
    
    def _deduplicate_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Node 3: Check for duplicates"""
        logger.info("→ Running Deduplication Agent")
        duplicate_flags = []
        for article in state['processed_articles']:
            result = self.deduplication_agent.process(article)
            duplicate_flags.append(result['is_duplicate'])
        state['duplicate_flags'] = duplicate_flags
        unique_count = sum(1 for f in duplicate_flags if not f)
        dup_count = len(duplicate_flags) - unique_count
        logger.info(f"  Found {unique_count} unique, {dup_count} duplicates")
        return state
    
    def _entity_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Node 4: Extract entities"""
        logger.info("→ Running Entity Extraction Agent")
        processed = []
        for article in state['processed_articles']:
            processed_article = self.entity_agent.process(article)
            processed.append(processed_article)
        state['processed_articles'] = processed
        return state
    
    def _impact_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Node 5: Analyze impacts"""
        logger.info("→ Running Impact Analysis Agent")
        processed = []
        for article in state['processed_articles']:
            processed_article = self.impact_agent.process(article)
            processed.append(processed_article)
        state['processed_articles'] = processed
        return state
    
    def _storage_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Node 6: Store articles"""
        logger.info("→ Running Storage Agent")
        results = self.storage_agent.batch_store(
            state['processed_articles'],
            state['duplicate_flags']
        )
        state['stats'] = results
        return state
    
    # Public methods
    def process_news(self, articles: List[Dict]) -> Dict:
        """Process a batch of news articles through the pipeline"""
        logger.info(f"🚀 Starting news processing: {len(articles)} articles")
        
        # Initialize state
        initial_state = NewsProcessingState(
            raw_articles=articles,
            processed_articles=[],
            duplicate_flags=[],
            stored_articles=[],
            stats={},
            errors=[]
        )
        
        # Run through graph
        final_state = self.graph.invoke(initial_state)
        
        logger.info(f"✓ Processing complete: {final_state['stats']}")
        
        return {
            'processed': len(final_state['processed_articles']),
            'stored': final_state['stats'].get('stored', 0),
            'duplicates': final_state['stats'].get('skipped', 0),
            'errors': final_state['stats'].get('errors', 0),
            'articles': final_state['processed_articles']
        }
    
    def query_news(self, query: str, top_k: int = 10, explain: bool = True) -> Dict:
        """Query the news database"""
        return self.query_agent.process(query, top_k, explain)
    
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        return {
            'vector_store': self.vector_store.get_stats(),
            'knowledge_graph': self.knowledge_graph.get_stats(),
            'ingestion': {
                'processed': self.ingestion_agent.processed_count
            },
            'storage': self.storage_agent.get_stats()
        }

# Main execution
if __name__ == "__main__":
    orchestrator = TradlOrchestrator()
    
    test_articles = [
        {
            'title': 'RBI increases repo rate by 25 basis points',
            'content': 'Reserve Bank of India raised the repo rate to 6.75% citing inflation concerns',
            'source': 'Economic Times',
            'date': '2024-12-01'
        },
        {
            'title': 'HDFC Bank announces dividend',
            'content': 'HDFC Bank declared 15% dividend and approved stock buyback',
            'source': 'MoneyControl',
            'date': '2024-12-01'
        }
    ]
    
    result = orchestrator.process_news(test_articles)
    print(f"\nProcessed: {result['processed']}, Stored: {result['stored']}, Duplicates: {result['duplicates']}")
