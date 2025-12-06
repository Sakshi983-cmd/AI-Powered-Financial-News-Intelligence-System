# Secure Agentic Architecture

```mermaid
graph TD
    A[User → JWT Auth] --> B[FastAPI Gateway]
    B --> C[Async Ingestion + Encrypted Cache]
    C --> D[7 LangGraph Agents]
    D --> E[Financial Copilot + yfinance Backtest]
    E --> F[HTML Dashboard + Audit Logs]

