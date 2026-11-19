
import { Link } from "react-router-dom";
import HomeCard from "../Components/HomeCard";
function LikedHomes({ likedHomes = [], toggleLike }) {
  return (
    <main className="main-content">
      <section className="page-heading">
        <h1>My Liked Homes</h1>
        <p>All your favorite properties in one place.</p>
      </section>

      {likedHomes.length === 0 ? (
        <div className="empty-state">
          <h2>No saved homes yet</h2>

          <p>
            Click the heart icon on any listing to save it here.
          </p>

          <Link to="/" className="primary-link">
            Explore Homes
          </Link>
        </div>
      ) : (
        <>
          <p>
            You have saved {likedHomes.length}{" "}
            {likedHomes.length === 1 ? "home" : "homes"}.
          </p>

          <div className="home-list">
            {likedHomes.map((home, index) => (
              <HomeCard
                key={home.id ?? index}
                home={home}
                isLiked={true}
                toggleLike={toggleLike}
              />
            ))}
          </div>
        </>
      )}
    </main>
  );
}

export default LikedHomes;
