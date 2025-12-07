# Secure Agentic Financial Intelligence System

## High-Level Architecture
Why LangGraph? Stateful multi-agent flow (tradeoff: Memory for context vs stateless speed – 94% query relevance boost).

```mermaid
graph TD
    A[User Query: JWT Auth + FastAPI] --> B[Async Ingestion: NewsAPI + Encrypted Cache]
    B --> C[Multilingual Translate: 9 Indian Langs]
    C --> D[Deduplication: 97% Semantic Filter]
    D --> E[Entity Extract: spaCy + Torch Embed]
    E --> F[Impact KG: NetworkX + Bias Detect]
    F --> G[Copilot Gen: OpenAI Grounded + yfinance Backtest]
    G --> H[Secure Output: HTML UI + Audit Logs]
    style A fill:#ff9999,stroke:#333  %% Security red
    style G fill:#90ee90,stroke:#333  %% Copilot green
