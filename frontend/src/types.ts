export type Product = {
  id: number;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
};

export type ProductModule = {
  id: number;
  product_id: number;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
};

export type Customer = {
  id: number;
  name: string;
  code: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  product_ids: number[];
};

export type Assignee = { id: number; name: string; email: string | null; is_active: boolean };
export type TicketStatus = 'Open' | 'Triaged' | 'In Progress' | 'Testing' | 'Resolved' | 'Closed';
export type TicketPriority = 'Low' | 'Medium' | 'High' | 'Critical';
export type TicketCategory = 'Bug' | 'Feature Request' | 'Technical Support' | 'Integration Issue' | 'Performance Issue' | 'General';

export type Ticket = {
  id: number;
  ticket_no: string;
  product_id: number | null;
  product_name?: string | null;
  module_id: number | null;
  module_name?: string | null;
  customer_id: number | null;
  customer_name?: string | null;
  title: string;
  description: string;
  category: TicketCategory | string;
  priority: TicketPriority | string;
  status: TicketStatus | string;
  assigned_to: number | null;
  assignee_name?: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
};

export type TicketPage = { items: Ticket[]; page: number; page_size: number; total: number };
export type TicketComment = { id: number; ticket_id: number; author_label: string; comment: string; created_at: string };
export type TicketHistory = { id: number; ticket_id: number; changed_field: string; old_value: string | null; new_value: string | null; actor_label: string; created_at: string };
export type DashboardSummary = {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  resolved_tickets: number;
  critical_tickets: number;
  by_product: Array<{ product_id: number; product_name: string; count: number }>;
  recent_tickets: Ticket[];
};
