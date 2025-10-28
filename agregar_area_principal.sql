-- Script para agregar área principal a personas
-- Ejecutar en PostgreSQL de Render

BEGIN;

-- 1. Agregar columna area_principal a tabla personas
ALTER TABLE personas ADD COLUMN IF NOT EXISTS area_principal_id INTEGER;
ALTER TABLE personas ADD CONSTRAINT fk_personas_area_principal
    FOREIGN KEY (area_principal_id) REFERENCES areas(id);

-- 2. Obtener IDs de áreas
DO $$
DECLARE
    area_externas_id INTEGER;
    area_aapp_id INTEGER;
    area_internas_id INTEGER;
    area_diseno_id INTEGER;
    area_redes_id INTEGER;
BEGIN
    SELECT id INTO area_externas_id FROM areas WHERE nombre = 'Externas';
    SELECT id INTO area_aapp_id FROM areas WHERE nombre = 'Asuntos Públicos';
    SELECT id INTO area_internas_id FROM areas WHERE nombre = 'Internas';
    SELECT id INTO area_diseno_id FROM areas WHERE nombre = 'Diseño';
    SELECT id INTO area_redes_id FROM areas WHERE nombre = 'Redes Sociales';

    RAISE NOTICE 'IDs de áreas: Externas=%, AAPP=%, Internas=%, Diseño=%, Redes=%',
        area_externas_id, area_aapp_id, area_internas_id, area_diseno_id, area_redes_id;

    -- 3. EXTERNAS (área principal)
    -- Bernardita, Nicolás, Carolina Romero, Carolina Rodríguez, Isidora, Janett, Rocío,
    -- Carla, Nidia, Constanza, Víctor, Enrique, José Manuel, Ignacio E., Anaís

    UPDATE personas SET area_principal_id = area_externas_id
    WHERE nombre IN (
        'Bernardita Ochagavía',
        'Nicolás Marticorena',
        'Carolina Romero',
        'Carolina Rodríguez',
        'Isidora Bello',
        'Janett Poblete',
        'Rocío Romero',
        'Carla Borja',
        'Juana Nidia Millahueique',
        'Constanza Pérez-Cueto',
        'Víctor Guillou',
        'Enrique Elgueta',
        'José Manuel Valdivieso',
        'Ignacio Echeverria',
        'Anais Sarmiento'
    );

    -- Aranza Fernández: Externas (aunque también está en Redes)
    UPDATE personas SET area_principal_id = area_externas_id
    WHERE nombre = 'Aranza Fernández';

    -- Andrea Tapia: Externas (aunque también está en AAPP)
    UPDATE personas SET area_principal_id = area_externas_id
    WHERE nombre = 'Andrea Tapia';

    -- Ángeles Pérez: Externas (aunque también está en Redes)
    UPDATE personas SET area_principal_id = area_externas_id
    WHERE nombre LIKE '%Ángeles Pérez%' OR nombre LIKE '%Angeles Perez%';

    -- 4. ASUNTOS PÚBLICOS (área principal)
    -- Erick Rojas (aunque también está en Externas)
    -- Josefa Arraztoa (aunque también está en Externas)
    -- Sofía Martínez

    UPDATE personas SET area_principal_id = area_aapp_id
    WHERE nombre IN (
        'Erick Rojas',
        'Josefa Arraztoa',
        'Sofía Martínez',
        'Sofia Martinez'
    );

    -- 5. INTERNAS (área principal)
    -- Liliana Cortés (aunque también está en Externas)
    -- Pilar Gordillo

    UPDATE personas SET area_principal_id = area_internas_id
    WHERE nombre IN (
        'Liliana Cortés',
        'Liliana Cortes',
        'Pilar Gordillo'
    );

    -- 6. REDES SOCIALES (área principal)
    -- Luisa, Pedro Pablo, Ignacio Díaz, Francisca, Leonardo

    UPDATE personas SET area_principal_id = area_redes_id
    WHERE nombre IN (
        'Luisa Mendoza',
        'Pedro Pablo Thies',
        'Ignacio Diaz',
        'Francisca Carlino',
        'Leonardo Pezoa'
    );

    -- 7. DISEÑO (área principal)
    -- Mariela, Kaenia, Christian, Hernán

    UPDATE personas SET area_principal_id = area_diseno_id
    WHERE nombre IN (
        'Mariela Moyano',
        'Kaenia Berenguel',
        'Christian Orrego',
        'Hernán Díaz',
        'Hernan Diaz'
    );

    -- 8. Isabel Espinoza: Tiene Redes Sociales Y Diseño
    -- Por horas trabajadas (878h Redes vs 532h Externas), su área principal es Redes Sociales
    UPDATE personas SET area_principal_id = area_redes_id
    WHERE nombre = 'Isabel Espinoza';

    -- 9. Personas administrativas sin área
    UPDATE personas SET area_principal_id = NULL
    WHERE nombre IN (
        'Blanca Bulnes',
        'Macarena Puigrredón',
        'Jazmín Sapunar',
        'Carlos Valera'
    );

END $$;

-- 10. Verificar asignaciones
SELECT '=== DISTRIBUCIÓN POR ÁREA PRINCIPAL ===' as info;

SELECT
    a.nombre as area,
    COUNT(p.id) as personas,
    STRING_AGG(p.nombre, ', ' ORDER BY p.nombre) as equipo
FROM areas a
LEFT JOIN personas p ON p.area_principal_id = a.id AND p.activo = true
WHERE a.activo = true
GROUP BY a.id, a.nombre
ORDER BY
    CASE a.nombre
        WHEN 'Externas' THEN 1
        WHEN 'Asuntos Públicos' THEN 2
        WHEN 'Internas' THEN 3
        WHEN 'Diseño' THEN 4
        WHEN 'Redes Sociales' THEN 5
    END;

SELECT '=== PERSONAS SIN ÁREA (ADMINISTRATIVAS) ===' as info;

SELECT nombre, cargo
FROM personas
WHERE area_principal_id IS NULL
  AND activo = true
ORDER BY nombre;

SELECT '=== RESUMEN POR ÁREA ===' as info;

SELECT
    a.nombre,
    COUNT(DISTINCT p.id) as personas_asignadas
FROM areas a
LEFT JOIN personas p ON p.area_principal_id = a.id AND p.activo = true
WHERE a.activo = true
GROUP BY a.nombre
ORDER BY a.nombre;

COMMIT;

SELECT '✅ ÁREA PRINCIPAL ASIGNADA A TODAS LAS PERSONAS' as resultado;
