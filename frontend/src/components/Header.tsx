"use client";

import React from "react";
import { ShoppingBag, RefreshCw, Smartphone, Globe } from "lucide-react";
import { useTelegram } from "./TelegramProvider";

interface HeaderProps {
  cartCount: number;
  onOpenCart: () => void;
  onRefresh: () => void;
  isLoading: boolean;
}

export function Header({ cartCount, onOpenCart, onRefresh, isLoading }: HeaderProps) {
  const { isTMA, user } = useTelegram();

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-sm transition-all">
      <div className="max-w-5xl mx-auto px-3 sm:px-4 py-2.5 sm:py-3 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-1.5 sm:gap-2">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
              Каталог
            </h1>
            <span
              className={`text-[11px] sm:text-xs px-2 py-0.5 rounded-full font-medium flex items-center gap-1 ${
                isTMA
                  ? "bg-blue-100 text-blue-700 border border-blue-200"
                  : "bg-slate-100 text-slate-700 border border-slate-200"
              }`}
              title={isTMA ? "Открыто в Telegram Mini App" : "Открыто в стандартном браузере"}
            >
              {isTMA ? (
                <>
                  <Smartphone className="w-3 h-3" /> TMA
                </>
              ) : (
                <>
                  <Globe className="w-3 h-3" /> Web
                </>
              )}
            </span>
          </div>
          {user && (
            <p className="text-[11px] sm:text-xs text-slate-500 mt-0.5">
              Привет, {user.first_name}!
            </p>
          )}
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition disabled:opacity-50"
            title="Обновить список"
          >
            <RefreshCw className={`w-4 h-4 sm:w-5 sm:h-5 ${isLoading ? "animate-spin" : ""}`} />
          </button>

          <button
            onClick={onOpenCart}
            className="relative p-2 text-slate-700 hover:bg-slate-100 rounded-xl transition flex items-center gap-1"
            title="Корзина"
          >
            <ShoppingBag className="w-5 h-5 sm:w-6 sm:h-6" />
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-[11px] sm:text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center animate-scale-in">
                {cartCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
