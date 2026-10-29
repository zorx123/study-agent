import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import tools


def test_calculate_basic():
    assert tools.calculate("12*(3+4)") == "84"
    assert tools.calculate("2**10") == "1024"


def test_calculate_rejects_code():
    assert tools.calculate("__import__('os').system('ls')").startswith("Ошибка")


def test_calculate_zero_and_big_power():
    assert "ноль" in tools.calculate("1/0")
    assert tools.calculate("2**1000").startswith("Ошибка")


def test_notes_roundtrip(tmp_path):
    p = tmp_path / "n.json"
    assert "Заметок пока нет" in tools.list_notes(p)
    tools.save_note("купить тетрадь", p)
    assert "купить тетрадь" in tools.list_notes(p)


def test_run_tool_unknown_and_bad_args():
    assert tools.run_tool("nope", {}).startswith("Ошибка")
    assert tools.run_tool("calculate", {"wrong": 1}).startswith("Ошибка аргументов")
