from types import SimpleNamespace

from app import ask as ask_module


def test_follow_up_questions_share_chat_history(monkeypatch):
    messages = []

    class FakeChat:
        def send_message(self, message):
            messages.append(message)
            return SimpleNamespace(text=f"answer {len(messages)}")

    chat = FakeChat()

    class FakeChats:
        def create(self, model):
            return chat

    class FakeClient:
        def __init__(self, api_key):
            self.chats = FakeChats()

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "What is MCP?"])
    prompts = iter(["Why is it useful?", "quit"])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))

    ask_module.main()

    assert messages == ["What is MCP?", "Why is it useful?"]


def test_ask_can_pass_temperature_config(monkeypatch):
    recorded = {}

    class FakeChat:
        def send_message(self, message, config=None):
            recorded["message"] = message
            recorded["config"] = config
            return SimpleNamespace(text="done")

    chat = FakeChat()

    result = ask_module.ask("What is MCP?", chat=chat, temperature=0.7)

    assert result == "done"
    assert recorded["message"] == "What is MCP?"
    assert recorded["config"].temperature == 0.7