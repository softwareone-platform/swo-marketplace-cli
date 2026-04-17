from cli.core.stats import ErrorMessagesCollector, PriceListStatsCollector


def test_status_is_empty():
    stats = ErrorMessagesCollector()

    result = stats.is_empty()

    assert result is True


def test_status_is_not_empty():
    stats = ErrorMessagesCollector()
    stats.add_msg("Test", "Test Item", "test message")

    result = stats.is_empty()

    assert result is False


def test_stats_str():
    stats = ErrorMessagesCollector()
    stats.add_msg("Test", "Test Item", "test message")
    stats.add_msg("Test", "Test Item", "new message")

    result = str(stats)

    assert result == "Test:\n\t\tTest Item: test message, new message"


def test_stats_str_with_empty_item():
    stats = ErrorMessagesCollector()
    stats.add_msg("Test", "Test Item", "test message")
    stats.add_msg("Test", "", "new message")

    result = str(stats)

    assert result == "Test: new message\n\t\tTest Item: test message"


def test_stats_collectors_do_not_share_errors():
    first_collector = PriceListStatsCollector()
    second_collector = PriceListStatsCollector()
    first_collector.errors.add_msg("General", "Item", "error")

    result = second_collector.errors.is_empty()

    assert result is True
