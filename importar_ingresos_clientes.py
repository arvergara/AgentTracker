#!/usr/bin/env python3
"""
Importar ingresos mensuales desde Cliente_Comsulting.csv
"""

import csv
from datetime import datetime
from app import app, db, Cliente, Servicio, IngresoMensual

def normalizar_nombre(nombre):
    """Normaliza nombre para comparación"""
    if not nombre:
        return ""
    return nombre.strip().upper().replace('.', '').replace('  ', ' ')

def importar_ingresos():
    """Importa ingresos mensuales desde el CSV"""

    print("=" * 80)
    print("IMPORTACIÓN DE INGRESOS MENSUALES")
    print("=" * 80)
    print()

    # Leer CSV
    csv_path = "../Cliente_Comsulting.csv"

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            lineas = list(reader)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {csv_path}")
        return

    print(f"📄 CSV cargado: {len(lineas)} líneas")
    print()

    # Variables de estado
    cliente_actual = None
    servicios_creados = 0
    ingresos_creados = 0
    errores = []

    # Año y mes actual para los ingresos (Octubre 2025)
    año = 2025
    mes = 10

    for idx, linea in enumerate(lineas, 1):
        # Saltar líneas vacías o encabezados
        if idx <= 2:
            continue

        if not linea or len(linea) < 4:
            continue

        nombre_cliente = linea[0].strip() if linea[0] else ""
        nombre_servicio = linea[1].strip() if linea[1] else ""
        fee_especifico = linea[2].strip() if linea[2] else ""

        # Línea vacía = fin de sección
        if not nombre_cliente and not nombre_servicio:
            cliente_actual = None
            continue

        # Secciones especiales - saltar
        if nombre_cliente in ['CLIENTES PERMANENTES', 'CLIENTES O SERVICIOS SPOT']:
            continue

        # Nuevo cliente
        if nombre_cliente:
            # Buscar cliente en la base de datos
            cliente_norm = normalizar_nombre(nombre_cliente)
            cliente = Cliente.query.filter(
                db.func.upper(db.func.replace(Cliente.nombre, '.', '')) == cliente_norm
            ).first()

            if not cliente:
                # Intentar match parcial
                cliente = Cliente.query.filter(
                    Cliente.nombre.ilike(f'%{nombre_cliente[:10]}%')
                ).first()

            if cliente:
                cliente_actual = cliente
                print(f"✓ Cliente encontrado: {cliente.nombre}")
            else:
                print(f"⚠️  Cliente NO encontrado: {nombre_cliente}")
                cliente_actual = None
                continue

        # Servicio con ingreso
        if nombre_servicio and fee_especifico and cliente_actual:
            try:
                ingreso_uf = float(fee_especifico.replace(',', '.'))

                if ingreso_uf <= 0:
                    continue

                # Buscar o crear servicio
                servicio = Servicio.query.filter_by(
                    cliente_id=cliente_actual.id,
                    nombre=nombre_servicio
                ).first()

                if not servicio:
                    # Crear servicio nuevo (asignar a área "Externas" por defecto)
                    from app import Area
                    area_externa = Area.query.filter_by(nombre='Externas').first()

                    if not area_externa:
                        area_externa = Area.query.first()

                    servicio = Servicio(
                        nombre=nombre_servicio,
                        cliente_id=cliente_actual.id,
                        area_id=area_externa.id if area_externa else None,
                        activo=True
                    )
                    db.session.add(servicio)
                    db.session.flush()
                    servicios_creados += 1
                    print(f"  + Servicio creado: {nombre_servicio}")

                # Crear o actualizar ingreso mensual
                ingreso = IngresoMensual.query.filter_by(
                    servicio_id=servicio.id,
                    año=año,
                    mes=mes
                ).first()

                if ingreso:
                    ingreso.ingreso_uf = ingreso_uf
                    print(f"    → Ingreso actualizado: {ingreso_uf} UF")
                else:
                    ingreso = IngresoMensual(
                        servicio_id=servicio.id,
                        año=año,
                        mes=mes,
                        ingreso_uf=ingreso_uf
                    )
                    db.session.add(ingreso)
                    ingresos_creados += 1
                    print(f"    + Ingreso creado: {ingreso_uf} UF")

            except (ValueError, TypeError) as e:
                errores.append(f"Línea {idx}: Error procesando fee '{fee_especifico}': {e}")

    # Commit
    db.session.commit()

    print()
    print("=" * 80)
    print("✓ IMPORTACIÓN COMPLETADA")
    print("=" * 80)
    print(f"📊 Servicios creados: {servicios_creados}")
    print(f"💰 Ingresos mensuales creados: {ingresos_creados}")
    print(f"📅 Mes de referencia: {mes}/{año}")

    if errores:
        print(f"\n⚠️  Errores ({len(errores)}):")
        for err in errores[:10]:
            print(f"  - {err}")

    print()

    # Resumen final
    total_ingresos = db.session.query(db.func.sum(IngresoMensual.ingreso_uf)).scalar() or 0
    print(f"💵 Total ingresos en sistema: {total_ingresos:,.2f} UF")
    print()

if __name__ == '__main__':
    with app.app_context():
        importar_ingresos()
