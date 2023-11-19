import random
from typing import Self, Iterable, Sequence, TypeVar, Any

from abc import ABC, abstractmethod

_T = TypeVar("_T")


class RNG(ABC):
    def __init__(self, seed, *args, **kwargs):
        pass

    @abstractmethod
    def get(self) -> int:
        pass

    @abstractmethod
    def __iter__(self) -> Self:
        pass

    @abstractmethod
    def __next__(self) -> int:
        pass


class PyRNG(RNG):
    def __init__(self, seed: int, max=255, min=-255):
        self.rng = random.Random(seed)
        self.min = min
        self.max = max

    def get(self):
        return self.rng.randint(self.min, self.max)

    def __iter__(self):
        return self

    def __next__(self):
        return self.get()


class Mask(ABC):
    @abstractmethod
    def mask(self, data: _T) -> _T:
        pass


class XORMask(Mask):
    def __init__(self, generator: Iterable):
        self.generator = iter(generator)

    def mask(self, data: bytes):
        sequence: list[int] = []
        for byte in data:
            sequence.append(byte ^ next(self.generator) & 255)

        return bytes(sequence)


class Crypto(ABC):
    @abstractmethod
    def encrypt(self, data: bytes) -> Any:
        pass

    @abstractmethod
    def decrypt(self, data: Any) -> bytes:
        pass


class RNGCrypto(Crypto):
    def __init__(self, seed: int):
        self.mask = XORMask(PyRNG(seed))

    def encrypt(self, data: bytes):
        return self.mask.mask(data)

    def decrypt(self, data: bytes):
        return self.encrypt(data)
