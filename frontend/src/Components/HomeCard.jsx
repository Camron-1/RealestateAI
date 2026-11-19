
import HomeImageGallery from "../Home_Gallery";

function HomeCard({ home, isLiked, toggleLike }) {
  const address = home.address || {};

  const street = [
    address.streetNumber,
    address.streetDirection,
    address.streetName,
    address.streetSuffix,
  ]
    .filter(Boolean)
    .join(" ");

  const cityState = [
    address.city,
    address.state,
    address.zip,
  ]
    .filter(Boolean)
    .join(", ");

  const amenities = [
    ["hospital", "🏥"],
    ["school", "🏫"],
    ["park", "🌳"],
    ["dog_park", "🐕"],
    ["playground", "🛝"],
  ];

  return (
    <article className="home-card">
      <div className="home-card-image">
        <HomeImageGallery images={home.images} />

        <button
          type="button"
          className={`like-button ${isLiked ? "liked" : ""}`}
          onClick={() => toggleLike(home)}
          aria-label={isLiked ? "Remove saved home" : "Save home"}
          aria-pressed={isLiked}
        >
          {isLiked ? "♥" : "♡"}
        </button>
      </div>

      <div className="home-card-content">
        <div className="home-card-heading">
          <h3>
            {home.price != null
              ? `$${home.price.toLocaleString()}`
              : "Price unavailable"}
          </h3>

          {home.match_score != null && (
            <span className="match-score">
              {home.match_score}% Match
            </span>
          )}
        </div>

        <p className="home-specs">
          {home.bedrooms ?? "—"} beds •{" "}
          {home.bathrooms ?? "—"} baths •{" "}
          {home.sqft?.toLocaleString() ?? "—"} sqft
        </p>

        <p className="home-address">
          {street}
          {address.unit ? `, Unit ${address.unit}` : ""}
        </p>

        <p className="home-location">{cityState}</p>

        <div className="nearby-places">
          <h4>Nearby Amenities</h4>

          {amenities.map(([type, icon]) => {
            const place = home.nearby?.[type];

            if (!place) return null;

            return (
              <p key={type}>
                {icon} {place.name || type.replace("_", " ")}
                {place.distance_miles != null &&
                  ` — ${place.distance_miles} miles`}
              </p>
            );
          })}
        </div>
      </div>
    </article>
  );
}

export default HomeCard;
