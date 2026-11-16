"use client";

import { useEffect, useState, useCallback } from "react";
import { Product, CartItem } from "@/types";

export function useCatalog() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [serverInfo, setServerInfo] = useState<{ instance_id?: string }>({});

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
      if (!res.ok) throw new Error(`Ошибка загрузки: ${res.statusText}`);
      const data = await res.json();
      setProducts(data.items || []);

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
    const existingIndex = cart.findIndex((item: CartItem) => item.product.id === product.id);
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
      .map((item: CartItem) => {
        if (item.product.id === productId) {
          const newQty = item.quantity + delta;
          return newQty > 0 ? { ...item, quantity: newQty } : null;
        }
        return item;
      })
      .filter(Boolean) as CartItem[];

    saveCart(updated);
  };

  const handleClearCart = () => saveCart([]);

  const totalCartCount = cart.reduce((sum: number, item: CartItem) => sum + item.quantity, 0);

  return {
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
  };
}
