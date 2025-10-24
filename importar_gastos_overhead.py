#!/usr/bin/env python3
"""
Script para importar gastos overhead desde JSON a la base de datos

Uso:
    python importar_gastos_overhead.py
"""

import json
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import GastoOverhead

# Configuración de base de datos
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    DATABASE_URL = 'sqlite:///comsulting_simplified.db'

# Mapeo de conceptos a categorías
CATEGORIAS = {
    'arriendo': 'Oficina',
    'oficina': 'Oficina',
    'gastos comunes': 'Oficina',
    'patente': 'Administrativo',
    'seguro': 'Administrativo',
    'banco': 'Financiero',
    'comisiones': 'Financiero',
    'retención': 'Impuestos',
    'aportes patronales': 'Remuneraciones',  # Nota: Quizás excluir esto
    'servicios externalizados': 'Servicios',
    'contador': 'Servicios',
    'aseo': 'Servicios',
    'suscripciones': 'Tecnología',
    'licencias': 'Tecnología',
    'software': 'Tecnología',
    'hosting': 'Tecnología',
    'caja chica': 'Gastos Generales',
    'capacitación': 'Desarrollo',
    'regalos': 'Gastos Generales',
}

def categorizar_gasto(concepto):
    """Determina la categoría de un gasto basado en su concepto"""
    concepto_lower = concepto.lower()

    for keyword, categoria in CATEGORIAS.items():
        if keyword in concepto_lower:
            return categoria

    return 'Otros'

def main():
    print("=" * 80)
    print("IMPORTACIÓN DE GASTOS OVERHEAD")
    print("=" * 80)

    # Leer JSON (usar el archivo actualizado con línea 74)
    json_path = 'gastos_overhead_2025_real.json'

    if not os.path.exists(json_path):
        print(f"\n❌ Error: No se encontró el archivo {json_path}")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    gastos_por_mes = data['gastos_por_mes']
    resumen = data['resumen']
    print(f"\n📂 Datos cargados: {len(gastos_por_mes)} registros mensuales")
    print(f"💰 Total anual: ${resumen['total_pesos']:,.0f} = {resumen['total_uf']:.2f} UF")

    # Conectar a BD
    print(f"\n🔗 Conectando a: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Verificar si ya existen datos para 2025
    existing_count = session.query(GastoOverhead).filter_by(año=2025).count()

    if existing_count > 0:
        print(f"\n⚠️  Ya existen {existing_count} registros para 2025 en la base de datos")
        respuesta = input("   ¿Deseas eliminarlos y reimportar? (SI/NO): ")

        if respuesta.strip().upper() == 'SI':
            session.query(GastoOverhead).filter_by(año=2025).delete()
            session.commit()
            print("   ✅ Registros anteriores eliminados")
        else:
            print("   ❌ Importación cancelada")
            return

    # Importar gastos
    print("\n📥 Importando gastos overhead mensuales...")

    total_registros = 0

    for gasto_mes in gastos_por_mes:
        nuevo_gasto = GastoOverhead(
            año=gasto_mes['año'],
            mes=gasto_mes['mes'],
            concepto=gasto_mes['concepto'],
            categoria=gasto_mes['categoria'],
            monto_pesos=float(gasto_mes['monto_pesos'])
        )
        session.add(nuevo_gasto)
        total_registros += 1

        print(f"   {gasto_mes['mes_nombre']:>12}: ${gasto_mes['monto_pesos']:>15,.0f} = {gasto_mes['monto_uf']:>8,.2f} UF")

    # Commit
    try:
        session.commit()
        print(f"\n✅ Importación completada: {total_registros} registros")

        # Verificar totales
        print("\n📊 Verificación en BD:")
        total_en_bd = session.query(GastoOverhead).filter_by(año=2025).with_entities(
            GastoOverhead.monto_pesos
        ).all()

        suma_bd = sum(row[0] for row in total_en_bd)
        print(f"   Total en BD:      ${suma_bd:>15,.0f}")
        print(f"   Total esperado:   ${resumen['total_pesos']:>15,.0f}")
        print(f"   Diferencia:       ${abs(suma_bd - resumen['total_pesos']):>15,.0f}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error al importar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    main()
