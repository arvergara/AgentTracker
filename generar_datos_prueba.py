#!/usr/bin/env python3
"""
Script para generar datos de prueba realistas:
- 10 clientes variados
- 20 personas (periodistas y equipo)
- Proyectos múltiples por cliente
- Horas registradas en los últimos 3 meses
- Facturas asociadas a proyectos
"""

from app import app, db, Persona, Cliente, Proyecto, AsignacionProyecto, RegistroHora, Factura, Servicio, ValorUF
from datetime import datetime, timedelta
import random

def limpiar_base_datos():
    """Limpia todas las tablas"""
    print("🗑️  Limpiando base de datos...")
    db.drop_all()
    db.create_all()
    print("✅ Base de datos limpiada\n")

def crear_servicios():
    """Crea los servicios de Comsulting"""
    servicios_data = [
        ('Comunicaciones Externas', 'Externas'),
        ('Gestión de Crisis', 'Externas'),
        ('Talleres de vocería', 'Externas'),
        ('Monitoreo de medios', 'Externas'),
        ('Comunicaciones Internas', 'Internas'),
        ('Cultura organizacional', 'Internas'),
        ('Asuntos Públicos', 'Asuntos Públicos'),
        ('Relaciones gubernamentales', 'Asuntos Públicos'),
        ('Estrategia y gestión de redes', 'Redes sociales'),
        ('Monitoreo digital', 'Redes sociales'),
        ('Community management', 'Redes sociales'),
        ('Diseño gráfico', 'Diseño'),
        ('Diseño web', 'Diseño'),
        ('Producción audiovisual', 'Diseño'),
    ]

    print("📋 Creando servicios...")
    for nombre, area in servicios_data:
        servicio = Servicio(nombre=nombre, area=area)
        db.session.add(servicio)

    db.session.commit()
    print(f"✅ {len(servicios_data)} servicios creados\n")

def crear_personas():
    """Crea 20 personas del equipo"""
    personas_data = [
        # Socios
        ('María González', 'maria.gonzalez@comsulting.cl', 'Socia', 'full-time', 'Externas', 3.5, 150),
        ('Roberto Silva', 'roberto.silva@comsulting.cl', 'Socio', 'full-time', 'Asuntos Públicos', 3.5, 150),

        # Directores
        ('Carmen López', 'carmen.lopez@comsulting.cl', 'Directora', 'full-time', 'Externas', 2.8, 120),
        ('Fernando Rojas', 'fernando.rojas@comsulting.cl', 'Director', 'full-time', 'Internas', 2.8, 120),
        ('Patricia Mendoza', 'patricia.mendoza@comsulting.cl', 'Directora', 'full-time', 'Redes sociales', 2.5, 110),

        # Consultores Senior
        ('Juan Pérez', 'juan.perez@comsulting.cl', 'Consultor Senior', 'full-time', 'Externas', 2.0, 85),
        ('Ana Martínez', 'ana.martinez@comsulting.cl', 'Consultora Senior', 'full-time', 'Externas', 1.9, 82),
        ('Diego Torres', 'diego.torres@comsulting.cl', 'Consultor Senior', 'full-time', 'Asuntos Públicos', 2.0, 85),
        ('Sofía Vargas', 'sofia.vargas@comsulting.cl', 'Consultora Senior', 'full-time', 'Internas', 1.8, 80),

        # Consultores
        ('Andrés Contreras', 'andres.contreras@comsulting.cl', 'Consultor', 'full-time', 'Externas', 1.5, 65),
        ('Valentina Soto', 'valentina.soto@comsulting.cl', 'Consultora', 'full-time', 'Externas', 1.5, 65),
        ('Cristóbal Muñoz', 'cristobal.munoz@comsulting.cl', 'Consultor', 'full-time', 'Internas', 1.4, 62),
        ('Francisca Ramírez', 'francisca.ramirez@comsulting.cl', 'Consultora', 'full-time', 'Redes sociales', 1.6, 68),
        ('Matías Herrera', 'matias.herrera@comsulting.cl', 'Consultor', 'full-time', 'Asuntos Públicos', 1.5, 65),

        # Analistas
        ('Javiera Castro', 'javiera.castro@comsulting.cl', 'Analista', 'full-time', 'Externas', 1.2, 52),
        ('Benjamín Vera', 'benjamin.vera@comsulting.cl', 'Analista', 'full-time', 'Redes sociales', 1.2, 52),
        ('Isidora Parra', 'isidora.parra@comsulting.cl', 'Analista', 'full-time', 'Internas', 1.1, 50),

        # Diseño
        ('Luis Torres', 'luis.torres@comsulting.cl', 'Designer Senior', 'full-time', 'Diseño', 1.8, 78),
        ('Camila Espinoza', 'camila.espinoza@comsulting.cl', 'Designer', 'full-time', 'Diseño', 1.4, 60),

        # Media jornada
        ('Paula Núñez', 'paula.nunez@comsulting.cl', 'Consultora', 'media-jornada', 'Externas', 1.5, 65),
    ]

    print("👥 Creando equipo de 20 personas...")
    for nombre, email, cargo, jornada, area, costo, sueldo in personas_data:
        persona = Persona(
            nombre=nombre,
            email=email,
            cargo=cargo,
            tipo_jornada=jornada,
            area=area,
            costo_hora=costo,
            sueldo_mensual=sueldo
        )
        db.session.add(persona)

    db.session.commit()
    print(f"✅ {len(personas_data)} personas creadas\n")

