"""
Script para consolidar clientes duplicados
Resuelve el problema de Falabella, Collahuasi, COPEC apareciendo con margen negativo

IMPORTANTE: Ejecutar en producción (Render PostgreSQL)
"""

from app import app, db, Cliente, RegistroHora, IngresoMensual, ServicioCliente
from sqlalchemy import func

def normalizar_nombre_cliente(nombre):
    """Normaliza nombres de clientes para matching correcto"""
    if not nombre:
        return None

    nombre = nombre.strip().upper()

    # Remover sufijos comunes
    sufijos = [' S.A.', ' S.A', ' SPA', ' LTDA', ' S.P.A.', ' SA', ' LTDA.']
    for sufijo in sufijos:
        if nombre.endswith(sufijo):
            nombre = nombre[:-len(sufijo)].strip()

    return nombre

def consolidar_clientes():
    """Consolida clientes duplicados en la base de datos"""

    with app.app_context():
        print("\n" + "="*80)
        print("🔄 CONSOLIDACIÓN DE CLIENTES DUPLICADOS")
        print("="*80 + "\n")

        # Definir duplicados conocidos
        # (nombre_incorrecto, nombre_correcto)
        duplicados = [
            ('FALABELLA S.A.', 'Falabella'),
            ('FALABELLA SA', 'Falabella'),
            ('Falabella S.A.', 'Falabella'),

            ('COLLAHUASI', 'Collahuasi'),

            ('Empresas COPEC', 'EMPRESAS COPEC'),
            ('COPEC', 'EMPRESAS COPEC'),

            ('CAPSTONE MINNING CORP', 'Capstone Copper'),
            ('Capstone Minning Corp', 'Capstone Copper'),
            ('CAPSTONE', 'Capstone Copper'),
            ('Capstone', 'Capstone Copper'),

            ('AFP MODELO', 'AFP Modelo'),

            ('MAE HOLDING CHILE SPA', 'MAE'),
            ('MAE HOLDING', 'MAE'),

            ('OXZO S.A', 'OXZO'),
            ('OXZO S.A.', 'OXZO'),

            ('EMBAJADA ITALIA', 'Embajada de Italia'),
            ('EMBAJADA DE ITALIA', 'Embajada de Italia'),
        ]

        print("📋 PASO 1: Clientes a consolidar\n")
        for incorrecto, correcto in duplicados:
            print(f"  - '{incorrecto}' → '{correcto}'")

        print(f"\n  Total: {len(duplicados)} consolidaciones\n")

        # 2. Ejecutar consolidación
        print("🔀 PASO 2: Ejecutando consolidación...\n")

        consolidados = 0
        errores = 0

        for nombre_incorrecto, nombre_correcto in duplicados:
            try:
                # Buscar clientes
                cliente_incorrecto = Cliente.query.filter(
                    func.upper(Cliente.nombre) == nombre_incorrecto.upper()
                ).first()

                cliente_correcto = Cliente.query.filter(
                    func.upper(Cliente.nombre) == nombre_correcto.upper()
                ).first()

                if not cliente_incorrecto:
                    print(f"  ⚠️  Cliente '{nombre_incorrecto}' no encontrado, saltando...")
                    continue

                if not cliente_correcto:
                    # Si el cliente correcto no existe, renombrar el incorrecto
                    print(f"  🔄 Renombrando '{cliente_incorrecto.nombre}' → '{nombre_correcto}'")
                    cliente_incorrecto.nombre = nombre_correcto
                    consolidados += 1
                    continue

                # Si ambos existen, consolidar
                print(f"  🔀 Consolidando '{nombre_incorrecto}' → '{nombre_correcto}'...")

                # Mover registros de horas
                horas_movidas = RegistroHora.query.filter_by(
                    cliente_id=cliente_incorrecto.id
                ).update({'cliente_id': cliente_correcto.id})

                print(f"     - {horas_movidas} registros de horas movidos")

                # Mover servicios del cliente
                servicios_movidos = ServicioCliente.query.filter_by(
                    cliente_id=cliente_incorrecto.id
                ).count()

                if servicios_movidos > 0:
                    # Mover ingresos mensuales asociados a servicios
                    servicios_incorrectos = ServicioCliente.query.filter_by(
                        cliente_id=cliente_incorrecto.id
                    ).all()

                    for servicio in servicios_incorrectos:
                        # Verificar si ya existe un servicio similar en el cliente correcto
                        servicio_existente = ServicioCliente.query.filter_by(
                            cliente_id=cliente_correcto.id,
                            nombre=servicio.nombre
                        ).first()

                        if servicio_existente:
                            # Mover ingresos al servicio existente
                            IngresoMensual.query.filter_by(
                                servicio_id=servicio.id
                            ).update({'servicio_id': servicio_existente.id})

                            # Marcar servicio duplicado como inactivo
                            servicio.activo = False
                        else:
                            # Mover servicio al cliente correcto
                            servicio.cliente_id = cliente_correcto.id

                    print(f"     - {servicios_movidos} servicios procesados")

                # Marcar cliente incorrecto como inactivo
                cliente_incorrecto.activo = False
                print(f"     - Cliente '{nombre_incorrecto}' marcado como inactivo")

                consolidados += 1

            except Exception as e:
                print(f"  ❌ Error consolidando '{nombre_incorrecto}': {str(e)}")
                errores += 1
                db.session.rollback()
                continue

        # Commit todos los cambios
        db.session.commit()

        # 3. Verificar resultados
        print("\n📊 PASO 3: Verificación de resultados...\n")

        print("Clientes consolidados:")
        for _, nombre_correcto in set([(i, c) for i, c in duplicados]):
            cliente = Cliente.query.filter(
                func.upper(Cliente.nombre) == nombre_correcto.upper()
            ).first()

            if cliente:
                horas = db.session.query(func.sum(RegistroHora.horas)).filter(
                    RegistroHora.cliente_id == cliente.id
                ).scalar() or 0

                servicios = ServicioCliente.query.filter_by(
                    cliente_id=cliente.id,
                    activo=True
                ).count()

                ingresos = db.session.query(func.sum(IngresoMensual.ingreso_uf)).join(
                    ServicioCliente
                ).filter(
                    ServicioCliente.cliente_id == cliente.id,
                    IngresoMensual.año == 2025
                ).scalar() or 0

                print(f"  ✅ {cliente.nombre}:")
                print(f"     - Horas totales: {horas:.1f}h")
                print(f"     - Servicios activos: {servicios}")
                print(f"     - Ingresos 2025: {ingresos:.1f} UF")

        print("\n" + "="*80)
        print("✅ CONSOLIDACIÓN COMPLETADA")
        print("="*80 + "\n")

        print("📋 RESUMEN:")
        print(f"  - Clientes consolidados: {consolidados}")
        print(f"  - Errores: {errores}\n")

        if errores > 0:
            print("⚠️  Revisar errores arriba para verificar qué consolidaciones fallaron\n")

