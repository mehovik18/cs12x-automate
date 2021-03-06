"""
Module: sqltools
----------------
Contains tools to help with parsing and checking SQL.
"""

import re
from cStringIO import StringIO

from CONFIG import VERBOSE

# Used to find delimiters in the file.
DELIMITER_RE = re.compile(r"^\s*delimiter\s*([^\s]+)\s*$", re.I)

# Dictionary of keywords of the form <start keyword> : <end keyword>. If
# <end keyword> is empty, then this kind of statement ends with a semicolon.
#
# IMPORTANT NOTE:
#   If any of these keyword-specified ranges can overlap, then the one that
#   matches earlier should be specified first!  For example, this is important
#   to properly handle the "WITH" clause on a "SELECT" statement, or the
#   "CREATE VIEW" statement which includes a "SELECT" statement.
#
KEYWORDS_DICT = {
  "ALTER TABLE": "",
  "CALL": "",
  "COMMIT": "",
  "CREATE FUNCTION": "END",
  "CREATE OR REPLACE FUNCTION": "END",
  "CREATE INDEX": "",
  "CREATE OR REPLACE PROCEDURE": "END",
  "CREATE PROCEDURE": "END",

  # "CREATE TABLE" : ");",
  # Must come before SELECT so we can handle "CREATE TABLE t AS SELECT ..."
  "CREATE TABLE" : "",

  "CREATE OR REPLACE TRIGGER": "END",
  "CREATE TRIGGER": "END",
  "CREATE OR REPLACE VIEW": "",

  # Must come before SELECT since views are specified in terms of SELECT.
  "CREATE VIEW": "",
  "DELETE": "",
  "DO": "",
  "DROP FUNCTION": "",
  "DROP INDEX": "",
  "DROP PROCEDURE": "",
  "DROP TABLE": "",
  "DROP TRIGGER": "",
  "DROP VIEW": "",
  "HANDLER": "",
  "INSERT" : "",
  "LOAD DATA": "",
  "RELEASE SAVEPOINT": "",
  "REPLACE": "",
  "ROLLBACK": "",
  "SAVEPOINT": "",

  "WITH": "",   # WITH must come before SELECT
  "SELECT": "",

  "SET": "",
  "START TRANSACTION": "",
  "UPDATE": "",
}
KEYWORDS = KEYWORDS_DICT.keys()

# Control keywords. Used to figure out where a function begins and ends.
CTRL_KEYWORDS = [
  ("CASE", "END CASE"),
  ("IF", "END IF"),
  ("IF(", ")"),
  ("LOOP", "END LOOP"),
  ("WHILE", "END WHILE"),
  ("REPEAT", "END REPEAT"),
  ("BEGIN", "END")
]
CTRL_KEYWORDS_IGNORE = [
  "ELSEIF"
]

# Types of quotes.
QUOTES = ['\'', '\"']

def check_valid_query(query, query_type):
  """
  Function: check_valid_query
  ---------------------------
  Check to see that a query is a valid query (i.e. it is not a malicious query).
  Does this by making sure the query_type is found in the beginning of the query
  and that there are no other SQL statements being run. For example, if the
  query_type is an INSERT statement, makes sure that the 'INSERT' keyword is
  found in the beginning of query.

  This does not work for multi-statement SQL queries, such as CREATE PROCEDURE.

  Obviously this is not perfect and plenty of statements can get through.
  However, it should be sufficient unless there are some very evil students.

  query: The query to check.
  query_type: The query type (e.g. INSERT, DELETE, SELECT).
  returns: True if the query is valid, False otherwise.
  """
  return query_type.upper() in query.upper() and query.count(";") <= 1
  # TODO: This is turned off because students like to put code before their
  #       answer, causing this function to return false negatives. Really,
  #       this function needs to be improved.
  '''
  return (
    # Make sure the query type can be found in the query.
    query.lower().strip().find(query_type.lower()) == 0 and
    # Make sure there is only one SQL statement.
    query.strip().strip().rstrip(";").find(";") == -1
  )
  '''


def find_valid_sql(query, query_type, ignore_irrelevant=False):
  """
  Function: find_valid_sql
  ------------------------
  Finds the valid SQL statement of query_type within a large SQL statement. If
  it cannot be found, return None.

  query: The query to search within.
  query_type: The query type (e.g. INSERT, DELETE, SELECT).
  ignore_irrelevant: True if should ignore non-relevant SQL, False otherwise.
  returns: The query if valid SQL can be found, False otherwise.
  """
  if query.lower().strip().find((query_type + " ").lower()) != -1:
    semicolon_pos = \
      query.strip().find(";", query.lower().find((query_type + " ").lower()))

    # Remove irrelevant SQL if specified.
    #if ignore_irrelevant:
    #  query = query[query.upper().find(query_type.upper() + " "):]
    #  semicolon_pos = \
    #    query.strip().find(";", query.lower().find((query_type + " ").lower()))
    if semicolon_pos == -1:
      return query.strip()
    return query.strip()[0:semicolon_pos]
  else:
    return None


