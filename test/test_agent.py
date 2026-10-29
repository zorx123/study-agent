"""Проверка цикла агента на поддельном клиенте: API-ключ не нужен."""
import sys, pathlib
from types import SimpleNamespace as NS
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import agent


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.messages = self  # client.messages.create(...)

    def create(self, **kwargs):
        return self.replies.pop(0)


def test_agent_calls_tool_then_answers():
    tool_call = NS(stop_reason="tool_use", content=[
        NS(type="tool_use", id="1", name="calculate", input={"expression": "6*7"})])
    final = NS(stop_reason="end_turn", content=[NS(type="text", text="Ответ: 42")])
    msgs = [{"role": "user", "content": "6*7?"}]
    assert agent.run_agent(FakeClient([tool_call, final]), msgs) == "Ответ: 42"
    # результат инструмента попал в историю
    assert msgs[2]["content"][0]["content"] == "42"


def test_agent_step_limit():
    loop = NS(stop_reason="tool_use", content=[
        NS(type="tool_use", id="1", name="get_time", input={})])
    out = agent.run_agent(FakeClient([loop] * 20), [{"role": "user", "content": "?"}])
    assert "лимит" in out
