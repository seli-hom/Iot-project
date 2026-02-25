import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [flash, setFlash] = useState(null);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      let data;
      try {
        data = await response.json();
      } catch {
        data = {};
      }

      if (response.ok) {
        localStorage.setItem("user", JSON.stringify(data.user));
        navigate("/", {
          state: { flash: { type: "success", message: "Login successful!" } },
        });
      } else if (data?.error) {
        setFlash({ type: "error", message: data.error });
      } else {
        setFlash({ type: "error", message: "Login failed. Please try again." });
      }
    } catch (err) {
      setFlash({ type: "error", message: "Network error. Please check your connection." });
    }
  }

  return (
    <div className="container py-5 d-flex justify-content-center">
      <div style={{ maxWidth: "400px", width: "100%" }}>
        <h2 className="text-primary fw-bold mb-3 text-center">Login</h2>

        {flash && (
          <div
            className={`alert alert-${flash.type === "success" ? "success" : "danger"} alert-dismissible fade show`}
            role="alert"
          >
            {flash.message}
            <button
              type="button"
              className="btn-close"
              aria-label="Close"
              onClick={() => setFlash(null)}
            ></button>
          </div>
        )}

        <form className="row g-3" onSubmit={handleSubmit}>
          <div className="col-12">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-control"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="col-12">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-control"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="col-12 d-grid">
            <button type="submit" className="btn btn-primary">
              Login
            </button>
          </div>

          <div className="col-12 text-center mt-3">
            <p>
              Don’t have an account?{" "}
              <Link to="/registration" className="text-primary text-decoration-underline">
                Sign up
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}