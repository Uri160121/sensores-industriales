from pathlib import Path
import pandas as pd

UMBRAL_C = 85  # regla didáctica del examen

RUTA_CSV = Path("data") / "sensores_industriales.csv"
RUTA_ALERTAS = Path("resultados") / "alertas.csv"

df = pd.read_csv(RUTA_CSV)

# 1) Registros y sensores distintos
print(f"Registros: {len(df)}")
print(f"Sensores distintos: {df['id_sensor'].nunique()}")

# 2) Temperatura promedio por planta
print("\nTemperatura promedio por planta (°C):")
print(df.groupby("planta")["temperatura_c"].mean().round(2).to_string())

# 3) Temperatura máxima (con empates)
t_max = df["temperatura_c"].max()
filas_max = df[df["temperatura_c"] == t_max]
print(f"\nTemperatura máxima: {t_max} °C")
print(filas_max[["id_sensor", "fecha_hora", "planta"]].to_string(index=False))

# 4) Lecturas con alerta (> 85 °C)
alertas = df[df["temperatura_c"] > UMBRAL_C]
print(f"\nLecturas con alerta (> {UMBRAL_C} °C): {len(alertas)}")

# 5) Planta(s) con más alertas (con empates)
alertas_por_planta = alertas["planta"].value_counts()
print("\nAlertas por planta:")
print(alertas_por_planta.to_string())
top = alertas_por_planta[alertas_por_planta == alertas_por_planta.max()]
print(f"\nPlanta(s) con más alertas: {', '.join(top.index)} ({top.iloc[0]} alertas)")

# 6) Exportar alertas con las columnas originales
RUTA_ALERTAS.parent.mkdir(exist_ok=True)
alertas.to_csv(RUTA_ALERTAS, index=False)
print(f"\nAlertas exportadas a {RUTA_ALERTAS}")
