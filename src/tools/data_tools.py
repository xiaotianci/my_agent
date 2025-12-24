# 数据处理工具

# tools/data_tools.py
"""
数据处理工具 - 计算、转换、分析等
"""
import pandas as pd
import numpy as np
import json
import csv
import math
from io import StringIO
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from registry import BaseTool, ToolMetadata, ToolParameter, tool_decorator
import ast

class CalculatorTool(BaseTool):
    """高级计算器工具"""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="calculator",
            description="执行数学计算和表达式求值",
            category="data",
            parameters=[
                ToolParameter(
                    name="expression",
                    type="string",
                    description="数学表达式 (支持 +, -, *, /, **, sin, cos 等)",
                    required=True
                ),
                ToolParameter(
                    name="variables",
                    type="object",
                    description="变量字典 (如 {'x': 5, 'y': 3})",
                    required=False,
                    default={}
                ),
                ToolParameter(
                    name="precision",
                    type="integer",
                    description="结果精度 (小数位数)",
                    required=False,
                    default=6
                )
            ],
            returns="计算结果",
            timeout=5
        )
        super().__init__(metadata)
        # 安全允许的函数
        self.safe_namespace = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'len': len, 'int': int, 'float': float,
            'str': str, 'bool': bool, 'list': list, 'dict': dict,
            'set': set, 'pow': pow, 'divmod': divmod,
            'math': math  # 导入math模块的函数
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行计算"""
        expression = kwargs["expression"]
        variables = kwargs.get("variables", {})
        precision = kwargs.get("precision", 6)
        
        try:
            # 创建安全的命名空间
            namespace = {**self.safe_namespace, **variables}
            
            tree = ast.parse(expression, '<string>', 'eval')

            # 验证代码安全性
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id not in namespace:
                            raise ValueError(f"不安全函数: {node.func.id}")
            
            # 禁用危险操作
            code = compile(tree, '<string>', 'eval')
            # 执行计算
            result = eval(code, {"__builtins__": {}}, namespace)
            
            # 处理精度
            if isinstance(result, float):
                result = round(result, precision)
            
            return {
                "result": result,
                "expression": expression,
                "variables": variables,
                "type": type(result).__name__
            }
        except Exception as e:
            return {
                "error": f"计算失败: {str(e)}",
                "expression": expression
            }

class DataAnalyzerTool(BaseTool):
    """数据分析工具"""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="data_analyzer",
            description="分析JSON/CSV数据，提供统计信息",
            category="data",
            parameters=[
                ToolParameter(
                    name="data",
                    type="string",
                    description="JSON或CSV格式的数据",
                    required=True
                ),
                ToolParameter(
                    name="data_type",
                    type="string",
                    description="数据类型 (json/csv)",
                    required=False,
                    default="json"
                ),
                ToolParameter(
                    name="analysis_type",
                    type="string",
                    description="分析类型 (summary/stats/correlation)",
                    required=False,
                    default="summary"
                )
            ],
            returns="分析结果",
            timeout=10
        )
        super().__init__(metadata)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """分析数据"""
        data_str = kwargs["data"]
        data_type = kwargs.get("data_type", "json")
        analysis_type = kwargs.get("analysis_type", "summary")
        
        try:
            if data_type == "json":
                data = json.loads(data_str)
                df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
            else:  # csv
                df = pd.read_csv(StringIO(data_str))
            
            # 执行不同类型的分析
            if analysis_type == "summary":
                result = self._get_summary(df)
            elif analysis_type == "stats":
                result = self._get_statistics(df)
            elif analysis_type == "correlation":
                result = self._get_correlation(df)
            else:
                result = {"error": f"不支持的分析类型: {analysis_type}"}
            
            return {
                "analysis_type": analysis_type,
                "data_shape": f"{df.shape[0]}行 x {df.shape[1]}列",
                "columns": list(df.columns),
                "result": result
            }
        except Exception as e:
            return {"error": f"数据分析失败: {str(e)}"}
    
    def _get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取数据摘要"""
        return {
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "unique_counts": df.nunique().to_dict()
        }
    
    def _get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取统计信息"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {"message": "没有数值列可用于统计分析"}
        
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "q1": float(df[col].quantile(0.25)),
                "q3": float(df[col].quantile(0.75))
            }
        
        return stats
    
    def _get_correlation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取相关性矩阵"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {"message": "需要至少两个数值列计算相关性"}
        
        corr_matrix = df[numeric_cols].corr()
        
        # 转换为字典格式
        return corr_matrix.to_dict()

# 装饰器方式定义的数据工具
@tool_decorator(
    name="json_validator",
    description="验证和格式化JSON数据"
)
async def json_validator(json_str: str, pretty_print: bool = True) -> Dict[str, Any]:
    """
    验证JSON字符串并可选地美化输出
    
    Args:
        json_str: JSON字符串
        pretty_print: 是否美化输出
        
    Returns:
        验证结果和格式化后的JSON
    """
    try:
        data = json.loads(json_str)
        
        if pretty_print:
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            formatted = json.dumps(data, ensure_ascii=False)
        
        return {
            "valid": True,
            "size_bytes": len(json_str.encode('utf-8')),
            "type": type(data).__name__,
            "formatted": formatted
        }
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": str(e),
            "position": e.pos,
            "suggestion": f"检查位置 {e.pos} 附近的语法"
        }

@tool_decorator(
    name="csv_converter",
    description="将JSON转换为CSV格式"
)
async def csv_converter(json_data: str, delimiter: str = ",") -> Dict[str, Any]:
    """将JSON数组转换为CSV格式"""
    try:
        data = json.loads(json_data)
        
        if not isinstance(data, list):
            data = [data]
        
        # 确保所有字典有相同的键
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=list(all_keys), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
        
        return {
            "success": True,
            "csv": output.getvalue(),
            "rows": len(data),
            "columns": len(all_keys)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}