# 网络搜索等

# tools/web_tools.py
"""
网络相关工具 - 搜索、爬虫、API调用等
"""
# Playwright 示例（异步）
from playwright.async_api import async_playwright
import aiohttp
import asyncio
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode
import json
from datetime import datetime
from registry import BaseTool, ToolMetadata, ToolParameter, tool_decorator

class WebSearchTool(BaseTool):
    """网页搜索工具 (可替换为 SerpAPI、Google Search API 等)"""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="web_search",
            description="搜索互联网获取最新信息",
            category="web",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="搜索关键词",
                    required=True
                ),
                ToolParameter(
                    name="max_results",
                    type="integer",
                    description="最大结果数",
                    required=False,
                    default=5
                ),
                ToolParameter(
                    name="search_engine",
                    type="string",
                    description="搜索引擎 (google/bing/duckduckgo)",
                    required=False,
                    default="google"
                )
            ],
            returns="搜索结果的JSON列表",
            timeout=15
        )
        super().__init__(metadata)
        self.session = None
    
    async def _ensure_session(self):
        """确保HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.metadata.timeout)
            )
    
    async def execute(self, **kwargs) -> List[Dict[str, Any]]:
        """执行搜索"""
        await self._ensure_session()
        
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 5)
        search_engine = kwargs.get("search_engine", "google")
        
        # 这里使用DuckDuckGo的HTML scraping作为示例
        # 生产环境建议使用官方API (如 SerpAPI、Google Custom Search)
        
        if search_engine == "duckduckgo":
            return await self._search_duckduckgo(query, max_results)
        else:
            # 模拟返回，实际应调用相应API
            return [
                {
                    "title": f"搜索结果 {i} - {query}",
                    "url": f"https://example.com/result{i}",
                    "snippet": f"这是关于 '{query}' 的模拟结果 {i}。生产环境请替换为真实API。",
                    "source": search_engine,
                    "timestamp": datetime.now().isoformat()
                }
                for i in range(1, max_results + 1)
            ]
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """使用DuckDuckGo搜索 (示例)"""
        try:
            url = f"https://html.duckduckgo.com/html/?{urlencode({'q': query})}"
            
            async with self.session.get(url, headers={
                "User-Agent": "Mozilla/5.0 (兼容Agent系统)"
            }) as response:
                html = await response.text()
                
                # 这里简化处理，实际应解析HTML
                return [
                    {
                        "title": f"DuckDuckGo结果: {query}",
                        "url": "https://duckduckgo.com",
                        "snippet": "实际实现需要HTML解析",
                        "source": "duckduckgo",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
        except Exception as e:
            return [{"error": f"搜索失败: {str(e)}"}]
    
    async def close(self):
        """关闭资源"""
        if self.session and not self.session.closed:
            await self.session.close()

class APICallerTool(BaseTool):
    """通用API调用工具"""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="api_call",
            description="调用外部API",
            category="web",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="API端点URL",
                    required=True
                ),
                ToolParameter(
                    name="method",
                    type="string",
                    description="HTTP方法 (GET/POST/PUT/DELETE)",
                    required=False,
                    default="GET"
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="请求头",
                    required=False,
                    default={}
                ),
                ToolParameter(
                    name="params",
                    type="object",
                    description="查询参数",
                    required=False,
                    default={}
                ),
                ToolParameter(
                    name="data",
                    type="object",
                    description="请求体数据",
                    required=False,
                    default={}
                ),
                ToolParameter(
                    name="timeout",
                    type="integer",
                    description="超时时间(秒)",
                    required=False,
                    default=30
                )
            ],
            returns="API响应",
            timeout=60
        )
        super().__init__(metadata)
        self.session = None
    
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行API调用"""
        await self._ensure_session()
        
        url = kwargs["url"]
        method = kwargs.get("method", "GET").upper()
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})
        data = kwargs.get("data", {})
        timeout = kwargs.get("timeout", 30)
        
        # 设置默认请求头
        if "Content-Type" not in headers and method in ["POST", "PUT", "PATCH"]:
            headers["Content-Type"] = "application/json"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data if method in ["POST", "PUT", "PATCH"] else None,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                # 尝试解析JSON响应
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "url": str(response.url),
                    "success": 200 <= response.status < 300
                }
        except asyncio.TimeoutError:
            return {"error": f"请求超时 ({timeout}秒)", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# 装饰器方式定义的网络工具
@tool_decorator(
    name="fetch_webpage",
    description="获取网页内容"
)
async def fetch_webpage(url: str, timeout: int = 10) -> str:
    """
    获取指定URL的网页内容
    
    Args:
        url: 网页URL
        timeout: 超时时间(秒)
    
    Returns:
        网页HTML内容
    """
    print('fetch_webpage')
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                url, 
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers={"User-Agent": "Agent-System/1.0"}
            ) as response:
                return await response.text()
        except Exception as e:
            return f"获取网页失败: {str(e)}"

@tool_decorator(
    name="fetch_dynamic_webpage",
    description="获取客户端渲染的动态网页内容"
)
async def fetch_dynamic_webpage(url: str, timeout: int = 10) -> str:
    """
    获取指定URL的网页内容
    
    Args:
        url: 网页URL
        timeout: 超时时间(秒)
    
    Returns:
        网页HTML内容
    """
    
    print('fetch_dynamic_webpage')
    async with async_playwright() as session:
        try:
            browser = await session.chromium.launch(
                channel="chrome",
                headless=True
                )
            page = await browser.new_page()
            await page.goto(url)
            content = await page.inner_text("#dynamic-content")
            await browser.close()
            return content
        except Exception as e:
            return {"url": url, "error": str(e), "status_code": 0}

@tool_decorator(
    name="check_website_status",
    description="检查网站状态"
)
async def check_website_status(url: str) -> Dict[str, Any]:
    """检查网站是否可达及其状态码"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(url, allow_redirects=True) as response:
                return {
                    "url": url,
                    "status_code": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "final_url": str(response.url)
                }
        except Exception as e:
            return {"url": url, "error": str(e), "status_code": 0}
        
if __name__=="__main__":
    a = asyncio.run(fetch_dynamic_webpage(url='https://www.baidu.com'))
    # a = asyncio.run(fetch_dynamic_webpage(url='https://www.ccxi.com.cn/creditrating/result'))
    # asyncio.run(check_website_status(url='https://www.ccxi.com.cn/creditrating/result'))
    1