def crear_clientes():
    """Crea 10 clientes variados"""
    clientes_data = [
        ('Banco Nacional', 'permanente', 'Externas'),
        ('Minera del Norte', 'permanente', 'Externas'),
        ('Retail Plus', 'permanente', 'Externas'),
        ('Compañía Eléctrica', 'permanente', 'Asuntos Públicos'),
        ('Municipalidad Central', 'permanente', 'Internas'),
        ('Startup Tech', 'spot', 'Redes sociales'),
        ('Inmobiliaria Global', 'spot', 'Externas'),
        ('ONG Ambiental', 'spot', 'Asuntos Públicos'),
        ('Universidad del Sur', 'permanente', 'Internas'),
        ('Comsulting', 'permanente', 'Diseño'),
    ]

    print("🏢 Creando 10 clientes...")
    fecha_base = datetime.now().date() - timedelta(days=365)

    for nombre, tipo, area in clientes_data:
        cliente = Cliente(
            nombre=nombre,
            tipo=tipo,
            area=area,
            fecha_inicio=fecha_base + timedelta(days=random.randint(0, 180))
        )
        db.session.add(cliente)

    db.session.commit()
    print(f"✅ {len(clientes_data)} clientes creados\n")

def crear_proyectos():
    """Crea 2-3 proyectos por cliente"""
    proyectos_config = [
        # Banco Nacional
        ('Banco Nacional', [
            ('Campaña Digital 2025', 'Comunicaciones Externas', 450, 18),
            ('Crisis Reputacional', 'Gestión de Crisis', 200, 12),
            ('Redes Sociales Corporativas', 'Estrategia y gestión de redes', 180, 20)
        ]),
        # Minera del Norte
        ('Minera del Norte', [
            ('Relaciones Comunitarias', 'Comunicaciones Externas', 380, 15),
            ('Asuntos Indígenas', 'Asuntos Públicos', 250, 14)
        ]),
        # Retail Plus
        ('Retail Plus', [
            ('Black Friday Campaign', 'Estrategia y gestión de redes', 320, 22),
            ('Comunicaciones Internas', 'Comunicaciones Internas', 150, 16)
        ]),
        # Compañía Eléctrica
        ('Compañía Eléctrica', [
            ('Lobby Regulatorio', 'Asuntos Públicos', 400, 13),
            ('Crisis Medioambiental', 'Gestión de Crisis', 280, 10)
        ]),
        # Municipalidad Central
        ('Municipalidad Central', [
            ('Plan de Comunicaciones 2025', 'Comunicaciones Internas', 220, 17),
            ('Participación Ciudadana', 'Comunicaciones Externas', 190, 15)
        ]),
        # Startup Tech
        ('Startup Tech', [
            ('Lanzamiento Producto', 'Estrategia y gestión de redes', 150, 25),
        ]),
        # Inmobiliaria Global
        ('Inmobiliaria Global', [
            ('Gestión de Crisis Legal', 'Gestión de Crisis', 180, 11),
            ('Campaña Nuevo Proyecto', 'Comunicaciones Externas', 200, 19)
        ]),
        # ONG Ambiental
        ('ONG Ambiental', [
            ('Campaña COP30', 'Asuntos Públicos', 160, 14),
        ]),
        # Universidad del Sur
        ('Universidad del Sur', [
            ('Comunicaciones Internas', 'Comunicaciones Internas', 240, 16),
            ('Posicionamiento Digital', 'Estrategia y gestión de redes', 180, 20)
        ]),
        # Comsulting
        ('Comsulting', [
            ('Diseño Corporativo 2025', 'Diseño gráfico', 120, 18),
        ])
    ]

    print("📁 Creando proyectos múltiples por cliente...")
    total_proyectos = 0

    for nombre_cliente, proyectos in proyectos_config:
        cliente = Cliente.query.filter_by(nombre=nombre_cliente).first()

        for i, (nombre_proy, servicio_nombre, presupuesto, margen) in enumerate(proyectos, 1):
            servicio = Servicio.query.filter_by(nombre=servicio_nombre).first()

            # Generar código único usando ID del cliente
            codigo = f"{cliente.nombre[:3].upper().replace(' ', '')}-{cliente.id:02d}-{i:02d}"

            fecha_inicio = datetime.now().date() - timedelta(days=random.randint(60, 150))
            fecha_fin = fecha_inicio + timedelta(days=random.randint(90, 270))

            # Determinar estado según fecha
            hoy = datetime.now().date()
            if fecha_fin < hoy:
                estado = 'cerrado'
            elif random.random() < 0.1:
                estado = 'pausado'
            else:
                estado = 'activo'

            proyecto = Proyecto(
                cliente_id=cliente.id,
                nombre=nombre_proy,
                codigo=codigo,
                servicio_id=servicio.id if servicio else None,
                tipo=cliente.tipo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                presupuesto_uf=presupuesto,
                estado=estado,
                descripcion=f"Proyecto de {servicio_nombre} para {cliente.nombre}",
                margen_objetivo=margen
            )
            db.session.add(proyecto)
            total_proyectos += 1

    db.session.commit()
    print(f"✅ {total_proyectos} proyectos creados\n")

