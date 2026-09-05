import { NavLink } from "react-router-dom";

export default function NavBar() {
  return (
    <nav className="navbar">
      <NavLink to="/discover" className={({ isActive }) => (isActive ? "nav-link nav-link-active" : "nav-link")}>
        Discover
      </NavLink>
      <NavLink to="/matches" className={({ isActive }) => (isActive ? "nav-link nav-link-active" : "nav-link")}>
        Matches
      </NavLink>
      <NavLink to="/profile" className={({ isActive }) => (isActive ? "nav-link nav-link-active" : "nav-link")}>
        Profile
      </NavLink>
    </nav>
  );
}
