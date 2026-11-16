"use client";

import React from "react";
import { CheckCircle2, Database, Sparkles, X } from "lucide-react";

interface OrderSuccessModalProps {
  orderId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export function OrderSuccessModal({ orderId, isOpen, onClose }: OrderSuccessModalProps) {
  if (!isOpen || !orderId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-sm bg-white rounded-3xl p-6 shadow-2xl border border-slate-100 flex flex-col items-center text-center transform transition-all animate-scale-up">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="relative mb-4 mt-2">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 animate-bounce" />
          </div>
          <Sparkles className="w-5 h-5 text-amber-400 absolute -top-1 -right-1" />
        </div>

        <h3 className="text-2xl font-bold text-slate-900">
          Заказ №{orderId}
        </h3>
        <p className="text-sm font-semibold text-emerald-600 mt-1">
          Успешно создан и сохранён!
        </p>

        <div className="mt-4 w-full bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 space-y-2 text-left">
          <div className="flex items-center justify-between text-xs text-slate-600">
            <span className="flex items-center gap-1.5 font-medium">
              <Database className="w-3.5 h-3.5 text-blue-500" />
              База данных:
            </span>
            <span className="font-semibold text-slate-800">PostgreSQL 16</span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-600">
            <span>Статус:</span>
            <span className="font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
              Принят
            </span>
          </div>
        </div>

        <p className="text-xs text-slate-400 mt-4">
          Демонстрационный режим без списания средств
        </p>

        <button
          onClick={onClose}
          className="mt-4 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl transition shadow-lg shadow-blue-500/25 active:scale-[0.98]"
        >
          Вернуться к покупкам
        </button>
      </div>
    </div>
  );
}
