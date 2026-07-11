class ExecutorError(RuntimeError):
    """Base exception raised by an automation executor."""


class InvalidKeyError(ExecutorError):
    """Raised when a keyboard key is not allowed."""


class ExecutorDisabledError(ExecutorError):
    """Raised when a real executor is disabled."""