// src/pages/Dashboard.js
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FaSearch, FaMoon, FaSun, FaUserGraduate } from "react-icons/fa";
import "../Dashboard.css";
import LoadingDrop from "../components/LoadingDrop";
import Sidebar from "../components/Sidebar";
import ChartsSection from "../components/ChartsSection";
import FilterPanel from "../components/filtros";
import { PiStudentBold } from "react-icons/pi";
import { FaRegUser } from "react-icons/fa";
import { MdOutlineWorkOutline } from "react-icons/md";

function Dashboard({}) {
  const { authorId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [selectedTab, setTab] = useState("Biografia");

  const [yearFilter, setYearFilter] = useState("");
  const [citationSort, setCitationSort] = useState("");
  const [filteredWorks, setFilteredWorks] = useState([]);
  const [showFullBio, setShowFullBio] = useState(false);

  useEffect(() => {
    document.body.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode((prev) => !prev);

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

  useEffect(() => {
    async function fetchAndFilterWorks() {
      try {
        let works = [];

        const res = await fetch(
          `http://localhost:8000/orcid/${authorId}/works/filter_by_citations`
        );
        const json = await res.json();
        works = json.works || [];

        if (yearFilter) {
          works = works.filter(
            (w) => w.year && w.year.toString() === yearFilter
          );
        }

        if (searchTerm) {
          works = works.filter((w) =>
            w.title.toLowerCase().includes(searchTerm.toLowerCase())
          );
        }

        if (citationSort !== "desc") {
          works = works.sort((a, b) => b.year - a.year);
        }

        setFilteredWorks(works);
      } catch (err) {
        console.error("Erro ao buscar obras filtradas:", err);
      }
    }

    fetchAndFilterWorks();
  }, [authorId, searchTerm, yearFilter, citationSort]);

  if (loading) return <LoadingDrop />;
  if (error) return <p className="error">Erro: {error}</p>;
  if (!data) return null;
  const hasBio = !!data?.personal?.biography;
  const hasEmployments =
    Array.isArray(data?.employments) && data.employments.length > 0;
  const hasEducations =
    Array.isArray(data?.educations) && data.educations.length > 0;

  return (
    <div className="dashboard-container">
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} data={data} />

      <header className="dashboard-header">
        <div className="logo">
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

      <main className="main-content">
        <div className="profile-box">
          <h1>{data.personal.full_name}</h1>

          {data.employments?.some((e) => !e.end_date) && (
            <div className="active-jobs">
              {data.employments
                .filter((e) => !e.end_date)
                .map((e, i) => (
                  <div key={i} className="job-entry">
                    <p className="position">{e.role_title}</p>
                    <p className="affiliation">{e.organization}</p>
                  </div>
                ))}
            </div>
          )}

          {data.keywords?.length > 0 && (
            <div className="keywords">
              {data.keywords.map((kw, i) => (
                <span key={i} className="keyword">
                  {kw}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="tabs modern-tabs" style={{ width: "100%" }}>
          {["Biografia", "Publicações", "Métricas"].map((tab) => (
            <button
              key={tab}
              onClick={() => setTab(tab)}
              className={`modern-tab-button ${
                selectedTab === tab ? "active" : ""
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="tab-content">
          {selectedTab === "Biografia" &&
            (hasBio || hasEmployments || hasEducations ? (
              <div className="bio-two-column">
                {hasBio && (
                  <div className="bio-card">
                    <h3 className="section-title">
                      <FaRegUser className="section-icon" />
                      Sobre
                    </h3>
                    <div
                      className={`bio-text ${
                        showFullBio ? "expanded" : "collapsed"
                      }`}
                    >
                      {data.personal.biography}
                    </div>
                    {data.personal.biography.length > 500 && (
                      <button
                        className="see-more-button"
                        onClick={() => setShowFullBio((prev) => !prev)}
                      >
                        {showFullBio ? "Ver menos" : "Ver mais"}
                      </button>
                    )}
                  </div>
                )}

                {hasEmployments && (
                  <div className="bio-card">
                    <h3 className="section-title">
                      <MdOutlineWorkOutline className="section-icon" />
                      Empregos e cargos
                    </h3>
                    {data.employments.map((job, i) => (
                      <div key={i} className="employment-entry">
                        <p className="position">{job.role_title}</p>
                        <p className="affiliation">
                          {job.organization}
                          {(job.start_date || job.end_date) && (
                            <>
                              {" "}
                              ({job.start_date || "?"} –{" "}
                              {job.end_date || "atual"})
                            </>
                          )}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
                {hasEducations && (
                  <div className="bio-card full-width">
                    <h3 className="section-title">
                      <PiStudentBold className="section-icon" />
                      Educação e qualificações
                    </h3>
                    <div className="education-grid">
                      {data.educations.map((edu, i) => (
                        <div key={i} className="education-block">
                          <p className="edu-institution">{edu.organization}</p>
                          <p className="edu-details">{edu.start_date}</p>
                          <p className="edu-details">{edu.degree_title}</p>
                          {edu.areas?.length > 0 && (
                            <p className="edu-areas">{edu.areas.join(", ")}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-state">
                <p>
                  Nenhuma informação biográfica disponível para este perfil.
                </p>
              </div>
            ))}

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

              <FilterPanel
                years={Array.from(new Set(data.works.map((w) => w.year))).sort(
                  (a, b) => b - a
                )}
                filterYear={yearFilter}
                setFilterYear={setYearFilter}
                filterSortCitations={citationSort}
                setFilterSortCitations={setCitationSort}
              />

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
              <div className="metric-card">
                Crescimento de Produção Científica
              </div>
              <ChartsSection orcidId={authorId} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
