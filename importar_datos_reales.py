#!/usr/bin/env python3
"""
Script para importar datos reales de Comsulting desde CSV
- Costos_Personal.csv -> Tabla personas
- Cliente_Comsulting.csv -> Tabla clientes y proyectos
"""

import csv
import re
from datetime import datetime
from app import app, db, Persona, Cliente, Proyecto, Servicio, ValorUF

# Valor UF actual
VALOR_UF_ACTUAL = 37500

def limpiar_monto(valor_str):
    """Convierte string con formato $1,234,567 a número"""
    if not valor_str or valor_str.strip() == '':
        return 0
    # Remover $, espacios y comas
    limpio = re.sub(r'[\$\s,]', '', valor_str.strip())
    try:
        return float(limpio)
    except:
        return 0

def calcular_costo_hora_uf(costo_mensual_pesos):
    """Calcula costo por hora en UF"""
    if costo_mensual_pesos <= 0:
        return 0
    # 156 horas efectivas al mes
    costo_hora_pesos = costo_mensual_pesos / 156
    costo_hora_uf = costo_hora_pesos / VALOR_UF_ACTUAL
    return round(costo_hora_uf, 4)

def determinar_cargo(nombre, costo_mensual):
    """Determina el cargo según el costo mensual"""
    if costo_mensual >= 7000000:
        return "Socia"
    elif costo_mensual >= 5500000:
        return "Directora"
    elif costo_mensual >= 3800000:
        return "Consultora Senior"
    elif costo_mensual >= 2500000:
        return "Consultora"
    else:
        return "Analista"

def determinar_area(nombre):
    """Determina el área según el nombre (puedes personalizar)"""
    # Por defecto, todas en Externas (puedes ajustar manualmente después)
    areas = {
        'Blanca': 'Dirección',
        'María Macarena': 'Dirección',
        'Bernardita': 'Externas',
        'Carolina Romero': 'Externas',
        'Nicolás': 'Asuntos Públicos',
        'Isabel': 'Internas',
        'Erick': 'Digital',
        'Raúl': 'Redes sociales',
        'María De Los Ángeles': 'Externas',
        'Constanza': 'Externas',
        'Andrea': 'Internas',
        'Juana': 'Externas',
        'Enrique': 'Asuntos Públicos',
        'Jazmín': 'Redes sociales',
    }

    for key, area in areas.items():
        if key in nombre:
            return area

    return 'Externas'  # Default

