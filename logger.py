"""
日志配置模块
提供统一的日志配置和管理
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    log_to_file: bool = True,
    log_to_console: bool = True
) -> logging.Logger:
    """
    配置并返回根日志器
    
    Args:
        log_level: 日志级别
        log_dir: 日志文件目录
        log_to_file: 是否输出到文件
        log_to_console: 是否输出到控制台
    
    Returns:
        配置好的根日志器
    """
    # 创建日志目录
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
    
    # 获取根日志器
    logger = logging.getLogger()
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 日志格式
    console_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_to_file:
        # 主日志文件
        log_file = Path(log_dir) / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # 错误日志文件（单独记录错误）
        error_log_file = Path(log_dir) / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(
            error_log_file,
            encoding='utf-8',
            mode='a'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称（通常使用 __name__）
    
    Returns:
        日志器实例
    """
    return logging.getLogger(name)


class LoggerContext:
    """
    日志上下文管理器
    用于临时修改日志级别
    """
    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.level = getattr(logging, level.upper())
        self.original_level = logger.level
    
    def __enter__(self):
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


# 初始化日志系统
try:
    from config import settings
    root_logger = setup_logger(
        log_level=settings.LOG_LEVEL,
        log_dir=settings.LOG_DIR
    )
except Exception:
    # 如果配置加载失败，使用默认配置
    root_logger = setup_logger()
