import React from 'react';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import App from './App';

afterEach(() => vi.unstubAllGlobals());

describe('workspace shell', () => {
  it('identifies the local prototype and reports API loading failures', async () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise<Response>(() => undefined)));
    render(<App />);

    expect(screen.getByRole('status')).toHaveTextContent('Loading workspace');
  });

  it('reports an actionable error when the API cannot be reached', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')));
    render(<App />);

    expect(await screen.findByRole('alert')).toHaveTextContent('The support API is unavailable.');
    expect(screen.getAllByText(/Authentication and role-based access control are not implemented/).length).toBeGreaterThan(0);
  });

  it('renders live dashboard values after the reference and summary requests complete', async () => {
    const responses: Record<string, unknown> = {
      '/api/v1/products': [{ id: 1, name: 'Vanforces', code: 'VF', description: null, is_active: true }],
      '/api/v1/customers': [],
      '/api/v1/assignees': [],
      '/api/v1/products/1/modules': [],
      '/api/v1/dashboard/summary': {
        total_tickets: 4, open_tickets: 2, in_progress_tickets: 0, resolved_tickets: 0, critical_tickets: 1,
        by_product: [{ product_id: 1, product_name: 'Vanforces', count: 2 }], recent_tickets: [],
      },
    };
    vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL) => {
      const url = new URL(String(input));
      return Promise.resolve(new Response(JSON.stringify(responses[url.pathname] ?? []), { status: 200 }));
    }));
    render(<App />);

    await waitFor(() => expect(screen.getAllByText('Vanforces').length).toBeGreaterThan(0));
    expect(screen.getByText('LOCAL PROTOTYPE · NO AUTH')).toBeInTheDocument();
    expect(screen.getByText('Total tickets')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });
});

const demoProduct = { id: 1, name: 'Vanforces', code: 'VF', description: 'Sales platform', is_active: true };
const demoTicket = {
  id: 7, ticket_no: 'TEX-000007', product_id: 1, module_id: null, customer_id: null,
  title: 'Invoice sync fails', description: 'Invoices stay pending after sync.', category: 'Bug',
  priority: 'High', status: 'Open', assigned_to: null, created_at: '2026-10-26T10:00:00Z',
  updated_at: '2026-10-26T10:00:00Z', resolved_at: null,
};

function apiResponse(body: unknown, status = 200) {
  return new Response(body === null ? null : JSON.stringify(body), { status });
}

