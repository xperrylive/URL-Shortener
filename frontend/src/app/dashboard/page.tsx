"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { urlsAPI, type ShortURL, type URLListResponse, APIError } from "@/lib/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      title="Copy short URL"
      onClick={async () => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      style={{
        background: copied ? "rgba(74, 222, 128, 0.12)" : "rgba(255,255,255,0.05)",
        border: `1px solid ${copied ? "rgba(74,222,128,0.25)" : "rgba(255,255,255,0.08)"}`,
        color: copied ? "#4ade80" : "var(--text-secondary)",
        borderRadius: "7px",
        padding: "0.3rem 0.65rem",
        fontSize: "0.75rem",
        cursor: "pointer",
        fontWeight: 500,
        transition: "all 0.2s ease",
        whiteSpace: "nowrap",
      }}
    >
      {copied ? "✓ Copied" : "Copy"}
    </button>
  );
}

function DeleteButton({ onDelete }: { onDelete: () => Promise<void> }) {
  const [confirming, setConfirming] = useState(false);
  const [loading, setLoading] = useState(false);

  if (confirming) {
    return (
      <div style={{ display: "flex", gap: "0.4rem" }}>
        <button
          onClick={async () => {
            setLoading(true);
            await onDelete();
            setLoading(false);
            setConfirming(false);
          }}
          disabled={loading}
          style={{
            background: "rgba(239,68,68,0.15)",
            border: "1px solid rgba(239,68,68,0.3)",
            color: "#f87171",
            borderRadius: "7px",
            padding: "0.3rem 0.6rem",
            fontSize: "0.75rem",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          {loading ? "..." : "Confirm"}
        </button>
        <button
          onClick={() => setConfirming(false)}
          style={{
            background: "transparent",
            border: "1px solid rgba(255,255,255,0.08)",
            color: "var(--text-muted)",
            borderRadius: "7px",
            padding: "0.3rem 0.6rem",
            fontSize: "0.75rem",
            cursor: "pointer",
          }}
        >
          Cancel
        </button>
      </div>
    );
  }

  return (
    <button
      title="Deactivate link"
      onClick={() => setConfirming(true)}
      style={{
        background: "transparent",
        border: "1px solid rgba(255,255,255,0.08)",
        color: "var(--text-muted)",
        borderRadius: "7px",
        padding: "0.3rem 0.6rem",
        fontSize: "0.75rem",
        cursor: "pointer",
        transition: "all 0.2s ease",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(239,68,68,0.3)";
        (e.currentTarget as HTMLButtonElement).style.color = "#f87171";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(255,255,255,0.08)";
        (e.currentTarget as HTMLButtonElement).style.color = "var(--text-muted)";
      }}
    >
      Delete
    </button>
  );
}

export default function DashboardPage() {
  const { isAuthenticated, loading: authLoading, user } = useAuth();
  const router = useRouter();

  const [data, setData] = useState<URLListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [shortenUrl, setShortenUrl] = useState("");
  const [shortenAlias, setShortenAlias] = useState("");
  const [shortenLoading, setShortenLoading] = useState(false);
  const [shortenError, setShortenError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  const fetchURLs = useCallback(async (p = 1) => {
    setFetchLoading(true);
    try {
      const res = await urlsAPI.list(p, 8);
      setData(res);
      setPage(p);
    } catch (_) {}
    finally { setFetchLoading(false); }
  }, []);

  useEffect(() => {
    if (isAuthenticated) fetchURLs(1);
  }, [isAuthenticated, fetchURLs]);

  const handleShorten = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!shortenUrl.trim()) return;
    setShortenLoading(true);
    setShortenError(null);
    try {
      await urlsAPI.shorten(shortenUrl.trim(), shortenAlias.trim() || undefined);
      setShortenUrl("");
      setShortenAlias("");
      fetchURLs(1);
    } catch (err) {
      if (err instanceof APIError) setShortenError(err.detail);
      else setShortenError("Something went wrong.");
    } finally {
      setShortenLoading(false);
    }
  };

  const handleDelete = async (short_code: string) => {
    await urlsAPI.delete(short_code);
    fetchURLs(page);
  };

  if (authLoading) {
    return (
      <div style={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div className="spinner" style={{ width: 32, height: 32 }} />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  const totalClicks = data?.items.reduce((acc, u) => acc + u.click_count, 0) ?? 0;

  return (
    <div
      style={{
        maxWidth: "1000px",
        margin: "0 auto",
        padding: "5.5rem 1.5rem 4rem",
        position: "relative",
      }}
    >
      {/* Glow */}
      <div
        className="glow-orb"
        style={{
          width: "500px",
          height: "300px",
          background: "radial-gradient(ellipse, rgba(139, 92, 246, 0.1) 0%, transparent 70%)",
          top: "0",
          left: "50%",
          transform: "translateX(-50%)",
        }}
      />

      {/* ── Header ── */}
      <div className="fade-in" style={{ marginBottom: "2rem", position: "relative", zIndex: 1 }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 800, letterSpacing: "-0.02em" }}>
          Dashboard
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginTop: "0.3rem" }}>
          Welcome back, <strong style={{ color: "var(--text-primary)" }}>{user?.email}</strong>
        </p>
      </div>

      {/* ── Stats Cards ── */}
      <div
        className="fade-in-delay-1"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "1rem",
          marginBottom: "2rem",
          position: "relative",
          zIndex: 1,
        }}
      >
        {[
          { label: "Total links", value: data?.total ?? 0, icon: "🔗" },
          { label: "Total clicks", value: totalClicks, icon: "👆" },
          { label: "Active links", value: data?.items.filter((u) => u.is_active).length ?? 0, icon: "✅" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="glass-card"
            style={{ padding: "1.25rem 1.5rem" }}
          >
            <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{stat.icon}</div>
            <div style={{ fontSize: "1.8rem", fontWeight: 800, letterSpacing: "-0.02em" }}>
              {stat.value}
            </div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* ── Shorten Box ── */}
      <div
        className="glass-card fade-in-delay-2"
        style={{ padding: "1.5rem", marginBottom: "2rem", position: "relative", zIndex: 1 }}
      >
        <h2 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "1rem" }}>
          ✦ Shorten a new URL
        </h2>
        <form onSubmit={handleShorten} style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <input
            type="url"
            className="input-field"
            placeholder="https://example.com/long-url"
            value={shortenUrl}
            onChange={(e) => setShortenUrl(e.target.value)}
            required
            style={{ flex: "2 1 260px", minWidth: 0 }}
          />
          <input
            type="text"
            className="input-field mono"
            placeholder="custom-alias (optional)"
            value={shortenAlias}
            onChange={(e) => setShortenAlias(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ""))}
            style={{ flex: "1 1 160px", minWidth: 0 }}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={shortenLoading}
            style={{ flex: "0 0 auto", height: "44px", padding: "0 1.25rem" }}
          >
            {shortenLoading ? <span className="spinner" /> : "Shorten"}
          </button>
        </form>
        {shortenError && (
          <p style={{ color: "#f87171", fontSize: "0.82rem", marginTop: "0.5rem" }}>{shortenError}</p>
        )}
      </div>

      {/* ── Links Table ── */}
      <div style={{ position: "relative", zIndex: 1 }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "1rem",
          }}
        >
          <h2 style={{ fontSize: "0.95rem", fontWeight: 700 }}>Your links</h2>
          {data && (
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              {data.total} total
            </span>
          )}
        </div>

        {fetchLoading ? (
          <div
            style={{
              height: "200px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div className="spinner" style={{ width: 28, height: 28 }} />
          </div>
        ) : !data || data.items.length === 0 ? (
          <div
            className="glass-card"
            style={{ padding: "3rem", textAlign: "center", color: "var(--text-muted)" }}
          >
            <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>🔗</div>
            <p style={{ fontWeight: 600, marginBottom: "0.4rem" }}>No links yet</p>
            <p style={{ fontSize: "0.875rem" }}>Shorten your first URL above to get started</p>
          </div>
        ) : (
          <>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem" }}>
              {data.items.map((url) => (
                <div
                  key={url.id}
                  className="glass-card glass-card-hover"
                  style={{
                    padding: "1rem 1.25rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "1rem",
                    flexWrap: "wrap",
                    opacity: url.is_active ? 1 : 0.5,
                  }}
                >
                  {/* Short code + status */}
                  <div style={{ flex: "0 0 auto", minWidth: "100px" }}>
                    <a
                      href={`${BASE_URL}/${url.short_code}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mono"
                      style={{
                        fontSize: "0.9rem",
                        fontWeight: 600,
                        color: url.is_active ? "var(--purple-400)" : "var(--text-muted)",
                        textDecoration: "none",
                      }}
                    >
                      /{url.short_code}
                    </a>
                    <div style={{ marginTop: "0.2rem" }}>
                      <span className={`badge ${url.is_active ? "badge-green" : "badge-red"}`}>
                        {url.is_active ? "Active" : "Inactive"}
                      </span>
                    </div>
                  </div>

                  {/* Original URL */}
                  <div style={{ flex: "1 1 200px", minWidth: 0 }}>
                    <div
                      style={{
                        fontSize: "0.82rem",
                        color: "var(--text-secondary)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                      title={url.original_url}
                    >
                      {url.original_url}
                    </div>
                    <div style={{ fontSize: "0.73rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>
                      {new Date(url.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </div>
                  </div>

                  {/* Click count */}
                  <div style={{ flex: "0 0 auto", textAlign: "center", minWidth: "60px" }}>
                    <div style={{ fontSize: "1.2rem", fontWeight: 700 }}>{url.click_count}</div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>clicks</div>
                  </div>

                  {/* Actions */}
                  <div style={{ flex: "0 0 auto", display: "flex", gap: "0.4rem", alignItems: "center" }}>
                    <CopyButton text={`${BASE_URL}/${url.short_code}`} />
                    {url.is_active && (
                      <DeleteButton onDelete={() => handleDelete(url.short_code)} />
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: "0.5rem",
                  marginTop: "1.5rem",
                }}
              >
                <button
                  onClick={() => fetchURLs(page - 1)}
                  disabled={page <= 1}
                  className="btn-secondary"
                  style={{ padding: "0.4rem 1rem", fontSize: "0.82rem" }}
                >
                  ← Previous
                </button>
                <span
                  style={{
                    display: "flex",
                    alignItems: "center",
                    fontSize: "0.82rem",
                    color: "var(--text-muted)",
                    padding: "0 0.5rem",
                  }}
                >
                  Page {page} of {data.pages}
                </span>
                <button
                  onClick={() => fetchURLs(page + 1)}
                  disabled={page >= data.pages}
                  className="btn-secondary"
                  style={{ padding: "0.4rem 1rem", fontSize: "0.82rem" }}
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
