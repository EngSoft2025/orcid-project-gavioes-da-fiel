// src/pages/Dashboard.js
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FaSearch, FaBars } from "react-icons/fa";
import "../Dashboard.css";
import LoadingDrop from "../components/LoadingDrop";

function Dashboard({ isLoggedIn, user }) {
  const { authorId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

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

  // works come from format_works → [ { title, year }, … ]
  const filteredWorks = data.works.filter((w) =>
    w.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="dashboard-container">
      <button className="hamburger" onClick={() => setShowSidebar((v) => !v)}>
        <FaBars />
      </button>

      {showSidebar && (
        <aside className="sidebar">
          <h2>{data.personal.full_name}</h2>

          {data.personal.biography && (
            <>
              <h3>Biografia</h3>
              <p>{data.personal.biography}</p>
            </>
          )}

          {data.keywords?.length > 0 && (
            <>
              <h3>Palavras-chave</h3>
              <ul>
                {data.keywords.map((kw, i) => (
                  <li key={i}>{kw}</li>
                ))}
              </ul>
            </>
          )}

          {data.personal.other_names?.length > 0 && (
            <>
              <h3>Outros nomes</h3>
              <ul>
                {data.personal.other_names.map((n, i) => (
                  <li key={i}>{n}</li>
                ))}
              </ul>
            </>
          )}

          {data.personal.urls?.length > 0 && (
            <>
              <h3>URLs</h3>
              <ul>
                {data.personal.urls.map((url, i) => (
                  <li key={i}>
                    <a href={url} target="_blank" rel="noopener noreferrer">
                      {url}
                    </a>
                  </li>
                ))}
              </ul>
            </>
          )}

          {data.personal.emails?.length > 0 && (
            <>
              <h3>E-mails</h3>
              <ul>
                {data.personal.emails.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </>
          )}

          {data.personal.countries?.length > 0 && (
            <>
              <h3>Países</h3>
              <ul>
                {data.personal.countries.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </>
          )}

          {data.personal.external_ids?.length > 0 && (
            <>
              <h3>Identificadores externos</h3>
              <ul>
                {data.personal.external_ids.map((ex, i) => (
                  <li key={i}>
                    {ex.type}: {ex.value}
                  </li>
                ))}
              </ul>
            </>
          )}
        </aside>
      )}

      <main className="main-content">
        <header className="main-header">
          <h1>{data.personal.full_name}</h1>
        </header>

        <section className="search-section">
          <input
            type="text"
            placeholder="Buscar trabalhos por título..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <FaSearch className="search-icon" />
        </section>

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
      </main>
    </div>
  );
}

export default Dashboard;
