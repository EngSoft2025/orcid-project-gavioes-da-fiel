import React, { useEffect, useRef, useState } from "react";
import Chart from "chart.js/auto";

const API_URL = process.env.REACT_APP_API_URL;

// Loader enquanto o gráfico carrega
const ChartSkeleton = () => (
  <div className="chart-skeleton-container">
    <div className="skeleton-bar" style={{ height: "60%" }}></div>
    <div className="skeleton-bar" style={{ height: "80%" }}></div>
    <div className="skeleton-bar" style={{ height: "70%" }}></div>
    <div className="skeleton-bar" style={{ height: "90%" }}></div>
    <div className="skeleton-bar" style={{ height: "75%" }}></div>
    <div className="skeleton-bar" style={{ height: "85%" }}></div>
  </div>
);

function ChartsSection({ orcidId }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!orcidId) {
      setLoading(false);
      return;
    }

    async function fetchStats() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_URL}/orcid/${orcidId}/stats`);
        if (!res.ok) throw new Error("Erro ao buscar estatísticas do gráfico.");
        const json = await res.json();
        setChartData(json);
      } catch (err) {
        setError(err.message);
        console.error("Erro ao carregar dados do gráfico:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [orcidId]);

  useEffect(() => {
    if (!chartData || loading || error) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null;
      }
      return;
    }

    const { years, publications, citations } = chartData;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext("2d");
    chartInstance.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels: years,
        datasets: [
          {
            label: "Citações",
            data: citations,
            type: "line",
            fill: false,
            borderColor: "rgba(255, 99, 132, 1)",
            backgroundColor: "rgba(255, 99, 132, 0.5)",
            yAxisID: "yCitations",
            tension: 0.1,
            order: 0,
          },
          {
            label: "Publicações",
            data: publications,
            backgroundColor: "rgba(54, 162, 235, 0.8)",
            borderColor: "rgba(54, 162, 235, 1)",
            yAxisID: "yPublications",
            order: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: { title: { display: true, text: "Ano" } },
          yCitations: {
            type: "linear",
            display: true,
            position: "left",
            title: {
              display: true,
              text: "Citações",
              color: "rgba(255, 99, 132, 1)",
            },
            ticks: { color: "rgba(255, 99, 132, 1)" },
            grid: { drawOnChartArea: true },
          },
          yPublications: {
            type: "linear",
            display: true,
            position: "right",
            title: {
              display: true,
              text: "Publicações",
              color: "rgba(54, 162, 235, 1)",
            },
            ticks: { color: "rgba(54, 162, 235, 1)", stepSize: 5 },
            grid: { drawOnChartArea: false },
          },
        },
        plugins: {
          legend: { position: "top" },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.dataset.label || ""}: ${context.parsed.y}`;
              },
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null;
      }
    };
  }, [chartData, loading, error]);

  if (loading) return <ChartSkeleton />;
  if (error)
    return (
      <div className="error-message chart-error">
        Erro ao carregar o gráfico.
      </div>
    );
  if (!chartData || !chartData.years || chartData.years.length === 0)
    return (
      <div className="empty-state chart-empty">Nenhum dado disponível.</div>
    );

  return (
    <div
      className="chart-canvas-container"
      style={{ height: "450px", width: "100%" }}
    >
      <canvas ref={chartRef}></canvas>
    </div>
  );
}

export default ChartsSection;
