"""
Diagnóstico completo de rentabilidad basado en archivos Excel fuente
Investiga los 4 problemas reportados por las socias
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Rutas a los archivos
BASE_DIR = Path('/Users/alfil/Desktop/Desarrollos/Comsulting')
CLIENTES_FILE = BASE_DIR / 'Cliente_Comsulting.xlsx'
HISTORIAL_FILE = BASE_DIR / 'Historial 2024-2025.xlsx'

# Constantes
VALOR_UF = 37513  # Pesos chilenos por UF (aproximado 2025)

def cargar_horas_2025():
    """Carga registros de horas de 2025"""
    print("📊 Cargando horas 2025...")

    df_horas = pd.read_excel(HISTORIAL_FILE, sheet_name='Horas')

    # Filtrar solo 2025
    df_horas['Date'] = pd.to_datetime(df_horas['Date'])
    df_2025 = df_horas[df_horas['anio'] == 2025].copy()

    print(f"  Total registros 2025: {len(df_2025)}")
    print(f"  Clientes únicos: {df_2025['Client'].nunique()}")
    print(f"  Personas únicas: {df_2025['First Name'].nunique()}")
    print(f"  Total horas: {df_2025['Hours'].sum():.1f}\n")

    return df_2025

def cargar_ingresos_2025():
    """Carga ingresos de clientes para 2025"""
    print("💰 Cargando ingresos 2025...")

    # Cargar clientes permanentes
    df_perm = pd.read_excel(CLIENTES_FILE, sheet_name='Permanentes')

    # Limpiar datos
    df_perm = df_perm.dropna(subset=['CLIENTES PERMANENTES'])
    df_perm = df_perm[df_perm['CLIENTES PERMANENTES'] != 'NaN']

    # Extraer ingresos de 2025 (columnas con fechas de 2025)
    cols_2025 = [col for col in df_perm.columns if isinstance(col, datetime) and col.year == 2025]

    ingresos_por_cliente = {}

    for _, row in df_perm.iterrows():
        cliente = str(row['CLIENTES PERMANENTES']).strip()
        if cliente and cliente not in ['NaN', 'nan']:
            # Sumar ingresos de todos los meses 2025
            ingresos_uf = sum(row[col] for col in cols_2025 if pd.notna(row[col]))
            if ingresos_uf > 0:
                ingresos_por_cliente[cliente] = ingresos_uf

    # Cargar clientes spot
    df_spot = pd.read_excel(CLIENTES_FILE, sheet_name='Spot')
    df_spot = df_spot.dropna(subset=['CLIENTES O SERVICIOS SPOT'])

    cols_2025_spot = [col for col in df_spot.columns if isinstance(col, datetime) and col.year == 2025]

    for _, row in df_spot.iterrows():
        cliente = str(row['CLIENTES O SERVICIOS SPOT']).strip()
        if cliente and cliente not in ['NaN', 'nan']:
            ingresos_uf = sum(row[col] for col in cols_2025_spot if pd.notna(row[col]))
            if ingresos_uf > 0:
                if cliente in ingresos_por_cliente:
                    ingresos_por_cliente[cliente] += ingresos_uf
                else:
                    ingresos_por_cliente[cliente] = ingresos_uf

    total_ingresos = sum(ingresos_por_cliente.values())
    print(f"  Clientes con ingresos: {len(ingresos_por_cliente)}")
    print(f"  Total ingresos 2025: {total_ingresos:.1f} UF\n")

    return ingresos_por_cliente

def calcular_costo_persona():
    """Calcula costo por hora de cada persona (estimado)"""
    # Costos estimados por cargo (UF/hora)
    costos_cargo = {
        'Socia': 2.5,
        'Director': 2.0,
        'Consultor Senior': 1.5,
        'Consultor': 1.2,
        'Analista Senior': 1.0,
        'Analista': 0.8
    }

    # Mapeo de nombres a cargos (basado en conocimiento del equipo)
    mapeo_personas = {
        'Blanca': 'Socia',
        'Macarena': 'Socia',
        'Carola': 'Director',
        'Jazmín': 'Director',
        'Paula': 'Consultor Senior',
        'Catalina': 'Consultor',
        'Antonia': 'Analista Senior',
        'María José': 'Analista',
        'María Jesús': 'Analista',
        'Constanza': 'Analista'
    }

    return mapeo_personas, costos_cargo

def analizar_rentabilidad():
    """Análisis completo de rentabilidad por cliente"""

    print("\n" + "="*100)
    print("🔍 DIAGNÓSTICO COMPLETO DE RENTABILIDAD - AÑO 2025")
    print("="*100 + "\n")

    # Cargar datos
    df_horas = cargar_horas_2025()
    ingresos_por_cliente = cargar_ingresos_2025()
    mapeo_personas, costos_cargo = calcular_costo_persona()

    # Calcular costos por cliente
    print("⚙️  Calculando costos por cliente...\n")

    costos_por_cliente = {}
    horas_por_cliente = {}

    for cliente in df_horas['Client'].unique():
        if pd.isna(cliente):
            continue

        df_cliente = df_horas[df_horas['Client'] == cliente]

        total_horas = df_cliente['Hours'].sum()
        total_costo_uf = 0

        for _, row in df_cliente.iterrows():
            nombre = row['First Name']
            horas = row['Hours']

            # Determinar cargo
            cargo = mapeo_personas.get(nombre, 'Analista')  # Default a Analista
            costo_hora_uf = costos_cargo.get(cargo, 1.0)

            total_costo_uf += horas * costo_hora_uf

        costos_por_cliente[cliente] = total_costo_uf
        horas_por_cliente[cliente] = total_horas

    # Análisis de rentabilidad
    print("="*100)
    print("📊 ANÁLISIS DE RENTABILIDAD POR CLIENTE (2025)")
    print("="*100 + "\n")

    resultados = []

    # Obtener todos los clientes (union de clientes con horas e ingresos)
    todos_clientes = set(list(costos_por_cliente.keys()) + list(ingresos_por_cliente.keys()))

    for cliente in todos_clientes:
        if not cliente or cliente in ['NaN', 'nan', None]:
            continue

        # Matching de nombres (algunos clientes pueden tener nombres ligeramente diferentes)
        cliente_clean = cliente.strip().upper()

        # Buscar ingresos
        ingresos_uf = 0
        for key in ingresos_por_cliente.keys():
            if key.strip().upper() == cliente_clean or cliente_clean in key.strip().upper() or key.strip().upper() in cliente_clean:
                ingresos_uf = ingresos_por_cliente[key]
                break

        # Costos
        costos_uf = costos_por_cliente.get(cliente, 0)
        horas = horas_por_cliente.get(cliente, 0)

        # Solo incluir si tiene ingresos o costos
        if ingresos_uf > 0 or costos_uf > 0:
            utilidad_uf = ingresos_uf - costos_uf
            margen = (utilidad_uf / ingresos_uf * 100) if ingresos_uf > 0 else -100

            resultados.append({
                'cliente': cliente,
                'ingresos_uf': ingresos_uf,
                'horas': horas,
                'costos_uf': costos_uf,
                'utilidad_uf': utilidad_uf,
                'margen': margen
            })

    # Ordenar por utilidad descendente
    resultados.sort(key=lambda x: x['utilidad_uf'], reverse=True)

    # Mostrar tabla
    print(f"{'#':<4} {'Cliente':<35} {'Ingresos (UF)':>15} {'Horas':>10} {'Costos (UF)':>15} {'Utilidad (UF)':>15} {'Margen %':>12}")
    print("-" * 110)

    total_ingresos = 0
    total_costos = 0
    total_utilidad = 0

    for i, r in enumerate(resultados, 1):
        color = "✅" if r['utilidad_uf'] > 0 else "❌"
        print(f"{color} {i:<2} {r['cliente']:<35} {r['ingresos_uf']:>13.1f} {r['horas']:>10.1f} {r['costos_uf']:>13.1f} {r['utilidad_uf']:>13.1f} {r['margen']:>11.1f}%")

        total_ingresos += r['ingresos_uf']
        total_costos += r['costos_uf']
        total_utilidad += r['utilidad_uf']

    margen_total = (total_utilidad / total_ingresos * 100) if total_ingresos > 0 else 0

    print("-" * 110)
    print(f"{'TOTAL':<40} {total_ingresos:>13.1f} {'':>10} {total_costos:>13.1f} {total_utilidad:>13.1f} {margen_total:>11.1f}%")

    # ANÁLISIS ESTADÍSTICO
    print("\n" + "="*100)
    print("📈 ANÁLISIS ESTADÍSTICO Y DIAGNÓSTICO")
    print("="*100 + "\n")

    clientes_positivos = [r for r in resultados if r['margen'] > 0]
    clientes_negativos = [r for r in resultados if r['margen'] <= 0]

    print(f"Total clientes analizados: {len(resultados)}")
    print(f"  ✅ Con margen positivo: {len(clientes_positivos)} ({len(clientes_positivos)/len(resultados)*100:.1f}%)")
    print(f"  ❌ Con margen negativo: {len(clientes_negativos)} ({len(clientes_negativos)/len(resultados)*100:.1f}%)\n")

    if clientes_positivos:
        margen_promedio_positivos = sum(r['margen'] for r in clientes_positivos) / len(clientes_positivos)
        print(f"Margen promedio clientes positivos: {margen_promedio_positivos:.1f}%")
        print(f"  Mayor margen: {max(r['margen'] for r in clientes_positivos):.1f}%")
        print(f"  Menor margen (positivo): {min(r['margen'] for r in clientes_positivos):.1f}%\n")

    print(f"⚠️  MARGEN TOTAL EMPRESA: {margen_total:.1f}%")
    print(f"    (Este margen considera solo costos directos de horas, NO overhead)\n")

    # PROBLEMA 1: Margen promedio vs individual
    print("="*100)
    print("🔍 PROBLEMA 1: Margen promedio ~70% reportado")
    print("="*100 + "\n")

    print(f"Margen total calculado: {margen_total:.1f}%")
    print(f"Margen promedio de clientes positivos: {margen_promedio_positivos:.1f}%\n")

    if margen_total > 60:
        print("⚠️  POSIBLE CAUSA: Falta incluir overhead en el cálculo")
        print("   Los costos actuales solo incluyen horas trabajadas (costos directos)")
        print("   NO incluyen: gastos operacionales, horas no imputadas, etc.\n")

    # PROBLEMA 2: Clientes con margen negativo
    print("="*100)
    print("🔍 PROBLEMA 2: EC, Falabella, Collahuasi con margen negativo")
    print("="*100 + "\n")

    clientes_a_verificar = ['EC', 'FALABELLA', 'COLLAHUASI']

    for nombre_buscar in clientes_a_verificar:
        cliente_encontrado = None
        for r in resultados:
            if nombre_buscar in r['cliente'].upper():
                cliente_encontrado = r
                break

        if cliente_encontrado:
            print(f"\n{cliente_encontrado['cliente']}:")
            print(f"  Ingresos: {cliente_encontrado['ingresos_uf']:.1f} UF")
            print(f"  Horas: {cliente_encontrado['horas']:.1f}h")
            print(f"  Costos: {cliente_encontrado['costos_uf']:.1f} UF")
            print(f"  Utilidad: {cliente_encontrado['utilidad_uf']:.1f} UF")
            print(f"  Margen: {cliente_encontrado['margen']:.1f}%")

            if cliente_encontrado['margen'] < 0:
                print(f"  ❌ PROBLEMA: Cliente a pérdida")

                # Diagnóstico
                if cliente_encontrado['ingresos_uf'] == 0:
                    print(f"     CAUSA: No hay ingresos registrados en 2025")
                    print(f"     ACCIÓN: Verificar si falta registrar ingresos en Excel 'Cliente_Comsulting.xlsx'")
                elif cliente_encontrado['costos_uf'] > cliente_encontrado['ingresos_uf']:
                    ratio = (cliente_encontrado['costos_uf'] / cliente_encontrado['ingresos_uf'] * 100) if cliente_encontrado['ingresos_uf'] > 0 else 0
                    print(f"     CAUSA: Costos ({cliente_encontrado['costos_uf']:.1f} UF) exceden ingresos")
                    print(f"     Costos representan {ratio:.1f}% de ingresos")
                    print(f"     ACCIÓN: Revisar si hay horas mal imputadas o si fee del cliente es muy bajo")
        else:
            print(f"\n⚠️  {nombre_buscar}: No encontrado en datos 2025")

    print("\n" + "="*100)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("="*100 + "\n")

    # Exportar resultados a Excel para revisión
    df_resultados = pd.DataFrame(resultados)
    output_file = BASE_DIR / 'AgentTracker' / 'diagnostico_rentabilidad_2025.xlsx'
    df_resultados.to_excel(output_file, index=False)
    print(f"📊 Resultados exportados a: {output_file}\n")

if __name__ == '__main__':
    analizar_rentabilidad()
