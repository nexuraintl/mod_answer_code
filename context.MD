# Guía de Estilo y Desarrollo de la Plataforma

## 1. Introducción

Este documento es la guía de referencia para todo el desarrollo realizado en la plataforma. Su objetivo es asegurar que el código sea **consistente, mantenible, seguro y de alta calidad**.

Seguir estas directrices no es opcional. Un código estandarizado facilita la colaboración, reduce los errores y simplifica el proceso de incorporación de nuevos desarrolladores.

## 2. La Regla de Oro: Consistencia

Si te encuentras en una situación no cubierta por esta guía, la regla principal es: **sé consistente con el código existente a tu alrededor**.

Si el código existente viola esta guía, tómate un momento para corregirlo. La calidad es una responsabilidad compartida.

## 3. Estándares de Codificación PHP

Nos adherimos estrictamente a los estándares **PSR-1 (Basic Coding Standard)** y **PSR-12 (Extended Coding Style)**. A continuación, se resumen los puntos más importantes.

### 3.1. Formato de Archivo
- **Etiquetas PHP:** Usar `<?php` y `<?=`. Omitir la etiqueta de cierre `?>` en archivos que solo contienen PHP.
- **Codificación:** UTF-8 sin BOM.
- **Efectos Secundarios:** Un archivo DEBE declarar símbolos (clases, funciones, constantes, etc.) o DEBE ejecutar lógica con efectos secundarios (ej. generar salida, modificar `.ini` settings), pero NO DEBE hacer ambas cosas.

### 3.2. Nomenclatura
- **Clases, Traits, Interfaces:** `PascalCase`.
- **Métodos:** `camelCase`.
- **Constantes:** `UPPER_CASE_WITH_UNDERSCORES`.
- **Propiedades y Variables:** `camelCase`.
- **Coherencia:** Los nombres DEBEN ser descriptivos y tener coherencia con el dato que almacenan.
- **Idioma:** Los nombres de clases, métodos, propiedades y variables DEBEN estar en **inglés**. Los comentarios y la documentación DEBEN estar en **español**.

### 3.2.1. Constantes de Lenguaje

-   **Regla Fundamental:** Todo texto que se muestre al usuario final (mensajes de éxito/error, títulos, etiquetas de botones, textos de correos, etc.) DEBE ser definido como una constante de lenguaje. Está **ESTRICTAMENTE PROHIBIDO** usar cadenas de texto ("hardcoded strings") directamente en controladores, clases de gestión o vistas.

-   **Ubicación:** Las constantes se definen en los archivos PHP dentro del directorio `/lang/` de cada módulo, como se especifica en la guía de desarrollo.
    -   `lang/default/global.php`: Para constantes globales del módulo.
    -   `lang/default/[nombre_controlador].php`: Para constantes específicas de un controlador.

-   **Nomenclatura:** Para mantener la claridad y evitar colisiones, las constantes DEBEN seguir el formato `[NOMBREMODULO]_[ENTIDAD]_[CONCEPTO]`.
    -   **Ejemplos Correctos:**
        -   `GFILES_RADICADO_CREADO_EXITO`
        -   `GFILES_VALIDACION_CAMPO_REQUERIDO`
        -   `GFILES_NOTIFICACION_ASUNTO_NUEVA_SOLICITUD`

**Ejemplo de Implementación Correcta (extraído de `Gfiles/lang/default/SignaturaElectronica.php`):**

```php
define("GFILES_SIGNATURAELECTRONICA_TITTLE_BTN_JSTREE","Seleccionar signatura");
define("GFILES_E_SIGNATURAELECTRONICA_TREE_SELECTION_MESSAGE","Debe seleccionar el &uacute;ltimo nivel");
```

### 3.2.2. Constantes para Cadenas Mágicas (Magic Strings)

-   **Regla:** Cualquier cadena de texto literal (conocida como "magic string") o número ("magic number") que se repita **3 o más veces** dentro de un mismo archivo DEBE ser declarado como una constante.

-   **Justificación:** Esta práctica mejora drásticamente la mantenibilidad, ya que el valor se puede cambiar en un único lugar. También reduce el riesgo de errores tipográficos en valores críticos que no serían detectados por el sistema.

-   **Alcance:** Esta regla se aplica a valores que **no** son para el usuario final (los cuales ya están cubiertos por la sección 3.2.1). Algunos ejemplos comunes son:
    -   Nombres de columnas de base de datos.
    -   Claves de arrays.
    -   Valores fijos usados en la lógica de negocio.

-   **Nomenclatura:** Las constantes DEBEN seguir el formato `UPPER_CASE_WITH_UNDERSCORES`. Si la constante es específica para una clase, se DEBE usar `private const` o `public const` según sea necesario, lo cual es la práctica recomendada.

### 3.2.3. Constantes de Configuración

-   **Regla:** Cualquier valor que actúe como un parámetro de configuración del sistema DEBE ser definido como una constante. Estos valores son "parametrizables" porque pueden cambiar entre diferentes entornos (desarrollo, producción) o para diferentes clientes.

-   **Justificación:** Centralizar la configuración en constantes facilita la modificación del comportamiento de la aplicación sin tener que buscar y reemplazar valores "mágicos" en el código. Esto es crucial para la mantenibilidad y para adaptar la plataforma a necesidades específicas.

-   **Alcance:** Esta regla se aplica a valores como:
    -   Límites (ej. tamaño máximo de archivo, número de ítems por página).
    -   Valores por defecto (ej. rol de usuario por defecto, extensiones de archivo permitidas).
    -   Parámetros de comportamiento (ej. dirección de correo del remitente, prefijos de asunto).

-   **Ubicación y Nomenclatura:**
    -   **Globales:** Las constantes de configuración que aplican a toda la plataforma DEBEN definirse en `librerias/config/sx/constantes.php` y seguir el formato `SX_CONFIG_[AREA]_[PARAMETRO]`.
    -   **Por Módulo:** Las constantes específicas de un módulo DEBEN definirse en `mod/[NombreModulo]/lib/vars.php` o en la clase `Config` del módulo y seguir el formato `[NOMBREMODULO]_CONFIG_[PARAMETRO]`.

### 3.3. Estructura
- **Indentación:** 4 espacios, no tabuladores.
- **Líneas:** No deben superar los 120 caracteres.
- **Sentencias:** Cada línea DEBE contener una única sentencia.
- **Visibilidad:** DEBE declararse en todas las propiedades y métodos (`public`, `protected`, `private`).
- **Estructuras de Control:** `if`, `foreach`, etc., deben tener llaves `{}` incluso para bloques de una sola línea. La palabra clave `elseif` se usa en lugar de `else if`.
- **Funciones de Depuración:** El código finalizado NO DEBE contener llamadas a `var_dump()`, `print_r()`, `die()` o `sleep()`, ni siquiera comentadas.

### 3.4. Aprovechamiento de PHP 8.1+
- **Tipos Estrictos:** Todos los archivos PHP DEBEN empezar con `declare(strict_types=1);` después de la etiqueta de apertura `<?php`. Esto previene errores de coerción de tipos.
- **Enums:** Para valores que representan un conjunto finito de estados (ej. status de un artículo, roles de usuario), se DEBE utilizar `Enums` en lugar de constantes de clase o "magic strings".
- **Propiedades Readonly:** Para objetos de transferencia de datos (DTOs) o Value Objects, se DEBEN usar propiedades `readonly` para garantizar su inmutabilidad.
- **Promoción de Propiedades del Constructor:** Para reducir el código repetitivo en clases simples, se DEBE usar la promoción de propiedades en el constructor.
- **Expresiones `match`:** Para comparaciones complejas que devuelven un valor, se DEBE preferir la expresión `match` sobre la estructura `switch` por ser más estricta y legible.
- **Atributo `#[AllowDynamicProperties]` (PHP 8.2+):**
    - **Contexto:** A partir de PHP 8.2, la creación de propiedades dinámicas (asignar un valor a una propiedad no declarada) está obsoleta y lanzará un error fatal en PHP 9.0.
    - **Propósito:** El atributo `#[AllowDynamicProperties]` se utiliza para suprimir esta advertencia de obsolescencia en clases específicas, permitiendo una transición más suave para el código heredado.
    - **Uso (Solución Temporal):** Se DEBE usar como una medida temporal en clases que dependen de propiedades dinámicas y no pueden ser refactorizadas inmediatamente.
        ```php
        #[\AllowDynamicProperties]
        class MiClaseHeredada
        {
            // ...
        }
        ```
    - **Recomendación (Solución Definitiva):** La práctica recomendada es **NO** usar este atributo. En su lugar, se DEBE refactorizar la clase para declarar explícitamente todas sus propiedades. Esto mejora la legibilidad, previene errores y permite un mejor análisis estático del código.

## 4. Documentación del Proyecto

