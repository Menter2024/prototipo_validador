-- Jobs asincrónicos para importación real de padrones.
-- Separa upload, procesamiento Cloud Run Job, validación e indexación.

create table if not exists public.padron_import_jobs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  provincia text not null,
  periodo text not null default '',
  vigencia_hasta date,
  fuente_id text references public.fuentes_fiscales(id),
  cliente text not null default 'CCU',
  cuit_agente text not null default '',
  estado text not null default 'pendiente_upload' check (estado in (
    'pendiente_upload',
    'upload_completo',
    'pendiente_proceso',
    'procesando',
    'validado',
    'indexando',
    'completado',
    'observado',
    'fallido',
    'cancelado'
  )),
  storage_original_path text not null default '',
  storage_normalizado_path text not null default '',
  archivo_nombre text not null default '',
  tamano_bytes bigint not null default 0,
  sha256_original text not null default '',
  sha256_normalizado text not null default '',
  registros_raw integer not null default 0,
  registros_validos integer not null default 0,
  registros_insertados integer not null default 0,
  errores jsonb not null default '[]'::jsonb,
  advertencias jsonb not null default '[]'::jsonb,
  calidad jsonb not null default '{}'::jsonb,
  job_metadata jsonb not null default '{}'::jsonb,
  cloud_run_execution text not null default '',
  creado_en timestamptz not null default now(),
  actualizado_en timestamptz not null default now(),
  iniciado_en timestamptz,
  finalizado_en timestamptz
);

create index if not exists idx_padron_import_jobs_tenant_estado
on public.padron_import_jobs (tenant_id, estado, creado_en desc);

create index if not exists idx_padron_import_jobs_tenant_provincia_periodo
on public.padron_import_jobs (tenant_id, provincia, periodo, creado_en desc);

alter table public.padron_import_jobs enable row level security;

alter table public.padron_versiones
  add column if not exists import_job_id uuid references public.padron_import_jobs(id) on delete set null,
  add column if not exists sha256_normalizado text not null default '';

create index if not exists idx_padron_versiones_import_job
on public.padron_versiones (import_job_id);

