"""
Script de Análisis Avanzado de Productividad
Proporciona análisis comparativos y reportes ejecutivos
"""

from app import app, db, Persona, Cliente, RegistroHora, Factura, reporte_productividad_persona, rentabilidad_por_area
from datetime import datetime, timedelta
from sqlalchemy import func
import json

def analisis_comparativo_equipo(periodo_meses=6):
    """
    Genera un análisis comparativo de todo el equipo
    Útil para evaluaciones anuales y decisiones estratégicas
    """
    with app.app_context():
        personas = Persona.query.filter_by(activo=True).all()
        resultados = []
        
        for persona in personas:
            reporte = reporte_productividad_persona(persona.id, periodo_meses)
            if reporte:
                resultados.append(reporte)
        
        # Ordenar por ROI
        resultados.sort(key=lambda x: x['roi_global'], reverse=True)
        
        # Calcular promedios del equipo
        if resultados:
            promedio_roi = sum([r['roi_global'] for r in resultados]) / len(resultados)
            promedio_margen = sum([r['margen_porcentual'] for r in resultados]) / len(resultados)
            promedio_eficiencia = sum([r['eficiencia_costos'] for r in resultados]) / len(resultados)
            promedio_cumplimiento = sum([r['porcentaje_cumplimiento'] for r in resultados]) / len(resultados)
        else:
            promedio_roi = promedio_margen = promedio_eficiencia = promedio_cumplimiento = 0
        
        return {
            'periodo_meses': periodo_meses,
            'total_personas': len(resultados),
            'promedios': {
                'roi': round(promedio_roi, 2),
                'margen_porcentual': round(promedio_margen, 2),
                'eficiencia_costos': round(promedio_eficiencia, 2),
                'cumplimiento_horas': round(promedio_cumplimiento, 2)
            },
            'ranking': resultados,
            'top_performers': resultados[:5] if len(resultados) >= 5 else resultados,
            'necesitan_atencion': [r for r in resultados if r['roi_global'] < 80 or r['porcentaje_cumplimiento'] < 80]
        }

def analisis_por_area(periodo_meses=6):
    """
    Analiza productividad agregada por área de negocio
    Identifica áreas más y menos productivas
    """
    with app.app_context():
        areas = ['Externas', 'Internas', 'Asuntos Públicos', 'Redes sociales', 'Diseño']
        resultados = []
        
        for area in areas:
            personas_area = Persona.query.filter_by(area=area, activo=True).all()
            
            if not personas_area:
                continue
            
            # Métricas agregadas del área
            roi_area = []
            margen_area = []
            eficiencia_area = []
            cumplimiento_area = []
            ingresos_total = 0
            costos_total = 0
            margen_total = 0
            
            for persona in personas_area:
                reporte = reporte_productividad_persona(persona.id, periodo_meses)
                if reporte:
                    roi_area.append(reporte['roi_global'])
                    margen_area.append(reporte['margen_porcentual'])
                    eficiencia_area.append(reporte['eficiencia_costos'])
                    cumplimiento_area.append(reporte['porcentaje_cumplimiento'])
                    ingresos_total += reporte['ingresos_prorrateados']
                    costos_total += reporte['costo_total']
                    margen_total += reporte['margen_generado']
            
            if roi_area:
                resultados.append({
                    'area': area,
                    'personas': len(personas_area),
                    'roi_promedio': round(sum(roi_area) / len(roi_area), 2),
                    'margen_promedio': round(sum(margen_area) / len(margen_area), 2),
                    'eficiencia_promedio': round(sum(eficiencia_area) / len(eficiencia_area), 2),
                    'cumplimiento_promedio': round(sum(cumplimiento_area) / len(cumplimiento_area), 2),
                    'ingresos_total': round(ingresos_total, 2),
                    'costos_total': round(costos_total, 2),
                    'margen_total': round(margen_total, 2),
                    'margen_porcentual_total': round((margen_total / ingresos_total * 100) if ingresos_total > 0 else 0, 2)
                })
        
        # Ordenar por margen total
        resultados.sort(key=lambda x: x['margen_total'], reverse=True)
        
        return resultados

def identificar_desbalances_carga():
    """
    Identifica personas sobrecargadas o subutilizadas
    Útil para redistribuir trabajo
    """
    with app.app_context():
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)  # Último mes
        
        personas = Persona.query.filter_by(activo=True).all()
        desbalances = {
            'sobrecargados': [],
            'subutilizados': [],
            'optimo': []
        }
        
        for persona in personas:
            horas_trabajadas = db.session.query(func.sum(RegistroHora.horas))\
                .filter(RegistroHora.persona_id == persona.id)\
                .filter(RegistroHora.fecha >= fecha_inicio)\
                .filter(RegistroHora.fecha <= fecha_fin)\
                .scalar() or 0
            
            horas_esperadas = 156 if persona.tipo_jornada == 'full-time' else 78
            utilizacion = (horas_trabajadas / horas_esperadas * 100) if horas_esperadas > 0 else 0
            
            info = {
                'persona': persona.nombre,
                'cargo': persona.cargo,
                'area': persona.area,
                'horas_trabajadas': round(horas_trabajadas, 2),
                'horas_esperadas': horas_esperadas,
                'utilizacion': round(utilizacion, 2),
                'diferencia_horas': round(horas_trabajadas - horas_esperadas, 2)
            }
            
            if utilizacion > 110:
                desbalances['sobrecargados'].append(info)
            elif utilizacion < 70:
                desbalances['subutilizados'].append(info)
            else:
                desbalances['optimo'].append(info)
        
        return desbalances

