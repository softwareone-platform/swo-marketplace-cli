from cli.core.stats import ErrorMessagesCollector


def test_status_is_empty():
    stats = ErrorMessagesCollector()

    assert stats.is_empty()


def test_status_is_not_empty():
    stats = ErrorMessagesCollector()
    stats.add_msg("Test", "Test Item", "test message")

    assert not stats.is_empty()


def test_stats_str():
    stats = ErrorMessagesCollector()

    stats.add_msg("Test", "Test Item", "test message")
    stats.add_msg("Test", "Test Item", "new message")

    assert str(stats) == "Test:\n\t\tTest Item: test message, new message"


def test_stats_str_with_empty_item():
    stats = ErrorMessagesCollector()

    stats.add_msg("Test", "Test Item", "test message")
    stats.add_msg("Test", "", "new message")

    assert str(stats) == "Test: new message\n\t\tTest Item: test message"
