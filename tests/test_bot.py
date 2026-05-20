from datetime import UTC, datetime

from telegram import Chat, Message, MessageEntity
from telegram.constants import MessageEntityType

from security_bot.bot import (
    _extract_command_payload,
    _message_moderation_text,
    _shift_message_entities,
)
from security_bot.moderation import contains_blocked_url


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
