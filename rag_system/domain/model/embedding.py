from dataclasses import dataclass


@dataclass(frozen=True)
class Embedding:
    vector: list[float]
    model: str
    dimensions: int

    def __post_init__(self) -> None:
        if self.dimensions <= 0:
            raise ValueError("dimensions must be positive")
        if len(self.vector) != self.dimensions:
            raise ValueError(
                f"vector length ({len(self.vector)}) does not match dimensions ({self.dimensions})"
            )
