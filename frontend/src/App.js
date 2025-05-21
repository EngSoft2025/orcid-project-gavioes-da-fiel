// src/App.js
import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Cadastro from "./pages/Cadastro";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // checa token/localStorage…
  }, []);

  return (
    <Routes>
      <Route path="/" element={<Home isLoggedIn={!!user} user={user || {}} />} />
      <Route path="/cadastro" element={<Cadastro onAuth={setUser} />} />
      {/* Alinha a rota com o seu Dashboard.js */}
      <Route
        path="/dashboard/:authorId"
        element={<Dashboard isLoggedIn={!!user} user={user || {}} />}
      />
    </Routes>
  );
}

export default App;
