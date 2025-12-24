# 自定义工具

# tools/custom_tools.py
"""
自定义工具 - 业务特定工具示例
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from registry import BaseTool, ToolMetadata, ToolParameter, tool_decorator

class FileReaderTool(BaseTool):
    """文件读取工具 (示例)"""
    
    def __init__(self, allowed_extensions: List[str] = None):
        metadata = ToolMetadata(
            name="file_reader",
            description="读取本地文件内容",
            category="custom",
            parameters=[
                ToolParameter(
                    name="file_path",
                    type="string",
                    description="文件路径",
                    required=True
                ),
                ToolParameter(
                    name="encoding",
                    type="string",
                    description="文件编码",
                    required=False,
                    default="utf-8"
                ),
                ToolParameter(
                    name="max_size_mb",
                    type="integer",
                    description="最大文件大小(MB)",
                    required=False,
                    default=10
                )
            ],
            returns="文件内容",
            timeout=10,
            requires_auth=True  # 需要授权，因为是本地文件操作
        )
        super().__init__(metadata)
        self.allowed_extensions = allowed_extensions or ['.txt', '.md', '.json', '.csv', '.py']
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """读取文件"""
        file_path = kwargs["file_path"]
        encoding = kwargs.get("encoding", "utf-8")
        max_size_mb = kwargs.get("max_size_mb", 10)
        
        # 安全检查
        if not self._is_safe_path(file_path):
            return {"error": "不允许的文件路径"}
        
        # 检查文件扩展名
        if not any(file_path.endswith(ext) for ext in self.allowed_extensions):
            return {"error": f"不支持的文件类型，允许的类型: {self.allowed_extensions}"}
        
        try:
            # 检查文件大小
            import os
            file_size = os.path.getsize(file_path)
            if file_size > max_size_mb * 1024 * 1024:
                return {"error": f"文件过大，限制为 {max_size_mb}MB"}
            
            # 读取文件
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "file_path": file_path,
                "size_bytes": file_size,
                "content": content,
                "encoding": encoding,
                "read_time": datetime.now().isoformat()
            }
        except FileNotFoundError:
            return {"error": f"文件不存在: {file_path}"}
        except Exception as e:
            return {"error": f"读取文件失败: {str(e)}"}
    
    def _is_safe_path(self, file_path: str) -> bool:
        """检查文件路径是否安全"""
        # 实现路径安全检查
        # 这里简化处理，实际应根据业务需求实现
        forbidden_patterns = ['..', '~', '/etc/', '/var/', 'C:\\Windows']
        return not any(pattern in file_path for pattern in forbidden_patterns)

class TimeSensitiveTool(BaseTool):
    """时间敏感工具示例"""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="time_operations",
            description="时间相关操作",
            category="custom",
            parameters=[
                ToolParameter(
                    name="operation",
                    type="string",
                    description="操作类型 (now/format/calculate/convert)",
                    required=True
                ),
                ToolParameter(
                    name="timestamp",
                    type="string",
                    description="时间戳或日期字符串",
                    required=False
                ),
                ToolParameter(
                    name="format",
                    type="string",
                    description="时间格式",
                    required=False,
                    default="%Y-%m-%d %H:%M:%S"
                ),
                ToolParameter(
                    name="delta_days",
                    type="integer",
                    description="天数偏移量",
                    required=False,
                    default=0
                )
            ],
            returns="时间操作结果",
            timeout=5
        )
        super().__init__(metadata)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行时间操作"""
        operation = kwargs["operation"]
        
        if operation == "now":
            now = datetime.now()
            return {
                "timestamp": now.isoformat(),
                "formatted": now.strftime(kwargs.get("format", "%Y-%m-%d %H:%M:%S")),
                "timezone": "UTC"  # 实际应获取时区
            }
        
        elif operation == "format":
            timestamp = kwargs.get("timestamp")
            if not timestamp:
                return {"error": "需要timestamp参数"}
            
            try:
                # 尝试解析时间戳
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return {
                    "original": timestamp,
                    "formatted": dt.strftime(kwargs.get("format", "%Y-%m-%d %H:%M:%S")),
                    "timestamp": dt.timestamp()
                }
            except ValueError:
                return {"error": "无法解析时间戳"}
        
        elif operation == "calculate":
            delta_days = kwargs.get("delta_days", 0)
            base_date = datetime.now()
            target_date = base_date + timedelta(days=delta_days)
            
            return {
                "base_date": base_date.isoformat(),
                "target_date": target_date.isoformat(),
                "delta_days": delta_days,
                "day_of_week": target_date.strftime("%A"),
                "is_future": delta_days > 0
            }
        
        else:
            return {"error": f"不支持的操作: {operation}"}

# 业务特定工具示例
@tool_decorator(
    name="generate_password",
    description="生成随机密码"
)
async def generate_password(
    length: int = 12,
    use_uppercase: bool = True,
    use_numbers: bool = True,
    use_symbols: bool = True
) -> Dict[str, Any]:
    """生成安全随机密码"""
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if use_uppercase else ''
    numbers = '0123456789' if use_numbers else ''
    symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?' if use_symbols else ''
    
    all_chars = lowercase + uppercase + numbers + symbols
    
    if not all_chars:
        return {"error": "至少选择一种字符类型"}
    
    if length < 4:
        return {"error": "密码长度至少为4位"}
    
    # 确保每种类型至少有一个字符
    password_chars = []
    if lowercase:
        password_chars.append(random.choice(lowercase))
    if uppercase:
        password_chars.append(random.choice(uppercase))
    if numbers:
        password_chars.append(random.choice(numbers))
    if symbols:
        password_chars.append(random.choice(symbols))
    
    # 填充剩余长度
    remaining = length - len(password_chars)
    password_chars.extend(random.choice(all_chars) for _ in range(remaining))
    
    # 随机打乱
    random.shuffle(password_chars)
    password = ''.join(password_chars)
    
    # 评估密码强度
    strength = "弱"
    score = 0
    if length >= 12:
        score += 1
    if use_uppercase:
        score += 1
    if use_numbers:
        score += 1
    if use_symbols:
        score += 1
    
    if score >= 3:
        strength = "强"
    elif score >= 2:
        strength = "中"
    
    return {
        "password": password,
        "length": length,
        "strength": strength,
        "score": score,
        "contains_uppercase": use_uppercase,
        "contains_numbers": use_numbers,
        "contains_symbols": use_symbols
    }

@tool_decorator(
    name="mock_payment",
    description="模拟支付处理"
)
async def mock_payment(
    amount: float,
    currency: str = "USD",
    payment_method: str = "credit_card"
) -> Dict[str, Any]:
    """模拟支付处理流程"""
    await asyncio.sleep(1)  # 模拟处理时间
    
    # 模拟成功率
    success_rate = 0.95  # 95%成功率
    is_successful = random.random() < success_rate
    
    if is_successful:
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "message": "支付成功"
        }
    else:
        return {
            "success": False,
            "error": "支付处理失败",
            "error_code": random.choice(["INSUFFICIENT_FUNDS", "NETWORK_ERROR", "DECLINED"]),
            "amount": amount,
            "currency": currency,
            "status": "failed",
            "timestamp": datetime.now().isoformat(),
            "suggestion": "请重试或使用其他支付方式"
        }