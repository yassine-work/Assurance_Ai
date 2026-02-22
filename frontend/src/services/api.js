import axios from "axios";

// In dev: Vite proxy forwards /api to localhost:8000
// In prod: VITE_API_URL points to Render backend (e.g. https://assuranceai-api.onrender.com/api)
const BASE_URL = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Attach JWT token to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, clear token and redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.dispatchEvent(new Event("auth-expired"));
    }
    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────

export async function registerUser(email, full_name, password) {
  const { data } = await api.post("/auth/register", { email, full_name, password });
  return data;
}

export async function loginUser(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

export async function getMe() {
  const { data } = await api.get("/auth/me");
  return data;
}

// ── Public ────────────────────────────────────────────────────────────────

export async function getHealth() {
  const { data } = await api.get("/health");
  return data;
}

export async function getBundles() {
  const { data } = await api.get("/bundles");
  return data;
}

export async function getFormSchema() {
  const { data } = await api.get("/form-schema");
  return data;
}

// ── Prediction (auth required) ────────────────────────────────────────────

export async function predictBundle(customerData) {
  const { data } = await api.post("/predict", customerData);
  return data;
}

export async function getPredictionHistory() {
  const { data } = await api.get("/predictions/history");
  return data;
}

// ── Admin ─────────────────────────────────────────────────────────────────

export async function getAdminStats() {
  const { data } = await api.get("/admin/stats");
  return data;
}

export async function getAdminUsers() {
  const { data } = await api.get("/admin/users");
  return data;
}

export async function getAdminPredictions() {
  const { data } = await api.get("/admin/predictions");
  return data;
}

export async function toggleUserActive(userId) {
  const { data } = await api.patch(`/admin/users/${userId}/toggle`);
  return data;
}

export default api;
