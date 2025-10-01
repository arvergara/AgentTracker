#!/usr/bin/env python3
"""
Script para agregar @login_required a todas las rutas protegidas
"""

# Leer el archivo
with open('app.py', 'r') as f:
    lines = f.readlines()

# Rutas que NO deben tener @login_required
exclude_routes = ['/login', '/logout']

# Procesar líneas
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)

    # Si encontramos una ruta
    if line.strip().startswith('@app.route('):
        # Verificar si es una ruta a excluir
        should_protect = True
        for exclude in exclude_routes:
            if exclude in line:
                should_protect = False
                break

        # Verificar si ya tiene @login_required en la línea siguiente
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            has_decorator = '@login_required' in next_line

            # Si debe proteger y no tiene el decorador
            if should_protect and not has_decorator and next_line.strip().startswith('def '):
                # Agregar @login_required antes de def
                new_lines.append('@login_required\n')

    i += 1

# Escribir el archivo
with open('app.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Decoradores @login_required agregados correctamente")
