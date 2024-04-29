from swo.mpt.cli.core.stats import StatsCollector


def test_stats_add_msg():
    stats = StatsCollector()

    stats.add_msg("Test", "Test Item", "test message")

    assert stats._sections == {"Test": {"Test Item": ["test message"]}}


def test_status_is_empty():
    stats = StatsCollector()

    assert stats.is_empty()


def test_status_is_not_empty():
    stats = StatsCollector()
    stats.add_msg("Test", "Test Item", "test message")

    assert not stats.is_empty()


def test_stats_add_one_more_msg():
    stats = StatsCollector()

    stats.add_msg("Test", "Test Item", "test message")
    stats.add_msg("Test", "Test Item", "new message")

    assert stats._sections == {"Test": {"Test Item": ["test message", "new message"]}}


def test_stats_str():
    stats = StatsCollector()

    stats.add_msg("Test", "Test Item", "test message")
    stats.add_msg("Test", "Test Item", "new message")

    assert str(stats) == "Test:\n\t\tTest Item: test message, new message"


def test_stats_str_with_empty_item():
    stats = StatsCollector()

    stats.add_msg("Test", "Test Item", "test message")
    stats.add_msg("Test", "", "new message")

    assert str(stats) == "Test: new message\n\t\tTest Item: test message"
