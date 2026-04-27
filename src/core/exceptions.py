class AppError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

class RangeValidationError(AppError):
    def __init__(self, message: str = "Values out of biological range [0.1 - 15.0 cm]."):
        super().__init__("ERR_01", message)

class NullInputError(AppError):
    def __init__(self, message: str = "Null or NaN values detected in input."):
        super().__init__("ERR_04", message)

class LogicConsistencyError(AppError):
    def __init__(self, message: str = "Biological logic consistency failed."):
        super().__init__("ERR_05", message)

class SchemaValidationError(AppError):
    def __init__(self, message: str = "Strict payload and typing validation failed."):
        super().__init__("ERR_07", message)

class StatisticalDriftWarning(Warning):
    """Warning disparado cuando se detecta deriva estadística (ERR_06)."""
    def __init__(self, message: str = "[ERR_06] Statistical drift detected (Z-score > 3)."):
        self.message = message
        super().__init__(self.message)
