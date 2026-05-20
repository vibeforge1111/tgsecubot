from security_bot.storage import SettingsStore


def test_store_persists_warning_settings(tmp_path):
    data_file = tmp_path / "settings.json"
    store = SettingsStore(data_file)
    settings = store.chat(-100123)
    settings.warning_enabled = True
    settings.warning_text = "Stay alert"
    settings.warning_freq_seconds = 600
    settings.warning_media_type = "photo"
    settings.warning_media_file_id = "photo-file-id"
    settings.warning_entities = [{"type": "bold", "offset": 0, "length": 4}]
    store.save()

    loaded = SettingsStore(data_file).chat(-100123)

    assert loaded.warning_enabled is True
    assert loaded.warning_text == "Stay alert"
    assert loaded.warning_freq_seconds == 600
    assert loaded.warning_media_type == "photo"
    assert loaded.warning_media_file_id == "photo-file-id"
    assert loaded.warning_entities == [{"type": "bold", "offset": 0, "length": 4}]


def test_store_ignores_malformed_warning_entities(tmp_path):
    data_file = tmp_path / "settings.json"
    data_file.write_text(
        """
        {
          "-100123": {
            "warning_entities": [
              {"type": "bold", "offset": 0, "length": 4},
              {"type": "italic", "offset": "bad", "length": 6},
              "invalid"
            ]
          }
        }
        """,
        encoding="utf-8",
    )

    loaded = SettingsStore(data_file).chat(-100123)

    assert loaded.warning_entities == [{"type": "bold", "offset": 0, "length": 4}]
