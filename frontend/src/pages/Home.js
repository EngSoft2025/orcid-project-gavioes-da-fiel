import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import {
  FaSearch,
  FaUser,
  FaBook,
  FaQuoteRight,
  FaInfoCircle,
  FaSpinner,
  FaMoon,
  FaSun,
  FaChartBar,
} from "react-icons/fa";
import { FaUsers } from "react-icons/fa6";

export default function Home() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    document.body.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode((prev) => !prev);
  };

  const orcidRegex = /^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$/;

  const handleSearch = async (term) => {
    const searchTerm = query.trim();
    if (!searchTerm) return;

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      let data;
      if (orcidRegex.test(searchTerm)) {
        const res = await fetch(
          `http://localhost:8000/orcid/${searchTerm}/name`
        );
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const obj = await res.json();
        data = [{ orcid: searchTerm, full_name: obj.full_name }];
      } else {
        const res = await fetch(
          `http://localhost:8000/orcid/search/name?query=${encodeURIComponent(
            searchTerm
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

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (query.length > 2) {
        handleSearch(query);
      } else {
        setResults([]);
      }
    }, 400);

    return () => clearTimeout(delayDebounce);
  }, [query]);

  return (
    <div>
      <header className="home-header">
        <div className="logo">
          {" "}
          <img
            src="../img/logo.png"
            alt="Logo da Plataforma"
            className="logo-img"
          />
        </div>
        <div className="header-controls">
          <button className="theme-toggle" onClick={toggleDarkMode}>
            {darkMode ? <FaSun /> : <FaMoon />}
          </button>
        </div>
      </header>

      <div className="home-main">
        <section className="hero-section">
          <h1 className="hero-title">
            <span className="highlight">Descubra o futuro</span>
            {"\n"}da pesquisa acadêmica
          </h1>
          <p className="hero-subtitle">
            Conecte-se com pesquisadores, explore publicações e acompanhe
            métricas em uma plataforma moderna e intuitiva.
          </p>
          {/* Busca */}
          <div className="search-wrapper">
            <FaSearch className="search-icon" />
            <input
              type="text"
              placeholder="Digite um ORCID ou nome de autor..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button className="search-button" onClick={handleSearch}>
              {" "}
              Buscar
            </button>
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
                        <span className="suggestion-name">
                          {item.full_name}
                        </span>
                        <span className="suggestion-subtitle">
                          {item.orcid}
                        </span>
                      </div>
                      <FaInfoCircle className="info-icon" />
                    </li>
                  ))}
              </ul>
            )}
          </div>
        </section>
        <section className="stats-section">
          <div className="stat-card">
            <FaUsers className="stat-icon" />
            <h3>50.000+</h3>
            <p>Pesquisadores Ativos</p>
          </div>
          <div className="stat-card">
            <FaBook className="stat-icon" />
            <h3>2.5 milhões+</h3>
            <p>Publicações</p>
          </div>
          <div className="stat-card">
            <FaQuoteRight className="stat-icon" />
            <h3>15 milhões+</h3>
            <p>Citações Globais</p>
          </div>
        </section>
        <section className="benefits-section">
          <h2 className="benefits-title">Por que escolher nossa plataforma?</h2>
          <div className="benefits-grid">
            <div className="benefit-box blue">
              <div className="benefit-icon blue">
                <FaSearch />
              </div>
              <h3>Descoberta Inteligente</h3>
              <p>
                Algoritmos de pesquisa avançada ajudam você a encontrar os
                pesquisadores e publicações mais relevantes em sua área.
              </p>
            </div>
            <div className="benefit-box green">
              <div className="benefit-icon green">
                <FaUsers />
              </div>
              <h3>Rede global</h3>
              <p>
                Conecte-se com pesquisadores de instituições do mundo todo e
                construa relacionamentos acadêmicos significativos.
              </p>
            </div>
            <div className="benefit-box purple">
              <div className="benefit-icon purple">
                <FaChartBar />
              </div>
              <h3>Rastreamento de Impacto</h3>
              <p>
                Monitore o impacto da sua pesquisa com análises detalhadas e
                métricas de visibilidade.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
