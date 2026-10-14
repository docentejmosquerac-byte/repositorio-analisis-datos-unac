"""Genera analisis_ign_games.ipynb. Ejecutar luego con nbconvert."""
import nbformat as nbf
from conclusiones import UNI, BI, GEN, HTML

nb = nbf.v4.new_notebook()
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md("""
# Análisis exploratorio — Reseñas de videojuegos IGN

**Fuente:** tabla `public.ign_games` en Supabase (PostgreSQL), cargada desde `IGN games from best to worst (1).csv`.

**Contenido:**
0. Limpieza de datos
1. Análisis univariado
2. Análisis bivariado
3. Análisis gráfico
""")

md("## Conexión a Supabase y carga de datos")
code("""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()  # lee DIRECT_URL desde el archivo .env
engine = create_engine(os.environ["DIRECT_URL"])

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (11, 5)
pd.set_option("display.max_columns", 20)

df_raw = pd.read_sql("SELECT * FROM public.ign_games", engine)
print(df_raw.shape)
df_raw.head()
""")
code("df_raw.info()")

# ---------------- 0. LIMPIEZA ----------------
md("""
---
## 0. Limpieza de datos

Revisamos: tipos de datos, valores nulos, duplicados, espacios sobrantes, fechas inválidas y valores atípicos.
""")
code("""
df = df_raw.copy()
print("Nulos por columna:")
print(df.isna().sum())
print("\\nFilas duplicadas exactas:", df.duplicated().sum())
""")
md("### 0.1 Espacios en blanco en columnas de texto")
code("""
cols_texto = ["title", "score_phrase", "platform", "genre"]
for c in cols_texto:
    df[c] = df[c].str.strip()
df[cols_texto].describe()
""")
md("### 0.2 Eliminar duplicados")
code("""
antes = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print(f"Duplicados eliminados: {antes - len(df)}  ->  filas restantes: {len(df)}")
""")
md("### 0.3 Valores nulos en `genre`\nSon muy pocos; se imputan con la etiqueta `Desconocido` para no perder la reseña.")
code("""
print("Juegos sin género:", df["genre"].isna().sum())
df["genre"] = df["genre"].fillna("Desconocido")
""")
md("### 0.4 Fechas: validación y columna `fecha`")
code("""
df["fecha"] = pd.to_datetime(
    dict(year=df.release_year, month=df.release_month, day=df.release_day), errors="coerce"
)
print("Fechas inválidas:", df["fecha"].isna().sum())
df["release_year"].value_counts().sort_index().head()
""")
md("Aparece un registro en **1970**, muy lejos del resto (IGN empieza a reseñar en 1996). Es un error de captura, así que lo eliminamos.")
code("""
display(df[df.release_year < 1996])
df = df[df.release_year >= 1996].reset_index(drop=True)
""")
md("### 0.5 Validar rango de `score` y coherencia con `score_phrase`")
code("""
print("Score fuera de [0, 10]:", (~df.score.between(0, 10)).sum())
df.groupby("score_phrase")["score"].agg(["min", "max", "count"]).sort_values("min")
""")
md("Cada frase corresponde a un rango fijo de puntaje, sin solapamientos: la columna es consistente. La convertimos a **categoría ordenada**.")
code("""
orden_frases = ["Disaster", "Unbearable", "Painful", "Awful", "Bad", "Mediocre",
                "Okay", "Good", "Great", "Amazing", "Masterpiece"]
df["score_phrase"] = pd.Categorical(df["score_phrase"], categories=orden_frases, ordered=True)
""")
md("### 0.6 Variables derivadas\n- `genero_principal`: primer género listado (`\"Action, RPG\"` → `Action`), reduce 112 combinaciones a pocas categorías.\n- `num_generos`: cuántos géneros tiene el juego.\n- `periodo`: tramo de años.")
code("""
df["genero_principal"] = df["genre"].str.split(",").str[0].str.strip()
df["num_generos"] = df["genre"].str.count(",") + 1
df["periodo"] = pd.cut(df.release_year, bins=[1995, 2000, 2005, 2010, 2016],
                       labels=["1996-2000", "2001-2005", "2006-2010", "2011-2016"])
print("Géneros originales:", df.genre.nunique(), " -> géneros principales:", df.genero_principal.nunique())
print("Plataformas:", df.platform.nunique())
print("Dataset limpio:", df.shape)
df.head()
""")
md("**Resumen de limpieza:** se quitaron espacios, se eliminaron 48 duplicados, se imputaron 36 géneros nulos, se descartó 1 registro con año atípico (1970), se validaron fechas y rangos de puntaje, y se crearon variables derivadas.")