def proyectar_bonos_anuales(periodo_meses=12):
    """
    Proyecta el monto total en bonos según el desempeño actual
    Útil para presupuestos
    """
    with app.app_context():
        personas = Persona.query.filter_by(activo=True).all()
        proyeccion = {
            '100%': [],
            '75%': [],
            '50%': [],
            '25%': [],
            '0%': []
        }
        
        total_sueldos = 0
        total_bonos_proyectados = 0
        
        for persona in personas:
            if not persona.sueldo_mensual:
                continue
                
            reporte = reporte_productividad_persona(persona.id, periodo_meses)
            if not reporte:
                continue
            
            # Extraer porcentaje de bono de la recomendación
            bono_texto = reporte['recomendacion_bono']
            if '100%' in bono_texto:
                porcentaje_bono = 1.0
                categoria = '100%'
            elif '75%' in bono_texto:
                porcentaje_bono = 0.75
                categoria = '75%'
            elif '50%' in bono_texto:
                porcentaje_bono = 0.5
                categoria = '50%'
            elif '25%' in bono_texto:
                porcentaje_bono = 0.25
                categoria = '25%'
            else:
                porcentaje_bono = 0
                categoria = '0%'
            
            # Calcular bono (asumiendo 1 mes de sueldo como base)
            bono_anual = persona.sueldo_mensual * porcentaje_bono
            total_sueldos += persona.sueldo_mensual * 12
            total_bonos_proyectados += bono_anual
            
            proyeccion[categoria].append({
                'persona': persona.nombre,
                'sueldo_mensual': persona.sueldo_mensual,
                'bono_proyectado': round(bono_anual, 2),
                'roi': reporte['roi_global'],
                'margen': reporte['margen_porcentual']
            })
        
        return {
            'total_sueldos_anuales': round(total_sueldos, 2),
            'total_bonos_proyectados': round(total_bonos_proyectados, 2),
            'porcentaje_sobre_sueldos': round((total_bonos_proyectados / total_sueldos * 100) if total_sueldos > 0 else 0, 2),
            'distribucion': proyeccion
        }

def reporte_ejecutivo_completo(periodo_meses=6):
    """
    Genera un reporte ejecutivo completo para presentar a dirección
    """
    with app.app_context():
        analisis_equipo = analisis_comparativo_equipo(periodo_meses)
        analisis_areas = analisis_por_area(periodo_meses)
        desbalances = identificar_desbalances_carga()
        bonos = proyectar_bonos_anuales(12)
        
        # Calcular métricas globales de la empresa
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30 * periodo_meses)
        
        # Total de horas trabajadas
        horas_totales = db.session.query(func.sum(RegistroHora.horas))\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0
        
        # Total de costos
        costos_totales = db.session.query(
            func.sum(RegistroHora.horas * Persona.costo_hora)
        ).join(Persona)\
            .filter(RegistroHora.fecha >= fecha_inicio)\
            .filter(RegistroHora.fecha <= fecha_fin)\
            .scalar() or 0
        
        # Total de ingresos
        ingresos_totales = db.session.query(func.sum(Factura.monto_uf))\
            .filter(Factura.fecha >= fecha_inicio)\
            .filter(Factura.fecha <= fecha_fin)\
            .scalar() or 0
        
        margen_empresa = ingresos_totales - costos_totales
        margen_porcentual_empresa = (margen_empresa / ingresos_totales * 100) if ingresos_totales > 0 else 0
        roi_empresa = (margen_empresa / costos_totales * 100) if costos_totales > 0 else 0
        
        return {
            'periodo': f'{periodo_meses} meses',
            'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M'),
            
            'metricas_empresa': {
                'horas_totales': round(horas_totales, 2),
                'costos_totales': round(costos_totales, 2),
                'ingresos_totales': round(ingresos_totales, 2),
                'margen_total': round(margen_empresa, 2),
                'margen_porcentual': round(margen_porcentual_empresa, 2),
                'roi_empresa': round(roi_empresa, 2)
            },
            
            'analisis_equipo': analisis_equipo,
            'analisis_areas': analisis_areas,
            'desbalances_carga': desbalances,
            'proyeccion_bonos': bonos
        }

def generar_reporte_json(filename='reporte_productividad.json'):
    """Genera y guarda el reporte ejecutivo en formato JSON"""
    reporte = reporte_ejecutivo_completo(6)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Reporte generado: {filename}")
    return reporte

