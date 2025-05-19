import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FaSearch, FaBars } from "react-icons/fa";
import FilterPanel from "../components/filtros";
import "../Dashboard.css";

function Dashboard({ isLoggedIn, user }) {
  const { authorId } = useParams();
  const loggedId = user?.id;
  const isOwnProfile = isLoggedIn && loggedId === authorId;
  const [showSidebar, setShowSidebar] = useState(isOwnProfile);

  useEffect(() => {
    setShowSidebar(isOwnProfile);
  }, [authorId, isOwnProfile]);

  // state for filters reusable
  const [filterYear, setFilterYear] = useState("");
  const [filterAuthor, setFilterAuthor] = useState("");
  const [filterInstitution, setFilterInstitution] = useState("");
  const [filterSortCitations, setFilterSortCitations] = useState("");
  const [filterCoAuthor, setFilterCoAuthor] = useState("");
  const [filterLanguage, setFilterLanguage] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  // dummy data - replace with API call by authorId
  const [researchData, setResearchData] = useState([]);
  useEffect(() => {
    fetch("/data/research.json")
      .then((r) => r.json())
      .then(setResearchData);
  }, []);

  // derive options and reuse FilterPanel
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

  // apply filters similar to Home
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
  let sorted = [...filtered];
  if (filterSortCitations === "desc")
    sorted.sort((a, b) => b.citations - a.citations);
  if (filterSortCitations === "asc")
    sorted.sort((a, b) => a.citations - b.citations);

  return (
    <div className="dashboard-container">
      {isLoggedIn && !isOwnProfile && (
        <button
          className="hamburger"
          onClick={() => setShowSidebar(!showSidebar)}
        >
          <FaBars />
        </button>
      )}
      {showSidebar && isLoggedIn && <aside className="sidebar">…</aside>}
      <main className="main-content">
        <header className="main-header">
          <h1>
            {isOwnProfile
              ? "Meu Dashboard"
              : `Perfil de ${authorId.replace(/-/g, " ")}`}
          </h1>
        </header>
        <section className="search-section">
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar pesquisas acadêmicas..."
          />
          <FaSearch className="search-icon" />
        </section>
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
        <section className="results-panel">
          {sorted.map((item, i) => (
            <div key={i}>{item.title}</div>
          ))}
        </section>
      </main>
    </div>
  );
}
export default Dashboard;
