from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, final

T = TypeVar("T")
E = TypeVar("E")

@final
@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    value: T

@final
@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    error: E

type Result[T, E] = Ok[T] | Err[E]

TOut = TypeVar("TOut")

def map_result(func: Callable[[T], TOut], result: Result[T, E]) -> Result[TOut, E]:
    match result:
        case Ok(v):
            return Ok(func(v))
        case Err():
            return result

def bind_result(func: Callable[[T], Result[TOut, E]], result: Result[T, E]) -> Result[TOut, E]:
    match result:
        case Ok(v):
            return func(v)
        case Err():
            return result

def bind_result_partial(func: Callable[[T], Result[TOut, E]]) -> Callable[[Result[T, E]], Result[TOut, E]]:
    return lambda x: bind_result(func, x)