def imprimir_resumen_ejecutivo():
    """Imprime un resumen ejecutivo en consola"""
    reporte = reporte_ejecutivo_completo(6)
    
    print("\n" + "="*80)
    print(" REPORTE EJECUTIVO DE PRODUCTIVIDAD - COMSULTING ".center(80))
    print("="*80)
    
    print(f"\n📅 Período: {reporte['periodo']}")
    print(f"📅 Fecha: {reporte['fecha_generacion']}")
    
    print("\n" + "-"*80)
    print(" MÉTRICAS GLOBALES DE LA EMPRESA ".center(80))
    print("-"*80)
    
    metricas = reporte['metricas_empresa']
    print(f"\n💼 Horas Totales:        {metricas['horas_totales']:>10.2f} h")
    print(f"💰 Costos Totales:       {metricas['costos_totales']:>10.2f} UF")
    print(f"💵 Ingresos Totales:     {metricas['ingresos_totales']:>10.2f} UF")
    print(f"📊 Margen Total:         {metricas['margen_total']:>10.2f} UF ({metricas['margen_porcentual']:.1f}%)")
    print(f"📈 ROI Empresa:          {metricas['roi_empresa']:>10.2f} %")
    
    print("\n" + "-"*80)
    print(" ANÁLISIS DEL EQUIPO ".center(80))
    print("-"*80)
    
    equipo = reporte['analisis_equipo']
    print(f"\n👥 Total Personas:       {equipo['total_personas']}")
    print(f"\n📊 Promedios del Equipo:")
    print(f"   ROI Promedio:         {equipo['promedios']['roi']:>10.2f} %")
    print(f"   Margen Promedio:      {equipo['promedios']['margen_porcentual']:>10.2f} %")
    print(f"   Eficiencia Promedio:  {equipo['promedios']['eficiencia_costos']:>10.2f} x")
    print(f"   Cumplimiento Promedio:{equipo['promedios']['cumplimiento_horas']:>10.2f} %")
    
    print(f"\n🏆 Top 5 Performers:")
    for i, persona in enumerate(equipo['top_performers'], 1):
        print(f"   {i}. {persona['persona']:<25} ROI: {persona['roi_global']:>6.1f}%  Margen: {persona['margen_porcentual']:>5.1f}%")
    
    if equipo['necesitan_atencion']:
        print(f"\n⚠️  Necesitan Atención ({len(equipo['necesitan_atencion'])} personas):")
        for persona in equipo['necesitan_atencion']:
            print(f"   • {persona['persona']:<25} ROI: {persona['roi_global']:>6.1f}%  Cumpl: {persona['porcentaje_cumplimiento']:>5.1f}%")
    
    print("\n" + "-"*80)
    print(" ANÁLISIS POR ÁREA ".center(80))
    print("-"*80)
    
    for area_info in reporte['analisis_areas']:
        print(f"\n📁 {area_info['area']}")
        print(f"   Personas:      {area_info['personas']}")
        print(f"   Ingresos:      {area_info['ingresos_total']:>10.2f} UF")
        print(f"   Margen:        {area_info['margen_total']:>10.2f} UF ({area_info['margen_porcentual_total']:.1f}%)")
        print(f"   ROI Promedio:  {area_info['roi_promedio']:>10.2f} %")
    
    print("\n" + "-"*80)
    print(" BALANCE DE CARGA DE TRABAJO ".center(80))
    print("-"*80)
    
    desbalances = reporte['desbalances_carga']
    print(f"\n🔴 Sobrecargados: {len(desbalances['sobrecargados'])} personas")
    for p in desbalances['sobrecargados']:
        print(f"   • {p['persona']:<25} {p['utilizacion']:>5.1f}% ({p['diferencia_horas']:+.1f}h)")
    
    print(f"\n🟡 Subutilizados: {len(desbalances['subutilizados'])} personas")
    for p in desbalances['subutilizados']:
        print(f"   • {p['persona']:<25} {p['utilizacion']:>5.1f}% ({p['diferencia_horas']:+.1f}h)")
    
    print(f"\n🟢 Óptimo: {len(desbalances['optimo'])} personas")
    
    print("\n" + "-"*80)
    print(" PROYECCIÓN DE BONOS ANUALES ".center(80))
    print("-"*80)
    
    bonos = reporte['proyeccion_bonos']
    print(f"\n💰 Sueldos Anuales:      {bonos['total_sueldos_anuales']:>10.2f} UF")
    print(f"💸 Bonos Proyectados:    {bonos['total_bonos_proyectados']:>10.2f} UF")
    print(f"📊 % sobre Sueldos:      {bonos['porcentaje_sobre_sueldos']:>10.2f} %")
    
    print("\n📈 Distribución de Bonos:")
    for categoria, personas in bonos['distribucion'].items():
        if personas:
            total_categoria = sum([p['bono_proyectado'] for p in personas])
            print(f"   {categoria}: {len(personas)} personas - {total_categoria:.2f} UF")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    print("\n🚀 Generando Reporte Ejecutivo de Productividad...\n")
    
    # Opción 1: Imprimir en consola
    imprimir_resumen_ejecutivo()
    
    # Opción 2: Generar archivo JSON
    # generar_reporte_json('reporte_ejecutivo.json')
