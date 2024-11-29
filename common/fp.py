"""
Some statically-typed functional programming utilities.

See:
- https://earldouglas.com/mypy-lists.html
"""

from functools import reduce
from itertools import chain
from typing import Callable, TypeVar

A = TypeVar("A")
B = TypeVar("B")


def fmap(f: Callable[[A], B], xs: list[A]) -> list[B]:
    return list(map(f, xs))


def flatten(xs: list[list[A]]) -> list[A]:
    return reduce(lambda acc, nested: acc + nested, xs)
    return list(chain.from_iterable(xs))


def flatMap(f: Callable[[A], list[B]], xs: list[A]) -> list[B]:
    return flatten(fmap(f, xs))


def pipe(value: A, *functions: Callable[[A], A]) -> A:
    """
    Pass a value through a series of functions that take one argument of the same type.

    .. code:: python
       >>> # => executes: str(float(int('1')))
       >>> assert flow("1", int, float, str) == "1.0"
    """
    return reduce(lambda acc, f: f(acc), functions, value)
