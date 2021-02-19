import unittest

class MyTest(unittest.TestCase):

  def test_pass(self):
      pass

  def test_fail(self):
      call_method_that_does_not_exist()

if __name__ == '__main__':
unittest.main()
