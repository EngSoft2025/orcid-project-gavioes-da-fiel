// src/pages/Dashboard.js
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FaSearch, FaMoon, FaSun, FaBars } from "react-icons/fa";
import "../Dashboard.css";
import LoadingDrop from "../components/LoadingDrop";
import Sidebar from "../components/Sidebar";
import ChartsSection from "../components/ChartsSection";
import FilterPanel from "../components/filtros";
import AggregatedMetrics from "../components/AggregatedMetrics";
import { PiStudentBold } from "react-icons/pi";
import { FaRegUser } from "react-icons/fa";
import { MdOutlineWorkOutline } from "react-icons/md";
import MenuIcon from "@mui/icons-material/Menu";

function Dashboard() {
  const { authorId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [yearFilter, setYearFilter] = useState("");
  const [citationSort, setCitationSort] = useState("");
  const [filteredWorks, setFilteredWorks] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [selectedTab, setTab] = useState("Biografia");
  const [showFullBio, setShowFullBio] = useState(false);
  const [selectedWork, setSelectedWork] = useState(null);
  const [isModalClosing, setIsModalClosing] = useState(false);

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

        // Faz fetch dos cited_by_count
        const citRes = await fetch(
          `http://localhost:8000/orcid/${authorId}/works/filter_by_citations`
        );
        if (!citRes.ok) throw new Error(`Status ${citRes.status}`);
        const citJson = await citRes.json();
        const worksWithCitations = citJson.works_sorted_by_citations;

        const updatedWorks = (json.works || []).map((work) => {
          const matching = worksWithCitations.find((w) => w.doi === work.doi);
          return {
            ...work,
            cited_by_count: matching?.cited_by_count ?? 0,
          };
        });

        setData({
          ...json,
          works: updatedWorks,
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, [authorId]);

  const handleKeywordClick = async (keyword) => {
    if (!keyword) return;
    setLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/orcid/${authorId}/works/filter_by_keyword?keyword=${encodeURIComponent(
          keyword
        )}`
      );
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const json = await res.json();
      setFilteredWorks(json.works || []);
      setTab("Publicações");
    } catch (err) {
      console.error("Erro ao filtrar por keyword:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    async function fetchAndFilterWorks() {
      if (!data?.works) return;
      try {
        let works = [];
        if (citationSort === "desc") {
          const res = await fetch(
            `http://localhost:8000/orcid/${authorId}/works/filter_by_citations`
          );
          if (!res.ok) throw new Error(`Status ${res.status}`);
          const json = await res.json();
          works = json.works_sorted_by_citations || [];
        } else {
          works = [...data.works].sort((a, b) => (b.year || 0) - (a.year || 0));
        }
        if (yearFilter) {
          works = works.filter((w) => w.year?.toString() === yearFilter);
        }
        if (searchTerm) {
          works = works.filter((w) =>
            w.title?.toLowerCase().includes(searchTerm.toLowerCase())
          );
        }
        setFilteredWorks(works);
      } catch (err) {
        console.error("Erro ao buscar obras filtradas:", err);
      }
    }
    fetchAndFilterWorks();
  }, [authorId, data, searchTerm, yearFilter, citationSort]);

  const handleWorkClick = async (work, e) => {
    if (e) e.preventDefault();
    if (!work?.doi) {
      setSelectedWork(work); // fallback
      return;
    }
    console.log(work);

    setLoading(true);
    try {
      const encodedDoi = encodeURIComponent(work.doi);
      const res = await fetch(
        `http://localhost:8000/works/publication/${encodedDoi}`
      );
      if (!res.ok) throw new Error("Erro ao buscar detalhes da publicação");

      const detailedWork = await res.json();
      setSelectedWork(detailedWork);
    } catch (err) {
      console.error("Erro ao buscar detalhes do trabalho:", err);
      setSelectedWork(work); // fallback
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadXML = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/orcid/${authorId}/export/xml`
      );
      if (!response.ok) throw new Error("Erro ao baixar XML");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `perfil_${authorId}.xml`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Erro ao baixar o XML:", error);
      alert("Falha ao baixar o arquivo XML.");
    }
  };

  const handleCloseModal = () => {
    setIsModalClosing(true);
    setTimeout(() => {
      setSelectedWork(null);
      setIsModalClosing(false);
    }, 300);
  };

  if (loading && !data) return <LoadingDrop />;
  if (error) return <p className="error">Erro: {error}</p>;
  if (!data) return null;

  const hasBio = !!data.personal?.biography;
  const hasEmployments =
    Array.isArray(data.employments) && data.employments.length > 0;
  const hasEducations =
    Array.isArray(data.educations) && data.educations.length > 0;

  return (
    <div className={`dashboard-container${sidebarOpen ? " sidebar-open" : ""}`}>
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} data={data} />
      <header className="dashboard-header">
        <button
          className="hamburger"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle sidebar"
        >
          <MenuIcon />
        </button>
        <div className="logo">
          <a href="#">
            <img
              src="../img/logo.png"
              alt="Logo da Plataforma"
              className="logo-img"
            />
          </a>
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
                    <p className="affiliation">
                      {e.organization}
                      {(e.start_date || e.end_date) && (
                        <>
                          {" "}
                          ({e.start_date || "?"} – {e.end_date || "atual"})
                        </>
                      )}
                    </p>
                  </div>
                ))}
            </div>
          )}
          {data.keywords?.length > 0 && (
            <div className="keywords">
              {data.keywords.map((kw, i) => (
                <button
                  key={i}
                  className="keyword-button"
                  onClick={() => handleKeywordClick(kw)}
                >
                  {kw}
                </button>
              ))}
            </div>
          )}
          <button onClick={handleDownloadXML} className="download-button">
            Baixar XML do Perfil
          </button>
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
                      <FaRegUser className="section-icon" /> Sobre
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
                      <MdOutlineWorkOutline className="section-icon" /> Empregos
                      e cargos
                    </h3>
                    {data.employments.map((e, i) => (
                      <div key={i} className="employment-entry">
                        <p className="position">{e.role_title}</p>
                        <p className="affiliation">
                          {e.organization}
                          {(e.start_date || e.end_date) && (
                            <>
                              {" "}
                              ({e.start_date || "?"} – {e.end_date || "atual"})
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
                      <PiStudentBold className="section-icon" /> Educação e
                      qualificações
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
                      <li
                        key={i}
                        onClick={(e) => handleWorkClick(w, e)}
                        className="clickable-work"
                      >
                        <div>
                          {w.title} <em>({w.year || "—"})</em>
                          {w.url && (
                            <span className="external-link-icon"> ↗</span>
                          )}
                        </div>
                        <div className="citation-count">
                          {w.cited_by_count ?? 0} citações
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>Nenhum trabalho encontrado.</p>
                )}
              </section>
            </>
          )}

          {selectedTab === "Métricas" ? (
            filteredWorks.length > 0 ? (
              <div className="metrics-layout">
                <div className="chart-container-card">
                  <h3 className="section-title chart-title">
                    Crescimento de Produção Científica & Métricas Chave
                  </h3>
                  <ChartsSection orcidId={authorId} />
                </div>
                <AggregatedMetrics orcidId={authorId} />
              </div>
            ) : (
              <div className="empty-state-metrics">
                <p>Nenhum trabalho encontrado.</p>
              </div>
            )
          ) : null}
        </div>

        {/* Modal para exibir detalhes do trabalho */}
        {selectedWork && (
          <div
            className={`work-modal-overlay ${isModalClosing ? "closing" : ""}`}
            onClick={handleCloseModal}
          >
            <div className="work-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close-button" onClick={handleCloseModal}>
                &times;
              </button>

              <h3 className="modal-title">{selectedWork.title}</h3>

              {selectedWork.authorships?.length > 0 && (
                <p className="modal-authors">
                  {selectedWork.authorships.map((a, i) => (
                    <React.Fragment key={a.author_orcid}>
                      <span
                        onClick={() => window.open(a.author_orcid, "_blank")}
                        className="author-hover"
                      >
                        {a.author_name}
                      </span>
                      {i < selectedWork.authorships.length - 1 && ", "}
                    </React.Fragment>
                  ))}
                </p>
              )}
              <p className="modal-subinfo">
                {selectedWork.publication_year ||
                  selectedWork.orcid_publication_year}{" "}
                · {selectedWork.container || "Periódico desconhecido"}
              </p>

              <div className="modal-details">
                <p>
                  <strong>Tipo:</strong> {selectedWork.type || "—"}
                </p>
                {selectedWork.doi && (
                  <p>
                    <strong>DOI:</strong>{" "}
                    <a
                      href={`https://doi.org/${selectedWork.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {selectedWork.doi}
                    </a>
                  </p>
                )}
              </div>

              <div className="modal-footer">
                <div className="metric-square">
                  <span className="metric-label">Citações</span>
                  <br></br>
                  <span className="metric-value">
                    {selectedWork.cited_by_count ?? 0}
                  </span>
                </div>
                {selectedWork.url && (
                  <a
                    href={selectedWork.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="modal-link-button"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Ver publicação
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