### 4.1. Documentación de Código (PHPDoc)
- Todos los archivos, clases, métodos y funciones DEBEN tener un "DocBlock" en formato **PHPDoc**.
- El DocBlock debe describir el propósito del elemento, sus parámetros (`@param`), su valor de retorno (`@return`) y las excepciones que puede lanzar (`@throws`).

    ```php
    /**
     * Genera una miniatura para una imagen específica.
     *
     * Esta función localiza la imagen original, calcula las dimensiones
     * y utiliza Imagick para crear la versión en miniatura.
     *
     * @category   Utils
     * @package    Nexura\Thumbnail
     * @subpackage lib
     * @param      string      $module   El módulo al que pertenece la imagen.
     * @param      int         $id       El ID de la imagen.
     * @return     string|null La ruta a la miniatura o null si falla.
     */
    public function generateThumbs(string $module, int $id): ?string
    {
        // ...
    }
    ```
- **Generación Automática:** Se recomienda el uso de herramientas como **phpDocumentor** o **ApiGen** para generar automáticamente un manual de API navegable a partir de estos comentarios.

### 4.2. Documentación de Arquitectura
- **geners Markdown:** La documentación de alto nivel sobre la arquitectura, las decisiones de diseño y las guías de contribución DEBE mantenerse en archivos Markdown dentro del repositorio.
    - `README.md`: Puerta de entrada al proyecto. Explica qué es y cómo empezar.
    - `CONTRIBUTING.md`: Guía para nuevos contribuidores.
    - `STYLEGUIDE.MD` (este archivo): La guía de estilo y desarrollo.
- **Diagramas como Código:** Para visualizar la arquitectura, se DEBE utilizar la sintaxis de **Mermaid.js** dentro de los archivos Markdown. Esto permite versionar los diagramas junto con el código. GitHub renderiza estos diagramas automáticamente.

### 4.3. Manuales de Usuario (Docs as Code)
- **Filosofía:** La documentación para el usuario final (manuales de módulo) DEBE seguir el enfoque de **"Docs as Code"**. Esto implica escribir la documentación en un formato de texto plano, versionarla en Git y publicarla de forma automatizada.
- **Formato:** Se DEBE utilizar **Markdown** para escribir los manuales.
- **Herramientas:** Se recomienda el uso de generadores de sitios estáticos como **MkDocs** o **Docusaurus** para convertir los archivos Markdown en un sitio de documentación profesional y fácil de navegar.
- **Evolución:** Este enfoque reemplaza la práctica anterior de crear archivos `manual.html` estáticos, ofreciendo una solución más mantenible y escalable.

## 5. Estándares de Arquitectura e Interoperabilidad (PSR)

Para asegurar un código desacoplado y moderno, adoptamos los siguientes estándares de la PHP-FIG.

### 5.1. Autoloading (PSR-4)
- Todo el código nuevo DEBE seguir el estándar de autoloading PSR-4. Las clases deben residir en un archivo propio y estar en un `namespace` que corresponda a la estructura de directorios. Esto elimina la necesidad de usar `include` o `require`.

**Ejemplo de Implementación Correcta:**

El módulo `Gfiles` ya implementa correctamente esta práctica. La clase `Signatura` se encuentra en el archivo `Gfiles/Signatura.php` y está declarada dentro del namespace correspondiente, permitiendo que otras clases la referencien de forma limpia con `use`.

```php
// Archivo: Gfiles/Signatura.php

namespace Mod\GFiles;

use Mod\GFiles\lib\GstSignatura;
// ... otros 'use'

class Signatura extends ConfigSGD { /* ... */ }
```
### 5.2. Interfaces de Mensajes HTTP (PSR-7 & PSR-17)
- La manipulación de peticiones (`Request`) y respuestas (`Response`) HTTP DEBE realizarse a través de objetos que implementen las interfaces de PSR-7.
- La creación de estos objetos se DEBE realizar a través de factorías que cumplan con PSR-17.
- **Esto prohíbe el acceso directo a variables superglobales como `$_GET`, `$_POST`, `$_SERVER`**.

### 5.3. Contenedor de Dependencias (PSR-11)

**Anti-Patrón (Código a Evitar - extraído de `Gfiles/Digitalizacion.php`):**

El método depende de las superglobales `$_POST` y `$_FILES`, lo que lo hace difícil de probar y acoplado al contexto HTTP.

```php
// INCORRECTO: El método accede directamente a las superglobales.
public function digitalizeProcess(GstSgd $gstSgd, GstPermisos $gstPermisos)
{
    // ...
    $ownerRegistryId = $_POST["formIdRad"];
    $response = $this->saveMetadata($_FILES, $ownerRegistryId, $_POST);
    // ...
}
```

**Patrón Correcto (Código a Seguir):**

La lógica de negocio debe recibir los datos explícitamente, idealmente a través de un objeto `Request` que cumpla con PSR-7, o un objeto de transferencia de datos (DTO). Esto permite que la lógica sea independiente del origen de los datos.

- Se DEBE utilizar un contenedor de inyección de dependencias (DI Container) que cumpla con la interfaz de PSR-11 para gestionar las dependencias entre clases.

### 5.4. Otros Estándares Recomendados
Para continuar modernizando la plataforma, se recomienda la adopción progresiva de los siguientes estándares:

- **PSR-3 (Logger Interface):** Define una interfaz común para los componentes de registro de eventos (logs).
- **PSR-14 (Event Dispatcher):** Estandariza el envío y la escucha de eventos para desacoplar componentes.
- **PSR-15 (HTTP Handlers):** Define la forma en que un servidor procesa una petición HTTP a través de un pipeline de "middleware".
- **PSR-16 (Simple Cache):** Proporciona una interfaz sencilla y estandarizada para interactuar con sistemas de caché.
- **PSR-18 (HTTP Client):** Define cómo se envían peticiones HTTP a servicios externos.
- **PSR-20 (Clock):** Proporciona una interfaz para acceder al reloj del sistema, facilitando las pruebas de lógicas dependientes del tiempo.

## 6. Prácticas de Seguridad

La seguridad es una prioridad máxima.

### 6.1. Principio Fundamental: Nunca Confíes en la Entrada del Usuario
Toda la información que proviene del exterior (formularios, parámetros de URL, cabeceras HTTP) DEBE ser considerada insegura y DEBE ser validada y saneada rigurosamente.

### 6.2. Validación de Entradas (Input Validation)
- **Siempre por el lado del servidor:** La validación en el cliente (JavaScript) es útil para la experiencia de usuario, pero NUNCA debe ser la única línea de defensa. La validación real y definitiva DEBE ocurrir en el servidor.
- **`trim()` a todos los campos:** Antes de cualquier validación, se DEBE aplicar `trim()` a todos los campos de texto para eliminar espacios en blanco no deseados.
- **Reglas por tipo de dato:**
    - **Texto:** Validar longitud (`min`/`max`), caracteres permitidos (`alpha`, `alpha_num`, `alpha_dash`) y usar expresiones regulares para formatos específicos.
    - **Numérico:** Validar si es numérico, si es entero o flotante, y si está dentro de un rango (`min`/`max`/`between`).
    - **Fecha:** Validar el formato y si es una fecha real (`checkdate`). Almacenar como timestamp o en formato `YYYY-MM-DD`. Usar un control de calendario con `readonly` para garantizar el formato.
    - **Correo Electrónico:** Validar con una expresión regular robusta o con `filter_var($email, FILTER_VALIDATE_EMAIL)`.
    - **Archivo:** Validar tipo MIME, extensión, y tamaño máximo. Nunca confiar en el nombre del archivo proporcionado por el cliente.
    - **Contraseña:** Validar longitud mínima y complejidad. NUNCA almacenar en texto plano; usar `password_hash()` y `password_verify()`.
- **CAPTCHA:** Se DEBE implementar un sistema de CAPTCHA en todos los formularios públicos (registro, contacto) para prevenir el spam y los bots.

### 6.3. Saneamiento de Salidas (Output Escaping)
- **Prevenir XSS:** Todas las salidas de datos al HTML DEBEN ser saneadas para prevenir ataques de Cross-Site Scripting.
- **Uso de Blade:** El motor de plantillas Blade lo hace automáticamente por defecto al imprimir variables con `{{ $variable }}`. Esto convierte caracteres como `<` en `&lt;`.
- **Contexto Manual:** Si no se usa Blade, se DEBE usar `htmlspecialchars($variable, ENT_QUOTES, 'UTF-8')` antes de imprimir cualquier dato en HTML.

### 6.4. Seguridad en Base de Datos
- **Prevenir Inyección SQL:** NUNCA se deben construir consultas SQL concatenando variables. Siempre se DEBEN usar **consultas preparadas (prepared statements)** con parámetros vinculados, preferiblemente a través del ORM Eloquent.
- **Procedimientos Almacenados:** Su uso es una alternativa recomendada para encapsular la lógica de base de datos y reducir la superficie de ataque.

