"use client";

import React from "react";
import { CartItem } from "@/types";
import { Plus, Minus, Trash2 } from "lucide-react";

interface CartItemRowProps {
  item: CartItem;
  disabled?: boolean;
  onUpdateQuantity: (productId: number, delta: number) => void;
}

export function CartItemRow({ item, disabled, onUpdateQuantity }: CartItemRowProps) {
  return (
    <div className="py-3 flex items-center gap-3">
      <div className="w-16 h-16 rounded-lg bg-slate-100 overflow-hidden flex-shrink-0">
        <img
          src={item.product.image_url}
          alt={item.product.title}
          className="w-full h-full object-cover"
          onError={(e) => {
            (e.target as HTMLElement).style.display = "none";
          }}
        />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-slate-900 truncate">
          {item.product.title}
        </h4>
        <p className="text-xs text-slate-500 mt-0.5">
          {item.product.price
            ? `${Number(item.product.price).toLocaleString("ru-RU")} ₽`
            : "0 ₽"}
        </p>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onUpdateQuantity(item.product.id, -1)}
          className="p-1 rounded bg-slate-100 text-slate-700 hover:bg-slate-200"
          disabled={disabled}
        >
          {item.quantity === 1 ? (
            <Trash2 className="w-4 h-4 text-red-500" />
          ) : (
            <Minus className="w-4 h-4" />
          )}
        </button>
        <span className="text-sm font-semibold w-6 text-center">
          {item.quantity}
        </span>
        <button
          onClick={() => onUpdateQuantity(item.product.id, 1)}
          className="p-1 rounded bg-slate-100 text-slate-700 hover:bg-slate-200"
          disabled={disabled}
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
