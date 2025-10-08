from app import app, db, Area, Servicio, Tarea, Cliente, ServicioCliente

with app.app_context():
    print("="*60)
    print("ESTRUCTURA DE DATOS")
    print("="*60)

    # Verificar Áreas y Servicios (nuevo sistema)
    print("\n📁 ÁREAS Y SERVICIOS (nuevo sistema):")
    areas = Area.query.all()
    for area in areas:
        print(f"\n  {area.nombre}:")
        servicios = area.servicios.all()
        for servicio in servicios:
            tareas_count = servicio.tareas.count()
            print(f"    - {servicio.nombre} ({tareas_count} tareas)")

    # Verificar Clientes (sistema antiguo para rentabilidad)
    print("\n\n💼 CLIENTES (para rentabilidad):")
    clientes = Cliente.query.all()
    for cliente in clientes:
        servicios_cliente = cliente.servicios.all()
        print(f"  - {cliente.nombre} ({len(servicios_cliente)} servicios)")
        for sc in servicios_cliente[:3]:  # Mostrar máximo 3
            print(f"      • {sc.nombre}: {sc.valor_mensual_uf} UF/mes")

    print("\n" + "="*60)
