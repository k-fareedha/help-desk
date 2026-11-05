import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { TicketForm } from './TicketForm';

const props = {
  products: [
    { id: 1, name: 'Vanforces', code: 'VF', description: null, is_active: true },
    { id: 2, name: 'Taskforce', code: 'TF', description: null, is_active: true },
  ],
  modules: [
    { id: 10, product_id: 1, name: 'Mobile Sales', code: 'MOBILE_SALES', description: null, is_active: true },
    { id: 20, product_id: 2, name: 'Workflow', code: 'WORKFLOW', description: null, is_active: true },
  ],
  customers: [
    { id: 100, name: 'Demo Customer A', code: 'DEMO-A', email: null, phone: null, is_active: true, product_ids: [1] },
    { id: 200, name: 'Demo Customer B', code: 'DEMO-B', email: null, phone: null, is_active: true, product_ids: [2] },
  ],
  assignees: [{ id: 7, name: 'Demo Engineer', email: null, is_active: true }],
  submitting: false,
  onSubmit: vi.fn().mockResolvedValue(undefined),
  onCancel: vi.fn(),
};

describe('TicketForm', () => {
  it('filters module and customer choices to the selected product', () => {
    render(<TicketForm {...props} />);
    fireEvent.change(screen.getByRole('combobox', { name: /Product/ }), { target: { value: '1' } });

    expect(screen.getByRole('option', { name: 'Mobile Sales' })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: 'Workflow' })).not.toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Demo Customer A' })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: 'Demo Customer B' })).not.toBeInTheDocument();
  });

  it('requires a product and submits normalized required data', async () => {
    render(<TicketForm {...props} />);
    expect(screen.getByRole('button', { name: 'Create ticket' })).toBeDisabled();
    fireEvent.change(screen.getByRole('combobox', { name: /Product/ }), { target: { value: '2' } });
    fireEvent.change(screen.getByRole('textbox', { name: /Title/ }), { target: { value: '  Sync problem  ' } });
    fireEvent.change(screen.getByRole('textbox', { name: /Description/ }), { target: { value: '  Orders are not syncing.  ' } });
    fireEvent.change(screen.getByRole('combobox', { name: /Priority/ }), { target: { value: 'High' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create ticket' }));

    await waitFor(() => expect(props.onSubmit).toHaveBeenCalledWith(expect.objectContaining({
      product_id: 2,
      module_id: null,
      customer_id: null,
      title: 'Sync problem',
      description: 'Orders are not syncing.',
      category: 'General',
      priority: 'High',
    })));
  });
});
