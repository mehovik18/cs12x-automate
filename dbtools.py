"""
Module: dbtools
---------------
Contains helper methods involving the database and queries.
"""

import codecs
from CONFIG import *
import mysql.connector
import sqlparse
import subprocess
import prettytable
from models import Result

def source_files(assignment, files, cursor):
  """
  Function: source_files
  ----------------------
  Sources files into the database. Since the "source" command is for the
  MySQL command-line interface, we have to parse the source file and run
  each command one at a time.

  assignment: The assignment name. Is prepended to all the files.
  files: The source files to source.
  cursor: The database cursor.
  """

  if len(files) == 0:
    return

  # Loop through each source file.
  for source in files:
    # If the source is a SQL file, run it.
    if source.find(".sql") != -1:
      f = codecs.open(assignment + "/" + source, "r", "utf-8")
      sql_list = sqlparse.split(f.read())
      for sql in sql_list:
        if len(sql.strip()) == 0:
          continue
        cursor.execute(sql)
      f.close()


def import_files(assignment, files):
  """
  Function: import_files
  ----------------------
  Imports raw data files into the database. This uses the "mysqlimport"
  command on the terminal. We will have to invoke the command via python.

  assignment: The assignment name. Is prepended to all the files.
  files: The files to import.
  """
  if len(files) == 0:
    return

  print "\nImporting files..."
  # Import all the data files.
  files = " ".join([assignment + "/" + f for f in files])
  subprocess.call("mysqlimport -h " + HOST + " -P " + PORT + " -u " + USER + \
    " -p" + PASS + " --delete --local " + DATABASE + " " + files)


def get_schema(cursor):
  """
  Function: get_schema
  --------------------
  Gets the schema of the result. Returns a list of tuples, where each tuple is
  of the form (column_name, type, None, None, None, None, null_ok, flags).

  cursor: The database cursor.
  returns: A list of tuples representing the schema.
  """
  return cursor.description


def get_column_names(cursor):
  """
  Function: get_column_names
  --------------------------
  Gets the column names of the results.
  """
  return [col[0] for col in cursor.description]


def run_query(setup, query, cursor):
  """
  Function: run_query
  -------------------
  Runs a query and does all the setup and teardown required for the query.

  setup: A JSON object containing the setup for the query.
  query: The query to run.
  cursor: The database cursor.

  returns: A Result object containing the result, the schema of the results and
           pretty-printed output.
  """
  # Source files to insert data needed for the query.
  if "source" in setup:
    source_files(setup["source"], cursor)

  # Query setup.
  if "setup" in setup:
    cursor.execute(setup["setup"], multi=True)
  cursor.execute(query)

  # Get the query results and schema.
  result = Result()
  result.results = [row for row in cursor]
  result.schema = get_schema(cursor)
  result.col_names = get_column_names(cursor)

  # Truncate the output if it is too long.
  output_results = result.results
  # TODO no longer truncate
  #if len(output_results) > 15:
  #  output_results = result.results[0:7]
  #  filler = ("   ...  ", ) * len(output_results[0])
  #  output_results += [filler] + result.results[-7:]

  # Pretty-print output.
  output = prettytable.PrettyTable(get_column_names(cursor))
  output.align = "l"
  for row in output_results:
    output.add_row(row)
  result.output = output.get_string()

  # Query teardown.
  if "teardown" in setup:
    cursor.execute(setup["teardown"], multi=True)
  return result
