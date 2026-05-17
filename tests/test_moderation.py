import pytest

from security_bot.moderation import (
    contains_blocked_url,
    contains_evm_address,
    extract_urls,
    host_allowed,
    name_matches_keywords,
    normalize_domain,
)


def test_normalize_domain_accepts_plain_domain_and_urls():
    assert normalize_domain("x.com") == "x.com"
    assert normalize_domain("https://www.x.com/path") == "x.com"


def test_normalize_domain_rejects_invalid_values():
    with pytest.raises(ValueError):
        normalize_domain("not-a-domain")


def test_host_allowed_matches_domain_and_subdomains():
    assert host_allowed("x.com", ["x.com"])
    assert host_allowed("mobile.x.com", ["x.com"])
    assert not host_allowed("evilx.com", ["x.com"])


def test_extract_urls_finds_domains_and_schemed_urls():
    urls = extract_urls("see https://example.com/a and www.x.com and test.org.")
    assert [url.host for url in urls] == ["example.com", "x.com", "test.org"]


def test_contains_blocked_url_ignores_allowed_domains():
    assert not contains_blocked_url("go to https://x.com/profile", ["x.com"])
    assert contains_blocked_url("go to https://example.com", ["x.com"])


def test_contains_evm_address_detects_address_like_text():
    assert contains_evm_address("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    assert not contains_evm_address("0x1234")


def test_name_matches_keywords_case_insensitive():
    assert name_matches_keywords("Meta Support", ["meta"])
    assert not name_matches_keywords("Regular User", ["meta"])
