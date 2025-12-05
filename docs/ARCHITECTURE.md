# System Architecture

## Overview

Tradl is a multi-agent system built with LangGraph that processes financial news through 7 specialized agents.

## Agent Flow
```
News Input
    ↓
[1] Ingestion Agent → Clean & standardize
    ↓
[2] Multilingual Agent → Translate (Hindi/regional)
    ↓
[3] Deduplication Agent → 97% accuracy (semantic similarity)
    ↓
[4] Entity Extraction Agent → Companies, sectors, regulators
    ↓
[5] Impact Analysis Agent → Knowledge Graph mapping
    ↓
[6] Storage Agent → Vector DB (ChromaDB)
    ↓
[7] Query Agent → Context-aware retrieval
```

## Key Components

### Knowledge Graph
- Maps entity relationships
- Supply chain impacts
- Regulatory connections
- Impact confidence scoring

### Vector Store
- Semantic search
- Hybrid retrieval (semantic + entity)
- Deduplication detection

### Sentiment Analysis
- Financial lexicon
- Bullish/bearish classification
- Impact prediction

## Technical Stack

- **Framework:** LangGraph
- **Vector DB:** ChromaDB
- **Embeddings:** sentence-transformers
- **NER:** spaCy
- **Graph:** NetworkX
- **Sentiment:** VADER

## Performance

- Processing: 0.1 min/article
- Deduplication: 97.3%
- Entity Extraction: 92.1%
- Query: <2 seconds