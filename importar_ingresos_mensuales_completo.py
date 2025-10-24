#!/usr/bin/env python3
"""
Importar ingresos mensuales históricos desde Cliente_Comsulting.csv
Importa 24 meses de ingresos (Ene 2024 - Dic 2025)
"""

import csv
from app import app, db, Cliente, ServicioCliente, IngresoMensual

# Mapeo de columnas a meses
MESES_COLUMNAS = {
    5: (2024, 1),   # ene-24
    6: (2024, 2),   # feb-24
    7: (2024, 3),   # mar-24
    8: (2024, 4),   # abr-24
    9: (2024, 5),   # may-24
    10: (2024, 6),  # jun-24
    11: (2024, 7),  # jul-24
    12: (2024, 8),  # ago-24
    13: (2024, 9),  # sept-24
    14: (2024, 10), # oct-24
    15: (2024, 11), # nov-24
    16: (2024, 12), # dic-24
    17: (2025, 1),  # ene-25
    18: (2025, 2),  # feb-25
    19: (2025, 3),  # mar-25
    20: (2025, 4),  # abr-25
    21: (2025, 5),  # may-25
    22: (2025, 6),  # jun-25
    23: (2025, 7),  # jul-25
    24: (2025, 8),  # ago-25
    25: (2025, 9),  # sept-25
    26: (2025, 10), # oct-25
    27: (2025, 11), # nov-25
    28: (2025, 12), # dic-25
}

def normalizar_nombre(nombre):
    """Normaliza nombre para comparación"""
    if not nombre:
        return ""
    return nombre.strip().upper().replace('.', '').replace('  ', ' ')

def buscar_cliente(nombre_csv):
    """Busca cliente en la base de datos"""
    nombre_norm = normalizar_nombre(nombre_csv)

    # Intento 1: Match exacto normalizado
    cliente = Cliente.query.filter(
        db.func.upper(db.func.replace(Cliente.nombre, '.', '')) == nombre_norm
    ).first()

    if cliente:
        return cliente

    # Intento 2: Match parcial (primeras 10 letras)
    if len(nombre_csv) >= 10:
        cliente = Cliente.query.filter(
            Cliente.nombre.ilike(f'%{nombre_csv[:10]}%')
        ).first()
        if cliente:
            return cliente

    # Intento 3: Casos especiales (mapeo CSV → BD)
    mapeo_especial = {
        'MANTOS COPPER SA': 'Capstone',
        'MANTO VERDE SA': 'Capstone',
        'CAPSTONE MINNING CORP': 'Capstone Copper',
        'CAPSTONE': 'Capstone Copper',
        'ISIDORO QUIROGA': 'IQ SALMONES',
        'LIBERTY SEGUROS': 'LIBERTY',
        'MAE HOLDING CHILE SPA': 'MAE',
        'FALABELLA S.A.': 'FALABELLA',
        'OXZO S.A': 'OXZO',
        'EMBAJADA DE ITALIA': 'EMBAJADA ITALIA',
        'BCI': 'Comité de Paltas',  # Revisar si este mapeo es correcto
        'CONCHA Y TORO': 'Frutas de Chile',  # Revisar mapeo
    }

    nombre_mapeado = mapeo_especial.get(nombre_csv.upper().strip())
    if nombre_mapeado:
        cliente = Cliente.query.filter(
            Cliente.nombre.ilike(f'%{nombre_mapeado}%')
        ).first()

    return cliente

