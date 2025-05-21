<<<<<<< HEAD
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../App.css";

function Home() {
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
=======
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FaSearch, FaBars } from "react-icons/fa";
import FilterPanel from "../components/filtros";
import "../App.css";

function Home({ isLoggedIn }) {
  const navigate = useNavigate();
  const [researchData, setResearchData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // estados de filtro
  const [filterYear, setFilterYear] = useState("");
  const [filterAuthor, setFilterAuthor] = useState("");
  const [filterInstitution, setFilterInstitution] = useState("");
  const [filterSortCitations, setFilterSortCitations] = useState("");
  const [filterCoAuthor, setFilterCoAuthor] = useState("");
  const [filterLanguage, setFilterLanguage] = useState("");
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

  // derive opções para filtros
  const years = Array.from(new Set(researchData.map((r) => r.year))).sort(
    (a, b) => b - a
  );
  const authors = Array.from(
    new Set(
      researchData.flatMap((r) => r.authors.split(";").map((a) => a.trim()))
    )
  ).sort();
  const institutions = Array.from(
    new Set(researchData.map((r) => r.institution))
  ).sort();
  const coAuthors = Array.from(
    new Set(researchData.flatMap((r) => r.coAuthors))
  ).sort();
  const languages = Array.from(
    new Set(researchData.map((r) => r.language))
  ).sort();

  // aplique filtros
  let filtered = researchData
    .filter((r) => !filterYear || r.year === Number(filterYear))
    .filter((r) => !filterInstitution || r.institution === filterInstitution)
    .filter((r) => !filterLanguage || r.language === filterLanguage)
    .filter((r) => !filterAuthor || r.authors.includes(filterAuthor))
    .filter((r) => !filterCoAuthor || r.coAuthors.includes(filterCoAuthor))
    .filter(
      (r) =>
        !searchTerm || r.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

  // ordene por citações
  let sorted = [...filtered];
  if (filterSortCitations === "desc")
    sorted.sort((a, b) => b.citations - a.citations);
  if (filterSortCitations === "asc")
    sorted.sort((a, b) => a.citations - b.citations);
>>>>>>> features/isa

  return (
    <div className="home-container">
      <header className="home-header">
        <h2 className="logo">AbraoAbrao</h2>
<<<<<<< HEAD
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
                            <Link to={`/author/${item.orcid}`}>
                              {item.orcid}
                            </Link>
                          </td>
                          <td>
                            <Link to={`/author/${item.orcid}`}>
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
=======
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

      {isLoggedIn && showSidebar && <aside className="sidebar">…</aside>}

      <main className="home-main">
        <div className="search-wrapper">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar pesquisas acadêmicas..."
          />
          <FaSearch className="search-icon" />
        </div>

        <FilterPanel
          years={years}
          authors={authors}
          institutions={institutions}
          coAuthors={coAuthors}
          languages={languages}
          filterYear={filterYear}
          setFilterYear={setFilterYear}
          filterAuthor={filterAuthor}
          setFilterAuthor={setFilterAuthor}
          filterInstitution={filterInstitution}
          setFilterInstitution={setFilterInstitution}
          filterSortCitations={filterSortCitations}
          setFilterSortCitations={setFilterSortCitations}
          filterCoAuthor={filterCoAuthor}
          setFilterCoAuthor={setFilterCoAuthor}
          filterLanguage={filterLanguage}
          setFilterLanguage={setFilterLanguage}
        />

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
                {sorted.map((item, i) => (
                  <tr key={i}>
                    <td className="title-cell">{item.title}</td>
                    <td>
                      {item.authors.split(";").map((name) => {
                        const id = name
                          .trim()
                          .toLowerCase()
                          .replace(/\s+/g, "-");
                        return (
                          <span
                            key={id}
                            className="author-link"
                            onClick={() => navigate(`/dashboard/${id}`)}
                          >
                            {name.trim()}
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
              {sorted.map((item, i) => (
                <div key={i} className="card">
                  <div className="card-title">{item.title}</div>
                  <div className="card-authors">{item.authors}</div>
                  <div className="card-year">{item.year}</div>
                </div>
              ))}
            </div>
>>>>>>> features/isa
          )}
        </section>
      </main>
    </div>
  );
}

export default Home;
