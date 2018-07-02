from uiucprescon.imagevalidate import messages, report


def test_invalid_data():
    message_generator = messages.MessageGenerator(
        strategy=messages.InvalidData())

    new_message = message_generator.generate_message(
        field="spam",
        data=report.Result(expected="bacon", actual="eggs")
    )
    assert new_message == 'Invalid match for "spam". ' \
                          'Expected: "bacon". Got: "eggs".'


def test_empty_data():
    message_generator = messages.MessageGenerator(
        strategy=messages.EmptyData())

    new_message = message_generator.generate_message(
        field="spam",
        data=report.Result(expected="bacon", actual="")
    )
    assert new_message == 'The "spam" field exists but contains no data.'


def test_missing_field():
    message_generator = messages.MessageGenerator(
        strategy=messages.MissingField())

    new_message = message_generator.generate_message(
        field="spam",
        data=report.Result(expected="bacon", actual=None)
    )
    assert new_message == 'No metadata field for "spam" found in file.'
