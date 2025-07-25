import React, { useState, useEffect } from "react";

const API_URL = process.env.REACT_APP_API_URL;

// Componente de loading
const MetricItemSkeleton = () => (
  <li className="skeleton-item">
    <span className="skeleton-text short"></span>
    <span className="skeleton-text long"></span>
  </li>
);

function AggregatedMetrics({ orcidId }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!orcidId) {
      setLoading(false);
      return;
    }

    async function fetchMetrics() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_URL}/orcid/${orcidId}/metrics`);
        if (!res.ok)
          throw new Error(`Failed to fetch metrics with status ${res.status}`);
        const data = await res.json();
        setMetrics(data);
      } catch (err) {
        setError(err.message);
        console.error("Error fetching aggregated metrics:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchMetrics();
  }, [orcidId]);

  const formatNumber = (num) =>
    typeof num === "number"
      ? num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")
      : num;

  const formatFloat = (num) =>
    typeof num === "number" ? num.toFixed(1).replace(".", ",") : num;

  return (
    <div className="aggregated-metrics-card">
      <h3 className="section-title">Métricas Agregadas</h3>
      {loading && (
        <ul className="metrics-list">
          {Array.from({ length: 7 }).map((_, i) => (
            <MetricItemSkeleton key={i} />
          ))}
        </ul>
      )}
      {error && <div className="error-message">Erro ao carregar métricas.</div>}
      {!loading && !error && metrics && (
        <ul className="metrics-list">
          <li>
            <span>Total de Publicações:</span>
            <strong>{formatNumber(metrics.total_publicacoes)}</strong>
          </li>
          <li>
            <span>Total de Citações:</span>
            <strong>{formatNumber(metrics.total_citacoes)}</strong>
          </li>
          <li>
            <span>Média de Citações:</span>
            <strong>{formatFloat(metrics.media_citacoes)}</strong>
          </li>
          <li>
            <span>Fator de Impacto (2 anos):</span>
            <strong>{formatFloat(metrics.fator_de_impacto)}</strong>
          </li>
          <li>
            <span>Índice H:</span>
            <strong>{metrics.h_index}</strong>
          </li>
          <li>
            <span>Índice i10:</span>
            <strong>{metrics.i10_index}</strong>
          </li>
          <li>
            <span>Citações da Pesquisa Mais Citada:</span>
            <strong>
              {formatNumber(metrics.pesquisa_mais_citada?.citations)}
            </strong>
          </li>
        </ul>
      )}
    </div>
  );
}

export default AggregatedMetrics;
