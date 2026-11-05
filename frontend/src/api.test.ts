import { afterEach, describe, expect, it, vi } from 'vitest';
import { api } from './api';

afterEach(() => vi.unstubAllGlobals());

describe('API client', () => {
  it('requests versioned product data and decodes JSON', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify([{ id: 1, name: 'Vanforces' }]), { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(api.products()).resolves.toEqual([{ id: 1, name: 'Vanforces' }]);
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/v1/products', { headers: {} });
  });

  it('reports safe server error details as an ApiError', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'Product code already exists.' }), { status: 409 })));

    await expect(api.products()).rejects.toMatchObject({ status: 409, message: 'Product code already exists.' });
  });

  it('converts network failures into a visible, actionable message', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')));

    await expect(api.products()).rejects.toThrow('The support API is unavailable. Start the FastAPI backend and try again.');
  });
});
