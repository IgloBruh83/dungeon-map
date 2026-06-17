
from __future__ import annotations
import math
from config import Config as cfg


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"[{self.x}x, {self.y}y]"


    def checkConvergence(self, other: Vector2) -> bool:
        return max(abs(self.x - other.x), abs(self.y - other.y)) < cfg.maxError

    def distance(self, other: Vector2) -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> Vector2:
        _max_abs = max(abs(self.x), abs(self.y))
        if _max_abs == 0:
            return Vector2(0, 0)
        return Vector2(self.x / _max_abs, self.y / _max_abs)

    def lerp(self, other: Vector2, factor: float) -> Vector2:
        _new_x = self.x + (other.x - self.x) * factor
        _new_y = self.y + (other.y - self.y) * factor
        return Vector2(_new_x, _new_y)