### 6.5. Otras Prácticas Críticas
- **Ejecución de Código Remoto:** El uso de `eval()` está **ESTRICTAMENTE PROHIBIDO**.
- **Acceso a Archivos:** Validar cuidadosamente las rutas de archivos. Nunca usar la entrada del usuario para construir rutas (`../../etc/passwd`).
- **Manejo de Errores:** Utilizar bloques `try-catch` para manejar excepciones de forma controlada. No mostrar errores detallados de PHP en producción.
- **Uso de HTTPS:** Utilizar SSL/TLS en todo el sitio para cifrar la comunicación, especialmente en formularios de login y cualquier página que maneje datos sensibles.
- **Tokens CSRF:** Todos los formularios que realizan acciones de escritura (POST, PUT, DELETE) DEBEN estar protegidos contra ataques de Cross-Site Request Forgery. Se DEBE usar la función `token()` de la plataforma para generar el campo oculto del token.
- **Enmascaramiento de Datos:** En entornos de no producción (desarrollo, QA), los datos personales sensibles DEBEN ser anonimizados o enmascarados para proteger la privacidad, siguiendo los lineamientos internos de la compañía.

### 6.6. Gestión de Permisos y Control de Acceso
- **Principio de Privilegio Mínimo (PoLP):** Este es el principio fundamental. Un usuario o proceso DEBE tener únicamente los permisos mínimos necesarios para realizar su función, y nada más. No se deben otorgar permisos "por si acaso".
- **Modelo de Control de Acceso Basado en Roles (RBAC):** La plataforma DEBE seguir un modelo RBAC. Los permisos no se asignan directamente a los usuarios, sino a "roles" o "grupos". Luego, los usuarios son asignados a estos grupos. Esto simplifica enormemente la gestión y la auditoría de permisos.
- **Centralización del Control de Acceso:** La lógica para verificar permisos (ej. `validarAcceso()`) DEBE estar centralizada. Se debe evitar la dispersión de lógica de permisos por diferentes partes del código. El objetivo a largo plazo es migrar estas validaciones a un `AuthorizationService` central.
- **Auditoría Regular de Permisos:** Se DEBE establecer un proceso para revisar periódicamente los permisos asignados a los usuarios y grupos, eliminando aquellos que ya no sean necesarios. Esto reduce la superficie de ataque con el tiempo.

## 7. Estándares de Desarrollo Web (Front-End)

### 7.1. HTML y CSS Válido
- Todo el código HTML generado DEBE ser semánticamente correcto y validar según el estándar **HTML5**.
- Se DEBE utilizar **CSS3** válido.
- Se recomienda el uso de los validadores del W3C para verificar el código: W3C HTML Validator y W3C CSS Validator.

### 7.2. Accesibilidad (WCAG)
- El desarrollo DEBE seguir las **Pautas de Accesibilidad para el Contenido Web (WCAG) 2.1** en el nivel AA como mínimo.
- **Uso de HTML semántico:** Utilizar etiquetas como `<header>`, `<footer>`, `<nav>`, `<main>`, `<section>` y `<article>` para estructurar el contenido correctamente. Se DEBE respetar la jerarquía de encabezados (`<h1>` a `<h6>`).
- **Alternativas textuales:** Todas las imágenes (`<img>`) DEBEN tener un atributo `alt` descriptivo. Las imágenes puramente decorativas deben tener un `alt` vacío (`alt=""`).
- **Etiquetas de Formulario:** Todas las etiquetas `<label>` DEBEN estar asociadas a su control de formulario correspondiente mediante el atributo `for`.
- **Navegación por teclado:** Toda la funcionalidad interactiva (enlaces, botones, campos de formulario) DEBE ser completamente operable a través del teclado.
- **Texto de Enlaces Descriptivo:** El texto de un enlace DEBE describir claramente a dónde lleva. Evitar textos genéricos como "clic aquí", "ver más" o "leer más". Un lector de pantalla que lee solo los enlaces debe poder entender el propósito de cada uno.

**Anti-Patrón (Código a Evitar - extraído de `Gfiles/views/signatura/massImportCsv.blade.php`):**

```html
<!-- INCORRECTO: El texto del enlace no es descriptivo y es ambiguo fuera de contexto. -->
<p>
    ...para visualizar un ejemplo dar clic <a href="{{ ... }}">aquí</a>.
</p>
```

**Patrón Correcto (Código a Seguir):**

```html
<!-- CORRECTO: El texto del enlace describe claramente la acción y el destino. -->
<p>
    ...puede <a href="{{ ... }}">visualizar un ejemplo del archivo .csv con la cabecera específica</a>.
</p>
```
- **Contraste de color:** Asegurar que el contraste entre el texto y su fondo cumple con los ratios mínimos de WCAG.

### 7.3. Buenas Prácticas de Front-End
- **JavaScript no intrusivo y externalización obligatoria:**
    - El código JavaScript DEBE estar separado del HTML. Está **ESTRICTAMENTE PROHIBIDO** incluir bloques `<script>` con código directamente en los archivos de las vistas (Blade) o HTML.
    - Todo el código JavaScript DEBE residir en archivos `.js` externos, los cuales se cargan exclusivamente a través del controlador con `$this->addResource()` o `$this->addPlugin()`.
    - Se DEBE evitar el uso de manejadores de eventos en línea (ej. `onclick="..."`). Para vincular elementos HTML con comportamientos de JavaScript, se DEBEN usar **atributos `data-*`**.

**Anti-Patrón 1: Manejadores en línea (inline handlers)**

```html
<div id="folder_123" ondblclick="navegationFolder(this.id);">Carpeta</div>
```

**Patrón Correcto (Código a Seguir):**

*HTML (en la vista Blade):*
```html
<div class="folder-item" data-action="navigate" data-folder-id="123">Carpeta</div>
```

*JavaScript (en un archivo `.js`):*
```javascript
document.querySelectorAll('[data-action="navigate"]').forEach(element => {
  element.addEventListener('dblclick', event => {
    const folderId = event.currentTarget.dataset.folderId;
    // Llama a la función de navegación con el ID correcto.
    navegationFolder(folderId);
  });
});
```

**Anti-Patrón 2: Scripts incrustados (embedded scripts) - extraído de `Glosario/views/admin/main.blade.php`**

```blade
<!-- INCORRECTO: El código JavaScript está incrustado en la vista. -->
@push('js')
<script>
    $(document).ready(function() {
        $('.form-delete').on('submit', function(e) {
            if (!confirm('{{ GLOSARIO_CONFIRMAR_ELIMINAR }}')) {
                e.preventDefault();
            }
        });
    });
</script>
@endpush
```

**Patrón Correcto (Código a Seguir):**

*Controlador (ej. `Glosario/admin.php`):*
```php
// CORRECTO: El controlador carga el script externo.
public function main()
{
    // ...
    $this->addResource('admin.js', 'Glosario'); // Carga mod/Glosario/js/admin.js
    $this->render();
}
```

*JavaScript (en `Glosario/js/admin.js`):*
```javascript
// CORRECTO: La lógica reside en un archivo .js separado.
$(document).ready(function() {
    $('.form-delete').on('submit', function(e) {
        if (!confirm('¿Está seguro de que desea eliminar este término?')) {
            e.preventDefault();
        }
    });
});
```

- **CSS no intrusivo y externalización obligatoria:**
    - Los estilos CSS DEBEN estar separados del HTML. Está **ESTRICTAMENTE PROHIBIDO** usar el atributo `style` para aplicar estilos en línea o bloques `<style>` dentro de las vistas.
    - Se prohíbe el uso de **atributos de presentación HTML obsoletos** (ej. `width`, `height`, `align`, `bgcolor`, `border`) directamente en las etiquetas. Toda la presentación DEBE ser controlada por clases CSS.
    - Todos los estilos DEBEN residir en archivos `.css` externos, los cuales se cargan a través del controlador con `$this->addResource()`.
    - Se DEBE priorizar el uso de clases semánticas y reutilizables sobre la creación de estilos para IDs únicos.

**Anti-Patrón 1: Bloques de estilo incrustados - extraído de `Gfiles/views/flows/formularioFlow.blade.php`**

```blade
{{-- INCORRECTO: Bloque <style> incrustado directamente en la vista. --}}
<style>
    .versionPlatform {
        display: none;
    }
    /* ... más estilos ... */
</style>

@if ($configFlujo)
    {{-- INCORRECTO: Otro bloque <style> condicional. --}}
    <style>
        body, #visualizadorFsm.todoAzul {
            border: 0;
            background: #f8f9fc;
        }
    </style>
@endif
```

**Patrón Correcto (Código a Seguir):**

