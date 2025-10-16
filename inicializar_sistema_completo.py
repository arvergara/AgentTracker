"""
Script maestro para inicializar el sistema completo con jerarquía

Pasos:
1. Crea la base de datos con el nuevo esquema (incluye es_admin y reporte_a_id)
2. Crea todos los usuarios
3. Configura administradores y jerarquía según organigrama
"""

from app import app, db, Persona
import hashlib
from datetime import date

def inicializar_sistema():
    """Inicializa el sistema completo"""

    with app.app_context():
        print("="*80)
        print("INICIALIZACIÓN COMPLETA DEL SISTEMA AGENTTRACKER")
        print("="*80)

        # Paso 1: Crear esquema
        print("\n1. CREANDO ESQUEMA DE BASE DE DATOS...")
        print("-"*80)

        # Eliminar todas las tablas primero
        db.drop_all()

        # Crear todas las tablas con el nuevo esquema
        db.create_all()
        print("✓ Esquema creado (con es_admin y reporte_a_id)")

        # Paso 2: Crear usuarios
        print("\n2. CREANDO USUARIOS...")
        print("-"*80)

        usuarios = [
            {'nombre': 'Blanca Bulnes', 'costo': 7419495, 'cargo': 'Socia', 'es_socia': True},
            {'nombre': 'María Macarena Puigrredon', 'costo': 7419494, 'cargo': 'Socia', 'es_socia': True},
            {'nombre': 'María Bernardita Ochagavia', 'costo': 6550324, 'cargo': 'Directora', 'es_socia': False},
            {'nombre': 'Carolina Romero', 'costo': 6471115, 'cargo': 'Directora', 'es_socia': False},
            {'nombre': 'Nicolás Marticorena', 'costo': 6931883, 'cargo': 'Director', 'es_socia': False},
            {'nombre': 'Isabel Espinoza', 'costo': 6563236, 'cargo': 'Directora', 'es_socia': False},
            {'nombre': 'Erick Rojas', 'costo': 6573437, 'cargo': 'Director', 'es_socia': False},
            {'nombre': 'Raúl Andrés Azócar', 'costo': 2643085, 'cargo': 'Consultor Senior', 'es_socia': False},
            {'nombre': 'María De Los Ángeles Pérez', 'costo': 4802869, 'cargo': 'Consultora Senior', 'es_socia': False},
            {'nombre': 'Constanza Pérez-Cueto', 'costo': 4893305, 'cargo': 'Consultora Senior', 'es_socia': False},
            {'nombre': 'Andrea Tapia', 'costo': 4303868, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Juana Nidia Millahueique', 'costo': 4013336, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Enrique Elgueta', 'costo': 4519075, 'cargo': 'Consultor', 'es_socia': False},
            {'nombre': 'Jazmín Sapunar', 'costo': 3161448, 'cargo': 'Administración', 'es_socia': False},
            {'nombre': 'Luisa Mendoza', 'costo': 3224194, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Josefa Arraztoa', 'costo': 3323825, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Carolina Rodríguez', 'costo': 3646830, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Carla Borja', 'costo': 3133265, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Pilar Gordillo', 'costo': 2986826, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Liliana Cortes', 'costo': 3002780, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Victor Guillou', 'costo': 2581520, 'cargo': 'Consultor', 'es_socia': False},
            {'nombre': 'José Manuel Valdivieso', 'costo': 2853744, 'cargo': 'Consultor', 'es_socia': False},
            {'nombre': 'Aranza Fernández', 'costo': 3264626, 'cargo': 'Consultora', 'es_socia': False},
            {'nombre': 'Isidora Bello', 'costo': 2556239, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Mariela Moyano', 'costo': 2064861, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Leonardo Pezoa', 'costo': 1981235, 'cargo': 'Consultor Junior', 'es_socia': False},
            {'nombre': 'Janett Poblete', 'costo': 1373781, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Luis Ignacio Echeverría', 'costo': 1638976, 'cargo': 'Consultor Junior', 'es_socia': False},
            {'nombre': 'Kaenia Berenguel', 'costo': 2009251, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Pedro Pablo Thies', 'costo': 1434261, 'cargo': 'Consultor Junior', 'es_socia': False},
            {'nombre': 'Anais Sarmiento', 'costo': 1000410, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Ignacio Diaz', 'costo': 1338768, 'cargo': 'Consultor Junior', 'es_socia': False},
            {'nombre': 'Rocío Romero', 'costo': 1250000, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Sofía Martínez', 'costo': 973225, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Christian Orrego', 'costo': 887784, 'cargo': 'Consultor Junior', 'es_socia': False},
            {'nombre': 'Francisca Carlino', 'costo': 1425437, 'cargo': 'Consultora Junior', 'es_socia': False},
            {'nombre': 'Hernán Díaz', 'costo': 1793767, 'cargo': 'Consultor Junior', 'es_socia': False},
            {'nombre': 'Carlos Valera', 'costo': 2500000, 'cargo': 'Administración y TI', 'es_socia': False},
        ]

        def generar_email(nombre_completo):
            """Genera email formato: inicial + apellido @ comsulting.cl"""
            partes = nombre_completo.strip().split()
            if len(partes) >= 2:
                inicial = partes[0][0].lower()
                apellido = partes[-1].lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                return f"{inicial}{apellido}@comsulting.cl"
            return f"{nombre_completo.lower().replace(' ', '')}@comsulting.cl"

        password_default = 'comsulting2025'
        password_hash = hashlib.sha256(password_default.encode()).hexdigest()

        for user_data in usuarios:
            email = generar_email(user_data['nombre'])

            persona = Persona(
                nombre=user_data['nombre'],
                email=email,
                password_hash=password_hash,
                cargo=user_data['cargo'],
                es_socia=user_data['es_socia'],
                es_admin=False,  # Se configurará después
                reporte_a_id=None,  # Se configurará después
                costo_mensual_empresa=user_data['costo'],
                activo=True,
                fecha_ingreso=date(2020, 1, 1)
            )

            db.session.add(persona)

        db.session.commit()
        print(f"✓ {len(usuarios)} usuarios creados")

        # Paso 3: Configurar administradores
        print("\n3. CONFIGURANDO ADMINISTRADORES...")
        print("-"*80)

        admins = [
            'bbulnes@comsulting.cl',
            'mpuigrredon@comsulting.cl',
            'jsapunar@comsulting.cl',
        ]

        for email in admins:
            persona = Persona.query.filter_by(email=email).first()
            if persona:
                persona.es_admin = True
                print(f"✓ {persona.nombre}")

        db.session.commit()

        # Paso 4: Configurar jerarquía
        print("\n4. CONFIGURANDO JERARQUÍA...")
        print("-"*80)

        def buscar(nombre_parcial):
            partes = nombre_parcial.strip().split()
            query = Persona.query
            for parte in partes:
                query = query.filter(Persona.nombre.ilike(f'%{parte}%'))
            return query.first()

        def asignar(sub_nombre, sup_nombre):
            sub = buscar(sub_nombre)
            sup = buscar(sup_nombre)
            if sub and sup:
                sub.reporte_a_id = sup.id
                return True
            return False

        # Reportes según organigrama
        reportes = [
            # Blanca Bulnes
            ("Josefa Arraztoa", "Blanca Bulnes"),
            ("Sofía Martínez", "Blanca Bulnes"),
            ("Andrés Azócar", "Blanca Bulnes"),
            ("José Manuel Valdivieso", "Blanca Bulnes"),

            # Macarena Puigrredón
            ("Luisa Mendoza", "Macarena Puigrredon"),
            ("Mariela Moyano", "Macarena Puigrredon"),
            ("Kaenia Berenguel", "Macarena Puigrredon"),
            ("Christian Orrego", "Macarena Puigrredon"),
            ("Hernán Díaz", "Macarena Puigrredon"),
            ("Pedro Pablo Thies", "Macarena Puigrredon"),
            ("Ignacio Diaz", "Macarena Puigrredon"),
            ("Francisca Carlino", "Macarena Puigrredon"),
            ("Leonardo Pezoa", "Macarena Puigrredon"),

            # Bernardita Ochagavía
            ("Carolina Rodríguez", "Bernardita Ochagavia"),
            ("Isidora Bello", "Bernardita Ochagavia"),
            ("Janett Poblete", "Bernardita Ochagavia"),
            ("Rocío Romero", "Bernardita Ochagavia"),
            ("Aranza Fernández", "Bernardita Ochagavia"),

            # Carolina Romero
            ("Ángeles Pérez", "Carolina Romero"),
            ("Constanza Pérez-Cueto", "Carolina Romero"),
            ("Victor Guillou", "Carolina Romero"),
            ("Enrique Elgueta", "Carolina Romero"),

            # Nicolás Marticorena
            ("Andrea Tapia", "Nicolás Marticorena"),
            ("Carla Borja", "Nicolás Marticorena"),
            ("Nidia Millahueique", "Nicolás Marticorena"),
            ("Pilar Gordillo", "Nicolás Marticorena"),
            ("Liliana Cortes", "Nicolás Marticorena"),

            # Isabel Espinoza
            ("Ignacio Echeverría", "Isabel Espinoza"),
            ("Anais Sarmiento", "Isabel Espinoza"),
        ]

        for sub, sup in reportes:
            if asignar(sub, sup):
                print(f"✓ {sub} → {sup}")

        db.session.commit()

        # Resumen final
        print("\n" + "="*80)
        print("✓ SISTEMA INICIALIZADO EXITOSAMENTE")
        print("="*80)

        print(f"\nTotal usuarios: {Persona.query.count()}")
        print(f"Administradores: {Persona.query.filter_by(es_admin=True).count()}")
        print(f"Con supervisor: {Persona.query.filter(Persona.reporte_a_id != None).count()}")

        print("\nCredenciales de acceso:")
        print(f"  Password: {password_default}")
        print(f"\nEjemplos de login:")
        print(f"  Admin: bbulnes@comsulting.cl")
        print(f"  Socia: mochagavia@comsulting.cl")
        print(f"  Usuario: crodriguez@comsulting.cl")

        print("\n" + "="*80)

if __name__ == '__main__':
    inicializar_sistema()
