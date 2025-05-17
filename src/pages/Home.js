import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

// Exemplo de dados de pesquisa acadêmica
const researchData = [
  {
    title: "Estudo sobre Inteligência Artificial",
    authors: "Silva, A.; Souza, B.",
    year: 2023,
  },
  {
    title: "Análise de Algoritmos de Machine Learning",
    authors: "Costa, C.; Lima, D.",
    year: 2022,
  },
  {
    title: "Impacto da IA na Educação",
    authors: "Rocha, E.; Martins, F.",
    year: 2021,
  },
  {
    title: "Redes Neurais em Diagnóstico Médico",
    authors: "Almeida, G.; Fernanda, H.",
    year: 2023,
  },
];

function Home() {
  const navigate = useNavigate();
  const [view, setView] = useState("table");

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
        <div className="search-wrapper">
          <input type="text" placeholder="Buscar pesquisas acadêmicas..." />
          <span className="search-icon">🔍</span>
        </div>

        <section className="filters-section">
          <h3>Filtros</h3>
          {/* Aqui você pode implementar dropdowns ou checkboxes de área, ano, autores, etc. */}
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
                {researchData.map((item, idx) => (
                  <tr key={idx}>
                    <td className="title-cell">{item.title}</td>
                    <td>{item.authors}</td>
                    <td>{item.year}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="results-grid">
              {researchData.map((item, idx) => (
                <div key={idx} className="card">
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
