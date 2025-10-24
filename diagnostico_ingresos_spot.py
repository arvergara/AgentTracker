"""
Script de diagnóstico para identificar problemas de sobredimensionamiento en ingresos SPOT
"""
import os
from app import app, db, Cliente, ServicioCliente, IngresoMensual
from sqlalchemy import func, extract
from datetime import datetime

def diagnosticar_ingresos_spot():
    with app.app_context():
        print("=" * 80)
        print("DIAGNÓSTICO DE INGRESOS SPOT")
        print("=" * 80)
        print()

        # 1. Clientes SPOT con múltiples servicios
        print("1. CLIENTES SPOT CON MÚLTIPLES SERVICIOS ACTIVOS")
        print("-" * 80)

        clientes_spot = Cliente.query.filter_by(tipo='spot', activo=True).all()

        for cliente in clientes_spot:
            servicios_activos = cliente.servicios.filter_by(activo=True).all()

            if len(servicios_activos) > 1:
                print(f"\n⚠️  CLIENTE: {cliente.nombre}")
                print(f"   Servicios activos: {len(servicios_activos)}")

                for servicio in servicios_activos:
                    ingresos_2025 = IngresoMensual.query.filter_by(
                        servicio_id=servicio.id,
                        año=2025
                    ).all()

                    total_servicio = sum(i.ingreso_uf for i in ingresos_2025)

                    print(f"   - Servicio ID {servicio.id}: {servicio.nombre if hasattr(servicio, 'nombre') else 'Sin nombre'}")
                    print(f"     Ingresos 2025: {total_servicio:.2f} UF")
                    print(f"     Meses con ingresos: {len(ingresos_2025)}")

                    for ingreso in ingresos_2025:
                        print(f"       {ingreso.año}-{ingreso.mes:02d}: {ingreso.ingreso_uf:.2f} UF")

        print("\n")
        print("2. COMPARACIÓN: TOTAL SPOT SEGÚN DASHBOARD VS SUMA REAL")
        print("-" * 80)

        # Cálculo según dashboard (suma todos los servicios)
        total_dashboard = 0
        for cliente in clientes_spot:
            servicios = cliente.servicios.filter_by(activo=True).all()
            for servicio in servicios:
                ingresos_año = db.session.query(func.sum(IngresoMensual.ingreso_uf)).filter(
                    IngresoMensual.servicio_id == servicio.id,
                    IngresoMensual.año == 2025
                ).scalar() or 0
                total_dashboard += ingresos_año

        # Suma real (sin duplicar)
        total_real = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
            ServicioCliente
        ).join(
            Cliente
        ).filter(
            Cliente.tipo == 'spot',
            Cliente.activo == True,
            ServicioCliente.activo == True,
            IngresoMensual.año == 2025
        ).scalar() or 0

        print(f"Total según lógica del dashboard: {total_dashboard:.2f} UF")
        print(f"Total real en base de datos: {total_real:.2f} UF")

        if total_dashboard != total_real:
            print(f"\n⚠️  DIFERENCIA DETECTADA: {abs(total_dashboard - total_real):.2f} UF")
        else:
            print("\n✓ Los totales coinciden (no hay duplicación por múltiples servicios)")

        print("\n")
        print("3. INGRESOS DUPLICADOS (mismo servicio, año, mes)")
        print("-" * 80)

        duplicados = db.session.query(
            IngresoMensual.servicio_id,
            IngresoMensual.año,
            IngresoMensual.mes,
            func.count(IngresoMensual.id).label('count')
        ).group_by(
            IngresoMensual.servicio_id,
            IngresoMensual.año,
            IngresoMensual.mes
        ).having(
            func.count(IngresoMensual.id) > 1
        ).all()

        if duplicados:
            print(f"⚠️  SE ENCONTRARON {len(duplicados)} DUPLICADOS:")
            for dup in duplicados:
                servicio = ServicioCliente.query.get(dup.servicio_id)
                cliente = servicio.cliente if servicio else None
                print(f"   - Servicio ID {dup.servicio_id} ({cliente.nombre if cliente else 'N/A'})")
                print(f"     {dup.año}-{dup.mes:02d}: {dup.count} registros")
        else:
            print("✓ No se encontraron duplicados")

        print("\n")
        print("4. DESGLOSE MENSUAL DE INGRESOS SPOT 2025")
        print("-" * 80)

        ingresos_por_mes = db.session.query(
            IngresoMensual.mes,
            func.sum(IngresoMensual.ingreso_uf).label('total')
        ).join(
            ServicioCliente
        ).join(
            Cliente
        ).filter(
            Cliente.tipo == 'spot',
            Cliente.activo == True,
            ServicioCliente.activo == True,
            IngresoMensual.año == 2025
        ).group_by(
            IngresoMensual.mes
        ).order_by(
            IngresoMensual.mes
        ).all()

        meses_nombres = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        total_anual = 0
        for mes_num, total_mes in ingresos_por_mes:
            print(f"{meses_nombres[mes_num]:12s}: {total_mes:10.2f} UF")
            total_anual += total_mes

        print(f"\n{'TOTAL 2025':12s}: {total_anual:10.2f} UF")

        print("\n")
        print("5. CLIENTES QUE ESTÁN EN PERMANENTE Y SPOT")
        print("-" * 80)

        # Buscar clientes con servicios tanto permanentes como spot
        clientes_mixtos = db.session.query(Cliente).join(
            ServicioCliente
        ).filter(
            Cliente.activo == True,
            ServicioCliente.activo == True
        ).all()

        for cliente in clientes_mixtos:
            servicios_perm = cliente.servicios.filter_by(activo=True, es_spot=False).count()
            servicios_spot = cliente.servicios.filter_by(activo=True, es_spot=True).count()

            if servicios_perm > 0 and servicios_spot > 0:
                print(f"\n⚠️  CLIENTE MIXTO: {cliente.nombre}")
                print(f"   Tipo cliente: {cliente.tipo}")
                print(f"   Servicios permanentes: {servicios_perm}")
                print(f"   Servicios spot: {servicios_spot}")

        print("\n")
        print("6. TOP 10 CLIENTES SPOT POR INGRESOS 2025")
        print("-" * 80)

        top_clientes = db.session.query(
            Cliente.nombre,
            Cliente.tipo,
            func.sum(IngresoMensual.ingreso_uf).label('total_ingresos')
        ).join(
            ServicioCliente, Cliente.id == ServicioCliente.cliente_id
        ).join(
            IngresoMensual, ServicioCliente.id == IngresoMensual.servicio_id
        ).filter(
            Cliente.tipo == 'spot',
            Cliente.activo == True,
            IngresoMensual.año == 2025
        ).group_by(
            Cliente.id
        ).order_by(
            func.sum(IngresoMensual.ingreso_uf).desc()
        ).limit(10).all()

        for idx, (nombre, tipo, total) in enumerate(top_clientes, 1):
            print(f"{idx:2d}. {nombre:40s} {total:10.2f} UF")

        print("\n")
        print("=" * 80)
        print("FIN DEL DIAGNÓSTICO")
        print("=" * 80)

if __name__ == '__main__':
    diagnosticar_ingresos_spot()
