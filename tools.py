"""Инструменты, которые агент может вызывать: калькулятор, заметки, время."""
import ast
import datetime
import json
import operator
from pathlib import Path

NOTES_FILE = Path("notes.json")

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def calculate(expression: str) -> str:
    """Безопасный калькулятор: только числа и операции + - * / % **."""
    def ev(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            left, right = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("слишком большая степень")
            return _OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError("разрешены только числа и операции + - * / % **")

    try:
        return str(ev(ast.parse(expression, mode="eval").body))
    except ZeroDivisionError:
        return "Ошибка: деление на ноль"
    except (ValueError, SyntaxError) as e:
        return f"Ошибка: {e}"


def save_note(text: str, path: Path = None) -> str:
    path = Path(path or NOTES_FILE)
    notes = json.loads(path.read_text("utf-8")) if path.exists() else []
    notes.append({"time": datetime.datetime.now().isoformat(timespec="seconds"), "text": text})
    path.write_text(json.dumps(notes, ensure_ascii=False, indent=2), "utf-8")
    return f"Заметка сохранена (всего: {len(notes)})"


def list_notes(path: Path = None) -> str:
    path = Path(path or NOTES_FILE)
    if not path.exists():
        return "Заметок пока нет"
    notes = json.loads(path.read_text("utf-8"))
    return "\n".join(f"{i}. {n['text']} ({n['time']})" for i, n in enumerate(notes, 1)) or "Заметок пока нет"


def get_time() -> str:
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M")


# Описание инструментов для модели (формат tool use)
TOOLS = [
    {"name": "calculate", "description": "Вычисляет арифметическое выражение, например 12*(3+4)",
     "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    {"name": "save_note", "description": "Сохраняет заметку пользователя",
     "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "list_notes", "description": "Показывает все сохранённые заметки",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_time", "description": "Возвращает текущие дату и время",
     "input_schema": {"type": "object", "properties": {}}},
]

_DISPATCH = {"calculate": calculate, "save_note": save_note, "list_notes": list_notes, "get_time": get_time}


def run_tool(name: str, args: dict) -> str:
    if name not in _DISPATCH:
        return f"Ошибка: неизвестный инструмент {name}"
    try:
        return _DISPATCH[name](**args)
    except TypeError as e:
        return f"Ошибка аргументов: {e}"
