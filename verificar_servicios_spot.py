#!/usr/bin/env python3
"""
Verificar y corregir servicios SPOT mal marcados en la base de datos
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def cargar_env_produccion():
    """Carga DATABASE_URL desde .env.production si existe"""
    env_file = '.env.production'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'DATABASE_URL':
                        os.environ['DATABASE_URL'] = value
                        return True
    return False


def conectar_produccion():
    """Conecta a la base de datos de producción"""
    cargar_env_produccion()
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ No se encontró DATABASE_URL")
        return None, None

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.execute(text('SELECT 1'))
        print("✓ Conectado a base de datos de producción")
        return session, engine
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None, None


def verificar_servicios_spot(session):
    """Verifica qué servicios tienen es_spot=True"""

    print("\n" + "=" * 80)
    print("SERVICIOS MARCADOS COMO SPOT (es_spot=True)")
    print("=" * 80)
    print()

    result = session.execute(text("""
        SELECT
            c.nombre as cliente,
            sc.nombre as servicio,
            sc.es_spot,
            sc.activo,
            COUNT(im.id) as num_ingresos,
            COALESCE(SUM(im.ingreso_uf), 0) as total_ingresos
        FROM servicios_cliente sc
        JOIN clientes c ON sc.cliente_id = c.id
        LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
        WHERE sc.es_spot = true
        GROUP BY c.nombre, sc.nombre, sc.es_spot, sc.activo
        ORDER BY c.nombre, sc.nombre
    """))

    servicios_spot = list(result)

    if servicios_spot:
        print(f"Encontrados {len(servicios_spot)} servicios marcados como SPOT:\n")
        print(f"{'Cliente':30s} {'Servicio':50s} {'Activo':7s} {'Ingresos':10s}")
        print("-" * 100)

        total = 0
        for cliente, servicio, es_spot, activo, num_ing, total_ing in servicios_spot:
            activo_str = "Sí" if activo else "No"
            print(f"{cliente[:29]:30s} {servicio[:49]:50s} {activo_str:7s} {total_ing:10.2f} UF")
            if activo:
                total += total_ing

        print("-" * 100)
        print(f"{'TOTAL SPOT (activos)':80s} {total:10.2f} UF")
    else:
        print("⚠️  NO hay servicios marcados como es_spot=True")

    print("\n")
    print("=" * 80)
    print("SERVICIOS QUE DEBERÍAN SER SPOT (según CSV)")
    print("=" * 80)
    print()

    # Servicios que deberían ser SPOT según el CSV proporcionado
    servicios_spot_esperados = [
        ('Capital Advisores', 'Sept-oct-nov por UF 250 promedio mensual', 250),
        ('Capstone', 'Diseño por 1 vez UF 70 promedio mensual', 70),
        ('Capstone', 'Embajadores por 1 vez UF 65 promedio mensual', 65),
        ('Capstone', 'Un taller de vocería UF 200 promedio mensual', 200),
        ('Concha y Toro', 'Un Taller de vocería UF 60 promedio mensual', 60),
        ('Embajada de Italia', 'Asesoría comunicacional x 4 meses promedio mensual UF 22,2', 89),
        ('FALABELLA S.A.', 'Taller de vocería Una vez UF 200, promedio mensual UF 16,7', 200),
        ('FRUTAS DE CHILE', 'Taller de vocería una vez UF 200, promedio mensual UF 16,7', 200),
        ('OXZO S.A', 'Diagnóstico una vez UF 210 promedio mensual', 210),
    ]

    print(f"{'Cliente':30s} {'Servicio (esperado)':60s} {'Total UF':10s} {'¿Existe?':10s}")
    print("-" * 115)

    for cliente, servicio, total_uf in servicios_spot_esperados:
        # Buscar en BD (matching parcial)
        result = session.execute(text("""
            SELECT
                sc.id,
                sc.nombre,
                sc.es_spot,
                sc.activo,
                COALESCE(SUM(im.ingreso_uf), 0) as total_ingresos
            FROM servicios_cliente sc
            JOIN clientes c ON sc.cliente_id = c.id
            LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
            WHERE UPPER(c.nombre) LIKE :cliente_pattern
            GROUP BY sc.id, sc.nombre, sc.es_spot, sc.activo
        """), {'cliente_pattern': f'%{cliente.upper()[:15]}%'})

        servicios_cliente = list(result)

        if servicios_cliente:
            # Buscar coincidencia por nombre de servicio
            encontrado = False
            for sc_id, sc_nombre, es_spot, activo, total_ing in servicios_cliente:
                # Match parcial por palabras clave
                palabras_clave = ['taller', 'vocería', 'diseño', 'embajador', 'diagnóstico', 'asesoría']
                servicio_lower = servicio.lower()
                sc_nombre_lower = sc_nombre.lower()

                # Si el servicio esperado contiene alguna palabra clave y el servicio en BD también
                match = False
                for palabra in palabras_clave:
                    if palabra in servicio_lower and palabra in sc_nombre_lower:
                        match = True
                        break

                if match or abs(total_ing - total_uf) < 10:  # Match por monto similar
                    encontrado = True
                    marca = "✓" if es_spot else "❌"
                    estado = f"{marca} es_spot={es_spot}, activo={activo}"
                    print(f"{cliente[:29]:30s} {servicio[:59]:60s} {total_uf:10.0f} {estado:20s}")
                    break

            if not encontrado:
                print(f"{cliente[:29]:30s} {servicio[:59]:60s} {total_uf:10.0f} ❌ NO ENCONTRADO")
        else:
            print(f"{cliente[:29]:30s} {servicio[:59]:60s} {total_uf:10.0f} ❌ Cliente no existe")

    print()


def sugerir_correcciones(session):
    """Sugiere qué servicios corregir"""

    print("\n" + "=" * 80)
    print("SERVICIOS QUE NECESITAN CORRECCIÓN")
    print("=" * 80)
    print()

    # Servicios que contienen palabras clave de SPOT pero no están marcados
    palabras_spot = ['taller', 'una vez', 'spot', 'diagnóstico', 'puntual', 'proyecto']

    result = session.execute(text("""
        SELECT
            sc.id,
            c.nombre as cliente,
            sc.nombre as servicio,
            sc.es_spot,
            sc.activo,
            COUNT(im.id) as num_ingresos,
            COALESCE(SUM(im.ingreso_uf), 0) as total_ingresos
        FROM servicios_cliente sc
        JOIN clientes c ON sc.cliente_id = c.id
        LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
        WHERE sc.activo = true
        GROUP BY sc.id, c.nombre, sc.nombre, sc.es_spot, sc.activo
        ORDER BY c.nombre, sc.nombre
    """))

    servicios = list(result)

    servicios_a_corregir = []

    for sc_id, cliente, servicio, es_spot, activo, num_ing, total_ing in servicios:
        servicio_lower = servicio.lower()

        # Detectar si debería ser SPOT
        es_probable_spot = any(palabra in servicio_lower for palabra in palabras_spot)

        # Solo tiene ingresos en pocos meses (< 6)
        es_temporal = num_ing < 6 if num_ing > 0 else False

        if (es_probable_spot or es_temporal) and not es_spot:
            servicios_a_corregir.append({
                'id': sc_id,
                'cliente': cliente,
                'servicio': servicio,
                'es_spot_actual': es_spot,
                'num_ingresos': num_ing,
                'total': total_ing,
                'razon': 'Nombre sugiere SPOT' if es_probable_spot else 'Temporal (< 6 meses)'
            })

    if servicios_a_corregir:
        print(f"Encontrados {len(servicios_a_corregir)} servicios a corregir:\n")
        print(f"{'ID':5s} {'Cliente':25s} {'Servicio':45s} {'Total UF':10s} {'Razón':25s}")
        print("-" * 115)

        for s in servicios_a_corregir:
            print(f"{s['id']:5d} {s['cliente'][:24]:25s} {s['servicio'][:44]:45s} {s['total']:10.2f} {s['razon'][:24]:25s}")

        print()
        print("Para corregir estos servicios, ejecuta:")
        print("  python corregir_servicios_spot.py --ejecutar")
    else:
        print("✓ No se detectaron servicios que necesiten corrección automática")

    print()


def main():
    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  VERIFICACIÓN DE SERVICIOS SPOT".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session, engine = conectar_produccion()

    if not session:
        sys.exit(1)

    verificar_servicios_spot(session)
    sugerir_correcciones(session)

    session.close()


if __name__ == '__main__':
    main()
