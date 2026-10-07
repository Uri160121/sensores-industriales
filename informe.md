# Informe — Parte II: aplicación al caso de Big Data

**Alumno:** Uriel Moreno González · **Grupo:** IDIA222 · **Materia:** Manejo Masivo de Datos

> Los datos de `sensores_industriales.csv` son **simulados** y se usan solo con fines didácticos. El umbral de 85 °C es una regla del ejercicio, no un criterio real de falla.

Los números que uso salen de correr `analisis.py` y de revisar el mismo CSV (nulos, duplicados y rangos). El archivo tiene 100,000 mediciones de 40 sensores en 4 plantas, con una lectura por minuto por sensor entre el 01/09/26 00:00 y el 02/09/26 17:39 (2,500 lecturas por sensor).

---

## 5. Las 5 V aplicadas al proyecto

| V | Cómo se relaciona con el sistema | Ejemplo concreto | ¿Está en el CSV o es ampliación? |
|---|---|---|---|
| **Volumen** | Es la cantidad de datos que generan los sensores. | El CSV tiene 100,000 mediciones (40 sensores × 2,500 lecturas, unos 4.5 MB). Con 5,000 sensores y una lectura por segundo serían unos 432 millones de lecturas al día (5,000 × 86,400). | El CSV actual es **poco volumen**. El volumen de verdad aparece con la **ampliación**. |
| **Velocidad** | Qué tan rápido llegan los datos y qué tan rápido hay que reaccionar. | Cada sensor mide una vez por minuto, pero en el CSV esas lecturas ya están guardadas y las analizo después. En la ampliación llegarían cada segundo y habría que avisar a los pocos segundos de pasar de 85 °C. | En el CSV solo está el **ritmo de medición** (una por minuto, columna `fecha_hora`). El flujo en vivo y las lecturas por segundo son **ampliación**. |
| **Variedad** | Los distintos formatos de datos que se mezclan. | El CSV es una sola tabla con seis columnas (identificadores, fecha y hora, planta, temperatura y vibración). En la ampliación se sumarían fotos de las máquinas, reportes de mantenimiento en texto libre y mensajes JSON. | El CSV tiene **un solo tipo de dato (estructurado)**. Fotos, reportes y JSON son **ampliación**. |
| **Veracidad** | Qué tan confiables y limpios son los datos. | Revisé el CSV: 0 valores nulos, 0 filas duplicadas, temperatura entre 45.0 y 104.99 °C, vibración entre 0.5 y 5.5 mm/s y exactamente 2,500 lecturas por sensor. Pero como son datos simulados, esto no dice nada sobre fallas reales de los sensores. En un sistema real habría sensores descalibrados, lecturas perdidas por fallas de red o mensajes duplicados. | La **revisión de calidad** es del CSV actual (salió limpio). Los problemas reales de confiabilidad serían de la **ampliación**. |
| **Valor** | Qué decisiones útiles se pueden tomar con los datos. | De las 100,000 lecturas, 6,954 (6.95 %) pasan de 85 °C y Planta_3 es la que más alertas tiene (1,777). Con eso la empresa puede decidir a qué planta mandar primero una revisión. Una alerta no es una falla: solo marca dónde conviene mirar. | Este valor **sí sale del CSV actual**. Mejorarlo (anticipar fallas usando fotos y reportes) sería **ampliación**. |

---

## 6. Tipos de datos y procesamiento tradicional

### Clasificación

| Elemento | Tipo | Por qué |
|---|---|---|
| El CSV de sensores | **Estructurado** | Son filas y columnas fijas, cada columna con un tipo definido (número, fecha, texto). |
| Un mensaje JSON enviado por un sensor | **Semiestructurado** | Tiene campos con nombre (clave y valor), pero no sigue una tabla rígida: un mensaje puede traer campos distintos a otro. |
| Una fotografía de una máquina | **No estructurado** | Son píxeles, no hay campos ni columnas; hace falta procesamiento de imágenes para sacar información. |
| El texto libre de un reporte de mantenimiento | **No estructurado** | Es lenguaje natural escrito sin formato fijo; hay que interpretarlo para extraer datos. |

