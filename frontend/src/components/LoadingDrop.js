import React from "react";
import "../LoadingDrop.css";

function LoadingDrop() {
  return (
    <div className="loading-container">
      <img
        src={`${process.env.PUBLIC_URL}/img/GotaLoader.svg`}
        alt="Carregando..."
        className="gota-loader"
      />

      <span className="loading-text">Carregando perfil...</span>
    </div>
  );
}

export default LoadingDrop;
