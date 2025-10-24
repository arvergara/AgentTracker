"""
Script para importar datos del análisis de matching (ene-sep 2025) a AgentTracker

Este script:
1. Inicializa la base de datos si no existe
2. Crea personas (equipo) con sus costos
3. Crea clientes consolidados (aplicando misma lógica de consolidación)
4. Importa registros de horas (Historial2024-2025.csv filtrado ene-sep 2025)
5. Importa ingresos mensuales (Clientes_Permanentes.csv y Clientes_Spot.csv)
"""

from app import app, db, Persona, Cliente, RegistroHora, ServicioCliente, IngresoMensual, Area, Servicio, Tarea
import pandas as pd
import hashlib
from datetime import datetime, date

# ============= CONSTANTES =============
VALOR_UF = 38000  # Pesos chilenos por UF
HORAS_EFECTIVAS_MES = 156
FECHA_INICIO = '2025-01-01'
FECHA_FIN = '2025-09-30'
MESES_INGRESOS = ['ene-25', 'feb-25', 'mar-25', 'abr-25', 'may-25', 'jun-25', 'jul-25', 'ago-25', 'sept-25']

# Mapeo de mes texto a número
MES_NUMERO = {
    'ene-25': 1, 'feb-25': 2, 'mar-25': 3, 'abr-25': 4, 'may-25': 5, 'jun-25': 6,
    'jul-25': 7, 'ago-25': 8, 'sept-25': 9
}

# Consolidación de clientes (misma lógica del análisis)
CONSOLIDACION_CLIENTES = {
    'CLÍNICAS': 'EBM',
    'ISAPRES': 'EBM',
    'PRESTADORES EBM': 'EBM',
    'CAPSTONE COPPER': 'CAPSTONE',
    'CAPSTONE MINNING CORP': 'CAPSTONE',
    'CAPSTONE': 'CAPSTONE',
    'MAE': 'MAE HOLDING CHILE SPA',
    'IQ SALMONES': 'ISIDORO QUIROGA',
    'LIBERTY': 'LIBERTY SEGUROS',
    'EMBAJADA ITALIA': 'EMBAJADA DE ITALIA',
}

def normalizar_nombre_cliente(nombre):
    """Normaliza nombre de cliente aplicando consolidación"""
    if pd.isna(nombre) or nombre == '':
        return None

    nombre = str(nombre).upper().strip()

    # Ignorar notas que no son clientes
    if 'A PARTIR DE' in nombre:
        return None

    nombre = nombre.replace('.', '').replace('  ', ' ')

    # Eliminar sufijos legales
    for sufijo in [' S.A', ' SA', ' SPA', ' LTDA', ' S.A.', ' HOLDING']:
        if nombre.endswith(sufijo):
            nombre = nombre[:-len(sufijo)].strip()

    # Aplicar consolidación
    if nombre in CONSOLIDACION_CLIENTES:
        nombre = CONSOLIDACION_CLIENTES[nombre]

    return nombre

def leer_costos_personal():
    """Lee costos de personal del archivo CSV"""
    print("\n📊 Leyendo costos de personal...")

    df = pd.read_csv('/Users/alfil/Desktop/Desarrollos/Comsulting/Costos_Personal.csv',
                     sep=';', encoding='utf-8-sig', skiprows=17, header=None)

    costos_personas = {}
    for idx, row in df.iterrows():
        nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
        costo_str = str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else None

        if nombre and costo_str and nombre != 'nan':
            try:
                costo = float(costo_str.replace('$', '').replace(',', '').replace(' ', '').strip())
                costos_personas[nombre] = costo
            except:
                pass

    print(f"   ✓ {len(costos_personas)} personas con costos identificados")
    return costos_personas

def procesar_ingresos_csv(archivo, tipo_cliente):
    """Procesa archivo de ingresos (permanentes o spot)"""
    df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig')

    ingresos = {}
    meses_cols = [col for col in df.columns if col in MESES_INGRESOS]
    cliente_actual = None

    for idx, row in df.iterrows():
        cliente_raw = row.iloc[0]

        # Saltar filas totales
        if pd.notna(cliente_raw):
            cliente_str = str(cliente_raw).strip().upper()
            if 'TOTAL' in cliente_str:
                continue

        # Si la fila tiene cliente, actualizamos cliente_actual
        if pd.notna(cliente_raw) and str(cliente_raw).strip() != '':
            cliente_actual = normalizar_nombre_cliente(cliente_raw)

        if not cliente_actual:
            continue

        # Sumar ingresos del período por mes
        for mes_col in meses_cols:
            if mes_col in row.index:
                valor = row[mes_col]
                if pd.notna(valor):
                    try:
                        valor_clean = str(valor).replace(',', '').strip()
                        if valor_clean and valor_clean != '-':
                            valor_uf = float(valor_clean)

                            if cliente_actual not in ingresos:
                                ingresos[cliente_actual] = {
                                    'tipo': tipo_cliente,
                                    'ingresos_mensuales': {}
                                }

                            if mes_col not in ingresos[cliente_actual]['ingresos_mensuales']:
                                ingresos[cliente_actual]['ingresos_mensuales'][mes_col] = 0

                            ingresos[cliente_actual]['ingresos_mensuales'][mes_col] += valor_uf
                    except:
                        pass

    return ingresos

