"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function NotFoundContent() {
  const searchParams = useSearchParams();
  const reason = searchParams.get("reason");

  let title = "Link not found";
  let message = "The link you clicked doesn't exist or may have been deleted.";
  let icon = "🤔";

  if (reason === "expired") {
    title = "Link expired";
    message = "This link was set to expire and is no longer active.";
    icon = "⏳";
  } else if (reason === "inactive") {
    title = "Link deactivated";
    message = "The creator of this link has temporarily deactivated it.";
    icon = "⏸️";
  }

  return (
    <div style={{ position: "relative", overflowX: "hidden", minHeight: "100vh" }}>
      {/* Background glow orbs */}
      <div
        className="glow-orb"
        style={{
          width: "500px",
          height: "500px",
          background: "radial-gradient(circle, rgba(239, 68, 68, 0.15) 0%, transparent 70%)",
          top: "100px",
          left: "50%",
          transform: "translateX(-50%)",
        }}
      />

      <section
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "2rem",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div
          className="glass-card fade-in"
          style={{
            maxWidth: "480px",
            width: "100%",
            padding: "3.5rem 2.5rem",
            textAlign: "center",
            boxShadow: "0 24px 80px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05)",
          }}
        >
          <div style={{ fontSize: "4.5rem", marginBottom: "1.5rem" }}>{icon}</div>
          <h1
            style={{
              fontSize: "2rem",
              fontWeight: 800,
              marginBottom: "1rem",
              letterSpacing: "-0.02em",
            }}
          >
            {title}
          </h1>
          <p
            style={{
              color: "var(--text-secondary)",
              fontSize: "1.1rem",
              lineHeight: 1.6,
              marginBottom: "2.5rem",
            }}
          >
            {message}
          </p>

          <Link
            href="/"
            className="btn-primary pulse-glow"
            style={{
              display: "inline-block",
              padding: "0.8rem 2rem",
              fontSize: "1rem",
              textDecoration: "none",
            }}
          >
            Create your own short link
          </Link>
        </div>
      </section>
    </div>
  );
}

export default function NotFoundPage() {
  return (
    <Suspense fallback={
      <div style={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div className="spinner" style={{ width: 32, height: 32 }} />
      </div>
    }>
      <NotFoundContent />
    </Suspense>
  );
}
