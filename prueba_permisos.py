"""
Script de prueba para verificar que el sistema de permisos jerárquicos funciona correctamente
"""

from app import app, db, Persona

def prueba_permisos():
    """Prueba el sistema de permisos con diferentes usuarios"""

    with app.app_context():
        print("="*80)
        print("PRUEBA DE SISTEMA DE PERMISOS JERÁRQUICOS")
        print("="*80)

        # Test 1: Administradores ven todo
        print("\n📋 TEST 1: Administradores ven TODO")
        print("-"*80)

        blanca = Persona.query.filter(Persona.nombre.ilike('%Blanca%')).first()
        if blanca:
            ids_visibles = blanca.obtener_personas_visibles()
            print(f"{blanca.nombre}:")
            print(f"  - Es admin: {blanca.es_admin}")
            print(f"  - Puede ver: {len(ids_visibles)} personas (de {Persona.query.count()} totales)")
            print(f"  - ✓ CORRECTO" if len(ids_visibles) == Persona.query.count() else "  - ✗ ERROR")

        # Test 2: Socia ve solo sus reportes directos
        print("\n👔 TEST 2: Socia ve solo REPORTES DIRECTOS")
        print("-"*80)

        bernardita = Persona.query.filter(Persona.nombre.ilike('%Bernardita%')).first()
        if bernardita:
            subordinados = Persona.query.filter_by(reporte_a_id=bernardita.id).all()
            ids_visibles = bernardita.obtener_personas_visibles()

            print(f"{bernardita.nombre}:")
            print(f"  - Es admin: {bernardita.es_admin}")
            print(f"  - Subordinados directos: {len(subordinados)}")
            print(f"  - Puede ver: {len(ids_visibles)} personas (ella + subordinados)")
            print(f"\n  Subordinados directos:")
            for sub in subordinados:
                print(f"    • {sub.nombre}")

            # Verificar que ve solo a ella + subordinados
            esperado = len(subordinados) + 1  # ella + subordinados
            print(f"\n  - Esperado: {esperado}, Real: {len(ids_visibles)}")
            print(f"  - ✓ CORRECTO" if len(ids_visibles) == esperado else "  - ✗ ERROR")

            # Verificar que NO puede ver a alguien fuera de su equipo
            angeles = Persona.query.filter(Persona.nombre.ilike('%Ángeles Pérez%')).first()
            if angeles:
                puede_ver = bernardita.puede_ver_persona(angeles.id)
                print(f"\n  ¿Puede ver a Ángeles Pérez (subordinada de Carolina Romero)? {puede_ver}")
                print(f"  - ✓ CORRECTO (no debería poder ver)" if not puede_ver else "  - ✗ ERROR (no debería poder ver)")

        # Test 3: Usuario regular solo ve su info
        print("\n👤 TEST 3: Usuario regular ve solo SU PROPIA INFO")
        print("-"*80)

        carolina_rod = Persona.query.filter(Persona.nombre.ilike('%Carolina Rodríguez%')).first()
        if carolina_rod:
            ids_visibles = carolina_rod.obtener_personas_visibles()

            print(f"{carolina_rod.nombre}:")
            print(f"  - Es admin: {carolina_rod.es_admin}")
            print(f"  - Reporta a: {carolina_rod.supervisor.nombre if carolina_rod.supervisor else 'Nadie'}")
            print(f"  - Subordinados: {len(carolina_rod.subordinados)}")
            print(f"  - Puede ver: {len(ids_visibles)} personas")
            print(f"\n  Personas visibles:")
            for pid in ids_visibles:
                p = Persona.query.get(pid)
                print(f"    • {p.nombre}")

            print(f"\n  - ✓ CORRECTO (solo ella misma)" if len(ids_visibles) == 1 else "  - ✗ ERROR (debería ver solo 1)")

        # Test 4: Verificar jerarquía completa
        print("\n🌳 TEST 4: JERARQUÍA ORGANIZACIONAL COMPLETA")
        print("-"*80)

        supervisores = Persona.query.filter(Persona.subordinados.any()).all()
        print(f"\nSupervisores (personas con reportes directos): {len(supervisores)}\n")

        for sup in sorted(supervisores, key=lambda x: len(x.subordinados), reverse=True):
            subs = Persona.query.filter_by(reporte_a_id=sup.id).all()
            es_admin_text = " (ADMIN)" if sup.es_admin else ""
            print(f"{sup.nombre}{es_admin_text}:")
            print(f"  Subordinados: {len(subs)}")
            for sub in subs:
                print(f"    → {sub.nombre}")
            print()

        # Test 5: Resumen estadístico
        print("="*80)
        print("RESUMEN ESTADÍSTICO")
        print("="*80)

        total = Persona.query.count()
        admins = Persona.query.filter_by(es_admin=True).count()
        con_supervisor = Persona.query.filter(Persona.reporte_a_id != None).count()
        sin_supervisor = Persona.query.filter_by(reporte_a_id=None).count()
        supervisores_count = len(supervisores)

        print(f"\n📊 Estadísticas:")
        print(f"  Total personas: {total}")
        print(f"  Administradores (ven todo): {admins}")
        print(f"  Supervisores (con subordinados): {supervisores_count}")
        print(f"  Con supervisor asignado: {con_supervisor}")
        print(f"  Sin supervisor (admin o sin asignar): {sin_supervisor}")

        # Verificar que todos (excepto admins y top-level) tienen supervisor
        sin_supervisor_no_admin = Persona.query.filter_by(
            reporte_a_id=None,
            es_admin=False
        ).all()

        if sin_supervisor_no_admin:
            print(f"\n⚠️  ADVERTENCIA: {len(sin_supervisor_no_admin)} personas sin supervisor (no admin):")
            for p in sin_supervisor_no_admin:
                print(f"    • {p.nombre}")
        else:
            print(f"\n✓ Todos los usuarios (excepto admins) tienen supervisor asignado")

        print("\n" + "="*80)
        print("✓ PRUEBAS COMPLETADAS")
        print("="*80)

if __name__ == '__main__':
    prueba_permisos()
