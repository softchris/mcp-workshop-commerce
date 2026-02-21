import { useState, useEffect } from 'react';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { createMcpClient } from './mcp-client';
import { ToolUI } from './ToolUI';
import './App.css';

function App() {
  const [client, setClient] = useState<Client | null>(null);
  const [tools, setTools] = useState<any[]>([]);
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [toolInput, setToolInput] = useState<Record<string, unknown>>({});
  const [error, setError] = useState<string | null>(null);

  // Connect to MCP server on mount
  useEffect(() => {
    const connect = async () => {
      try {
        // Replace with your MCP server URL
        const mcpClient = await createMcpClient('http://localhost:8000/mcp');
        setClient(mcpClient);

        // List available tools
        const toolsResult = await mcpClient.listTools({});
        setTools(toolsResult.tools);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    };

    connect();
  }, []);

  // Filter tools that have UI content
  const toolsWithUI = tools.filter((tool) =>
    (tool as any)._meta?.ui?.isUITool || (tool as any)._meta?.ui?.resourceUri
  );

  const categories = [
    { title: 'New Arrivals', note: 'Fresh drops for the season' },
    { title: 'Everyday Essentials', note: 'Core pieces that go anywhere' },
    { title: 'Studio & Home', note: 'Objects for a calm workspace' },
    { title: 'Limited Editions', note: 'Small-batch collaborations' },
  ];

  const featured = [
    { name: 'Harbor Knit Throw', price: '$68', desc: 'Cotton blend, cloud-soft texture.' },
    { name: 'Dune Leather Tote', price: '$189', desc: 'Structured carryall with brass trim.' },
    { name: 'Sienna Ceramic Set', price: '$72', desc: 'Hand-glazed, each piece unique.' },
    { name: 'Marin Linen Shirt', price: '$94', desc: 'Relaxed fit, washed linen finish.' },
    { name: 'Atlas Desk Lamp', price: '$128', desc: 'Warm glow, matte brass hardware.' },
    { name: 'Ember Travel Mug', price: '$36', desc: 'Double-wall ceramic, keeps heat.' },
  ];


  if (error) {
    return <div className="state state-error">Error: {error}</div>;
  }

  if (!client) {
    return <div className="state">Connecting to storefront...</div>;
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <span className="brand-mark">Marrow</span>
          <span className="brand-note">Curated goods for slow mornings</span>
        </div>
        <nav className="nav">
          <a href="#new">New</a>
          <a href="#home">Home</a>
          <a href="#studio">Studio</a>
          <a href="#tools">Live Tools</a>
        </nav>
        <button className="ghost">Sign in</button>
      </header>

      <section className="hero" id="new">
        <div className="hero-copy">
          <span className="pill">Spring Collection 2026</span>
          <h1>Calm, crafted essentials for modern living.</h1>
          <p>
            Thoughtful apparel, homeware, and desk objects designed to feel good every day.
            Built with natural textures and warm tones.
          </p>
          <div className="hero-actions">
            <button className="primary">Shop new arrivals</button>
            <button className="ghost">View lookbook</button>
          </div>
        </div>
        <div className="hero-card">
          <div className="hero-card__label">Featured drop</div>
          <div className="hero-card__title">Stonewashed linen sets</div>
          <div className="hero-card__detail">Available in clay, dune, and seafoam.</div>
          <div className="hero-card__price">From $84</div>
          <button className="ghost">Explore colors</button>
        </div>
      </section>

      <section className="section" id="home">
        <div className="section-head">
          <h2>Shop by mood</h2>
          <p>Small collections designed for focus, rest, and ritual.</p>
        </div>
        <div className="category-grid">
          {categories.map((item) => (
            <div className="category-card" key={item.title}>
              <h3>{item.title}</h3>
              <p>{item.note}</p>
              <button className="ghost">Browse</button>
            </div>
          ))}
        </div>
      </section>

      <section className="section" id="studio">
        <div className="section-head">
          <h2>Featured essentials</h2>
          <p>Best sellers that balance craft, comfort, and utility.</p>
        </div>
        <div className="product-grid">
          {featured.map((item) => (
            <div className="product-card" key={item.name}>
              <div className="product-card__swatch" />
              <div className="product-card__body">
                <div>
                  <h3>{item.name}</h3>
                  <p>{item.desc}</p>
                </div>
                <div className="product-card__meta">
                  <span className="price">{item.price}</span>
                  <button className="ghost">Add to bag</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="section tools" id="tools">
        <div className="section-head">
          <h2>Live tools & demos</h2>
          <p>Interactive storefront widgets powered by MCP tools.</p>
        </div>
        <div className="tools-shell">
          <div className="tools-list">
            <h3>Available tools</h3>
            {toolsWithUI.length === 0 ? (
              <p className="muted">No tools with UI found. Check your server metadata.</p>
            ) : (
              <div className="tool-chips">
                {toolsWithUI.map((tool) => (
                  <button
                    key={tool.name}
                    className={`tool-chip ${selectedTool === tool.name ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedTool(tool.name);
                      setToolInput({ query: 'Hello from client!' });
                    }}
                  >
                    <span>{tool.name}</span>
                    <small>{tool.description}</small>
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="tools-panel">
            {selectedTool && client ? (
              <>
                <div className="tools-panel__header">
                  <h3>{selectedTool}</h3>
                  <span className="pill soft">Live preview</span>
                </div>
                <ToolUI client={client} toolName={selectedTool} toolInput={toolInput} />
              </>
            ) : (
              <div className="tools-empty">
                <h3>Select a tool to preview</h3>
                <p>Use the list to explore UI-driven experiences.</p>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;