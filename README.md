# Análisis de sensores industriales

## Objetivo
Analizar con Python las mediciones de temperatura y vibración de sensores instalados en cuatro plantas industriales, identificar las lecturas con alerta de temperatura (mayor que 85 °C) y documentar el caso desde la perspectiva de Big Data.

## Datos
El archivo `data/sensores_industriales.csv` contiene 100,000 mediciones **simuladas**. No son datos reales de una empresa.

| Columna | Significado |
|---|---|
| id_registro | Identificador de la medición |
| fecha_hora | Fecha y hora de la lectura |
| id_sensor | Identificador del sensor |
| planta | Planta donde está instalado |
| temperatura_c | Temperatura en grados Celsius |
| vibracion_mm_s | Vibración en milímetros por segundo |

El umbral de alerta (85 °C) es una regla didáctica del ejercicio.

## Instalación y ejecución

```bash
git clone https://github.com/Uri160121/sensores-industriales.git
cd sensores-industriales
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python analisis.py
```

El programa imprime los resultados en pantalla y guarda las lecturas con alerta en `resultados/alertas.csv`.

## Contenido del repositorio
- `analisis.py`: programa de análisis
- `data/`: CSV original
- `resultados/alertas.csv`: lecturas con temperatura mayor que 85 °C
- `informe.md`: respuestas de la Parte II (Big Data)
- `evidencias/`: captura de la ejecución reproducible
