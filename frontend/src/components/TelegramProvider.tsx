"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import Script from "next/script";

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
}

interface TelegramContextType {
  isTMA: boolean;
  user: TelegramUser | null;
  webApp: any;
  showAlert: (message: string) => void;
}

const TelegramContext = createContext<TelegramContextType>({
  isTMA: false,
  user: null,
  webApp: null,
  showAlert: () => {},
});

export const useTelegram = () => useContext(TelegramContext);

export function TelegramProvider({ children }: { children: React.ReactNode }) {
  const [isTMA, setIsTMA] = useState(false);
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [webApp, setWebApp] = useState<any>(null);

  const initTelegram = () => {
    if (typeof window !== "undefined" && (window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp;
      tg.ready();
      tg.expand();

      // Check if actually inside Telegram client (initData is non-empty)
      const hasInitData = Boolean(tg.initData && tg.initData.length > 0);
      setIsTMA(hasInitData);
      setWebApp(tg);

      if (tg.initDataUnsafe?.user) {
        setUser(tg.initDataUnsafe.user);
      }
    }
  };

  useEffect(() => {
    initTelegram();
  }, []);

  const showAlert = (message: string) => {
    if (webApp && isTMA) {
      webApp.showAlert(message);
    } else {
      alert(message);
    }
  };

  return (
    <TelegramContext.Provider value={{ isTMA, user, webApp, showAlert }}>
      <Script
        src="https://telegram.org/js/telegram-web-app.js"
        strategy="beforeInteractive"
        onLoad={initTelegram}
      />
      {children}
    </TelegramContext.Provider>
  );
}
