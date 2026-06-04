# Cloud Run Jobs para padrones reales

Objetivo: procesar padrones grandes fuera del request web. La app crea una carga en Supabase; el job descarga el original desde Storage, normaliza, sube CSV canónico y registra versión.

## Prerrequisitos

1. Aplicar migraciones Supabase:
   - `supabase/migrations/001_mvp_ccu_schema.sql`
   - `supabase/migrations/002_padron_import_jobs.sql`
2. Bucket privado `menter-fiscal`.
3. Secrets disponibles para Cloud Run Job:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_STORAGE_BUCKET=menter-fiscal`
   - `SUPABASE_TENANT_SLUG=ccu`

## Variables del job

| Variable | Uso |
|---|---|
| `PADRON_IMPORT_JOB_ID` | ID de `padron_import_jobs` a procesar |
| `PADRON_IMPORT_BATCH_SIZE` | tamaño de lote para indexación opcional |
| `PADRON_JOB_INDEX_ROWS` | `false` por defecto; `true` inserta filas en `padron_registros_demo` |

## Deploy inicial

```bash
gcloud run jobs deploy menter-padron-import \
  --source . \
  --region us-central1 \
  --memory 8Gi \
  --cpu 4 \
  --task-timeout 3600 \
  --set-env-vars SUPABASE_URL="$SUPABASE_URL",SUPABASE_STORAGE_BUCKET=menter-fiscal,SUPABASE_TENANT_SLUG=ccu,PADRON_JOB_INDEX_ROWS=false \
  --set-secrets SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest \
  --command python \
  --args scripts/process_padron_job.py
```

## Ejecución manual

```bash
gcloud run jobs execute menter-padron-import \
  --region us-central1 \
  --update-env-vars PADRON_IMPORT_JOB_ID="JOB_ID"
```

## Flujo operativo

1. `/padrones` → preparar carga asistida.
2. Subir archivo a Supabase Storage.
3. Confirmar upload.
4. Marcar `pendiente_proceso`.
5. Ejecutar Cloud Run Job con `PADRON_IMPORT_JOB_ID`.
6. Revisar estado:
   - `completado`: normalizado correcto.
   - `observado`: normalizado con advertencias.
   - `fallido`: revisar `errores`.

## Nota de activación

Este sprint registra versiones como `pendiente_validacion`. La activación e indexación productiva completa se implementa después para evitar que un padrón observado afecte consultas reales automáticamente.

