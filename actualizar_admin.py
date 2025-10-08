"""
Script para actualizar los permisos de administrador (es_socia)
"""
from app import app, db, Persona
import hashlib
from datetime import date

def actualizar_admin():
    """Actualiza los permisos de administrador"""

    with app.app_context():
        print("Actualizando permisos de administrador...")

        # Emails de administradores
        admin_emails = [
            'bbulnes@comsulting.cl',
            'mpuigrredon@comsulting.cl',
            'jsapunar@comsulting.cl',
            'andres.vergara@maindset.cl'
        ]

        # Primero, quitar permisos de admin a todos
        Persona.query.update({'es_socia': False})
        db.session.commit()

        # Luego, otorgar permisos solo a los administradores
        for email in admin_emails:
            persona = Persona.query.filter_by(email=email).first()

            if persona:
                persona.es_socia = True
                print(f"✓ Admin: {persona.nombre} ({email})")
            else:
                # Si no existe (caso de andres.vergara), crear el usuario
                if email == 'andres.vergara@maindset.cl':
                    password_hash = hashlib.sha256('comsulting2025'.encode()).hexdigest()

                    nuevo_admin = Persona(
                        nombre='Andrés Vergara',
                        email=email,
                        password_hash=password_hash,
                        cargo='Desarrollador',
                        es_socia=True,
                        costo_mensual_empresa=0,
                        activo=True,
                        fecha_ingreso=date.today()
                    )
                    db.session.add(nuevo_admin)
                    print(f"✓ Admin CREADO: Andrés Vergara ({email})")
                else:
                    print(f"✗ No encontrado: {email}")

        db.session.commit()

        print("\n" + "="*60)
        print("PERMISOS ACTUALIZADOS")
        print("="*60)
        print(f"\nAdministradores con acceso completo:")

        admins = Persona.query.filter_by(es_socia=True).all()
        for admin in admins:
            print(f"  • {admin.nombre} - {admin.email}")

        print("\n" + "="*60)

if __name__ == '__main__':
    actualizar_admin()
