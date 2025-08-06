# ai_agent_template

This is a general AI Agent template. I found it hard learning agents when every tutorial uses frameworks or just makes simple tool calls. This template has a planner. Creates a plan to be executed, each task in the plan has tool calls to be used. The executor takes in a plan an exectues a task. The tools are on a mcp server. We access them through the mcp client. I plan on using this in other agent projects. This might be updated to include other features but for now this template should work.

### Install

```python
uv init
source .venv/bin/activate
uv sync

```

### Run

```python
python main.py
```
