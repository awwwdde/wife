import axios from "axios";

// В dev ходим на /api (проксируется Vite на backend). В проде — тот же origin.
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  withCredentials: true,
});
