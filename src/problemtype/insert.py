from sqltools import check_valid_query
from errors import DatabaseError
from types import ProblemType, SuccessType

class Insert(ProblemType):
  """
  Class: Insert
  -------------
  Tests an insert statement and sees if the student's query produces the
  same diff as the solution query. Does this using transactions to ensure the
  database is not modified incorrectly.
  """
  def grade_test(self, test, output):
    # Get the state of the table before the insert.
    table_sql = "SELECT * FROM " + test["table"]
    before = self.db.execute_sql(table_sql)

    # Make sure the student did not submit a malicious query.
    if not check_valid_query(self.response.sql, "insert"):
      # TODO output something that says they attempted somethign OTHER than insert
      return test["points"]

    # If this is a self-contained DELETE test (Which means it will occur within
    # a transaction and rolled back aftewards).
    if test.get("rollback"):
      self.db.start_transaction()

    # Create a savepoint and run the student's insert statement.
    exception = None
    self.db.savepoint('spt_insert')
    try:
      self.db.execute_sql(self.response.sql, setup=test.get("setup"), \
                          teardown=test.get("teardown"))
      actual = self.db.execute_sql(table_sql)
    except DatabaseError as e:
      exception = e
    finally:
      self.db.rollback('spt_insert')
      # Make sure the rollback occurred properly.
      assert(len(before.results) == len(self.db.execute_sql(table_sql).results))

    # Run the solution insert statement.
    self.db.execute_sql(test["query"], setup=test.get("setup"), \
                     teardown=test.get("teardown"))
    expected = self.db.execute_sql(table_sql)

    # A self-contained INSERT. Make sure the rollback occurred properly.
    if test.get("rollback"):
      self.db.rollback()
      assert(len(before.results) == len(self.db.execute_sql(table_sql).results))

    # Otherwise, release the savepoint.
    else:
      self.db.release('spt_insert')

    # Raise the exception if it occurred.
    if exception: raise exception

    # Compare the results of the test insert versus the actual. If the results
    # are not equal in size, then it is automatically wrong. If the results are
    # not the same, then they are also wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      output["expected"] = expected.subtract(before).output
      output["actual"] = actual.subtract(before).output
      return test["points"]

    # Otherwise, their insert statement is correct.
    output["success"] = SuccessType.SUCCESS
    return 0


  def output_test(self, o, test, specs):
    # Don't output anything if they are successful.
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    self.generate_diffs(test["expected"].split("\n"), \
                        test["actual"].split("\n"), o)
    o.write("</pre>")
