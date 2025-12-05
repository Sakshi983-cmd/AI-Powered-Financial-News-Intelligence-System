"""
Simple CLI Demo - Easy to run!
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_orchestrator import TradlOrchestrator
from rich.console import Console
from rich.panel import Panel
import json

console = Console()

def main():
    console.print("\n[bold cyan]🚀 TRADL NEWS INTELLIGENCE DEMO[/bold cyan]\n")
    
    # Initialize
    console.print("Initializing system...")
    orchestrator = TradlOrchestrator()
    console.print("[green]✓ System ready![/green]\n")
    
    # Load sample data
    try:
        with open('data/news_articles.json', 'r') as f:
            articles = json.load(f)[:5]  # First 5 only
    except:
        console.print("[red]Error loading data![/red]")
        return
    
    # Demo 1: Process News
    console.print("[bold yellow]📰 DEMO 1: Processing News[/bold yellow]")
    console.print(f"Processing {len(articles)} articles...\n")
    
    result = orchestrator.process_news(articles)
    
    console.print(f"[green]✓ Processed: {result['processed']}[/green]")
    console.print(f"[green]✓ Stored: {result['stored']}[/green]")
    console.print(f"[yellow]⊘ Duplicates: {result['duplicates']}[/yellow]\n")
    
    # Demo 2: Query
    console.print("[bold yellow]🔍 DEMO 2: Intelligent Query[/bold yellow]")
    query = "RBI policy"
    console.print(f"Query: '{query}'\n")
    
    query_result = orchestrator.query_news(query, top_k=3, explain=True)
    
    console.print(f"[green]Found {query_result['total_found']} articles[/green]\n")
    
    for i, article in enumerate(query_result['results'], 1):
        console.print(Panel(
            f"[bold]{article['metadata']['title']}[/bold]\n"
            f"Score: {article['final_score']:.2f}\n"
            f"Why: {article.get('explanation', 'N/A')}",
            title=f"Result {i}",
            border_style="cyan"
        ))
    
    # Demo 3: Stats
    console.print("\n[bold yellow]📊 SYSTEM STATS[/bold yellow]")
    stats = orchestrator.get_system_stats()
    
    console.print(f"Total Articles: {stats['vector_store']['total_articles']}")
    console.print(f"Knowledge Graph Nodes: {stats['knowledge_graph']['total_nodes']}")
    console.print(f"Companies: {stats['knowledge_graph']['companies']}")
    console.print(f"Sectors: {stats['knowledge_graph']['sectors']}\n")
    
    console.print("[bold green]✓ Demo Complete![/bold green]")

if __name__ == "__main__":
    main()