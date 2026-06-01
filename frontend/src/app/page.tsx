"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { urlsAPI, type ShortURL, APIError } from "@/lib/api";

const FEATURES = [
  {
    icon: "⚡",
    title: "Blazing fast redirects",
    desc: "Redis-first caching delivers sub-millisecond redirects globally.",
  },
  {
    icon: "📊",
    title: "Real-time analytics",
    desc: "Track clicks, devices, and referrers from your dashboard.",
  },
  {
    icon: "🔒",
    title: "Secure & reliable",
    desc: "HTTPS enforced, bcrypt auth, rate-limited endpoints.",
  },
  {
    icon: "🎯",
    title: "Custom aliases",
    desc: "Brand your links with memorable custom slugs.",
  },
];

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={handleCopy} className="btn-secondary" style={{ fontSize: "0.82rem", padding: "0.45rem 0.9rem" }}>
      {copied ? "✓ Copied!" : "Copy"}
    </button>
  );
}

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [alias, setAlias] = useState("");
  const [result, setResult] = useState<ShortURL | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [authLoading, isAuthenticated, router]);

  const handleShorten = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await urlsAPI.shorten(url.trim(), alias.trim() || undefined);
      setResult(data);
      setUrl("");
      setAlias("");
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

  if (authLoading || isAuthenticated) {
    return null; // prevent flash of landing page while redirecting
  }

  return (
    <div style={{ position: "relative", overflowX: "hidden" }}>
      {/* Background glow orbs */}
      <div
        className="glow-orb"
        style={{
          width: "600px",
          height: "600px",
          background: "radial-gradient(circle, rgba(139, 92, 246, 0.18) 0%, transparent 70%)",
          top: "-100px",
          left: "50%",
          transform: "translateX(-50%)",
        }}
      />
      <div
        className="glow-orb"
        style={{
          width: "400px",
          height: "400px",
          background: "radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 70%)",
          top: "300px",
          right: "-100px",
        }}
      />

      {/* ── Hero Section ── */}
      <section
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "8rem 1.5rem 4rem",
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* Badge */}
        <div className="badge badge-purple fade-in" style={{ marginBottom: "1.5rem" }}>
          <span>✦</span> Free URL Shortener · No signup required
        </div>

        {/* Headline */}
        <h1
          className="fade-in-delay-1"
          style={{
            fontSize: "clamp(2.5rem, 7vw, 4.5rem)",
            fontWeight: 900,
            textAlign: "center",
            lineHeight: 1.1,
            letterSpacing: "-0.03em",
            marginBottom: "1.25rem",
            maxWidth: "800px",
          }}
        >
          Short links,{" "}
          <span className="gradient-text">big impact</span>
        </h1>

        {/* Subheading */}
        <p
          className="fade-in-delay-2"
          style={{
            fontSize: "1.15rem",
            color: "var(--text-secondary)",
            textAlign: "center",
            maxWidth: "520px",
            marginBottom: "3rem",
            lineHeight: 1.7,
          }}
        >
          Create powerful short links in seconds. Track clicks, measure reach, and
          own your brand — no credit card required.
        </p>

        {/* ── Shorten Box ── */}
        <div
          className="glass-card fade-in-delay-3"
          style={{
            width: "100%",
            maxWidth: "620px",
            padding: "2rem",
            boxShadow: "0 24px 80px rgba(0,0,0,0.4), 0 0 0 1px rgba(139,92,246,0.1)",
          }}
        >
          <form onSubmit={handleShorten} style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
            {/* URL input */}
            <div>
              <label
                htmlFor="url-input"
                style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.4rem", display: "block" }}
              >
                Paste your long URL
              </label>
              <input
                id="url-input"
                type="url"
                className="input-field"
                placeholder="https://example.com/very/long/url/here"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
                style={{ fontSize: "1rem" }}
              />
            </div>

            {/* Custom alias (optional) */}
            <div>
              <label
                htmlFor="alias-input"
                style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.4rem", display: "block" }}
              >
                Custom alias{" "}
                <span style={{ color: "#5c5b72", fontStyle: "italic" }}>(optional)</span>
              </label>
              <div style={{ position: "relative" }}>
                <span
                  className="mono"
                  style={{
                    position: "absolute",
                    left: "1rem",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "var(--text-muted)",
                    fontSize: "0.85rem",
                    pointerEvents: "none",
                  }}
                >
                  lynk.io/
                </span>
                <input
                  id="alias-input"
                  type="text"
                  className="input-field mono"
                  placeholder="my-brand"
                  value={alias}
                  onChange={(e) => setAlias(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ""))}
                  style={{ paddingLeft: "5.5rem", fontSize: "0.9rem" }}
                />
              </div>
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

            {/* Result */}
            {result && (
              <div
                style={{
                  padding: "1rem",
                  borderRadius: "10px",
                  background: "rgba(139, 92, 246, 0.08)",
                  border: "1px solid rgba(139, 92, 246, 0.25)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "0.75rem",
                  flexWrap: "wrap",
                }}
              >
                <div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.2rem" }}>
                    Your short link ✓
                  </div>
                  <a
                    href={result.short_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mono"
                    style={{
                      fontSize: "1.05rem",
                      fontWeight: 600,
                      color: "var(--purple-400)",
                      textDecoration: "none",
                    }}
                  >
                    {result.short_url}
                  </a>
                </div>
                <CopyButton text={result.short_url} />
              </div>
            )}

            {/* Submit */}
            <button
              id="shorten-btn"
              type="submit"
              className="btn-primary pulse-glow"
              disabled={loading}
              style={{ height: "48px", fontSize: "1rem" }}
            >
              {loading ? <span className="spinner" /> : null}
              {loading ? "Shortening..." : "✦ Shorten URL"}
            </button>
          </form>

          <p style={{ textAlign: "center", marginTop: "1rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
            <Link
              href="/register"
              style={{ color: "var(--purple-400)", textDecoration: "none" }}
            >
              Sign up free
            </Link>{" "}
            to track clicks and manage your links
          </p>
        </div>

        {/* Stats row */}
        <div
          style={{
            display: "flex",
            gap: "2.5rem",
            marginTop: "3rem",
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          {[
            { value: "< 1ms", label: "Redirect latency" },
            { value: "∞", label: "Links created" },
            { value: "99.9%", label: "Uptime SLA" },
          ].map((s) => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <div
                style={{
                  fontSize: "1.75rem",
                  fontWeight: 800,
                  background: "linear-gradient(135deg, #a78bfa, #22d3ee)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                {s.value}
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features Section ── */}
      <section
        style={{
          padding: "4rem 1.5rem 6rem",
          maxWidth: "1100px",
          margin: "0 auto",
          position: "relative",
          zIndex: 1,
        }}
      >
        <h2
          style={{
            textAlign: "center",
            fontSize: "clamp(1.6rem, 4vw, 2.25rem)",
            fontWeight: 800,
            marginBottom: "0.75rem",
            letterSpacing: "-0.02em",
          }}
        >
          Everything you need
        </h2>
        <p
          style={{
            textAlign: "center",
            color: "var(--text-secondary)",
            fontSize: "1rem",
            marginBottom: "3rem",
          }}
        >
          Built for speed, reliability, and simplicity
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: "1.25rem",
          }}
        >
          {FEATURES.map((f, i) => (
            <div
              key={f.title}
              className="glass-card glass-card-hover"
              style={{
                padding: "1.75rem",
                animationDelay: `${i * 0.1}s`,
              }}
            >
              <div
                style={{
                  fontSize: "2rem",
                  marginBottom: "1rem",
                  width: "52px",
                  height: "52px",
                  borderRadius: "14px",
                  background: "rgba(139, 92, 246, 0.12)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "1px solid rgba(139, 92, 246, 0.2)",
                }}
              >
                {f.icon}
              </div>
              <h3
                style={{
                  fontSize: "1rem",
                  fontWeight: 700,
                  marginBottom: "0.5rem",
                  letterSpacing: "-0.01em",
                }}
              >
                {f.title}
              </h3>
              <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section
        style={{
          padding: "4rem 1.5rem",
          margin: "0 1.5rem 4rem",
          borderRadius: "20px",
          background: "linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%)",
          border: "1px solid rgba(139, 92, 246, 0.2)",
          textAlign: "center",
          position: "relative",
          zIndex: 1,
          maxWidth: "1100px",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        <h2
          style={{
            fontSize: "clamp(1.5rem, 4vw, 2rem)",
            fontWeight: 800,
            marginBottom: "0.75rem",
            letterSpacing: "-0.02em",
          }}
        >
          Ready to take control of your links?
        </h2>
        <p style={{ color: "var(--text-secondary)", marginBottom: "1.75rem", fontSize: "1rem" }}>
          Create your free account and start shortening in 30 seconds.
        </p>
        <Link href="/register" className="btn-primary" style={{ fontSize: "1rem", padding: "0.8rem 2rem" }}>
          Get started — it's free →
        </Link>
      </section>
    </div>
  );
}
