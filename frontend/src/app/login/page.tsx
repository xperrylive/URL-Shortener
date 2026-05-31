"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { APIError } from "@/lib/api";
import type { Metadata } from "next";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.detail);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "5rem 1.5rem 2rem",
        position: "relative",
      }}
    >
      {/* Glow orb */}
      <div
        className="glow-orb"
        style={{
          width: "500px",
          height: "500px",
          background: "radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%)",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
        }}
      />

      <div
        className="glass-card fade-in"
        style={{
          width: "100%",
          maxWidth: "420px",
          padding: "2.5rem",
          position: "relative",
          zIndex: 1,
          boxShadow: "0 24px 80px rgba(0,0,0,0.5)",
        }}
      >
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <Link href="/" style={{ textDecoration: "none" }}>
            <span
              style={{
                fontSize: "1.5rem",
                fontWeight: 800,
                background: "linear-gradient(135deg, #a78bfa 0%, #22d3ee 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              Lynk
            </span>
          </Link>
          <h1
            style={{
              fontSize: "1.4rem",
              fontWeight: 700,
              marginTop: "1rem",
              marginBottom: "0.4rem",
              letterSpacing: "-0.02em",
            }}
          >
            Welcome back
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            Sign in to your account to continue
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {/* Email */}
          <div>
            <label
              htmlFor="login-email"
              style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "0.4rem" }}
            >
              Email address
            </label>
            <input
              id="login-email"
              type="email"
              className="input-field"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="login-password"
              style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "0.4rem" }}
            >
              Password
            </label>
            <input
              id="login-password"
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {/* Error */}
          {error && (
            <div
              style={{
                padding: "0.75rem 1rem",
                borderRadius: "10px",
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.2)",
                color: "#f87171",
                fontSize: "0.875rem",
              }}
            >
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            id="login-submit"
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ height: "46px", marginTop: "0.25rem", fontSize: "0.95rem" }}
          >
            {loading ? <span className="spinner" /> : null}
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            marginTop: "1.5rem",
            fontSize: "0.875rem",
            color: "var(--text-secondary)",
          }}
        >
          Don't have an account?{" "}
          <Link
            href="/register"
            style={{ color: "var(--purple-400)", textDecoration: "none", fontWeight: 600 }}
          >
            Sign up free
          </Link>
        </p>
      </div>
    </div>
  );
}
