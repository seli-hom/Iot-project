import { Link } from "react-router-dom";

export default function NavBar() {
  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow">
      <div className="container">
        <Link className="navbar-brand fw-bold fs-4" to="/">
          IoT Project
        </Link>

        <div className="ms-auto text-white">
          {user ? (
            <span>
              Welcome back, <strong>{user.first_name}</strong>
            </span>
          ) : (
            <span>Welcome, Anonymous</span>
          )}
        </div>

      </div>
    </nav>
  );
}