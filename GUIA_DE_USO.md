# Guía de uso · Cuentacuentos en Familia

Esta guía explica cómo funciona la web de reservas, sin tecnicismos. Tiene dos partes:

- **Parte 1 — Las familias:** cómo entra alguien en la web, reserva y cancela.
- **Parte 2 — Quien organiza (administrador):** cómo crear pases, ver quién viene,
  descargar el listado en Excel y borrar un pase.

| | |
|---|---|
| **Web pública** | https://cuentacuentosaranjuez2026.pythonanywhere.com/ |
| **Panel de administración** | https://cuentacuentosaranjuez2026.pythonanywhere.com/admin |

---

## Lo esencial en un minuto

- La web **solo sirve para reservar plaza**. No cobra nada: el importe se abona en la
  entrada del pase, y así lo avisa la web en la portada y al confirmar la reserva.
- Cada día de cuentacuentos puede tener dos **pases**: el de las **11:00** y el de las **12:00**.
- Cada reserva es de **una familia**: mínimo **1 adulto y 1 menor**, máximo **4 personas** en total.
- Las reservas se **cierran 5 horas antes** de cada pase.
- La familia recibe un **email de confirmación** con un enlace para **cancelar** si no puede ir.
- Quien organiza entra en el **panel** con una contraseña, y desde ahí crea los pases,
  ve las reservas y descarga el listado para la puerta.

---

# Parte 1 — Las familias

## Cómo se reserva, paso a paso

1. **Entrar en la web.** No hace falta registrarse ni tener cuenta.
2. **Elegir pase.** En «Próximas sesiones» aparece una tarjeta por cada fecha y, dentro,
   los pases de ese día. Cada pase muestra cómo está:

   | Lo que se ve | Qué significa |
   |---|---|
   | «36 de 40 libres» + botón **Reservar** | Quedan plazas y se puede reservar. |
   | «Completo» | No quedan plazas. |
   | «Reservas cerradas» | Faltan menos de 5 horas para el pase. |

3. **Pulsar «Reservar»** y rellenar el formulario. **Todos los campos son obligatorios:**
   - **Nombre**, **primer apellido**, **segundo apellido** y **email** de quien hace la reserva.
   - Número de **adultos** y de **menores**, que se cambia con los botones **−** y **+**
     (no se puede escribir el número a mano).
   - El **nombre de cada asistente**: al añadir personas aparece un recuadro por cada una.
     El primero se rellena solo con el nombre de quien reserva (se puede cambiar).
4. **Pulsar «Confirmar reserva».** Si algo no está bien, el aviso sale justo encima del
   botón y no se pierde nada de lo escrito.
5. **Reserva hecha.** La web enseña el **número de reserva** (por ejemplo `3110_1100_01`:
   día 31/10, pase de las 11:00, reserva nº 1) y envía un **email de confirmación**.

> Si el email no llega en unos minutos, que miren en la carpeta de **spam**.

## Si ese email ya tenía una reserva en el mismo pase

Al pulsar «Confirmar reserva» aparece una ventana: **«Ya tienes una reserva para este
día. ¿Confirmar nueva reserva?»**

- **Confirmar:** se guarda una segunda reserva, con su propio número y su propio email
  de confirmación. La primera sigue existiendo.
- **Cancelar:** se cierra la ventana y se vuelve al formulario, sin guardar nada.

El aviso solo sale si coinciden el email y el pase. Reservar con el mismo email en el
otro pase del día no avisa.

## Qué lleva el email de confirmación

- Número de reserva, pase, fecha y hora.
- Cuántas plazas (adultos y menores) y los nombres de los asistentes.
- Un **enlace para cancelar** la reserva.

En la entrada se pide el **nombre y apellidos** de quien reservó.

## Cómo cancela una familia

1. Abre el enlace **«cancelar»** del email de confirmación.
2. La web pregunta «¿Cancelar tu reserva?». Pulsa **«Sí, cancelar mi reserva»**.
3. Las plazas quedan libres al momento para otra familia y llega un email confirmando
   la cancelación.

Se puede cancelar **hasta la hora de inicio del pase**, aunque las reservas ya estén cerradas.

## Cómo cambia una familia su reserva

No se puede editar una reserva. Para cambiar algo (personas, nombres, pase) hay que
**cancelarla y volver a reservar**, siempre que queden plazas y las reservas sigan abiertas.

## Normas: qué puede y qué no puede hacer una familia

