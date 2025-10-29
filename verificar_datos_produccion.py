"""
Script simple para verificar el estado actual de la BD en producción

Muestra:
- Total de registros y horas en 2025
- Top 10 clientes por horas
- Top 10 personas por horas
- Comparación con objetivos del Excel TD 2025
"""

import os
from sqlalchemy import create_engine, text

# Objetivos del Excel TD 2025
OBJETIVO_REGISTROS = 45750
OBJETIVO_HORAS = 40426.83

# Obtener DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    print("Para producción (Render): La variable debería estar configurada automáticamente")
    print("Para local: export DATABASE_URL='postgresql://...'")
    exit(1)

# Fix para Render
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def verificar_estado():
    """Verifica el estado actual de la BD"""
    engine = create_engine(DATABASE_URL)

    print("="*70)
    print("ESTADO ACTUAL DE LA BASE DE DATOS (PRODUCCIÓN)")
    print("="*70)
    print(f"\nConectado a: {DATABASE_URL[:50]}...\n")

    try:
        with engine.connect() as conn:
            # 1. Totales 2025
            print("=== TOTALES 2025 (ene-sep) ===\n")
            result = conn.execute(text("""
                SELECT COUNT(*) as count, SUM(horas) as total_horas
                FROM registros_horas
                WHERE fecha >= '2025-01-01' AND fecha < '2025-10-01'
            """))
            count, total_horas = result.fetchone()

            print(f"  Total registros:  {count:,}")
            print(f"  Total horas:      {total_horas:,.2f}")
            print(f"\n  Objetivo Excel:   {OBJETIVO_REGISTROS:,} registros")
            print(f"  Objetivo Excel:   {OBJETIVO_HORAS:,.2f} horas")

            diff_registros = count - OBJETIVO_REGISTROS
            diff_horas = total_horas - OBJETIVO_HORAS
            pct_diff = (diff_horas / OBJETIVO_HORAS * 100) if OBJETIVO_HORAS > 0 else 0

            print(f"\n  Diferencia:       {diff_registros:+,} registros")
            print(f"  Diferencia:       {diff_horas:+,.2f} horas ({pct_diff:+.1f}%)")

            if abs(pct_diff) < 3:
                print("\n  ✓ ¡Los números están bien alineados!")
            elif abs(pct_diff) < 10:
                print("\n  ⚠️  Diferencia moderada - revisar")
            else:
                print("\n  ❌ Diferencia significativa - ejecutar importación")

            # 2. Top 10 clientes
            print("\n" + "="*70)
            print("=== TOP 10 CLIENTES POR HORAS (2025) ===\n")
            result = conn.execute(text("""
                SELECT c.nombre, SUM(r.horas) as total_horas
                FROM registros_horas r
                JOIN clientes c ON r.cliente_id = c.id
                WHERE r.fecha >= '2025-01-01' AND r.fecha < '2025-10-01'
                GROUP BY c.id, c.nombre
                ORDER BY total_horas DESC
                LIMIT 10
            """))

            print(f"  {'Cliente':<40s} {'Horas':>12s}")
            print("  " + "-"*54)
            for nombre, horas in result:
                print(f"  {nombre:<40s} {horas:>12.2f}")

            # 3. Top 10 personas
            print("\n" + "="*70)
            print("=== TOP 10 PERSONAS POR HORAS (2025) ===\n")
            result = conn.execute(text("""
                SELECT p.nombre, SUM(r.horas) as total_horas
                FROM registros_horas r
                JOIN personas p ON r.persona_id = p.id
                WHERE r.fecha >= '2025-01-01' AND r.fecha < '2025-10-01'
                GROUP BY p.id, p.nombre
                ORDER BY total_horas DESC
                LIMIT 10
            """))

            print(f"  {'Persona':<40s} {'Horas':>12s}")
            print("  " + "-"*54)
            for nombre, horas in result:
                print(f"  {nombre:<40s} {horas:>12.2f}")

            # 4. Total personas activas
            print("\n" + "="*70)
            print("=== PERSONAS EN LA BASE DE DATOS ===\n")
            result = conn.execute(text("""
                SELECT COUNT(*) FROM personas WHERE activo = true
            """))
            total_personas = result.fetchone()[0]
            print(f"  Total personas activas: {total_personas}")

            # 5. Verificar personas nuevas que deberían existir
            personas_nuevas = [
                'María Marañón', 'Vicente Vera', 'Catalina Durán',
                'Javiera Flores', 'Felipe Iglesias', 'Rosirene Clavero',
                'Belén Castro', 'Nicolás Campos'
            ]

            print("\n  Personas nuevas (deberían existir después de importación):")
            for persona in personas_nuevas:
                result = conn.execute(text("""
                    SELECT id FROM personas WHERE nombre = :nombre
                """), {"nombre": persona})
                existe = result.fetchone()
                status = "✓ Existe" if existe else "✗ NO EXISTE"
                print(f"    {status:12s} - {persona}")

            print("\n" + "="*70)
            print("✓ VERIFICACIÓN COMPLETADA")
            print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verificar_estado()
