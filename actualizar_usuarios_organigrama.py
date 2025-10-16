"""
Script para actualizar usuarios según el organigrama de octubre 2025
Agrega Carlos Valera que faltaba en la lista original
"""
from app import app, db, Persona
import hashlib
from datetime import date

def actualizar_usuarios():
    """Actualiza usuarios según organigrama oct 2025"""

    with app.app_context():
        print("Verificando usuarios según organigrama Oct 2025...")
        print("="*80)

        # Verificar si Carlos Valera ya existe
        carlos = Persona.query.filter_by(nombre='Carlos Valera').first()

        if carlos:
            print(f"✓ Carlos Valera ya existe en la base de datos")
            print(f"  Email: {carlos.email}")
            print(f"  Cargo: {carlos.cargo}")
            print(f"  Costo: ${carlos.costo_mensual_empresa:,.0f}")
        else:
            print("✗ Carlos Valera NO existe - AGREGANDO...")

            # Contraseña por defecto (misma que otros usuarios)
            password_default = 'comsulting2025'
            password_hash = hashlib.sha256(password_default.encode()).hexdigest()

            # Crear Carlos Valera
            carlos_data = {
                'nombre': 'Carlos Valera',
                'email': 'cvalera@comsulting.cl',
                'cargo': 'Administración y TI',
                'costo': 2500000,  # Costo estimado - ajustar según datos reales
                'es_socia': False
            }

            carlos = Persona(
                nombre=carlos_data['nombre'],
                email=carlos_data['email'],
                password_hash=password_hash,
                cargo=carlos_data['cargo'],
                es_socia=carlos_data['es_socia'],
                costo_mensual_empresa=carlos_data['costo'],
                activo=True,
                fecha_ingreso=date(2020, 1, 1)
            )

            db.session.add(carlos)
            db.session.commit()

            print(f"✓ AGREGADO: {carlos_data['nombre']}")
            print(f"  Email: {carlos_data['email']}")
            print(f"  Cargo: {carlos_data['cargo']}")
            print(f"  Costo: ${carlos_data['costo']:,}")
            print(f"  Password: {password_default}")

        print("\n" + "="*80)
        print("VERIFICACIÓN DE TODOS LOS USUARIOS DEL ORGANIGRAMA")
        print("="*80)

        # Lista completa según organigrama (página 2 y 3)
        usuarios_organigrama = [
            # SOCIAS
            'Blanca Bulnes',
            'Macarena Puigrredón',
            'Bernardita Ochagavía',
            'Carolina Romero',
            'Nicolás Marticorena',
            'Isabel Espinoza',
            'Erick Rojas',

            # ADMINISTRACIÓN
            'Jazmín Sapunar',
            'Carlos Valera',

            # CONSULTORES ASUNTOS PÚBLICOS
            'Josefa Arraztoa',
            'Sofía Martínez',

            # DIRECTOR COMUNICACIONES
            'Ángeles Pérez',
            'Andrea Tapia',
            'Constanza Pérez-Cueto',
            'Enrique Elgueta',
            'Nidia Millahueique',

            # CONSULTOR SENIOR
            'Carla Borja',
            'Carolina Rodríguez',
            'Liliana Cortes',
            'Pilar Gordillo',

            # CONSULTOR COMUNICACIONES
            'Aranza Fernández',
            'Isidora Bello',
            'Rocío Romero',

            # JEFE DE ESTUDIOS
            'José Manuel Valdivieso',

            # ANALISTA DE PRENSA
            'Ignacio Echeverría',
            'Janett Poblete',
            'Anais Sarmiento',

            # DIRECTOR DIGITAL
            'Raúl Andrés Azócar',

            # EDITORA RRSS
            'Luisa Mendoza',

            # JEFE DISEÑO
            'Mariela Moyano',
            'Kaenia Berenguel',
            'Hernán Díaz',
            'Christian Orrego',

            # ANALISTA DIGITAL
            'Ignacio Diaz',
            'Leonardo Pezoa',

            # COMMUNITY MANAGER
            'Francisca Carlino',
            'Pedro Pablo Thies',

            # OTROS (página 3)
            'Victor Guillou',
        ]

        print(f"\nTotal usuarios según organigrama: {len(usuarios_organigrama)}")

        # Verificar cada uno
        faltantes = []
        for nombre_org in usuarios_organigrama:
            # Normalizar nombre para búsqueda flexible
            persona = Persona.query.filter(
                Persona.nombre.ilike(f'%{nombre_org.split()[0]}%')
            ).filter(
                Persona.nombre.ilike(f'%{nombre_org.split()[-1]}%')
            ).first()

            if persona:
                print(f"✓ {nombre_org:40} -> {persona.email}")
            else:
                print(f"✗ {nombre_org:40} -> FALTANTE")
                faltantes.append(nombre_org)

        print("\n" + "="*80)
        if faltantes:
            print(f"⚠️  USUARIOS FALTANTES: {len(faltantes)}")
            for nombre in faltantes:
                print(f"   - {nombre}")
        else:
            print("✓ TODOS LOS USUARIOS DEL ORGANIGRAMA ESTÁN EN LA BASE DE DATOS")
        print("="*80)

        # Estadísticas finales
        total_db = Persona.query.count()
        socias = Persona.query.filter_by(es_socia=True).count()
        activos = Persona.query.filter_by(activo=True).count()

        print(f"\nEstadísticas:")
        print(f"  Total en DB: {total_db}")
        print(f"  Socias: {socias}")
        print(f"  Activos: {activos}")
        print(f"  Según organigrama: {len(usuarios_organigrama)}")
        print("="*80)

if __name__ == '__main__':
    actualizar_usuarios()
