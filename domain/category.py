from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip() if isinstance(self.name, str) else ""
        if not name:
            raise ValueError("Category name cannot be empty.")
        object.__setattr__(self, "name", name)
