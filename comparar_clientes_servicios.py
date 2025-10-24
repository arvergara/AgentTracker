#!/usr/bin/env python3
"""
Comparar clientes y servicios en BD vs. lo esperado según CSV
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
        return None

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.execute(text('SELECT 1'))
        print("✓ Conectado a base de datos de producción")
        return session
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None


def comparar_clientes(session):
    """Compara clientes en BD vs esperados"""

    print("\n" + "=" * 80)
    print("COMPARACIÓN: CLIENTES EN BD VS. ESPERADOS")
    print("=" * 80)
    print()

    # Clientes esperados (permanentes según CSV proporcionado)
    clientes_esperados = {
        'AFP MODELO': {'servicios': 1, 'ingreso_mensual': 225},
        'EBM': {'servicios': 6, 'ingreso_mensual': 1157},
        'COLLAHUASI': {'servicios': 6, 'ingreso_mensual': 803},
        'EMPRESAS COPEC': {'servicios': 1, 'ingreso_mensual': 250},
        'FALABELLA S.A.': {'servicios': 2, 'ingreso_mensual': 610},
        'FRUTAS DE CHILE': {'servicios': 2, 'ingreso_mensual': 476},
        'GUACOLDA': {'servicios': 4, 'ingreso_mensual': 292},
        'HITES': {'servicios': 1, 'ingreso_mensual': 150},
        'ISIDORO QUIROGA': {'servicios': 2, 'ingreso_mensual': 254},
        'LARRAÍN VIAL': {'servicios': 1, 'ingreso_mensual': 30},
        'LIBERTY SEGUROS': {'servicios': 1, 'ingreso_mensual': 30},
        'MAE HOLDING CHILE SPA': {'servicios': 4, 'ingreso_mensual': 170},
        'MANTOS COPPER SA': {'servicios': 6, 'ingreso_mensual': 316},
        'MANTO VERDE SA': {'servicios': 6, 'ingreso_mensual': 316},
        'CAPSTONE MINING CORP': {'servicios': 2, 'ingreso_mensual': 500},
        'NOVA AUSTRAL': {'servicios': 1, 'ingreso_mensual': 115},
        'OXZO S.A.': {'servicios': 2, 'ingreso_mensual': 160},  # Solo sept en adelante
        'SONNEDIX': {'servicios': 1, 'ingreso_mensual': 40},
    }

    total_esperado = sum(c['ingreso_mensual'] for c in clientes_esperados.values())

    print(f"Total de clientes permanentes esperados: {len(clientes_esperados)}")
    print(f"Total ingreso mensual esperado (sep): {total_esperado} UF")
    print()

    # Obtener clientes en BD
    result = session.execute(text("""
        SELECT
            c.nombre,
            c.tipo,
            COUNT(DISTINCT sc.id) as num_servicios,
            COALESCE(AVG(im.ingreso_uf), 0) as ingreso_promedio
        FROM clientes c
        LEFT JOIN servicios_cliente sc ON c.id = sc.cliente_id AND sc.activo = true
        LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025 AND im.mes = 9
        WHERE c.activo = true
        GROUP BY c.id, c.nombre, c.tipo
        ORDER BY c.nombre
    """))

    clientes_bd = {row[0]: {'tipo': row[1], 'servicios': row[2], 'ingreso': row[3]} for row in result}

    print("ANÁLISIS POR CLIENTE:")
    print("-" * 80)
    print(f"{'Cliente':35s} {'Estado':10s} {'Servicios':12s} {'Ingreso (sep)':15s}")
    print("-" * 80)

    clientes_faltantes = []
    clientes_con_problemas = []

    for nombre_esperado, datos_esperados in sorted(clientes_esperados.items()):
        # Buscar en BD (matching flexible)
        encontrado = None
        for nombre_bd in clientes_bd.keys():
            if nombre_esperado.upper()[:10] in nombre_bd.upper() or nombre_bd.upper()[:10] in nombre_esperado.upper():
                encontrado = nombre_bd
                break

        if encontrado:
            datos_bd = clientes_bd[encontrado]

            # Verificar discrepancias
            problemas = []
            if datos_bd['tipo'] != 'permanente':
                problemas.append(f"tipo={datos_bd['tipo']}")
            if datos_bd['servicios'] != datos_esperados['servicios']:
                problemas.append(f"servicios={datos_bd['servicios']}/{datos_esperados['servicios']}")

            ingreso_bd_total = datos_bd['ingreso'] * datos_bd['servicios'] if datos_bd['ingreso'] > 0 else 0
            if abs(ingreso_bd_total - datos_esperados['ingreso_mensual']) > 10:
                problemas.append(f"ingreso={ingreso_bd_total:.0f}/{datos_esperados['ingreso_mensual']}")

            if problemas:
                estado = "⚠️ PROBLEMA"
                detalles = ", ".join(problemas)
                clientes_con_problemas.append((nombre_esperado, detalles))
            else:
                estado = "✓ OK"
                detalles = ""

            print(f"{nombre_esperado[:34]:35s} {estado:10s} {datos_bd['servicios']:3d} / {datos_esperados['servicios']:3d}   {ingreso_bd_total:6.0f} / {datos_esperados['ingreso_mensual']:6.0f}  {detalles}")
        else:
            estado = "❌ FALTA"
            clientes_faltantes.append(nombre_esperado)
            print(f"{nombre_esperado[:34]:35s} {estado:10s} {'0':3s} / {datos_esperados['servicios']:3d}   {'0':6s} / {datos_esperados['ingreso_mensual']:6.0f}")

    print()

    if clientes_faltantes:
        print(f"\n❌ CLIENTES FALTANTES ({len(clientes_faltantes)}):")
        for cliente in clientes_faltantes:
            print(f"   - {cliente}")
        print()

    if clientes_con_problemas:
        print(f"\n⚠️  CLIENTES CON PROBLEMAS ({len(clientes_con_problemas)}):")
        for cliente, problema in clientes_con_problemas:
            print(f"   - {cliente}: {problema}")
        print()

    # Clientes en BD que no están en la lista esperada
    print("\nCLIENTES EN BD NO ESPERADOS (posible consolidación):")
    print("-" * 80)

    for nombre_bd, datos in sorted(clientes_bd.items()):
        # Verificar si está en esperados
        encontrado = False
        for nombre_esperado in clientes_esperados.keys():
            if nombre_esperado.upper()[:10] in nombre_bd.upper() or nombre_bd.upper()[:10] in nombre_esperado.upper():
                encontrado = True
                break

        if not encontrado:
            print(f"   {nombre_bd:40s} (tipo={datos['tipo']}, servicios={datos['servicios']})")

    print()


def main():
    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  COMPARACIÓN CLIENTES/SERVICIOS: BD VS. ESPERADO".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session = conectar_produccion()

    if not session:
        sys.exit(1)

    comparar_clientes(session)
    session.close()


if __name__ == '__main__':
    main()
