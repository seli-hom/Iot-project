import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="container py-5 text-center">

      <h1 className="text-secondary mb-4">Welcome to the smart store!</h1>
      <h3>please login to continue</h3>
      <p><b>OR</b></p>

      <Link to="/registration" className="btn btn-primary btn-lg">
        Registration Today!
      </Link>

    </div>
  );
}