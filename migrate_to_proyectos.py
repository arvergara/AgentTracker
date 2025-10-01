#!/usr/bin/env python3
"""
Script de migración de datos existentes al modelo con Proyectos.

Estrategia:
1. Para cada Cliente existente, crear un Proyecto "General"
2. Migrar todos los RegistroHora del cliente al proyecto
3. Migrar todas las Facturas del cliente al proyecto
4. Crear AsignacionProyecto automática para cada persona que trabajó en el cliente
"""

from app import app, db, Cliente, Proyecto, RegistroHora, Factura, AsignacionProyecto, Persona
from datetime import datetime
from sqlalchemy import func

def generar_codigo_proyecto(cliente, numero=1):
    """Genera un código único para el proyecto"""
    # Tomar las primeras 3 letras del nombre del cliente
    prefijo = cliente.nombre[:3].upper().replace(' ', '')
    año = datetime.now().year
    return f"{prefijo}-GEN-{año}-{numero:02d}"

def migrar_datos():
    with app.app_context():
        print("=" * 80)
        print("INICIANDO MIGRACIÓN DE DATOS A MODELO CON PROYECTOS")
        print("=" * 80)

        # Verificar si ya existen proyectos
        proyectos_existentes = Proyecto.query.count()
        if proyectos_existentes > 0:
            respuesta = input(f"\n⚠️  Ya existen {proyectos_existentes} proyectos. ¿Continuar? (s/n): ")
            if respuesta.lower() != 's':
                print("Migración cancelada.")
                return

        clientes = Cliente.query.all()
        print(f"\n📊 Encontrados {len(clientes)} clientes para migrar\n")

        estadisticas = {
            'proyectos_creados': 0,
            'horas_migradas': 0,
            'facturas_migradas': 0,
            'asignaciones_creadas': 0
        }

        for cliente in clientes:
            print(f"\n{'─' * 80}")
            print(f"📁 Procesando cliente: {cliente.nombre}")

            # 1. CREAR PROYECTO GENERAL PARA EL CLIENTE
            numero = 1
            codigo = generar_codigo_proyecto(cliente, numero)

            # Verificar si el código ya existe
            while Proyecto.query.filter_by(codigo=codigo).first():
                numero += 1
                codigo = generar_codigo_proyecto(cliente, numero)

            # Calcular fechas del proyecto basadas en registros de horas
            primera_hora = RegistroHora.query.filter_by(cliente_id=cliente.id)\
                .order_by(RegistroHora.fecha.asc()).first()
            ultima_hora = RegistroHora.query.filter_by(cliente_id=cliente.id)\
                .order_by(RegistroHora.fecha.desc()).first()

            fecha_inicio = primera_hora.fecha if primera_hora else cliente.fecha_inicio
            fecha_fin = ultima_hora.fecha if ultima_hora else datetime.now().date()

            # Calcular presupuesto total basado en facturas
            presupuesto_total = db.session.query(func.sum(Factura.monto_uf))\
                .filter_by(cliente_id=cliente.id).scalar() or 0

            proyecto = Proyecto(
                cliente_id=cliente.id,
                nombre=f"Proyecto General {cliente.nombre}",
                codigo=codigo,
                tipo=cliente.tipo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                presupuesto_uf=presupuesto_total,
                estado='activo',
                descripcion=f"Proyecto migrado automáticamente desde cliente {cliente.nombre}"
            )

            db.session.add(proyecto)
            db.session.flush()  # Para obtener el ID del proyecto

            print(f"   ✅ Proyecto creado: {codigo} - {proyecto.nombre}")
            print(f"      Período: {fecha_inicio} a {fecha_fin}")
            print(f"      Presupuesto: {presupuesto_total:.2f} UF")

            estadisticas['proyectos_creados'] += 1

            # 2. MIGRAR REGISTROS DE HORAS
            horas_cliente = RegistroHora.query.filter_by(cliente_id=cliente.id).all()
            horas_actualizadas = 0

            for hora in horas_cliente:
                if not hora.proyecto_id:  # Solo migrar si no tiene proyecto asignado
                    hora.proyecto_id = proyecto.id
                    horas_actualizadas += 1

            print(f"   ✅ Horas migradas: {horas_actualizadas}")
            estadisticas['horas_migradas'] += horas_actualizadas

            # 3. MIGRAR FACTURAS
            facturas_cliente = Factura.query.filter_by(cliente_id=cliente.id).all()
            facturas_actualizadas = 0

            for factura in facturas_cliente:
                if not factura.proyecto_id:  # Solo migrar si no tiene proyecto asignado
                    factura.proyecto_id = proyecto.id
                    facturas_actualizadas += 1

            print(f"   ✅ Facturas migradas: {facturas_actualizadas}")
            estadisticas['facturas_migradas'] += facturas_actualizadas

            # 4. CREAR ASIGNACIONES DE PERSONAS AL PROYECTO
            # Obtener todas las personas que trabajaron en este cliente
            personas_query = db.session.query(
                RegistroHora.persona_id,
                func.sum(RegistroHora.horas).label('total_horas')
            ).filter(
                RegistroHora.cliente_id == cliente.id
            ).group_by(RegistroHora.persona_id).all()

            for persona_info in personas_query:
                persona = Persona.query.get(persona_info.persona_id)
                if persona:
                    # Determinar rol basado en cargo
                    rol = 'lider' if 'Socio' in persona.cargo or 'Director' in persona.cargo else 'colaborador'

                    asignacion = AsignacionProyecto(
                        persona_id=persona.id,
                        proyecto_id=proyecto.id,
                        rol_proyecto=rol,
                        horas_estimadas=persona_info.total_horas,
                        costo_hora_proyecto=persona.costo_hora,
                        fecha_inicio=fecha_inicio,
                        activo=True
                    )

                    db.session.add(asignacion)
                    estadisticas['asignaciones_creadas'] += 1
                    print(f"      → {persona.nombre} ({rol}): {persona_info.total_horas:.1f}h")

        # COMMIT FINAL
        try:
            db.session.commit()
            print("\n" + "=" * 80)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print(f"\n📊 Estadísticas:")
            print(f"   • Proyectos creados: {estadisticas['proyectos_creados']}")
            print(f"   • Horas migradas: {estadisticas['horas_migradas']}")
            print(f"   • Facturas migradas: {estadisticas['facturas_migradas']}")
            print(f"   • Asignaciones creadas: {estadisticas['asignaciones_creadas']}")
            print("\n✨ Los datos han sido migrados correctamente al nuevo modelo con Proyectos.\n")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR durante la migración: {e}")
            print("Se ha revertido la transacción.\n")
            raise

