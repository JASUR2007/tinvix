"use client";

import React, { useState } from "react";
import { Product, CartItem } from "@/types";
import { Header } from "@/components/Header";
import { ProductCard } from "@/components/ProductCard";
import { CartModal } from "@/components/CartModal";
import { AlertCircle, Server } from "lucide-react";
import { useCatalog } from "@/hooks/useCatalog";
import { EmptyCatalog } from "@/components/catalog/EmptyCatalog";
import { CatalogSkeleton } from "@/components/catalog/CatalogSkeleton";

export default function CatalogPage() {
  const [isCartOpen, setIsCartOpen] = useState(false);
  const {
    products,
    cart,
    isLoading,
    error,
    serverInfo,
    totalCartCount,
    fetchProducts,
    handleAddToCart,
    handleUpdateQuantity,
    handleClearCart,
  } = useCatalog();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      <Header
        cartCount={totalCartCount}
        onOpenCart={() => setIsCartOpen(true)}
        onRefresh={fetchProducts}
        isLoading={isLoading}
      />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-6">
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

        {isLoading && products.length === 0 ? (
          <CatalogSkeleton />
        ) : products.length === 0 ? (
          <EmptyCatalog />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {products.map((product: Product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
                isInCart={cart.some((item: CartItem) => item.product.id === product.id)}
              />
            ))}
          </div>
        )}
      </main>

      <CartModal
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={cart}
        onUpdateQuantity={handleUpdateQuantity}
        onClearCart={handleClearCart}
      />

      <footer className="mt-auto border-t border-slate-200 bg-white py-4 px-4 text-center text-xs text-slate-500">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Tinvix Catalog Microservice &copy; 2026</span>
          {serverInfo.instance_id && (
            <span className="flex items-center gap-1 font-mono text-[11px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
              <Server className="w-3 h-3" />
              replica: {serverInfo.instance_id.slice(0, 8)}
            </span>
          )}
        </div>
      </footer>
    </div>
  );
}