def split(raw_sql):
  """
  Function: split
  ---------------
  Splits SQL into separate statements.
  """

  def find_keyword(sql, keyword, start_idx=0):
    """
    Function: find_keyword
    ----------------------
    Finds a SQL keyword within a statement as long as it is not enclosed
    by quotes.

    sql: The SQL to search within.
    keyword: The keyword to search for.
    start_idx: Where to start searching for the keyword.

    returns: The starting index of the keyword.
    """
    quotes = []
    comment_type = None

    # if VERBOSE:
    #   print("Searching for keyword '%s', starting at index %d" % (keyword, start_idx))

    while True:
      idx = sql.find(keyword, start_idx)
      if idx == -1:
        return -1

      # if VERBOSE:
      #   print("Found keyword '%s' at index %d" % (keyword, idx))

      # Make sure not surrounded by quotes.
      for i in range(start_idx, idx):
        # Make sure this is not a quote within a comment.
        if sql[i:].startswith("/*"):
          comment_type = "block"
          i += 1
        elif comment_type == "block" and sql[i:].startswith("*/"):
          comment_type = None
          i += 1
        elif sql[i:].startswith("--") or sql[i:].startswith("#"):
          comment_type = "single"
          i += 1
        elif comment_type == "single" and sql[i:].startswith("\n"):
          comment_type = None
          i += 1
        elif comment_type is None and sql[i] in QUOTES:
          if len(quotes) > 0 and quotes[-1] == sql[i]:
            quotes.pop()
          else:
            quotes.append(sql[i])

      # If the keyword is "END", make sure it wasn't an END WHILE, END LOOP,
      # END IF, etc. If it is, continue.
      if keyword.lower() == "end":
        result = re.sub(r'\s+', ' ', sql[i:]).strip()
        if not (result.startswith("end;") or
                result.startswith("end ;") or
                result == "end"):
          if idx + 1 < len(sql):
            start_idx = idx + 1
            continue
          else:
            return -1

      # If not surrounded by quotes, then this is the keyword.
      if len(quotes) == 0:
        return idx

      # Otherwise, continue if possible.
      if idx + 1 < len(sql):
        start_idx = idx + 1

      # Could not find keyword.
      else:
        return -1

  def get_start_idx(sql, keyword):
    """
    Function: get_start_idx
    -----------------------
    Checks if this SQL statement starts with this keyword, ignoring comments.
    Returns the starting index of the keyword if found.

    sql: The SQL to search.
    keyword: The keyword to search for.
    returns: The starting index of the keyword if found, -1 otherwise.
    """
    start_idx = 0
    while start_idx < len(sql):
      clean_sql = sql[start_idx:].strip()

      # Ignore comments.
      if clean_sql.startswith("/*"):
        end_idx = sql.find("*/", start_idx)
        # This whole thing must be a comment because can't even find end of it!
        if end_idx == -1:
          return -1
        else:
          start_idx = end_idx + len("*/")
      elif clean_sql.startswith("--") or clean_sql.startswith("#"):
        end_idx = sql.find("\n", start_idx)
        if end_idx == -1:
          return -1
        else:
          start_idx = end_idx + len("\n")

      # Found the keyword.
      elif clean_sql.startswith(keyword):
        return start_idx

      # Could not find the keyword.
      else:
        return -1

    return -1

  sql = raw_sql.strip()
  sql_list = []
  while len(sql) > 0:
    found_sql = False

    # if VERBOSE:
    #   print("Looking for SQL");

    for keyword in KEYWORDS:
      # print("Looking for keyword %s" % keyword)

      start_idx = get_start_idx(sql.lower(), keyword.lower())
      if start_idx != -1:
        keyword_end = KEYWORDS_DICT[keyword] or ";"

        # if VERBOSE:
        #   print("Found keyword '%s' at index %d.  Searching for end-keyword '%s'." % (keyword, start_idx, keyword_end))

        end_idx = find_keyword(sql.lower(), keyword_end.lower(), start_idx)
        end_idx = end_idx + len(keyword_end) if end_idx != -1 else len(sql)
        sql_list.append(sql[0:end_idx])
        sql = sql[end_idx + 1:].strip()

        # if VERBOSE:
        #   print("End-keyword found at index %d.  Remaining SQL is:\n%s" % (end_idx, sql))

        # Remove start and end semicolons.
        while sql.startswith(";") or sql.endswith(";"):
          sql = sql.strip(";").strip()
        found_sql = True
        break

    if not found_sql:
      break

  return sql_list


