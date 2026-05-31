"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { APIError } from "@/lib/api";

const PASSWORD_HINTS = [
  { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
  { label: "One uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: "One digit", test: (p: string) => /[0-9]/.test(p) },
];

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showHints, setShowHints] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const passwordStrength = PASSWORD_HINTS.filter((h) => h.test(password)).length;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await register(email, password);
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

  const strengthColor =
    passwordStrength === 3 ? "#4ade80" : passwordStrength >= 2 ? "#facc15" : "#f87171";

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
          background: "radial-gradient(circle, rgba(6, 182, 212, 0.12) 0%, transparent 70%)",
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
            Create your account
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            Free forever · No credit card required
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {/* Email */}
          <div>
            <label
              htmlFor="reg-email"
              style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "0.4rem" }}
            >
              Email address
            </label>
            <input
              id="reg-email"
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
              htmlFor="reg-password"
              style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "0.4rem" }}
            >
              Password
            </label>
            <input
              id="reg-password"
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setShowHints(true);
              }}
              required
              autoComplete="new-password"
            />

            {/* Strength bar */}
            {showHints && password.length > 0 && (
              <div style={{ marginTop: "0.6rem" }}>
                <div
                  style={{
                    display: "flex",
                    gap: "4px",
                    marginBottom: "0.5rem",
                  }}
                >
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      style={{
                        flex: 1,
                        height: "4px",
                        borderRadius: "2px",
                        background: i < passwordStrength ? strengthColor : "rgba(255,255,255,0.08)",
                        transition: "background 0.3s ease",
                      }}
                    />
                  ))}
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                  {PASSWORD_HINTS.map((h) => (
                    <div
                      key={h.label}
                      style={{
                        fontSize: "0.75rem",
                        color: h.test(password) ? "#4ade80" : "var(--text-muted)",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.4rem",
                        transition: "color 0.2s ease",
                      }}
                    >
                      {h.test(password) ? "✓" : "○"} {h.label}
                    </div>
                  ))}
                </div>
              </div>
            )}
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
            id="register-submit"
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ height: "46px", marginTop: "0.25rem", fontSize: "0.95rem" }}
          >
            {loading ? <span className="spinner" /> : null}
            {loading ? "Creating account..." : "Create free account"}
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
          Already have an account?{" "}
          <Link
            href="/login"
            style={{ color: "var(--purple-400)", textDecoration: "none", fontWeight: 600 }}
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
