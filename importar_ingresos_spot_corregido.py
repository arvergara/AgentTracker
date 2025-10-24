#!/usr/bin/env python3
"""
Importar ingresos SPOT desde CSV de forma CORRECTA

CORRECCIÓN: No mapea clientes spot a clientes permanentes existentes.
Cada cliente del CSV se trata como cliente independiente.
"""

import csv
from app import app, db, Cliente, ServicioCliente, IngresoMensual, Area, Servicio

# Mapeo de nombres de meses a números
MESES_MAP = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dic': 12
}

# CORRECCIÓN: Solo normalización de nombres, NO mapeo a otros clientes
NORMALIZACION_NOMBRES = {
    'BCI': 'BCI',
    'CAPITAL ADVISORES': 'Capital Advisores',
    'CAPSTONE': 'Capstone',  # NO mapear a Capstone Copper
    'CONCHA Y TORO': 'Concha y Toro',  # NO mapear a Frutas de Chile
    'EMBAJADA DE ITALIA': 'Embajada de Italia',
    'FALABELLA S.A.': 'Falabella',
    'FALABELLA S.A': 'Falabella',
    'FRUTAS DE CHILE': 'Frutas de Chile Spot',  # Diferenciarlo del permanente
    'OXZO S.A': 'OXZO',
    'OXZO SA': 'OXZO',
}


def normalizar_nombre_cliente(nombre):
    """Normaliza el nombre del cliente sin mapearlo a otro"""
    if not nombre:
        return None

    nombre = nombre.strip()

    # Usar normalización si existe
    nombre_upper = nombre.upper()
    if nombre_upper in NORMALIZACION_NOMBRES:
        return NORMALIZACION_NOMBRES[nombre_upper]

    # Limpiar caracteres especiales comunes
    nombre = nombre.replace('S.A.', 'S.A')
    nombre = nombre.strip()

    return nombre


