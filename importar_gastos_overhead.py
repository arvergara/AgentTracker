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

    # Leer JSON
    json_path = 'gastos_overhead_2025.json'

    if not os.path.exists(json_path):
        print(f"\n❌ Error: No se encontró el archivo {json_path}")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    gastos = data['gastos']
    print(f"\n📂 Cargados {len(gastos)} conceptos de gasto")

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
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    total_registros = 0
    registros_por_categoria = {}

    print("\n📥 Importando gastos...")

    for gasto in gastos:
        concepto = gasto['concepto']
        categoria = categorizar_gasto(concepto)

        # Excluir ciertos conceptos que no son overhead puro
        conceptos_excluir = ['aportes patronales', 'jazmin', 'jazmín']
        if any(exc in concepto.lower() for exc in conceptos_excluir):
            print(f"   ⏭️  Omitiendo: {concepto} (es parte de remuneraciones)")
            continue

        # Contador por categoría
        registros_por_categoria[categoria] = registros_por_categoria.get(categoria, 0) + 1

        # Crear registros mensuales
        for mes_idx, valor in enumerate(gasto['valores_mensuales']):
            if valor > 0:  # Solo importar si hay valor
                nuevo_gasto = GastoOverhead(
                    año=2025,
                    mes=mes_idx + 1,
                    concepto=concepto,
                    categoria=categoria,
                    monto_pesos=float(valor)
                )
                session.add(nuevo_gasto)
                total_registros += 1

    # Commit
    try:
        session.commit()
        print(f"\n✅ Importación completada: {total_registros} registros")

        print("\n📊 Resumen por categoría:")
        for cat, count in sorted(registros_por_categoria.items()):
            print(f"   {cat:.<30} {count:>3} conceptos")

        # Verificar totales por mes
        print("\n💰 Totales por mes:")
        for mes_idx, mes_nombre in enumerate(meses):
            total_mes = session.query(GastoOverhead).filter_by(
                año=2025,
                mes=mes_idx + 1
            ).with_entities(GastoOverhead.monto_pesos).all()

            suma = sum(row[0] for row in total_mes)
            print(f"   {mes_nombre:>12}: ${suma:>15,.0f}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error al importar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    main()
