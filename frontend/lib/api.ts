/**
 * PayPilot Frontend API Client.
 * Centralizes base URL configuration, headers, and error handling.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE_URL}${path}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    let errorData = null;
    try {
      errorData = await response.json();
      if (errorData?.detail) {
        errorDetail =
          typeof errorData.detail === "string"
            ? errorData.detail
            : JSON.stringify(errorData.detail);
      }
    } catch {
      // Body not JSON
    }
    throw new ApiError(errorDetail, response.status, errorData);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  get: <T>(path: string, headers?: Record<string, string>) =>
    request<T>(path, { method: "GET", headers }),

  post: <T>(path: string, body?: any, headers?: Record<string, string>) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
      headers,
    }),

  put: <T>(path: string, body?: any, headers?: Record<string, string>) =>
    request<T>(path, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
      headers,
    }),

  delete: <T>(path: string, headers?: Record<string, string>) =>
    request<T>(path, { method: "DELETE", headers }),

  getTimelineEvents: (params?: { order_id?: string; event_type?: string; start_date?: string; end_date?: string }) => {
    const query = new URLSearchParams();
    if (params?.order_id) query.append("order_id", params.order_id);
    if (params?.event_type) query.append("event_type", params.event_type);
    if (params?.start_date) query.append("start_date", params.start_date);
    if (params?.end_date) query.append("end_date", params.end_date);
    const qs = query.toString();
    return request<any>(`/api/timeline/events${qs ? `?${qs}` : ""}`, { method: "GET" });
  },

  getTimelineSummary: () => request<any>("/api/timeline/summary", { method: "GET" }),

  getAstropodsOverview: () => request<any>("/api/agent/astropods/overview", { method: "GET" }),

  // Channel3 API
  searchChannel3: (body: { query: string; category?: string; min_price?: number; max_price?: number; brand?: string; limit?: number }) =>
    request<any>("/api/channel3/search", { method: "POST", body: JSON.stringify(body) }),

  compareChannel3: (product_ids: string[]) =>
    request<any>("/api/channel3/compare", { method: "POST", body: JSON.stringify({ product_ids }) }),

  // Elasticsearch API
  searchElastic: (body: { query: string; mode?: "hybrid" | "keyword" | "semantic"; category?: string; min_price?: number; max_price?: number; limit?: number }) =>
    request<any>("/api/elastic/search", { method: "POST", body: JSON.stringify(body) }),

  getElasticHealth: () => request<any>("/api/elastic/health", { method: "GET" }),
};

