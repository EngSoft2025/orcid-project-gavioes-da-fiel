<<<<<<< HEAD
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Cadastro from './pages/Cadastro';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/cadastro" element={<Cadastro />} />
=======
// src/App.js
import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Cadastro from "./pages/Cadastro";

function App() {
  // null = visitante; objeto = pesquisador logado
  const [user, setUser] = useState(null);

  useEffect(() => {
    // aqui você pode checar um token/localStorage para manter login
    // ex: const token = localStorage.getItem('token');
    // autenticar e setar setUser({ id, name, avatar })
  }, []);

  return (
    <Routes>
      {/* Página inicial de busca */}
      <Route
        path="/"
        element={<Home isLoggedIn={!!user} user={user || {}} />}
      />

      {/* Cadastro / Login */}
      <Route path="/cadastro" element={<Cadastro onAuth={setUser} />} />

      {/* Dashboard de autor/pesquisador */}
      <Route
        path="/dashboard/:authorId"
        element={<Dashboard isLoggedIn={!!user} user={user || {}} />}
      />
>>>>>>> features/isa
    </Routes>
  );
}

<<<<<<< HEAD
export default App;
=======
export default App;
>>>>>>> features/isa
