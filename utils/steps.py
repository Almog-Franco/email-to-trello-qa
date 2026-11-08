class BaseStep(object):
    def __init__(self, description):
        self.description = description

    def __enter__(self):
        print(f"  → {self.__class__.__name__}: {self.description}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print(f"  ✓ {self.__class__.__name__} completed")
        return False  # Don't suppress exceptions


class Prepare(BaseStep):
    pass


class Action(BaseStep):
    pass


class Verify(BaseStep):
    pass
