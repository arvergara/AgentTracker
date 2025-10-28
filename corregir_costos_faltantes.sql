-- =====================================================
-- CORRECCIÓN DE COSTOS FALTANTES
-- Fecha: 2025-10-28
-- Blanca Bulnes, Macarena Puigrredon y CORRECCIÓN Andrea Tapia
-- =====================================================

BEGIN;

-- Backup de costos actuales
CREATE TEMP TABLE backup_costos_correccion AS
SELECT id, nombre, costo_mensual_empresa FROM personas WHERE id IN (1, 2, 11);

UPDATE personas SET costo_mensual_empresa = 7263919 WHERE id = 1; -- Blanca Bulnes
UPDATE personas SET costo_mensual_empresa = 7263919 WHERE id = 2; -- María Macarena Puigrredon
UPDATE personas SET costo_mensual_empresa = 2522405 WHERE id = 11; -- Andrea Tapia

-- Verificar cambios
SELECT 
    p.nombre,
    b.costo_mensual_empresa as costo_anterior,
    p.costo_mensual_empresa as costo_nuevo,
    (p.costo_mensual_empresa - b.costo_mensual_empresa) as diferencia,
    ROUND(((p.costo_mensual_empresa - b.costo_mensual_empresa) / NULLIF(b.costo_mensual_empresa, 0)::NUMERIC * 100)::NUMERIC, 1) as cambio_pct
FROM personas p
JOIN backup_costos_correccion b ON p.id = b.id
WHERE p.id IN (1, 2, 11)
ORDER BY p.id;

-- Total actualizado
SELECT 
    COUNT(*) as personas_totales,
    SUM(costo_mensual_empresa) as total_pesos,
    ROUND((SUM(costo_mensual_empresa) / 38000.0)::NUMERIC, 2) as total_uf
FROM personas
WHERE activo = true;

COMMIT;

SELECT '✅ CORRECCIÓN COMPLETADA' as resultado;