*Controlador (ej. `Glosario/admin.php`):*
```php
// CORRECTO: El controlador carga la hoja de estilos externa.
$this->addResource('admin.css', 'Glosario'); // Carga mod/Glosario/css/admin.css
```

*CSS (en `Glosario/css/admin.css`):*
```css
/* CORRECTO: Los estilos residen en un archivo .css separado y usan clases. */
.form-inline-display {
    display: inline-block;
}
```
- **Nomenclatura CSS:** Utilizar nombres de clases descriptivos, en minúsculas y con guiones como separadores (kebab-case). Ejemplo: `class="user-profile-card"`. Se recomienda una metodología como BEM.
- **Selectores CSS eficientes:** Evitar selectores de ID para estilado y selectores demasiado específicos. No usar `!important` salvo en casos excepcionales.
- **Unidades relativas:** Preferir `rem` para tamaños de fuente y `em` para espaciados dentro de componentes.
- **Automatización:** Utilizar herramientas en el proceso de build (como Gulp/Webpack) para tareas como autoprefixing y minificación.
- **Librerías Externas:** No se deben incluir librerías JavaScript o CSS diferentes a las que ya tiene el producto, a menos que sean aprobadas e indicadas en el documento de arquitectura del proyecto.

### 7.4. Buenas Prácticas con Bootstrap 4/5
- **Utility-First:** Se DEBE priorizar el uso de las clases de utilidad de Bootstrap (ej. `mt-3`, `p-2`, `d-flex`, `text-center`) para ajustes de espaciado, layout y tipografía, en lugar de crear clases CSS personalizadas para estilos simples.
- **Personalización con Sass:** La personalización de colores, fuentes o componentes de Bootstrap DEBE realizarse modificando las variables Sass de Bootstrap y recompilando, no sobreescribiendo las clases CSS directamente.
- **Grid System:** Se DEBE respetar la estructura `container > row > col` para la construcción de layouts. No aplicar padding o margin directamente a las `row` que alteren su comportamiento de gutter.
- **JavaScript:** Para nuevo código personalizado, se debe evitar el uso de jQuery si no es estrictamente necesario para interactuar con un plugin existente. Bootstrap 5 ya no depende de jQuery.

### 7.5. Experiencia de Usuario (UX) y Usabilidad
- **Mensajes Claros:** Los mensajes de error, confirmación e información deben ser claros y concisos, utilizando los colores estándar de la plataforma (rojo para error, verde para éxito, azul para info, amarillo para alerta).
- **Ayudas Visuales:**
    - Los campos obligatorios DEBEN estar claramente marcados (ej. con un asterisco `*`).
    - Los campos de difícil comprensión DEBEN tener textos de ayuda o tooltips.
- **Navegación:** El botón "atrás" del navegador no debe dejar de funcionar. Todas las funcionalidades deben tener una ruta de miga (breadcrumb) coherente.

## 8. Control de Versiones (Git)
### 7.6. Validación en el Cliente (JavaScript)

La validación en el cliente es una herramienta para mejorar la **experiencia de usuario**, proporcionando retroalimentación inmediata sin necesidad de recargar la página.

- **No es un sustituto de la seguridad:** La validación del lado del cliente NUNCA debe ser la única línea de defensa. La validación definitiva y autoritativa siempre DEBE ocurrir en el servidor.
- **Consistencia:** Las reglas de validación del cliente DEBEN ser un reflejo lo más fiel posible de las reglas del servidor para evitar discrepancias.
- **Retroalimentación Inmediata:** Los errores de validación deben mostrarse al usuario de forma clara y junto al campo correspondiente, tan pronto como sea posible (ej. al salir del campo o al intentar enviar el formulario).
- **Uso de Plugins de la Plataforma:** Se DEBE utilizar el plugin `jQueryValidate` proporcionado por la plataforma, cargándolo a través del controlador con `$this->addPlugin()`.
- **Evitar Lógica Compleja:** No se debe replicar lógica de negocio compleja (ej. verificar si un email ya existe en la base de datos) en el cliente. Estas son validaciones que pertenecen exclusivamente al servidor.

**Anti-Patrón (Código a Evitar):**

```javascript
// INCORRECTO: Confiar solo en JavaScript para la validación.
function validateForm() {
  let email = document.getElementById('email').value;
  if (email === "") {
    alert("Email es requerido");
    return false; // Si esto falla, el formulario no se envía, pero se puede eludir fácilmente.
  }
}
```

- **Commits Atómicos:** Cada commit debe representar un cambio lógico y completo.
- **Mensajes de Commit:**
    - Deben estar en modo imperativo (ej. "Agrega" en lugar de "Agregado" o "Agregando").
    - La primera línea debe ser un resumen conciso (máx. 50 caracteres).
    - Opcionalmente, se puede añadir un cuerpo más detallado después de una línea en blanco.
    - Si el commit resuelve un ticket, referenciarlo al final (ej. `Resuelve: #123`).

## 9. Checklist de Calidad y "Definición de Hecho" (Definition of Done)

Un desarrollo se considera **"hecho" (Done)** únicamente cuando cumple con **todos** los puntos de esta guía. La siguiente lista de verificación debe ser utilizada por el desarrollador antes de solicitar una revisión de código.

### 9.1. Funcionalidad y Lógica
- [ ] La funcionalidad cubre todos los escenarios y criterios de aceptación definidos en los requisitos.
- [ ] No existen vínculos rotos.
- [ ] La funcionalidad se ejecuta correctamente en todos los navegadores soportados por el proyecto.
- [ ] No hay errores de ortografía en los textos y constantes.
- [ ] El tiempo de carga es adecuado y cumple con los requisitos no funcionales.

### 9.2. Estándares de Código y Seguridad
- [ ] El código cumple con todos los estándares de PHP (Sección 3) y Arquitectura (Sección 5).
- [ ] Se ha pasado una herramienta de análisis estático como **PHP_CodeSniffer** (para estilo) y **PHPStan** (para errores).
- [ ] Se han seguido todas las prácticas de seguridad (Sección 6).
- [ ] Todos los campos de formularios se validan tanto en el front-end como en el back-end.
- [ ] El código ha sido documentado siguiendo los estándares de PHPDoc (Sección 4).

### 9.3. Front-End y Accesibilidad
- [ ] Todo el HTML y CSS generado pasa la validación de los servicios del W3C.
- [ ] Se ha realizado una auditoría de accesibilidad (WCAG 2.1 AA), combinando herramientas automáticas (Lighthouse, Axe) y verificación manual (navegación por teclado, TAWDIS).
- [ ] Se cumplen todas las buenas prácticas de Front-End y UX (Sección 7).

### 9.4. Revisión por Pares (Peer Review)
- Una vez completada la autoevaluación anterior, el código DEBE ser revisado por al menos otro miembro del equipo antes de ser fusionado a la rama principal.

## 10. Convenciones de la Plataforma Nexura

Esta sección adapta las directrices del instructivo de desarrollo interno (`GIS-I-004`) para alinear el código heredado y el nuevo desarrollo con los estándares modernos.

### 10.1. Estructura de Módulos
- Cada módulo DEBE seguir una estructura de directorios estándar para garantizar la consistencia:
    - `/img/`, `/js/`, `/css/`: Assets específicos del módulo.
    - `/lang/`: Archivos de constantes de lenguaje (traducciones).
    - `/lib/`: Clases de lógica de negocio (`class.gst*.php`), configuración (`class.config.php`) y ORM.
    - `/sql/`: Scripts de base de datos (iniciales y `_alter`).
    - `/views/`: Plantillas Blade.
    - `/[controllerName].php`: Archivos de controladores.

### 10.2. Arquitectura de Módulos (MVC)

#### 10.2.1. Modelos (ORM, Clases de Gestión y Base de Datos)
- **Entidades ORM (Eloquent):**
    - **Ubicación:** `/lib/orm/eloquent/`.
    - **Nomenclatura:** `Tn[NombreTablaUnido]`. Ejemplo: para `tn_demo_articulos`, la clase es `TnDemoArticulos`.
    - **Herencia:** La clase DEBE extender de la clase base `modelORM` (definida en `lib/php/utils/class.modelORM.php`). Para referenciarla correctamente desde un archivo con `namespace`, se DEBE incluir la sentencia `use Utils\eloquent\modelORM;` al inicio del mismo.
- **Clases de Gestión (Lógica de Negocio):**
    - **Responsabilidad:** Contienen la lógica de negocio y son el único lugar donde se deben utilizar las clases del ORM.
    - **Ubicación:** `/lib/`.
    - **Nomenclatura:** `gst[NombreEntidad]`. Ejemplo: `gstArticulos`.

**Ejemplo de Implementación Correcta (Nomenclatura):**

El módulo `Gfiles` sigue esta convención para sus clases de lógica de negocio, facilitando la comprensión de su arquitectura.

