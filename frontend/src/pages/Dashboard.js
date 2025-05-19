import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FaSearch, FaBars } from "react-icons/fa";
import "../Dashboard.css";

function Dashboard({ isLoggedIn, user }) {
  const { authorId } = useParams();
  const loggedId = user?.id;
  const isOwnProfile = isLoggedIn && loggedId === authorId;
  const [showSidebar, setShowSidebar] = useState(isOwnProfile);
  // opcional: ao mudar authorId, resetar sidebar se não for próprio
  useEffect(() => {
    setShowSidebar(isOwnProfile);
  }, [authorId, isOwnProfile]);

  return (
    <div className="dashboard-container">
      {/* mostre o hambúrguer para logados em outros perfis */}
      {isLoggedIn && !isOwnProfile && (
        <button
          className="hamburger"
          onClick={() => setShowSidebar(!showSidebar)}
        >
          <FaBars />
        </button>
      )}

      {/* sidebar sempre visível no próprio perfil ou quando toggled */}
      {showSidebar && isLoggedIn && (
        <aside className="sidebar">
          <div className="brand">AbraoAbrao</div>
          <div className="profile">
            <img src={user.avatar || "/img/profile.png"} alt="Avatar" />
            <span>{user.name || "Usuário da Silva"}</span>
          </div>
          <nav className="menu">
            <a href="#">Visão Geral</a>
            <a href="#">Minhas Pesquisas</a>
            <a href="#">Configurações</a>
            <a href="#">Sair</a>
          </nav>
        </aside>
      )}

      <main className="main-content">
        <header className="main-header">
          {/* só mostra título */}
          <h1>
            {isOwnProfile
              ? "Meu Dashboard"
              : `Perfil de ${authorId.replace(/-/g, " ")}`}
          </h1>
        </header>

        <section className="search-section">
          <input type="text" placeholder="Buscar pesquisas acadêmicas..." />
          <FaSearch className="search-icon" />
        </section>

        <section className="filter-bar">
          <h3>Filtros</h3>
          <hr />
        </section>

        <section className="results-panel">
          <div className="placeholder">
            {!isLoggedIn
              ? "Faça login para ver suas pesquisas ou busque um autor abaixo."
              : "Conteúdo do dashboard"}
          </div>
        </section>
      </main>
    </div>
  );
}

export default Dashboard;