describe('ticket interactions', () => {
  it('filters the queue, opens detail, updates ticket status, and adds a comment', async () => {
    let ticket = { ...demoTicket };
    const comments: Array<{ id: number; ticket_id: number; author_label: string; comment: string; created_at: string }> = [];
    const requests: Array<{ path: string; method: string; body?: Record<string, unknown> }> = [];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      const method = init?.method ?? 'GET';
      const body = init?.body ? JSON.parse(String(init.body)) as Record<string, unknown> : undefined;
      requests.push({ path: url.pathname + url.search, method, body });
      if (url.pathname === '/api/v1/products') return apiResponse([demoProduct]);
      if (url.pathname === '/api/v1/customers' || url.pathname === '/api/v1/assignees' || url.pathname.endsWith('/modules')) return apiResponse([]);
      if (url.pathname === '/api/v1/tickets' && method === 'GET') return apiResponse({ items: [ticket], page: 1, page_size: 10, total: 1 });
      if (url.pathname === '/api/v1/tickets/7' && method === 'GET') return apiResponse(ticket);
      if (url.pathname === '/api/v1/tickets/7' && method === 'PATCH') {
        ticket = { ...ticket, ...body } as typeof ticket;
        return apiResponse(ticket);
      }
      if (url.pathname === '/api/v1/tickets/7/comments' && method === 'GET') return apiResponse(comments);
      if (url.pathname === '/api/v1/tickets/7/history') return apiResponse([]);
      if (url.pathname === '/api/v1/tickets/7/comments' && method === 'POST') {
        comments.push({ id: 1, ticket_id: 7, author_label: 'Local demo operator', comment: String(body?.comment), created_at: '2026-10-27T10:00:00Z' });
        return apiResponse(comments[0], 201);
      }
      return apiResponse({ detail: 'Unexpected request' }, 404);
    }));
    render(<App />);

    fireEvent.click(await screen.findByRole('button', { name: 'Tickets' }));
    await screen.findByText('Invoice sync fails');
    fireEvent.change(screen.getByRole('combobox', { name: 'Filter by status' }), { target: { value: 'Open' } });
    await waitFor(() => expect(requests.some((request) => request.path.includes('status=Open'))).toBe(true));
    fireEvent.click(screen.getByText('TEX-000007'));

    expect(await screen.findByRole('heading', { name: 'Invoice sync fails' })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Status'), { target: { value: 'In Progress' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));
    await waitFor(() => expect(requests.some((request) => request.method === 'PATCH' && request.body?.status === 'In Progress')).toBe(true));

    fireEvent.change(screen.getByLabelText('Edit title'), { target: { value: 'Invoice sync stalls' } });
    fireEvent.change(screen.getByLabelText('Edit description'), { target: { value: 'Invoice synchronization remains pending.' } });
    fireEvent.change(screen.getByLabelText('Edit category'), { target: { value: 'Integration Issue' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save ticket details' }));
    await waitFor(() => expect(requests.some((request) => request.method === 'PATCH' && request.body?.title === 'Invoice sync stalls' && request.body?.description === 'Invoice synchronization remains pending.' && request.body?.category === 'Integration Issue')).toBe(true));

    fireEvent.change(screen.getByLabelText('Add a comment'), { target: { value: 'Reproduced and investigating.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add comment' }));
    expect(await screen.findByText('Reproduced and investigating.')).toBeInTheDocument();
    expect(requests.some((request) => request.method === 'POST' && request.body?.comment === 'Reproduced and investigating.')).toBe(true);
  });
});

describe('directory management interactions', () => {
  it('saves a new assignee and shows API failure feedback', async () => {
    const assignees: Array<{ id: number; name: string; email: string | null; is_active: boolean }> = [];
    let failCreate = false;
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      if (url.pathname === '/api/v1/products') return apiResponse([demoProduct]);
      if (url.pathname === '/api/v1/products/1/modules' || url.pathname === '/api/v1/customers') return apiResponse([]);
      if (url.pathname === '/api/v1/assignees' && (init?.method ?? 'GET') === 'GET') return apiResponse(assignees);
      if (url.pathname === '/api/v1/assignees' && init?.method === 'POST') {
        if (failCreate) return apiResponse({ detail: 'An assignee with this name already exists.' }, 409);
        const body = JSON.parse(String(init.body)) as { name: string; email: string };
        const created = { id: 9, ...body, is_active: true };
        assignees.push(created);
        return apiResponse(created, 201);
      }
      return apiResponse({ detail: 'Unexpected request' }, 404);
    }));
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: 'Assignees' }));
    await screen.findByRole('heading', { name: 'Add assignee' });
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Demo Engineer' } });
    fireEvent.change(screen.getByLabelText(/Email/), { target: { value: 'demo@example.test' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add assignee' }));

    expect(await screen.findByText('Demo Engineer')).toBeInTheDocument();
    expect(await screen.findByText('Assignee added.')).toBeInTheDocument();

    failCreate = true;
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Duplicate Engineer' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add assignee' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('An assignee with this name already exists.');
    expect(within(screen.getByRole('alert')).getByText(/already exists/)).toBeInTheDocument();
  });

  it('updates customer details and product memberships in one PATCH request', async () => {
    const products = [demoProduct, { id: 2, name: 'Taskforce', code: 'TF', description: null, is_active: true }];
    let customer = { id: 4, name: 'Demo Customer', code: 'DEMO', email: 'old@example.test', phone: null, is_active: true, product_ids: [1] };
    const writes: Array<{ method: string; path: string; body?: Record<string, unknown> }> = [];
    let failUpdate = false;
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      const method = init?.method ?? 'GET';
      const body = init?.body ? JSON.parse(String(init.body)) as Record<string, unknown> : undefined;
      if (method !== 'GET') writes.push({ method, path: url.pathname, body });
      if (url.pathname === '/api/v1/products') return apiResponse(products);
      if (url.pathname === '/api/v1/products/1/modules' || url.pathname === '/api/v1/products/2/modules' || url.pathname === '/api/v1/assignees') return apiResponse([]);
      if (url.pathname === '/api/v1/customers' && method === 'GET') return apiResponse([customer]);
      if (url.pathname === '/api/v1/customers/4' && method === 'PATCH') {
        if (failUpdate) return apiResponse({ detail: 'Customer update was rejected.' }, 409);
        customer = { ...customer, ...body } as typeof customer;
        return apiResponse(customer);
      }
      return apiResponse({ detail: 'Unexpected request' }, 404);
    }));
    render(<App />);

    fireEvent.click(await screen.findByRole('button', { name: 'Customers' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Edit' }));
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Demo Customer Updated' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'updated@example.test' } });
    fireEvent.click(screen.getByLabelText('Taskforce'));
    fireEvent.click(screen.getByRole('button', { name: 'Save customer' }));

    await screen.findByText('Customer updated.');
    expect(writes).toHaveLength(1);
    expect(writes[0]).toMatchObject({
      method: 'PATCH', path: '/api/v1/customers/4',
      body: { name: 'Demo Customer Updated', email: 'updated@example.test', product_ids: [1, 2] },
    });

    failUpdate = true;
    fireEvent.click(await screen.findByRole('button', { name: 'Edit' }));
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Rejected Customer Update' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save customer' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Customer update was rejected.');
    expect(writes).toHaveLength(2);
    expect(writes[1].method).toBe('PATCH');
  });
});