```php
// Archivo: /Gfiles/lib/GstSignaturaElectronica.php
namespace Mod\GFiles\lib;

class GstSignaturaElectronica { /* ... */ }
```

**Manejo de Errores con Excepciones:** Los métodos en las Clases de Gestión NUNCA DEBEN retornar un `string` o `false` para indicar un fallo. En su lugar, DEBEN lanzar una `Exception`. El controlador que invoca el método es el responsable de capturar (`catch`) la excepción y traducirla en un mensaje amigable para el usuario usando `setMsg()`.

**Anti-Patrón (Código a Evitar - extraído de `GstGFilesCarpetasE.php`):**

```php
// INCORRECTO: La clase de gestión maneja la presentación del error.
public function updateManagementFile($post)
{
    try {
        // ... lógica ...
        if ($manaFile->save()) {
            return $manaFile->id;
        }
        throw new Exception('No se pudo actualizar');
    } catch (Exception $e) {
        error_log($e->getMessage());
        return "Problema al actualizar la carpeta electrónica"; // ¡Mal!
    }
}
```

**Patrón Correcto (Código a Seguir):**

```php
// CORRECTO: La clase de gestión lanza la excepción.
public function updateManagementFile($post): int
{
    // ... lógica ...
    if ($this->model->save()) { return $this->model->id; }
    throw new \Exception('No se pudo actualizar la carpeta electronica');
}
```
- **Estándares de Base de Datos:**
    - **Nomenclatura de Tablas:** `[prefijo]_[nombre_modulo]_[unidad_informacion]` (ej. `tn_foros_categorias`).
    - **Índices:** Todas las tablas DEBEN tener una llave primaria. Las columnas únicas DEBEN estar indexadas.
    - **Llaves Foráneas:** Las tablas relacionadas DEBEN tener sus respectivas llaves foráneas definidas.
    - **Bitácora de Cambios:** Todos los cambios a la estructura de la base de datos DEBEN registrarse en un archivo `_alter.sql`.

#### 10.2.2. Vistas (Blade)
- **Nomenclatura:** El archivo de la vista DEBE llamarse como la función que la renderiza. Ejemplo: la función `create()` renderiza la vista `create.blade.php`.
- **Layouts:** Todas las vistas DEBEN extender de un layout principal (`@extends('layouts.adminLayout')`).
- **Secciones:** El contenido principal DEBE estar dentro de una sección (`@section('content')`).

#### 10.2.3. Controladores
- **Nomenclatura:** El nombre de la clase del controlador DEBE coincidir con el nombre del archivo. Ejemplo: para el archivo `Admin.php`, la clase DEBE ser `Admin`, si el archivo es `admin.php`, la clase DEBE ser `admin`.
    - **Nota de Precedencia:** Esta regla específica de la plataforma tiene **prioridad** sobre la convención general `PascalCase` de PSR-12 (Sección 3.2) para los controladores. Esto es crucial para mantener la compatibilidad con el sistema de carga de archivos existente.
    - **Recomendación a Futuro:** Para nuevos desarrollos, se recomienda nombrar los archivos de controladores en `PascalCase` (ej. `NuevoTermino.php`) para alinearse gradualmente con los estándares modernos.
- **Herencia:** La clase del controlador DEBE extender de la clase de configuración del módulo (`config[NombreModulo]`).
- **Namespace:** Los controladores DEBEN estar dentro de un namespace que siga la estructura del módulo (ej. `namespace Mod\Demo;`).
- **Acceso a Datos:** Los controladores NO DEBEN acceder directamente a la base de datos o al ORM. Deben delegar esta responsabilidad a las Clases de Gestión.
- **Inyección de Dependencias:** Para un código más limpio, testeable y desacoplado, los controladores DEBEN recibir sus dependencias (como las clases de gestión) a través del constructor.

**Ejemplo de Implementación Correcta (extraído de `Gfiles/Digitalizacion.php`):**

Este controlador declara sus dependencias como parámetros tipados en el constructor, permitiendo que un contenedor de dependencias las resuelva automáticamente.

```php
class Digitalizacion extends ConfigSGD
{
    // ... propiedadesl
    public function __construct(
        GstNivelesSeguridad $gstNivelesSeguridad,
        GstHistoricos $gstHistoricos,
        // ... otras dependencias
    ) {
        $this->gstNivelesSeguridad = $gstNivelesSeguridad;
        $this->gstHistoricos = $gstHistoricos;
        // ...
    }
    // ...
}
```
- **Atributos Estándar:** Los controladores utilizan atributos predefinidos para gestionar la vista: `$isAdmin`, `$title`, `$view`, `$vData`, `$template`, los cuales deben ser publicos.
- **Funciones CRUD Estándar:** Se DEBE seguir una nomenclatura estándar:
    - **Renderizan Vistas:** `main()`, `lst()`, `info()`, `create()`, `update()`.
    - **Procesan Formularios (POST):** `createProcess()`, `updateProcess()`, `deleteProcess()`.

- **Refactorización y Reutilización de Código (Principio DRY):**
    - Se DEBE evitar la duplicación de código. Si varios métodos de un controlador comparten una lógica similar (por ejemplo, la configuración y renderizado de una vista de formulario), esta lógica DEBE ser extraída a un método privado para mejorar la mantenibilidad.

**Anti-Patrón (Código a Evitar - extraído de `Glosario/admin.php`):**

```php
// INCORRECTO: Los métodos create() y update() repiten la lógica de renderizado del formulario.
public function create()
{
    $this->title = GLOSARIO_MENU_NUEVO;
    $this->view = 'admin.form';
    $this->vData['termino'] = null;
    $this->vData['action'] = 'createProcess';
    $this->addPlugin([SX_P_EDITOR]);
    $this->render();
}

public function update()
{
    // ... lógica para buscar el término ...
    $this->title = GLOSARIO_MENU_EDITAR;
    $this->view = 'admin.form';
    $this->vData['termino'] = $termino;
    $this->vData['action'] = 'updateProcess';
    $this->addPlugin([SX_P_EDITOR]);
    $this->render();
}
```

**Patrón Correcto (Código a Seguir - extraído de `Glosario/admin.php`):**

```php
// CORRECTO: La lógica común se extrae a un método privado `renderForm`.
public function create()
{
    $this->renderForm(GLOSARIO_MENU_NUEVO, 'createProcess');
}

public function update()
{
    // ... lógica para buscar el término ...
    $this->renderForm(GLOSARIO_MENU_EDITAR, 'updateProcess', $termino);
}

/**
 * Renderiza el formulario para crear o editar un término.
 *
 * @param string $title El título de la página.
 * @param string $action La acción del formulario.
 * @param TnGlosarioTerminos|null $termino El término a editar.
 */
private function renderForm(string $title, string $action, ?TnGlosarioTerminos $termino = null): void
{
    $this->title = $title;
    $this->view = 'admin.form';
    $this->vData['termino'] = $termino;
    $this->vData['action'] = $action;
    $this->addPlugin([SX_P_EDITOR]);
    $this->render();
}
```

#### 10.2.4. Clases de Configuración

#### 10.2.5. Prohibición de Código de Presentación en Controladores y Clases de Gestión

La generación de código de presentación (HTML, CSS, JavaScript) está **ESTRICTAMENTE PROHIBIDA** dentro de las clases de Controlador y de Gestión.

-   **Controladores:** Su única responsabilidad es recibir la petición, llamar a la lógica de negocio y devolver una respuesta, ya sea renderizando una vista Blade (`$this->render()`) o retornando datos puros (`echo json_encode(...)`).
-   **Clases de Gestión:** Su responsabilidad es únicamente la lógica de negocio.

**Anti-Patrón (Código a Evitar - extraído de `Signatura.php`):**

```php
// INCORRECTO: El controlador está generando HTML.
public function getRootSignaturas()
{
    $rootsSignaturas = $this->signatura->getRootSignaturas(...);
    $html = "";
    foreach ($rootsSignaturas as $rootSignatura) {
        $html .= "<div id='folder_" . $rootSignatura['id'] . "' ... >"; // Mezcla de lógica y presentación
        // ... más concatenación de HTML
    }
    echo $html; // Devuelve un fragmento de HTML
}
```

**Patrón Correcto (Código a Seguir):**

El controlador debe pasar los datos a una vista Blade, que se encarga de la lógica de presentación. Para peticiones AJAX, se debe devolver JSON (ver sección 17.4).

```php
// CORRECTO: El controlador prepara los datos y delega a la vista.
public function getRootSignaturas()
{
    $rootsSignaturas = $this->signatura->getRootSignaturas(...);
    $this->vData['folders'] = $rootsSignaturas;
    $this->view = 'signatura.partials.folders';
    $this->render();
}
```

**Anti-Patrón 2 (Código a Evitar - extraído de `Gfiles/Digitalizacion.php`):**

Generar fragmentos de HTML, incluso para respuestas AJAX, viola el principio de separación de responsabilidades.

