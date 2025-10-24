#!/usr/bin/env python3
"""
Importar ingresos desde CSV separados (Permanentes y Spot)
"""

import csv
from app import app, db, Cliente, ServicioCliente, IngresoMensual

# Mapeo de nombres de meses a números
MESES_MAP = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dic': 12
}

# Mapeo de clientes CSV → BD
MAPEO_CLIENTES = {
    'AFP MODELO': 'AFP Modelo',
    'CHILEXPRESS': 'Chilexpress',
    'CLINICAS': 'CLÍNICAS',
    'COMITE DE PALTAS': 'Comité de Paltas',
    'ISAPRES': 'ISAPRES',
    'OXZO SA': 'OXZO',
    'MANT COPPER SA': 'Capstone Copper',
    'MANTO VERDE SA': 'Capstone Copper',
    'CAPITAL ADVISORES': 'Comité de Paltas',  # Revisar
    'CAPSTONE': 'Capstone Copper',
    'BCI': 'Grupo Defensa',  # Revisar mapeo
    'CONCHA Y TORO': 'Frutas de Chile',  # Revisar
}

def buscar_cliente(nombre_csv):
    """Busca cliente en BD"""
    if not nombre_csv:
        return None

    nombre = nombre_csv.strip()

    # Usar mapeo si existe
    nombre_bd = MAPEO_CLIENTES.get(nombre.upper(), nombre)

    # Buscar en BD
    cliente = Cliente.query.filter(
        db.func.upper(Cliente.nombre) == nombre_bd.upper()
    ).first()

    if not cliente:
        # Match parcial
        cliente = Cliente.query.filter(
            Cliente.nombre.ilike(f'%{nombre[:6]}%')
        ).first()

    return cliente

def importar_csv(csv_path, tipo_cliente):
    """Importa un CSV"""

    print(f"\n{'='*60}")
    print(f"📋 Importando: {csv_path}")
    print(f"   Tipo: {tipo_cliente.upper()}")
    print(f"{'='*60}\n")

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
                año = 2024 if '-24' in header else 2025
                col_meses.append((idx, año, mes_num))
                break

    print(f"📅 Encontradas {len(col_meses)} columnas de fechas")
    print()

    # Variables
    cliente_actual = None
    servicios_creados = 0
    ingresos_creados = 0
    no_encontrados = set()

    # Procesar filas
    for linea in lineas[2:]:  # Saltar encabezado y primera fila vacía
        if len(linea) < 3:
            continue

        nombre_cliente = linea[0].strip() if linea[0] else ""
        nombre_servicio = linea[1].strip() if linea[1] else ""

        # Saltar vacías
        if not nombre_cliente and not nombre_servicio:
            continue

        # Nuevo cliente
        if nombre_cliente:
            cliente = buscar_cliente(nombre_cliente)
            if cliente:
                cliente_actual = cliente
                if cliente.tipo != tipo_cliente:
                    cliente.tipo = tipo_cliente
                print(f"✓ {cliente.nombre}")
            else:
                no_encontrados.add(nombre_cliente)
                cliente_actual = None
                continue

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
                    es_spot=(tipo_cliente == 'spot'),
                    activo=True
                )
                db.session.add(servicio)
                db.session.flush()
                servicios_creados += 1
                print(f"  + {nombre_servicio}")

            # Importar ingresos mes a mes
            total_ingreso = 0
            meses_con_ingreso = 0

            for col_idx, año, mes in col_meses:
                if col_idx >= len(linea):
                    continue

                valor_str = str(linea[col_idx]).strip()
                if not valor_str or valor_str == '':
                    continue

                try:
                    # Limpiar valor
                    valor_str = valor_str.replace(',', '.')
                    ingreso_uf = float(valor_str)

                    if ingreso_uf > 0:
                        # Crear o actualizar ingreso
                        ingreso = IngresoMensual.query.filter_by(
                            servicio_id=servicio.id,
                            año=año,
                            mes=mes
                        ).first()

                        if ingreso:
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

                        total_ingreso += ingreso_uf
                        meses_con_ingreso += 1

                except (ValueError, TypeError):
                    pass

            # Actualizar valor promedio
            if meses_con_ingreso > 0:
                promedio = total_ingreso / meses_con_ingreso
                servicio.valor_mensual_uf = round(promedio, 2)
                print(f"    💰 {meses_con_ingreso} meses, {promedio:.2f} UF/mes")

            # Commit cada 20
            if servicios_creados % 20 == 0:
                db.session.commit()

    db.session.commit()

    if no_encontrados:
        print(f"\n⚠️  No encontrados ({len(no_encontrados)}):")
        for n in sorted(no_encontrados):
            print(f"  - {n}")

    return servicios_creados, ingresos_creados

if __name__ == '__main__':
    with app.app_context():
        print("=" * 80)
        print("IMPORTACIÓN DE INGRESOS DESDE CSV")
        print("=" * 80)

        # Importar permanentes
        s1, i1 = importar_csv('../Clientes_Permanentes.csv', 'permanente')

        # Importar spot
        s2, i2 = importar_csv('../Clientes_Spot.csv', 'spot')

        # Resumen
        print(f"\n{'='*80}")
        print("✅ IMPORTACIÓN COMPLETADA")
        print(f"{'='*80}")
        print(f"📊 Servicios creados: {s1 + s2}")
        print(f"💰 Ingresos creados: {i1 + i2}")

        total_uf = db.session.query(db.func.sum(IngresoMensual.ingreso_uf)).scalar() or 0
        total_reg = IngresoMensual.query.count()

        print(f"\n💵 Total en sistema: {total_uf:,.2f} UF")
        print(f"📅 Total registros: {total_reg:,}")
        print()
