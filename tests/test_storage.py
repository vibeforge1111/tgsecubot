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
    store.save()

    loaded = SettingsStore(data_file).chat(-100123)

    assert loaded.warning_enabled is True
    assert loaded.warning_text == "Stay alert"
    assert loaded.warning_freq_seconds == 600
    assert loaded.warning_media_type == "photo"
    assert loaded.warning_media_file_id == "photo-file-id"
