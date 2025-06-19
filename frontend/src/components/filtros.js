// src/components/filtros.js
import React from "react";

function FilterPanel({
  years = [],
  filterYear,
  setFilterYear,
  filterSortCitations,
  setFilterSortCitations,
}) {
  return (
    <div className="filters-section">
      <div className="filter-group">
        <label htmlFor="year-select">Ano</label>
        <select
          id="year-select"
          value={filterYear}
          onChange={(e) => setFilterYear(e.target.value)}
        >
          <option value="">Todos</option>
          {years.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="citations-select">Ordenar por</label>
        <select
          id="citations-select"
          value={filterSortCitations}
          onChange={(e) => setFilterSortCitations(e.target.value)}
        >
          <option value="">Mais recentes</option>
          <option value="desc">Mais citadas</option>
        </select>
      </div>
    </div>
  );
}

export default FilterPanel;
