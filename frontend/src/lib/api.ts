const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

type ValidationDetailItem = string | { msg?: string; message?: string };

export interface ApiError {
  success?: boolean;
  message?: string;
  detail?: string | ValidationDetailItem[];
}

function detailItemMessage(item: ValidationDetailItem): string {
  if (typeof item === "string") {
    return item;
  }
  if (typeof item.msg === "string") {
    return item.msg;
  }
  if (typeof item.message === "string") {
    return item.message;
  }
  return "";
}

function messagesFromDetail(detail: ValidationDetailItem[]): string {
  return detail.map(detailItemMessage).filter(Boolean).join(", ");
}

export class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}

export function getErrorMessage(
  err: unknown,
  fallback = "Request failed",
): string {
  if (err instanceof ApiClientError || err instanceof Error) {
    const message = err.message.trim();
    if (message) {
      return message;
    }
  }
  return fallback;
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as ApiError;
    const detailMessages = Array.isArray(data.detail)
      ? messagesFromDetail(data.detail)
      : "";

    if (typeof data.message === "string" && data.message.trim()) {
      const message = data.message.trim();
      if (message === "Validation error" && detailMessages) {
        return detailMessages;
      }
      return message;
    }
    if (typeof data.detail === "string" && data.detail.trim()) {
      return data.detail.trim();
    }
    if (detailMessages) {
      return detailMessages;
    }
    return "Request failed";
  } catch {
    return "Request failed";
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const message = await parseError(response);
    throw new ApiClientError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export { API_BASE_URL };
