-- Script SQL para consolidar clientes duplicados
-- Ejecutar en PostgreSQL de Render

BEGIN;

-- 1. FALABELLA: Consolidar todas las variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    -- Obtener ID del cliente correcto
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'Falabella' LIMIT 1;

    -- Si no existe, crear
    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) LIKE '%FALABELLA%' AND activo = true LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'Falabella' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    -- Consolidar variantes
    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) IN ('FALABELLA S.A.', 'FALABELLA SA', 'FALABELLA S.A')
        AND id != cliente_correcto_id
    LOOP
        -- Mover registros de horas
        UPDATE registros_horas SET cliente_id = cliente_correcto_id
        WHERE cliente_id = cliente_incorrecto_id;

        -- Mover servicios
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id
        WHERE cliente_id = cliente_incorrecto_id;

        -- Marcar como inactivo
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;

        RAISE NOTICE 'Cliente % consolidado en Falabella', cliente_incorrecto_id;
    END LOOP;
END $$;

-- 2. COLLAHUASI: Consolidar variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'Collahuasi' LIMIT 1;

    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) = 'COLLAHUASI' LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'Collahuasi' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) = 'COLLAHUASI'
        AND id != cliente_correcto_id
    LOOP
        UPDATE registro_horas SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;
        RAISE NOTICE 'Cliente % consolidado en Collahuasi', cliente_incorrecto_id;
    END LOOP;
END $$;

-- 3. EMPRESAS COPEC: Consolidar variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'EMPRESAS COPEC' LIMIT 1;

    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) LIKE '%COPEC%' LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'EMPRESAS COPEC' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) IN ('EMPRESAS COPEC S.A.', 'COPEC', 'COPEC S.A.', 'EMPRESAS COPEC SA')
        AND id != cliente_correcto_id
    LOOP
        UPDATE registro_horas SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;
        RAISE NOTICE 'Cliente % consolidado en EMPRESAS COPEC', cliente_incorrecto_id;
    END LOOP;
END $$;

-- 4. CAPSTONE: Consolidar variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'Capstone Copper' LIMIT 1;

    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) LIKE '%CAPSTONE%' LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'Capstone Copper' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) IN ('CAPSTONE', 'CAPSTONE MINNING CORP', 'CAPSTONE MINING CORP')
        AND id != cliente_correcto_id
    LOOP
        UPDATE registro_horas SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;
        RAISE NOTICE 'Cliente % consolidado en Capstone Copper', cliente_incorrecto_id;
    END LOOP;
END $$;

-- 5. AFP MODELO: Consolidar variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'AFP Modelo' LIMIT 1;

    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) LIKE '%AFP%MODELO%' LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'AFP Modelo' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) = 'AFP MODELO'
        AND id != cliente_correcto_id
    LOOP
        UPDATE registro_horas SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;
        RAISE NOTICE 'Cliente % consolidado en AFP Modelo', cliente_incorrecto_id;
    END LOOP;
END $$;

-- 6. MAE: Consolidar variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'MAE' LIMIT 1;

    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) LIKE '%MAE%' LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'MAE' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) IN ('MAE HOLDING CHILE SPA', 'MAE HOLDING', 'MAE HOLDING CHILE')
        AND id != cliente_correcto_id
    LOOP
        UPDATE registro_horas SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;
        RAISE NOTICE 'Cliente % consolidado en MAE', cliente_incorrecto_id;
    END LOOP;
END $$;

-- 7. OXZO: Consolidar variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'OXZO' LIMIT 1;

    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) LIKE '%OXZO%' LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'OXZO' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) IN ('OXZO S.A', 'OXZO S.A.', 'OXZO SA')
        AND id != cliente_correcto_id
    LOOP
        UPDATE registro_horas SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id WHERE cliente_incorrecto_id;
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;
        RAISE NOTICE 'Cliente % consolidado en OXZO', cliente_incorrecto_id;
    END LOOP;
END $$;

-- 8. EMBAJADA ITALIA: Consolidar variantes
DO $$
DECLARE
    cliente_correcto_id INTEGER;
    cliente_incorrecto_id INTEGER;
BEGIN
    SELECT id INTO cliente_correcto_id FROM clientes WHERE nombre = 'Embajada de Italia' LIMIT 1;

    IF cliente_correcto_id IS NULL THEN
        SELECT id INTO cliente_correcto_id FROM clientes WHERE UPPER(nombre) LIKE '%EMBAJADA%ITALIA%' LIMIT 1;
        IF cliente_correcto_id IS NOT NULL THEN
            UPDATE clientes SET nombre = 'Embajada de Italia' WHERE id = cliente_correcto_id;
        END IF;
    END IF;

    FOR cliente_incorrecto_id IN
        SELECT id FROM clientes
        WHERE UPPER(nombre) IN ('EMBAJADA ITALIA', 'EMBAJADA DE ITALIA')
        AND id != cliente_correcto_id
    LOOP
        UPDATE registro_horas SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE servicios_cliente SET cliente_id = cliente_correcto_id WHERE cliente_id = cliente_incorrecto_id;
        UPDATE clientes SET activo = false WHERE id = cliente_incorrecto_id;
        RAISE NOTICE 'Cliente % consolidado en Embajada de Italia', cliente_incorrecto_id;
    END LOOP;
END $$;

-- Verificar resultados
SELECT
    'Clientes activos consolidados' as descripcion,
    COUNT(*) as total
FROM clientes
WHERE activo = true;

SELECT
    'Clientes inactivos (duplicados)' as descripcion,
    COUNT(*) as total
FROM clientes
WHERE activo = false;

-- Mostrar clientes consolidados con sus horas
SELECT
    c.nombre,
    COUNT(DISTINCT rh.id) as registros_horas,
    COALESCE(SUM(rh.horas), 0) as total_horas
FROM clientes c
LEFT JOIN registros_horas rh ON c.id = rh.cliente_id
WHERE c.activo = true
  AND c.nombre IN ('Falabella', 'Collahuasi', 'EMPRESAS COPEC', 'Capstone Copper', 'AFP Modelo', 'MAE', 'OXZO', 'Embajada de Italia')
GROUP BY c.nombre
ORDER BY c.nombre;

COMMIT;
