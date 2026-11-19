
import { useState } from "react";
import HomeCard from "../Components/HomeCard";
import "./HomeLayout.css";

const API_URL = "http://127.0.0.1:8000";

const amenityOptions = [
  { id: "hospital", label: "Hospital", icon: "🏥" },
  { id: "school", label: "School", icon: "🏫" },
  { id: "park", label: "Park", icon: "🌳" },
  { id: "dog_park", label: "Dog Park", icon: "🐕" },
  { id: "playground", label: "Playground", icon: "🛝" },
];

const priceOptions = [
  200000,
  300000,
  400000,
  500000,
  600000,
  750000,
  1000000,
  1500000,
];

function Home({ likedHomes = [], toggleLike }) {
  // Home search input and assistant input are separate.
  const [query, setQuery] = useState("");
  const [chatInput, setChatInput] = useState("");

  const [bedrooms, setBedrooms] = useState("");
  const [bathrooms, setBathrooms] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [amenities, setAmenities] = useState([]);

  const [messages, setMessages] = useState([]);
  const [searchPreferences, setSearchPreferences] = useState(null);

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [sortBy, setSortBy] = useState("match");

  const [dirtyFilters, setDirtyFilters] = useState([]);

  const markFilterChanged = (name) => {
    setDirtyFilters((current) =>
      current.includes(name) ? current : [...current, name]
    );
  };

  // Synchronize visible filters with the AI's preferences.
  const syncFiltersWithAI = (preferences) => {
    if (!preferences) return;

    setBedrooms(
      preferences.bedroom_mode === "minimum" &&
      preferences.min_bedrooms != null
        ? String(preferences.min_bedrooms)
        : ""
    );

    setBathrooms(
      preferences.bathroom_mode === "minimum" &&
      preferences.min_bathrooms != null
        ? String(preferences.min_bathrooms)
        : ""
    );

    setMaxPrice(
      preferences.max_price != null
        ? String(preferences.max_price)
        : ""
    );

    setAmenities(
      amenityOptions
        .filter(
          (amenity) =>
            preferences[`wants_${amenity.id}`] === true
        )
        .map((amenity) => amenity.id)
    );
  };

  const toggleAmenity = (id) => {
    setAmenities((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id]
    );

    markFilterChanged("amenities");
  };

  // Shared request handler for searching and assistant messages.
  const sendMessage = async (
    message,
    applyFilters = false,
    source = "search"
  ) => {
    if (loading) return false;

    const finalMessage = message.trim();

    if (
      !finalMessage &&
      (!applyFilters || !searchPreferences?.city)
    ) {
      setError(
        "Enter a city or describe the homes you want first."
      );
      return false;
    }

    const manualFilters = {};

    if (applyFilters) {
      if (dirtyFilters.includes("bedrooms")) {
        manualFilters.min_bedrooms = bedrooms
          ? Number(bedrooms)
          : null;
      }

      if (dirtyFilters.includes("bathrooms")) {
        manualFilters.min_bathrooms = bathrooms
          ? Number(bathrooms)
          : null;
      }

      if (dirtyFilters.includes("maxPrice")) {
        manualFilters.max_price = maxPrice
          ? Number(maxPrice)
          : null;
      }

      if (dirtyFilters.includes("amenities")) {
        manualFilters.amenities = amenities;
      }
    }

    const userMessage = {
      role: "user",
      content:
        finalMessage ||
        "Apply my selected home search filters",
    };

    setMessages((current) => [...current, userMessage]);
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/ai-chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message:
            finalMessage ||
            "Update my search using the selected filters",
          previous_preferences: searchPreferences,
          previous_results: results,
          ...(applyFilters
            ? { manual_filters: manualFilters }
            : {}),
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();

      const updatedResults = Array.isArray(data.results)
        ? data.results
        : [];

      const assistantMessage = {
        role: "assistant",
        content:
          data.reply ||
          `I found ${updatedResults.length} matching homes.`,
      };

      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);

      const updatedPreferences =
        data.search_preferences || null;

      setSearchPreferences(updatedPreferences);
      syncFiltersWithAI(updatedPreferences);

      setResults(updatedResults);
      setHasSearched(true);
      setDirtyFilters([]);

      if (source === "search") {
        setQuery("");
      }

      return true;
    } catch (err) {
      console.error("AI CHAT ERROR:", err);

      setError(
        "Something went wrong while contacting the AI assistant."
      );

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "I'm having trouble completing that request. Please try again.",
        },
      ]);

      return false;
    } finally {
      setLoading(false);
    }
  };

  // Search for homes using the main search bar.
  const handleSearch = () => {
    sendMessage(
      query,
      messages.length === 0 || dirtyFilters.length > 0,
      "search"
    );
  };

  // Apply filters without needing a new search message.
  const handleApplyFilters = () => {
    sendMessage(query, true, "search");
  };

  // Send a separate assistant message.
  const handleAssistantMessage = async () => {
    const message = chatInput.trim();

    if (!message || loading) return;

    setChatInput("");

    const success = await sendMessage(
      message,
      false,
      "assistant"
    );

    if (!success) {
      setChatInput(message);
    }
  };

  const handleClearFilters = () => {
    setBedrooms("");
    setBathrooms("");
    setMaxPrice("");
    setAmenities([]);

    setDirtyFilters([
      "bedrooms",
      "bathrooms",
      "maxPrice",
      "amenities",
    ]);
  };

  const handleNewSearch = () => {
    if (loading) return;

    setQuery("");
    setChatInput("");
    setMessages([]);
    setSearchPreferences(null);
    setResults([]);
    setHasSearched(false);
    setError("");
    setBedrooms("");
    setBathrooms("");
    setMaxPrice("");
    setAmenities([]);
    setDirtyFilters([]);
    setSortBy("match");
  };

  const sortedResults = [...results].sort((a, b) => {
    if (sortBy === "price-low") {
      return (
        (a.price ?? Infinity) -
        (b.price ?? Infinity)
      );
    }

    if (sortBy === "price-high") {
      return (
        (b.price ?? -Infinity) -
        (a.price ?? -Infinity)
      );
    }

    return (
      (b.match_score ?? 0) -
      (a.match_score ?? 0)
    );
  });

  // Reusable filters for homepage and results sidebar.
  const renderFilters = (prefix) => (
    <section
      className={`filter-section ${
        prefix === "landing"
          ? "landing-filters"
          : "sidebar-filters"
      }`}
    >
      <div className="filter-heading">
        <h2>Refine Your Search</h2>
        <p>Choose the features that matter most to you.</p>
      </div>

      <div className="filter-grid">
        <div className="filter-field">
          <label htmlFor={`${prefix}-bedrooms`}>
            Bedrooms
          </label>

          <select
            id={`${prefix}-bedrooms`}
            value={bedrooms}
            onChange={(event) => {
              setBedrooms(event.target.value);
              markFilterChanged("bedrooms");
            }}
          >
            <option value="">Any</option>

            {[1, 2, 3, 4, 5].map((number) => (
              <option key={number} value={number}>
                {number}+
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor={`${prefix}-bathrooms`}>
            Bathrooms
          </label>

          <select
            id={`${prefix}-bathrooms`}
            value={bathrooms}
            onChange={(event) => {
              setBathrooms(event.target.value);
              markFilterChanged("bathrooms");
            }}
          >
            <option value="">Any</option>

            {[1, 2, 3, 4, 5].map((number) => (
              <option key={number} value={number}>
                {number}+
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor={`${prefix}-maxPrice`}>
            Maximum Price
          </label>

          <select
            id={`${prefix}-maxPrice`}
            value={maxPrice}
            onChange={(event) => {
              setMaxPrice(event.target.value);
              markFilterChanged("maxPrice");
            }}
          >
            <option value="">Any Price</option>

            {priceOptions.map((price) => (
              <option key={price} value={price}>
                ${price.toLocaleString()}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="amenity-section">
        <h3>Nearby Amenities</h3>

        <div className="amenity-options">
          {amenityOptions.map((amenity) => {
            const selected = amenities.includes(amenity.id);

            return (
              <button
                type="button"
                key={amenity.id}
                className={`amenity-chip ${
                  selected ? "selected" : ""
                }`}
                aria-pressed={selected}
                onClick={() => toggleAmenity(amenity.id)}
              >
                <span>{amenity.icon}</span>
                {amenity.label}
                {selected && <span>✓</span>}
              </button>
            );
          })}
        </div>
      </div>

      <div className="filter-actions">
        <button
          type="button"
          className="clear-filters"
          onClick={handleClearFilters}
          disabled={loading}
        >
          Clear Filters
        </button>

        <button
          type="button"
          className="apply-filters"
          onClick={handleApplyFilters}
          disabled={loading}
        >
          {loading
            ? "Searching..."
            : "Find Matching Homes"}
        </button>
      </div>
    </section>
  );

  // AI assistant conversation with its own input bar.
  const renderAIChat = () => (
    <section className="ai-chat-section sidebar-chat">
      <div className="ai-chat-container">
        <div className="ai-chat-header">
          <div>
            <h2>✨ RealestateAI Assistant</h2>

            <p>
              Ask questions about homes or refine your search.
            </p>
          </div>
        </div>

        <div
          className="ai-chat-messages"
          role="log"
          aria-live="polite"
        >
          {messages.length === 0 && (
            <div className="ai-chat-welcome">
              <p>
                Hi! I'm your RealestateAI assistant.
                How can I help you find your perfect home?
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`ai-chat-message ${
                message.role === "user"
                  ? "ai-chat-user"
                  : "ai-chat-assistant"
              }`}
            >
              <div className="ai-chat-avatar">
                {message.role === "user" ? "👤" : "✨"}
              </div>

              <div className="ai-chat-bubble">
                <strong>
                  {message.role === "user"
                    ? "You"
                    : "RealestateAI"}
                </strong>

                <p>{message.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="ai-chat-message ai-chat-assistant">
              <div className="ai-chat-avatar">✨</div>

              <div className="ai-chat-bubble">
                <strong>RealestateAI</strong>
                <p>Thinking...</p>
              </div>
            </div>
          )}
        </div>

        {/* SEPARATE AI ASSISTANT INPUT */}
        <div className="ai-chat-input-area">
          <textarea
            value={chatInput}
            onChange={(event) =>
              setChatInput(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey &&
                !event.nativeEvent.isComposing
              ) {
                event.preventDefault();
                handleAssistantMessage();
              }
            }}
            placeholder="Ask RealestateAI a question..."
            rows={2}
            aria-label="Ask RealestateAI"
          />

          <button
            type="button"
            onClick={handleAssistantMessage}
            disabled={loading || !chatInput.trim()}
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </section>
  );

  return (
    <main
      className={
        hasSearched
          ? "search-results-page"
          : "home-landing-page"
      }
    >
      {/* BEFORE SEARCHING */}
      {!hasSearched && (
        <>
          <section className="hero-section">
            <div className="hero-content">
              <span className="hero-eyebrow">
                ✨ AI-Powered Home Finder
              </span>

              <h1>Find a home that fits your life.</h1>

              <p>
                Discover homes personalized to your budget,
                preferences, and lifestyle.
              </p>

              <div className="hero-search">
                <input
                  type="text"
                  value={query}
                  onChange={(event) =>
                    setQuery(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      handleSearch();
                    }
                  }}
                  placeholder="Describe your dream home..."
                  aria-label="Search for homes"
                />

                <button
                  type="button"
                  onClick={handleSearch}
                  disabled={loading || !query.trim()}
                >
                  {loading
                    ? "Searching..."
                    : "Search Homes"}
                </button>
              </div>

              {loading && (
                <p className="search-loading-text">
                  Finding homes that match your preferences...
                </p>
              )}

              {error && (
                <p className="error-message">{error}</p>
              )}
            </div>
          </section>

          {renderFilters("landing")}
        </>
      )}

      {/* AFTER SEARCHING */}
      {hasSearched && (
        <div className="search-workspace">

          {/* LEFT SIDE */}
          <aside className="search-sidebar">
            <div className="sidebar-top">
              <div>
                <span className="sidebar-eyebrow">
                  ✨ AI-Powered Home Search
                </span>

                <h2>Find Your Home</h2>
                <p>Search and refine your results.</p>
              </div>

              <button
                type="button"
                className="new-ai-search"
                onClick={handleNewSearch}
                disabled={loading}
              >
                + Start New Search
              </button>
            </div>

            {/* PROPERTY SEARCH BAR */}
            <div className="sidebar-search">
              <label htmlFor="sidebar-query">
                Search Homes
              </label>

              <textarea
                id="sidebar-query"
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey &&
                    !event.nativeEvent.isComposing
                  ) {
                    event.preventDefault();

                    if (query.trim() && !loading) {
                      handleSearch();
                    }
                  }
                }}
                placeholder="Example: 3 bedroom homes under $400,000 in Charlotte..."
                rows={3}
              />

              <button
                type="button"
                className="sidebar-search-button"
                onClick={handleSearch}
                disabled={loading || !query.trim()}
              >
                {loading
                  ? "Searching..."
                  : "Search Homes"}
              </button>
            </div>

            {renderFilters("sidebar")}

            {error && (
              <p className="error-message">{error}</p>
            )}

            {/* AI ASSISTANT WITH ITS OWN CHAT BAR */}
            {renderAIChat()}
          </aside>

          {/* RIGHT SIDE */}
          <section className="search-results-column">
            <div className="results-section realestate-results">
              <div className="results-header">
                <div>
                  <span className="results-eyebrow">
                    Personalized Recommendations
                  </span>

                  <h2>
                    Homes Matched to Your Preferences
                  </h2>

                  <p>
                    {results.length}{" "}
                    {results.length === 1
                      ? "home"
                      : "homes"}{" "}
                    found
                    {searchPreferences?.city
                      ? ` in ${searchPreferences.city}`
                      : ""}
                  </p>
                </div>

                {results.length > 0 && (
                  <div className="filter-field sort-field">
                    <label htmlFor="sortBy">
                      Sort By
                    </label>

                    <select
                      id="sortBy"
                      value={sortBy}
                      onChange={(event) =>
                        setSortBy(event.target.value)
                      }
                    >
                      <option value="match">
                        Best AI Match
                      </option>

                      <option value="price-low">
                        Price: Low to High
                      </option>

                      <option value="price-high">
                        Price: High to Low
                      </option>
                    </select>
                  </div>
                )}
              </div>

              {loading && (
                <div className="empty-state">
                  <h3>Finding your matches...</h3>
                  <p>
                    Our AI is analyzing available properties.
                  </p>
                </div>
              )}

              {!loading && results.length === 0 && (
                <div className="empty-state">
                  <h3>No homes found</h3>
                  <p>
                    Try adjusting your search requirements
                    or ask the AI to broaden your search.
                  </p>
                </div>
              )}

              {!loading && sortedResults.length > 0 && (
                <div className="home-list">
                  {sortedResults.map((home, index) => (
                    <HomeCard
                      key={home.id ?? index}
                      home={home}
                      isLiked={likedHomes.some(
                        (liked) => liked.id === home.id
                      )}
                      toggleLike={toggleLike}
                    />
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

export default Home;