```php
// INCORRECTO: El método `getFields` genera un fragmento de HTML.
public function getFields($conf_metada, $colum, $id_conf)
{
    // ... lógica para determinar la vista ...
    $this->view = SGD_PATH_VIEW_DGT.$view;
    return $this->getViewHtml(); // Devuelve un string HTML
}
```
- **Propósito:** Definir la configuración específica del módulo, como las opciones del menú (`modMenu`), la ruta de miga (`modPath`) y las URLs amigables.
- **Ubicación:** `/lib/class.config.php`.
- **Nomenclatura:** El nombre de la clase DEBE ser `config[NombreModulo]`. Ejemplo: `configDemo`.
- **Herencia:** La clase de configuración DEBE extender de la clase base `controller` (definida en `lib/php/utils/class.controller.php`). Para referenciarla correctamente desde un archivo con `namespace`, se DEBE incluir la sentencia `use Utils\controller;` al inicio del mismo.
- **Atributos Clave:**
    - `$listModMenu`: Array que define las opciones del menú lateral.
    - `$listModPath`: Array que define la ruta de miga (breadcrumbs).
    - `$optionsByFunction`: Array que mapea qué menú y ruta de miga se muestra para cada función de un controlador.

### 10.3. Personalización y Sesión
- **Personalización por Cliente:** Para personalizar un módulo, se DEBE replicar su estructura de directorios dentro de la carpeta del cliente (`/info/[nombre_cliente]/mod/[NombreModulo]/...`). La plataforma cargará automáticamente el archivo personalizado.
- **Variables de Sesión:** Para evitar colisiones, todas las variables de sesión específicas de un módulo DEBEN guardarse bajo una llave principal con el nombre del módulo.
- **Mensajes al Usuario:** Se DEBE utilizar la función `setMsg()` para establecer mensajes de notificación (flash messages) y `dspMsg()` para mostrarlos.
- **Assets:** Los archivos JavaScript y CSS no deben incluirse directamente en las vistas. Deben cargarse a través del controlador usando `$this->addResource()` o `$this->addPlugin()`.

### 10.4. Ecosistema de Plugins
- La plataforma cuenta con plugins predefinidos para funcionalidades comunes (`jQueryValidate`, `dataTable`, `Calendar`, `Editor`).
- Estos plugins se DEBEN cargar a través del controlador mediante el atributo `$this->addPlugin([...])`.

### 10.5. Validaciones
- **Centralización:** Las reglas de validación de campos DEBEN definirse dentro de la entidad ORM correspondiente, en el atributo protegido `$fields`.
- **Retención de Datos:** En caso de fallo de validación, los datos ingresados por el usuario DEBEN mantenerse en el formulario. Esto se gestiona mediante variables de sesión con el formato `$_SESSION['NOMBRE_MODULO']['ACCION']['NOMBRE_CAMPO']`.

### 10.6. Rendimiento
- **SQL:**
    - Usar `JOIN`s en lugar de subconsultas cuando sea posible.
    - Seleccionar solo las columnas necesarias, evitando `SELECT *`.
    - Utilizar `LIMIT` para paginar resultados.
    - Aprovechar el lenguaje de consultas del ORM (Eloquent).
- **Aplicativo:**
    - Evitar ciclos anidados (`O(n^2)`) sobre grandes conjuntos de datos.
    - Utilizar el disco lo menos posible. Cerrar siempre los manejadores de archivos (`fclose`).
    - No suprimir errores con el operador `@`.
estas
### 10.7. Minificación de Assets
- Se DEBE utilizar el proceso automatizado con **Gulp** para minificar los archivos JavaScript y CSS antes de subirlos a producción.

### 10.8. Buenas Prácticas con Eloquent ORM
- **Eager Loading (Carga Ansiosa):** Para prevenir el problema de rendimiento "N+1", siempre se DEBE usar Eager Loading al cargar modelos con sus relaciones.
    ```php
    // INCORRECTO: Ejecuta 1 consulta para los artículos + N consultas para cada autor.
    $articles = TnDemoArticulos::all();
    foreach ($articles as $article) {
        echo $article->author->name; // ¡Consulta a la BD en cada iteración!
    }

    // CORRECTO: Ejecuta solo 2 consultas en total.
    $articles = TnDemoArticulos::with('author')->get();
    foreach ($articles as $article) {
        echo $article->author->name; // No hay consulta nueva aquí.
    }
    ```

- **Protección de Asignación Masiva (Mass Assignment):** Todos los modelos DEBEN utilizar la propiedad `$fillable` para definir explícitamente qué campos se pueden rellenar mediante métodos como `create()` o `update()`. Esto es una medida de seguridad crucial.

- **Scopes de Consulta (Query Scopes):** Para consultas complejas o que se repiten, se DEBEN crear "scopes" en el modelo para encapsular la lógica y hacer el código más legible.
    ```php
    // En el modelo TnDemoArticulos.php
    public function scopePublished($query)
    {
        return $query->where('status', '=', 'published');
    }

    // En la clase de gestión (gstArticulos)
    $publishedArticles = TnDemoArticulos::published()->get();
    ```

- **Aislamiento de la Lógica de Datos:** El acceso directo a los modelos de Eloquent DEBE realizarse exclusivamente desde las **Clases de Gestión** (ej. `gstMiClase`). Los controladores NUNCA deben interactuar directamente con el ORM.

**Ejemplo de Implementación Correcta:**

La clase `GstGFilesCarpetasE` encapsula correctamente la interacción con el modelo `TnGFilesCarpetasE`, exponiendo un método (`find`) que puede ser utilizado por el controlador. Esto mantiene el controlador limpio de lógica de base de datos.

```php
// Archivo: /Gfiles/lib/GstGFilesCarpetasE.php

namespace Mod\GFiles\lib;

class GstGFilesCarpetasE {
    public function find($value, $field)
    {
        return \TnGFilesCarpetasE::where($field, $value)->first();
    }
}
```
- **Transacciones de Base de Datos:** Cualquier operación que implique múltiples escrituras en la base de datos (ej. crear un usuario y su perfil) DEBE estar envuelta en una transacción para garantizar la integridad de los datos.

## 11. Refactorización de Código Heredado (Legacy)

La modernización de la base de código es un proceso continuo.

- **Funciones Globales:** Evitar la creación de nuevas funciones globales. La lógica existente en archivos como `funciones.php`  debe ser refactorizada gradualmente en clases de servicio con responsabilidades únicas. Se realizara poco a poco los desarrollos.

#### 11.1. Uso de Funciones Globales Existentes (Periodo de Transición)

Se reconoce que la plataforma depende de funciones globales y métodos estáticos heredados (ej. `genUrl()`, `thumbnail::createThumb()`) que se cargan automáticamente. Mientras se completa la refactorización, se aplicará la siguiente política:

1.  **Prohibido Crear Nuevas:** Está **ESTRICTAMENTE PROHIBIDO** añadir nuevas funciones globales o métodos estáticos de utilidad a archivos como `funciones.php`.

2.  **Permitido Usar Existentes (con Precaución):** Se permite el uso de funciones globales y métodos estáticos **existentes** en el código que se está modificando o creando, pero solo si aún no existe una alternativa moderna (un servicio inyectable), estas se encuentran en archivos como (ej. `librerias/php/tribunet/funciones.php`), ademas dar prioridad al uso de funciones globales definidas en la ruta `lib/php/utils`, la cual contiene utilidades del sistema, que son desarrollos propios.

3.  **Priorizar Alternativas Modernas:** Si ya existe un servicio que reemplace una funcionalidad existente global (ej. `genUrl()`), su uso es **OBLIGATORIO** a través de inyección de dependencias.

4.  **La Regla del Boy Scout:** "Deja el campamento más limpio de lo que lo encontraste". Si modificas un archivo que utiliza una función global para la cual ya existe una alternativa moderna, **DEBES** refactorizar esa parte del código para usar el nuevo servicio.

5.  **Documentación con `@deprecated`:** Al encontrar una función global en el código, se recomienda marcar su uso con un comentario `@deprecated` para señalar que es un punto de deuda técnica a resolver.

    ```php
    /**
     * @deprecated Utilizar ThumbnailService inyectado en su lugar.
     */
    $thumbPath = thumbnail::createThumb($config);
    ```

#### 11.1.1. Uso Correcto de `genUrl()`

La función `genUrl()` es la herramienta estándar de la plataforma para crear URLs internas de manera consistente. Su uso correcto es fundamental para el funcionamiento de las URLs amigables y la mantenibilidad del código.