| ✅ Puede | ❌ No puede |
|---|---|
| Reservar sin registrarse. | Reservar sin al menos **1 adulto y 1 menor**. |
| Reservar de 2 a 4 personas: 1+1, 1+2, 2+1, 1+3, 2+2 o 3+1 (adultos + menores). | Reservar para **más de 4 personas**. |
| Reservar en los dos pases del mismo día (son reservas distintas). | Reservar más plazas de las que quedan libres. |
| Hacer otra reserva con el mismo email en el mismo pase, confirmándolo en el aviso. | Reservar cuando faltan **menos de 5 horas** o el pase está completo. |
| Cancelar su reserva desde el enlace del email. | Dejar algún campo sin rellenar, incluidos los nombres de los asistentes. |
| Volver a reservar después de cancelar. | Ver o cancelar reservas de otras familias (cada enlace es secreto y único). |

---

# Parte 2 — Quien organiza (administrador)

## Entrar y salir

1. Ir a **/admin** (la dirección está al principio de esta guía). No hay ningún enlace
   en la web pública: hay que escribir la dirección o guardarla en favoritos.
2. Escribir la **contraseña** y pulsar «Entrar».
3. Mientras se está dentro, arriba a la derecha aparecen **Panel** y **Salir**.
4. Al terminar, pulsar **Salir**, sobre todo en un ordenador o móvil compartido.

Hay **una sola contraseña** para todo el equipo; no hay usuarios individuales.
Quien la tenga puede hacer todo lo que se explica aquí, así que conviene compartirla
solo con quien haga falta. Para cambiarla, hablar con quien mantiene la web.

## El panel

Es la lista de **todos los pases**, también los ya pasados (en gris). De cada uno se ve:

- **Fecha** y hora.
- **Sesión**: «Pase de las 11:00» o «Pase de las 12:00».
- **Ocupación**: plazas reservadas / plazas totales (por ejemplo `36 / 40`).
- **Ver reservas**: abre el listado de ese pase.

## Crear un pase

1. En el panel, pulsar **«+ Nueva sesión»**.
2. Elegir la **fecha**. No se pueden elegir días pasados.
3. Elegir la **hora del pase** en el desplegable: **11:00** o **12:00**.
4. Escribir las **plazas** (el aforo: cuenta a todas las personas, adultos y menores).
5. Pulsar **«Crear»**.

El pase aparece al momento en la web pública, dentro de la tarjeta de su fecha.
El título se pone solo («Pase de las 11:00»); el lugar, el precio y lo demás ya salen
en el cartel de la portada.

**No puede haber dos pases el mismo día a la misma hora.** Si un día ya tiene el pase de
las 11:00, esa hora sale desactivada y marcada «(ya creado)». Si ya tiene los dos, la web
avisa de que ese día está completo.

## Ver las reservas de un pase

En el panel, pulsar **«Ver reservas»**. De cada reserva se ve:

- **Nº** de reserva.
- **Titular** (nombre y apellidos de quien reservó) y su **email**.
- Número de **adultos** y de **menores**.
- **Asistentes**: los nombres de todos, con los menores aparte.

Al final hay una fila con el **total** de adultos y de menores.
En el móvil cada reserva se muestra como una ficha, para no tener que desplazarse de lado.

## Descargar el listado en Excel

1. Entrar en **«Ver reservas»** del pase.
2. Pulsar **«Descargar listado (Excel)»** (el botón solo aparece si hay alguna reserva).
3. Se descarga un archivo llamado, por ejemplo, `listado_3110_1100.csv`, que se abre con
   Excel con doble clic.

El listado está pensado para **imprimirlo y llevarlo a la puerta**:

- Va ordenado por **apellidos**.
- Columnas: Nº reserva · Apellidos · Nombre · Adultos · Menores · Total ·
  Nombres adultos · Nombres menores · **Asistencia** (en blanco, para ir marcando).
- La última fila es el **total** de personas.

Conviene descargarlo **cuando ya estén cerradas las reservas** (5 horas antes), para que
sea el definitivo. Aun así, alguna familia puede cancelar hasta la hora del pase.

## Borrar (cancelar) un pase

1. Entrar en **«Ver reservas»** del pase.
2. Abajo del todo, pulsar el botón rojo **«Borrar sesión»**.
3. Confirmar en la ventana que aparece.

**Qué ocurre:**

- El pase desaparece de la web y del panel, con **todas sus reservas**.
- Si el pase aún no se ha celebrado, la web envía **un email a cada familia** avisando de
  que se ha cancelado. La propia pantalla indica a cuántas reservas se avisará.
- Si el pase ya pasó, se borra sin avisar a nadie.

> ⚠️ **No se puede deshacer.** Si se borra por error un pase con reservas, las familias ya
> habrán recibido el aviso de cancelación y tendrán que volver a reservar.

Los pases ya celebrados no hace falta borrarlos: dejan de verse en la web pública solos
y se quedan en gris en el panel, por si se quiere consultar quién vino.

## Cambiar un pase (fecha, hora o plazas)