def importar_ingresos():
    """Importa ingresos mensuales desde el CSV"""

    print("=" * 80)
    print("IMPORTACIÓN DE INGRESOS MENSUALES 2024-2025")
    print("=" * 80)
    print()

    csv_path = "../Cliente_Comsulting.csv"

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            lineas = list(reader)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {csv_path}")
        return

    print(f"📄 CSV cargado: {len(lineas)} líneas")
    print(f"📅 Importando {len(MESES_COLUMNAS)} meses (Ene 2024 - Dic 2025)")
    print()

    # Estadísticas
    cliente_actual = None
    servicios_creados = 0
    ingresos_creados = 0
    ingresos_actualizados = 0
    clientes_no_encontrados = set()

    # Variables de seguimiento

    for idx, linea in enumerate(lineas, 1):
        # Saltar encabezados
        if idx <= 2:
            continue

        if not linea or len(linea) < 5:
            continue

        nombre_cliente = linea[0].strip() if linea[0] else ""
        nombre_servicio = linea[1].strip() if linea[1] else ""

        # Línea vacía = fin de sección
        if not nombre_cliente and not nombre_servicio:
            cliente_actual = None
            continue

        # Secciones especiales - marcar pero continuar
        if nombre_cliente in ['CLIENTES PERMANENTES', 'CLIENTES O SERVICIOS SPOT']:
            print(f"\n{'='*60}")
            print(f"📂 {nombre_cliente}")
            print(f"{'='*60}")
            continue

        # Nuevo cliente
        if nombre_cliente:
            cliente = buscar_cliente(nombre_cliente)

            if cliente:
                cliente_actual = cliente
                print(f"\n✓ {cliente.nombre}")
            else:
                clientes_no_encontrados.add(nombre_cliente)
                cliente_actual = None
                continue

        # Servicio con ingresos mensuales
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
                    valor_mensual_uf=0,  # Se calculará del promedio
                    activo=True
                )
                db.session.add(servicio)
                db.session.flush()
                servicios_creados += 1
                print(f"  + Servicio: {nombre_servicio}")

            # Importar ingresos mes a mes
            ingresos_mes = []
            for col_idx, (año, mes) in MESES_COLUMNAS.items():
                if col_idx >= len(linea):
                    continue

                valor_str = linea[col_idx].strip()
                if not valor_str:
                    continue

                try:
                    ingreso_uf = float(valor_str.replace(',', '.'))

                    if ingreso_uf <= 0:
                        continue

                    # Buscar o crear ingreso
                    ingreso = IngresoMensual.query.filter_by(
                        servicio_id=servicio.id,
                        año=año,
                        mes=mes
                    ).first()

                    if ingreso:
                        ingreso.ingreso_uf = ingreso_uf
                        ingresos_actualizados += 1
                    else:
                        ingreso = IngresoMensual(
                            servicio_id=servicio.id,
                            año=año,
                            mes=mes,
                            ingreso_uf=ingreso_uf
                        )
                        db.session.add(ingreso)
                        ingresos_creados += 1

                    ingresos_mes.append(f"{mes}/{año}:{ingreso_uf}")

                except (ValueError, TypeError):
                    continue

            if ingresos_mes:
                print(f"    💰 {len(ingresos_mes)} meses con ingresos")

            # Commit cada 50 servicios para no sobrecargar
            if (servicios_creados + ingresos_creados) % 50 == 0:
                db.session.commit()

    # Commit final
    db.session.commit()

    print()
    print("=" * 80)
    print("✓ IMPORTACIÓN COMPLETADA")
    print("=" * 80)
    print(f"📊 Servicios creados: {servicios_creados}")
    print(f"💰 Ingresos creados: {ingresos_creados}")
    print(f"🔄 Ingresos actualizados: {ingresos_actualizados}")
    print(f"⚠️  Clientes no encontrados: {len(clientes_no_encontrados)}")

    if clientes_no_encontrados:
        print(f"\n📋 Clientes no encontrados:")
        for nombre in sorted(clientes_no_encontrados):
            print(f"  - {nombre}")

    # Resumen final
    print()
    total_ingresos = db.session.query(db.func.sum(IngresoMensual.ingreso_uf)).scalar() or 0
    total_registros = IngresoMensual.query.count()
    print(f"💵 Total en sistema: {total_ingresos:,.2f} UF")
    print(f"📅 Total registros: {total_registros:,} (24 meses x servicios)")
    print()

if __name__ == '__main__':
    with app.app_context():
        importar_ingresos()