### ¿Por qué 100,000 registros no hacen que el archivo sea Big Data?

Big Data no depende solo del número de filas. Se habla de Big Data cuando las herramientas tradicionales ya no alcanzan por el volumen, la velocidad o la variedad de los datos. Este archivo pesa unos 4.5 MB, cabe completo en la memoria de una laptop y `analisis.py` lo procesa con pandas en segundos. Es un problema pequeño que se resuelve con herramientas normales.

### Limitaciones al aumentar la escala

- **Memoria:** pandas carga todo el archivo en la memoria de una sola computadora. Con cientos de millones de lecturas al día ya no cabría.
- **Una sola máquina:** el disco y el procesador de un solo equipo serían el cuello de botella, y si falla, se detiene todo.
- **Datos que llegan sin parar:** un CSV es un archivo estático. No sirve para recibir una lectura por segundo de miles de sensores y reaccionar a tiempo.
- **Otros formatos:** una tabla en CSV no sirve para guardar ni analizar fotos o reportes de texto libre.
- **Solución:** habría que pasar a almacenamiento y procesamiento distribuidos (varias máquinas trabajando juntas, por ejemplo con herramientas como Hadoop o Spark).

---

## 7. Batch y Streaming

**Lo que hice:** mi programa hace procesamiento **batch (por lotes)**. Lee un archivo completo que ya estaba guardado, procesa las 100,000 filas juntas y entrega los resultados al terminar. Es batch porque los datos ya estaban completos y no se esperaba que llegaran más mientras el programa corría.

**Alerta pocos segundos después de una lectura mayor que 85 °C:** usaría **streaming** (procesamiento de flujo en casi tiempo real). Cada lectura se evalúa en cuanto llega, con una regla simple (`temperatura_c > 85`), y si se cumple se emite la alerta de inmediato. Se podría armar con un sistema de mensajes (como Kafka) y un procesador de flujo (como Flink o Spark Streaming). Aquí no sirve esperar a juntar un lote, porque una alerta que llega tarde pierde su utilidad.

**Resumen al terminar el día:** usaría **batch**. Al cierre del día se procesa todo lo acumulado en una sola corrida (promedio por planta, cantidad de alertas, etc.). No hay urgencia, es más sencillo de armar y más barato, y si hay un error se puede volver a correr.

**Relación con el tiempo en que se necesita cada resultado:**

| Resultado | ¿Cuándo se necesita? | Enfoque |
|---|---|---|
| Alerta por temperatura mayor que 85 °C | En pocos segundos | Streaming |
| Resumen diario por planta | Una vez al día, al cierre | Batch |
| Análisis del historial (como `analisis.py`) | Sin urgencia | Batch |

---

## 8. Lambda y Kappa

### Escenario A: Lambda

**Elijo la arquitectura Lambda.** El escenario pide combinar una ruta que recalcule todo el historial por lotes con otra que procese rápido lo reciente, y eso es justo lo que hace Lambda: una **capa batch** (resultados completos y precisos, aunque tarden) y una **capa de velocidad** (resultados rápidos de lo más reciente), que se unen en una **capa de servicio** para consultar. La desventaja es que hay que mantener la lógica en dos lugares.

```
                  +-----------+
                  | Sensores  |
                  +-----+-----+
                        |
                        v
              +---------+----------+
              |  Ingesta de datos  |
              +----+----------+----+
                   |          |
         historial |          | lecturas recientes
                   v          v
        +----------+--+   +---+----------------+
        | Capa batch  |   | Capa de velocidad  |
        | (recalcula  |   | (procesa rapido    |
        |  todo el    |   |  lo reciente)      |
        |  historial) |   |                    |
        +------+------+   +---------+----------+
               |                    |
               v                    v
        +------+------+   +---------+----------+
        | Resultados  |   | Resultados rapidos |
        | por lotes   |   | (casi tiempo real) |
        +------+------+   +---------+----------+
               |                    |
               +----------+---------+
                          |
                          v
                +---------+---------+
                |  Capa de servicio |
                | (une las dos vias)|
                +---------+---------+
                          |
                          v
                 Alertas, consultas
                   y reportes
```

