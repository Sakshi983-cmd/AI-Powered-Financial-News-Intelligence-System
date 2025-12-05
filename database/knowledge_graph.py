"""
Knowledge Graph Implementation - KILLER FEATURE for Rank 1
Maps relationships between companies, sectors, regulators, and impacts
"""
import networkx as nx
from typing import List, Dict, Set, Tuple
import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from collections import defaultdict

class FinancialKnowledgeGraph:
    """
    Knowledge Graph for financial entities and their relationships
    This is what will make you WIN!
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self._initialize_base_graph()
    
    def _initialize_base_graph(self):
        """Initialize with Indian financial market structure"""
        
        # Regulators
        self.graph.add_node("RBI", type="regulator", full_name="Reserve Bank of India")
        self.graph.add_node("SEBI", type="regulator", full_name="Securities and Exchange Board")
        
        # Sectors
        sectors = [
            "Banking", "IT", "Pharmaceuticals", "Auto", "Steel", 
            "Real Estate", "FMCG", "Telecom", "Energy", "Cement"
        ]
        for sector in sectors:
            self.graph.add_node(sector, type="sector")
        
        # Major Companies (sample - you'll add more)
        companies = {
            "HDFCBANK": ("HDFC Bank", "Banking"),
            "ICICIBANK": ("ICICI Bank", "Banking"),
            "AXISBANK": ("Axis Bank", "Banking"),
            "TCS": ("Tata Consultancy Services", "IT"),
            "INFY": ("Infosys", "IT"),
            "RELIANCE": ("Reliance Industries", "Energy"),
            "TATAMOTORS": ("Tata Motors", "Auto"),
            "MARUTI": ("Maruti Suzuki", "Auto"),
        }
        
        for symbol, (name, sector) in companies.items():
            self.graph.add_node(symbol, type="company", full_name=name)
            self.graph.add_edge(symbol, sector, relationship="PART_OF")
        
        # Regulatory relationships
        self.graph.add_edge("RBI", "Banking", relationship="REGULATES")
        self.graph.add_edge("SEBI", "Banking", relationship="OVERSEES")
        self.graph.add_edge("SEBI", "IT", relationship="OVERSEES")
        
        # Supply chain relationships (IMPORTANT for bonus!)
        self.graph.add_edge("Auto", "Steel", relationship="DEPENDS_ON")
        self.graph.add_edge("Real Estate", "Cement", relationship="DEPENDS_ON")
        self.graph.add_edge("Real Estate", "Steel", relationship="DEPENDS_ON")
        
        # Economic relationships
        self.graph.add_edge("RBI", "Interest Rates", relationship="CONTROLS")
        self.graph.add_edge("Interest Rates", "Banking", relationship="AFFECTS")
        self.graph.add_edge("Interest Rates", "Real Estate", relationship="AFFECTS")
    
    def add_company(self, symbol: str, name: str, sector: str):
        """Add a company to the knowledge graph"""
        self.graph.add_node(symbol, type="company", full_name=name)
        if self.graph.has_node(sector):
            self.graph.add_edge(symbol, sector, relationship="PART_OF")
    
    def add_relationship(self, source: str, target: str, relationship: str):
        """Add custom relationship"""
        self.graph.add_edge(source, target, relationship=relationship)
    
    def get_impacted_entities(self, entity: str, max_depth: int = 3) -> Dict[str, float]:
        """
        Get all entities impacted by the given entity with confidence scores
        This is THE KEY FEATURE!
        """
        if entity not in self.graph:
            return {}
        
        impacted = {}
        
        # BFS to find all connected entities
        for target in nx.descendants(self.graph, entity):
            try:
                path_length = nx.shortest_path_length(self.graph, entity, target)
                if path_length <= max_depth:
                    # Confidence decreases with distance
                    confidence = 1.0 / (path_length + 1)
                    impacted[target] = confidence
            except nx.NetworkXNoPath:
                continue
        
        # Also check reverse relationships (what impacts this entity)
        for source in nx.ancestors(self.graph, entity):
            try:
                path_length = nx.shortest_path_length(self.graph, source, entity)
                if path_length <= max_depth:
                    confidence = 0.7 / (path_length + 1)  # Slightly lower for reverse
                    impacted[source] = confidence
            except nx.NetworkXNoPath:
                continue
        
        return impacted
    
    def get_companies_in_sector(self, sector: str) -> List[str]:
        """Get all companies in a sector"""
        if sector not in self.graph:
            return []
        
        companies = []
        for node in self.graph.predecessors(sector):
            if self.graph.nodes[node].get('type') == 'company':
                companies.append(node)
        
        return companies
    
    def explain_relationship(self, source: str, target: str) -> List[str]:
        """
        Explain why two entities are related (for explainability feature)
        THIS MAKES DEMO IMPRESSIVE!
        """
        if source not in self.graph or target not in self.graph:
            return []
        
        try:
            paths = list(nx.all_simple_paths(self.graph, source, target, cutoff=3))
            
            explanations = []
            for path in paths[:3]:  # Top 3 paths
                explanation_parts = []
                for i in range(len(path) - 1):
                    rel = self.graph.edges[path[i], path[i+1]].get('relationship', 'related to')
                    explanation_parts.append(f"{path[i]} {rel} {path[i+1]}")
                
                explanations.append(" → ".join(explanation_parts))
            
            return explanations
        
        except nx.NetworkXNoPath:
            return []
    
    def get_supply_chain_impact(self, sector: str) -> Dict[str, float]:
        """
        Get supply chain impacts (solves bonus challenge!)
        """
        impacts = {}
        
        # Downstream impacts (who depends on this sector)
        for node in self.graph.nodes():
            if self.graph.has_edge(node, sector):
                rel = self.graph.edges[node, sector].get('relationship')
                if rel == "DEPENDS_ON":
                    impacts[node] = 0.7  # High impact
        
        # Upstream impacts (what this sector depends on)
        for node in self.graph.successors(sector):
            rel = self.graph.edges[sector, node].get('relationship')
            if rel == "DEPENDS_ON":
                impacts[node] = 0.6  # Medium impact
        
        return impacts
    
    def visualize_impact(self, entity: str, output_path: str = "demo/impact_graph.png"):
        """
        Visualize impact network (for demo!)
        """
        impacted = self.get_impacted_entities(entity)
        
        # Create subgraph
        nodes_to_show = [entity] + list(impacted.keys())[:10]
        subgraph = self.graph.subgraph(nodes_to_show)
        
        # Layout
        pos = nx.spring_layout(subgraph, k=2, iterations=50)
        
        # Draw
        plt.figure(figsize=(12, 8))
        
        # Color nodes by type
        colors = {
            "company": "#3498db",
            "sector": "#e74c3c",
            "regulator": "#2ecc71"
        }
        
        node_colors = [colors.get(subgraph.nodes[n].get('type', 'company'), '#95a5a6') 
                       for n in subgraph.nodes()]
        
        nx.draw(subgraph, pos, 
                node_color=node_colors,
                node_size=3000,
                with_labels=True,
                font_size=10,
                font_weight='bold',
                arrows=True,
                edge_color='#7f8c8d',
                width=2)
        
        plt.title(f"Impact Network: {entity}", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def get_stats(self) -> Dict:
        """Get graph statistics"""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "companies": sum(1 for n in self.graph.nodes() 
                           if self.graph.nodes[n].get('type') == 'company'),
            "sectors": sum(1 for n in self.graph.nodes() 
                         if self.graph.nodes[n].get('type') == 'sector'),
            "regulators": sum(1 for n in self.graph.nodes() 
                            if self.graph.nodes[n].get('type') == 'regulator')
        }