"""
Script para analizar los datos de los archivos Excel fuente
y diagnosticar los problemas de rentabilidad reportados
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Rutas a los archivos
BASE_DIR = Path('/Users/alfil/Desktop/Desarrollos/Comsulting')
CLIENTES_FILE = BASE_DIR / 'Cliente_Comsulting.xlsx'
HISTORIAL_FILE = BASE_DIR / 'Historial 2024-2025.xlsx'
FLUJO_CAJA_FILE = BASE_DIR / 'Planilla Flujo de Caja  Comsulting 2025.xlsx'

def analizar_clientes():
    """Analizar archivo de clientes"""
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE CLIENTES")
    print("="*80 + "\n")

    try:
        # Leer todas las hojas del archivo
        xls = pd.ExcelFile(CLIENTES_FILE)
        print(f"Hojas disponibles: {xls.sheet_names}\n")

        for sheet_name in xls.sheet_names[:3]:  # Primeras 3 hojas
            print(f"\n--- Hoja: {sheet_name} ---")
            df = pd.read_excel(CLIENTES_FILE, sheet_name=sheet_name)
            print(f"Dimensiones: {df.shape}")
            print(f"Columnas: {df.columns.tolist()}")
            print(f"\nPrimeras filas:")
            print(df.head())

    except Exception as e:
        print(f"Error leyendo clientes: {e}")

def analizar_historial():
    """Analizar historial de horas 2024-2025"""
    print("\n" + "="*80)
    print("⏱️  ANÁLISIS DE HISTORIAL DE HORAS")
    print("="*80 + "\n")

    try:
        # Leer todas las hojas
        xls = pd.ExcelFile(HISTORIAL_FILE)
        print(f"Hojas disponibles: {xls.sheet_names}\n")

        # Buscar la hoja principal de datos
        for sheet_name in xls.sheet_names[:5]:
            print(f"\n--- Hoja: {sheet_name} ---")
            df = pd.read_excel(HISTORIAL_FILE, sheet_name=sheet_name, nrows=10)
            print(f"Dimensiones (primeras 10 filas): {df.shape}")
            print(f"Columnas: {df.columns.tolist()}")
            print(f"\nPrimeras filas:")
            print(df.head())

    except Exception as e:
        print(f"Error leyendo historial: {e}")

def analizar_flujo_caja():
    """Analizar planilla de flujo de caja 2025"""
    print("\n" + "="*80)
    print("💰 ANÁLISIS DE FLUJO DE CAJA 2025")
    print("="*80 + "\n")

    try:
        # Leer todas las hojas
        xls = pd.ExcelFile(FLUJO_CAJA_FILE)
        print(f"Hojas disponibles: {xls.sheet_names}\n")

        for sheet_name in xls.sheet_names[:5]:
            print(f"\n--- Hoja: {sheet_name} ---")
            df = pd.read_excel(FLUJO_CAJA_FILE, sheet_name=sheet_name, nrows=15)
            print(f"Dimensiones (primeras 15 filas): {df.shape}")
            print(f"Columnas: {df.columns.tolist()}")
            print(f"\nPrimeras filas:")
            print(df.head(10))

    except Exception as e:
        print(f"Error leyendo flujo de caja: {e}")

def diagnostico_rentabilidad():
    """Diagnóstico completo de rentabilidad"""
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO DE RENTABILIDAD - DATOS DESDE EXCEL")
    print("="*80)

    # Analizar cada archivo
    analizar_clientes()
    analizar_historial()
    analizar_flujo_caja()

    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80 + "\n")

if __name__ == '__main__':
    diagnostico_rentabilidad()
