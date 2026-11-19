
import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./Components/navbar";
import Home from "./pages/home";
import LikedHomes from "./pages/LikedHomes";
import Contact from "./pages/contact";

import "./App.css";

function App() {
  const [likedHomes, setLikedHomes] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("likedHomes"));
      return Array.isArray(saved) ? saved : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(
      "likedHomes",
      JSON.stringify(likedHomes)
    );
  }, [likedHomes]);

  const toggleLike = (home) => {
    setLikedHomes((current) => {
      const exists = current.some(
        (item) => item.id === home.id
      );

      if (exists) {
        return current.filter(
          (item) => item.id !== home.id
        );
      }

      return [...current, home];
    });
  };

  return (
    <BrowserRouter>
      <Navbar likedCount={likedHomes.length} />

      <Routes>
        <Route
          path="/"
          element={
            <Home
              likedHomes={likedHomes}
              toggleLike={toggleLike}
            />
          }
        />

        <Route
          path="/liked"
          element={
            <LikedHomes
              likedHomes={likedHomes}
              toggleLike={toggleLike}
            />
          }
        />

        <Route
          path="/contact"
          element={<Contact />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
