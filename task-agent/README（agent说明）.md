## 一、需求描述

本项目实现了一个具备“能说会做”能力的智能体（AI Agent），主要目标如下：

- ✅ 支持自然语言交互（用户可以直接输入任务）
- ✅ 能理解用户意图并进行任务拆解
- ✅ 能调用工具执行具体操作（如查询天气、生成任务列表、保存文件等）
- ✅ 支持基础的多轮对话记忆

本智能体的典型应用场景包括：

- 任务管理助手（生成待办清单）
- 简单办公助手（保存任务到文件）
- 信息查询助手（天气查询）

------

## 二、业务流程描述

智能体整体工作流程如下：

```
用户输入 → Agent理解意图 → 判断是否需要调用工具 → 执行工具 → 返回结果 → 输出给用户
```

### 详细流程：

1. 用户输入自然语言任务
   （如：“帮我规划今天的学习任务”）
2. Agent（基于大模型）解析意图：
   - 判断是否需要调用工具
   - 拆分任务步骤
3. 如果需要调用工具：
   - 调用对应 Tool（如任务生成、天气查询等）
4. Tool 返回结果
5. Agent 对结果进行整理总结
6. 返回结构化响应给用户

------

## 三、实现说明

### 1️⃣ Agent 核心设计

基于 **LangChain Agent + Tool 调用机制** 实现：

- 使用 `create_agent()` 构建智能体
- 使用 `SYSTEM_PROMPT` 控制智能体行为（强调“能说会做”）
- 使用 `ToolStrategy` 实现结构化输出

核心能力：

- 自然语言理解
- 工具调用决策
- 多步骤任务处理

------

### 2️⃣ 模型配置

```python
model = init_chat_model(
    "deepseek-chat",
    temperature=0.5,
    timeout=10,
    max_tokens=1000
)
```

特点：

- 使用 DeepSeek 大模型
- 控制生成稳定性（temperature=0.5）
- 限制响应长度

------

### 3️⃣ 工具（Tools）设计

系统实现了 4 个核心工具 ：

#### 📌 (1) 天气查询工具

```python
get_weather_for_location(city: str)
```

- 输入：城市名
- 输出：天气信息（模拟）

------

#### 📌 (2) 用户位置获取

```python
get_user_location(runtime)
```

- 根据 user_id 返回用户位置

------

#### 📌 (3) 任务列表生成

```python
create_task_list(user_input: str)
```

- 自动将用户需求转为结构化任务步骤

------

#### 📌 (4) 文件保存工具

```python
save_to_file(content: str)
```

- 将任务写入本地 `tasks.txt`

------

### 4️⃣ 多轮对话记忆

使用：

```python
InMemorySaver()
```

实现：

- 通过 `thread_id` 区分不同会话
- 支持上下文连续对话（基础记忆能力）

------

### 5️⃣ 结构化输出

定义输出格式：

```python
class ResponseFormat(BaseModel):
    punny_response: str
    completion_report: str | None
```

优势：

- 输出规范统一
- 方便后续前端接入或日志处理

------

### 6️⃣ 主程序运行逻辑

```python
while True:
    user_input = input()
    response = agent.invoke(...)
```

特点：

- CLI 交互方式
- 实时任务执行
- 支持连续对话

------

## 四、使用示例（功能演示）

### 示例 1：任务生成

**输入：**

```
帮我安排今天的学习计划
```

**输出：**

```
任务列表：
1. 分析需求
2. 拆分任务
3. 执行计划
```

------

### 示例 2：天气查询

**输入：**

```
今天天气怎么样？
```

**Agent 行为：**

- 调用 `get_user_location`
- 调用 `get_weather_for_location`

------

### 示例 3：保存任务

**输入：**

```
帮我把任务保存下来
```

**执行：**

- 调用 `save_to_file`

------

## 五、GitHub 链接

```
https://github.com/Shirotori0/Schoolworks-group-of-software-engineering-24/tree/main/task-agent
```

------

## 六、小组分工

| 成员      | 分工           |
| --------- | -------------- |
| A  黄天豪 | Agent 架构设计 |
| B         |                |
| C         |                |
| D         |                |

------

## 七、成员心得（示例）

- 通过本项目理解了 Agent 的核心思想：**LLM + Tools**
- 学会了如何让模型“做事”，而不仅仅是“回答问题”
- 熟悉了 LangChain Agent 的基本用法
- 理解了 Prompt 在 Agent 中的重要性

------

