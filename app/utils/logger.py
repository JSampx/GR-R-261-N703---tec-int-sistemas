"""
Sistema de logging estruturado da aplicação.
Fornece funções para logging consistente em todo o projeto.
"""

import logging
import os
from typing import Any, Dict


class StructuredLogger:
    """Logger estruturado que adiciona contexto aos logs."""
    
    def __init__(self, name: str):
        """
        Inicializa o logger estruturado.
        
        Args:
            name: Nome do logger (geralmente __name__)
        """
        self.logger = logging.getLogger(name)
        self._setup_handler()
    
    def _setup_handler(self):
        """Configura o handler do logger."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # Configurar nível de log
            log_level = os.getenv("LOG_LEVEL", "INFO")
            self.logger.setLevel(log_level)
    
    def debug(self, message: str, **context: Any) -> None:
        """Log de debug."""
        self.logger.debug(self._format_message(message, context))
    
    def info(self, message: str, **context: Any) -> None:
        """Log de informação."""
        self.logger.info(self._format_message(message, context))
    
    def warning(self, message: str, **context: Any) -> None:
        """Log de aviso."""
        self.logger.warning(self._format_message(message, context))
    
    def error(self, message: str, **context: Any) -> None:
        """Log de erro."""
        self.logger.error(self._format_message(message, context))
    
    def critical(self, message: str, **context: Any) -> None:
        """Log crítico."""
        self.logger.critical(self._format_message(message, context))
    
    @staticmethod
    def _format_message(message: str, context: Dict[str, Any]) -> str:
        """Formata mensagem de log com contexto."""
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            return f"{message} | {context_str}"
        return message


# Função auxiliar para obter logger
def get_logger(name: str) -> StructuredLogger:
    """
    Retorna uma instância de StructuredLogger.
    
    Args:
        name: Nome do logger (geralmente __name__)
    
    Returns:
        StructuredLogger: Instância do logger estruturado
    """
    return StructuredLogger(name)
