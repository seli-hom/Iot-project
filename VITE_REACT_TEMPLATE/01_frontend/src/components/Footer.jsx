import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="bg-primary text-white py-4 mt-auto">
      <div className="container d-flex justify-content-between align-items-center">
        <span>&copy; {new Date().getFullYear()} IoT Project</span>
        <div>
          <Link to="/" className="text-white me-3 text-decoration-none">
            Home
          </Link>
          <Link to="/registration" className="text-white text-decoration-none">
            Register
          </Link>
        </div>
      </div>
    </footer>
  );
}