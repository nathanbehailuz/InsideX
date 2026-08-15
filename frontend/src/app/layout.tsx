import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpenSignal",
  description:
    "An AI platform that analyzes financial disclosures and transactions from influential decision-makers—including government officials and corporate executives—to identify market signals.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans bg-background text-on-surface">
        {children}
      </body>
    </html>
  );
}
