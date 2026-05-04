import hashlib
import json


class CacheUtils:
    """Utility class for cache key computation and hashing."""

    @classmethod
    def compute_hash(
        cls, content: bytes | str | dict, algorithm: str = "blake2b"
    ) -> str:
        """
        Compute hash of content using specified algorithm.

        Args:
            content: Content to hash (bytes, string, or dictionary)
            algorithm: Hashing algorithm to use (default: blake2b)

        Returns:
            Hexadecimal hash string
        """
        if isinstance(content, dict):
            # Convert dict to deterministic JSON string
            content = json.dumps(content, sort_keys=True)

        if isinstance(content, str):
            content = content.encode()

        hash_func = getattr(hashlib, algorithm)
        return hash_func(content).hexdigest()

    @classmethod
    def compute_cache_key(
        cls,
        prefix: str,
        content: bytes | str | dict,
        additional_context: str = "",
        algorithm: str = "blake2b",
    ) -> str:
        """
        Compute cache key combining prefix, content hash, and optional context.

        Args:
            prefix: Prefix for the cache key (e.g., 'ocr', 'extraction', provider name)
            content: Content to hash (bytes, string, or dictionary)
            additional_context: Optional additional context to include in key
            algorithm: Hashing algorithm to use (default: blake2b)

        Returns:
            Cache key string in format: prefix_hash or prefix_hash_context
        """
        content_hash = cls.compute_hash(content, algorithm)
        key_parts = [prefix, content_hash]

        if additional_context:
            context_hash = cls.compute_hash(additional_context, algorithm)[:8]
            key_parts.append(context_hash)

        return "_".join(key_parts)
