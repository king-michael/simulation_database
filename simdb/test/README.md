# Test folder
Some tests using `pytest` to check the integrity of new implementations.

# HowTo
Tests are placed in files beginning with `test_`.

Create in the `test_*.py` file a function starting with
`test_` followed by a descriptive name what is tested.
Do what every you want to test in the function and use `assert`
to make sure the testing is successful.

For complexer testing cases where a more complex assert logic is needed
place it in `helperfunctions.py` if you want to reuse it.
For `numpy.ndarray` testing use `np.testing.assert_*` to test multidimensional arrays.

If the test needs additional data use:
`setup_module()` to create data before the testing
and `teardown_module()` to delete it after testing.
This is particular useful if you want to connect or
create a database in advance disconnect / delete it later on.


# Normal scripts

* `helperfunctions.py` <br>
    Various functions needed for testing

# Tests
## General Tests

* `test_helperfunctions.py` <br>
    Tests for the helper functions used during testing

## DatabaseAPI Tests

* `test_databaseAPI_keywords.py` <br>
    Tests for API functions around `Keywords`


