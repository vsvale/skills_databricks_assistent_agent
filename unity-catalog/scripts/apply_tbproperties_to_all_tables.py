%pip install dbl-discoverx

from_tables = ".".join(["*", "*", "*"])

from discoverx import DX

dx = DX()

# Define how small is too small
small_file_max_size_MB = 10

# It's okay to have small files as long as there are not too many
min_file_number = 100

df = dx.from_tables(from_tables).with_sql("""ALTER TABLE {full_table_name} SET TBLPROPERTIES (
  delta.enableDeletionVectors = true,
  delta.enableRowTracking = true,
  delta.enableChangeDataFeed = true,
  delta.deletedFileRetentionDuration = '30 day',
  delta.logRetentionDuration = '30 day',
  delta.autoOptimize.optimizeWrite = true)""").apply()