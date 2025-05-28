// src/pages/Home.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaSearch, FaUser, FaInfoCircle, FaSpinner } from "react-icons/fa";

import "../App.css";
import Sidebar from "../components/Sidebar";

function Home({ isLoggedIn, user }) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

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
        const res = await fetch(`http://localhost:8000/orcid/${term}/name`);
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const obj = await res.json();
        data = [{ orcid: term, full_name: obj.full_name }];
      } else {
        const res = await fetch(
          `http://localhost:8000/orcid/search/name?query=${encodeURIComponent(
            term
          )}&max_results=10`
        );
        if (!res.ok) throw new Error(`Status ${res.status}`);
        data = await res.json();
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
          <button onClick={() => navigate('/cadastro', { state: { isLogin: true } })}>Sign In</button>
          <button onClick={() => navigate('/cadastro', { state: { isLogin: false } })}>Sign Up</button>
        </nav>
      </header>

      <main className="home-main">
        {/* Sidebar positioned first in the flex container */}
        <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
        
        {/* Main content area */}
        <div className="content-area">
          {/* Busca */}
          <div className="search-wrapper">
            <input
              type="text"
              placeholder="Digite um ORCID ou nome de autor..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <FaSearch className="search-icon" />

            {/* Sugestões */}
            {(loading || results.length > 0 || error) && (
              <ul className="suggestions-list">
                {loading && (
                  <li className="suggestion-item loading">
                    <FaSpinner className="spin suggestion-icon" />
                    <span>Carregando...</span>
                  </li>
                )}
                {!loading && error && (
                  <li className="suggestion-item no-results">{error}</li>
                )}
                {!loading &&
                  !error &&
                  results.length === 0 &&
                  query.trim() !== "" && (
                    <li className="suggestion-item no-results">
                      Nenhum resultado encontrado
                    </li>
                  )}
                {!loading &&
                  !error &&
                  results.map((item) => (
                    <li
                      key={item.orcid}
                      className="suggestion-item"
                      onClick={() => navigate(`/dashboard/${item.orcid}`)}
                    >
                      <FaUser className="suggestion-icon" />
                      <div className="suggestion-content">
                        <span className="suggestion-name">{item.full_name}</span>
                        <span className="suggestion-subtitle">{item.orcid}</span>
                      </div>
                      <FaInfoCircle className="info-icon" />
                    </li>
                  ))}
              </ul>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default Home;