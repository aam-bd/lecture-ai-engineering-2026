"""第5回: 検索処理・コンテキスト拡張（Window）・ツールのテスト。APIは呼ばない。"""

import json
from unittest.mock import Mock, patch
import pytest

from app import retrieval, tools


def test_search_with_window_adjacent_pages(monkeypatch):
    """シードページの前後1ページが同一ドキュメントから拡張されることを確認する。"""
    hit = {
        "page_id": "lec02-main-p052",
        "document_id": "lec02-main",
        "lecture": 2,
        "page": 52,
        "distance": 0.12,
        "title": "LoRA と QLoRA",
        "content": "元の重みは固定し、小さな差分だけを学習する",
    }
    monkeypatch.setattr(retrieval, "search", lambda *args, **kwargs: [hit])

    results = retrieval.search_with_window("LoRA QLoRA 違い", window=1)
    # 前後1ページで最大3件（p51, p52, p53）
    assert len(results) == 3
    page_ids = [r["page_id"] for r in results]
    assert page_ids == ["lec02-main-p051", "lec02-main-p052", "lec02-main-p053"]

    # シードと前後コンテキストのメタデータを検証
    p51 = results[0]
    p52 = results[1]
    p53 = results[2]

    assert p51["is_seed"] is False
    assert p51["relative_pos"] == "offset_-1"
    assert p51["page"] == 51

    assert p52["is_seed"] is True
    assert p52["relative_pos"] == "seed"
    assert p52["page"] == 52

    assert p53["is_seed"] is False
    assert p53["relative_pos"] == "offset_+1"
    assert p53["page"] == 53


def test_search_with_window_document_boundary(monkeypatch):
    """ドキュメント先頭（p.1）のシードに対して、p.0や別資料へ越境しないことを確認する。"""
    hit = {
        "page_id": "lec01-main-p001",
        "document_id": "lec01-main",
        "lecture": 1,
        "page": 1,
        "distance": 0.08,
        "title": "タイトル",
        "content": "講義1の表紙",
    }
    monkeypatch.setattr(retrieval, "search", lambda *args, **kwargs: [hit])

    results = retrieval.search_with_window("第1回 表紙", window=1)
    # p.1の前にp.0は存在しないため、p.1とp.2の2件のみ
    assert len(results) == 2
    assert results[0]["page"] == 1
    assert results[0]["is_seed"] is True
    assert results[1]["page"] == 2
    assert results[1]["is_seed"] is False
    assert all(r["document_id"] == "lec01-main" for r in results)


def test_search_with_window_deduplication(monkeypatch):
    """連続するスライドがシードになった場合、重複ページが排除されることを確認する。"""
    hits = [
        {
            "page_id": "lec02-main-p051",
            "document_id": "lec02-main",
            "lecture": 2,
            "page": 51,
            "distance": 0.15,
            "title": "PEFT",
            "content": "PEFTの概要",
        },
        {
            "page_id": "lec02-main-p052",
            "document_id": "lec02-main",
            "lecture": 2,
            "page": 52,
            "distance": 0.10,
            "title": "LoRA と QLoRA",
            "content": "LoRAとQLoRAの仕組み",
        },
    ]
    monkeypatch.setattr(retrieval, "search", lambda *args, **kwargs: hits)

    results = retrieval.search_with_window("LoRA PEFT", window=1)
    # p51のウィンドウ: 50, 51, 52
    # p52のウィンドウ: 51, 52, 53
    # 重複除去後のページ一覧: 50, 51, 52, 53 （4件）
    pages = [r["page"] for r in results]
    assert pages == [50, 51, 52, 53]
    assert len(set(r["page_id"] for r in results)) == 4


def test_search_materials_with_window_tool(monkeypatch):
    """app.tools.search_materials_with_window がJSON形式で結果を返すことを確認する。"""
    dummy_results = [
        {"page_id": "lec02-main-p052", "page": 52, "content": "本文", "is_seed": True}
    ]
    monkeypatch.setattr(retrieval, "search_with_window", lambda q, window=1: dummy_results)

    raw_json = tools.search_materials_with_window("LoRA")
    data = json.loads(raw_json)
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["page_id"] == "lec02-main-p052"


def test_tree_navigation():
    """Tree探索（browse_tree）が目次ノードおよび本文を取得できることを確認する。"""
    # ルートノード
    root = retrieval.browse_tree(None)
    assert root["node"]["id"] == "aie2026-materials"
    child_ids = [c["id"] for c in root["children"]]
    assert "lec02-main" in child_ids

    # 第2回の講義ノード
    lec02 = retrieval.browse_tree("lec02-main")
    assert lec02["node"]["title"] == "基盤モデルの仕組み"
    section_ids = [c["id"] for c in lec02["children"]]
    assert "lec02-main-s045" in section_ids

    # ページの全文取得
    page = retrieval.browse_tree("lec02-main-p052")
    assert page["node"]["id"] == "lec02-main-p052"
    assert "LoRA と QLoRA" in page["node"]["title"]
    assert "元の重みは固定" in page["node"]["content"]


def test_search_graph_expansion(monkeypatch):
    """search_graph がシードから隣接ページおよび共通用語をたどって候補を広げることを確認する。"""
    hit = {
        "page_id": "lec02-main-p052",
        "document_id": "lec02-main",
        "lecture": 2,
        "page": 52,
        "distance": 0.10,
        "title": "LoRA と QLoRA",
        "content": "LoRAとQLoRAの仕組み",
    }
    monkeypatch.setattr(retrieval, "search", lambda *args, **kwargs: [hit])

    graph_res = retrieval.search_graph("LoRA QLoRA")
    assert "seeds" in graph_res and "expanded" in graph_res
    assert len(graph_res["seeds"]) == 1
    assert graph_res["seeds"][0]["page_id"] == "lec02-main-p052"

    # expanded に前後ページや関連用語で接続されたページが含まれる
    expanded_ids = [e["page_id"] for e in graph_res["expanded"]]
    assert len(expanded_ids) > 0
    # 隣接ページ（p051 または p053）が含まれることを確認
    assert "lec02-main-p051" in expanded_ids or "lec02-main-p053" in expanded_ids


def test_read_page_and_get_all_materials():
    """read_page および get_all_materials の基本動作を確認する。"""
    page = retrieval.read_page("lec02-main-p052")
    assert page["page_id"] == "lec02-main-p052"
    assert page["page"] == 52

    with pytest.raises(ValueError, match="対象のページが見つかりません"):
        retrieval.read_page("nonexistent-page-id")

    all_mat = retrieval.get_all_materials()
    assert "資料: lec01-main" in all_mat
    assert "PDF p.52" in all_mat
