# 主工作流构建


# src/core/workflow.py
from langgraph.graph import StateGraph, END
from src.graph.nodes import (
    PreprocessNode, RoutingNode, 
    AgentExecutionNode, ToolCallingNode
)
from src.core.state import AgentState

class WorkflowBuilder:
    """工作流构建器，负责组装节点"""
    
    def __init__(self, settings):
        self.graph = StateGraph(AgentState)
        self.settings = settings
        self._init_nodes()
    
    def _init_nodes(self):
        # 初始化所有节点实例
        self.nodes = {
            "preprocess": PreprocessNode(),
            "router": RoutingNode(),
            "agent_executor": AgentExecutionNode(),
            "tool_caller": ToolCallingNode()
        }
        
        # 注册节点到图
        for name, node in self.nodes.items():
            self.graph.add_node(name, node)
    
    def build(self) -> StateGraph:
        """构建完整工作流"""
        # 定义边连接
        self.graph.set_entry_point("preprocess")
        self.graph.add_edge("preprocess", "router")
        
        # 条件路由
        self.graph.add_conditional_edges(
            "router",
            self._route_to_agent,
            {agent: "agent_executor" for agent in self.settings.enabled_agents}
        )
        
        self.graph.add_edge("agent_executor", END)
        return self.graph.compile()