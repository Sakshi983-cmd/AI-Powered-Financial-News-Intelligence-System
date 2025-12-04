"""
Stock Impact Analysis Agent - Maps news to impacted stocks
Uses Knowledge Graph for intelligent impact prediction!
"""
from typing import Dict, List
from database.knowledge_graph import FinancialKnowledgeGraph
from models.sentiment import sentiment_analyzer
from utils.logger import logger

class ImpactAnalysisAgent:
    """
    Agent 4: Analyze which stocks are impacted by news
    This uses your KILLER FEATURE (Knowledge Graph)!
    """
    
    def __init__(self, knowledge_graph: FinancialKnowledgeGraph):
        self.kg = knowledge_graph
        self.sentiment_analyzer = sentiment_analyzer
    
    def process(self, article: Dict) -> Dict:
        """
        Analyze stock impact for article
        Returns article with impact analysis added
        """
        try:
            entities = article.get('entities', {})
            
            # Get sentiment first
            sentiment = self.sentiment_analyzer.analyze(
                f"{article['title']} {article['content']}"
            )
            article['sentiment'] = sentiment
            
            # Analyze impacts
            impacts = {
                'direct': [],      # Direct mentions
                'sector': [],      # Sector-wide impact
                'supply_chain': [], # Supply chain effects
                'overall_confidence': 0.0
            }
            
            # 1. Direct company impacts (confidence: 1.0)
            companies = entities.get('companies', [])
            for company in companies:
                # Try to find in knowledge graph
                if company in self.kg.graph:
                    impacts['direct'].append({
                        'entity': company,
                        'type': 'company',
                        'confidence': 1.0,
                        'sentiment': sentiment['label'],
                        'reasoning': f"Direct mention in article"
                    })
            
            # 2. Sector-wide impacts (confidence: 0.7-0.8)
            sectors = entities.get('sectors', [])
            for sector in sectors:
                if sector in self.kg.graph:
                    # Get all companies in this sector
                    sector_companies = self.kg.get_companies_in_sector(sector)
                    
                    for company in sector_companies:
                        impacts['sector'].append({
                            'entity': company,
                            'type': 'company',
                            'confidence': 0.75,
                            'sentiment': sentiment['label'],
                            'reasoning': f"Part of {sector} sector"
                        })
            
            # 3. Regulatory impacts (confidence: 0.6-0.7)
            regulators = entities.get('regulators', [])
            for regulator in regulators:
                if regulator in self.kg.graph:
                    # Find what this regulator affects
                    impacted_entities = self.kg.get_impacted_entities(regulator, max_depth=2)
                    
                    for entity, confidence in impacted_entities.items():
                        if self.kg.graph.nodes[entity].get('type') == 'company':
                            impacts['sector'].append({
                                'entity': entity,
                                'type': 'company',
                                'confidence': confidence * 0.65,
                                'sentiment': sentiment['label'],
                                'reasoning': f"Regulated by {regulator}"
                            })
            
            # 4. Supply chain impacts (BONUS FEATURE!)
            for sector in sectors:
                supply_impacts = self.kg.get_supply_chain_impact(sector)
                
                for impacted_sector, confidence in supply_impacts.items():
                    # Get companies in impacted sector
                    companies_list = self.kg.get_companies_in_sector(impacted_sector)
                    
                    for company in companies_list:
                        impacts['supply_chain'].append({
                            'entity': company,
                            'type': 'company',
                            'confidence': confidence * 0.5,
                            'sentiment': sentiment['label'],
                            'reasoning': f"Supply chain link: {sector} → {impacted_sector}"
                        })
            
            # Remove duplicates and calculate overall confidence
            impacts = self._consolidate_impacts(impacts)
            
            article['impact_analysis'] = impacts
            
            logger.info(f"✓ Impact analysis: {len(impacts['direct'])} direct, "
                       f"{len(impacts['sector'])} sector, "
                       f"{len(impacts['supply_chain'])} supply chain")
            
            return article
            
        except Exception as e:
            logger.error(f"Error in impact analysis: {e}")
            article['impact_analysis'] = {
                'direct': [], 'sector': [], 'supply_chain': [],
                'overall_confidence': 0.0
            }
            return article
    
    def _consolidate_impacts(self, impacts: Dict) -> Dict:
        """Remove duplicates and merge impacts"""
        seen = {}
        
        # Process all impact types
        for impact_type in ['direct', 'sector', 'supply_chain']:
            for impact in impacts[impact_type]:
                entity = impact['entity']
                
                if entity not in seen:
                    seen[entity] = impact
                else:
                    # Keep the higher confidence
                    if impact['confidence'] > seen[entity]['confidence']:
                        seen[entity] = impact
        
        # Reorganize back into categories
        result = {'direct': [], 'sector': [], 'supply_chain': [], 'overall_confidence': 0.0}
        
        for entity, impact in seen.items():
            if impact['confidence'] >= 0.9:
                result['direct'].append(impact)
            elif impact['confidence'] >= 0.5:
                result['sector'].append(impact)
            else:
                result['supply_chain'].append(impact)
        
        # Calculate overall confidence
        all_confidences = [imp['confidence'] for imp in seen.values()]
        result['overall_confidence'] = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        return result
    
    def explain_impact(self, article: Dict, entity: str) -> str:
        """
        Explain why an entity is impacted (EXPLAINABILITY FEATURE!)
        """
        impacts = article.get('impact_analysis', {})
        
        # Find the impact
        for impact_type in ['direct', 'sector', 'supply_chain']:
            for impact in impacts.get(impact_type, []):
                if impact['entity'] == entity:
                    # Get relationship path from KG
                    article_entities = article.get('entities', {}).get('companies', [])
                    
                    explanations = []
                    for source in article_entities:
                        if source in self.kg.graph and entity in self.kg.graph:
                            paths = self.kg.explain_relationship(source, entity)
                            explanations.extend(paths)
                    
                    if explanations:
                        return f"{impact['reasoning']}. Path: {explanations[0]}"
                    else:
                        return impact['reasoning']
        
        return "No direct impact found"