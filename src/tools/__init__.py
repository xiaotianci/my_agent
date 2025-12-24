# tools/__init__.py
"""
工具系统 - 提供Agent调用外部能力的统一接口
"""
from .registry import ToolRegistry, BaseTool
from .web_tools import *
from .data_tools import *
from .custom_tools import *

__all__ = [
    'ToolRegistry', 'BaseTool',
    'WebSearchTool', 'CalculatorTool',
    'FileReaderTool', 'CustomTool'
]