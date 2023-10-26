import pytest

from mosaic_traj.thermo import equ_pot

@pytest.mark.parametrize(
    "t, q, p, result",
    [
        (273, 0, 1000, 273),
    ]
)
def test_equ_pot(t, q, p, result):
    """Test equivalent potential temperature calculation."""
    assert equ_pot(t, q, p) == pytest.approx(result), "Equivalent potential tempature calculation returned unexpected value"


@pytest.mark.parametrize(
    "t, q, p",
    [
        (273, -1, 1000),  # invalid specific humidity
        (273, 1, 1000),  # invalid specific humidity
        (273, 0.018, 0),  # invalid pressure
        (0, 0.018, 1000),  # invalid temperature
    ]
)
def test_equ_pot_error(t, q, p):
    '''Test incorrect input to equivalent potential temperature calculation.'''
    with pytest.raises(ValueError):
        equ_pot(t, q, p)
