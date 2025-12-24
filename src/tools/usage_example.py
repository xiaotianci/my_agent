# tools/usage_example.py
"""
工具系统使用示例
"""
import asyncio
import json
from registry import ToolRegistry
from web_tools import WebSearchTool, APICallerTool, fetch_webpage, check_website_status, fetch_dynamic_webpage
from data_tools import CalculatorTool, DataAnalyzerTool, json_validator
from custom_tools import FileReaderTool, TimeSensitiveTool, generate_password

async def main():
    """演示工具系统使用"""
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

    # 4. 列出所有工具
    print("=== 所有可用工具 ===")
    for tool_info in registry.list_all_tools():
        print(f"- {tool_info['name']}: {tool_info['description']}")
    

    # 5. 使用计算器工具
    print("\n=== 使用计算器工具 ===")
    calculator = registry.get_tool("calculator")
    if calculator:
        result = await calculator.safe_execute(
            expression="math.sin(math.pi/2) + math.sqrt(16)",
            variables={},
            precision=4
        )
        print(f"计算结果: {result}")
    
    # 6. 搜索工具
    print("\n=== 搜索 '数据分析' 相关工具 ===")
    search_results = registry.search_tools("web_search")
    for tool in search_results:
        print(f"- {tool['name']} ({tool['category']}): {tool['description']}")
    
    # 7. 使用装饰器工具
    print("\n=== 使用装饰器工具 ===")
    password_tool = registry.get_tool("generate_password")
    if password_tool:
        result = await password_tool.safe_execute(
            length=16,
            use_uppercase=True,
            use_numbers=True,
            use_symbols=True
        )
        print(f"生成的密码: {result}")
    
    # 8. 按分类获取工具
    print("\n=== 按分类查看工具 ===")
    web_tools = registry.get_tools_by_category("web")
    print(f"网络工具: {web_tools}")
    
    # 9. 移除工具
    print("\n=== 移除工具测试 ===")
    if registry.remove_tool("file_reader"):
        print("成功移除 file_reader 工具")
    
    # 10. 显示最终工具列表
    print("\n=== 最终工具统计 ===")
    for tool_info in registry.list_all_tools():
        print(f"{tool_info['name']}: 调用 {tool_info['stats']['call_count']} 次, "
              f"成功率 {tool_info['stats']['success_rate']:.1%}")

if __name__ == "__main__":
    asyncio.run(main())