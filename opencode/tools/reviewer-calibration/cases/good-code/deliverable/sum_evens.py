def sum_even_numbers(numbers):
    """Sum of even numbers in a list.

    Args:
        numbers: list of integers.

    Returns:
        Sum of even values.
    """
    return sum(n for n in numbers if n % 2 == 0)
