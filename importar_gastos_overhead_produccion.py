"""
Script para importar GASTOS OVERHEAD desde Flujo de Caja 2025 a PostgreSQL

Este script:
1. Lee la Fila 119 de "Planilla Flujo de Caja Comsulting 2025.xlsx"
2. Extrae los gastos mensuales (antes de remuneraciones) para Ene-Sep 2025
3. Los inserta en la tabla gastos_overhead

FUENTE: Fila 119 = "Total Gastos mes" (antes de remuneraciones)
        Incluye: arriendos, suscripciones, servicios, gastos operacionales, etc.

IMPORTANTE: Ejecutar localmente contra BD remota porque necesita acceso al Excel
"""

import pandas as pd
import os
from sqlalchemy import create_engine, text

# Configuración
EXCEL_PATH_FLUJO = "/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/Planilla Flujo de Caja  Comsulting 2025.xlsx"
EXCEL_PATH_COSTOS = "/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/Costos RRHH_Facturacion 09_2025 VF.xlsx"
VALOR_UF_ACTUAL = 38000  # Pesos por UF

# Remuneración mensual de Jazmín (Admin y Finanzas) - va al overhead porque no se imputa a clientes
COSTO_JAZMIN_MENSUAL = 3161448  # Pesos (de Costos RRHH Excel)

# Obtener DATABASE_URL del ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    print("Ejecuta: export DATABASE_URL='postgresql://...'")
    exit(1)

# Fix para Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def limpiar_gastos_existentes(conn, año):
    """Elimina gastos overhead existentes del año para reimportar"""
    result = conn.execute(text("""
        DELETE FROM gastos_overhead WHERE año = :año
    """), {"año": año})
    count = result.rowcount
    conn.commit()
    print(f"  ✓ Eliminados {count} registros existentes de {año}")
    return count

