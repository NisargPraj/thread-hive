import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const BASE_URL = "http://54.208.64.57:8000/api/users/";

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const [form, setForm] = useState<LoginForm>({ username: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BASE_URL}login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        const errData = await response.json();
        const errorMessage = errData.detail || "Invalid username or password.";
        throw new Error(errorMessage);
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);

      // Redirect to home or profile after login
      navigate("/home/");
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <form className="flex flex-col gap-4 w-1/3" onSubmit={handleSubmit}>
        <h1 className="text-2xl font-bold">Login</h1>
        {error && <div className="text-red-500">{error}</div>}

        <input
          type="text"
          name="username"
          placeholder="Username"
          className="p-2 border border-gray-300 rounded"
          value={form.username}
          onChange={handleChange}
          required
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          className="p-2 border border-gray-300 rounded"
          value={form.password}
          onChange={handleChange}
          required
        />

        <button
          type="submit"
          className="py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        <div className="text-center mt-4">
          <button
            type="button"
            onClick={() => navigate("/register")}
            className="text-blue-500 hover:text-blue-700"
          >
            Don't have an account? Sign up
          </button>
        </div>
      </form>
    </div>
  );
};

export default Login;
