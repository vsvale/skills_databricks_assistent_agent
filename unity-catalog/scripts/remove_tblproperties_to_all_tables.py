%pip install dbl-discoverx

from_tables = ".".join(["*", "*", "*"])

from discoverx import DX

dx = DX()

df_unset = dx.from_tables(from_tables).with_sql("""ALTER TABLE {full_table_name} UNSET TBLPROPERTIES (
  delta.autoOptimize.autoCompact)""").apply()