def listar_posibles_duplicados():
    """Busca clientes potencialmente duplicados por similitud de nombres"""

    with app.app_context():
        print("\n" + "="*80)
        print("🔍 BÚSQUEDA DE POSIBLES DUPLICADOS")
        print("="*80 + "\n")

        clientes = Cliente.query.filter_by(activo=True).all()

        # Agrupar por nombre normalizado
        clientes_normalizados = {}

        for cliente in clientes:
            nombre_norm = normalizar_nombre_cliente(cliente.nombre)

            if nombre_norm not in clientes_normalizados:
                clientes_normalizados[nombre_norm] = []

            clientes_normalizados[nombre_norm].append(cliente)

        # Mostrar duplicados potenciales
        duplicados_encontrados = 0

        for nombre_norm, clientes_grupo in clientes_normalizados.items():
            if len(clientes_grupo) > 1:
                duplicados_encontrados += 1
                print(f"\n⚠️  Posible duplicado: {nombre_norm}")
                for cliente in clientes_grupo:
                    horas = db.session.query(func.sum(RegistroHora.horas)).filter(
                        RegistroHora.cliente_id == cliente.id
                    ).scalar() or 0

                    print(f"  - '{cliente.nombre}' (ID: {cliente.id}) - {horas:.1f} horas")

        if duplicados_encontrados == 0:
            print("✅ No se encontraron duplicados potenciales\n")
        else:
            print(f"\n📋 Total grupos de duplicados encontrados: {duplicados_encontrados}\n")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--listar':
        listar_posibles_duplicados()
    else:
        print("\n⚠️  ADVERTENCIA: Este script modificará la base de datos en producción.")
        print("    Asegúrate de haber hecho un backup antes de continuar.\n")

        print("Opciones:")
        print("  1. Consolidar clientes duplicados conocidos")
        print("  2. Listar posibles duplicados")
        print("  3. Cancelar\n")

        opcion = input("Selecciona una opción (1/2/3): ")

        if opcion == '1':
            confirm = input("\n¿Confirmas ejecutar la consolidación? (yes/no): ")
            if confirm.lower() == 'yes':
                consolidar_clientes()
            else:
                print("Consolidación cancelada")
        elif opcion == '2':
            listar_posibles_duplicados()
        else:
            print("Operación cancelada")
