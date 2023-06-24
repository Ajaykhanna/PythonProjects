# Mastering Exception Handling in Python: Basics to Mastery

# Ground Level
try:
    # Code that may raise an exception
    x = 5 / 0
except:
    # Code to handle the exception
    print("An error occurred")

# Specific Type of Exceptions
try:
    x = int("foo")
except ZeroDivisionError:
    print("You can't divide a number by zero!")
except:
    print("Unknown error occurred")

# Detailing The Exception
try:
    x = int("foo")
except ZeroDivisionError:
    print("You can't divide a number by zero!")
except Exception as e:
    print("An Error occurred:", e)

# Level - 1
# Function with exception handling
def divide(x, y):
    return x / y

def calculate(a, b):
    try:
        result = divide(a, b)
        print("Result:", result)
    except ZeroDivisionError:
        print("You can't divide a number by zero!")

calculate(10, 0)

# The Finally Block: Let it through
try:
    x = 5 / 1
except ZeroDivisionError:
    print("You can't divide a number by zero!")
finally:
    print("Calculation finished")

# Raise an Exception Deliberatively
def calculate(a, b):
    try:
        raise Exception("I just want to raise an exception!")
    except Exception as e:
        print(e)

calculate(10, 0)

# The Else Block
try:
    x = 5 / 1
except ZeroDivisionError:
    print("You can't divide a number by zero!")
else:
    print("The result is: ", x)
finally:
    print("Calculation finished")

# Level-2
# The Warning Module
import warnings

def calculate(x, y):
    try:
        result = x / y
    except ZeroDivisionError:
        print("You can't divide a number by zero!")
    else:
        if x == result:
            warnings.warn("All numbers divide by 1 will remain the same.")
        print("Result: ", result)

calculate(10, 1)

# Assertion — Another Way of Raising an Exception
def calculate(x, y):
    assert y != 0, "You can't divide a number by zero!"
    result = x / y
    print("Result: ", result)

calculate(10, 0)

# Custom Exception Type
class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"A customized exception has occurred: {self.args[0]}"

raise CustomException("This is a custom exception")

# Level-3
# The Suppress Module
from contextlib import suppress

nums = [3, -1, -2, 1, 1, 0, 3, 1, -2, 1, 0, -1, -1, -1, 3, -2, -1, 3, '3', -1] 

result = 0
for num in nums:
    with suppress(ZeroDivisionError, TypeError):
        result += 1/num
