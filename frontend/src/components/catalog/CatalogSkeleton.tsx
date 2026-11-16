"use client";

import React from "react";

export function CatalogSkeleton() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
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
  );
}
