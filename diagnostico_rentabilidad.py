"""
Script de diagnóstico para analizar la rentabilidad de clientes
Investiga por qué el margen promedio aparece como ~70% cuando clientes individuales no tienen ese margen
"""

from app import app, db, Cliente, IngresoMensual, RegistroHora, ServicioCliente, calcular_overhead_distribuido
from sqlalchemy import extract, func
from datetime import datetime

def diagnosticar_rentabilidad():
    """Diagnóstico completo de rentabilidad por cliente"""

    with app.app_context():
        año = 2025
        print(f"\n{'='*80}")
        print(f"DIAGNÓSTICO DE RENTABILIDAD - AÑO {año}")
        print(f"{'='*80}\n")

        # 1. Calcular overhead
        print("📊 PASO 1: Calculando overhead distribuido...")
        try:
            overhead_info = calcular_overhead_distribuido(año, mes=None)
            distribucion_overhead = overhead_info['distribucion_por_cliente']

            print(f"  Overhead Total: {overhead_info['overhead_total_uf']:.2f} UF")
            print(f"  - Operacional: {overhead_info['overhead_operacional_uf']:.2f} UF")
            print(f"  - Horas no imputadas: {overhead_info['overhead_horas_no_imputadas_uf']:.2f} UF")
            print(f"  Total horas asignadas: {overhead_info['total_horas_asignadas']:.2f} hrs\n")
        except Exception as e:
            print(f"  ⚠️  WARNING: No se pudo calcular overhead: {str(e)}")
            print(f"  Usando overhead = 0 para todos los clientes\n")
            distribucion_overhead = {}
            overhead_info = {
                'overhead_total_uf': 0,
                'overhead_operacional_uf': 0,
                'overhead_horas_no_imputadas_uf': 0,
                'total_horas_asignadas': 0
            }

        # 2. Análisis por cliente
        print("💼 PASO 2: Analizando clientes...\n")

        clientes = Cliente.query.filter_by(activo=True).all()

        resultados = []
        total_ingresos = 0
        total_costos_directos = 0
        total_overhead = 0
        total_utilidad = 0

        for cliente in clientes:
            if cliente.nombre in ['CLIENTES PERMANENTES', 'COMSULTING']:
                continue

            # Ingresos
            ingresos_query = IngresoMensual.query.join(ServicioCliente).filter(
                ServicioCliente.cliente_id == cliente.id,
                IngresoMensual.año == año
            )
            ingresos = ingresos_query.all()
            ingresos_uf = sum(i.ingreso_uf for i in ingresos)

            # Costos directos (horas)
            registros = RegistroHora.query.filter_by(cliente_id=cliente.id).filter(
                extract('year', RegistroHora.fecha) == año
            ).all()

            horas = sum(r.horas for r in registros)
            costos_directos_uf = sum(r.costo_uf for r in registros)

            # Overhead
            overhead_uf = distribucion_overhead.get(cliente.id, 0)

            # Totales
            costos_totales_uf = costos_directos_uf + overhead_uf
            utilidad_uf = ingresos_uf - costos_totales_uf
            margen = (utilidad_uf / ingresos_uf * 100) if ingresos_uf > 0 else 0

            # Solo incluir clientes con ingresos
            if ingresos_uf > 0:
                resultados.append({
                    'cliente': cliente.nombre,
                    'ingresos': ingresos_uf,
                    'horas': horas,
                    'costos_directos': costos_directos_uf,
                    'overhead': overhead_uf,
                    'costos_totales': costos_totales_uf,
                    'utilidad': utilidad_uf,
                    'margen': margen
                })

                total_ingresos += ingresos_uf
                total_costos_directos += costos_directos_uf
                total_overhead += overhead_uf
                total_utilidad += utilidad_uf

        # Ordenar por utilidad descendente
        resultados.sort(key=lambda x: x['utilidad'], reverse=True)

        # Mostrar tabla
        print(f"{'Cliente':<30} {'Ingresos':>12} {'Horas':>10} {'C.Directos':>12} {'Overhead':>12} {'C.Totales':>12} {'Utilidad':>12} {'Margen %':>10}")
        print("-" * 140)

        for r in resultados:
            color = "✅" if r['utilidad'] > 0 else "❌"
            print(f"{color} {r['cliente']:<28} {r['ingresos']:>10.1f} UF {r['horas']:>8.1f}h {r['costos_directos']:>10.1f} UF {r['overhead']:>10.1f} UF {r['costos_totales']:>10.1f} UF {r['utilidad']:>10.1f} UF {r['margen']:>9.1f}%")

        print("-" * 140)
        total_costos = total_costos_directos + total_overhead
        margen_total = (total_utilidad / total_ingresos * 100) if total_ingresos > 0 else 0
        print(f"{'TOTAL':<30} {total_ingresos:>10.1f} UF {'':>10} {total_costos_directos:>10.1f} UF {total_overhead:>10.1f} UF {total_costos:>10.1f} UF {total_utilidad:>10.1f} UF {margen_total:>9.1f}%")

        # 3. Análisis estadístico
        print(f"\n{'='*80}")
        print("📈 ANÁLISIS ESTADÍSTICO")
        print(f"{'='*80}\n")

        clientes_con_margen_positivo = [r for r in resultados if r['margen'] > 0]
        clientes_con_margen_negativo = [r for r in resultados if r['margen'] < 0]

        print(f"Total clientes analizados: {len(resultados)}")
        print(f"  - Con margen positivo: {len(clientes_con_margen_positivo)} ({len(clientes_con_margen_positivo)/len(resultados)*100:.1f}%)")
        print(f"  - Con margen negativo: {len(clientes_con_margen_negativo)} ({len(clientes_con_margen_negativo)/len(resultados)*100:.1f}%)")

        if clientes_con_margen_positivo:
            margen_promedio_positivos = sum(r['margen'] for r in clientes_con_margen_positivo) / len(clientes_con_margen_positivo)
            print(f"\nMargen promedio clientes positivos: {margen_promedio_positivos:.1f}%")
            print(f"Margen más alto: {max(r['margen'] for r in clientes_con_margen_positivo):.1f}% ({[r['cliente'] for r in clientes_con_margen_positivo if r['margen'] == max(r['margen'] for r in clientes_con_margen_positivo)][0]})")
            print(f"Margen más bajo (positivo): {min(r['margen'] for r in clientes_con_margen_positivo):.1f}%")

        if clientes_con_margen_negativo:
            margen_promedio_negativos = sum(r['margen'] for r in clientes_con_margen_negativo) / len(clientes_con_margen_negativo)
            print(f"\nMargen promedio clientes negativos: {margen_promedio_negativos:.1f}%")

        print(f"\n⚠️  MARGEN TOTAL EMPRESA: {margen_total:.1f}%")
        print(f"    (Este es el valor que aparece en el dashboard)")

        # 4. Identificar problemas
        print(f"\n{'='*80}")
        print("🔍 PROBLEMAS IDENTIFICADOS")
        print(f"{'='*80}\n")

        # Clientes con alta rentabilidad que distorsionan el promedio
        clientes_alto_margen = [r for r in resultados if r['margen'] > 60]
        if clientes_alto_margen:
            print("⚠️  Clientes con margen > 60% (posible distorsión):")
            for r in clientes_alto_margen:
                print(f"  - {r['cliente']}: {r['margen']:.1f}% | Ingresos: {r['ingresos']:.1f} UF | Horas: {r['horas']:.1f}h")
                # Verificar si tiene pocas horas (posible falta de registro)
                if r['horas'] < 10:
                    print(f"    ⚠️  ALERTA: Pocas horas registradas ({r['horas']:.1f}h). Puede faltar registro de horas.")

        # Clientes con margen negativo que deberían ser positivos
        print("\n❌ Clientes con margen negativo:")
        for r in clientes_con_margen_negativo:
            print(f"  - {r['cliente']}: {r['margen']:.1f}% | Ingresos: {r['ingresos']:.1f} UF | Costos: {r['costos_totales']:.1f} UF | Horas: {r['horas']:.1f}h")

            # Verificar posibles problemas
            if r['costos_directos'] > r['ingresos']:
                print(f"    ⚠️  PROBLEMA: Costos directos ({r['costos_directos']:.1f} UF) > Ingresos ({r['ingresos']:.1f} UF)")
                print(f"       Horas registradas: {r['horas']:.1f}h")
                print(f"       Posible causa: Muchas horas senior asignadas o ingresos no registrados correctamente")

            if r['overhead'] > r['ingresos'] * 0.5:
                print(f"    ⚠️  PROBLEMA: Overhead ({r['overhead']:.1f} UF) es > 50% de ingresos")
                print(f"       Posible causa: Pocas horas asignadas en relación al overhead total")

        # 5. Verificar clientes específicos mencionados por las socias
        print(f"\n{'='*80}")
        print("🎯 VERIFICACIÓN DE CLIENTES ESPECÍFICOS")
        print(f"{'='*80}\n")

        clientes_a_verificar = ['EC', 'Falabella', 'Collahuasi']
        for nombre in clientes_a_verificar:
            cliente_data = next((r for r in resultados if nombre.lower() in r['cliente'].lower()), None)
            if cliente_data:
                print(f"\n{cliente_data['cliente']}:")
                print(f"  Ingresos: {cliente_data['ingresos']:.2f} UF")
                print(f"  Costos directos: {cliente_data['costos_directos']:.2f} UF ({cliente_data['horas']:.1f} horas)")
                print(f"  Overhead: {cliente_data['overhead']:.2f} UF")
                print(f"  Costos totales: {cliente_data['costos_totales']:.2f} UF")
                print(f"  Utilidad: {cliente_data['utilidad']:.2f} UF")
                print(f"  Margen: {cliente_data['margen']:.1f}%")

                if cliente_data['margen'] < 0:
                    print(f"  ❌ CLIENTE A PÉRDIDA")
                    ratio_costos = (cliente_data['costos_directos'] / cliente_data['ingresos'] * 100) if cliente_data['ingresos'] > 0 else 0
                    print(f"     Costos directos representan {ratio_costos:.1f}% de ingresos")
            else:
                print(f"\n⚠️  {nombre}: No encontrado o sin ingresos en {año}")

        print(f"\n{'='*80}")
        print("✅ DIAGNÓSTICO COMPLETADO")
        print(f"{'='*80}\n")

if __name__ == '__main__':
    diagnosticar_rentabilidad()
