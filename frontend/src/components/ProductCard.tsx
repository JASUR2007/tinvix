"use client";

import React, { useState } from "react";
import { Product } from "@/types";
import { ShoppingCart, Check, ImageOff } from "lucide-react";

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  isInCart?: boolean;
}

export function ProductCard({ product, onAddToCart, isInCart }: ProductCardProps) {
  const [imageError, setImageError] = useState(false);
  const [isAdded, setIsAdded] = useState(false);

  const handleAdd = () => {
    onAddToCart(product);
    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 1200);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col group">
      <div className="relative aspect-square w-full bg-slate-100 overflow-hidden flex items-center justify-center">
        {!imageError && product.image_url ? (
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={() => setImageError(true)}
            loading="lazy"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-slate-400 p-2 text-center">
            <ImageOff className="w-8 h-8 mb-1 opacity-40" />
            <span className="text-[11px] text-slate-400">Нет фото</span>
          </div>
        )}
      </div>

      <div className="p-3 sm:p-4 flex-1 flex flex-col justify-between">
        <div>
          <h3 className="font-semibold text-slate-900 line-clamp-2 text-xs sm:text-sm md:text-base leading-snug">
            {product.title}
          </h3>
          {product.description && (
            <p className="text-[11px] sm:text-xs text-slate-500 mt-1 line-clamp-1 sm:line-clamp-2">
              {product.description}
            </p>
          )}
        </div>

        <div className="mt-2.5 sm:mt-4 pt-2 sm:pt-3 border-t border-slate-100 flex items-center justify-between gap-1.5">
          <div className="min-w-0">
            <span className="text-[10px] sm:text-xs text-slate-400 block leading-none mb-0.5">
              Цена
            </span>
            <span className="text-sm sm:text-base md:text-lg font-bold text-slate-900 truncate block">
              {product.price && product.price > 0
                ? `${Number(product.price).toLocaleString("ru-RU")} ₽`
                : "0 ₽"}
            </span>
          </div>

          <button
            onClick={handleAdd}
            aria-label="Добавить в корзину"
            className={`p-2 sm:px-3 sm:py-2 rounded-xl font-medium text-xs sm:text-sm flex items-center justify-center gap-1.5 transition-all flex-shrink-0 ${
              isAdded || isInCart
                ? "bg-emerald-600 text-white"
                : "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
            }`}
          >
            {isAdded ? (
              <>
                <Check className="w-4 h-4" />
                <span className="hidden sm:inline">Добавлено</span>
              </>
            ) : (
              <>
                <ShoppingCart className="w-4 h-4" />
                <span className="hidden sm:inline">В корзину</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
