"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useState } from "react";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    await logout();
    router.push("/");
    setLoggingOut(false);
  };

  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        backdropFilter: "blur(16px)",
        WebkitBackdropFilter: "blur(16px)",
        background: "rgba(10, 10, 15, 0.8)",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "0 1.5rem",
          height: "60px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        {/* Logo */}
        <Link href="/" style={{ textDecoration: "none" }}>
          <span
            style={{
              fontSize: "1.35rem",
              fontWeight: 800,
              background: "linear-gradient(135deg, #a78bfa 0%, #22d3ee 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              letterSpacing: "-0.02em",
            }}
          >
            Lynk
          </span>
        </Link>

        {/* Nav links */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {isAuthenticated ? (
            <>
              <Link
                href="/dashboard"
                style={{
                  padding: "0.4rem 0.9rem",
                  borderRadius: "8px",
                  fontSize: "0.875rem",
                  fontWeight: 500,
                  textDecoration: "none",
                  color: pathname === "/dashboard" ? "#a78bfa" : "#a1a0b8",
                  background:
                    pathname === "/dashboard"
                      ? "rgba(139, 92, 246, 0.12)"
                      : "transparent",
                  transition: "all 0.2s ease",
                }}
              >
                Dashboard
              </Link>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.75rem",
                  marginLeft: "0.5rem",
                  paddingLeft: "0.75rem",
                  borderLeft: "1px solid rgba(255,255,255,0.07)",
                }}
              >
                <span
                  style={{
                    fontSize: "0.8rem",
                    color: "#5c5b72",
                  }}
                >
                  {user?.email}
                </span>
                <button
                  onClick={handleLogout}
                  disabled={loggingOut}
                  className="btn-secondary"
                  style={{ padding: "0.35rem 0.9rem", fontSize: "0.82rem" }}
                >
                  {loggingOut ? "..." : "Logout"}
                </button>
              </div>
            </>
          ) : (
            <>
              <Link
                href="/login"
                style={{
                  padding: "0.4rem 0.9rem",
                  borderRadius: "8px",
                  fontSize: "0.875rem",
                  fontWeight: 500,
                  textDecoration: "none",
                  color: "#a1a0b8",
                  transition: "color 0.2s ease",
                }}
              >
                Login
              </Link>
              <Link href="/register" className="btn-primary" style={{ padding: "0.4rem 1rem", fontSize: "0.875rem" }}>
                Sign up free
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
