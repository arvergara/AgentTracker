#!/usr/bin/env python3
"""
Verificar si los clientes del CSV Spot están mapeados incorrectamente
a clientes permanentes existentes
"""

from app import app, db, Cliente, ServicioCliente, IngresoMensual
from sqlalchemy import func

# Clientes del CSV Spot que podrían estar mapeados incorrectamente
CLIENTES_SPOT_CSV = {
    'BCI': 'Grupo Defensa',
    'Capital Advisores': None,  # Debería ser cliente independiente
    'Capstone': 'Capstone Copper',
    'Concha y Toro': 'Frutas de Chile',
    'Embajada de Italia': None,
    'FALABELLA S.A.': None,
    'FRUTAS DE CHILE': 'Frutas de Chile',
    'OXZO S.A': 'OXZO',
}

def verificar_duplicacion():
    with app.app_context():
        print("=" * 80)
        print("VERIFICACIÓN DE DUPLICACIÓN DE CLIENTES SPOT")
        print("=" * 80)
        print()

        print("1. CLIENTES CON SERVICIOS PERMANENTES Y SPOT")
        print("-" * 80)

        clientes_mixtos = []

        # Buscar todos los clientes
        todos_clientes = Cliente.query.filter_by(activo=True).all()

        for cliente in todos_clientes:
            servicios_perm = ServicioCliente.query.filter_by(
                cliente_id=cliente.id,
                es_spot=False,
                activo=True
            ).count()

            servicios_spot = ServicioCliente.query.filter_by(
                cliente_id=cliente.id,
                es_spot=True,
                activo=True
            ).count()

            if servicios_perm > 0 and servicios_spot > 0:
                clientes_mixtos.append({
                    'nombre': cliente.nombre,
                    'tipo': cliente.tipo,
                    'servicios_perm': servicios_perm,
                    'servicios_spot': servicios_spot
                })

        if clientes_mixtos:
            print(f"⚠️  ENCONTRADOS {len(clientes_mixtos)} CLIENTES CON AMBOS TIPOS DE SERVICIOS:\n")

            for c in clientes_mixtos:
                print(f"  • {c['nombre']}")
                print(f"    Tipo en BD: {c['tipo']}")
                print(f"    Servicios permanentes: {c['servicios_perm']}")
                print(f"    Servicios spot: {c['servicios_spot']}")

                # Calcular ingresos de cada tipo
                cliente_obj = Cliente.query.filter_by(nombre=c['nombre']).first()

                ingresos_perm = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
                    ServicioCliente
                ).filter(
                    ServicioCliente.cliente_id == cliente_obj.id,
                    ServicioCliente.es_spot == False,
                    ServicioCliente.activo == True
                ).scalar() or 0

                ingresos_spot = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
                    ServicioCliente
                ).filter(
                    ServicioCliente.cliente_id == cliente_obj.id,
                    ServicioCliente.es_spot == True,
                    ServicioCliente.activo == True
                ).scalar() or 0

                print(f"    Ingresos permanentes: {ingresos_perm:.2f} UF")
                print(f"    Ingresos spot: {ingresos_spot:.2f} UF")
                print(f"    TOTAL (duplicado): {ingresos_perm + ingresos_spot:.2f} UF")
                print()
        else:
            print("✓ No hay clientes con servicios permanentes y spot mezclados")

        print("\n")
        print("2. VERIFICACIÓN DE MAPEO INCORRECTO")
        print("-" * 80)

        for nombre_csv, nombre_mapeado in CLIENTES_SPOT_CSV.items():
            if nombre_mapeado:
                cliente = Cliente.query.filter(
                    db.func.upper(Cliente.nombre) == nombre_mapeado.upper()
                ).first()

                if cliente:
                    servicios_perm = ServicioCliente.query.filter_by(
                        cliente_id=cliente.id,
                        es_spot=False,
                        activo=True
                    ).count()

                    servicios_spot = ServicioCliente.query.filter_by(
                        cliente_id=cliente.id,
                        es_spot=True,
                        activo=True
                    ).count()

                    if servicios_perm > 0 and servicios_spot > 0:
                        print(f"❌ MAPEO INCORRECTO DETECTADO:")
                        print(f"   CSV Spot: '{nombre_csv}' → Mapeado a: '{nombre_mapeado}'")
                        print(f"   Este cliente tiene {servicios_perm} servicios permanentes")
                        print(f"   y {servicios_spot} servicios spot")
                        print(f"   Los ingresos spot están sumándose incorrectamente!")
                        print()

        print("\n")
        print("3. DETALLE DE SERVICIOS POR CLIENTE")
        print("-" * 80)

        # Mostrar todos los servicios de los clientes problemáticos
        for c in clientes_mixtos:
            print(f"\n{'='*60}")
            print(f"CLIENTE: {c['nombre']}")
            print(f"{'='*60}")

            cliente_obj = Cliente.query.filter_by(nombre=c['nombre']).first()
            servicios = ServicioCliente.query.filter_by(
                cliente_id=cliente_obj.id,
                activo=True
            ).all()

            for servicio in servicios:
                tipo_servicio = "SPOT" if servicio.es_spot else "PERMANENTE"
                ingresos_servicio = db.session.query(func.sum(IngresoMensual.ingreso_uf)).filter(
                    IngresoMensual.servicio_id == servicio.id
                ).scalar() or 0

                print(f"\n  Servicio: {servicio.nombre}")
                print(f"  Tipo: {tipo_servicio}")
                print(f"  Ingresos totales: {ingresos_servicio:.2f} UF")

                # Mostrar ingresos mensuales
                ingresos_mensuales = IngresoMensual.query.filter_by(
                    servicio_id=servicio.id
                ).order_by(IngresoMensual.año, IngresoMensual.mes).all()

                if ingresos_mensuales:
                    print(f"  Meses con ingresos:")
                    for ing in ingresos_mensuales:
                        print(f"    - {ing.año}-{ing.mes:02d}: {ing.ingreso_uf:.2f} UF")

        print("\n")
        print("=" * 80)
        print("RECOMENDACIÓN")
        print("=" * 80)
        print()
        print("Si se encontraron clientes con servicios permanentes y spot:")
        print()
        print("1. Los clientes SPOT del CSV deben ser clientes INDEPENDIENTES")
        print("2. NO deben mapearse a clientes permanentes existentes")
        print("3. Eliminar el mapeo incorrecto en importar_ingresos_csv_final.py")
        print("4. Crear clientes spot separados si no existen")
        print("5. Reasignar los servicios spot a los clientes correctos")
        print()

if __name__ == '__main__':
    verificar_duplicacion()