**Un pase no se puede editar.** Las opciones son:

- **Si aún no tiene reservas:** borrarlo y crearlo de nuevo con los datos correctos.
- **Si ya tiene reservas:** borrarlo avisa por email a todas las familias de que se ha
  cancelado, y tendrían que reservar otra vez. Antes de hacerlo conviene pensar si
  compensa, o escribirles primero para explicarlo.
- **Para ampliar plazas** sin tocar el pase: no es posible desde el panel; hay que
  pedírselo a quien mantiene la web.

## Cancelar o cambiar la reserva de una familia

**Desde el panel no se puede** borrar ni modificar una reserva suelta. Lo que sí se puede:

- **Pedir a la familia que cancele** desde el enlace de su email de confirmación.
- Si quieren cambiarla, que cancelen y **vuelvan a reservar**.
- Si han perdido el email y no pueden cancelar, anotarlo a mano en el listado impreso.
  Su plaza seguirá contando como ocupada en la web.

## Apuntar a una familia que avisa por teléfono

No hay botón de «añadir reserva» en el panel. Se hace igual que cualquier familia:
entrando en la web pública y rellenando el formulario con sus datos. Hay que tener en cuenta:

- Hace falta un **email** (a esa dirección llegará la confirmación y el enlace de cancelar).
- Si ese email ya tiene una reserva en el mismo pase, la web pide confirmación antes de
  guardar otra.
- Si las reservas ya están cerradas o el pase está completo, no se puede.

## Normas: qué puede y qué no puede hacer el administrador

| ✅ Puede | ❌ No puede (desde el panel) |
|---|---|
| Crear pases a las 11:00 y a las 12:00 en cualquier fecha futura. | Crear dos pases el mismo día a la misma hora. |
| Ver todas las reservas, con nombres, emails y asistentes. | Crear pases a otras horas o en fechas pasadas. |
| Descargar el listado de cada pase en Excel. | Editar un pase ya creado (fecha, hora o plazas). |
| Borrar un pase (avisando por email a las familias). | Borrar o modificar la reserva de una sola familia. |
| Consultar pases ya celebrados. | Añadir reservas saltándose las normas (aforo, cierre, máximo 4). |
| | Cambiar los carteles, los textos o la contraseña. |

Lo de la columna derecha no es imposible: son cosas que hoy no tiene el panel y que
puede añadir o cambiar quien mantiene la web.

---

# Emails que envía la web

| Cuándo | A quién | Qué dice |
|---|---|---|
| Al hacer una reserva | A la familia | Confirmación con los datos y el enlace para cancelar. |
| Al cancelar la familia | A la familia | Confirmación de que la reserva está anulada. |
| Al borrar el administrador un pase futuro | A todas las familias con reserva | Aviso de que el pase se ha cancelado. |

Al pie de la web y de los emails aparecen el **teléfono y el email de contacto** de la
organización, si están configurados. Si una familia responde a un email, la respuesta
llega a ese email de contacto.

Si algún email fallara al enviarse, **la reserva queda guardada igualmente** y se ve en el panel.

---

# Dudas frecuentes

**Una familia dice que no le ha llegado el email.**
Que mire en spam. Si reservó, su reserva aparece en «Ver reservas» aunque no tenga el
email. Sin el email no puede cancelar por su cuenta.

**Una familia quiere venir con 5 personas.**
La web no lo permite: el máximo es 4 por reserva. Pueden hacer una segunda reserva, que
también debe llevar al menos 1 adulto y 1 menor. Si usan el mismo email, la web les
pedirá confirmación.

**Quieren ir solo adultos, o solo menores.**
No se puede: cada reserva necesita al menos 1 adulto y 1 menor.

**El pase está completo y alguien quiere apuntarse.**
Solo podrá si otra familia cancela: la plaza vuelve a aparecer libre en la web al momento.
No hay lista de espera.

**Faltan menos de 5 horas y alguien quiere reservar.**
La web ya no admite reservas para ese pase, tampoco al administrador.

**¿Se borran solos los pases antiguos?**
No se borran, pero dejan de verse en la web pública. En el panel quedan en gris.

**La web no carga o da error.**
Avisar a quien mantiene la web. Está alojada en un servicio gratuito (PythonAnywhere)
que pide renovarla cada cierto tiempo desde su cuenta.

---

# Datos personales

La web guarda nombres, apellidos y emails de las familias, y los **nombres de los
menores**. Solo los ve quien tiene la contraseña del panel. El listado de Excel contiene
esos mismos datos: mejor no reenviarlo ni dejarlo en ordenadores compartidos, y
destruir las copias impresas después del evento.

---

*Para la parte técnica (instalación, configuración y actualización de la web), ver `README.md`.*