def parse_create(sql):
  """
  Function: parse_create
  ----------------------
  Parses a CREATE TABLE statement and only runs those (instead of random INSERT
  statements that students should not be including).

  full_sql: The statement to parse.
  returns: Only the CREATE TABLE statement(s).
  """
  sql_lines = []
  started_table = False
  for line in remove_comments(sql).split("\n"):
    if "CREATE TABLE" in line.upper():
      line = line[line.upper().index("CREATE TABLE"):]
      started_table = True
    end_create = re.search(r"\)\s*;", line)
    if end_create and started_table:
      line = line[:line.find(end_create.group()) + len(end_create.group())]
      sql_lines.append(line)
      started_table = False
    if started_table:
      sql_lines.append(line)
    else:
      continue
  return "\n".join(sql_lines)


def parse_func_and_proc(full_sql, is_procedure=False):
  """
  Function: parse_func_and_proc
  -----------------------------
  Parses functions and procedures such that only the CREATE statement is
  extracted (no unnecessary or random SELECT statements, for example).

  full_sql: The statement to parse.
  is_procedure: True if this is for a procedure, False if for a function.
  returns: Only the function or procedure statement.
  """
  sql_lines = []
  stack = []

  # Make sure this is actually a CREATE PROCEDURE or CREATE FUNCTION statement
  # by seeing if the SQL starts with the proper CREATE statement.
  check_keyword = "CREATE PROCEDURE" if is_procedure else "CREATE FUNCTION"
  check_or_keyword = "CREATE OR REPLACE PROCEDURE" \
                     if is_procedure else "CREATE OR REPLACE FUNCTION"
  if check_keyword in full_sql.upper() and "BEGIN" in full_sql.upper():
    sql_lines.append(full_sql[
      full_sql.upper().index(check_keyword):
      full_sql.upper().index("BEGIN")])
    sql = full_sql[full_sql.upper().index("BEGIN"):].strip()
  elif check_or_keyword in full_sql.upper() and "BEGIN" in full_sql.upper():
    sql_lines.append(full_sql[
      full_sql.upper().index(check_or_keyword):
      full_sql.upper().index("BEGIN")])
  else:
    raise Exception

  # Go through each line.
  for line in remove_comments(sql).split("\n"):
    # TODO go through firs tword, then first and second word, etc.
    # once you find a keyword, look start from there and look at the first word, etc.
    # TODO problem if open and close at the same line
    for (open, close) in CTRL_KEYWORDS:
      # A close "parenthesis".
      if re.search('(\\W|^)%s(\\W|$)' % close, line, re.IGNORECASE):
        to_pop = stack[-1]
        if to_pop != open:
          raise Exception
        stack.pop()
        break

      # An open "parenthesis".
      elif re.search('(\\W|^)%s(\\W|$)' % open, line, re.IGNORECASE):
        stack.append(open)
        break
    sql_lines.append(line + "\n")

    # If there are no more open "parenthesis", then we have reached the end of
    # the procedure or function.
    if not stack:
      break

  # If they are unbalanced at this point, the function or procedure definition
  # was never terminated.
  if stack:
    raise Exception
  return "".join(sql_lines)


def preprocess_sql(sql_file):
  """
  Function: preprocess_sql
  ------------------------
  Preprocess the SQL in order to handle the DELIMITER statements.

  sql_file: The SQL file to preprocess.
  returns: The newly-processed SQL stringL.
  """
  lines = StringIO()
  delimiter = ';'
  for line in sql_file:
    # See if there is a new delimiter.
    match = re.match(DELIMITER_RE, line)
    if match:
      # if VERBOSE:
      #   print("preprocess_sql():  Matched DELIMITER spec line:  %s" % line)
      delimiter = match.group(1)
      continue

    # If we've reached the end of a statement.
    if line.strip().endswith(delimiter):
      line = line.replace(delimiter, ";")
    lines.write(line)
    # if VERBOSE:
    #   print("Appended line to lines:  %s" % line)

  return lines.getvalue()


def remove_comments(in_sql):
  """
  Function: remove_comments
  -------------------------
  Removes comments from SQL.
  """
  sql = []
  in_block_comment = False
  for line in in_sql.split("\n"):
    if "/*" in line and not in_block_comment:
      line = line[0:line.index("/*")]
      in_block_comment = True
    if in_block_comment and "*/" in line:
      line = line[line.index("*/") + 2:]
      in_block_comment = False
    if "--" in line:
      line = line[0:line.index("--")]
    elif in_block_comment:
      continue
    sql.append(line)
  return "\n".join(sql)
