from errors import DatabaseError, QueryError
from sqltools import check_valid_query, find_valid_sql
from types import ProblemType, SuccessType

class Delete(ProblemType):
  """
  Class: Delete
  -------------
  Tests a delete statement to see if the student's query deletes the same rows
  as the solution query. Does this using transactions to ensure the database
  is not modified incorrectly.

  Compares the remaining rows in the tables in order to check if deletion was
  done correctly.
  """

  def grade_test(self, test, output):
    # Get the state of the table before the delete.
    table_sql = "SELECT " + \
                (", ".join(test["columns"]) if test.get("columns") else "*") + \
                " FROM " + test["table"]
    before = self.db.execute_sql(table_sql)
    sql = self.response.sql

    # Make sure the student did not submit a malicious query or malformed query.
    if not check_valid_query(sql, "delete"):
      output["deductions"].append(QueryError.BAD_QUERY)
      sql = find_valid_sql(sql, "delete")
      if sql is None:
        return test["points"]

    # Start a transaction in order to rollback if this is a self-contained
    # DELETE test.
    self.db.start_transaction()

    # Create a savepoint and run the student's delete statement.
    exception = None
    self.db.savepoint('spt_delete')
    try:
      self.db.execute_sql(sql)
      actual = self.db.execute_sql(table_sql)
    except DatabaseError as e:
      exception = e
    finally:
      self.db.rollback('spt_delete')
      # Make sure the rollback occurred properly.
      assert len(before.results) == len(self.db.execute_sql(table_sql).results)

    # Run the solution delete statement.
    self.db.execute_sql(test["query"])
    expected = self.db.execute_sql(table_sql)

    # A self-contained DELETE. Make sure the rollback occurred properly.
    if test.get("rollback"):
      self.db.rollback()
      assert len(before.results) == len(self.db.execute_sql(table_sql).results)

    # Otherwise, release the savepoint.
    else:
      self.db.release('spt_delete')
      self.db.commit()

    # Raise the exception if it occurred.
    if exception:
      raise exception

    # Compare the remaining expected rows versus the actual. If the results are
    # not the same, then they are wrong.
    if not self.equals(expected, actual):
      output["expected"] = before.subtract(expected).output
      output["actual"] = before.subtract(actual).output
      return test["points"]

    # Otherwise, their delete statement is correct.
    output["success"] = SuccessType.SUCCESS
    return 0


  def output_test(self, o, test, specs):
    # Don't output anything if they are successful.
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    self.generate_diffs(test["expected"].split("\n"),
                        test["actual"].split("\n"),
                        o)
    o.write("</pre>")
