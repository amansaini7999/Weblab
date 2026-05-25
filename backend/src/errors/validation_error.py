class ValidationError(ValueError):
    def __init__(self, errors):
        super().__init__("validation failed")
        self.errors = errors
