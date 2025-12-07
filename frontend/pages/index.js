// pages/index.js
// Custom UX: Pre-filled HDFC query, smooth transitions, error toast (no ugly popups), mobile-responsive.
// Ties to your /api/copilot (FastAPI backend) – Vercel proxy handles.
import { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState("Generate RSI strategy for volatile markets");  // Pre-load (user delight)
  const [ticker, setTicker] = useState("HDFC.NS");
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const askCopilot = async () => {
    if (!query.trim() || !ticker.trim()) {
      setError('Query & ticker required!');  // UX: Inline error
      setTimeout(() => setError(''), 3000);  // Auto-hide toast
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`/api/copilot?q=${encodeURIComponent(query)}&ticker=${encodeURIComponent(ticker)}`);  // Backend tie
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setResponse(data.response || 'No response – Check logs?');
    } catch (err) {
      setError(`Error: ${err.message}`);  // Graceful fail
      setTimeout(() => setError(''), 5000);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-finance-dark text-white flex flex-col items-center justify-center p-4">
      <style jsx global>{`
        @tailwind base;
        @tailwind components;
        @tailwind utilities;
      `}</style>
      <div className="max-w-2xl w-full space-y-6">
        <h1 className="text-4xl font-bold text-center bg-gradient-to-r from-accent-green to-blue-400 bg-clip-text text-transparent animate-pulse">
          Secure Financial Copilot
        </h1>
        <p className="text-center text-gray-300">Grounded strategies for Indian markets – Try HDFC pre-load!</p>
        
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., 'Bias check for RBI policy'"
          className="w-full p-4 bg-gray-800 border border-gray-600 rounded-lg focus:border-accent-green focus:outline-none transition-all duration-300"
        />
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="e.g., HDFC.NS"
          className="w-full p-4 bg-gray-800 border border-gray-600 rounded-lg focus:border-accent-green focus:outline-none transition-all duration-300"
        />
        <button
          onClick={askCopilot}
          disabled={loading}
          className="w-full p-4 bg-accent-green text-black font-bold rounded-lg hover:bg-green-500 transition-all duration-300 disabled:opacity-50 transform hover:scale-105"
        >
          {loading ? 'Agents Computing... 🚀' : 'Ask Copilot'}
        </button>
        
        {error && (
          <div className="p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-300 animate-bounce">
            {error}
          </div>
        )}
        
        {loading && <div className="text-center text-accent-green animate-pulse">Secure LangGraph agents at work...</div>}
        
        {response && (
          <div className="p-6 bg-gray-800 border border-gray-600 rounded-lg whitespace-pre-wrap text-left font-mono text-sm leading-relaxed transition-all duration-500 opacity-0 animate-fade-in">
            {response}
          </div>
        )}
      </div>
    </div>
  );
}
