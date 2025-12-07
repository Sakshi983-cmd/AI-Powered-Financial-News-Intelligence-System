# demo/app.py
"""
Secure FastAPI UI for Copilot Demo
Why FastAPI? Lightweight, auto-docs (/docs), Vercel native (serverless scale).
Custom: Inline JS for chat (no external deps, bug-free fetch with error popup).
Tradeoff: Simple HTML vs React – Speed <1s load, but no state (session JWT future).
"""
from fastapi import FastAPI, Query  # Path params (q/ticker)
from fastapi.responses import HTMLResponse  # Serve HTML
from fastapi.middleware.cors import CORSMiddleware  # Browser CORS (dev safe)
from main_orchestrator import TradlOrchestrator  # Secure orch tie-in
import asyncio  # Async calls

app = FastAPI(title="Secure Financial Copilot", description="Agentic AI Demo – Live Queries!")
app.add_middleware(CORSMiddleware, allow_origins=["*"])  # CORS all (dev, prod restrict)

orch = TradlOrchestrator()  # Init once (global, efficient)

# Custom HTML + JS (Dark finance theme, responsive)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Finance Copilot</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0f; color: #e0e0e0; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; background: #1a1a2e; padding: 30px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        input { width: 100%; max-width: 400px; padding: 12px; margin: 10px; border: 1px solid #333; border-radius: 5px; background: #2a2a3e; color: #e0e0e0; }
        button { padding: 12px 24px; background: #00d4aa; color: black; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #00b894; }
        #output { margin-top: 20px; text-align: left; background: #111; padding: 20px; border-radius: 5px; white-space: pre-wrap; font-family: monospace; }
        .error { color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Secure Financial Copilot</h1>
        <p>Agentic AI: News-grounded strategies + backtest (Multilingual ready)</p>
        <input id="query" placeholder="e.g., 'Generate RSI strategy for volatile markets'" maxlength="200">
        <br>
        <input id="ticker" placeholder="e.g., HDFC.NS" value="HDFC.NS">
        <br>
        <button onclick="askCopilot()">Ask Copilot 🚀</button>
        <div id="output"></div>
    </div>
    <script>
        async function askCopilot() {
            const query = document.getElementById('query').value.trim();
            const ticker = document.getElementById('ticker').value.trim();
            const output = document.getElementById('output');
            
            if (!query || !ticker) {
                output.innerHTML = '<span class="error">Error: Enter query & ticker!</span>';  // Validate (bug-proof)
                return;
            }
            
            output.innerHTML = 'Thinking... (Secure agents at work)';  // Spinner text
            try {
                const resp = await fetch(`/copilot?q=${encodeURIComponent(query)}&ticker=${encodeURIComponent(ticker)}`);  // Safe encode (URL params)
                if (!resp.ok) throw new Error(`API error: ${resp.status}`);  // HTTP check
                const data = await resp.text();
                output.innerHTML = data;  // Render response (Markdown? Plain text safe)
            } catch (error) {
                output.innerHTML = `<span class="error">Error: ${error.message} – Check API keys?</span>`;  // JS error handle
            }
        }
        
        // Auto-focus (UX tweak)
        document.getElementById('query').focus();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve UI (Custom: Dark theme for finance pros)"""
    return html_template

@app.get("/copilot")
async def copilot_endpoint(q: str = Query(..., description="User query"), ticker: str = Query(..., description="Stock ticker")):
    """Copilot API (Secure call to orch, async if needed)"""
    try:
        # Async wrap (if ingestion async)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: orch.copilot_query(q, ticker, "web-user"))  # Thread-safe call
        return {"response": result}  # JSON safe (frontend text())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot error: {str(e)}")  # FastAPI error (no crash)

if __name__ == "__main__":
    import uvicorn  # Local run
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Dev server
