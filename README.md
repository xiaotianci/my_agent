comprehensive-agent-system/
├── .env                    # 环境变量 (API密钥、数据库URL等)
├── .gitignore
├── pyproject.toml         # 现代Python依赖管理 (或 requirements.txt)
├── README.md
│
├── src/                   # 主代码目录
│   ├── __init__.py
│   ├── main.py           # FastAPI应用入口
│   │
│   ├── config/           # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py   # Pydantic配置类
│   │   └── constants.py  # 枚举、常量
│   │
│   ├── core/             # 核心框架
│   │   ├── __init__.py
│   │   ├── state.py      # AgentState 定义
│   │   └── workflow.py   # 主工作流构建
│   │
│   ├── agents/           # 代理实现
│   │   ├── __init__.py
│   │   ├── base.py       # BaseAgent 基类
│   │   ├── researcher.py # 研究型代理
│   │   ├── analyst.py    # 分析型代理
│   │   ├── writer.py     # 写作型代理
│   │   ├── coordinator.py # MultiAgentCoordinator
│   │   └── router.py     # IntelligentRouter
│   │
│   ├── tools/            # 工具系统
│   │   ├── __init__.py
│   │   ├── registry.py   # 工具注册与管理
│   │   ├── web_tools.py  # 网络搜索等
│   │   ├── data_tools.py # 数据处理工具
│   │   └── custom_tools.py # 自定义工具
│   │
│   ├── memory/           # 记忆系统
│   │   ├── __init__.py
│   │   ├── base.py       # 记忆基类
│   │   ├── short_term.py # 短期记忆实现
│   │   ├── long_term.py  # 向量存储长期记忆
│   │   └── manager.py    # HierarchicalMemory 管理器
│   │
│   ├── graph/            # LangGraph节点定义
│   │   ├── __init__.py
│   │   ├── nodes/        # 各功能节点
│   │   │   ├── __init__.py
│   │   │   ├── preprocess.py
│   │   │   ├── routing.py
│   │   │   ├── agent_execution.py
│   │   │   ├── tool_calling.py
│   │   │   └── response_gen.py
│   │   └── edges.py      # 边和条件逻辑定义
│   │
│   ├── api/              # API层
│   │   ├── __init__.py
│   │   ├── endpoints.py  # FastAPI路由
│   │   ├── schemas.py    # Pydantic请求/响应模型
│   │   └── dependencies.py # 依赖注入
│   │
│   ├── monitor/          # 监控与可观测性
│   │   ├── __init__.py
│   │   ├── logging.py    # 结构化日志
│   │   ├── metrics.py    # 性能指标收集
│   │   └── tracer.py     # 执行追踪
│   │
│   └── utils/            # 工具函数
│       ├── __init__.py
│       ├── helpers.py    # 通用辅助函数
│       └── validators.py # 数据验证
│
├── tests/                # 测试目录
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_workflow.py
│   ├── test_tools.py
│   └── conftest.py      # pytest 配置
│
├── data/                 # 数据存储 (gitignore)
│   ├── vector_store/     # ChromaDB 数据
│   ├── sqlite/          # 检查点数据库
│   └── logs/            # 应用日志
│
├── scripts/              # 运维脚本
│   ├── deploy.sh
│   ├── seed_memory.py    # 初始化记忆库
│   └── benchmark.py      # 性能测试
│
└── docker/               # Docker配置
    ├── Dockerfile
    ├── docker-compose.yml
    └── nginx.conf