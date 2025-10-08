"""
Script para crear usuarios desde el archivo de costos de personal
"""
from app import app, db, Persona
import hashlib
from datetime import date

def crear_usuarios():
    """Crea usuarios desde el CSV de costos"""

    with app.app_context():
        print("Creando usuarios desde Costos_Personal.csv...")

        # Verificar si ya existen usuarios
        if Persona.query.count() > 0:
            print(f"Ya existen {Persona.query.count()} usuarios en la base de datos.")
            respuesta = input("¿Deseas eliminar todos los usuarios y crear nuevos? (s/n): ")
            if respuesta.lower() != 's':
                print("Operación cancelada.")
                return

            Persona.query.delete()
            db.session.commit()

        # Lista de usuarios del CSV (columnas: ID, Nombre, Costo Total Mensual)
        # Formato email: inicial + apellido @ comsulting.cl
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
            {'nombre': 'Jazmín Sapunar', 'costo': 3161448, 'cargo': 'Consultora', 'es_socia': False},
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
        ]

        def generar_email(nombre_completo):
            """Genera email formato: inicial + apellido @ comsulting.cl"""
            partes = nombre_completo.strip().split()
            if len(partes) >= 2:
                inicial = partes[0][0].lower()
                apellido = partes[-1].lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                return f"{inicial}{apellido}@comsulting.cl"
            return f"{nombre_completo.lower().replace(' ', '')}@comsulting.cl"

        # Contraseña por defecto
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
                costo_mensual_empresa=user_data['costo'],
                activo=True,
                fecha_ingreso=date(2020, 1, 1)  # Fecha genérica
            )

            db.session.add(persona)
            print(f"✓ {user_data['nombre']:40} | {email:30} | ${user_data['costo']:>10,}")

        db.session.commit()

        print("\n" + "="*80)
        print("USUARIOS CREADOS EXITOSAMENTE")
        print("="*80)
        print(f"Total usuarios creados: {len(usuarios)}")
        print(f"Contraseña para todos: {password_default}")
        print("="*80)
        print("\nEjemplo de login:")
        print(f"  Email: bbulnes@comsulting.cl")
        print(f"  Password: {password_default}")
        print("="*80)

if __name__ == '__main__':
    crear_usuarios()
