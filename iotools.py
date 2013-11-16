"""
Module: iotools
---------------
Functions involving input and output into the system, as well as file-related
functions.
"""

import json
import os
from response import Response

def format_lines(sep, lines):
  """
  Function: format_lines
  ----------------------
  Format lines in a nice way. Gets rid of extra spacing.

  lines: The lines to print and format.
  """
  return "\n" + sep + " " + ("\n" + sep + " ").join( \
    filter(None, [line.strip() for line in lines.split("\n")])) + "\n"


def get_students(assignment):
  # TODO grade students who'ev submitted after a given time
  """
  Function: get_students
  ----------------------
  Gets all the students for a given assignment.

  assignment: The assignment.
  returns: A list of students who've submitted for that assignment.
  """
  return [f.replace("-" + assignment, "") for f in \
    os.walk(assignment + "/").next()[1] if f.endswith("-" + assignment)]


def parse_file(f):
  """
  Function: parse_file
  --------------------
  Parses the file into a dict of the question number and the student's response
  to that question.

  f: The file object to parse.
  returns: The dict of the question number and student's response.
  """

  # Dictionary containing a mapping from the question number to the response.
  responses = {}
  # The current problem number being parsed.
  current_problem = ""

  for line in f:
    # If this is a blank line, just skip it.
    if len(line.strip()) == 0:
      continue

    # Find the indicator denoting the start of an response.
    elif line.strip().startswith("-- [Problem ") and line.strip().endswith("]"):
      current_problem = line.replace("-- [Problem ", "").replace("]", "")
      current_problem = current_problem.strip()
      # This is a new problem, so create an empty response to with no comments.
      responses[current_problem] = Response()

    # Lines with comments of the form "--".
    elif line.startswith("--"):
      responses[current_problem].comments += \
        line.replace("-- ", "").replace("--", "")

    # Lines with comments of the form /* */.
    # TODO

    # Continuation of a response from a previous line.
    else:
      responses[current_problem].sql += line

  return responses


def parse_specs(assignment):
  """
  Function: parse_specs
  ---------------------
  Parse the specs for a given assignment.

  assignment: The assignment.
  returns: A JSON object containing the specs for that assignment.
  """
  f = open(assignment + "/" + assignment + "." + "spec", "r")
  specs = json.loads("".join(f.readlines()))
  f.close()
  return specs


def write(f, line):
  """
  Function: write
  ---------------
  Writes out a line to a provided file. Adds two newlines since this is in
  markdown.
  """
  f.write(line + "\n\n")
