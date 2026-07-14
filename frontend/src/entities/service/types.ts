// Тип услуги — зеркалит ServiceRead из backend (модуль service).
export interface Service {
  id: number;
  title: string;
  description: string | null;
  duration_min: number;
  price: string; // Numeric сериализуется строкой
  category: string | null;
  photo_url: string | null;
}
