"""
Script para exportar todos los datos de la base de datos local a JSON
para luego importarlos en Render
"""

from app import app, db
from app import Cliente, Area, Servicio, Tarea, RegistroHora
import json

def exportar_datos():
    """Exporta toda la base de datos a JSON"""

    with app.app_context():
        print("="*80)
        print("EXPORTANDO DATOS A JSON")
        print("="*80)

        data = {
            'clientes': [],
            'areas': [],
            'servicios': [],
            'tareas': [],
            'registros_horas': []
        }

        # Exportar clientes
        print("\n📊 Exportando clientes...")
        for c in Cliente.query.all():
            data['clientes'].append({
                'id': c.id,
                'nombre': c.nombre,
                'tipo': c.tipo,
                'activo': c.activo
            })
        print(f"✓ {len(data['clientes'])} clientes exportados")

        # Exportar áreas
        print("\n📂 Exportando áreas...")
        for a in Area.query.all():
            data['areas'].append({
                'id': a.id,
                'nombre': a.nombre,
                'activo': a.activo
            })
        print(f"✓ {len(data['areas'])} áreas exportadas")

        # Exportar servicios
        print("\n⚙️  Exportando servicios...")
        for s in Servicio.query.all():
            data['servicios'].append({
                'id': s.id,
                'area_id': s.area_id,
                'nombre': s.nombre,
                'activo': s.activo
            })
        print(f"✓ {len(data['servicios'])} servicios exportados")

        # Exportar tareas
        print("\n📋 Exportando tareas...")
        for t in Tarea.query.all():
            data['tareas'].append({
                'id': t.id,
                'servicio_id': t.servicio_id,
                'nombre': t.nombre,
                'activo': t.activo
            })
        print(f"✓ {len(data['tareas'])} tareas exportadas")

        # Exportar registros de horas
        print("\n⏰ Exportando registros de horas...")
        total = RegistroHora.query.count()
        print(f"  Total a exportar: {total:,} registros")

        count = 0
        for r in RegistroHora.query.all():
            data['registros_horas'].append({
                'persona_id': r.persona_id,
                'cliente_id': r.cliente_id,
                'area_id': r.area_id,
                'servicio_id': r.servicio_id,
                'tarea_id': r.tarea_id,
                'fecha': str(r.fecha),
                'horas': r.horas,
                'descripcion': r.descripcion or ''
            })
            count += 1
            if count % 10000 == 0:
                print(f"  Procesados: {count:,} registros...")

        print(f"✓ {len(data['registros_horas']):,} registros de horas exportados")

        # Guardar a archivo JSON
        filename = 'datos_historicos.json'
        print(f"\n💾 Guardando en {filename}...")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Tamaño del archivo
        import os
        size_mb = os.path.getsize(filename) / (1024 * 1024)

        print("\n" + "="*80)
        print("EXPORTACIÓN COMPLETADA")
        print("="*80)
        print(f"\n📄 Archivo: {filename}")
        print(f"📊 Tamaño: {size_mb:.2f} MB")
        print(f"\n📈 Contenido:")
        print(f"  • Clientes: {len(data['clientes'])}")
        print(f"  • Áreas: {len(data['areas'])}")
        print(f"  • Servicios: {len(data['servicios'])}")
        print(f"  • Tareas: {len(data['tareas'])}")
        print(f"  • Registros de horas: {len(data['registros_horas']):,}")
        print("\n" + "="*80)
        print("\n🚀 Próximos pasos:")
        print("  1. Subir este archivo a GitHub:")
        print(f"     git add {filename}")
        print(f"     git commit -m 'feat: Datos históricos para Render'")
        print(f"     git push origin main")
        print("\n  2. En Render Shell, ejecutar:")
        print(f"     python importar_desde_json.py")
        print("="*80)

if __name__ == '__main__':
    exportar_datos()
