import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telegram import Chat, Message, MessageEntity
from telegram.constants import MessageEntityType

from security_bot.bot import (
    _extract_command_payload,
    _message_moderation_text,
    _shift_message_entities,
    send_warning_message,
)
from security_bot.moderation import contains_blocked_url
from security_bot.storage import SettingsStore


def _message(**kwargs) -> Message:
    return Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=Chat(id=-100123, type=Chat.GROUP),
        **kwargs,
    )


def test_message_moderation_text_includes_hidden_text_link_url():
    message = _message(
        text="click here",
        entities=[
            MessageEntity(
                type=MessageEntityType.TEXT_LINK,
                offset=0,
                length=5,
                url="https://evil.example/path",
            )
        ],
    )

    text = _message_moderation_text(message)

    assert "https://evil.example/path" in text
    assert contains_blocked_url(text, allowed_domains=[])


def test_message_moderation_text_includes_caption_url_entities():
    url = "https://evil.example/path"
    message = _message(
        caption=f"photo {url}",
        caption_entities=[
            MessageEntity(
                type=MessageEntityType.URL,
                offset=len("photo "),
                length=len(url),
            )
        ],
    )

    text = _message_moderation_text(message)

    assert url in text
    assert contains_blocked_url(text, allowed_domains=[])


def test_extract_command_payload_preserves_newlines():
    text, offset = _extract_command_payload("/warningtxt First line\nSecond line")

    assert text == "First line\nSecond line"
    assert offset == len("/warningtxt ")


def test_shift_message_entities_keeps_formatting_and_links_only():
    payload_start = len("/warningtxt ")
    url = "https://example.com"
    message = _message(
        text="/warningtxt bold link @user",
        entities=[
            MessageEntity(type=MessageEntityType.BOT_COMMAND, offset=0, length=len("/warningtxt")),
            MessageEntity(type=MessageEntityType.BOLD, offset=payload_start, length=len("bold")),
            MessageEntity(
                type=MessageEntityType.TEXT_LINK,
                offset=payload_start + len("bold "),
                length=4,
                url=url,
            ),
            MessageEntity(
                type=MessageEntityType.MENTION,
                offset=payload_start + len("bold link "),
                length=5,
            ),
        ],
    )

    entities = _shift_message_entities(message, payload_start)

    assert entities == [
        {"type": MessageEntityType.BOLD, "offset": 0, "length": 4},
        {"type": MessageEntityType.TEXT_LINK, "offset": 5, "length": 4, "url": url},
    ]


def test_send_warning_message_deletes_previous_and_records_new_id(tmp_path):
    data_file = tmp_path / "settings.json"
    store = SettingsStore(data_file)
    settings = store.chat(-100123)
    settings.warning_enabled = True
    settings.warning_text = "Stay alert"
    settings.warning_message_ids = [111]
    store.save()
    bot = SimpleNamespace(
        delete_message=AsyncMock(),
        send_message=AsyncMock(return_value=SimpleNamespace(message_id=222)),
    )
    context = SimpleNamespace(
        application=SimpleNamespace(bot_data={"store": store}),
        bot=bot,
        job=SimpleNamespace(data={"chat_id": -100123}),
    )

    asyncio.run(send_warning_message(context))

    bot.delete_message.assert_awaited_once_with(chat_id=-100123, message_id=111)
    bot.send_message.assert_awaited_once_with(chat_id=-100123, text="Stay alert", entities=None)
    assert SettingsStore(data_file).chat(-100123).warning_message_ids == [222]
