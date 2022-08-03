from gkeepclient.duration_to_string import duration_to_string


def test_duration_to_string():
    assert duration_to_string(0) == '0s'

    assert duration_to_string(59) == '59s'
    assert duration_to_string(60) == '1m0s'
    assert duration_to_string(61) == '1m1s'

    assert duration_to_string(60 * 60 - 1) == '59m59s'
    assert duration_to_string(60 * 60) == '1h0m0s'
    assert duration_to_string(60 * 60 + 1) == '1h0m1s'

    assert duration_to_string(24 * 60 * 60 - 1) == '23h59m59s'
    assert duration_to_string(24 * 60 * 60) == '1d0h0m0s'
    assert duration_to_string(24 * 60 * 60 + 1) == '1d0h0m1s'
