"""
Script para configurar la jerarquía organizacional según el organigrama Oct 2025

Este script:
1. Marca a Blanca Bulnes, Macarena Puigrredón y Jazmín Sapunar como administradoras (es_admin=True)
2. Asigna las relaciones de reporte (reporte_a_id) según la página 3 del organigrama

Reglas de permisos:
- Admin (es_admin=True): Ven TODO
- Socios/Directores: Solo ven a sus reportes DIRECTOS
- Resto: Solo ven su propia información
"""

from app import app, db, Persona

def configurar_jerarquia():
    """Configura la jerarquía según organigrama Oct 2025"""

    with app.app_context():
        print("="*80)
        print("CONFIGURACIÓN DE JERARQUÍA ORGANIZACIONAL")
        print("="*80)

        # Paso 1: Marcar administradores
        print("\n1. CONFIGURANDO ADMINISTRADORES (acceso total)")
        print("-"*80)

        admins_emails = [
            'bbulnes@comsulting.cl',        # Blanca Bulnes - Gerenta General
            'mpuigrredon@comsulting.cl',    # Macarena Puigrredón - Socia Ejecutiva
            'jsapunar@comsulting.cl',       # Jazmín Sapunar - Admin y Finanzas
        ]

        # Primero, quitar permisos de admin a todos
        Persona.query.update({'es_admin': False})
        db.session.commit()

        for email in admins_emails:
            persona = Persona.query.filter_by(email=email).first()
            if persona:
                persona.es_admin = True
                print(f"✓ Admin: {persona.nombre:40} ({email})")
            else:
                print(f"✗ NO ENCONTRADO: {email}")

        db.session.commit()

        # Paso 2: Configurar relaciones de reporte según organigrama página 3
        print("\n2. CONFIGURANDO RELACIONES DE REPORTE")
        print("-"*80)

        # Limpiar todas las relaciones primero
        Persona.query.update({'reporte_a_id': None})
        db.session.commit()

        def buscar_persona(nombre_parcial):
            """Busca persona por nombre parcial"""
            partes = nombre_parcial.strip().split()
            query = Persona.query
            for parte in partes:
                query = query.filter(Persona.nombre.ilike(f'%{parte}%'))
            return query.first()

        def asignar_supervisor(subordinado_nombre, supervisor_nombre):
            """Asigna supervisor a un subordinado"""
            subordinado = buscar_persona(subordinado_nombre)
            supervisor = buscar_persona(supervisor_nombre)

            if subordinado and supervisor:
                subordinado.reporte_a_id = supervisor.id
                print(f"  • {subordinado.nombre:35} → {supervisor.nombre}")
                return True
            else:
                if not subordinado:
                    print(f"  ✗ NO ENCONTRADO: {subordinado_nombre}")
                if not supervisor:
                    print(f"  ✗ SUPERVISOR NO ENCONTRADO: {supervisor_nombre}")
                return False

        # Reportes a BLANCA BULNES
        print("\nReportan a BLANCA BULNES:")
        asignar_supervisor("Josefa Arraztoa", "Blanca Bulnes")
        asignar_supervisor("Sofía Martínez", "Blanca Bulnes")
        asignar_supervisor("Andrés Azócar", "Blanca Bulnes")
        asignar_supervisor("José Manuel Valdivieso", "Blanca Bulnes")

        # Reportes a MACARENA PUIGRREDÓN
        print("\nReportan a MACARENA PUIGRREDÓN:")
        asignar_supervisor("Luisa Mendoza", "Macarena Puigrredon")
        asignar_supervisor("Mariela Moyano", "Macarena Puigrredon")
        asignar_supervisor("Kaenia Berenguel", "Macarena Puigrredon")
        asignar_supervisor("Christian Orrego", "Macarena Puigrredon")
        asignar_supervisor("Hernán Díaz", "Macarena Puigrredon")
        asignar_supervisor("Pedro Pablo Thies", "Macarena Puigrredon")
        asignar_supervisor("Ignacio Diaz", "Macarena Puigrredon")
        asignar_supervisor("Francisca Carlino", "Macarena Puigrredon")
        asignar_supervisor("Leonardo Pezoa", "Macarena Puigrredon")

        # Reportes a BERNARDITA OCHAGAVÍA
        print("\nReportan a BERNARDITA OCHAGAVÍA:")
        asignar_supervisor("Carolina Rodríguez", "Bernardita Ochagavia")
        asignar_supervisor("Isidora Bello", "Bernardita Ochagavia")
        asignar_supervisor("Janett Poblete", "Bernardita Ochagavia")
        asignar_supervisor("Rocío Romero", "Bernardita Ochagavia")
        asignar_supervisor("Aranza Fernández", "Bernardita Ochagavia")

        # Reportes a CAROLINA ROMERO
        print("\nReportan a CAROLINA ROMERO:")
        asignar_supervisor("Ángeles Pérez", "Carolina Romero")
        asignar_supervisor("Constanza Pérez-Cueto", "Carolina Romero")
        asignar_supervisor("Victor Guillou", "Carolina Romero")
        asignar_supervisor("Enrique Elgueta", "Carolina Romero")

        # Reportes a NICOLÁS MARTICORENA
        print("\nReportan a NICOLÁS MARTICORENA:")
        asignar_supervisor("Andrea Tapia", "Nicolás Marticorena")
        asignar_supervisor("Carla Borja", "Nicolás Marticorena")
        asignar_supervisor("Nidia Millahueique", "Nicolás Marticorena")
        asignar_supervisor("Pilar Gordillo", "Nicolás Marticorena")
        asignar_supervisor("Liliana Cortes", "Nicolás Marticorena")

        # Reportes a ISABEL ESPINOZA
        print("\nReportan a ISABEL ESPINOZA:")
        asignar_supervisor("Ignacio Echeverría", "Isabel Espinoza")
        asignar_supervisor("Anais Sarmiento", "Isabel Espinoza")

        # Reportes a JOSÉ MANUEL VALDIVIESO (aunque él reporta a Blanca, tiene subordinados)
        print("\nReportan a JOSÉ MANUEL VALDIVIESO:")
        asignar_supervisor("Ignacio Echeverría", "José Manuel Valdivieso")  # También reporta aquí según org.
        asignar_supervisor("Anais Sarmiento", "José Manuel Valdivieso")

        db.session.commit()

        # Paso 3: Resumen y verificación
        print("\n" + "="*80)
        print("RESUMEN DE CONFIGURACIÓN")
        print("="*80)

        # Administradores
        admins = Persona.query.filter_by(es_admin=True).all()
        print(f"\n📋 Administradores (acceso total): {len(admins)}")
        for admin in admins:
            print(f"  • {admin.nombre:40} - {admin.email}")

        # Supervisores (personas con subordinados)
        supervisores = Persona.query.filter(Persona.subordinados.any()).all()
        print(f"\n👔 Supervisores (con reportes directos): {len(supervisores)}")
        for sup in supervisores:
            subordinados = Persona.query.filter_by(reporte_a_id=sup.id, activo=True).all()
            print(f"\n  {sup.nombre} ({len(subordinados)} subordinados):")
            for sub in subordinados:
                print(f"    → {sub.nombre}")

        # Personas sin supervisor (además de los admin)
        sin_supervisor = Persona.query.filter_by(reporte_a_id=None, activo=True).filter_by(es_admin=False).all()
        if sin_supervisor:
            print(f"\n⚠️  Personas SIN supervisor asignado (además de admins): {len(sin_supervisor)}")
            for persona in sin_supervisor:
                print(f"  • {persona.nombre}")

        print("\n" + "="*80)
        print("✓ CONFIGURACIÓN COMPLETADA")
        print("="*80)

        # Ejemplos de permisos
        print("\n📖 EJEMPLOS DE PERMISOS:")
        print("-"*80)

        # Ejemplo 1: Bernardita
        bernardita = Persona.query.filter(Persona.nombre.ilike('%Bernardita%')).first()
        if bernardita:
            print(f"\n{bernardita.nombre}:")
            print(f"  - Es admin: {bernardita.es_admin}")
            print(f"  - Puede ver a:")
            for pid in bernardita.obtener_personas_visibles():
                p = Persona.query.get(pid)
                if p:
                    print(f"    • {p.nombre}")

        # Ejemplo 2: Carolina Rodríguez (subordinada de Bernardita)
        carolina_rod = Persona.query.filter(Persona.nombre.ilike('%Carolina Rodríguez%')).first()
        if carolina_rod:
            print(f"\n{carolina_rod.nombre}:")
            print(f"  - Es admin: {carolina_rod.es_admin}")
            print(f"  - Reporta a: {carolina_rod.supervisor.nombre if carolina_rod.supervisor else 'Nadie'}")
            print(f"  - Puede ver a:")
            for pid in carolina_rod.obtener_personas_visibles():
                p = Persona.query.get(pid)
                if p:
                    print(f"    • {p.nombre}")

        print("\n" + "="*80)

if __name__ == '__main__':
    configurar_jerarquia()
