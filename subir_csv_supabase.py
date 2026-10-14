"""Sube el CSV de IGN a Supabase en una tabla nueva: public.ign_games"""
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()
engine = create_engine(os.environ["DIRECT_URL"])

TABLA = "ign_games"
if inspect(engine).has_table(TABLA, schema="public"):
    raise SystemExit(f"La tabla {TABLA} ya existe; no se sobrescribe.")

df = pd.read_csv("IGN games from best to worst (1).csv")
df.to_sql(TABLA, engine, schema="public", index=False, chunksize=2000, method="multi")
print(f"{len(df)} filas subidas a public.{TABLA}")