def asignar_personas_proyectos():
    """Asigna personas a proyectos según área"""
    print("👥 Asignando personas a proyectos...")
    proyectos = Proyecto.query.all()
    total_asignaciones = 0

    for proyecto in proyectos:
        # Determinar área del proyecto
        area_proyecto = proyecto.cliente.area

        # Obtener personas del área
        personas_area = Persona.query.filter_by(area=area_proyecto, activo=True).all()

        # Asignar líder (Socio o Director)
        lideres = [p for p in personas_area if 'Socio' in p.cargo or 'Director' in p.cargo]
        if lideres:
            lider = random.choice(lideres)
            asignacion = AsignacionProyecto(
                persona_id=lider.id,
                proyecto_id=proyecto.id,
                rol_proyecto='lider',
                horas_estimadas=random.uniform(30, 80),
                costo_hora_proyecto=lider.costo_hora,
                fecha_inicio=proyecto.fecha_inicio,
                activo=True
            )
            db.session.add(asignacion)
            total_asignaciones += 1

        # Asignar 2-4 colaboradores
        num_colaboradores = random.randint(2, 4)
        colaboradores = [p for p in personas_area if 'Consultor' in p.cargo or 'Analista' in p.cargo]

        if colaboradores:
            for persona in random.sample(colaboradores, min(num_colaboradores, len(colaboradores))):
                asignacion = AsignacionProyecto(
                    persona_id=persona.id,
                    proyecto_id=proyecto.id,
                    rol_proyecto='colaborador',
                    horas_estimadas=random.uniform(40, 120),
                    costo_hora_proyecto=persona.costo_hora,
                    fecha_inicio=proyecto.fecha_inicio,
                    activo=True
                )
                db.session.add(asignacion)
                total_asignaciones += 1

        # Si hay diseñadores y el proyecto lo requiere, asignar
        if random.random() < 0.3:
            disenadores = Persona.query.filter_by(area='Diseño', activo=True).all()
            if disenadores:
                disenador = random.choice(disenadores)
                asignacion = AsignacionProyecto(
                    persona_id=disenador.id,
                    proyecto_id=proyecto.id,
                    rol_proyecto='soporte',
                    horas_estimadas=random.uniform(20, 50),
                    costo_hora_proyecto=disenador.costo_hora,
                    fecha_inicio=proyecto.fecha_inicio,
                    activo=True
                )
                db.session.add(asignacion)
                total_asignaciones += 1

    db.session.commit()
    print(f"✅ {total_asignaciones} asignaciones creadas\n")

