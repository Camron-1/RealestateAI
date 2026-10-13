import { useState } from "react";
import HomeImageGallery from "./Home_Gallery.jsx";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/ai-search?query=${encodeURIComponent(query)}`
      );

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();

      console.log("Backend response:", data);
      console.log("Homes:", data.results);

      setResults(data.results || []);
    } catch (error) {
      console.error(error);
      setError("Something went wrong while searching for homes.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      <header className="header">
        <h1>RealestateAI</h1>
        <p>Find a home that fits what matters to you.</p>
      </header>

      <main className="main-content">

        <section className="search-section">
          <h2>Find Your Home</h2>

          <p>
            Tell us what you're looking for and we'll find homes
            that match your preferences.
          </p>

          <div className="search-bar">
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Example: 2 bedroom home in Chelan under $600k near a hospital and park"
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSearch();
                }
              }}
            />

            <button
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? "Searching..." : "Search Homes"}
            </button>
          </div>

          {error && (
            <p className="error-message">
              {error}
            </p>
          )}
        </section>

        {results.length > 0 && (
          <section className="results-section">

            <h2>Search Results</h2>

            <p>
              Found {results.length}{" "}
              {results.length === 1 ? "home" : "homes"}
            </p>

            <div className="home-list">

              {results.map((home) => (
                <div className="home-card" key={home.id}>

                  <HomeImageGallery images={home.images} />

                  <h3>
                    ${home.price?.toLocaleString()}
                  </h3>

                  <p>
                    {home.bedrooms} beds •{" "}
                    {home.bathrooms} baths •{" "}
                    {home.sqft?.toLocaleString()} sqft
                  </p>

                  <p>
                    {home.address?.streetNumber}{" "}
                    {home.address?.streetName}{" "}
                    {home.address?.streetSuffix}
                  </p>

                  <p>
                    {home.address?.city},{" "}
                    {home.address?.state}{" "}
                    {home.address?.zip}
                  </p>

                  {home.match_score != null && (
                    <p>
                      <strong>
                        Match Score: {home.match_score}%
                      </strong>
                    </p>
                  )}

                  <div className="nearby-places">

                    <h4>Nearby</h4>

                    {home.nearby?.hospital && (
                      <p>
                        🏥{" "}
                        {home.nearby.hospital.name || "Hospital"} -{" "}
                        {home.nearby.hospital.distance_miles} miles
                      </p>
                    )}

                    {home.nearby?.school && (
                      <p>
                        🏫{" "}
                        {home.nearby.school.name || "School"} -{" "}
                        {home.nearby.school.distance_miles} miles
                      </p>
                    )}

                    {home.nearby?.park && (
                      <p>
                        🌳{" "}
                        {home.nearby.park.name || "Park"} -{" "}
                        {home.nearby.park.distance_miles} miles
                      </p>
                    )}

                    {home.nearby?.dog_park && (
                      <p>
                        🐕{" "}
                        {home.nearby.dog_park.name || "Dog Park"} -{" "}
                        {home.nearby.dog_park.distance_miles} miles
                      </p>
                    )}

                    {home.nearby?.playground && (
                      <p>
                        🛝{" "}
                        {home.nearby.playground.name || "Playground"} -{" "}
                        {home.nearby.playground.distance_miles} miles
                      </p>
                    )}

                  </div>

                </div>
              ))}

            </div>

          </section>
        )}

      </main>
    </div>
  );
}

export default App;