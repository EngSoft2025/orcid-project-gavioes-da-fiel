// src/pages/Home.js
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../App.css";

function Home({ isLoggedIn, user }) {
  const navigate = useNavigate();
  const [view, setView] = useState("table");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);       // pode ser 1 ou vários
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Regex simples para ORCID no formato 0000-0000-0000-0000
  const orcidRegex = /^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$/;

  const handleSearch = async () => {
    const term = query.trim();
    if (!term) return;
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      let data;
      if (orcidRegex.test(term)) {
        // Se for ORCID, chama get_name e embrulha num array
        const res = await fetch(`http://localhost:8000/orcid/${term}/name`);
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const obj = await res.json(); // { full_name: "..." }
        data = [{ orcid: term, full_name: obj.full_name }];
      } else {
        // Senão, trata como nome e chama search/name
        const res = await fetch(
          `http://localhost:8000/orcid/search/name?query=${encodeURIComponent(
            term
          )}&max_results=10`
        );
        if (!res.ok) throw new Error(`Status ${res.status}`);
        data = await res.json(); // [ { orcid, full_name }, ... ]
      }
      setResults(data);
    } catch (err) {
      setError("Falha na busca: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <h2 className="logo">AbraoAbrao</h2>
        <nav className="nav-buttons">
          <button onClick={() => navigate("/cadastro")}>Sign In</button>
          <button onClick={() => navigate("/cadastro")}>Sign Up</button>
        </nav>
      </header>

      <main className="home-main">
        {/* ---------- Busca ---------- */}
        <div className="search-wrapper">
          <input
            type="text"
            placeholder="Digite um ORCID ou nome de autor..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch}>🔍</button>
        </div>

        {/* ---------- Filtros ---------- */}
        <section className="filters-section">
          <h3>Filtros</h3>
          {/* Dropdowns / checkboxes podem ir aqui */}
          <div className="view-toggle">
            <button
              className={view === "table" ? "active" : ""}
              onClick={() => setView("table")}
            >
              ☰
            </button>
            <button
              className={view === "grid" ? "active" : ""}
              onClick={() => setView("grid")}
            >
              ☐
            </button>
          </div>
        </section>

        {/* ---------- Resultados ---------- */}
        <section className="results-section">
          {loading && <p>Carregando...</p>}
          {error && <p className="error">{error}</p>}

          {results.length > 0 && (
            <>
              <h3>Resultados da busca</h3>
              {view === "table" ? (
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>ORCID</th>
                      <th>Nome completo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((item) => (
                      <tr key={item.orcid}>
                        <td>
                          <Link to={`/dashboard/${item.orcid}`}>
                            {item.orcid}
                          </Link>
                        </td>
                        <td>
                          <Link to={`/dashboard/${item.orcid}`}>
                            {item.full_name}
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="results-grid">
                  {results.map((item) => (
                    <Link
                      key={item.orcid}
                      to={`/author/${item.orcid}`}
                      className="card"
                    >
                      <div className="card-title">{item.full_name}</div>
                      <div className="card-subtitle">{item.orcid}</div>
                    </Link>
                  ))}
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default Home;
