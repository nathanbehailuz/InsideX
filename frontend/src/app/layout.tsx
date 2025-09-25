import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InsideX - Insider Trading Signals",
  description: "AI-powered insider trading signal detection and analysis platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50">
        {children}
      </body>
    </html>
  );
}