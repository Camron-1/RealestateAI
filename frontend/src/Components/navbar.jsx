
import { NavLink } from "react-router-dom";

function Navbar({ likedCount = 0 }) {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-logo">
        🏠 RealestateAI
      </NavLink>

      <div className="navbar-links">
        <NavLink to="/" end>
          Home
        </NavLink>

        <NavLink to="/liked">
          ♡ Liked Homes ({likedCount})
        </NavLink>

        <NavLink to="/contact">
          Contact Us
        </NavLink>
      </div>
    </nav>
  );
}

export default Navbar;
