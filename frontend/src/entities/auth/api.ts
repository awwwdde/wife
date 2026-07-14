import { api } from "@/shared/api/client";

// Клиент (зеркалит ClientRead бэка).
export interface Me {
  id: number;
  telegram_id: number | null;
  first_name: string | null;
  last_name: string | null;
  username: string | null;
  phone: string | null;
  consent_at: string | null;
}

// Payload Telegram Login Widget (браузер).
export interface WidgetPayload {
  id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export async function authMiniApp(initData: string): Promise<Me> {
  const { data } = await api.post<Me>("/auth/telegram/miniapp", { init_data: initData });
  return data;
}

export async function authWidget(payload: WidgetPayload): Promise<Me> {
  const { data } = await api.post<Me>("/auth/telegram/widget", payload);
  return data;
}

export async function fetchMe(): Promise<Me> {
  const { data } = await api.get<Me>("/auth/me");
  return data;
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout");
}
