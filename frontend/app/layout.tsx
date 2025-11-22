import type { Metadata } from "next";
import { Kaisei_Tokumin, Inconsolata } from "next/font/google";
import "./globals.css";
import { SessionProvider } from "next-auth/react";

const kaiseiTokumin = Kaisei_Tokumin({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  weight: ["400", "500", "700", "800"],
});

const inconsolata = Inconsolata({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Insight",
  description: "Interpretability for All",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${kaiseiTokumin.variable} ${inconsolata.variable} antialiased`}
      >
        <SessionProvider>
          {children}
        </SessionProvider>
      </body>
    </html>
  );
}
