import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function RegisterPage() {
  const [form, setForm] = useState({});
  const [flash, setFlash] = useState(null);
  const navigate = useNavigate();

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }
  async function handleSubmit(e) {
    e.preventDefault();
    setFlash(null);

    try {
      const response = await fetch("http://localhost:5000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (response.ok) {
        setFlash({ type: "success", message: data.message || "Registration successful!" });
        setTimeout(() => navigate("/login"), 2000);
      } else {
        setFlash({ type: "error", message: data.error || "Registration failed!" });
      }
    } catch (err) {
      setFlash({ type: "error", message: "Network error. Please try again." });
    }
  }

  return (
    <div className="container py-5 d-flex justify-content-center">
      <div style={{ maxWidth: "600px", width: "100%" }}>
        <h2 className="text-primary fw-bold mb-3 text-center">Register</h2>

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
          <div className="col-md-6">
            <label className="form-label">First Name</label>
            <input
              type="text"
              className="form-control"
              name="fname"
              required
              onChange={handleChange}
            />
          </div>

          <div className="col-md-6">
            <label className="form-label">Last Name</label>
            <input
              type="text"
              className="form-control"
              name="lname"
              required
              onChange={handleChange}
            />
          </div>

          <div className="col-12">
            <label className="form-label">Address</label>
            <input
              type="text"
              className="form-control"
              name="address"
              required
              onChange={handleChange}
            />
          </div>

          <div className="col-12">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-control"
              name="email"
              required
              onChange={handleChange}
            />
          </div>

          <div className="col-12">
            <label className="form-label">Phone</label>
            <input
              type="text"
              className="form-control"
              name="phone"
              required
              onChange={handleChange}
            />
          </div>

          <div className="col-12">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-control"
              name="password"
              required
              onChange={handleChange}
            />
          </div>

          <div className="col-12 d-grid">
            <button type="submit" className="btn btn-primary">
              Register
            </button>
          </div>

          <div className="col-12 text-center mt-3">
            <p>
              Already have an account?{" "}
              <Link to="/login" className="text-primary text-decoration-underline">
                Login
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}