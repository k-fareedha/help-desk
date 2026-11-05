import React, { useMemo, useState, type FormEvent } from 'react';
import type { Assignee, Customer, Product, ProductModule, TicketCategory, TicketPriority } from '../types';

const categories: TicketCategory[] = ['Bug', 'Feature Request', 'Technical Support', 'Integration Issue', 'Performance Issue', 'General'];
const priorities: TicketPriority[] = ['Low', 'Medium', 'High', 'Critical'];

type Props = {
  products: Product[];
  modules: ProductModule[];
  customers: Customer[];
  assignees: Assignee[];
  submitting: boolean;
  onSubmit: (payload: Record<string, unknown>) => Promise<void>;
  onCancel: () => void;
};

export function TicketForm({ products, modules, customers, assignees, submitting, onSubmit, onCancel }: Props) {
  const [productId, setProductId] = useState('');
  const [moduleId, setModuleId] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [assigneeId, setAssigneeId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<TicketCategory>('General');
  const [priority, setPriority] = useState<TicketPriority>('Medium');
  const availableModules = useMemo(() => modules.filter((item) => item.product_id === Number(productId) && item.is_active), [modules, productId]);
  const availableCustomers = useMemo(() => customers.filter((item) => item.is_active && item.product_ids.includes(Number(productId))), [customers, productId]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!productId || !title.trim() || !description.trim()) return;
    await onSubmit({
      product_id: Number(productId),
      module_id: moduleId ? Number(moduleId) : null,
      customer_id: customerId ? Number(customerId) : null,
      assigned_to: assigneeId ? Number(assigneeId) : null,
      title: title.trim(), description: description.trim(), category, priority,
    });
  }

  return (
    <form className="form-grid" onSubmit={submit} aria-label="Create ticket">
      <label>Product <span aria-hidden="true">*</span>
        <select required value={productId} onChange={(event) => { setProductId(event.target.value); setModuleId(''); setCustomerId(''); }}>
          <option value="">Select a product</option>
          {products.filter((item) => item.is_active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>
      <label>Module <span className="optional">Optional</span>
        <select value={moduleId} disabled={!productId} onChange={(event) => setModuleId(event.target.value)}>
          <option value="">No module</option>
          {availableModules.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>
      <label>Customer <span className="optional">Optional</span>
        <select value={customerId} disabled={!productId} onChange={(event) => setCustomerId(event.target.value)}>
          <option value="">Internal / no customer</option>
          {availableCustomers.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>
      <label>Assignee <span className="optional">Optional</span>
        <select value={assigneeId} onChange={(event) => setAssigneeId(event.target.value)}>
          <option value="">Unassigned</option>
          {assignees.filter((item) => item.is_active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>
      <label className="form-span">Title <span aria-hidden="true">*</span>
        <input required maxLength={240} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Summarize the issue" />
      </label>
      <label className="form-span">Description <span aria-hidden="true">*</span>
        <textarea required value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Describe what happened and what you expected." rows={5} />
      </label>
      <label>Category
        <select value={category} onChange={(event) => setCategory(event.target.value as TicketCategory)}>
          {categories.map((item) => <option key={item}>{item}</option>)}
        </select>
      </label>
      <label>Priority
        <select value={priority} onChange={(event) => setPriority(event.target.value as TicketPriority)}>
          {priorities.map((item) => <option key={item}>{item}</option>)}
        </select>
      </label>
      <div className="form-actions form-span">
        <button className="button button-quiet" type="button" onClick={onCancel}>Cancel</button>
        <button className="button button-primary" type="submit" disabled={submitting || !productId}>{submitting ? 'Creating…' : 'Create ticket'}</button>
      </div>
    </form>
  );
}
