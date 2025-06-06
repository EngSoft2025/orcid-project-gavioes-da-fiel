import React from "react";
import "../LoadingDrop.css";

function LoadingDrop() {
  return (
    <div className="loading-container">
      <div className="drop" />
      <span className="loading-text">Carregando perfil...</span>
    </div>
  );
}

export default LoadingDrop;
