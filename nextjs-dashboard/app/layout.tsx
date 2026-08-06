import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Météo — Tableau de bord",
  description: "Suivi météo multi-villes (Next.js)",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr" className="h-full antialiased">
      <body className="min-h-full font-sans">{children}</body>
    </html>
  );
}
