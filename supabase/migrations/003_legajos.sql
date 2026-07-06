-- Persistencia durable de legajos fiscales (C3).
-- El backend escribe dual: archivo local (respaldo/offline) + esta tabla (fuente durable en deploy).
-- El sellado SHA256 viaja con el legajo: la integridad se verifica sobre el contenido, venga de donde venga.

create table if not exists public.legajos (
  id text primary key,
  tenant_id uuid references public.tenants(id) on delete cascade,
  creado_en text not null default '',
  estado text not null default 'cerrado',
  operador jsonb not null default '{}'::jsonb,
  excel text not null default '',
  total_proveedores integer not null default 0,
  sha256 text not null default '',
  reglas_aplicadas jsonb not null default '{}'::jsonb,
  padrones_snapshot jsonb not null default '{}'::jsonb,
  resumen jsonb not null default '[]'::jsonb,
  resultados jsonb not null default '[]'::jsonb,
  registrado_en timestamptz not null default now()
);

create index if not exists idx_legajos_tenant_creado on public.legajos (tenant_id, registrado_en desc);

alter table public.legajos enable row level security;

-- MVP: el backend FastAPI usa service_role server-side. Sin políticas públicas (ver 001).
