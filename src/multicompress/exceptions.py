class MultiCompressError(Exception):
    """Base exception for the application."""


class FileOperationError(MultiCompressError):
    """Raised when file operations fail."""


class CompressionError(MultiCompressError):
    """Raised when compression fails."""


class DecompressionError(MultiCompressError):
    """Raised when decompression fails."""


class ValidationError(MultiCompressError):
    """Raised when input validation fails."""


class MissingDependencyError(MultiCompressError):
    """Raised when an optional external dependency is missing."""


class ArchiveError(MultiCompressError):
    """Raised when archive integrity or extraction fails."""
