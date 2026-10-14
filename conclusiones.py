UNI = """- **Puntaje (`score`)**: media de **6.95** y mediana de **7.30**; la moda es **8.0**. La asimetría negativa (**-0.85**) indica que la mayoría de juegos recibe notas altas y hay una cola larga hacia notas bajas. El 50 % central está entre 6.0 y 8.2.
- **Atípicos**: 389 juegos (2.1 %) tienen menos de 2.7 puntos; son reseñas reales muy negativas, no errores, así que se conservan.
- **Calificaciones**: *Great* (25.6 %) y *Good* (25.4 %) concentran más de la mitad de las reseñas. Las notas extremas son raras: solo 55 *Masterpiece* (0.3 %) y 3 *Disaster*.
- **Plataformas**: hay 59, pero el top 10 concentra el **75 %** de las reseñas. **PC** domina con 3 365 juegos, casi el doble que la siguiente (PlayStation 2).
- **Géneros**: *Action* es el género principal del **27 %** de los juegos, seguido de *Sports* (11.7 %) y *Shooter* (8.8 %).
- **Tiempo**: las reseñas crecen hasta un pico en **2008** (1 911 juegos) y luego caen. **Noviembre** es el mes con más lanzamientos (temporada navideña)."""

BI = """- **Año vs puntaje**: la correlación lineal es casi nula (Pearson **0.06**), pero la media por año no es plana: sube hasta ~7.2 en 2003-2005, cae a su mínimo en **2008 (6.45)** —el año con más reseñas— y desde 2011 sube hasta **7.66 en 2015**. La relación existe pero no es lineal.
- **Género vs puntaje**: *RPG* (7.57) y *Strategy* (7.29) son los géneros mejor valorados; *Party* (5.85) y *Hunting* (5.67) los peores. *Action*, el más numeroso, queda por debajo de la media (6.81).
- **Plataforma vs puntaje**: las consolas más recientes (**PS4 y Xbox One, 7.66**) tienen las notas más altas; **Wii, Nintendo DS y Game Boy Color** (~6.2-6.3) las más bajas, probablemente por la gran cantidad de juegos casuales o de baja calidad en esas plataformas.
- **Nº de géneros vs puntaje**: los juegos con 2 géneros promedian **7.21** frente a **6.91** de los de un solo género.
- **Género vs periodo**: *Sports* pasa del 20.9 % al 8.1 % y *Racing* del 17.2 % al 5.1 %, mientras que *Shooter* (3.8 % → 15.4 %), *Adventure* (5.1 % → 14.6 %) y *RPG* (5.8 % → 10.7 %) ganan peso.
- **Calificación vs periodo**: en 2011-2016 el 16.4 % de los juegos es *Amazing*, frente al 5.6 % de 2006-2010."""

GEN = """1. IGN califica de forma generosa: la nota típica está entre 7 y 8 y las notas bajas son minoría.
2. La calidad percibida cambia con el tiempo de forma no lineal: el *boom* de 2006-2010 (Wii, DS, muchos lanzamientos) trajo más juegos y notas más bajas; desde 2011 hay menos reseñas y mejor valoradas, posiblemente porque IGN reseña menos títulos y más seleccionados.
3. El género influye en la nota: RPG y estrategia destacan; juegos de fiesta, caza y trivia quedan al final.
4. La plataforma también importa: las de generación reciente puntúan más alto y las portátiles o casuales de Nintendo, más bajo.
5. El catálogo cambió de deportes y carreras a shooters, aventuras y RPG.

> Las relaciones encontradas son descriptivas (correlación, no causalidad)."""

HTML = """---
## Cómo exportar este notebook a HTML

Desde la terminal, en la carpeta del notebook:

```bash
python -m nbconvert --to html --execute analisis_ign_games.ipynb
```

`--execute` vuelve a ejecutar todas las celdas (consultando Supabase) antes de exportar. Para ocultar el código y dejar solo resultados, se agrega `--no-input`. En Jupyter/VS Code también se puede usar **Archivo → Exportar → HTML**."""
