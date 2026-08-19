import sys
from sum_evens import sum_even_numbers

assert sum_even_numbers([1, 2, 3, 4]) == 6
assert sum_even_numbers([2]) == 2
assert sum_even_numbers([]) == 0
assert sum_even_numbers([1, 3, 5]) == 0
print("OK")
sys.exit(0)
