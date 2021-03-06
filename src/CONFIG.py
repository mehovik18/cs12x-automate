"""
Module: CONFIG
--------------
Contains configuration parameters for the grading tool.
"""
import secret

# Verbose output. Set to True for all logging statements.
VERBOSE = True

# Error output. Set to True for only error messages (if VERBOSE is False)
ERROR = True

# ----------------------------- Database Details ----------------------------- #

# The first 3 fields must be modified in the secret.py file.

# Database login information. Must be a dictionary with the username as the
# key and the password as the value.
LOGIN = secret.LOGIN

# Database host.
HOST = secret.HOST

# Database port.
PORT = secret.PORT

# Default database connection timeout (in seconds).
CONNECTION_TIMEOUT = 30

# Maximum timeout for any query.
MAX_TIMEOUT = 600

# ------------------------------ Grading Config ------------------------------ #

# Directory where all the assignment specs and student files are stored.
ASSIGNMENT_DIR = "../assignments/"

# Directory where results an assignment are stored.
RESULT_DIR = "_results/"

# Directory within ASSIGNMENT_DIR where the student files are stored.
STUDENT_DIR = "students/"

# Directory where the stylesheet and Javascripts are.
STYLE_DIR = "../style/"
STYLE_DIR_BASE = "style/"

# Directory where the output files are stored.
FILE_DIR = "files/"

# MathJax library.
MATH_JAX = "http://cdn.mathjax.org/mathjax/latest/MathJax.js?" + \
           "config=TeX-AMS-MML_HTMLorMML"

# Directory where the output files for the students are stored.
STUDENT_OUTPUT_DIR = "student_output/"

# Maximum number of results to print out.
MAX_NUM_RESULTS = 50

# The number of decimal places to compare results with.
PRECISION = 2
