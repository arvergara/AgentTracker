# Usuarios del Sistema AgentTracker - Organigrama Oct 2025

## Resumen

Este documento detalla todos los usuarios del sistema AgentTracker según el organigrama oficial de Comsulting de octubre 2025.

**Total de usuarios**: 39 personas (incluyendo 7 socios/as)

## Estructura de Perfiles

### Socios y Gerencia (7 personas)

| Nombre | Email | Cargo | Área | Es Socia |
|--------|-------|-------|------|----------|
| Blanca Bulnes | bbulnes@comsulting.cl | Socia | Gerenta General | Sí |
| María Macarena Puigrredon | mpuigrredon@comsulting.cl | Socia | Socia Ejecutiva | Sí |
| María Bernardita Ochagavia | mochagavia@comsulting.cl | Directora | Comunicaciones | Sí* |
| Carolina Romero | cromero@comsulting.cl | Directora | Comunicaciones | Sí* |
| Nicolás Marticorena | nmarticorena@comsulting.cl | Director | Comunicaciones | Sí* |
| Isabel Espinoza | iespinoza@comsulting.cl | Directora | Digital | Sí* |
| Erick Rojas | erojas@comsulting.cl | Director | Asuntos Públicos | Sí* |

*Nota: Estos socios tienen el flag `es_socia=False` en la BD pero son socios según organigrama*

### Administración (2 personas)

| Nombre | Email | Cargo |
|--------|-------|-------|
| Jazmín Sapunar | jsapunar@comsulting.cl | Administración, Finanzas y RRHH |
| Carlos Valera | cvalera@comsulting.cl | Computación / TI |

**Nota**: Carlos Valera fue agregado según organigrama Oct 2025.

### Área Asuntos Públicos

#### Consultores (2 personas)
- Josefa Arraztoa (jarraztoa@comsulting.cl)
- Sofía Martínez (smartinez@comsulting.cl)

### Área Comunicaciones Externa e Interna

#### Directores (5 personas)
- María De Los Ángeles Pérez (mperez@comsulting.cl)
- Andrea Tapia (atapia@comsulting.cl)
- Constanza Pérez-Cueto (cperez-cueto@comsulting.cl)
- Enrique Elgueta (eelgueta@comsulting.cl)
- Juana Nidia Millahueique (jmillahueique@comsulting.cl)

#### Consultores Senior (4 personas)
- Carla Borja (cborja@comsulting.cl)
- Carolina Rodríguez (crodriguez@comsulting.cl)
- Liliana Cortes (lcortes@comsulting.cl)
- Pilar Gordillo (pgordillo@comsulting.cl)

#### Consultores (4 personas)
- Aranza Fernández (afernandez@comsulting.cl)
- Isidora Bello (ibello@comsulting.cl)
- Rocío Romero (rromero@comsulting.cl)
- Victor Guillou (vguillou@comsulting.cl)

#### Jefe de Estudios (1 persona)
- José Manuel Valdivieso (jvaldivieso@comsulting.cl)

#### Analistas de Prensa (3 personas)
- Luis Ignacio Echeverría (lecheverria@comsulting.cl)
- Janett Poblete (jpoblete@comsulting.cl)
- Anais Sarmiento (asarmiento@comsulting.cl)

### Área Digital y Diseño

#### Director Digital (1 persona)
- Raúl Andrés Azócar (razocar@comsulting.cl)

#### Editora RRSS (1 persona)
- Luisa Mendoza (lmendoza@comsulting.cl)

#### Jefe de Diseño y Diseñadores (4 personas)
- Mariela Moyano (mmoyano@comsulting.cl)
- Kaenia Berenguel (kberenguel@comsulting.cl)
- Hernán Díaz (hdiaz@comsulting.cl)
- Christian Orrego (corrego@comsulting.cl)

#### Analistas Digitales (2 personas)
- Ignacio Diaz (idiaz@comsulting.cl)
- Leonardo Pezoa (lpezoa@comsulting.cl)

#### Community Managers (2 personas)
- Francisca Carlino (fcarlino@comsulting.cl)
- Pedro Pablo Thies (pthies@comsulting.cl)

## Reportes Administrativos

Según la página 3 del organigrama, la estructura de reportes para temas administrativos es:

### Blanca Bulnes
- Josefa Arraztoa
- Sofía Martínez
- Andrés Azócar
- José Manuel Valdivieso

### Macarena Puigrredón
- Luisa Mendoza
- Mariela Moyano
- Kaenia Berenguel
- Christian Orrego
- Hernán Díaz
- Pedro Pablo Thies
- Ignacio Diaz
- Francisca Carlino
- Leonardo Pezoa

### Bernardita Ochagavía
- Carolina Rodríguez
- Isidora Bello
- Janette Poblete
- Rocío Romero
- Aranza Fernández

### Carolina Romero
- Ángeles Pérez
- Constanza Pérez-Cueto
- Víctor Guillou
- Enrique Elgueta

### Nicolás Marticorena
- Andrea Tapia
- Carla Borja
- Nidia Millahueique
- Pilar Gordillo
- Liliana Cortés

### Isabel Espinoza
- Ignacio Echeverría
- Anais Sarmiento

### Erick Rojas
(Sin reportes directos en el organigrama)

### Jazmín Sapunar
- Administración general

## Credenciales de Acceso

**Contraseña por defecto para todos los usuarios**: `comsulting2025`

**Formato de email**: `{inicial}{apellido}@comsulting.cl`

Ejemplo:
- Blanca Bulnes → bbulnes@comsulting.cl
- Carlos Valera → cvalera@comsulting.cl

## Scripts de Gestión

### Crear todos los usuarios
```bash
python crear_usuarios.py
```

### Verificar usuarios según organigrama
```bash
python actualizar_usuarios_organigrama.py
```

Este script:
- Verifica que todos los usuarios del organigrama estén en la BD
- Agrega Carlos Valera si no existe
- Muestra estadísticas de usuarios

## Notas Importantes

1. **Carlos Valera** fue agregado manualmente el 2025-10-15 basándose en el organigrama de octubre 2025
2. Los costos mensuales están expresados en pesos chilenos
3. El sistema calcula automáticamente el costo por hora en UF usando `VALOR_UF_ACTUAL = 38000`
4. Las socias (Blanca Bulnes y Macarena Puigrredón) tienen `es_socia=True` y pueden ver información completa del sistema
5. El resto de los directores/socios tienen `es_socia=False` en la BD actual

## Áreas de Comsulting

Según el organigrama:

1. **Comunicación externa e interna** (rojo)
2. **Digital y diseño** (verde)
3. **Asuntos públicos** (azul)

## Actualización de Datos

Para actualizar los datos de costos de personal, modificar el archivo CSV `Costos_Personal.csv` y ejecutar el script `crear_usuarios.py`.

---

**Última actualización**: 15 de octubre de 2025
**Fuente**: Comsulting_organigrama_oct2025 (1).pdf