**Firma de la Función:**
```php
function genUrl(
    $lServicio,
    $lTipo = 'user',
    $lFuncion = 'main',
    $args = array(),
    $proto = 'http'
)
```
- **`$lServicio`**: El módulo (ej. `GFiles`).
- **`$lTipo`**: El nombre de la clase del controlador (ej. `Digitalizacion`).
- **`$lFuncion`**: El nombre del método a invocar (ej. `digitize`).
- **`$args`**: **(Crucial)** Un array asociativo que contiene todos los parámetros que se pasarán en la URL.

**Anti-Patrón (Código a Evitar - extraído de `Gfiles/Digitalizacion.php`):**

Está **ESTRICTAMENTE PROHIBIDO** concatenar parámetros a la URL generada. Esta práctica anula el sistema de URLs amigables y es propensa a errores.

```php
// INCORRECTO: Los argumentos se concatenan a la URL, saltando la lógica de URLs amigables.
return redirect(genUrl(SGD, 'Digitalizacion', 'digitize')."&custodiaIdCarpeta=".$idCarpeta."&splash=false");
```

**Patrón Correcto (Código a Seguir):**

Todos los parámetros DEBEN pasarse a través del cuarto argumento, `$args`, como un array asociativo.

```php
// CORRECTO: Los argumentos se pasan como un array, permitiendo la correcta generación de la URL.
return redirect(genUrl(SGD, 'Digitalizacion', 'digitize', [
    'custodiaIdCarpeta' => $idCarpeta,
    'splash' => 'false'
]));
```

**Justificación:**

- **Compatibilidad con URLs Amigables:** El mecanismo interno para transformar `?lServicio=...&lTipo=...` en rutas limpias como `/sgd/digitalizacion/digitize` depende exclusivamente del contenido del array `$args`.
- **Consistencia y Legibilidad:** Mantiene un estándar único en toda la plataforma, facilitando la lectura y el mantenimiento del código.
- **Seguridad y Robustez:** La función se encarga de codificar correctamente los parámetros de la URL, previniendo errores de formato.

- **Superglobales:** El acceso directo a `$_GET`, `$_POST`, `$_SESSION` está obsoleto. Se debe refactorizar el código para usar un objeto `Request` que cumpla con PSR-7.
- **Seguridad:** Priorizar la eliminación de `eval()` y la refactorización de consultas SQL para usar **consultas preparadas**.
- **Documentación de Funciones Globales:** La documentación de funciones globales existentes debe realizarse exclusivamente a través de **PHPDoc** en el código fuente. El `STYLEGUIDE.MD` no debe contener un listado de estas funciones. La documentación de la API generada automáticamente será el manual de referencia para su uso mientras no sean migradas a clases.

## 12. Pruebas y Calidad de Software (Testing)

Para garantizar la estabilidad y fiabilidad del software, se DEBE adoptar una estrategia de pruebas automatizadas.

### 12.1. Pruebas Unitarias (Unit Tests)
- **Propósito:** Verificar que cada unidad de código (clases, métodos) funciona correctamente de forma aislada.
- **Herramienta:** Se DEBE utilizar **PHPUnit**.
- **Política:** Toda nueva clase de lógica de negocio (ej. en `lib/`) DEBE estar acompañada de sus correspondientes pruebas unitarias.

### 12.2. Pruebas de Integración (Integration Tests)
- **Propósito:** Verificar que diferentes partes del sistema (ej. un controlador y su clase de gestión) interactúan correctamente entre sí y con servicios externos como la base de datos.

### 12.3. Pruebas de Extremo a Extremo (End-to-End - E2E)
- **Propósito:** Simular flujos de usuario completos en un navegador real para verificar que la aplicación funciona como se espera desde la perspectiva del usuario final.
- **Herramientas:** Se recomienda el uso de frameworks como **Cypress** o **Playwright**.

## 13. Despliegue y Operaciones (DevOps)

### 13.1. Integración Continua / Despliegue Continuo (CI/CD)
- Se DEBE implementar un pipeline de CI/CD (ej. con GitHub Actions, GitLab CI) que automatice las tareas de calidad en cada commit.
- **Tareas Automatizadas:** El pipeline DEBE ejecutar automáticamente:
    1.  Análisis de estilo de código (`PHP_CodeSniffer`).
    2.  Análisis estático de errores (`PHPStan`).
    3.  Pruebas unitarias y de integración.

### 13.2. Gestión de Configuración (Twelve-Factor App)
- **Principio:** La configuración del entorno (credenciales de base de datos, claves de API, etc.) DEBE estar separada del código.
- **Práctica:** Se prohíbe almacenar credenciales en el control de versiones. Se DEBE utilizar **variables de entorno**, gestionadas a través de archivos `.env` (que no se suben al repositorio) y cargadas en la aplicación mediante una librería como `vlucas/phpdotenv`.

## 14. Entornos y Despliegue

Esta sección define el modelo de permisos y roles de usuario para los servidores de producción y desarrollo, basado en la "Guía de Configuración de Usuarios y Permisos". El objetivo es garantizar la seguridad y la correcta operación de la plataforma.

### 14.1. Roles de Usuario en Servidor
- **`nxdespliegue` (Usuario de Despliegue):** Es el **propietario** de todos los archivos de la aplicación. Su única responsabilidad es subir, bajar y modificar el código fuente. Este usuario **no** ejecuta el servidor web.
- **`portal` (Usuario de Ejecución):** Es el usuario bajo el cual se ejecutan los procesos del servidor web (Nginx) y PHP-FPM. Este usuario necesita leer los archivos de la aplicación para servirlos, pero **no debe tener permisos de escritura** sobre el código fuente.
- **Racionalidad:** Esta separación de roles es un principio de seguridad fundamental. Si un atacante compromete el servidor web (el usuario `portal`), no podrá modificar los archivos de la aplicación, limitando significativamente el daño potencial.

### 14.2. Permisos de Archivos y Directorios
- **Directorios:** DEBEN tener permisos `755` (`rwxr-xr-x`).
    - **`7` (Propietario `nxdespliegue`):** Control total (leer, escribir, ejecutar/entrar).
    - **`5` (Grupo `portal`):** Permiso para leer y entrar al directorio.
    - **`5` (Otros):** Permiso para leer y entrar al directorio.
- **Archivos:** DEBEN tener permisos `644` (`rw-r--r--`).
    - **`6` (Propietario `nxdespliegue`):** Permiso para leer y escribir el archivo.
    - **`4` (Grupo `portal`):** Permiso de solo lectura.
    - **`4` (Otros):** Permiso de solo lectura.
- **Excepciones:** Los directorios que requieren escritura por parte de la aplicación web (ej. `cache/blade`, `info/[cliente]/media/`) DEBEN tener permisos `775` (`rwxrwxr-x`).
    - **Carpetas de Cliente:** Específicamente, las siguientes carpetas dentro de `info/[cliente]/` deben tener permisos `775`: `cache`, `media`, `media/tmp`, `routes`, `web`, `resources/communities`.
    - **Módulos Específicos:** Algunos módulos pueden requerir permisos especiales. Por ejemplo, para `LiveChat`, las carpetas `public_html/chat/var`, `public_html/chat/cache` y `public_html/chat/settings` también deben tener permisos `775`.

### 14.3. Entornos de Desarrollo Local
- Para facilitar el desarrollo, en las máquinas locales se recomienda la siguiente configuración:
    - **Propietario:** El usuario del desarrollador debe ser el propietario de todos los archivos y directorios.
    - **Grupo:** El usuario del servidor web (ej. `www-data` en Ubuntu) debe pertenecer al grupo del usuario desarrollador.
    - **Permisos:**
        - **Directorios:** `775` (`rwxrwxr-x`).
        - **Archivos:** `664` (`rw-rw-r--`).
- **Racionalidad:** Esta configuración permite que tanto el desarrollador (a través de su editor de código) como el servidor web local puedan escribir en los archivos. Esto evita la necesidad de usar `sudo` para editar archivos o para que la aplicación escriba en logs o caché, agilizando el flujo de trabajo.

## 15. Gestión de Dependencias (Composer & NPM)

### 15.1. Dependencias de PHP (Composer)
- Todas las dependencias de PHP DEBEN ser gestionadas a través de **Composer**.
- El archivo `composer.lock` DEBE ser incluido en el control de versiones. Esto garantiza que todos los desarrolladores y los servidores de despliegue utilicen exactamente las mismas versiones de las librerías, evitando el comportamiento inesperado.
- El directorio `vendor/` DEBE ser ignorado por Git (a través del archivo `.gitignore`).

### 15.2. Dependencias de Front-End (NPM/Yarn)
- Todas las dependencias de front-end (JavaScript, CSS) DEBEN ser gestionadas a través de **NPM** o **Yarn**.
- El archivo `package-lock.json` o `yarn.lock` DEBE ser incluido en el control de versiones.
- El directorio `node_modules/` DEBE ser ignorado por Git.

## 16. Migraciones de Base de Datos

