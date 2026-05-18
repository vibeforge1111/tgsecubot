from datetime import UTC, datetime

from telegram import Chat, Message, MessageEntity
from telegram.constants import MessageEntityType

from security_bot.bot import _message_moderation_text
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
