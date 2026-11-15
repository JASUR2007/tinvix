import type { Metadata, Viewport } from "next";
import { TelegramProvider } from "@/components/TelegramProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Каталог товаров | Tinvix",
  description: "Каталог товаров для веб-браузера и Telegram Mini App",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <head>
        <meta name="theme-color" content="#ffffff" />
      </head>
      <body className="antialiased min-h-screen bg-slate-50">
        <TelegramProvider>{children}</TelegramProvider>
      </body>
    </html>
  );
}
