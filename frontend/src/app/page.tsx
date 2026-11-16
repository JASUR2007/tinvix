"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Product, CartItem } from "@/types";
import { Header } from "@/components/Header";
import { ProductCard } from "@/components/ProductCard";
import { CartModal } from "@/components/CartModal";
import { PackageOpen, AlertCircle, Server } from "lucide-react";

export default function CatalogPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [serverInfo, setServerInfo] = useState<{ instance_id?: string }>({});

  // Load cart from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("tinvix_cart");
      if (saved) {
        setCart(JSON.parse(saved));
      }
    } catch (e) {
      console.warn("Could not load cart from localStorage", e);
    }
  }, []);

  // Save cart to localStorage
  const saveCart = (newCart: CartItem[]) => {
    setCart(newCart);
    try {
      localStorage.setItem("tinvix_cart", JSON.stringify(newCart));
    } catch (e) {
      console.warn("Could not save cart to localStorage", e);
    }
  };

  const fetchProducts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/products", { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`Ошибка загрузки: ${res.statusText}`);
      }
      const data = await res.json();
      setProducts(data.items || []);

      // Also fetch health info for instance ID display
      const healthRes = await fetch("/api/health", { cache: "no-store" });
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setServerInfo(healthData);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Не удалось загрузить каталог товаров");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleAddToCart = (product: Product) => {
    const existingIndex = cart.findIndex((item) => item.product.id === product.id);
    if (existingIndex > -1) {
      const updated = [...cart];
      updated[existingIndex].quantity += 1;
      saveCart(updated);
    } else {
      saveCart([...cart, { product, quantity: 1 }]);
    }
  };

  const handleUpdateQuantity = (productId: number, delta: number) => {
    const updated = cart
      .map((item) => {
        if (item.product.id === productId) {
          const newQty = item.quantity + delta;
          return newQty > 0 ? { ...item, quantity: newQty } : null;
        }
        return item;
      })
      .filter(Boolean) as CartItem[];

    saveCart(updated);
  };

  const handleClearCart = () => {
    saveCart([]);
  };

  const totalCartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      <Header
        cartCount={totalCartCount}
        onOpenCart={() => setIsCartOpen(true)}
        onRefresh={fetchProducts}
        isLoading={isLoading}
      />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-6">
        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-center justify-between text-red-700">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
            <button
              onClick={fetchProducts}
              className="text-xs font-semibold underline hover:no-underline ml-4"
            >
              Повторить
            </button>
          </div>
        )}

        {/* Loading Skeleton */}
        {isLoading && products.length === 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div
                key={n}
                className="bg-white rounded-xl border border-slate-200 p-3 space-y-3 animate-pulse"
              >
                <div className="aspect-square bg-slate-200 rounded-lg" />
                <div className="h-4 bg-slate-200 rounded w-3/4" />
                <div className="h-4 bg-slate-200 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : products.length === 0 ? (
          /* Empty Catalog State */
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
        ) : (
          /* Product Grid */
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
                isInCart={cart.some((item) => item.product.id === product.id)}
              />
            ))}
          </div>
        )}
      </main>

      {/* Cart Drawer */}
      <CartModal
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={cart}
        onUpdateQuantity={handleUpdateQuantity}
        onClearCart={handleClearCart}
      />

      {/* Footer with stateless replica debug info */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-4 px-4 text-center text-xs text-slate-500">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Tinvix Catalog Microservice &copy; 2026</span>
          {serverInfo.instance_id && (
            <div className="flex items-center gap-1.5 text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md text-[11px] font-mono">
              <Server className="w-3.5 h-3.5 text-blue-600" />
              <span>Обработано инстансом: {serverInfo.instance_id}</span>
            </div>
          )}
        </div>
      </footer>
    </div>
  );
}