def importar_csv_spot(csv_path, año_predeterminado=2025):
    """
    Importa CSV de clientes SPOT de forma correcta

    Formato esperado del CSV:
    Columna 0: Nombre del cliente
    Columna 1: Descripción del servicio
    Columnas siguientes: meses (ene-24, feb-24, etc.)
    """

    print(f"\n{'='*80}")
    print(f"📋 IMPORTANDO CLIENTES SPOT: {csv_path}")
    print(f"{'='*80}\n")

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        lineas = list(reader)

    # Leer encabezados (fila 1)
    encabezados = lineas[0]

    # Identificar columnas de meses
    col_meses = []
    for idx, header in enumerate(encabezados):
        header = str(header).strip().lower()
        for mes_nombre, mes_num in MESES_MAP.items():
            if mes_nombre in header:
                # Determinar año
                año = 2024 if '-24' in header else año_predeterminado
                col_meses.append((idx, año, mes_num))
                break

    print(f"📅 Encontradas {len(col_meses)} columnas de fechas")
    print()

    # Obtener o crear área genérica
    area_general = Area.query.filter_by(nombre='General').first()
    if not area_general:
        area_general = Area(nombre='General', activo=True)
        db.session.add(area_general)
        db.session.commit()

    # Variables
    cliente_actual = None
    clientes_creados = 0
    servicios_creados = 0
    ingresos_creados = 0
    clientes_saltados = []

    # Procesar filas
    for linea in lineas[2:]:  # Saltar encabezado y primera fila vacía
        if len(linea) < 3:
            continue

        nombre_cliente_csv = linea[0].strip() if linea[0] else ""
        nombre_servicio = linea[1].strip() if linea[1] else ""

        # Saltar filas totales
        if 'TOTAL' in nombre_cliente_csv.upper():
            continue

        # Saltar vacías
        if not nombre_cliente_csv and not nombre_servicio:
            continue

        # Nuevo cliente
        if nombre_cliente_csv:
            nombre_normalizado = normalizar_nombre_cliente(nombre_cliente_csv)

            if not nombre_normalizado:
                clientes_saltados.append(nombre_cliente_csv)
                cliente_actual = None
                continue

            # Buscar o crear cliente SPOT
            cliente = Cliente.query.filter(
                db.func.upper(Cliente.nombre) == nombre_normalizado.upper()
            ).first()

            if not cliente:
                # Crear nuevo cliente SPOT
                cliente = Cliente(
                    nombre=nombre_normalizado,
                    tipo='spot',
                    activo=True,
                    fecha_inicio=None
                )
                db.session.add(cliente)
                db.session.flush()
                clientes_creados += 1
                print(f"✓ Creado cliente SPOT: {nombre_normalizado}")
            else:
                # Verificar que sea tipo spot
                if cliente.tipo != 'spot':
                    print(f"⚠️  Cliente '{nombre_normalizado}' existe como tipo '{cliente.tipo}'")
                    print(f"   Se actualizará a tipo 'spot'")
                    cliente.tipo = 'spot'
                else:
                    print(f"✓ Cliente existente: {nombre_normalizado}")

            cliente_actual = cliente

        # Servicio
        if nombre_servicio and cliente_actual:
            # Buscar o crear servicio
            servicio = ServicioCliente.query.filter_by(
                cliente_id=cliente_actual.id,
                nombre=nombre_servicio
            ).first()

            if not servicio:
                servicio = ServicioCliente(
                    nombre=nombre_servicio,
                    cliente_id=cliente_actual.id,
                    valor_mensual_uf=0,
                    es_spot=True,
                    activo=True
                )
                db.session.add(servicio)
                db.session.flush()
                servicios_creados += 1
                print(f"  + Servicio: {nombre_servicio}")

            # Importar ingresos mes a mes
            tiene_ingresos = False

            for col_idx, año, mes in col_meses:
                if col_idx >= len(linea):
                    continue

                valor_str = str(linea[col_idx]).strip()
                if not valor_str or valor_str == '' or valor_str == '-':
                    continue

                try:
                    # Limpiar valor
                    valor_str = valor_str.replace(',', '.')
                    ingreso_uf = float(valor_str)

                    if ingreso_uf > 0:
                        tiene_ingresos = True

                        # Crear o actualizar ingreso
                        ingreso = IngresoMensual.query.filter_by(
                            servicio_id=servicio.id,
                            año=año,
                            mes=mes
                        ).first()

                        if ingreso:
                            print(f"    ⚠️  Actualizando ingreso {año}-{mes:02d}: {ingreso.ingreso_uf:.2f} → {ingreso_uf:.2f} UF")
                            ingreso.ingreso_uf = ingreso_uf
                        else:
                            ingreso = IngresoMensual(
                                servicio_id=servicio.id,
                                año=año,
                                mes=mes,
                                ingreso_uf=ingreso_uf
                            )
                            db.session.add(ingreso)
                            ingresos_creados += 1

                except ValueError:
                    print(f"    ⚠️  Valor inválido en {año}-{mes:02d}: '{valor_str}'")
                    continue

            if tiene_ingresos:
                total_servicio = db.session.query(db.func.sum(IngresoMensual.ingreso_uf)).filter(
                    IngresoMensual.servicio_id == servicio.id
                ).scalar() or 0
                print(f"    Total servicio: {total_servicio:.2f} UF")

    # Commit final
    try:
        db.session.commit()
        print("\n" + "=" * 80)
        print("✓ IMPORTACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print()
        print(f"Clientes creados/actualizados: {clientes_creados}")
        print(f"Servicios creados: {servicios_creados}")
        print(f"Ingresos mensuales creados/actualizados: {ingresos_creados}")

        if clientes_saltados:
            print(f"\nClientes saltados ({len(clientes_saltados)}): {', '.join(clientes_saltados)}")

        # Resumen por cliente
        print("\n" + "=" * 80)
        print("RESUMEN DE INGRESOS SPOT POR CLIENTE")
        print("=" * 80)

        clientes_spot = Cliente.query.filter_by(tipo='spot', activo=True).all()
        total_spot = 0

        for cliente in clientes_spot:
            ingresos_cliente = db.session.query(db.func.sum(IngresoMensual.ingreso_uf)).join(
                ServicioCliente
            ).filter(
                ServicioCliente.cliente_id == cliente.id,
                ServicioCliente.es_spot == True,
                ServicioCliente.activo == True
            ).scalar() or 0

            if ingresos_cliente > 0:
                print(f"{cliente.nombre:40s} {ingresos_cliente:10.2f} UF")
                total_spot += ingresos_cliente

        print("-" * 80)
        print(f"{'TOTAL SPOT':40s} {total_spot:10.2f} UF")
        print()

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR al guardar cambios: {e}")
        return False

    return True


def main():
    import sys

    with app.app_context():
        print()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  IMPORTACIÓN CORREGIDA - CLIENTES SPOT".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        # Ruta al CSV
        if len(sys.argv) > 1:
            csv_path = sys.argv[1]
        else:
            csv_path = '/Users/alfil/Desktop/Desarrollos/Comsulting/Clientes_Spot.csv'

        if not csv_path:
            print("❌ Debe proporcionar la ruta al archivo CSV")
            print("   Uso: python importar_ingresos_spot_corregido.py <ruta_csv>")
            return

        # Importar
        importar_csv_spot(csv_path)


if __name__ == '__main__':
    main()
