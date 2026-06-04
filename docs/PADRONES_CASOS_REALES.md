# Casos reales para probar padrones

Objetivo: demostrar que el validador funciona con padrones heterogéneos de ARCA/provincias/regímenes, usando CUITs que efectivamente aparecen en los archivos cargados.

## Metodología

1. Cargar padrones reales en la carpeta operativa o en Supabase Storage.
2. Normalizarlos al formato canónico.
3. Generar un golden set desde los propios padrones:

```bash
.venv/bin/python3.13 scripts/generar_casos_padrones.py --por-padron 10 --out salidas/casos_padrones_reales.json
```

4. Revisar:
   - 8 a 10 CUITs por padrón.
   - CUITs con aparición en 2+ jurisdicciones.
   - empresas grandes que sirvan para demo nacional.
5. Ejecutar validaciones y guardar legajo/Excel como evidencia.

## Reglas

- No commitear padrones reales ni salidas con CUITs si el cliente lo restringe.
- Mantener casos por jurisdicción y casos cruzados.
- Cada caso debe indicar padrón, período, vigencia y resultado esperado.
- Si un padrón cambia mensualmente, regenerar el golden set y comparar diferencias.

## Casos esperados

| Tipo | Cantidad mínima | Uso |
|---|---:|---|
| CUIT presente por padrón | 8-10 | Validar parser/lookup específico |
| CUIT presente en varias jurisdicciones | 5-10 | Demo empresa nacional |
| CUIT ausente conocido | 3-5 | Validar no inscripción |
| Layout observado | 1-2 por formato | Validar advertencias |
| Archivo inválido | 1-2 | Validar bloqueo |

