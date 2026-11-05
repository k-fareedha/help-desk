import type { Assignee, Customer, DashboardSummary, Product, ProductModule, Ticket, TicketComment, TicketHistory, TicketPage } from './types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { ...(init?.body ? { 'Content-Type': 'application/json' } : {}), ...init?.headers },
    });
  } catch {
    throw new ApiError('The support API is unavailable. Start the FastAPI backend and try again.', 0);
  }
  const body = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join(' ')
      : typeof detail === 'string' ? detail : `Request failed (${response.status}).`;
    throw new ApiError(message, response.status);
  }
  return body as T;
}

function json(method: string, payload?: unknown): RequestInit {
  return { method, ...(payload === undefined ? {} : { body: JSON.stringify(payload) }) };
}

function query(params: Record<string, string | number | undefined>): string {
  const values = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') values.set(key, String(value));
  });
  const result = values.toString();
  return result ? `?${result}` : '';
}

export const api = {
  products: () => request<Product[]>('/api/v1/products'),
  createProduct: (payload: Pick<Product, 'name' | 'code'> & Partial<Pick<Product, 'description'>>) => request<Product>('/api/v1/products', json('POST', payload)),
  updateProduct: (id: number, payload: Partial<Product>) => request<Product>(`/api/v1/products/${id}`, json('PATCH', payload)),
  modules: (productId: number) => request<ProductModule[]>(`/api/v1/products/${productId}/modules`),
  createModule: (productId: number, payload: Pick<ProductModule, 'name' | 'code'> & Partial<Pick<ProductModule, 'description'>>) => request<ProductModule>(`/api/v1/products/${productId}/modules`, json('POST', payload)),
  updateModule: (id: number, payload: Partial<ProductModule>) => request<ProductModule>(`/api/v1/modules/${id}`, json('PATCH', payload)),
  customers: () => request<Customer[]>('/api/v1/customers'),
  createCustomer: (payload: Pick<Customer, 'name' | 'code'> & Partial<Pick<Customer, 'email' | 'phone'>> & { product_ids?: number[] }) => request<Customer>('/api/v1/customers', json('POST', payload)),
  updateCustomer: (id: number, payload: Partial<Customer>) => request<Customer>(`/api/v1/customers/${id}`, json('PATCH', payload)),
  setCustomerProducts: (id: number, productIds: number[]) => request<Customer>(`/api/v1/customers/${id}/products`, json('PUT', { product_ids: productIds })),
  assignees: () => request<Assignee[]>('/api/v1/assignees?include_inactive=true'),
  createAssignee: (payload: Pick<Assignee, 'name'> & Partial<Pick<Assignee, 'email'>>) => request<Assignee>('/api/v1/assignees', json('POST', payload)),
  updateAssignee: (id: number, payload: Partial<Assignee>) => request<Assignee>(`/api/v1/assignees/${id}`, json('PATCH', payload)),
  tickets: (params: { page?: number; page_size?: number; q?: string; product_id?: number; status?: string; priority?: string }) => request<TicketPage>(`/api/v1/tickets${query(params)}`),
  ticket: (id: number) => request<Ticket>(`/api/v1/tickets/${id}`),
  createTicket: (payload: Record<string, unknown>) => request<Ticket>('/api/v1/tickets', json('POST', payload)),
  updateTicket: (id: number, payload: Record<string, unknown>) => request<Ticket>(`/api/v1/tickets/${id}`, json('PATCH', payload)),
  comments: (id: number) => request<TicketComment[]>(`/api/v1/tickets/${id}/comments`),
  addComment: (id: number, comment: string) => request<TicketComment>(`/api/v1/tickets/${id}/comments`, json('POST', { comment })),
  history: (id: number) => request<TicketHistory[]>(`/api/v1/tickets/${id}/history`),
  dashboard: (productId?: number) => request<DashboardSummary>(`/api/v1/dashboard/summary${query({ product_id: productId })}`),
  assistant: (question: string) => request<{ answer: string; configured: boolean }>('/assistant', json('POST', { question })),
};
