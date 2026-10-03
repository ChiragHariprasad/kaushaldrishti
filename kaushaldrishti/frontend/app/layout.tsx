import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KaushalDrishti | Labour Market Intelligence System (MSDE)",
  description:
    "AI-enabled Labour Market Intelligence System for the Ministry of Skill Development and Entrepreneurship (MSDE). Smart India Hackathon 2026.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
