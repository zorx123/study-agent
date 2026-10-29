"""Консольный ИИ-агент: модель сама решает, когда вызвать инструмент."""
import os

from tools import TOOLS, run_tool

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")
MAX_STEPS = 6  # защита от бесконечного цикла
SYSTEM = (
    "Ты помощник для учёбы. Для вычислений, заметок и времени используй инструменты, "
    "не считай в уме. Отвечай кратко и по-русски."
)


def run_agent(client, messages, model=MODEL):
    """Цикл агента: запрос -> (вызов инструмента -> результат)* -> ответ."""
    for _ in range(MAX_STEPS):
        resp = client.messages.create(
            model=model, max_tokens=1000, system=SYSTEM, tools=TOOLS, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                output = run_tool(block.name, block.input)
                print(f"  [инструмент] {block.name}({block.input}) -> {output}")
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": results})
    return "Агент остановлен: превышен лимит шагов."


def main():
    from anthropic import Anthropic  # ключ берётся из переменной ANTHROPIC_API_KEY

    client = Anthropic()
    messages = []
    print("Помощник для учёбы. Выход: пустая строка или Ctrl+C.")
    while True:
        try:
            text = input("\nТы: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            break
        messages.append({"role": "user", "content": text})
        print("Агент:", run_agent(client, messages))


if __name__ == "__main__":
    main()