# ---------------- 1. UNIVARIADO ----------------
md("---\n## 1. Análisis univariado")
md("### 1.1 `score` (puntaje, variable numérica)")
code("""
s = df["score"]
resumen = pd.Series({
    "media": s.mean(), "mediana": s.median(), "moda": s.mode()[0],
    "desv. estándar": s.std(), "mínimo": s.min(), "máximo": s.max(),
    "Q1": s.quantile(.25), "Q3": s.quantile(.75), "rango IQR": s.quantile(.75) - s.quantile(.25),
    "asimetría": s.skew(), "curtosis": s.kurt(),
}).round(2)
resumen
""")
code("""
q1, q3 = s.quantile([.25, .75]); iqr = q3 - q1
atipicos = df[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]
print(f"Atípicos por IQR (score < {q1 - 1.5*iqr:.2f}): {len(atipicos)} juegos ({len(atipicos)/len(df):.1%})")
""")
code("""
fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
sns.histplot(s, bins=40, kde=True, ax=ax[0], color="#4C72B0")
ax[0].axvline(s.mean(), color="red", ls="--", label=f"media {s.mean():.2f}")
ax[0].axvline(s.median(), color="green", ls="--", label=f"mediana {s.median():.2f}")
ax[0].legend(); ax[0].set_title("Distribución del puntaje")
sns.boxplot(x=s, ax=ax[1], color="#4C72B0"); ax[1].set_title("Boxplot del puntaje")
plt.tight_layout(); plt.show()
""")
md("### 1.2 `score_phrase` (categórica ordinal)")
code("""
frec = df["score_phrase"].value_counts().reindex(orden_frases)
tabla = pd.DataFrame({"frecuencia": frec, "porcentaje": (frec / frec.sum() * 100).round(2)})
tabla
""")
code("""
ax = frec.plot(kind="bar", color=sns.color_palette("RdYlGn", len(frec)))
ax.set_title("Cantidad de juegos por calificación"); ax.set_ylabel("juegos"); plt.xticks(rotation=45); plt.show()
""")
md("### 1.3 `platform`")
code("""
plat = df["platform"].value_counts()
print("Plataformas distintas:", len(plat))
print(f"Top 10 concentra el {plat.head(10).sum()/plat.sum():.1%} de las reseñas")
plat.head(15).to_frame("juegos")
""")
code("""
plat.head(15).sort_values().plot(kind="barh", color="#55A868")
plt.title("Top 15 plataformas con más reseñas"); plt.xlabel("juegos"); plt.show()
""")
md("### 1.4 `genero_principal`")
code("""
gen = df["genero_principal"].value_counts()
(gen / gen.sum() * 100).round(2).head(15).to_frame("% de juegos")
""")
code("""
gen.head(12).sort_values().plot(kind="barh", color="#C44E52")
plt.title("Top 12 géneros principales"); plt.xlabel("juegos"); plt.show()
""")
md("### 1.5 `release_year` y `release_month`")
code("""
anio = df["release_year"].value_counts().sort_index()
print("Año con más reseñas:", anio.idxmax(), f"({anio.max()} juegos)")
fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
anio.plot(marker="o", ax=ax[0]); ax[0].set_title("Juegos reseñados por año")
mes = df["release_month"].value_counts().sort_index()
mes.plot(kind="bar", ax=ax[1], color="#8172B2"); ax[1].set_title("Juegos por mes de lanzamiento")
plt.tight_layout(); plt.show()
print("Mes con más lanzamientos:", mes.idxmax())
""")
md("### Conclusiones del análisis univariado\n\n" + UNI)

