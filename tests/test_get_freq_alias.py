import pytest

from mosaic_traj.read_traj import get_freq_alias

@pytest.mark.parametrize(
    "n, result",
    [
        (1440, "1min"),
        (1, "D")
    ]
)
def test_get_freq_alias(n, result):
    """Test getting frequency alias."""
    assert get_freq_alias(n) == result, "Get frequency alias returned unexpected value"


@pytest.mark.parametrize(
    "obj",
    [
        None,
        3.141,
        "test",
        ["list", "of", "words"]
    ]
)
def test_get_freq_alias_error(obj):
    '''Test incorrect input to get frequency alias'''
    with pytest.raises(TypeError):
        get_freq_alias(obj)