def validar_migracion():
    """Valida que la migración se haya completado correctamente"""
    with app.app_context():
        print("\n" + "=" * 80)
        print("VALIDANDO MIGRACIÓN")
        print("=" * 80)

        # Verificar que todos los RegistroHora tienen proyecto_id
        horas_sin_proyecto = RegistroHora.query.filter_by(proyecto_id=None).count()
        print(f"\n✓ Horas sin proyecto asignado: {horas_sin_proyecto}")

        # Verificar que todas las Facturas tienen proyecto_id (opcional)
        facturas_sin_proyecto = Factura.query.filter_by(proyecto_id=None).count()
        print(f"✓ Facturas sin proyecto asignado: {facturas_sin_proyecto}")

        # Verificar total de proyectos
        total_proyectos = Proyecto.query.count()
        print(f"✓ Total de proyectos: {total_proyectos}")

        # Verificar total de asignaciones
        total_asignaciones = AsignacionProyecto.query.count()
        print(f"✓ Total de asignaciones: {total_asignaciones}")

        # Comparar totales antes y después
        total_horas_original = db.session.query(func.sum(RegistroHora.horas)).scalar() or 0
        total_horas_proyecto = db.session.query(func.sum(RegistroHora.horas))\
            .filter(RegistroHora.proyecto_id.isnot(None)).scalar() or 0

        print(f"\n✓ Total horas en sistema: {total_horas_original:.2f}h")
        print(f"✓ Total horas con proyecto: {total_horas_proyecto:.2f}h")

        if horas_sin_proyecto == 0:
            print("\n✅ Validación exitosa: Todos los registros de horas tienen proyecto asignado")
        else:
            print(f"\n⚠️  Advertencia: {horas_sin_proyecto} registros de horas sin proyecto")

        print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    print("\n🚀 Script de Migración a Modelo con Proyectos\n")
    print("Este script:")
    print("  1. Crea un proyecto 'General' por cada cliente existente")
    print("  2. Migra todos los registros de horas al proyecto")
    print("  3. Migra todas las facturas al proyecto")
    print("  4. Crea asignaciones automáticas de personas a proyectos")
    print("\n⚠️  IMPORTANTE: Realiza un backup de la base de datos antes de continuar.\n")

    respuesta = input("¿Deseas continuar con la migración? (s/n): ")

    if respuesta.lower() == 's':
        migrar_datos()
        validar_migracion()
    else:
        print("\nMigración cancelada.\n")
