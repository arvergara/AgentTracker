-- =====================================================
-- ACTUALIZACIÓN DE COSTOS MENSUALES DESDE FLUJO DE CAJA
-- Fecha: 2025-10-28
-- Fuente: Planilla Flujo de Caja Comsulting 2025.xlsx
-- =====================================================

BEGIN;

-- Backup de costos actuales
CREATE TEMP TABLE backup_costos AS
SELECT id, nombre, costo_mensual_empresa FROM personas;

-- Actualizar costos según flujo de caja
UPDATE personas SET costo_mensual_empresa = 5648262 WHERE id = 4; -- Carolina Romero
UPDATE personas SET costo_mensual_empresa = 5592849 WHERE id = 5; -- Nicolás Marticorena
UPDATE personas SET costo_mensual_empresa = 5033406 WHERE id = 3; -- María Bernardita Ochagavia
UPDATE personas SET costo_mensual_empresa = 5684984 WHERE id = 6; -- Isabel Espinoza
UPDATE personas SET costo_mensual_empresa = 5676813 WHERE id = 7; -- Erick Rojas
UPDATE personas SET costo_mensual_empresa = 1750613 WHERE id = 8; -- Raúl Andrés Azócar
UPDATE personas SET costo_mensual_empresa = 4122199 WHERE id = 9; -- María De Los Ángeles Pérez
UPDATE personas SET costo_mensual_empresa = 3878947 WHERE id = 13; -- Enrique Elgueta
UPDATE personas SET costo_mensual_empresa = 3818961 WHERE id = 10; -- Constanza Pérez-Cueto
UPDATE personas SET costo_mensual_empresa = 1008962 WHERE id = 11; -- Andrea Tapia
UPDATE personas SET costo_mensual_empresa = 3640010 WHERE id = 12; -- Juana Nidia Millahueique
UPDATE personas SET costo_mensual_empresa = 2094388 WHERE id = 23; -- Aranza Fernández
UPDATE personas SET costo_mensual_empresa = 3068146 WHERE id = 16; -- Josefa Arraztoa
UPDATE personas SET costo_mensual_empresa = 2308429 WHERE id = 36; -- Francisca Carlino
UPDATE personas SET costo_mensual_empresa = 2811078 WHERE id = 17; -- Carolina Rodríguez
UPDATE personas SET costo_mensual_empresa = 2700240 WHERE id = 21; -- Victor Guillou
UPDATE personas SET costo_mensual_empresa = 2757070 WHERE id = 19; -- Pilar Gordillo
UPDATE personas SET costo_mensual_empresa = 2599634 WHERE id = 20; -- Liliana Cortes
UPDATE personas SET costo_mensual_empresa = 2634225 WHERE id = 22; -- José Manuel Valdivieso
UPDATE personas SET costo_mensual_empresa = 2894967 WHERE id = 18; -- Carla Borja
UPDATE personas SET costo_mensual_empresa = 2453989 WHERE id = 24; -- Isidora Bello
UPDATE personas SET costo_mensual_empresa = 2293982 WHERE id = 14; -- Jazmín Sapunar
UPDATE personas SET costo_mensual_empresa = 1983458 WHERE id = 25; -- Mariela Moyano
UPDATE personas SET costo_mensual_empresa = 1740002 WHERE id = 29; -- Kaenia Berenguel
UPDATE personas SET costo_mensual_empresa = 1774674 WHERE id = 26; -- Leonardo Pezoa
UPDATE personas SET costo_mensual_empresa = 1110224 WHERE id = 37; -- Hernán Díaz
UPDATE personas SET costo_mensual_empresa = 1573417 WHERE id = 28; -- Luis Ignacio Echeverría
UPDATE personas SET costo_mensual_empresa = 1318830 WHERE id = 27; -- Janett Poblete
UPDATE personas SET costo_mensual_empresa = 1338228 WHERE id = 30; -- Pedro Pablo Thies
UPDATE personas SET costo_mensual_empresa = 1245854 WHERE id = 32; -- Ignacio Diaz
UPDATE personas SET costo_mensual_empresa = 1200000 WHERE id = 33; -- Rocío Romero
UPDATE personas SET costo_mensual_empresa = 1112443 WHERE id = 31; -- Anais Sarmiento
UPDATE personas SET costo_mensual_empresa = 659095 WHERE id = 34; -- Sofía Martínez
UPDATE personas SET costo_mensual_empresa = 460724 WHERE id = 35; -- Christian Orrego

-- NOTA: Luisa Mendoza (id=15) no se actualizó (necesita verificación manual)
-- En Excel aparece como: 'Nicolás Campos/ Catalina Durán / Luisa Mendoza'
-- Costo compartido promedio mensual: $1,711,329 (~45 UF)
-- Valor actual en BD: $1,425,437 (~37.5 UF)

-- También faltan: Blanca Bulnes (id=1), María Macarena Puigrredon (id=2)
-- No aparecen en la sección de sueldos del flujo de caja (probablemente están en otra parte)

-- Verificar totales después de actualización
SELECT '=== VERIFICACIÓN POST-ACTUALIZACIÓN ===' as info;

SELECT
    COUNT(*) as personas_actualizadas,
    SUM(costo_mensual_empresa) as total_costo_mensual_pesos,
    ROUND((SUM(costo_mensual_empresa) / 38000.0)::NUMERIC, 1) as total_costo_mensual_uf
FROM personas
WHERE activo = true;

-- Comparar con backup
SELECT '=== COMPARACIÓN CON COSTOS ANTERIORES ===' as info;

SELECT
    p.nombre,
    b.costo_mensual_empresa as costo_anterior,
    p.costo_mensual_empresa as costo_nuevo,
    (p.costo_mensual_empresa - b.costo_mensual_empresa) as diferencia,
    ROUND(((p.costo_mensual_empresa - b.costo_mensual_empresa) / NULLIF(b.costo_mensual_empresa, 0) * 100)::NUMERIC, 1) as cambio_pct
FROM personas p
JOIN backup_costos b ON p.id = b.id
WHERE p.costo_mensual_empresa != b.costo_mensual_empresa
ORDER BY ABS(p.costo_mensual_empresa - b.costo_mensual_empresa) DESC
LIMIT 15;

COMMIT;

SELECT '✅ ACTUALIZACIÓN COMPLETADA' as resultado;
