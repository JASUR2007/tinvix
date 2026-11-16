"use client";

import React, { useState } from "react";
import { Product } from "@/types";
import { Plus, Check, ImageOff } from "lucide-react";

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
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col group">
      {/* Product Image */}
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
          <div className="flex flex-col items-center justify-center text-slate-400 p-4 text-center">
            <ImageOff className="w-10 h-10 mb-2 opacity-50" />
            <span className="text-xs">Изображение недоступно</span>
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <h3 className="font-semibold text-slate-900 line-clamp-2 text-base leading-snug">
            {product.title}
          </h3>
          {product.description && (
            <p className="text-xs text-slate-500 mt-1 line-clamp-2">
              {product.description}
            </p>
          )}
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block">Цена</span>
            <span className="text-lg font-bold text-slate-900">
              {product.price && product.price > 0
                ? `${Number(product.price).toLocaleString("ru-RU")} ₽`
                : "Бесплатно"}
            </span>
          </div>

          <button
            onClick={handleAdd}
            className={`px-3 py-2 rounded-lg font-medium text-sm flex items-center gap-1.5 transition-all ${
              isAdded || isInCart
                ? "bg-green-600 text-white"
                : "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
            }`}
          >
            {isAdded ? (
              <>
                <Check className="w-4 h-4" /> Добавлено
              </>
            ) : (
              <>
                <Plus className="w-4 h-4" /> В корзину
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
