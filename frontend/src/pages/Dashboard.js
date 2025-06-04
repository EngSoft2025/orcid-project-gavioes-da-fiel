// src/pages/Dashboard.js
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FaSearch, FaMoon, FaSun, FaFilter } from "react-icons/fa";
import "../Dashboard.css";
import LoadingDrop from "../components/LoadingDrop";
import Sidebar from "../components/Sidebar";
import ChartsSection from "../components/ChartsSection";



function Dashboard({ }) {
  const { authorId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [selectedTab, setTab] = useState("Biografia");
  const [yearFilter, setYearFilter] = useState("");
  const [selectedKeywords, setSelectedKeywords] = useState([]);
  



  useEffect(() => {
    document.body.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode((prev) => !prev);
  };

  useEffect(() => {
    async function fetchAll() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`http://localhost:8000/orcid/${authorId}/all`);
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, [authorId]);

  if (loading) return <LoadingDrop />;
  if (error) return <p className="error">Erro: {error}</p>;
  if (!data) return null;
  
  console.log(data);


  const filteredWorks = data.works.filter((w) => {
      const matchesSearch = w.title.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesYear = !yearFilter || w.year.toString() === yearFilter;
      return matchesSearch && matchesYear;
    });
    

  return (
      <div className="dashboard-container">
        <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} data={data} />

        <div>
          <header className="home-header">
            <div className="logo">
              <img src="../img/logo.png" alt="Logo da Plataforma" className="logo-img" />
            </div>
            <div className="header-controls">
              <button className="theme-toggle" onClick={toggleDarkMode}>
                {darkMode ? <FaSun /> : <FaMoon />}
              </button>
            </div>
          </header>
        </div>

        <main className="main-content">
          {/* Cabeçalho do Perfil */}
          <div className="profile-box">
              <h1>{data.personal.full_name}</h1>

              {/* Empregos ativos */}
              
              {data.employments?.some(e => !e.end_date) && (
                  <div className="active-jobs">
                    {data.employments
                      .filter(e => !e.end_date)
                      .map((e, i) => (
                        <div key={i} className="job-entry">
                          <p className="position">{e.role_title}</p>
                          <p className="affiliation">{e.organization}</p>
                        </div>
                      ))}
                  </div>
                )}

              {/* Palavras-chave */}
              {data.keywords?.length > 0 && (
                <div className="keywords">
                  {data.keywords.map((kw, i) => (
                    <span key={i} className="keyword">
                      {kw}
                    </span>
                  ))}
                </div>
              )}
              {data.personal?.urls?.length > 0 && (
                  <div className="url-container">
                    <a 
                      href={data.personal.urls[0]} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="url-button"
                    >
                      {data.personal.urls[0].includes('contact') ? 'Contact' : 'Site'}
                    </a>
                  </div>
                )}
              

            </div>
          {/* Abas */}
          <div className="tabs">
              {["Biografia", "Publicações", "Métricas"].map((tab, index, array) => (
                <button
                  key={tab}
                  onClick={() => setTab(tab)}
                  className={`tab-button ${tab === selectedTab ? "active" : ""} ${
                    index === 0 ? "first" : index === array.length - 1 ? "last" : "middle"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

          {/* Conteúdo Condicional por Aba */}
          <div className="tab-content">
            {selectedTab === "Biografia" && (
                <div className="bio-section">
                  {data.personal.biography && (
                    <div className="bio-content">
                      <h3 className="bio-title">Biografia</h3>
                      <p className="bio-text">
                        {data.personal.biography}
                      </p>
                    </div>
                  )}
                </div>
              )}

            {selectedTab === "Publicações" && (
              <>
                <section className="search-section">
                  <input
                    type="text"
                    placeholder="Buscar trabalhos por título..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                  <FaSearch className="search-icon" />
                </section>

                <div className="filters-container">
                  {/* Year filter dropdown on the left */}
                  <div className="filter-group">
                    <label>Ano</label>
                    <select 
                      onChange={(e) => setYearFilter(e.target.value)}
                      className="year-filter"
                    >
                      <option value="">Todos</option>
                      {Array.from(new Set(data.works.map(w => w.year))).sort((a, b) => b - a).map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <section className="results-panel">
                  {filteredWorks.length > 0 ? (
                    <ul>
                      {filteredWorks.map((w, i) => (
                        <li key={i}>
                          {w.title} <em>({w.year})</em>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>Nenhum trabalho encontrado.</p>
                  )}
                </section>
              </>
            )}

            {selectedTab === "Métricas" && (
             <div className="metrics-section">
                <div className="metric-card">Crescimento de Produção Científica</div>
                <ChartsSection works={data.works} />
              </div>
            )}
          </div>
        </main>
      </div>
    );

}

export default Dashboard;