def importar_personal():
    """Importa personal desde Costos_Personal.csv"""
    print("\n=== IMPORTANDO PERSONAL ===")

    archivo_csv = '/Users/alfil/Library/CloudStorage/GoogleDrive-andres.vergara@maindset.cl/Mi unidad/Comsulting/Costos_Personal.csv'

    personas_importadas = 0

    with open(archivo_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            nombre = row.get('Nombre', '').strip()

            # Saltar filas vacías o de encabezado
            if not nombre or nombre == '' or 'Nombre' in nombre:
                continue

            # Obtener costo total mensual
            costo_total_str = row.get('Costo total\nmensual\nempresa', '').strip()
            costo_mensual = limpiar_monto(costo_total_str)

            if costo_mensual == 0:
                print(f"⚠️  Saltando {nombre} - sin costo")
                continue

            # Calcular datos
            cargo = determinar_cargo(nombre, costo_mensual)
            area = determinar_area(nombre)
            costo_hora_uf = calcular_costo_hora_uf(costo_mensual)
            sueldo_uf = round(costo_mensual / VALOR_UF_ACTUAL, 2)

            # Generar email
            partes_nombre = nombre.split()
            if len(partes_nombre) >= 2:
                email = f"{partes_nombre[0].lower()}.{partes_nombre[-1].lower()}@comsulting.cl"
            else:
                email = f"{nombre.lower().replace(' ', '.')}@comsulting.cl"

            # Crear persona
            persona = Persona(
                nombre=nombre,
                email=email,
                cargo=cargo,
                area=area,
                tipo_jornada='full-time',
                costo_hora=costo_hora_uf,
                sueldo_mensual=sueldo_uf,
                activo=True
            )

            db.session.add(persona)
            personas_importadas += 1

            print(f"✅ {nombre:35} | {cargo:20} | {area:20} | ${costo_mensual:>12,.0f} | {costo_hora_uf:.4f} UF/h")

    db.session.commit()
    print(f"\n✅ Total personas importadas: {personas_importadas}")
    return personas_importadas

def importar_clientes():
    """Importa clientes y proyectos desde Cliente_Comsulting.csv"""
    print("\n=== IMPORTANDO CLIENTES Y PROYECTOS ===")

    archivo_csv = '/Users/alfil/Library/CloudStorage/GoogleDrive-andres.vergara@maindset.cl/Mi unidad/Comsulting/Cliente_Comsulting.csv'

    clientes_importados = 0
    proyectos_importados = 0

    cliente_actual = None
    tipo_actual = 'permanente'

    with open(archivo_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')

        for row in reader:
            if not row or len(row) < 3:
                continue

            # Obtener columnas
            col0 = row[0].strip() if row[0] else ''
            col1 = row[1].strip() if len(row) > 1 and row[1] else ''
            col2 = row[2].strip() if len(row) > 2 and row[2] else ''

            # Saltar primeras filas de encabezado
            if 'Fee Especifico' in col1 or 'FEE MENSUAL' in col1:
                continue

            # Detectar tipo de cliente
            if 'CLIENTES PERMANENTES' in col0.upper():
                tipo_actual = 'permanente'
                continue
            elif 'SPOT' in col0.upper():
                tipo_actual = 'spot'
                continue

            # Si hay un nombre de cliente (columna 0 tiene valor y columna 1 tiene descripción)
            if col0 and col1 and ('Asesor' in col1 or 'Comunicacion' in col1 or 'Monitoreo' in col1):
                # Es un cliente nuevo
                fee = limpiar_monto(col2)

                if fee > 0:
                    # Determinar área
                    area = 'Externas'
                    if 'AFP' in col0 or 'Isapre' in col1 or 'EBM' in col0:
                        area = 'Internas'
                    elif 'FRUTAS' in col0 or 'Asuntos' in col1:
                        area = 'Asuntos Públicos'
                    elif 'Digital' in col1 or 'RRSS' in col1:
                        area = 'Digital'

                    cliente = Cliente(
                        nombre=col0,
                        tipo=tipo_actual,
                        area=area,
                        activo=True,
                        fecha_inicio=datetime(2025, 1, 1).date()
                    )
                    db.session.add(cliente)
                    db.session.flush()

                    cliente_actual = cliente
                    clientes_importados += 1

                    # Crear proyecto principal
                    nombre_proyecto = col1.split('UF')[0].strip()
                    codigo_base = col0[:3].upper()
                    codigo_proyecto = f"{codigo_base}-{clientes_importados:02d}-01"

                    proyecto = Proyecto(
                        cliente_id=cliente.id,
                        codigo=codigo_proyecto,
                        nombre=nombre_proyecto,
                        tipo=tipo_actual,
                        estado='activo',
                        fecha_inicio=datetime(2025, 1, 1).date(),
                        presupuesto_uf=fee * 12,
                        margen_objetivo=12.5
                    )
                    db.session.add(proyecto)
                    proyectos_importados += 1

                    print(f"✅ {col0:30} | {tipo_actual:12} | {area:15} | {fee:.1f} UF/mes")

            # Si es un servicio adicional del cliente actual (col0 vacío, col1 tiene descripción)
            elif not col0 and col1 and cliente_actual:
                fee = limpiar_monto(col2)

                if fee > 0:
                    # Crear proyecto adicional
                    nombre_servicio = col1.split('UF')[0].strip()
                    codigo_base = cliente_actual.nombre[:3].upper()
                    # Usar timestamp para garantizar unicidad
                    import time
                    codigo = f"{codigo_base}-{clientes_importados:02d}-{proyectos_importados:03d}"

                    proyecto = Proyecto(
                        cliente_id=cliente_actual.id,
                        codigo=codigo,
                        nombre=nombre_servicio[:100],
                        tipo=cliente_actual.tipo,
                        estado='activo',
                        fecha_inicio=datetime(2025, 1, 1).date(),
                        presupuesto_uf=fee * 12,
                        margen_objetivo=12.5
                    )
                    db.session.add(proyecto)
                    proyectos_importados += 1
                    print(f"   └─ {nombre_servicio[:45]:45} | {fee:.1f} UF/mes")

    db.session.commit()
    print(f"\n✅ Total clientes importados: {clientes_importados}")
    print(f"✅ Total proyectos importados: {proyectos_importados}")
    return clientes_importados, proyectos_importados

def crear_servicios_base():
    """Crea servicios base de Comsulting"""
    print("\n=== CREANDO SERVICIOS BASE ===")

    servicios = [
        {'nombre': 'Asesoría Comunicacional', 'area': 'Externas'},
        {'nombre': 'Gestión de Crisis', 'area': 'Externas'},
        {'nombre': 'Comunicaciones Internas', 'area': 'Internas'},
        {'nombre': 'Estrategia y gestión de redes sociales', 'area': 'Redes sociales'},
        {'nombre': 'Monitoreo Digital', 'area': 'Digital'},
        {'nombre': 'Diseño Gráfico', 'area': 'Diseño'},
        {'nombre': 'Asuntos Públicos', 'area': 'Asuntos Públicos'},
        {'nombre': 'Talleres de Vocería', 'area': 'Externas'},
    ]

    for serv_data in servicios:
        servicio = Servicio(
            nombre=serv_data['nombre'],
            area=serv_data['area']
        )
        db.session.add(servicio)
        print(f"✅ {serv_data['nombre']:35} | {serv_data['area']}")

    db.session.commit()
    print(f"\n✅ Total servicios creados: {len(servicios)}")

def actualizar_valor_uf():
    """Actualiza el valor UF actual"""
    print("\n=== ACTUALIZANDO VALOR UF ===")

    # Eliminar valores UF anteriores
    ValorUF.query.delete()

    # Crear nuevo valor UF
    uf = ValorUF(
        fecha=datetime.now().date(),
        valor=VALOR_UF_ACTUAL
    )
    db.session.add(uf)
    db.session.commit()

    print(f"✅ Valor UF actualizado: ${VALOR_UF_ACTUAL:,}")

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("IMPORTACIÓN DE DATOS REALES DE COMSULTING")
    print("="*70)

    respuesta = input("\n⚠️  ADVERTENCIA: Esto eliminará todos los datos existentes.\n¿Continuar? (si/no): ")

    if respuesta.lower() != 'si':
        print("❌ Importación cancelada")
        return

    with app.app_context():
        print("\n🗑️  Eliminando datos anteriores...")

        # Eliminar en orden (respetando foreign keys)
        from app import RegistroHora, AsignacionProyecto, Factura

        RegistroHora.query.delete()
        AsignacionProyecto.query.delete()
        Factura.query.delete()
        Proyecto.query.delete()
        Cliente.query.delete()
        Persona.query.delete()
        Servicio.query.delete()
        ValorUF.query.delete()

        db.session.commit()
        print("✅ Datos anteriores eliminados")

        # Importar datos reales
        actualizar_valor_uf()
        personas = importar_personal()
        clientes, proyectos = importar_clientes()
        crear_servicios_base()

        print("\n" + "="*70)
        print("RESUMEN DE IMPORTACIÓN")
        print("="*70)
        print(f"✅ Personas importadas: {personas}")
        print(f"✅ Clientes importados: {clientes}")
        print(f"✅ Proyectos creados: {proyectos}")
        print(f"✅ Servicios creados: 8")
        print(f"✅ Valor UF: ${VALOR_UF_ACTUAL:,}")
        print("\n🎉 Importación completada exitosamente!")
        print("\nPróximos pasos:")
        print("1. Reinicia la aplicación: python app.py")
        print("2. Accede a http://localhost:5001")
        print("3. Asigna personas a proyectos")
        print("4. Registra horas trabajadas")

if __name__ == '__main__':
    main()
