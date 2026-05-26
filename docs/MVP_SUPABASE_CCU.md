# MVP Supabase CCU / Menter

Objetivo: demo barata y rápida, sin mover padrones reales a Git. FastAPI sigue siendo la app principal y Supabase se usa como Postgres + Storage.

## Estado MCP

Proyecto informado: `szpmuxncfdbzpfkngizk`.

El MCP actual no tiene permisos sobre ese proyecto (`You do not have permission to perform this action`). Para aplicar schema desde Codex, el usuario debe abrir acceso al proyecto/organización al conector Supabase o usar un proyecto listado por el MCP.

## Aplicar schema

Opción manual: abrir SQL Editor en Supabase y ejecutar:

`supabase/migrations/001_mvp_ccu_schema.sql`

Crea:

- `tenants`
- `empresas_cuit`
- `fuentes_fiscales`
- `padron_versiones`
- `padron_registros_demo`
- `validaciones`
- `accesos_fiscales`
- `cola_asistida`
- `audit_eventos`
- bucket privado `menter-fiscal`

Todas las tablas tienen RLS habilitado y no tienen políticas públicas. El MVP usa `service_role` sólo desde backend.

## Variables de entorno backend

Nunca publicar `SUPABASE_SERVICE_ROLE_KEY` en frontend.

```bash
SUPABASE_URL=https://szpmuxncfdbzpfkngizk.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_STORAGE_BUCKET=menter-fiscal
SUPABASE_TENANT_SLUG=ccu
```

## Flujo MVP recomendado

1. CCU/Menter carga padrón desde `/padrones`.
2. App guarda archivo y manifiesto local para demo.
3. Si Supabase está configurado, sube original a Storage.
4. Registra metadata en `padron_versiones`.
5. Validación proveedor usa parsers actuales y genera Excel/legajo.
6. Accesos fiscales se registran localmente y, si está configurado, se sincronizan a `accesos_fiscales`.

## Límites Free

Usar Free para construir y demo interna con muestras reducidas. Para demo externa CCU, pasar a Pro para evitar pausa/inestabilidad y ampliar storage.
