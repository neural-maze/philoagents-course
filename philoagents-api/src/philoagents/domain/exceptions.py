class PhilosopherNameNotFound(Exception):
    """Exception raised when a philosopher's name is not found."""

    def __init__(self, philosopher_id: str):
        self.message = f"Philosopher name for {philosopher_id} not found."
        super().__init__(self.message)


class PhilosopherPerspectiveNotFound(Exception):
    """Exception raised when a philosopher's perspective is not found."""

    def __init__(self, philosopher_id: str):
        self.message = f"Philosopher perspective for {philosopher_id} not found."
        super().__init__(self.message)


class PhilosopherStyleNotFound(Exception):
    """Exception raised when a philosopher's style is not found."""

    def __init__(self, philosopher_id: str):
        self.message = f"Philosopher style for {philosopher_id} not found."
        super().__init__(self.message)


class PhilosopherContextNotFound(Exception):
    """Exception raised when a philosopher's context is not found."""

    def __init__(self, philosopher_id: str):
        self.message = f"Philosopher context for {philosopher_id} not found."
        super().__init__(self.message)
