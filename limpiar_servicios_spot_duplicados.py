#!/usr/bin/env python3
"""
Script para limpiar servicios SPOT incorrectamente asignados a clientes PERMANENTES

IMPORTANTE: Este script identifica y (opcionalmente) elimina servicios SPOT
que fueron mapeados incorrectamente a clientes que deberían ser solo PERMANENTES.
"""

from app import app, db, Cliente, ServicioCliente, IngresoMensual, RegistroHora
from sqlalchemy import func
import sys

# Mapeo INCORRECTO del script original que causa la duplicación
MAPEO_INCORRECTO = {
    'BCI': 'Grupo Defensa',
    'CAPSTONE': 'Capstone Copper',
    'CONCHA Y TORO': 'Frutas de Chile',
    'CAPITAL ADVISORES': 'Comité de Paltas',
}

def analizar_problema():
    """Analiza el problema sin hacer cambios"""

    print("=" * 80)
    print("ANÁLISIS DE SERVICIOS SPOT DUPLICADOS")
    print("=" * 80)
    print()

    # Buscar clientes que tienen AMBOS tipos de servicios
    print("1. BUSCANDO CLIENTES CON SERVICIOS PERMANENTES Y SPOT...")
    print("-" * 80)
    print()

    clientes_problema = []

    for nombre_incorrecto, nombre_mapeado in MAPEO_INCORRECTO.items():
        cliente = Cliente.query.filter(
            db.func.upper(Cliente.nombre).like(f'%{nombre_mapeado.upper()}%')
        ).first()

        if not cliente:
            continue

        servicios_perm = ServicioCliente.query.filter_by(
            cliente_id=cliente.id,
            es_spot=False,
            activo=True
        ).all()

        servicios_spot = ServicioCliente.query.filter_by(
            cliente_id=cliente.id,
            es_spot=True,
            activo=True
        ).all()

        if servicios_perm and servicios_spot:
            ingresos_perm = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
                ServicioCliente
            ).filter(
                ServicioCliente.cliente_id == cliente.id,
                ServicioCliente.es_spot == False
            ).scalar() or 0

            ingresos_spot = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
                ServicioCliente
            ).filter(
                ServicioCliente.cliente_id == cliente.id,
                ServicioCliente.es_spot == True
            ).scalar() or 0

            horas_spot = db.session.query(func.sum(RegistroHora.horas)).join(
                ServicioCliente
            ).filter(
                ServicioCliente.cliente_id == cliente.id,
                ServicioCliente.es_spot == True
            ).scalar() or 0

            clientes_problema.append({
                'cliente': cliente,
                'servicios_perm': servicios_perm,
                'servicios_spot': servicios_spot,
                'ingresos_perm': ingresos_perm,
                'ingresos_spot': ingresos_spot,
                'horas_spot': horas_spot
            })

            print(f"❌ PROBLEMA DETECTADO: {cliente.nombre}")
            print(f"   Tipo en BD: {cliente.tipo}")
            print(f"   Servicios permanentes: {len(servicios_perm)}")
            print(f"   Servicios spot: {len(servicios_spot)}")
            print(f"   Ingresos permanentes: {ingresos_perm:.2f} UF")
            print(f"   Ingresos spot (DUPLICADOS): {ingresos_spot:.2f} UF")
            print(f"   Horas registradas en servicios spot: {horas_spot:.1f}h")
            print(f"   TOTAL SOBREDIMENSIONADO: {ingresos_perm + ingresos_spot:.2f} UF")
            print()

            # Detallar servicios spot
            print(f"   Servicios SPOT a eliminar:")
            for servicio in servicios_spot:
                ingresos_serv = db.session.query(func.sum(IngresoMensual.ingreso_uf)).filter(
                    IngresoMensual.servicio_id == servicio.id
                ).scalar() or 0

                horas_serv = db.session.query(func.sum(RegistroHora.horas)).filter(
                    RegistroHora.servicio_id == servicio.id
                ).scalar() or 0

                print(f"     - ID: {servicio.id} | Nombre: {servicio.nombre}")
                print(f"       Ingresos: {ingresos_serv:.2f} UF | Horas: {horas_serv:.1f}h")
            print()

    if not clientes_problema:
        print("✓ No se detectaron problemas de servicios spot duplicados")
        return []

    print("\n")
    print("=" * 80)
    print("RESUMEN DEL IMPACTO")
    print("=" * 80)
    print()

    total_ingresos_duplicados = sum(c['ingresos_spot'] for c in clientes_problema)
    total_horas_afectadas = sum(c['horas_spot'] for c in clientes_problema)

    print(f"Clientes afectados: {len(clientes_problema)}")
    print(f"Ingresos SPOT duplicados: {total_ingresos_duplicados:.2f} UF")
    print(f"Horas registradas en servicios spot: {total_horas_afectadas:.1f}h")
    print()

    return clientes_problema


