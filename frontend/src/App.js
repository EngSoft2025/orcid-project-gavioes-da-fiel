// src/App.js
import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";

function App() {
  const [user] = useState(null);

  useEffect(() => {
    // checa token/localStorage…
  }, []);

  return (
    <Routes>
      <Route
        path="/"
        element={<Home isLoggedIn={!!user} user={user || {}} />}
      />

      <Route
        path="/dashboard/:authorId"
        element={<Dashboard isLoggedIn={!!user} user={user || {}} />}
      />
    </Routes>
  );
}

export default App;
