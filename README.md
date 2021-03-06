CS 121 Automation Tool
======================

Libraries
---------
The following tools and libraries must be installed prior to running the tool.
* [Python 2.7.6](https://www.python.org/download/)
* [Python MySQL Connector 1.2.3](http://dev.mysql.com/downloads/connector/python/)
* [prettytable](https://code.google.com/p/prettytable/)


Config File
-----------
The configuration file can be found in `src/CONFIG.py`. Nothing needs to be
changed unless verbose output is desired or the directories to save things
in needs to be changed. However, the values in `src/secret.py` _do_ need
to be changed but should _**not**_ be committed to the repository!


Directory Structure
-------------------
The directory structure of the automation tool is as follows. All files for a
particular assignment should be in the corresponding folder (for example, the
`cs121hw2/` folder listed below).

    |-- assignments/
        |-- cs121hw2/
            |-- students/
                |-- agong-cs121hw2/
                |-- mqian-cs121hw2/
                    |-- file1.sql
                    |-- file2.sql
            |-- cs121hw2.spec
            |-- make-banking.sql
            |-- make-library.sql
            |-- make-university.sql
        |-- cs121hw3/
    |-- src/
        |-- *.py
    |-- style/

The specifications for the assignment must be in a file called
`<assignment name>.spec`. Each student's submission should be in a separate
folder of the form `<username>-<assignment name>`. Any dependent SQL files
should be in the assignment's base directory.

After the repository is cloned, it should have the directory structure
detailed above, except the `assignments` folder needs to be filled in with
the correct specs and student files!

Usage
-----

    python main.py --assignment <assignment name>
                   [--files <files to grade>]
                   [--students <students to grade>]
                   [--exclude <list of students to skip>]
                   [--after <grade files submitted after YYYY-MM-DD>]
                   [--user <database username>]
                   [--db <database to use for grading>]
                   [--deps]
                   [--purge]
                   [--raw]
                   [--hide]

Use `--purge` if the entire database is to be purged prior to grading
(this will drop every table, procedure, function, trigger, etc.). This
should be used between assignments and if there were any errors in grading
prior to this. Generally if there is some problem grading you should run
with the `--purge` flag.

The `--deps` flag is used to run the dependencies for the assignment.
Dependencies are SQL files that create the tables and rows necessary
for testing. They should only be run once per assignment unless `--purge`
is used.

Use `--raw` if the output results should be in raw JSON instead of HTML.

Use `--hide` if generating output for students to use (so solutions and
point values are hidden). Student output can be found in the
`_results/student_output` folder in the respective assignment folder.

Example usage:

    python main.py --assignment cs121hw3 --files queries.sql
                   --students agong mqian

Or:

    python main.py --assignment cs121hw7 --after 2014-03-01

If you wanted to run multiple instances of the grading too, you can do so
by using different users on the same database:

    python main.py --assignment cs121hw8 --db grading_database_1 --user grader1
    python main.py --assignment cs121hw8 --db grading_database_1 --user grader2

Or different databases:

    python_main.py --assignment cs121hw8 --db grading_database_1
    python main.py --assignment cs121hw8 --db grading_database_2

Output
------
Results of the grading run are outputted in the `_results/` folder of the
directory structure:

    |-- assignments/
        |-- cs121hw2/
            |-- _results/
                |-- files
                |-- student_output
                |-- style
                |-- index.html
            |-- students/
            |-- cs121hw2.spec

The output can be viewed in the `index.html` file, which opens up a web view.
The `files` folder contains all the files necessary for this web view, and
`style` contains the Javascript and CSS. The `student_output` folder
contains the files that can be given to the students for them to look at.
