import React, { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, ApiError } from './api';
import { TicketForm } from './components/TicketForm';
import type { Assignee, Customer, DashboardSummary, Product, ProductModule, Ticket, TicketComment, TicketHistory } from './types';

type Page = 'Dashboard' | 'Tickets' | 'Products' | 'Customers' | 'Assignees' | 'AI assistant';
const pages: Page[] = ['Dashboard', 'Tickets', 'Products', 'Customers', 'Assignees', 'AI assistant'];
const statuses = ['Open', 'Triaged', 'In Progress', 'Testing', 'Resolved', 'Closed'];
const priorities = ['Low', 'Medium', 'High', 'Critical'];
const categories = ['Bug', 'Feature Request', 'Technical Support', 'Integration Issue', 'Performance Issue', 'General'];

function message(error: unknown): string {
  return error instanceof ApiError ? error.message : 'Something went wrong. Please try again.';
}

function dateLabel(value?: string | null): string {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(date);
}

export default function App() {
  const [page, setPage] = useState<Page>('Dashboard');
  const [products, setProducts] = useState<Product[]>([]);
  const [modules, setModules] = useState<ProductModule[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [assignees, setAssignees] = useState<Assignee[]>([]);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [ticketTotal, setTicketTotal] = useState(0);
  const [ticketPage, setTicketPage] = useState(1);
  const [search, setSearch] = useState('');
  const [productFilter, setProductFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<TicketComment[]>([]);
  const [history, setHistory] = useState<TicketHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const loadReferenceData = useCallback(async () => {
    const [nextProducts, nextCustomers, nextAssignees] = await Promise.all([api.products(), api.customers(), api.assignees()]);
    const moduleLists = await Promise.all(nextProducts.map((product) => api.modules(product.id)));
    setProducts(nextProducts);
    setCustomers(nextCustomers);
    setAssignees(nextAssignees);
    setModules(moduleLists.flat());
  }, []);

  const loadTickets = useCallback(async () => {
    const result = await api.tickets({
      page: ticketPage,
      page_size: 10,
      q: search.trim() || undefined,
      product_id: productFilter ? Number(productFilter) : undefined,
      status: statusFilter || undefined,
      priority: priorityFilter || undefined,
    });
    setTickets(result.items);
    setTicketTotal(result.total);
  }, [ticketPage, search, productFilter, statusFilter, priorityFilter]);

  const loadDashboard = useCallback(async () => {
    setDashboard(await api.dashboard(productFilter ? Number(productFilter) : undefined));
  }, [productFilter]);

  const refreshPage = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      await loadReferenceData();
      if (page === 'Dashboard') await loadDashboard();
      if (page === 'Tickets') await loadTickets();
    } catch (cause) {
      setError(message(cause));
    } finally {
      setLoading(false);
    }
  }, [page, loadDashboard, loadTickets, loadReferenceData]);

  useEffect(() => { void refreshPage(); }, [refreshPage]);

  async function runAction(action: () => Promise<unknown>, success: string, refresh = true) {
    setWorking(true);
    setError('');
    setNotice('');
    try {
      await action();
      setNotice(success);
      if (refresh) await refreshPage();
    } catch (cause) {
      setError(message(cause));
    } finally {
      setWorking(false);
    }
  }

  async function openTicket(id: number) {
    setLoading(true);
    setError('');
    try {
      const [ticket, nextComments, nextHistory] = await Promise.all([api.ticket(id), api.comments(id), api.history(id)]);
      setSelectedTicket(ticket);
      setComments(nextComments);
      setHistory(nextHistory);
    } catch (cause) {
      setError(message(cause));
    } finally {
      setLoading(false);
    }
  }

  const currentProduct = (id: number | null) => products.find((item) => item.id === id)?.name ?? 'Unassigned';
  const currentModule = (id: number | null) => modules.find((item) => item.id === id)?.name ?? '—';
  const currentCustomer = (id: number | null) => customers.find((item) => item.id === id)?.name ?? (id ? 'Unknown customer' : 'Internal / unassigned');
  const currentAssignee = (id: number | null) => assignees.find((item) => item.id === id)?.name ?? 'Unassigned';

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#dashboard" onClick={(event) => { event.preventDefault(); setPage('Dashboard'); setSelectedTicket(null); }}>
          <span className="brand-mark">T</span><span>Texol<span className="brand-light">Support</span></span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {pages.map((item, index) => (
            <button key={item} className={`nav-item ${page === item && !selectedTicket ? 'active' : ''}`} onClick={() => { setPage(item); setSelectedTicket(null); setNotice(''); setError(''); }}>
              <span className="nav-icon" aria-hidden="true">{['◫', '▤', '◇', '♙', '♧', '✦'][index]}</span>{item}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer"><div className="avatar">LD</div><div><strong>Local demo</strong><small>Internal prototype</small></div></div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Support workspace <span>/</span> {selectedTicket ? 'Ticket details' : page}</div>
          <div className="topbar-right"><span className="prototype-tag">LOCAL PROTOTYPE · NO AUTH</span><span className="top-avatar" aria-label="Local demo operator">LD</span></div>
        </header>

        <div className="content-wrap">
          <div className="prototype-notice" role="note"><span aria-hidden="true">ⓘ</span><span>Internal local-development prototype. Authentication and role-based access control are not implemented.</span></div>
          {(error || notice) && <div className={error ? 'alert alert-error' : 'alert alert-success'} role={error ? 'alert' : 'status'}>{error || notice}<button type="button" aria-label="Dismiss message" onClick={() => { setError(''); setNotice(''); }}>×</button></div>}
          {loading ? <div className="loading-card" role="status"><span className="spinner" /> Loading workspace…</div> : selectedTicket ? (
            <TicketDetail
              ticket={selectedTicket} comments={comments} history={history} products={products} modules={modules} customers={customers} assignees={assignees}
              onBack={() => setSelectedTicket(null)} onOpen={openTicket} onUpdate={async (payload) => {
                const updated = await api.updateTicket(selectedTicket.id, payload);
                setSelectedTicket(updated);
                setNotice('Ticket updated.');
                const [nextComments, nextHistory] = await Promise.all([api.comments(updated.id), api.history(updated.id)]);
                setComments(nextComments); setHistory(nextHistory);
              }}
              onComment={async (comment) => { await api.addComment(selectedTicket.id, comment); setComments(await api.comments(selectedTicket.id)); setNotice('Comment added.'); }}
            />
          ) : (
            <>
              {page === 'Dashboard' && <DashboardView summary={dashboard} products={products} productFilter={productFilter} onFilter={setProductFilter} onOpenTicket={openTicket} productName={currentProduct} />}
              {page === 'Tickets' && <TicketsView tickets={tickets} total={ticketTotal} page={ticketPage} search={search} productFilter={productFilter} statusFilter={statusFilter} priorityFilter={priorityFilter} products={products} productName={currentProduct} moduleName={currentModule} customerName={currentCustomer} assigneeName={currentAssignee} onSearch={(value) => { setSearch(value); setTicketPage(1); }} onProduct={(value) => { setProductFilter(value); setTicketPage(1); }} onStatus={(value) => { setStatusFilter(value); setTicketPage(1); }} onPriority={(value) => { setPriorityFilter(value); setTicketPage(1); }} onPage={setTicketPage} onOpen={openTicket} onCreate={() => setSelectedTicket({} as Ticket)} />}
              {page === 'Products' && <ProductsView products={products} modules={modules} working={working} onCreateProduct={(payload) => runAction(() => api.createProduct(payload), 'Product added.')} onUpdateProduct={(id, payload) => runAction(() => api.updateProduct(id, payload), 'Product updated.')} onCreateModule={(id, payload) => runAction(() => api.createModule(id, payload), 'Module added.')} onUpdateModule={(id, payload) => runAction(() => api.updateModule(id, payload), 'Module updated.')} />}
              {page === 'Customers' && <CustomersView customers={customers} products={products} working={working} onCreate={(payload) => runAction(() => api.createCustomer(payload), 'Customer added.')} onUpdate={(customer, payload) => runAction(() => api.updateCustomer(customer.id, payload), 'Customer updated.')} />}
              {page === 'Assignees' && <AssigneesView assignees={assignees} working={working} onCreate={(payload) => runAction(() => api.createAssignee(payload), 'Assignee added.')} onUpdate={(id, payload) => runAction(() => api.updateAssignee(id, payload), 'Assignee updated.')} />}
              {page === 'AI assistant' && <AssistantView onAsk={async (question) => api.assistant(question)} />}
            </>
          )}
          {selectedTicket && !selectedTicket.id && (
            <div className="modal-backdrop" role="presentation">
              <section className="modal-card" role="dialog" aria-modal="true" aria-labelledby="new-ticket-title">
                <div className="section-heading"><div><p className="eyebrow">TICKET INTAKE</p><h1 id="new-ticket-title">Create a ticket</h1></div><button className="icon-button" aria-label="Close" onClick={() => setSelectedTicket(null)}>×</button></div>
                <p className="section-subtitle">Capture the issue and route it to the right product team.</p>
                <TicketForm products={products} modules={modules} customers={customers} assignees={assignees} submitting={working} onCancel={() => setSelectedTicket(null)} onSubmit={async (payload) => {
                  await runAction(async () => { const created = await api.createTicket(payload); setSelectedTicket(null); await openTicket(created.id); }, 'Ticket created.', false);
                  await loadTickets();
                }} />
              </section>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="section-subtitle">{description}</p></div>{action}</div>;
}

function DashboardView({ summary, products, productFilter, onFilter, onOpenTicket, productName }: {
  summary: DashboardSummary | null; products: Product[]; productFilter: string; onFilter: (value: string) => void;
  onOpenTicket: (id: number) => void; productName: (id: number | null) => string;
}) {
  if (!summary) return <section className="empty-state"><h2>No dashboard data</h2><p>The summary endpoint did not return data.</p></section>;
  const cards = [
    ['Total tickets', summary.total_tickets, 'All recorded issues', 'ink'],
    ['Open', summary.open_tickets, 'Awaiting triage', 'blue'],
    ['In progress', summary.in_progress_tickets, 'Being worked on', 'violet'],
    ['Resolved', summary.resolved_tickets, 'Completed requests', 'green'],
    ['Critical', summary.critical_tickets, 'Needs attention', 'red'],
  ] as const;
  return <>
    <PageHeading eyebrow="OVERVIEW" title="Good morning" description="A live view of support activity across your products."
      action={<label className="inline-filter">Product view<select aria-label="Filter dashboard by product" value={productFilter} onChange={(event) => onFilter(event.target.value)}><option value="">All products</option>{products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}</select></label>} />
    <div className="stat-grid">{cards.map(([label, value, hint, color]) => <article className="stat-card" key={label}><span className={`stat-dot ${color}`} /><p>{label}</p><strong>{value}</strong><small>{hint}</small></article>)}</div>
    <div className="dashboard-grid">
      <section className="surface"><div className="surface-heading"><div><h2>Tickets by product</h2><p>Current distribution across the portfolio</p></div></div>
        {summary.by_product.length ? <div className="product-bars">{summary.by_product.map((row) => {
          const max = Math.max(...summary.by_product.map((item) => item.count), 1);
          return <div className="product-bar-row" key={row.product_id}><div><span>{row.product_name}</span><b>{row.count}</b></div><div className="bar-track"><span style={{ width: `${Math.max(5, (row.count / max) * 100)}%` }} /></div></div>;
        })}</div> : <div className="empty-inline">No product tickets match this filter.</div>}
      </section>
      <section className="surface"><div className="surface-heading"><div><h2>Recent tickets</h2><p>The latest updates in your workspace</p></div></div>
        {summary.recent_tickets.length ? <div className="recent-list">{summary.recent_tickets.map((ticket) => <button className="recent-row" key={ticket.id} onClick={() => onOpenTicket(ticket.id)}><span className="ticket-initial">{ticket.title.slice(0, 1).toUpperCase()}</span><span className="recent-copy"><b>{ticket.title}</b><small>{ticket.ticket_no} · {productName(ticket.product_id)}</small></span><span className={`status-chip ${ticket.status.toLowerCase().replaceAll(' ', '-')}`}>{ticket.status}</span></button>)}</div> : <div className="empty-inline">No tickets yet. Create one from the Tickets page.</div>}
      </section>
    </div>
  </>;
}

function TicketsView(props: {
  tickets: Ticket[]; total: number; page: number; search: string; productFilter: string; statusFilter: string; priorityFilter: string;
  products: Product[]; productName: (id: number | null) => string; moduleName: (id: number | null) => string;
  customerName: (id: number | null) => string; assigneeName: (id: number | null) => string;
  onSearch: (value: string) => void; onProduct: (value: string) => void; onStatus: (value: string) => void; onPriority: (value: string) => void;
  onPage: (page: number) => void; onOpen: (id: number) => void; onCreate: () => void;
}) {
  const pageCount = Math.max(1, Math.ceil(props.total / 10));
  return <>
    <PageHeading eyebrow="SUPPORT QUEUE" title="Tickets" description="Search, filter, and manage support requests across products."
      action={<button className="button button-primary" onClick={props.onCreate}><span aria-hidden="true">＋</span> New ticket</button>} />
    <section className="surface">
      <div className="filter-row"><label className="search-field"><span aria-hidden="true">⌕</span><input aria-label="Search tickets" value={props.search} onChange={(event) => props.onSearch(event.target.value)} placeholder="Search ticket number or title" /></label>
        <select aria-label="Filter by product" value={props.productFilter} onChange={(event) => props.onProduct(event.target.value)}><option value="">All products</option>{props.products.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select>
        <select aria-label="Filter by status" value={props.statusFilter} onChange={(event) => props.onStatus(event.target.value)}><option value="">All statuses</option>{statuses.map((item) => <option key={item}>{item}</option>)}</select>
        <select aria-label="Filter by priority" value={props.priorityFilter} onChange={(event) => props.onPriority(event.target.value)}><option value="">All priorities</option>{priorities.map((item) => <option key={item}>{item}</option>)}</select>
      </div>
      {props.tickets.length ? <div className="table-wrap"><table><thead><tr><th>Ticket</th><th>Product / module</th><th>Customer</th><th>Category</th><th>Priority</th><th>Status</th><th>Assignee</th><th>Created</th></tr></thead><tbody>{props.tickets.map((ticket) => <tr key={ticket.id} onClick={() => props.onOpen(ticket.id)} tabIndex={0} onKeyDown={(event) => { if (event.key === 'Enter') props.onOpen(ticket.id); }}>
        <td><b className="ticket-title">{ticket.ticket_no || `#${ticket.id}`}</b><span className="table-secondary">{ticket.title}</span></td><td>{props.productName(ticket.product_id)}<span className="table-secondary">{props.moduleName(ticket.module_id)}</span></td><td>{props.customerName(ticket.customer_id)}</td><td>{ticket.category}</td><td><span className={`priority-chip ${ticket.priority.toLowerCase()}`}>{ticket.priority}</span></td><td><span className={`status-chip ${ticket.status.toLowerCase().replaceAll(' ', '-')}`}>{ticket.status}</span></td><td>{props.assigneeName(ticket.assigned_to)}</td><td>{dateLabel(ticket.created_at)}</td>
      </tr>)}</tbody></table></div> : <div className="empty-state"><span className="empty-icon">▤</span><h2>No tickets found</h2><p>Try a different search or create a ticket for your team.</p><button className="button button-primary" onClick={props.onCreate}>Create ticket</button></div>}
      <div className="pagination"><span>{props.total ? `Showing ${(props.page - 1) * 10 + 1}–${Math.min(props.page * 10, props.total)} of ${props.total}` : '0 tickets'}</span><div><button className="button button-quiet" disabled={props.page <= 1} onClick={() => props.onPage(props.page - 1)}>Previous</button><span>Page {props.page} of {pageCount}</span><button className="button button-quiet" disabled={props.page >= pageCount} onClick={() => props.onPage(props.page + 1)}>Next</button></div></div>
    </section>
  </>;
}

function TicketDetail({ ticket, comments, history, products, modules, customers, assignees, onBack, onUpdate, onComment }: {
  ticket: Ticket; comments: TicketComment[]; history: TicketHistory[]; products: Product[]; modules: ProductModule[]; customers: Customer[]; assignees: Assignee[];
  onBack: () => void; onOpen: (id: number) => void; onUpdate: (payload: Record<string, unknown>) => Promise<void>; onComment: (comment: string) => Promise<void>;
}) {
  const [status, setStatus] = useState(ticket.status);
  const [priority, setPriority] = useState(ticket.priority);
  const [assignee, setAssignee] = useState(ticket.assigned_to ? String(ticket.assigned_to) : '');
  const [title, setTitle] = useState(ticket.title);
  const [description, setDescription] = useState(ticket.description);
  const [category, setCategory] = useState(ticket.category);
  const [comment, setComment] = useState('');
  const [saving, setSaving] = useState(false);
  const [localError, setLocalError] = useState('');
  useEffect(() => {
    setStatus(ticket.status);
    setPriority(ticket.priority);
    setAssignee(ticket.assigned_to ? String(ticket.assigned_to) : '');
    setTitle(ticket.title);
    setDescription(ticket.description);
    setCategory(ticket.category);
  }, [ticket]);
  const productName = products.find((item) => item.id === ticket.product_id)?.name ?? 'Unassigned legacy ticket';
  const moduleName = modules.find((item) => item.id === ticket.module_id)?.name ?? 'No module';
  const customerName = customers.find((item) => item.id === ticket.customer_id)?.name ?? 'Internal / unassigned';
  const assigneeName = assignees.find((item) => item.id === ticket.assigned_to)?.name ?? 'Unassigned';
  async function save() {
    setSaving(true); setLocalError('');
    try { await onUpdate({ status, priority, assigned_to: assignee ? Number(assignee) : null }); }
    catch (error) { setLocalError(message(error)); }
    finally { setSaving(false); }
  }
  async function saveDetails(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true); setLocalError('');
    try { await onUpdate({ title: title.trim(), description: description.trim(), category }); }
    catch (error) { setLocalError(message(error)); }
    finally { setSaving(false); }
  }
  async function addComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!comment.trim()) return;
    setSaving(true); setLocalError('');
    try { await onComment(comment.trim()); setComment(''); }
    catch (error) { setLocalError(message(error)); }
    finally { setSaving(false); }
  }
  return <>
    <button className="back-link" onClick={onBack}>← Back to tickets</button>
    {localError && <div className="alert alert-error" role="alert">{localError}</div>}
    <div className="detail-heading"><div><p className="eyebrow">{ticket.ticket_no || `TICKET #${ticket.id}`}</p><h1>{ticket.title}</h1><p className="section-subtitle">Created {dateLabel(ticket.created_at)} · Updated {dateLabel(ticket.updated_at)}</p></div><span className={`status-chip large ${ticket.status.toLowerCase().replaceAll(' ', '-')}`}>{ticket.status}</span></div>
    <div className="detail-layout"><div className="detail-main">
      <section className="surface detail-section"><div className="surface-heading"><div><h2>Description</h2></div></div><p className="description-text">{ticket.description}</p></section>
      <section className="surface detail-section"><div className="surface-heading"><div><h2>Edit ticket details</h2><p>Update the title, description, or category.</p></div></div>
        <form className="compact-form" onSubmit={saveDetails}><label>Title<input aria-label="Edit title" required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} /></label><label>Description<textarea aria-label="Edit description" required rows={4} value={description} onChange={(event) => setDescription(event.target.value)} /></label><label>Category<select aria-label="Edit category" value={category} onChange={(event) => setCategory(event.target.value)}>{categories.map((item) => <option key={item}>{item}</option>)}</select></label><button className="button button-primary" disabled={saving}>{saving ? 'Saving…' : 'Save ticket details'}</button></form>
      </section>
      <section className="surface detail-section"><div className="surface-heading"><div><h2>Conversation</h2><p>Comments from the local demo workspace</p></div></div>
        <form className="comment-form" onSubmit={addComment}><label htmlFor="ticket-comment">Add a comment</label><textarea id="ticket-comment" value={comment} onChange={(event) => setComment(event.target.value)} rows={3} placeholder="Share an update with the team…" required /><button className="button button-primary" disabled={saving || !comment.trim()}>Add comment</button></form>
        {comments.length ? <div className="timeline">{comments.map((item) => <article className="timeline-item" key={item.id}><span className="timeline-avatar">LD</span><div><div className="timeline-meta"><b>{item.author_label || 'Local demo operator'}</b><time>{dateLabel(item.created_at)}</time></div><p>{item.comment}</p></div></article>)}</div> : <div className="empty-inline">No comments yet.</div>}
      </section>
      <section className="surface detail-section"><div className="surface-heading"><div><h2>Activity</h2><p>Recorded ticket changes</p></div></div>
        {history.length ? <div className="timeline">{history.map((item) => <article className="timeline-item" key={item.id}><span className="activity-dot" /><div><div className="timeline-meta"><b>{item.actor_label || 'Local demo operator'} · {item.changed_field.replaceAll('_', ' ')}</b><time>{dateLabel(item.created_at)}</time></div><p>{item.old_value ? `${item.old_value} → ` : ''}{item.new_value ?? '—'}</p></div></article>)}</div> : <div className="empty-inline">No activity recorded yet.</div>}
      </section>
    </div><aside className="detail-side"><section className="surface detail-section"><div className="surface-heading"><div><h2>Ticket properties</h2></div></div>
      <dl className="property-list"><div><dt>Product</dt><dd>{productName}</dd></div><div><dt>Module</dt><dd>{moduleName}</dd></div><div><dt>Customer</dt><dd>{customerName}</dd></div><div><dt>Category</dt><dd>{ticket.category}</dd></div><div><dt>Current assignee</dt><dd>{assigneeName}</dd></div><div><dt>Resolved at</dt><dd>{dateLabel(ticket.resolved_at)}</dd></div></dl>
      <div className="edit-properties"><label>Status<select value={status} onChange={(event) => setStatus(event.target.value)}>{statuses.map((item) => <option key={item}>{item}</option>)}</select></label><label>Priority<select value={priority} onChange={(event) => setPriority(event.target.value)}>{priorities.map((item) => <option key={item}>{item}</option>)}</select></label><label>Assignee<select value={assignee} onChange={(event) => setAssignee(event.target.value)}><option value="">Unassigned</option>{assignees.filter((item) => item.is_active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><button className="button button-primary button-full" onClick={() => void save()} disabled={saving}>{saving ? 'Saving…' : 'Save changes'}</button></div>
    </section></aside></div>
  </>;
}

function ProductsView({ products, modules, working, onCreateProduct, onUpdateProduct, onCreateModule, onUpdateModule }: {
  products: Product[]; modules: ProductModule[]; working: boolean;
  onCreateProduct: (payload: { name: string; code: string; description: string }) => void;
  onUpdateProduct: (id: number, payload: Partial<Product>) => void;
  onCreateModule: (id: number, payload: { name: string; code: string; description: string }) => void;
  onUpdateModule: (id: number, payload: Partial<ProductModule>) => void;
}) {
  const [selected, setSelected] = useState<number | null>(products[0]?.id ?? null);
  const [name, setName] = useState(''); const [code, setCode] = useState(''); const [description, setDescription] = useState('');
  const [moduleName, setModuleName] = useState(''); const [moduleCode, setModuleCode] = useState('');
  const active = products.find((item) => item.id === selected);
  useEffect(() => { if (!selected && products[0]) setSelected(products[0].id); }, [products, selected]);
  useEffect(() => { if (active) { setEditName(active.name); setEditCode(active.code); setEditDescription(active.description || ''); } }, [active]);
  const [editName, setEditName] = useState(''); const [editCode, setEditCode] = useState(''); const [editDescription, setEditDescription] = useState('');
  return <>
    <PageHeading eyebrow="PRODUCT CATALOG" title="Products & modules" description="Organize support work by product and functional area." />
    <div className="two-column-layout"><section className="surface"><div className="surface-heading"><div><h2>Products</h2><p>{products.length} registered products</p></div></div>
      <form className="compact-form" onSubmit={(event) => { event.preventDefault(); onCreateProduct({ name, code, description }); setName(''); setCode(''); setDescription(''); }}><h3>Add product</h3><div className="form-grid"><label>Name<input required value={name} onChange={(event) => setName(event.target.value)} placeholder="Product name" /></label><label>Code<input required value={code} onChange={(event) => setCode(event.target.value.toUpperCase())} placeholder="CODE" /></label><label className="form-span">Description<input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Optional summary" /></label></div><button className="button button-primary" disabled={working}>Add product</button></form>
      <div className="catalog-list">{products.map((product) => <button key={product.id} className={`catalog-row ${selected === product.id ? 'selected' : ''}`} onClick={() => setSelected(product.id)}><span className="product-code">{product.code}</span><span className="catalog-copy"><b>{product.name}</b><small>{product.description || 'No description'}</small></span><span className={product.is_active ? 'active-label' : 'inactive-label'}>{product.is_active ? 'Active' : 'Inactive'}</span><span role="presentation" className="row-chevron">›</span></button>)}</div>
    </section><section className="surface"><div className="surface-heading"><div><h2>{active ? `${active.name} modules` : 'Product modules'}</h2><p>Modules are scoped to one product.</p></div>{active && <button className="button button-quiet" onClick={() => onUpdateProduct(active.id, { is_active: !active.is_active })} disabled={working}>{active.is_active ? 'Deactivate' : 'Activate'} product</button>}</div>
      {active ? <><form className="compact-form" onSubmit={(event) => { event.preventDefault(); onUpdateProduct(active.id, { name: editName.trim(), code: editCode.trim(), description: editDescription.trim() }); }}><h3>Edit product</h3><div className="form-grid"><label>Name<input required value={editName} onChange={(event) => setEditName(event.target.value)} /></label><label>Code<input required value={editCode} onChange={(event) => setEditCode(event.target.value.toUpperCase())} /></label><label className="form-span">Description<input value={editDescription} onChange={(event) => setEditDescription(event.target.value)} /></label></div><button className="button button-quiet" disabled={working}>Save product</button></form>
      <form className="compact-form" onSubmit={(event) => { event.preventDefault(); onCreateModule(active.id, { name: moduleName, code: moduleCode, description: '' }); setModuleName(''); setModuleCode(''); }}><h3>Add module to {active.name}</h3><div className="form-grid"><label>Name<input required value={moduleName} onChange={(event) => setModuleName(event.target.value)} placeholder="Module name" /></label><label>Code<input required value={moduleCode} onChange={(event) => setModuleCode(event.target.value.toUpperCase())} placeholder="MODULE_CODE" /></label></div><button className="button button-secondary" disabled={working}>Add module</button></form>
      {modules.filter((item) => item.product_id === active.id).length ? <div className="module-list">{modules.filter((item) => item.product_id === active.id).map((item) => <ModuleEditor key={item.id} module={item} working={working} onUpdate={onUpdateModule} />)}</div> : <div className="empty-inline">No modules added yet.</div>}</> : <div className="empty-state compact"><h2>Select a product</h2><p>Choose a product to manage its modules.</p></div>}
    </section></div>
  </>;
}

function ModuleEditor({ module, working, onUpdate }: { module: ProductModule; working: boolean; onUpdate: (id: number, payload: Partial<ProductModule>) => void }) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(module.name);
  const [code, setCode] = useState(module.code);
  useEffect(() => { setName(module.name); setCode(module.code); }, [module.name, module.code]);
  return <div className="module-row"><span><b>{module.name}</b><small>{module.code}</small></span><div className="row-actions">{editing && <><input aria-label={`Edit ${module.name} name`} value={name} onChange={(event) => setName(event.target.value)} /><input aria-label={`Edit ${module.name} code`} value={code} onChange={(event) => setCode(event.target.value.toUpperCase())} /></>}<button className="button button-quiet" disabled={working} onClick={() => { if (editing) onUpdate(module.id, { name: name.trim(), code: code.trim() }); setEditing(!editing); }}>{editing ? 'Save' : 'Edit'}</button><button className="button button-quiet" disabled={working} onClick={() => onUpdate(module.id, { is_active: !module.is_active })}>{module.is_active ? 'Deactivate' : 'Activate'}</button></div></div>;
}

function CustomersView({ customers, products, working, onCreate, onUpdate }: {
  customers: Customer[]; products: Product[]; working: boolean;
  onCreate: (payload: { name: string; code: string; email: string; phone: string; product_ids: number[] }) => void;
  onUpdate: (customer: Customer, payload: { name: string; code: string; email: string; phone: string; is_active: boolean; product_ids: number[] }) => void;
}) {
  const [editing, setEditing] = useState<Customer | null>(null);
  const [name, setName] = useState(''); const [code, setCode] = useState(''); const [email, setEmail] = useState(''); const [phone, setPhone] = useState(''); const [productIds, setProductIds] = useState<number[]>([]);
  function beginEdit(customer: Customer) { setEditing(customer); setName(customer.name); setCode(customer.code); setEmail(customer.email || ''); setPhone(customer.phone || ''); setProductIds(customer.product_ids); }
  function reset() { setEditing(null); setName(''); setCode(''); setEmail(''); setPhone(''); setProductIds([]); }
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const payload = { name: name.trim(), code: code.trim(), email: email.trim(), phone: phone.trim(), is_active: editing?.is_active ?? true, product_ids: productIds }; if (editing) onUpdate(editing, payload); else onCreate(payload); reset(); }
  return <>
    <PageHeading eyebrow="CUSTOMER DIRECTORY" title="Customers" description="Manage customer records and the products they use." />
    <div className="two-column-layout"><section className="surface"><div className="surface-heading"><div><h2>{editing ? 'Edit customer' : 'Add customer'}</h2><p>Use fictional or approved customer data only.</p></div></div>
      <form className="form-grid" onSubmit={submit}><label>Name<input required value={name} onChange={(event) => setName(event.target.value)} /></label><label>Code<input required value={code} onChange={(event) => setCode(event.target.value.toUpperCase())} /></label><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label><label>Phone<input type="tel" value={phone} onChange={(event) => setPhone(event.target.value)} /></label>
        <fieldset className="product-checks form-span"><legend>Products used</legend>{products.length ? products.map((product) => <label key={product.id} className="check-label"><input type="checkbox" checked={productIds.includes(product.id)} onChange={(event) => setProductIds(event.target.checked ? [...productIds, product.id] : productIds.filter((id) => id !== product.id))} />{product.name}</label>) : <span className="muted">Register a product first.</span>}</fieldset>
        {editing && <label className="check-label form-span"><input type="checkbox" checked={editing.is_active} onChange={(event) => setEditing({ ...editing, is_active: event.target.checked })} />Active customer</label>}
        <div className="form-actions form-span">{editing && <button type="button" className="button button-quiet" onClick={reset}>Cancel edit</button>}<button className="button button-primary" disabled={working}>{editing ? 'Save customer' : 'Add customer'}</button></div>
      </form>
    </section><section className="surface"><div className="surface-heading"><div><h2>Customer records</h2><p>{customers.length} customers</p></div></div>
      {customers.length ? <div className="table-wrap"><table><thead><tr><th>Name</th><th>Code</th><th>Products</th><th>Contact</th><th>State</th><th></th></tr></thead><tbody>{customers.map((customer) => <tr key={customer.id}><td><b>{customer.name}</b></td><td>{customer.code}</td><td>{customer.product_ids.map((id) => products.find((product) => product.id === id)?.name).filter(Boolean).join(', ') || 'None'}</td><td>{customer.email || customer.phone || '—'}</td><td>{customer.is_active ? 'Active' : 'Inactive'}</td><td><button className="button button-quiet" onClick={() => beginEdit(customer)}>Edit</button></td></tr>)}</tbody></table></div> : <div className="empty-state"><h2>No customers yet</h2><p>Add a customer record to associate customer tickets.</p></div>}
    </section></div>
  </>;
}

function AssigneesView({ assignees, working, onCreate, onUpdate }: {
  assignees: Assignee[]; working: boolean; onCreate: (payload: { name: string; email: string }) => void; onUpdate: (id: number, payload: Partial<Assignee>) => void;
}) {
  const [name, setName] = useState(''); const [email, setEmail] = useState('');
  return <><PageHeading eyebrow="LOCAL DIRECTORY" title="Assignees" description="Demo assignment directory only. These entries are not authenticated user accounts." />
    <div className="two-column-layout"><section className="surface"><div className="surface-heading"><div><h2>Add assignee</h2><p>Use synthetic names for demonstrations.</p></div></div><form className="form-grid" onSubmit={(event) => { event.preventDefault(); onCreate({ name: name.trim(), email: email.trim() }); setName(''); setEmail(''); }}><label>Name<input required value={name} onChange={(event) => setName(event.target.value)} /></label><label>Email <span className="optional">Optional</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label><button className="button button-primary form-span" disabled={working}>Add assignee</button></form></section>
      <section className="surface"><div className="surface-heading"><div><h2>Demo directory</h2><p>{assignees.length} entries</p></div></div>{assignees.length ? <div className="catalog-list">{assignees.map((item) => <div className="catalog-row" key={item.id}><span className="avatar soft">{item.name.slice(0, 1).toUpperCase()}</span><span className="catalog-copy"><b>{item.name}</b><small>{item.email || 'No email supplied'}</small></span><span className={item.is_active ? 'active-label' : 'inactive-label'}>{item.is_active ? 'Active' : 'Inactive'}</span><button className="button button-quiet" disabled={working} onClick={() => onUpdate(item.id, { is_active: !item.is_active })}>{item.is_active ? 'Deactivate' : 'Activate'}</button></div>)}</div> : <div className="empty-state"><span className="empty-icon">♧</span><h2>No assignees yet</h2><p>Add a synthetic demo assignee to enable assignment.</p></div>}</section></div>
  </>;
}

function AssistantView({ onAsk }: { onAsk: (question: string) => Promise<{ answer: string; configured: boolean }> }) {
  const [question, setQuestion] = useState(''); const [answer, setAnswer] = useState(''); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!question.trim()) return; setBusy(true); setError(''); try { const response = await onAsk(question.trim()); setAnswer(response.answer); } catch (cause) { setError(message(cause)); } finally { setBusy(false); } }
  return <><PageHeading eyebrow="OPTIONAL TOOL" title="AI assistant" description="Standalone assistant questions are not connected to ticket records." /><section className="surface assistant-card"><div className="assistant-symbol">✦</div><h2>Ask a support question</h2><p>The assistant receives only the question you submit. It cannot access or update tickets.</p><form onSubmit={submit}><label htmlFor="assistant-question">Your question</label><textarea id="assistant-question" rows={5} required value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="How can I troubleshoot a sync issue?" /><button className="button button-primary" disabled={busy}>{busy ? 'Thinking…' : 'Ask assistant'}</button></form>{error && <div className="alert alert-error" role="alert">{error}</div>}{answer && <div className="assistant-answer"><b>Response</b><p>{answer}</p></div>}</section></>;
}
