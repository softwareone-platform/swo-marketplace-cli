import pytest


@pytest.fixture(autouse=True)
def mock_mpt_client(mocker, active_operations_account):
    mocks = {
        module_name: mocker.patch(
            f"cli.core.price_lists.app.{module_name}.CLIMPTClient", autospec=True
        )
        for module_name in ("export", "sync")
    }
    for module_mock in mocks.values():
        module_mock.return_value.mpt_account = active_operations_account
    return mocks