def inicializar_sistema():
    """Inicializa el sistema completo con datos del matching"""

    with app.app_context():
        print("="*80)
        print("IMPORTACIÓN DE DATOS DEL MATCHING (ENE-SEP 2025)")
        print("="*80)

        # Paso 1: Crear esquema
        print("\n1. CREANDO/VERIFICANDO ESQUEMA DE BASE DE DATOS...")
        db.create_all()
        print("   ✓ Esquema verificado")

        # Paso 2: Crear áreas, servicios y tareas básicas
        print("\n2. CREANDO ÁREAS, SERVICIOS Y TAREAS BÁSICAS...")

        # Crear área genérica si no existe
        area_general = Area.query.filter_by(nombre='General').first()
        if not area_general:
            area_general = Area(nombre='General', activo=True)
            db.session.add(area_general)
            db.session.commit()
            print("   ✓ Área 'General' creada")

        # Crear servicio genérico si no existe
        servicio_general = Servicio.query.filter_by(nombre='Consultoría General').first()
        if not servicio_general:
            servicio_general = Servicio(
                area_id=area_general.id,
                nombre='Consultoría General',
                activo=True
            )
            db.session.add(servicio_general)
            db.session.commit()
            print("   ✓ Servicio 'Consultoría General' creado")

        # Crear tarea genérica si no existe
        tarea_general = Tarea.query.filter_by(nombre='Trabajo General').first()
        if not tarea_general:
            tarea_general = Tarea(
                servicio_id=servicio_general.id,
                nombre='Trabajo General',
                activo=True
            )
            db.session.add(tarea_general)
            db.session.commit()
            print("   ✓ Tarea 'Trabajo General' creada")

        # Paso 3: Cargar costos de personal
        costos_personas = leer_costos_personal()

        # Paso 4: Crear personas
        print("\n3. CREANDO PERSONAS DEL EQUIPO...")
        personas_db = {}
        password_hash = hashlib.sha256('comsulting2025'.encode()).hexdigest()

        for nombre, costo in costos_personas.items():
            persona = Persona.query.filter_by(nombre=nombre).first()
            if not persona:
                # Generar email
                partes = nombre.strip().split()
                if len(partes) >= 2:
                    inicial = partes[0][0].lower()
                    apellido = partes[-1].lower()
                    email = f"{inicial}{apellido}@comsulting.cl"
                else:
                    email = f"{nombre.lower().replace(' ', '')}@comsulting.cl"

                persona = Persona(
                    nombre=nombre,
                    email=email,
                    password_hash=password_hash,
                    cargo='Consultor',
                    es_socia=False,
                    es_admin=False,
                    activo=True,
                    costo_mensual_empresa=costo,
                    fecha_ingreso=date(2025, 1, 1)
                )
                db.session.add(persona)
                personas_db[nombre] = persona
            else:
                personas_db[nombre] = persona

        db.session.commit()
        print(f"   ✓ {len(personas_db)} personas creadas/verificadas")

        # Paso 5: Cargar ingresos
        print("\n4. PROCESANDO INGRESOS DE CLIENTES...")

        ingresos_permanentes = procesar_ingresos_csv(
            '/Users/alfil/Desktop/Desarrollos/Comsulting/Clientes_Permanentes.csv',
            'permanente'
        )
        print(f"   ✓ {len(ingresos_permanentes)} clientes permanentes")

        ingresos_spot = procesar_ingresos_csv(
            '/Users/alfil/Desktop/Desarrollos/Comsulting/Clientes_Spot.csv',
            'spot'
        )
        print(f"   ✓ {len(ingresos_spot)} clientes spot")

        # Combinar ingresos (permanentes + spot)
        ingresos_totales = {}
        for cliente, data in ingresos_permanentes.items():
            ingresos_totales[cliente] = data.copy()

        for cliente, data in ingresos_spot.items():
            if cliente in ingresos_totales:
                # Combinar ingresos mensuales
                for mes, valor in data['ingresos_mensuales'].items():
                    if mes not in ingresos_totales[cliente]['ingresos_mensuales']:
                        ingresos_totales[cliente]['ingresos_mensuales'][mes] = 0
                    ingresos_totales[cliente]['ingresos_mensuales'][mes] += valor
                ingresos_totales[cliente]['tipo'] = 'Permanente+Spot'
            else:
                ingresos_totales[cliente] = data.copy()

        # Paso 6: Crear clientes
        print("\n5. CREANDO CLIENTES CONSOLIDADOS...")
        clientes_db = {}

        for nombre_cliente, data in ingresos_totales.items():
            cliente = Cliente.query.filter_by(nombre=nombre_cliente).first()
            if not cliente:
                cliente = Cliente(
                    nombre=nombre_cliente,
                    tipo=data['tipo'].lower().replace('+', '_'),
                    activo=True
                )
                db.session.add(cliente)
                db.session.commit()

            clientes_db[nombre_cliente] = cliente

            # Crear servicio genérico para el cliente si no existe
            servicio_cliente = ServicioCliente.query.filter_by(
                cliente_id=cliente.id,
                nombre='Servicio General'
            ).first()

            if not servicio_cliente:
                servicio_cliente = ServicioCliente(
                    cliente_id=cliente.id,
                    nombre='Servicio General',
                    valor_mensual_uf=0,  # Se calculará de los ingresos mensuales
                    es_spot=(data['tipo'] == 'spot'),
                    activo=True
                )
                db.session.add(servicio_cliente)
                db.session.commit()

            # Crear ingresos mensuales
            for mes_texto, valor_uf in data['ingresos_mensuales'].items():
                mes_num = MES_NUMERO[mes_texto]

                ingreso = IngresoMensual.query.filter_by(
                    servicio_id=servicio_cliente.id,
                    año=2025,
                    mes=mes_num
                ).first()

                if not ingreso:
                    ingreso = IngresoMensual(
                        servicio_id=servicio_cliente.id,
                        año=2025,
                        mes=mes_num,
                        ingreso_uf=valor_uf
                    )
                    db.session.add(ingreso)
                else:
                    ingreso.ingreso_uf = valor_uf

        db.session.commit()
        print(f"   ✓ {len(clientes_db)} clientes consolidados creados/actualizados")

        # Paso 7: Importar registros de horas
        print("\n6. IMPORTANDO REGISTROS DE HORAS (ENE-SEP 2025)...")

        df_horas = pd.read_csv('/Users/alfil/Desktop/Desarrollos/Comsulting/Historial2024-2025.csv')
        df_horas['Date'] = pd.to_datetime(df_horas['Date'])

        # Filtrar por período
        df_horas = df_horas[
            (df_horas['Date'] >= FECHA_INICIO) &
            (df_horas['Date'] <= FECHA_FIN)
        ]

        # Convertir horas (formato europeo)
        df_horas['Hours'] = df_horas['Hours'].apply(
            lambda x: float(str(x).replace(',', '.')) if pd.notna(x) else 0
        )

        registros_creados = 0
        registros_omitidos = 0

        for idx, row in df_horas.iterrows():
            # Obtener persona
            nombre_completo = f"{row['First Name']} {row['Last Name']}"
            persona = personas_db.get(nombre_completo)

            if not persona:
                registros_omitidos += 1
                continue

            # Obtener cliente
            nombre_cliente = normalizar_nombre_cliente(row['Client'])
            if not nombre_cliente:
                registros_omitidos += 1
                continue

            cliente = clientes_db.get(nombre_cliente)
            if not cliente:
                # Crear cliente si no existe (puede ser interno)
                cliente = Cliente.query.filter_by(nombre=nombre_cliente).first()
                if not cliente:
                    cliente = Cliente(
                        nombre=nombre_cliente,
                        tipo='interno',
                        activo=True
                    )
                    db.session.add(cliente)
                    db.session.commit()
                    clientes_db[nombre_cliente] = cliente

            # Verificar si ya existe este registro
            existe = RegistroHora.query.filter_by(
                persona_id=persona.id,
                cliente_id=cliente.id,
                fecha=row['Date'].date(),
                horas=row['Hours']
            ).first()

            if not existe:
                registro = RegistroHora(
                    persona_id=persona.id,
                    cliente_id=cliente.id,
                    area_id=area_general.id,
                    servicio_id=servicio_general.id,
                    tarea_id=tarea_general.id,
                    fecha=row['Date'].date(),
                    horas=row['Hours'],
                    descripcion=row.get('Notes', '')
                )
                db.session.add(registro)
                registros_creados += 1

                # Commit cada 1000 registros para evitar problemas de memoria
                if registros_creados % 1000 == 0:
                    db.session.commit()
                    print(f"   ... {registros_creados} registros creados")

        db.session.commit()
        print(f"   ✓ {registros_creados} registros de horas importados")
        print(f"   ⚠ {registros_omitidos} registros omitidos (persona/cliente no encontrado)")

        # Resumen final
        print("\n" + "="*80)
        print("RESUMEN DE IMPORTACIÓN")
        print("="*80)
        print(f"Personas: {len(personas_db)}")
        print(f"Clientes: {len(clientes_db)}")
        print(f"Registros de horas: {registros_creados}")
        print(f"Período: Enero - Septiembre 2025")
        print("="*80)
        print("\n✅ Importación completada exitosamente")
        print("\nPuedes acceder al sistema en: http://localhost:5000")
        print("Usuario: cualquier email del equipo")
        print("Contraseña: comsulting2025")
        print()

if __name__ == '__main__':
    inicializar_sistema()