# ---------------- 2. BIVARIADO ----------------
md("---\n## 2. Análisis bivariado")
md("### 2.1 `score` vs `release_year` (numérica – numérica)")
code("""
r_pearson = df["score"].corr(df["release_year"])
r_spearman = df["score"].corr(df["release_year"], method="spearman")
print(f"Correlación de Pearson:  {r_pearson:.3f}")
print(f"Correlación de Spearman: {r_spearman:.3f}")
por_anio = df.groupby("release_year")["score"].agg(["mean", "median", "count"]).round(2)
por_anio
""")
md("### 2.2 Matriz de correlación entre variables numéricas")
code("""
num = df[["score", "release_year", "release_month", "release_day", "num_generos"]]
corr = num.corr().round(3)
sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, fmt=".2f")
plt.title("Matriz de correlación"); plt.show()
""")
md("### 2.3 `score` vs `genero_principal` (numérica – categórica)")
code("""
top_gen = gen[gen >= 100].index
g = (df[df.genero_principal.isin(top_gen)]
     .groupby("genero_principal")["score"].agg(["mean", "median", "std", "count"])
     .round(2).sort_values("mean", ascending=False))
g
""")
md("### 2.4 `score` vs `platform` (plataformas con ≥ 200 reseñas)")
code("""
top_plat = plat[plat >= 200].index
p = (df[df.platform.isin(top_plat)]
     .groupby("platform")["score"].agg(["mean", "median", "count"])
     .round(2).sort_values("mean", ascending=False))
p
""")
md("### 2.5 `score` vs `num_generos`")
code("""
df.groupby("num_generos")["score"].agg(["mean", "count"]).round(2)
""")
md("### 2.6 `genero_principal` vs `periodo` (categórica – categórica)")
code("""
ct = pd.crosstab(df[df.genero_principal.isin(gen.head(8).index)].genero_principal,
                 df.periodo, normalize="columns").mul(100).round(1)
ct
""")
md("### 2.7 `score_phrase` vs `periodo`")
code("""
pd.crosstab(df.score_phrase, df.periodo, normalize="columns").mul(100).round(1)
""")
md("### Conclusiones del análisis bivariado\n\n" + BI)

# ---------------- 3. GRÁFICO ----------------
md("---\n## 3. Análisis gráfico")
md("### 3.1 Puntaje promedio y cantidad de reseñas por año")
code("""
fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.bar(por_anio.index, por_anio["count"], color="#B0C4DE", label="cantidad de juegos")
ax1.set_ylabel("cantidad de juegos")
ax2 = ax1.twinx()
ax2.plot(por_anio.index, por_anio["mean"], color="#C44E52", marker="o", lw=2, label="puntaje medio")
ax2.set_ylabel("puntaje medio"); ax2.grid(False)
fig.legend(loc="upper left", bbox_to_anchor=(0.08, 0.92))
plt.title("Evolución de reseñas IGN (1996-2016)"); plt.show()
""")
md("### 3.2 Dispersión año vs puntaje con línea de tendencia")
code("""
sns.regplot(data=df, x="release_year", y="score", x_jitter=0.3,
            scatter_kws={"alpha": 0.08, "s": 10}, line_kws={"color": "red"})
plt.title(f"Año vs puntaje (r = {r_pearson:.2f})"); plt.show()
""")
md("### 3.3 Distribución del puntaje por género (boxplot)")
code("""
orden = g.index
plt.figure(figsize=(13, 6))
sns.boxplot(data=df[df.genero_principal.isin(top_gen)], x="genero_principal", y="score", order=orden)
plt.xticks(rotation=45, ha="right"); plt.title("Puntaje por género principal (ordenado por media)"); plt.show()
""")
md("### 3.4 Puntaje medio por plataforma")
code("""
plt.figure(figsize=(10, 7))
sns.barplot(x=p["mean"], y=p.index, hue=p.index, palette="viridis", legend=False)
plt.axvline(df.score.mean(), color="red", ls="--", label="media global")
plt.legend(); plt.title("Puntaje medio por plataforma (≥ 200 reseñas)"); plt.xlabel("puntaje medio"); plt.show()
""")
md("### 3.5 Mapa de calor: puntaje medio por género y periodo")
code("""
pivot = (df[df.genero_principal.isin(top_gen)]
         .pivot_table(index="genero_principal", columns="periodo", values="score", aggfunc="mean", observed=False)
         .round(2))
plt.figure(figsize=(9, 7))
sns.heatmap(pivot, annot=True, cmap="RdYlGn", fmt=".2f")
plt.title("Puntaje medio por género y periodo"); plt.show()
""")
md("### 3.6 Densidad del puntaje por periodo")
code("""
sns.kdeplot(data=df, x="score", hue="periodo", common_norm=False, fill=True, alpha=0.25)
plt.title("Distribución del puntaje según periodo"); plt.show()
""")
md("### 3.7 Composición de calificaciones por periodo")
code("""
comp = pd.crosstab(df.periodo, df.score_phrase, normalize="index").mul(100)
comp.plot(kind="bar", stacked=True, colormap="RdYlGn", figsize=(12, 5))
plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left"); plt.ylabel("% de juegos")
plt.title("Composición de calificaciones por periodo"); plt.xticks(rotation=0); plt.show()
""")
md("### Conclusiones generales\n\n" + GEN)
md(HTML)

nb["cells"] = cells
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "analisis_ign_games.ipynb")
print("notebook creado")
