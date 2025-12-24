# 工具注册与管理

# tools/registry.py
"""
工具注册与管理中心
"""
from typing import Dict, List, Any, Callable, Optional
from pydantic import BaseModel, Field
from functools import wraps
import inspect
import hashlib
import json

class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None

class ToolMetadata(BaseModel):
    """工具元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "System"
    category: str = "general"
    parameters: List[ToolParameter]
    returns: str
    timeout: int = 30  # 超时时间(秒)
    requires_auth: bool = False

class BaseTool:
    """工具基类 - 所有工具应继承此类"""
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self._call_count = 0
        self._error_count = 0
    
    def validate_parameters(self, **kwargs) -> bool:
        """验证参数"""
        for param in self.metadata.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"缺少必需参数: {param.name}")
            if param.name in kwargs:
                # 简单类型检查
                expected_type = param.type.lower()
                actual_value = kwargs[param.name]
                
                type_checks = {
                    "string": lambda x: isinstance(x, str),
                    "integer": lambda x: isinstance(x, int),
                    "number": lambda x: isinstance(x, (int, float)),
                    "boolean": lambda x: isinstance(x, bool),
                    "object": lambda x: isinstance(x, dict),
                    "array": lambda x: isinstance(x, list)
                }
                
                if expected_type in type_checks:
                    if not type_checks[expected_type](actual_value):
                        raise TypeError(
                            f"参数 {param.name} 类型错误: "
                            f"期望 {expected_type}, 实际 {type(actual_value).__name__}"
                        )
        return True
    
    async def execute(self, **kwargs) -> Any:
        """执行工具 - 子类必须实现此方法"""
        raise NotImplementedError("子类必须实现 execute 方法")
    
    async def safe_execute(self, **kwargs) -> dict:
        """安全执行工具，包含错误处理"""
        self._call_count += 1
        
        try:
            # 验证参数
            self.validate_parameters(**kwargs)
            
            # 执行工具
            result = await self.execute(**kwargs)
            
            return {
                "success": True,
                "result": result,
                "tool": self.metadata.name,
                "execution_time": None  # 实际应计算执行时间
            }
        except Exception as e:
            self._error_count += 1
            return {
                "success": False,
                "error": str(e),
                "tool": self.metadata.name,
                "traceback": None  # 生产环境可记录详细堆栈
            }
    
    def get_stats(self) -> dict:
        """获取工具统计信息"""
        return {
            "call_count": self._call_count,
            "error_count": self._error_count,
            "success_rate": (
                1 - (self._error_count / self._call_count) 
                if self._call_count > 0 else 1.0
            )
        }

def tool_decorator(name: str = None, description: str = None):
    """工具装饰器 - 将普通函数转换为工具"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        async def async_wrapper(*args, **kwargs):
            print("async_wrapper 执行...")
            return await func(*args, **kwargs)

        # 从函数签名提取元数据
        sig = inspect.signature(func)
        parameters = []
        
        for param_name, param in sig.parameters.items():
            param_type = "string"  # 默认类型
            
            if param.annotation != inspect.Parameter.empty:
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    dict: "object",
                    list: "array"
                }
                param_type = type_map.get(param.annotation, "string")
            
            parameters.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=f"参数 {param_name}",
                required=param.default == inspect.Parameter.empty,
                default=param.default if param.default != inspect.Parameter.empty else None
            ))
        
        wrapper.metadata = ToolMetadata(
            name=name or func.__name__,
            description=description or func.__doc__ or "无描述",
            parameters=parameters,
            returns="执行结果"
        )
        
        return wrapper
    return decorator

class ToolRegistry:
    """工具注册表 - 单例管理所有工具"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
            cls._instance._categories = {}
        return cls._instance
    
    def register(self, tool: BaseTool) -> bool:
        """注册工具"""
        if tool.metadata.name in self._tools:
            raise ValueError(f"工具 {tool.metadata.name} 已注册")
        
        self._tools[tool.metadata.name] = tool
        
        # 按分类组织
        category = tool.metadata.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(tool.metadata.name)
        
        return True
    
    def register_function(self, func: Callable) -> bool:
        """注册函数作为工具"""
        if not hasattr(func, 'metadata'):
            raise ValueError("函数必须使用 @tool_decorator 装饰")
        
        class FunctionTool(BaseTool):
            async def execute(self, **kwargs):
                return await func(**kwargs)
        
        tool = FunctionTool(func.metadata)
        return self.register(tool)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """按分类获取工具"""
        return self._categories.get(category, [])
    
    def list_all_tools(self) -> List[dict]:
        """列出所有工具信息"""
        tools_info = []
        for name, tool in self._tools.items():
            info = tool.metadata.dict()
            info["stats"] = tool.get_stats()
            tools_info.append(info)
        return tools_info
    
    def search_tools(self, query: str) -> List[dict]:
        """搜索工具"""
        results = []
        query_lower = query.lower()
        
        for name, tool in self._tools.items():
            metadata = tool.metadata
            
            # 在名称、描述、分类中搜索
            if (query_lower in name.lower() or 
                query_lower in metadata.description.lower() or
                query_lower in metadata.category.lower()):
                
                results.append({
                    "name": name,
                    "description": metadata.description,
                    "category": metadata.category
                })
        
        return results
    
    def remove_tool(self, name: str) -> bool:
        """移除工具"""
        if name in self._tools:
            tool = self._tools[name]
            category = tool.metadata.category
            
            # 从分类中移除
            if category in self._categories:
                self._categories[category] = [
                    t for t in self._categories[category] 
                    if t != name
                ]
                if not self._categories[category]:
                    del self._categories[category]
            
            # 从主字典移除
            del self._tools[name]
            return True
        return False
    
    def clear(self):
        """清空所有工具"""
        self._tools.clear()
        self._categories.clear()

async def main():
    """演示工具系统使用"""
    from web_tools import WebSearchTool, APICallerTool, fetch_webpage, check_website_status, fetch_dynamic_webpage
    from data_tools import CalculatorTool, DataAnalyzerTool, json_validator
    from custom_tools import FileReaderTool, TimeSensitiveTool, generate_password

    # 1. 获取工具注册表实例
    registry = ToolRegistry()
    
    # 2. 注册工具
    registry.register(WebSearchTool())
    registry.register(CalculatorTool())
    registry.register(DataAnalyzerTool())
    registry.register(FileReaderTool())
    registry.register(TimeSensitiveTool())
    registry.register(APICallerTool())
    
    # 3. 注册装饰器工具
    registry.register_function(fetch_webpage)
    registry.register_function(fetch_dynamic_webpage)
    registry.register_function(check_website_status)
    registry.register_function(json_validator)
    registry.register_function(generate_password)
    
    a = registry.get_tool('fetch_dynamic_webpage')
    b = await a.safe_execute(url='www.baidu.com')
    

    1

if __name__=="__main__":
    """
    工具系统使用示例
    """
    import asyncio
    import json

        
    asyncio.run(main())