def importar_gastos_overhead(conn):
    """Importa gastos overhead desde Flujo de Caja + remuneración Jazmín"""
    print("\n=== IMPORTANDO GASTOS OVERHEAD ===\n")

    # Leer Excel Flujo de Caja
    print(f"Leyendo Flujo de Caja: {EXCEL_PATH_FLUJO}")
    df = pd.read_excel(EXCEL_PATH_FLUJO, sheet_name='2025', header=None)

    # Fila 119 = Total Gastos mes (antes de remuneraciones)
    fila_119 = df.iloc[119, :]

    # Verificar que sea la fila correcta
    if 'Total Gastos mes' not in str(fila_119[1]):
        print(f"⚠️  ADVERTENCIA: Fila 119 no contiene 'Total Gastos mes'")
        print(f"   Encontrado: {fila_119[1]}")
        respuesta = input("¿Continuar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            print("Importación cancelada")
            return 0

    # Meses están en columnas 3-14 (Enero = col 3, Diciembre = col 14)
    meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    año = 2025
    registros_creados = 0
    total_gastos_uf = 0
    total_jazmin_uf = 0

    print("\n1. Gastos operacionales (Flujo de Caja Fila 119):")
    for i, mes_nombre in enumerate(meses_nombres[:9]):  # Solo Ene-Sep 2025
        mes = i + 1
        col = 3 + i  # Col 3 = Enero, Col 4 = Feb, etc.

        valor_pesos = fila_119[col]

        if pd.isna(valor_pesos):
            print(f"  ⚠️  {mes_nombre}: Sin datos (saltando)")
            continue

        valor_uf = valor_pesos / VALOR_UF_ACTUAL

        # Insertar gastos operacionales
        conn.execute(text("""
            INSERT INTO gastos_overhead (año, mes, concepto, monto_pesos)
            VALUES (:año, :mes, :concepto, :monto_pesos)
        """), {
            "año": año,
            "mes": mes,
            "concepto": "Gastos operacionales mensuales (Flujo de Caja Fila 119)",
            "monto_pesos": float(valor_pesos)
        })

        registros_creados += 1
        total_gastos_uf += valor_uf

        print(f"  ✓ {mes_nombre:12s}: ${valor_pesos:15,.0f} pesos = {valor_uf:8,.2f} UF")

    print(f"\n2. Remuneración Jazmín Sapunar (Admin y Finanzas):")
    print(f"   Se agrega al overhead porque no se imputa a clientes específicos")

    for i, mes_nombre in enumerate(meses_nombres[:9]):  # Solo Ene-Sep 2025
        mes = i + 1

        # Insertar remuneración Jazmín
        conn.execute(text("""
            INSERT INTO gastos_overhead (año, mes, concepto, monto_pesos)
            VALUES (:año, :mes, :concepto, :monto_pesos)
        """), {
            "año": año,
            "mes": mes,
            "concepto": "Remuneración Jazmín Sapunar (Admin y Finanzas)",
            "monto_pesos": float(COSTO_JAZMIN_MENSUAL)
        })

        registros_creados += 1
        total_jazmin_uf += COSTO_JAZMIN_MENSUAL / VALOR_UF_ACTUAL

        print(f"  ✓ {mes_nombre:12s}: ${COSTO_JAZMIN_MENSUAL:15,.0f} pesos = {COSTO_JAZMIN_MENSUAL/VALOR_UF_ACTUAL:8,.2f} UF")

    conn.commit()

    total_overhead_uf = total_gastos_uf + total_jazmin_uf

    print("\n" + "="*70)
    print("RESUMEN DE IMPORTACIÓN DE GASTOS OVERHEAD")
    print("="*70)
    print(f"\n  Registros creados:                    {registros_creados}")
    print(f"\n  Gastos operacionales (Ene-Sep):       {total_gastos_uf:,.2f} UF")
    print(f"  Remuneración Jazmín (Ene-Sep):        {total_jazmin_uf:,.2f} UF")
    print(f"  {'─'*50}")
    print(f"  TOTAL OVERHEAD OPERACIONAL:           {total_overhead_uf:,.2f} UF")
    print(f"\n  Promedio mensual:                     {total_overhead_uf / 9:,.2f} UF/mes")
    print(f"\n  ⚠️  FALTA: Costo de horas no imputadas (gap)")
    print(f"      Se calculará dinámicamente en calcular_overhead_distribuido()")

    return registros_creados

def verificar_gastos(conn):
    """Verifica los gastos overhead importados"""
    print("\n=== VERIFICACIÓN DE GASTOS OVERHEAD ===\n")

    # Total por mes
    result = conn.execute(text("""
        SELECT mes, SUM(monto_pesos) as total_pesos
        FROM gastos_overhead
        WHERE año = 2025
        GROUP BY mes
        ORDER BY mes
    """))

    print("  Gastos overhead 2025:")
    total_año = 0
    for row in result:
        mes, total_pesos = row
        total_uf = total_pesos / VALOR_UF_ACTUAL
        total_año += total_uf
        print(f"    Mes {mes:2d}: ${total_pesos:15,.0f} pesos = {total_uf:8,.2f} UF")

    print(f"\n  Total año 2025: {total_año:,.2f} UF")

def main():
    """Función principal"""
    print("="*70)
    print("IMPORTACIÓN DE GASTOS OVERHEAD A PRODUCCIÓN (PostgreSQL)")
    print("="*70)
    print(f"\nConectando a: {DATABASE_URL[:50]}...")

    # Verificar que existen los Excels
    if not os.path.exists(EXCEL_PATH_FLUJO):
        print(f"\nERROR: No se encuentra Flujo de Caja")
        print(f"Buscado en: {EXCEL_PATH_FLUJO}")
        print("\nEste script debe ejecutarse en el entorno local donde está el Excel")
        exit(1)

    if not os.path.exists(EXCEL_PATH_COSTOS):
        print(f"\nERROR: No se encuentra Costos RRHH")
        print(f"Buscado en: {EXCEL_PATH_COSTOS}")
        exit(1)

    # Crear engine de SQLAlchemy
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # 1. Limpiar gastos existentes de 2025
            limpiar_gastos_existentes(conn, 2025)

            # 2. Importar gastos
            importar_gastos_overhead(conn)

            # 3. Verificar
            verificar_gastos(conn)

            print("\n" + "="*70)
            print("✓ IMPORTACIÓN COMPLETADA")
            print("="*70)
            print("\nAhora el overhead se calculará correctamente usando:")
            print("  1. Gastos operacionales (de esta tabla)")
            print("  2. Costo de horas no imputadas (gap)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
