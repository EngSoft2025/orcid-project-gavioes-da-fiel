import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";
import "../Dashboard.css";

function ChartsSection({ works }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!works || works.length === 0) return;

    const yearStats = {};

    works.forEach((work) => {
      const year = work.year;
      const citations = work.citations || 0;

      if (year) {
        if (!yearStats[year]) {
          yearStats[year] = { publications: 0, citations: 0 };
        }

        yearStats[year].publications += 1;
        yearStats[year].citations += citations;
      }
    });

    const sortedYears = Object.keys(yearStats).sort();
    const publications = sortedYears.map((year) => yearStats[year].publications);
    const citations = sortedYears.map((year) => yearStats[year].citations);

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext("2d");
    chartInstance.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels: sortedYears,
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
            mode: 'index',
            intersect: false
          },
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  label += context.parsed.y;
                  return label;
                }
              }
            }
          }
        },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [works]);

  return (
    <div className="chart-container">
      <canvas id="Chart" ref={chartRef}></canvas>
    </div>
  );
}

export default ChartsSection;
