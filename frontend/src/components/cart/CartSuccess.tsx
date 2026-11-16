"use client";

import React from "react";
import { CheckCircle2 } from "lucide-react";

interface CartSuccessProps {
  orderId: number | null;
  onClose: () => void;
}

export function CartSuccess({ orderId, onClose }: CartSuccessProps) {
  return (
    <div className="py-12 flex flex-col items-center justify-center text-center">
      <CheckCircle2 className="w-16 h-16 text-green-500 mb-3 animate-bounce" />
      <h3 className="text-xl font-bold text-slate-900">
        Заказ {orderId ? `#${orderId}` : ""} принят!
      </h3>
      <p className="text-sm text-slate-500 mt-1 max-w-sm">
        Заказ успешно сохранён в базе данных PostgreSQL. Демонстрационный режим без реальной оплаты.
      </p>
      <button
        onClick={onClose}
        className="mt-6 px-6 py-2.5 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition"
      >
        Вернуться к покупкам
      </button>
    </div>
  );
}
