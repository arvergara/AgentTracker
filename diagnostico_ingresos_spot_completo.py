"""
Script de diagnóstico completo para identificar problemas de sobredimensionamiento en ingresos SPOT
"""
import os
from app import app, db, Cliente, ServicioCliente, IngresoMensual
from sqlalchemy import func, extract, distinct
from datetime import datetime

def diagnosticar_ingresos_spot():
    with app.app_context():
        print("=" * 80)
        print("DIAGNÓSTICO COMPLETO DE INGRESOS SPOT")
        print("=" * 80)
        print()

        # 0. Años disponibles en la base de datos
        print("0. AÑOS CON DATOS EN LA BASE DE DATOS")
        print("-" * 80)

        años_disponibles = db.session.query(
            distinct(IngresoMensual.año)
        ).order_by(IngresoMensual.año).all()

        años = [año[0] for año in años_disponibles]
        print(f"Años con ingresos registrados: {años}")
        print()

        if not años:
            print("⚠️  NO HAY DATOS DE INGRESOS EN LA BASE DE DATOS")
            return

        # Analizar para cada año
        for año_analisis in años:
            print("\n")
            print("=" * 80)
            print(f"ANÁLISIS AÑO {año_analisis}")
            print("=" * 80)

            # 1. Clientes SPOT con múltiples servicios
            print(f"\n1. CLIENTES SPOT CON MÚLTIPLES SERVICIOS ACTIVOS ({año_analisis})")
            print("-" * 80)

            clientes_spot = Cliente.query.filter_by(tipo='spot').all()
            clientes_con_problema = []

            for cliente in clientes_spot:
                servicios_activos = cliente.servicios.filter_by(activo=True).all()

                if len(servicios_activos) > 1:
                    clientes_con_problema.append(cliente)
                    print(f"\n⚠️  CLIENTE: {cliente.nombre}")
                    print(f"   Servicios activos: {len(servicios_activos)}")

                    total_cliente = 0
                    for servicio in servicios_activos:
                        ingresos_año = IngresoMensual.query.filter_by(
                            servicio_id=servicio.id,
                            año=año_analisis
                        ).all()

                        total_servicio = sum(i.ingreso_uf for i in ingresos_año)
                        total_cliente += total_servicio

                        print(f"   - Servicio ID {servicio.id}: {servicio.nombre if hasattr(servicio, 'nombre') else 'Sin nombre'}")
                        print(f"     Ingresos {año_analisis}: {total_servicio:.2f} UF")
                        print(f"     Meses con ingresos: {len(ingresos_año)}")

                        for ingreso in ingresos_año:
                            print(f"       {ingreso.año}-{ingreso.mes:02d}: {ingreso.ingreso_uf:.2f} UF")

                    print(f"\n   TOTAL SUMADO (este cliente): {total_cliente:.2f} UF")
                    print(f"   ⚠️  Si estos servicios representan el mismo trabajo, hay DUPLICACIÓN")

            if not clientes_con_problema:
                print("\n✓ No hay clientes spot con múltiples servicios activos")

            print("\n")
            print(f"2. COMPARACIÓN: TOTAL SPOT SEGÚN DASHBOARD VS SUMA REAL ({año_analisis})")
            print("-" * 80)

            # Cálculo según dashboard (suma todos los servicios) - ESTO ES LO QUE SE MUESTRA
            total_dashboard = 0
            for cliente in clientes_spot:
                servicios = cliente.servicios.filter_by(activo=True).all()
                for servicio in servicios:
                    ingresos_año = db.session.query(func.sum(IngresoMensual.ingreso_uf)).filter(
                        IngresoMensual.servicio_id == servicio.id,
                        IngresoMensual.año == año_analisis
                    ).scalar() or 0
                    total_dashboard += ingresos_año

            # Suma real (contando TODOS los IngresoMensual de clientes spot)
            total_real = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
                ServicioCliente
            ).join(
                Cliente
            ).filter(
                Cliente.tipo == 'spot',
                ServicioCliente.activo == True,
                IngresoMensual.año == año_analisis
            ).scalar() or 0

            # Suma por cliente único (evitando múltiples servicios)
            total_por_cliente = {}
            for cliente in clientes_spot:
                ingresos_cliente = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
                    ServicioCliente
                ).filter(
                    ServicioCliente.cliente_id == cliente.id,
                    ServicioCliente.activo == True,
                    IngresoMensual.año == año_analisis
                ).scalar() or 0

                if ingresos_cliente > 0:
                    total_por_cliente[cliente.nombre] = ingresos_cliente

            suma_por_cliente = sum(total_por_cliente.values())

            print(f"Total según lógica del dashboard (suma servicios): {total_dashboard:.2f} UF")
            print(f"Total real en BD (suma IngresoMensual):           {total_real:.2f} UF")
            print(f"Total por cliente único:                          {suma_por_cliente:.2f} UF")

            if total_dashboard > suma_por_cliente:
                print(f"\n❌ SOBREDIMENSIONAMIENTO DETECTADO: {total_dashboard - suma_por_cliente:.2f} UF")
                print(f"   Ratio: {total_dashboard/suma_por_cliente:.2f}x (está multiplicado)")
            elif total_dashboard == total_real == suma_por_cliente:
                print("\n✓ Los totales coinciden - no hay duplicación")

            # 3. Ingresos duplicados
            print("\n")
            print(f"3. INGRESOS DUPLICADOS (mismo servicio, año, mes) - {año_analisis}")
            print("-" * 80)

            duplicados = db.session.query(
                IngresoMensual.servicio_id,
                IngresoMensual.año,
                IngresoMensual.mes,
                func.count(IngresoMensual.id).label('count')
            ).filter(
                IngresoMensual.año == año_analisis
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

                    registros = IngresoMensual.query.filter_by(
                        servicio_id=dup.servicio_id,
                        año=dup.año,
                        mes=dup.mes
                    ).all()

                    print(f"\n   - Servicio ID {dup.servicio_id} ({cliente.nombre if cliente else 'N/A'})")
                    print(f"     {dup.año}-{dup.mes:02d}: {dup.count} registros")
                    print(f"     IDs duplicados: {[r.id for r in registros]}")
                    print(f"     Valores: {[r.ingreso_uf for r in registros]}")
            else:
                print("✓ No se encontraron duplicados")

            # 4. Desglose mensual
            print("\n")
            print(f"4. DESGLOSE MENSUAL DE INGRESOS SPOT {año_analisis}")
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
                ServicioCliente.activo == True,
                IngresoMensual.año == año_analisis
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

            print(f"\n{'TOTAL':12s}: {total_anual:10.2f} UF")

            # 5. TOP clientes
            print("\n")
            print(f"5. TOP 10 CLIENTES SPOT POR INGRESOS {año_analisis}")
            print("-" * 80)

            top_clientes = db.session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.tipo,
                func.count(distinct(ServicioCliente.id)).label('num_servicios'),
                func.sum(IngresoMensual.ingreso_uf).label('total_ingresos')
            ).join(
                ServicioCliente, Cliente.id == ServicioCliente.cliente_id
            ).join(
                IngresoMensual, ServicioCliente.id == IngresoMensual.servicio_id
            ).filter(
                Cliente.tipo == 'spot',
                IngresoMensual.año == año_analisis
            ).group_by(
                Cliente.id
            ).order_by(
                func.sum(IngresoMensual.ingreso_uf).desc()
            ).limit(10).all()

            for idx, (cliente_id, nombre, tipo, num_servicios, total) in enumerate(top_clientes, 1):
                marca = "⚠️ " if num_servicios > 1 else "  "
                print(f"{idx:2d}. {marca}{nombre:35s} {total:10.2f} UF (servicios: {num_servicios})")

        print("\n")
        print("=" * 80)
        print("6. RESUMEN DE TODOS LOS CLIENTES SPOT")
        print("=" * 80)

        todos_clientes_spot = db.session.query(
            Cliente.nombre,
            func.count(distinct(ServicioCliente.id)).label('num_servicios'),
            func.sum(IngresoMensual.ingreso_uf).label('total_ingresos')
        ).join(
            ServicioCliente, Cliente.id == ServicioCliente.cliente_id
        ).join(
            IngresoMensual, ServicioCliente.id == IngresoMensual.servicio_id
        ).filter(
            Cliente.tipo == 'spot'
        ).group_by(
            Cliente.id
        ).order_by(
            func.sum(IngresoMensual.ingreso_uf).desc()
        ).all()

        for nombre, num_servicios, total in todos_clientes_spot:
            marca = "⚠️ " if num_servicios > 1 else "✓ "
            print(f"{marca} {nombre:40s} {total:10.2f} UF (servicios: {num_servicios})")

        print("\n")
        print("=" * 80)
        print("FIN DEL DIAGNÓSTICO")
        print("=" * 80)

if __name__ == '__main__':
    diagnosticar_ingresos_spot()
