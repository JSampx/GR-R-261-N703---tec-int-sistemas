"""
Módulo de Cache simples em memória com suporte a TTL (Time To Live).
Fornece cache para respostas de APIs externas.
"""

import time
from typing import Any, Dict, Optional


class CacheEntry:
    """Representa um item no cache com TTL."""
    
    def __init__(self, value: Any, ttl: int):
        """
        Inicializa um item de cache.
        
        Args:
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos
        """
        self.value = value
        self.ttl = ttl
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """Verifica se o item expirou."""
        return (time.time() - self.created_at) > self.ttl


class SimpleCache:
    """Cache em memória simples com suporte a TTL."""
    
    def __init__(self):
        """Inicializa o cache."""
        self._cache: Dict[str, CacheEntry] = {}
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave de cache
            value: Valor a armazenar
            ttl: Tempo de vida em segundos (padrão: 1 hora)
        """
        self._cache[key] = CacheEntry(value, ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um valor do cache.
        
        Args:
            key: Chave de cache
        
        Returns:
            Optional[Any]: Valor armazenado ou None se não encontrado/expirado
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.value
    
    def delete(self, key: str) -> None:
        """
        Remove um item do cache.
        
        Args:
            key: Chave de cache
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove itens expirados do cache."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]


# Instância global de cache
_cache_instance = SimpleCache()


def get_cache() -> SimpleCache:
    """Retorna a instância global de cache."""
    return _cache_instance
