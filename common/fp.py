"""
Some statically-typed functional programming utilities.

See:
- https://earldouglas.com/mypy-lists.html
"""

from functools import reduce
from typing import Callable, TypeVar

from expression import pipe

from common.logs import log

_A = TypeVar("A")
_B = TypeVar("B")


def fmap(f: Callable[[_A], _B], xs: list[_A]) -> list[_B]:
    return list(map(f, xs))


def flatten(xs: list[list[_A]]) -> list[_A]:
    return reduce(lambda acc, nested: acc + nested, xs)
    # return list(chain.from_iterable(xs))


def flatmap(f: Callable[[_A], list[_B]], xs: list[_A]) -> list[_B]:
    return flatten(fmap(f, xs))


if __name__ == "__main__":
    print(fmap(lambda x: x + 1, [1, 2, 3]))  # => [2, 3, 4]
    print(flatten([[1, 2], [3, 4], [5, 6]]))  # => [1, 2, 3, 4, 5, 6]
    print(flatmap(lambda x: [x, x + 1], [1, 2, 3]))  # => [1, 2, 2, 3, 3, 4]
    result = pipe("1", int, float, str)  # => "1.0"
    print(result)

    pipeline = (int, float, str, float)
    result2 = reduce(lambda acc, f: f(acc), (int, float, str, float), "1")
    result3 = reduce(lambda acc, f: f(acc), pipeline, "1")
    # result4 = flow("1", *pipeline)
    log.debug(f"🔍 result2: {result2}")
    log.debug(f"🔍 type result2: {type(result2)}")
    # log.debug(f"🔍 result4: {result4}")
