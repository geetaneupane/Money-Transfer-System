from app.core.config import Settings


def test_default_settings()->None:
    settings=Settings()

    assert settings is not None
    


