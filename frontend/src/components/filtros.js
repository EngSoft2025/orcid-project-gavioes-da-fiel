import React from "react";
import PropTypes from "prop-types";

export default function FilterPanel({
  years,
  authors,
  institutions,
  coAuthors,
  languages,
  filterYear,
  setFilterYear,
  filterAuthor,
  setFilterAuthor,
  filterInstitution,
  setFilterInstitution,
  filterSortCitations,
  setFilterSortCitations,
  filterCoAuthor,
  setFilterCoAuthor,
  filterLanguage,
  setFilterLanguage,
}) {
  return (
    <section className="filters-section">
      {/* Ano */}
      <div className="filter-group">
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

      {/* Autor */}
      <div className="filter-group">
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

      {/* Instituição */}
      <div className="filter-group">
        <label htmlFor="institution-select">Instituição:</label>
        <select
          id="institution-select"
          value={filterInstitution}
          onChange={(e) => setFilterInstitution(e.target.value)}
        >
          <option value="">Todas</option>
          {institutions.map((i) => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </select>
      </div>

      {/* Citações */}
      <div className="filter-group">
        <label htmlFor="citation-select">Citações:</label>
        <select
          id="citation-select"
          value={filterSortCitations}
          onChange={(e) => setFilterSortCitations(e.target.value)}
        >
          <option value="">Qualquer</option>
          <option value="desc">Mais citadas</option>
          <option value="asc">Menos citadas</option>
        </select>
      </div>

      {/* Co-autor */}
      <div className="filter-group">
        <label htmlFor="coauthor-select">Co-autor:</label>
        <select
          id="coauthor-select"
          value={filterCoAuthor}
          onChange={(e) => setFilterCoAuthor(e.target.value)}
        >
          <option value="">Todos</option>
          {coAuthors.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {/* Idioma */}
      <div className="filter-group">
        <label htmlFor="language-select">Idioma:</label>
        <select
          id="language-select"
          value={filterLanguage}
          onChange={(e) => setFilterLanguage(e.target.value)}
        >
          <option value="">Todos</option>
          {languages.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
      </div>
    </section>
  );
}

FilterPanel.propTypes = {
  years: PropTypes.array.isRequired,
  authors: PropTypes.array.isRequired,
  institutions: PropTypes.array.isRequired,
  coAuthors: PropTypes.array.isRequired,
  languages: PropTypes.array.isRequired,
  filterYear: PropTypes.string.isRequired,
  setFilterYear: PropTypes.func.isRequired,
  filterAuthor: PropTypes.string.isRequired,
  setFilterAuthor: PropTypes.func.isRequired,
  filterInstitution: PropTypes.string.isRequired,
  setFilterInstitution: PropTypes.func.isRequired,
  filterSortCitations: PropTypes.string.isRequired,
  setFilterSortCitations: PropTypes.func.isRequired,
  filterCoAuthor: PropTypes.string.isRequired,
  setFilterCoAuthor: PropTypes.func.isRequired,
  filterLanguage: PropTypes.string.isRequired,
  setFilterLanguage: PropTypes.func.isRequired,
};
