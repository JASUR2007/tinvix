"use client";

import React, { useState } from "react";
import { CartItem } from "@/types";
import { X, ShoppingBag, Loader2 } from "lucide-react";
import { useTelegram } from "./TelegramProvider";
import { CartItemRow } from "./cart/CartItemRow";
import { CartSuccess } from "./cart/CartSuccess";

interface CartModalProps {
  isOpen: boolean;
  onClose: () => void;
  items: CartItem[];
  onUpdateQuantity: (productId: number, delta: number) => void;
  onClearCart: () => void;
}

export function CartModal({
  isOpen,
  onClose,
  items,
  onUpdateQuantity,
  onClearCart,
}: CartModalProps) {
  const { user, showAlert } = useTelegram();
  const [isSuccess, setIsSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [orderId, setOrderId] = useState<number | null>(null);

  if (!isOpen) return null;

  const totalPrice = items.reduce(
    (sum, item) => sum + (Number(item.product.price) || 0) * item.quantity,
    0
  );

  const handleCheckout = async () => {
    setIsSubmitting(true);
    try {
      const orderPayload = {
        user_id: user ? String(user.id) : null,
        user_name: user
          ? `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username
          : "Web-пользователь",
        items: items.map((item) => ({
          product_id: item.product.id,
          title: item.product.title,
          price: Number(item.product.price) || 0,
          quantity: item.quantity,
        })),
      };

      const res = await fetch("/api/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(orderPayload),
      });

      if (!res.ok) throw new Error("Ошибка сервера при создании заказа");

      const orderData = await res.json();
      setOrderId(orderData.id);
      setIsSuccess(true);
      onClearCart();
      showAlert(`🎉 Заказ #${orderData.id} успешно создан и сохранён в PostgreSQL!`);
    } catch (err: any) {
      console.error(err);
      showAlert(`❌ Ошибка оформления: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setIsSuccess(false);
    setOrderId(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-white w-full sm:max-w-lg rounded-t-2xl sm:rounded-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-bold text-slate-900">Корзина</h2>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 overflow-y-auto flex-1 divide-y divide-slate-100">
          {isSuccess ? (
            <CartSuccess orderId={orderId} onClose={handleClose} />
          ) : items.length === 0 ? (
            <div className="py-12 flex flex-col items-center justify-center text-center text-slate-400">
              <ShoppingBag className="w-12 h-12 mb-3 opacity-40" />
              <p className="text-slate-600 font-medium">Ваша корзина пуста</p>
              <p className="text-xs text-slate-400 mt-1">
                Выберите товары из каталога и добавьте их сюда
              </p>
            </div>
          ) : (
            items.map((item) => (
              <CartItemRow
                key={item.product.id}
                item={item}
                disabled={isSubmitting}
                onUpdateQuantity={onUpdateQuantity}
              />
            ))
          )}
        </div>

        {items.length > 0 && !isSuccess && (
          <div className="p-4 border-t border-slate-200 bg-slate-50 space-y-3">
            <div className="flex items-center justify-between text-base">
              <span className="text-slate-600 font-medium">Итого к оплате:</span>
              <span className="text-xl font-bold text-slate-900">
                {totalPrice.toLocaleString("ru-RU")} ₽
              </span>
            </div>
            <button
              onClick={handleCheckout}
              disabled={isSubmitting}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition shadow-md active:scale-[0.99] flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Оформление заказа...
                </>
              ) : (
                "Оформить заказ"
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
