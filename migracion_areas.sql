-- Script SQL para migrar áreas de 5 a 3
-- Ejecutar en PostgreSQL de Render

BEGIN;

-- 1. Crear las 3 áreas nuevas (si no existen)
INSERT INTO areas (nombre, activo)
VALUES
    ('Comunicación Externa e Interna', true),
    ('Digital y Diseño', true),
    ('Asuntos Públicos', true)
ON CONFLICT (nombre) DO UPDATE SET activo = true;

-- 2. Obtener IDs de las áreas nuevas
DO $$
DECLARE
    area_comunicacion_id INTEGER;
    area_digital_id INTEGER;
    area_asuntos_id INTEGER;
    area_antigua_id INTEGER;
BEGIN
    -- IDs de áreas nuevas
    SELECT id INTO area_comunicacion_id FROM areas WHERE nombre = 'Comunicación Externa e Interna';
    SELECT id INTO area_digital_id FROM areas WHERE nombre = 'Digital y Diseño';
    SELECT id INTO area_asuntos_id FROM areas WHERE nombre = 'Asuntos Públicos';

    RAISE NOTICE 'Área Comunicación: %', area_comunicacion_id;
    RAISE NOTICE 'Área Digital: %', area_digital_id;
    RAISE NOTICE 'Área Asuntos Públicos: %', area_asuntos_id;

    -- 3. Migrar servicios y registros de horas de "Externas" → "Comunicación Externa e Interna"
    FOR area_antigua_id IN
        SELECT id FROM areas WHERE nombre IN ('Externas', 'Comunicaciones Externas') AND activo = true
    LOOP
        UPDATE servicios SET area_id = area_comunicacion_id WHERE area_id = area_antigua_id;
        UPDATE registros_horas SET area_id = area_comunicacion_id WHERE area_id = area_antigua_id;
        UPDATE areas SET activo = false WHERE id = area_antigua_id;
        RAISE NOTICE 'Migrado desde Externas (ID: %)', area_antigua_id;
    END LOOP;

    -- 4. Migrar servicios y registros de "Internas" → "Comunicación Externa e Interna"
    FOR area_antigua_id IN
        SELECT id FROM areas WHERE nombre IN ('Internas', 'Comunicaciones Internas') AND activo = true
    LOOP
        UPDATE servicios SET area_id = area_comunicacion_id WHERE area_id = area_antigua_id;
        UPDATE registros_horas SET area_id = area_comunicacion_id WHERE area_id = area_antigua_id;
        UPDATE areas SET activo = false WHERE id = area_antigua_id;
        RAISE NOTICE 'Migrado desde Internas (ID: %)', area_antigua_id;
    END LOOP;

    -- 5. Migrar servicios y registros de "Redes Sociales" → "Digital y Diseño"
    FOR area_antigua_id IN
        SELECT id FROM areas WHERE nombre IN ('Redes sociales', 'Redes Sociales', 'RRSS') AND activo = true
    LOOP
        UPDATE servicios SET area_id = area_digital_id WHERE area_id = area_antigua_id;
        UPDATE registro_horas SET area_id = area_digital_id WHERE area_id = area_antigua_id;
        UPDATE areas SET activo = false WHERE id = area_antigua_id;
        RAISE NOTICE 'Migrado desde Redes Sociales (ID: %)', area_antigua_id;
    END LOOP;

    -- 6. Migrar servicios y registros de "Diseño" → "Digital y Diseño"
    FOR area_antigua_id IN
        SELECT id FROM areas WHERE nombre IN ('Diseño', 'Design', 'Gráfica') AND activo = true
    LOOP
        UPDATE servicios SET area_id = area_digital_id WHERE area_id = area_antigua_id;
        UPDATE registro_horas SET area_id = area_digital_id WHERE area_id = area_antigua_id;
        UPDATE areas SET activo = false WHERE id = area_antigua_id;
        RAISE NOTICE 'Migrado desde Diseño (ID: %)', area_antigua_id;
    END LOOP;

    -- 7. Migrar servicios y registros de "Digital" → "Digital y Diseño"
    FOR area_antigua_id IN
        SELECT id FROM areas WHERE nombre = 'Digital' AND activo = true
    LOOP
        UPDATE servicios SET area_id = area_digital_id WHERE area_id = area_antigua_id;
        UPDATE registro_horas SET area_id = area_digital_id WHERE area_id = area_antigua_id;
        UPDATE areas SET activo = false WHERE id = area_antigua_id;
        RAISE NOTICE 'Migrado desde Digital (ID: %)', area_antigua_id;
    END LOOP;

    -- 8. Asegurar que "Asuntos Públicos" está activa
    UPDATE areas SET activo = true WHERE nombre IN ('Asuntos Públicos', 'Asuntos públicos');

END $$;

-- 9. Verificar resultados
SELECT
    '=== ÁREAS ACTIVAS ===' as separador;

SELECT
    a.nombre,
    COUNT(DISTINCT s.id) as servicios,
    COUNT(DISTINCT rh.id) as registros_horas,
    COALESCE(SUM(rh.horas), 0) as total_horas
FROM areas a
LEFT JOIN servicios s ON a.id = s.area_id
LEFT JOIN registros_horas rh ON a.id = rh.area_id
WHERE a.activo = true
GROUP BY a.nombre
ORDER BY a.nombre;

SELECT
    '=== ÁREAS INACTIVAS (ANTIGUAS) ===' as separador;

SELECT
    nombre
FROM areas
WHERE activo = false
ORDER BY nombre;

COMMIT;
