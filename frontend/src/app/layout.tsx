import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Lynk — Modern URL Shortener",
  description:
    "Shorten URLs, track analytics, and share your links with the world. Free forever for basic use.",
  keywords: ["url shortener", "link shortener", "analytics", "lynk"],
  openGraph: {
    title: "Lynk — Modern URL Shortener",
    description: "Shorten URLs, track analytics, and share your links.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AuthProvider>
          <Navbar />
          <main>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