def limpiar_servicios_spot(clientes_problema, ejecutar=False):
    """Limpia los servicios spot incorrectamente asignados"""

    if not clientes_problema:
        print("No hay nada que limpiar")
        return

    print("\n")
    print("=" * 80)
    print("LIMPIEZA DE SERVICIOS SPOT DUPLICADOS")
    print("=" * 80)
    print()

    if not ejecutar:
        print("⚠️  MODO SIMULACIÓN - No se realizarán cambios")
        print("    Ejecuta con --ejecutar para aplicar los cambios")
        print()

    total_servicios_eliminados = 0
    total_ingresos_eliminados = 0
    total_registros_horas_actualizados = 0

    for item in clientes_problema:
        cliente = item['cliente']
        servicios_spot = item['servicios_spot']

        print(f"Procesando: {cliente.nombre}")

        for servicio in servicios_spot:
            # Contar ingresos asociados
            ingresos = IngresoMensual.query.filter_by(servicio_id=servicio.id).all()
            num_ingresos = len(ingresos)
            total_ing = sum(i.ingreso_uf for i in ingresos)

            # Contar horas registradas
            horas = RegistroHora.query.filter_by(servicio_id=servicio.id).all()
            num_horas = len(horas)

            print(f"  - Servicio: {servicio.nombre} (ID: {servicio.id})")
            print(f"    Ingresos asociados: {num_ingresos} registros ({total_ing:.2f} UF)")
            print(f"    Horas registradas: {num_horas} registros")

            if ejecutar:
                # Eliminar ingresos mensuales
                for ingreso in ingresos:
                    db.session.delete(ingreso)

                # Actualizar registros de horas (cambiar servicio_id a NULL o al servicio genérico)
                # Por seguridad, solo los marcamos como servicio_id = None
                for hora in horas:
                    hora.servicio_id = None

                # Desactivar el servicio
                servicio.activo = False

                total_servicios_eliminados += 1
                total_ingresos_eliminados += num_ingresos
                total_registros_horas_actualizados += num_horas

                print(f"    ✓ Servicio desactivado, ingresos eliminados, horas actualizadas")
            else:
                print(f"    [SIMULACIÓN] Se eliminarían estos datos")

        print()

    if ejecutar:
        try:
            db.session.commit()
            print("=" * 80)
            print("✓ LIMPIEZA COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print()
            print(f"Servicios desactivados: {total_servicios_eliminados}")
            print(f"Registros de ingresos eliminados: {total_ingresos_eliminados}")
            print(f"Registros de horas actualizados: {total_registros_horas_actualizados}")
            print()
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR al aplicar cambios: {e}")
            return False
    else:
        print("=" * 80)
        print("RESUMEN DE CAMBIOS (SIMULACIÓN)")
        print("=" * 80)
        print()
        print("Para aplicar estos cambios, ejecuta:")
        print("  python limpiar_servicios_spot_duplicados.py --ejecutar")
        print()

    return True


def main():
    ejecutar = '--ejecutar' in sys.argv

    with app.app_context():
        print()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  SCRIPT DE LIMPIEZA - SERVICIOS SPOT DUPLICADOS".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        # Analizar problema
        clientes_problema = analizar_problema()

        if not clientes_problema:
            print("\n✓ No se requiere limpieza")
            return

        # Preguntar confirmación si se va a ejecutar
        if ejecutar:
            print()
            print("⚠️  ADVERTENCIA: Estás a punto de realizar cambios PERMANENTES en la base de datos")
            print()
            respuesta = input("¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): ")

            if respuesta.strip().upper() != 'SI':
                print("\nOperación cancelada")
                return

        # Limpiar
        limpiar_servicios_spot(clientes_problema, ejecutar)


if __name__ == '__main__':
    main()
