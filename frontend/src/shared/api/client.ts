import axios from "axios";

// В dev ходим на /api (проксируется Vite на backend). В проде — тот же origin.
// `||`, а не `??`: пустая строка VITE_API_URL (в prod-сборке) тоже должна дать "/api".
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  withCredentials: true,
});