def registrar_horas():
    """Registra horas para los últimos 90 días"""
    print("⏰ Registrando horas de los últimos 90 días...")
    proyectos = Proyecto.query.all()
    total_horas_registradas = 0

    for proyecto in proyectos:
        asignaciones = AsignacionProyecto.query.filter_by(proyecto_id=proyecto.id, activo=True).all()

        # Determinar días a registrar
        dias_proyecto = (proyecto.fecha_fin - proyecto.fecha_inicio).days
        dias_registro = min(90, dias_proyecto)

        for asignacion in asignaciones:
            persona = asignacion.persona

            # Calcular horas diarias aproximadas
            if persona.tipo_jornada == 'full-time':
                horas_dia_base = 6
            else:
                horas_dia_base = 3

            # Registrar horas aleatorias en días laborales
            for i in range(dias_registro):
                fecha = proyecto.fecha_inicio + timedelta(days=i)

                # Solo días laborales
                if fecha.weekday() < 5:
                    # No todos los días trabajan en todos los proyectos
                    if random.random() < 0.7:
                        horas = round(random.uniform(horas_dia_base * 0.5, horas_dia_base * 1.5), 1)

                        hora = RegistroHora(
                            persona_id=persona.id,
                            cliente_id=proyecto.cliente_id,
                            proyecto_id=proyecto.id,
                            fecha=fecha,
                            horas=horas,
                            descripcion=f"Trabajo en {proyecto.nombre}"
                        )
                        db.session.add(hora)
                        total_horas_registradas += horas

    db.session.commit()
    print(f"✅ {total_horas_registradas:.1f} horas registradas\n")