- **Principio:** Los cambios en la estructura de la base de datos DEBEN ser gestionados a través de un sistema de migraciones programáticas, no mediante archivos `.sql` manuales.
- **Herramienta Recomendada:** Se recomienda el uso de una herramienta como **Phinx** para gestionar las migraciones.
- **Beneficios:** Este enfoque permite versionar los cambios de la base de datos junto con el código, automatizar los despliegues y los rollbacks, y mantener la consistencia del esquema en todos los entornos.
- **Evolución:** Este sistema reemplaza la práctica de mantener un archivo `_alter.sql`, que es propenso a errores y difícil de gestionar en equipo.

### 15.3. Política de No Modificación de Dependencias Externas

Está **ESTRICTAMENTE PROHIBIDO** modificar directamente el código fuente de librerías, paquetes o plugins de terceros. Esto incluye, pero no se limita a, los archivos dentro de los directorios `vendor/`, `node_modules/` y `media/plugins/`.

**Razones:**

-   **Mantenibilidad:** Cualquier modificación local será **sobrescrita y perdida** la próxima vez que se actualicen las dependencias (ej. `composer update` o `npm install`).
-   **Licenciamiento y Legalidad:** Alterar código de terceros puede violar los términos de su licencia de software.
-   **Soporte:** Es imposible recibir soporte del autor original o de la comunidad si el código ha sido modificado.

**Anti-Patrón (Código a Evitar):**

Editar directamente un archivo de un plugin, como `media/plugins/dataTable/2.3.1/js/datatables.js`, para cambiar su comportamiento.

```javascript
// INCORRECTO: Se edita el archivo original de la librería para cambiar un texto.
return (
    '<tr ' + klass + '>' +
    '<td>' + (col.title ? col.title + ':' : 'Campo:') + '</td> ' + // ¡Cambio no autorizado!
    '<td>' + col.data + '</td>' +
    '</tr>'
);
```

**Patrón Correcto (Código a Seguir):**

La forma correcta de alterar o extender el comportamiento de una librería externa es a través de los mecanismos que esta proporciona:

-   **Configuración:** La mayoría de las librerías (como DataTables) permiten personalizar su comportamiento a través de un objeto de configuración al momento de inicializarlas en el código propio del módulo (ej. en `Glosario/js/admin.js`).
-   **Herencia:** Si la librería está basada en clases, se puede extender la clase original y sobreescribir los métodos necesarios en una clase propia.
-   **Forking (Último Recurso):** Si un cambio es indispensable y no se puede lograr por otros medios, el procedimiento correcto es crear un "fork" del repositorio original, aplicar los cambios en el fork y apuntar el `composer.json` o `package.json` a dicho fork. Esta decisión debe ser documentada y aprobada por el equipo de arquitectura.

## 17. Estándares para APIs (RESTful)

Para cualquier desarrollo de API (ej. para servicios, aplicaciones móviles o SPAs), se DEBEN seguir los siguientes principios RESTful.

### 17.1. Uso de Verbos y Status Codes HTTP
- **Verbos:** Utilizar los verbos HTTP de forma semántica:
    - `GET`: Para obtener recursos.
    - `POST`: Para crear nuevos recursos.
    - `PUT` / `PATCH`: Para actualizar recursos existentes.
    - `DELETE`: Para eliminar recursos.
- **Status Codes:** Utilizar los códigos de estado HTTP para indicar el resultado de una operación:
    - `200 OK`: Petición exitosa.
    - `201 Created`: Recurso creado con éxito.
    - `204 No Content`: Petición exitosa, pero no hay contenido que devolver (ej. en un `DELETE`).
    - `400 Bad Request`: La petición del cliente es inválida (ej. faltan parámetros).
    - `401 Unauthorized`: El cliente no está autenticado.
    - `403 Forbidden`: El cliente está autenticado, pero no tiene permiso para realizar la acción.
    - `404 Not Found`: El recurso solicitado no existe.
    - `500 Internal Server Error`: Ocurrió un error inesperado en el servidor.

### 17.2. Estructura de la Respuesta (JSON)
- Todas las respuestas de la API DEBEN estar en formato JSON.
- Se recomienda una estructura de respuesta consistente:

### 17.4. Estructura de Respuestas AJAX

Las peticiones realizadas desde JavaScript (vía `fetch` o `XMLHttpRequest`) NO DEBEN recibir fragmentos de HTML. En su lugar, DEBEN recibir una respuesta en formato **JSON**.

El front-end es responsable de interpretar este JSON y actualizar el DOM. Esto promueve un desacoplamiento claro y facilita el mantenimiento.

**Ejemplo de respuesta JSON para una lista de carpetas:**

```json
{
  "success": true,
  "data": [
    { "id": 10, "name": "Contratos 2023", "type": "signatura" },
    { "id": 12, "name": "Facturas Proveedores", "type": "signatura" },
    { "id": 15, "name": "Recibos de Caja", "type": "expediente" }
  ],
  "message": "Recursos obtenidos con éxito."
}
```

### 17.3. Versionado
- Las APIs DEBEN ser versionadas para permitir cambios futuros sin romper la compatibilidad con clientes antiguos. El versionado se DEBE incluir en la URL (ej. `/api/v1/...`).

## 18. Manejo de Errores y Excepciones

Un manejo de errores robusto es fundamental para la estabilidad de la aplicación y una buena experiencia de usuario.

### 18.1. Principios Fundamentales

-   **Separación de Responsabilidades:** La lógica de negocio (Clases de Gestión en `/lib/`) NUNCA debe mostrar errores al usuario ni realizar redirecciones. Su única responsabilidad es ejecutar la lógica y, si falla, **lanzar una excepción** (`throw new \Exception(...)`). El **Controlador** es el responsable de capturar (`catch`) esa excepción, registrar el error técnico (`error_log`) y presentar un mensaje amigable al usuario (`setMsg()`).

-   **Excepciones, no `false`:** Los métodos que pueden fallar (ej. al interactuar con la base de datos) DEBEN lanzar excepciones en lugar de retornar `false`, `null` o un `string` de error. Esto hace que los fallos sean explícitos e imposibles de ignorar.

-   **Diferenciación de Entornos:** La plataforma ya distingue entre entornos (`local` vs. `production`). En `local`, se utiliza **Whoops** para mostrar errores detallados. En `production`, los errores detallados NUNCA deben mostrarse al usuario; deben registrarse en logs y el usuario debe ver un mensaje genérico.

-   **Registro Centralizado:** Todos los errores inesperados capturados en un bloque `catch` DEBEN ser registrados usando `error_log()`.

### 18.2. Clases de Gestión (Capa de Lógica)

**Anti-Patrón (Código a Evitar):**

El método de gestión retorna un booleano, ocultando la causa real del error y forzando al controlador a adivinar qué salió mal.

```php
// INCORRECTO: El método en la clase de gestión retorna `false` en caso de error.
public function saveRadicado($datos)
{
    // ...
    $resultado = $radicado->save();
    if (!$resultado) {
        error_log($radicado->getMsgError()); // Mezcla de responsabilidades
        return false; // Devuelve un booleano ambiguo
    }
    return $radicado->id;
}
```

**Patrón Correcto (Código a Seguir):**

El método lanza una excepción clara y específica si la operación falla.

```php
// CORRECTO: El método lanza una excepción con un mensaje claro.
public function saveRadicado(array $datos): int
{
    $radicado = new TnSGDRadicados($datos);
    // ... Llenar el modelo ...

    if ($radicado->save()) {
        return $radicado->id;
    }

    // Lanza una excepción con un mensaje específico.
    throw new \Exception("No se pudo guardar el radicado: " . $radicado->getMsgError());
}
```

### 18.3. Controladores (Capa de Presentación)

El controlador debe envolver las llamadas a la lógica de negocio en bloques `try-catch` y gestionar las transacciones de base de datos.

**Patrón Correcto (Código a Seguir):**

```php
// CORRECTO: El controlador envuelve la lógica en un try-catch y maneja la transacción.
public function createProcess()
{
    $db = \bd::getEloquent();
    try {
        $db->beginTransaction();

        $radicado_id = $this->gstRadicados->saveRadicado($_POST);
        // ... otra lógica de negocio que puede fallar ...

        $db->commit();
        setMsg('Radicado creado con éxito.', 'ok');
        return redirect(genUrl(SGD_MODULO, 'RadicadoEntrada', 'lst'));

    } catch (\Exception $e) {
        $db->rollBack();

        // 1. Registrar el error técnico para los desarrolladores.
        error_log('Error en RadicadoEntrada::createProcess: ' . $e->getMessage());

        // 2. Mostrar un mensaje amigable al usuario.
        setMsg('No fue posible procesar su solicitud en este momento. Por favor, intente de nuevo más tarde.', 'error');

        // 3. Redirigir de vuelta al formulario.
        return redirect(genUrl(SGD_MODULO, 'RadicadoEntrada', 'create'));
    }
}