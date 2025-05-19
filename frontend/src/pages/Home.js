import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FaSearch, FaBars } from "react-icons/fa";
import "../App.css";

function Home({ isLoggedIn }) {
  const navigate = useNavigate();
  const [researchData, setResearchData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterYear, setFilterYear] = useState("");
  const [filterAuthor, setFilterAuthor] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [view, setView] = useState("table");
  const [showSidebar, setShowSidebar] = useState(false);

  useEffect(() => {
    fetch("/data/research.json")
      .then((res) => {
        if (!res.ok) throw new Error("Falha ao buscar dados");
        return res.json();
      })
      .then((json) => setResearchData(json))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="home-container">
        <p>Carregando…</p>
      </div>
    );
  if (error)
    return (
      <div className="home-container">
        <p>Erro: {error}</p>
      </div>
    );

  // listas de filtros...
  const years = Array.from(new Set(researchData.map((r) => r.year))).sort(
    (a, b) => b - a
  );
  const authors = Array.from(
    new Set(
      researchData.flatMap((r) => r.authors.split(";").map((a) => a.trim()))
    )
  ).sort();

  let filtered = researchData;
  if (filterYear)
    filtered = filtered.filter((r) => r.year === Number(filterYear));
  if (filterAuthor)
    filtered = filtered.filter((r) => r.authors.includes(filterAuthor));
  if (searchTerm)
    filtered = filtered.filter((r) =>
      r.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

  return (
    <div className="home-container">
      <header className="home-header">
        <h2 className="logo">AbraoAbrao</h2>
        {isLoggedIn ? (
          <button
            className="hamburger"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            <FaBars />
          </button>
        ) : (
          <nav className="nav-buttons">
            <button onClick={() => navigate("/cadastro")}>Sign In</button>
            <button onClick={() => navigate("/cadastro")}>Sign Up</button>
          </nav>
        )}
      </header>

      {isLoggedIn && showSidebar && (
        <aside className="sidebar">
          <div className="brand">AbraoAbrao</div>
          <div className="profile">
            <img src="/img/profile.png" alt="Avatar" />
            <span>Meu Perfil</span>
          </div>
          <nav className="menu">
            <a href="#">Visão Geral</a>
            <a href="#">Minhas Pesquisas</a>
            <a href="#">Configurações</a>
            <a href="#">Sair</a>
          </nav>
        </aside>
      )}

      <main className="home-main">
        <div className="search-wrapper">
          <input
            type="text"
            placeholder="Buscar pesquisas acadêmicas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <FaSearch className="search-icon" />
        </div>

        <section className="filters-section">
          <div className="year-filter">
            <label htmlFor="year-select">Ano:</label>
            <select
              id="year-select"
              value={filterYear}
              onChange={(e) => setFilterYear(e.target.value)}
            >
              <option value="">Todos</option>
              {years.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>
          <div className="author-filter">
            <label htmlFor="author-select">Autor:</label>
            <select
              id="author-select"
              value={filterAuthor}
              onChange={(e) => setFilterAuthor(e.target.value)}
            >
              <option value="">Todos</option>
              {authors.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
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

        <section className="results-section">
          {view === "table" ? (
            <table className="results-table">
              <thead>
                <tr>
                  <th>Título</th>
                  <th>Autores</th>
                  <th>Ano</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item, i) => (
                  <tr key={i}>
                    <td className="title-cell">{item.title}</td>
                    <td>
                      {item.authors.split(";").map((a) => {
                        const name = a.trim();
                        const authorId = name
                          .toLowerCase()
                          .replace(/\s+/g, "-");
                        return (
                          <span
                            key={authorId}
                            className="author-link"
                            onClick={() => navigate(`/dashboard/${authorId}`)}
                          >
                            {name}
                          </span>
                        );
                      })}
                    </td>
                    <td>{item.year}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="results-grid">
              {filtered.map((item, i) => (
                <div key={i} className="card">
                  <div className="card-title">{item.title}</div>
                  <div className="card-authors">{item.authors}</div>
                  <div className="card-year">{item.year}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Home;