def crear_facturas():
    """Crea facturas para los proyectos"""
    print("💰 Creando facturas por proyecto...")
    proyectos = Proyecto.query.all()
    total_facturas = 0

    for proyecto in proyectos:
        # Determinar número de facturas según duración
        duracion_meses = max(1, (proyecto.fecha_fin - proyecto.fecha_inicio).days // 30)
        num_facturas = min(duracion_meses, random.randint(1, 4))

        # Calcular monto base de factura
        if proyecto.presupuesto_uf:
            monto_base = proyecto.presupuesto_uf / num_facturas
        else:
            monto_base = random.uniform(50, 200)

        for i in range(num_facturas):
            fecha_factura = proyecto.fecha_inicio + timedelta(days=30 * (i + 1))

            # Añadir variación al monto
            monto = round(monto_base * random.uniform(0.8, 1.2), 2)

            factura = Factura(
                cliente_id=proyecto.cliente_id,
                proyecto_id=proyecto.id,
                numero=f"F-{proyecto.codigo}-{i+1:02d}",
                fecha=fecha_factura,
                monto_uf=monto,
                pagada=fecha_factura < datetime.now().date()
            )
            db.session.add(factura)
            total_facturas += 1

    db.session.commit()
    print(f"✅ {total_facturas} facturas creadas\n")

def crear_valor_uf():
    """Crea valor UF actual"""
    uf = ValorUF(
        fecha=datetime.now().date(),
        valor=37500
    )
    db.session.add(uf)
    db.session.commit()
    print("✅ Valor UF establecido: $37,500\n")

def generar_reporte():
    """Genera reporte de datos creados"""
    print("=" * 80)
    print("📊 RESUMEN DE DATOS GENERADOS")
    print("=" * 80)

    print(f"\n👥 Personas: {Persona.query.count()}")
    print(f"   • Socios: {Persona.query.filter(Persona.cargo.like('%Socio%')).count()}")
    print(f"   • Directores: {Persona.query.filter(Persona.cargo.like('%Director%')).count()}")
    print(f"   • Consultores: {Persona.query.filter(Persona.cargo.like('%Consultor%')).count()}")
    print(f"   • Analistas: {Persona.query.filter(Persona.cargo.like('%Analista%')).count()}")
    print(f"   • Diseñadores: {Persona.query.filter(Persona.cargo.like('%Designer%')).count()}")

    print(f"\n🏢 Clientes: {Cliente.query.count()}")
    print(f"   • Permanentes: {Cliente.query.filter_by(tipo='permanente').count()}")
    print(f"   • Spot: {Cliente.query.filter_by(tipo='spot').count()}")

    print(f"\n📁 Proyectos: {Proyecto.query.count()}")
    print(f"   • Activos: {Proyecto.query.filter_by(estado='activo').count()}")
    print(f"   • Pausados: {Proyecto.query.filter_by(estado='pausado').count()}")
    print(f"   • Cerrados: {Proyecto.query.filter_by(estado='cerrado').count()}")

    print(f"\n👥 Asignaciones: {AsignacionProyecto.query.count()}")

    total_horas = db.session.query(db.func.sum(RegistroHora.horas)).scalar() or 0
    print(f"\n⏰ Horas Registradas: {total_horas:.1f}h")

    total_facturas_uf = db.session.query(db.func.sum(Factura.monto_uf)).scalar() or 0
    print(f"\n💰 Facturación Total: {total_facturas_uf:.2f} UF (${total_facturas_uf * 37500:,.0f})")
    print(f"   • Número de facturas: {Factura.query.count()}")

    print("\n" + "=" * 80)
    print("✅ DATOS DE PRUEBA GENERADOS EXITOSAMENTE")
    print("=" * 80)
    print("\n🚀 Inicia la aplicación con: python app.py")
    print("📊 Accede a: http://localhost:5000")
    print("\n")

def main():
    with app.app_context():
        print("\n" + "=" * 80)
        print("🎲 GENERADOR DE DATOS DE PRUEBA - COMSULTING")
        print("=" * 80)
        print("\nEste script creará:")
        print("  • 10 clientes variados")
        print("  • 20 personas (periodistas y equipo)")
        print("  • ~20 proyectos (2-3 por cliente)")
        print("  • Asignaciones persona-proyecto")
        print("  • ~3 meses de horas registradas")
        print("  • Facturas por proyecto")
        print("\n")

        respuesta = input("¿Deseas continuar? (s/n): ")

        if respuesta.lower() != 's':
            print("\n❌ Operación cancelada.\n")
            return

        print("\n")
        limpiar_base_datos()
        crear_servicios()
        crear_personas()
        crear_clientes()
        crear_proyectos()
        asignar_personas_proyectos()
        registrar_horas()
        crear_facturas()
        crear_valor_uf()
        generar_reporte()

if __name__ == '__main__':
    main()
