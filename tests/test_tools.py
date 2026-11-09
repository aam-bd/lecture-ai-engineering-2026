"""ツールのテスト（LLMもAPIキーも使わない）。"""

import json

from app import tools


def test_glossary_ids_are_unique_and_related_links_exist():
    terms = tools.load_glossary()
    ids = [t["id"] for t in terms]
    assert len(ids) == len(set(ids))
    for t in terms:
        for r in t["related"]:
            assert r in ids, f"{t['id']} の related に存在しない id: {r}"


def test_search_finds_term_by_name_and_alias():
    for query in ["LoRA", "lora", "Low-Rank Adaptation"]:
        hits = json.loads(tools.search_glossary(query))
        assert hits[0]["term"] == "LoRA", query


def test_search_finds_course_specific_term():
    hits = json.loads(tools.search_glossary("lecNN-start"))
    assert hits[0]["term"] == "lecNN-start タグ"


def test_search_limits_number_of_results():
    hits = json.loads(tools.search_glossary("エージェント"))
    assert 1 <= len(hits) <= tools.MAX_RESULTS


def test_search_reports_not_found():
    assert "見つかりませんでした" in tools.search_glossary("存在しない用語xyz")


def test_lecture_summary():
    assert "エージェント" in tools.get_lecture_summary(3)
    assert "まだありません" in tools.get_lecture_summary(99)


def test_default_question_of_lecture1_is_answerable_from_glossary():
    """第1回の既定の質問（app.ask）は、第3回のエージェントが用語集で正しく答えられること。"""
    from app.ask import DEFAULT_QUESTION

    assert "3レベル" in DEFAULT_QUESTION
    hits = json.loads(tools.search_glossary("3レベル"))
    assert hits[0]["term"] == "宿題の3レベル"


def test_make_quiz_returns_valid_question_and_answer():
    quiz_str = tools.make_quiz(2)
    data = json.loads(quiz_str)
    assert "question" in data
    assert "answer" in data
    assert len(data["question"]) > 0
    assert len(data["answer"]) > 0


def test_make_quiz_handles_nonexistent_lecture():
    # 講義0や99など用語が存在しない回でも例外を出さずに案内文を返すこと
    res_zero = tools.make_quiz(0)
    assert "見つかりませんでした" in res_zero
    res_99 = tools.make_quiz(99)
    assert "見つかりませんでした" in res_99


def test_save_learning_log_creates_file(tmp_path, monkeypatch):
    # テスト用の一時ディレクトリを tools.DATA_DIR の親代わりに差し替えて検証
    import json
    from pathlib import Path

    test_log_dir = tmp_path / "learning_log"
    # tools.py 内の log_dir 取得パスを模倣または直接検証
    result = tools.save_learning_log(topic="PEFTとLoRA", notes="LoRAのrankとalphaを学んだ", lecture=2)
    assert "学習記録を保存しました" in result

    root_log_dir = Path(__file__).resolve().parent.parent / "learning_log"
    saved_files = list(root_log_dir.glob("*.json"))
    assert len(saved_files) >= 1
    content = json.loads(saved_files[-1].read_text(encoding="utf-8"))
    assert "topic" in content and "notes" in content

