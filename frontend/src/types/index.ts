export interface Product {
  id: number;
  title: string;
  image_url: string;
  price?: number;
  description?: string;
  created_at: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}
