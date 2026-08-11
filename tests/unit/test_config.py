from opslens.config import get_settings


def test_default_application_name() -> None:
    settings = get_settings()

    assert settings.app_name == "OpsLens API"
