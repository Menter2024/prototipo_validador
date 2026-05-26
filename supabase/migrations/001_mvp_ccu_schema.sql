-- MVP fiscal CCU / Menter: esquema Supabase barato, server-driven.
-- Ejecutar en SQL Editor o vía MCP apply_migration cuando el proyecto esté accesible.

create extension if not exists pgcrypto;

create table if not exists public.tenants (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  nombre text not null,
  estado text not null default 'activo' check (estado in ('activo','pausado','archivado')),
  creado_en timestamptz not null default now()
);

create table if not exists public.empresas_cuit (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  cuit text not null,
  razon_social text not null default '',
  rol text not null default 'empresa_grupo' check (rol in ('empresa_grupo','agente_retencion','agente_percepcion','agente_informacion','proveedor','cliente')),
  notas text not null default '',
  creado_en timestamptz not null default now(),
  unique (tenant_id, cuit)
);

create table if not exists public.fuentes_fiscales (
  id text primary key,
  organismo text not null,
  nombre text not null,
  jurisdiccion text not null default '',
  prioridad text not null default 'P3',
  tipo_acceso text not null default 'pendiente',
  url text not null default '',
  estado_integracion text not null default 'pendiente'
);

create table if not exists public.padron_versiones (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  fuente_id text references public.fuentes_fiscales(id),
  provincia text not null,
  periodo text not null default '',
  vigencia_hasta date,
  registros integer not null default 0,
  estado text not null default 'pendiente_validacion' check (estado in ('pendiente_validacion','observado','activo','vencido','rechazado','archivado')),
  storage_original_path text not null default '',
  storage_normalizado_path text not null default '',
  sha256_original text not null default '',
  sha256_normalizado text not null default '',
  calidad jsonb not null default '{}'::jsonb,
  evidencia jsonb not null default '{}'::jsonb,
  creado_en timestamptz not null default now()
);

create index if not exists idx_padron_versiones_tenant_fuente on public.padron_versiones (tenant_id, fuente_id, periodo);
create index if not exists idx_padron_versiones_estado on public.padron_versiones (tenant_id, estado);

create table if not exists public.padron_registros_demo (
  id bigserial primary key,
  padron_version_id uuid not null references public.padron_versiones(id) on delete cascade,
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  cuit text not null,
  jurisdiccion text not null default '',
  regimen text not null default '',
  alicuota_retencion text not null default '',
  alicuota_percepcion text not null default '',
  vigencia_desde date,
  vigencia_hasta date,
  datos jsonb not null default '{}'::jsonb
);

create index if not exists idx_padron_registros_demo_lookup on public.padron_registros_demo (tenant_id, cuit, jurisdiccion);

create table if not exists public.validaciones (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  cuit text not null,
  resultado jsonb not null default '{}'::jsonb,
  excel_storage_path text not null default '',
  legajo_id text not null default '',
  creado_en timestamptz not null default now()
);

create index if not exists idx_validaciones_tenant_cuit on public.validaciones (tenant_id, cuit, creado_en desc);

create table if not exists public.accesos_fiscales (
  id text primary key,
  tenant_id uuid references public.tenants(id) on delete cascade,
  cliente text not null,
  cuit_agente text not null,
  cuit_agente_limpio text not null,
  organismo text not null,
  servicio text not null,
  fuente_id text,
  tipo_acceso text not null,
  estado text not null,
  alcance text not null default '',
  responsable text not null default '',
  notas text not null default '',
  evidencias jsonb not null default '[]'::jsonb,
  historial jsonb not null default '[]'::jsonb,
  creado_en timestamptz not null default now(),
  actualizado_en timestamptz not null default now()
);

create index if not exists idx_accesos_fiscales_tenant on public.accesos_fiscales (tenant_id, cuit_agente_limpio, organismo);

create table if not exists public.cola_asistida (
  id text primary key,
  tenant_id uuid references public.tenants(id) on delete cascade,
  tipo text not null,
  fuente_id text not null default '',
  cuit text not null default '',
  estado text not null default 'pendiente' check (estado in ('pendiente','en_proceso','resuelto','bloqueado','descartado')),
  prioridad text not null default 'media',
  detalle jsonb not null default '{}'::jsonb,
  creado_en timestamptz not null default now(),
  actualizado_en timestamptz not null default now()
);

create table if not exists public.audit_eventos (
  id bigserial primary key,
  tenant_id uuid references public.tenants(id) on delete set null,
  actor text not null default 'sistema',
  accion text not null,
  entidad text not null default '',
  entidad_id text not null default '',
  detalle jsonb not null default '{}'::jsonb,
  creado_en timestamptz not null default now()
);

alter table public.tenants enable row level security;
alter table public.empresas_cuit enable row level security;
alter table public.fuentes_fiscales enable row level security;
alter table public.padron_versiones enable row level security;
alter table public.padron_registros_demo enable row level security;
alter table public.validaciones enable row level security;
alter table public.accesos_fiscales enable row level security;
alter table public.cola_asistida enable row level security;
alter table public.audit_eventos enable row level security;

-- MVP: el backend FastAPI usa service_role server-side. No se crean políticas públicas.
-- Cuando haya usuarios directos contra Supabase, agregar políticas por tenant/app_metadata.

do $$
begin
  insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  values ('menter-fiscal', 'menter-fiscal', false, 104857600, null)
  on conflict (id) do nothing;
exception when undefined_table then
  raise notice 'storage.buckets no disponible en este contexto; crear bucket privado menter-fiscal desde dashboard.';
end $$;

insert into public.tenants (slug, nombre)
values ('ccu', 'CCU Argentina - MVP')
on conflict (slug) do nothing;
