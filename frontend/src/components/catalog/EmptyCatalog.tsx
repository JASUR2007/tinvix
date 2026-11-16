"use client";

import React from "react";
import { PackageOpen } from "lucide-react";

export function EmptyCatalog() {
  return (
    <div className="py-16 text-center flex flex-col items-center justify-center bg-white rounded-2xl border border-dashed border-slate-300 p-8">
      <PackageOpen className="w-16 h-16 text-slate-400 mb-3" />
      <h2 className="text-xl font-bold text-slate-800">
        В каталоге пока нет товаров
      </h2>
      <p className="text-sm text-slate-500 max-w-md mt-2">
        Администратор может добавить товар через Telegram-бота, отправив
        фотографию с названием в подписи.
      </p>
    </div>
  );
}
