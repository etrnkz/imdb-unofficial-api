class ImdbError(Exception):
    """Base exception for all IMDb API errors."""


class ImdbNotFoundError(ImdbError):
    """Raised when a resource is not found (404)."""


class ImdbRateLimitError(ImdbError):
    """Raised when rate-limited (429)."""


class ImdbGraphQLError(ImdbError):
    """Raised when the GraphQL API returns errors."""