### Escenario B: Kappa

**Elijo la arquitectura Kappa.** El escenario pide una sola lógica de procesamiento de eventos y conservar las mediciones para volver a procesarlas, y Kappa hace exactamente eso: todo se trata como un flujo de eventos que se guarda en un **registro inmutable** y se procesa con **una sola lógica**. Si hay que corregir algo o cambiar la lógica, se vuelve a leer el registro desde el principio con el mismo procesador. Es más simple que Lambda, aunque depende de que el registro conserve los datos el tiempo suficiente y de que el procesador de flujo aguante el reprocesamiento.

```
+-----------+     +------------------------------+
| Sensores  | --> | Registro de eventos          |
+-----------+     | (log inmutable, guarda todo) |
                  +---------------+--------------+
                                  |
                                  v
                  +---------------+--------------+
                  | Procesamiento de flujo       |
                  | (una sola logica)            |
                  +---------------+--------------+
                                  |
                                  v
                  +---------------+--------------+
                  | Resultados (para consulta)   |
                  +---------------+--------------+
                                  |
                                  v
                         Alertas y reportes

Para reprocesar: se corrige la logica y se vuelve a leer el
registro de eventos desde el principio con el mismo procesador.
```

---

## 9. Analítica descriptiva, predictiva y prescriptiva

### Descriptiva (qué pasó)

1. **Alertas por planta:** de las 100,000 lecturas, **6,954** superan los 85 °C (6.95 %). Planta_3 tiene más alertas con **1,777**, seguida de Planta_1 (1,737), Planta_4 (1,732) y Planta_2 (1,708). Las diferencias entre plantas son chicas, y los promedios de temperatura también son parecidos (66.62, 66.53, 66.77 y 66.67 °C).
2. **Temperatura máxima:** el valor más alto es **104.99 °C** y lo alcanzan **cuatro lecturas empatadas**: S023 en Planta_3 (01/09/26 22:23), S019 en Planta_2 (02/09/26 13:11), S014 en Planta_2 (02/09/26 15:23) y S030 en Planta_3 (02/09/26 16:02).

### Predictiva (qué podría pasar)

**Pregunta:** ¿qué máquinas tienen más probabilidad de fallar en los próximos 7 días, a partir de cómo vienen cambiando su temperatura y su vibración?

**Datos adicionales que necesitaría:**

- Un registro de **fallas y paros** de cada máquina, con fecha. Sin esto no hay manera de saber qué lecturas terminaron en falla, y por eso con este CSV no se puede entrenar un modelo.
- Los **reportes de mantenimiento** (reparaciones, cambios de piezas) y la edad y el modelo de cada máquina.
- Datos de **carga de trabajo** y temperatura ambiente.
- Un **periodo más largo de mediciones**: el CSV cubre apenas un día y 17 horas.

### Prescriptiva (qué hacer)

**Acción propuesta:** si el análisis predictivo marca a una máquina con riesgo alto de falla, programar una **revisión preventiva** antes de que falle (por ejemplo, empezando por las máquinas de la planta o los sensores con más alertas, como S027, que tiene 211 alertas en el CSV), en lugar de esperar a que se detenga.

**Qué revisaría antes de decidir:**

- El **historial de mantenimiento** de esa máquina y si la alerta se repite o fue un pico aislado.
- Si el **sensor está calibrado**, para descartar una falsa alarma.
- La **vibración junto con la temperatura**, no solo la temperatura.
- El **costo de parar la máquina** contra el costo de que falle sola.
- Si hay técnicos y refacciones disponibles y cómo está el calendario de producción.

Una lectura arriba de 85 °C es una alerta del ejercicio. Por sí sola no demuestra que la máquina vaya a fallar, por eso la acción sería revisar y no reemplazar de entrada.
