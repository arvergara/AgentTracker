-- Script SQL simplificado para migrar áreas
-- Ejecutar en PostgreSQL de Render

BEGIN;

-- 1. Crear las áreas nuevas solo si no existen
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM areas WHERE nombre = 'Comunicación Externa e Interna') THEN
        INSERT INTO areas (nombre, activo) VALUES ('Comunicación Externa e Interna', true);
        RAISE NOTICE 'Área "Comunicación Externa e Interna" creada';
    ELSE
        UPDATE areas SET activo = true WHERE nombre = 'Comunicación Externa e Interna';
        RAISE NOTICE 'Área "Comunicación Externa e Interna" ya existe, activada';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM areas WHERE nombre = 'Digital y Diseño') THEN
        INSERT INTO areas (nombre, activo) VALUES ('Digital y Diseño', true);
        RAISE NOTICE 'Área "Digital y Diseño" creada';
    ELSE
        UPDATE areas SET activo = true WHERE nombre = 'Digital y Diseño';
        RAISE NOTICE 'Área "Digital y Diseño" ya existe, activada';
    END IF;

    -- Asegurar que Asuntos Públicos está activa
    UPDATE areas SET activo = true WHERE nombre = 'Asuntos Públicos';
    RAISE NOTICE 'Área "Asuntos Públicos" activada';
END $$;

-- 2. Migrar servicios y registros de horas
DO $$
DECLARE
    area_comunicacion_id INTEGER;
    area_digital_id INTEGER;
    area_externas_id INTEGER;
    area_internas_id INTEGER;
    area_redes_id INTEGER;
    area_diseno_id INTEGER;
    area_comunicaciones_id INTEGER;
    servicios_migrados INTEGER := 0;
    horas_migradas INTEGER := 0;
BEGIN
    -- Obtener IDs
    SELECT id INTO area_comunicacion_id FROM areas WHERE nombre = 'Comunicación Externa e Interna';
    SELECT id INTO area_digital_id FROM areas WHERE nombre = 'Digital y Diseño';
    SELECT id INTO area_externas_id FROM areas WHERE nombre = 'Externas';
    SELECT id INTO area_internas_id FROM areas WHERE nombre = 'Internas';
    SELECT id INTO area_redes_id FROM areas WHERE nombre = 'Redes Sociales';
    SELECT id INTO area_diseno_id FROM areas WHERE nombre = 'Diseño';
    SELECT id INTO area_comunicaciones_id FROM areas WHERE nombre = 'Comunicaciones';

    RAISE NOTICE 'IDs obtenidos: Comunicación=%, Digital=%', area_comunicacion_id, area_digital_id;

    -- Migrar Externas → Comunicación Externa e Interna
    IF area_externas_id IS NOT NULL THEN
        UPDATE servicios SET area_id = area_comunicacion_id WHERE area_id = area_externas_id;
        GET DIAGNOSTICS servicios_migrados = ROW_COUNT;
        RAISE NOTICE 'Servicios migrados desde Externas: %', servicios_migrados;

        UPDATE registros_horas SET area_id = area_comunicacion_id WHERE area_id = area_externas_id;
        GET DIAGNOSTICS horas_migradas = ROW_COUNT;
        RAISE NOTICE 'Registros de horas migrados desde Externas: %', horas_migradas;

        UPDATE areas SET activo = false WHERE id = area_externas_id;
        RAISE NOTICE 'Área Externas desactivada';
    END IF;

    -- Migrar Internas → Comunicación Externa e Interna
    IF area_internas_id IS NOT NULL THEN
        UPDATE servicios SET area_id = area_comunicacion_id WHERE area_id = area_internas_id;
        GET DIAGNOSTICS servicios_migrados = ROW_COUNT;
        RAISE NOTICE 'Servicios migrados desde Internas: %', servicios_migrados;

        UPDATE registros_horas SET area_id = area_comunicacion_id WHERE area_id = area_internas_id;
        GET DIAGNOSTICS horas_migradas = ROW_COUNT;
        RAISE NOTICE 'Registros de horas migrados desde Internas: %', horas_migradas;

        UPDATE areas SET activo = false WHERE id = area_internas_id;
        RAISE NOTICE 'Área Internas desactivada';
    END IF;

    -- Migrar Comunicaciones → Comunicación Externa e Interna
    IF area_comunicaciones_id IS NOT NULL THEN
        UPDATE servicios SET area_id = area_comunicacion_id WHERE area_id = area_comunicaciones_id;
        GET DIAGNOSTICS servicios_migrados = ROW_COUNT;
        RAISE NOTICE 'Servicios migrados desde Comunicaciones: %', servicios_migrados;

        UPDATE registros_horas SET area_id = area_comunicacion_id WHERE area_id = area_comunicaciones_id;
        GET DIAGNOSTICS horas_migradas = ROW_COUNT;
        RAISE NOTICE 'Registros de horas migrados desde Comunicaciones: %', horas_migradas;

        UPDATE areas SET activo = false WHERE id = area_comunicaciones_id;
        RAISE NOTICE 'Área Comunicaciones desactivada';
    END IF;

    -- Migrar Redes Sociales → Digital y Diseño
    IF area_redes_id IS NOT NULL THEN
        UPDATE servicios SET area_id = area_digital_id WHERE area_id = area_redes_id;
        GET DIAGNOSTICS servicios_migrados = ROW_COUNT;
        RAISE NOTICE 'Servicios migrados desde Redes Sociales: %', servicios_migrados;

        UPDATE registros_horas SET area_id = area_digital_id WHERE area_id = area_redes_id;
        GET DIAGNOSTICS horas_migradas = ROW_COUNT;
        RAISE NOTICE 'Registros de horas migrados desde Redes Sociales: %', horas_migradas;

        UPDATE areas SET activo = false WHERE id = area_redes_id;
        RAISE NOTICE 'Área Redes Sociales desactivada';
    END IF;

    -- Migrar Diseño → Digital y Diseño
    IF area_diseno_id IS NOT NULL THEN
        UPDATE servicios SET area_id = area_digital_id WHERE area_id = area_diseno_id;
        GET DIAGNOSTICS servicios_migrados = ROW_COUNT;
        RAISE NOTICE 'Servicios migrados desde Diseño: %', servicios_migrados;

        UPDATE registros_horas SET area_id = area_digital_id WHERE area_id = area_diseno_id;
        GET DIAGNOSTICS horas_migradas = ROW_COUNT;
        RAISE NOTICE 'Registros de horas migrados desde Diseño: %', horas_migradas;

        UPDATE areas SET activo = false WHERE id = area_diseno_id;
        RAISE NOTICE 'Área Diseño desactivada';
    END IF;
END $$;

-- 3. Verificar resultados
SELECT
    '=== ÁREAS ACTIVAS ===' as info;

SELECT
    a.nombre,
    COUNT(DISTINCT s.id) as servicios,
    COUNT(DISTINCT rh.id) as registros_horas,
    COALESCE(SUM(rh.horas), 0)::NUMERIC(10,2) as total_horas
FROM areas a
LEFT JOIN servicios s ON a.id = s.area_id
LEFT JOIN registros_horas rh ON a.id = rh.area_id
WHERE a.activo = true
GROUP BY a.nombre
ORDER BY a.nombre;

SELECT
    '=== ÁREAS INACTIVAS (ANTIGUAS) ===' as info;

SELECT
    nombre
FROM areas
WHERE activo = false
ORDER BY nombre;

COMMIT;

SELECT '✅ MIGRACIÓN COMPLETADA EXITOSAMENTE' as resultado;
