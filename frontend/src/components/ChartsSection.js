import React, { useEffect, useRef, useState } from "react";
import Chart from "chart.js/auto";
import "../Dashboard.css";

function ChartsSection({ orcidId }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch(`http://localhost:8000/orcid/${orcidId}/stats`);
        if (!res.ok) throw new Error("Erro ao buscar estatísticas.");
        const json = await res.json();
        setChartData(json);
      } catch (err) {
        console.error("Erro ao carregar dados do gráfico:", err);
      }
    }

    fetchStats();
  }, [orcidId]);

  useEffect(() => {
    if (!chartData) return;

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
            label: "Publicações",
            data: publications,
            backgroundColor: "rgba(54, 162, 235, 0.8)",
            borderColor: "rgba(54, 162, 235, 1)",
            borderWidth: 1,
          },
          {
            label: "Citações",
            data: citations,
            type: "line",
            fill: false,
            borderColor: "rgba(255, 99, 132, 1)",
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                let label = context.dataset.label || "";
                if (label) label += ": ";
                label += context.parsed.y;
                return label;
              },
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [chartData]);

  return (
    <div className="chart-container">
      <canvas id="Chart" ref={chartRef}></canvas>
    </div>
  );
}

export default ChartsSection;
