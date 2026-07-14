import { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";
import { HomePage } from "@/pages/HomePage";
import { BookingPage } from "@/pages/BookingPage";
import { CabinetPage } from "@/pages/CabinetPage";
import { PrivacyPage } from "@/pages/PrivacyPage";

// CRM — секретный роут /admin110220, ленивый чанк (DECISIONS §2).
const AdminApp = lazy(() => import("@/pages/admin/AdminApp"));

export const router = createBrowserRouter([
  { path: "/", element: <HomePage /> },
  { path: "/booking", element: <BookingPage /> },
  { path: "/cabinet", element: <CabinetPage /> },
  { path: "/privacy", element: <PrivacyPage /> },
  {
    path: "/admin110220/*",
    element: (
      <Suspense fallback={<div className="p-8">Загрузка…</div>}>
        <AdminApp />
      </Suspense>
    ),
  },
]);
