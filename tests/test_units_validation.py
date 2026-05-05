"""Tests for the units_validation module."""
# pylint: disable=import-error,import-outside-toplevel,line-too-long
# import-error: optional units package not installed in CI
# import-outside-toplevel: intentional — verifies lazy module attribute presence
# line-too-long: optional-import lines with type-ignore comments exceed 100 chars

import importlib.util

import pytest


class TestUnitsValidationModuleExists:
    """Verify the units_validation module exists as a separate module."""

    def test_units_validation_module_is_importable(self):
        """canteen.units_validation must exist as a standalone module."""
        spec = importlib.util.find_spec("canteen.units_validation")
        assert spec is not None

    def test_units_aware_functions_not_in_validation(self):
        """Units-aware functions must not be importable from canteen.validation."""
        import canteen.validation as val
        assert not hasattr(val, "is_all_quantities")
        assert not hasattr(val, "is_all_volume_quantities")
        assert not hasattr(val, "is_same_unit_and_value_base")

    def test_units_aware_functions_in_units_validation(self):
        """Units-aware functions must be present in canteen.units_validation."""
        import canteen.units_validation as uv  # type: ignore[import-not-found]
        assert hasattr(uv, "is_all_quantities")
        assert hasattr(uv, "is_all_volume_quantities")
        assert hasattr(uv, "is_same_unit_and_value_base")


class TestUnitsValidationWithUnits:
    """Tests for units-aware validators — skipped when units is not installed."""

    @pytest.fixture(autouse=True)
    def require_units(self):
        """Skip all tests in this class if units package is not installed."""
        pytest.importorskip("units")

    def test_is_all_quantities_true_for_quantities(self):
        """is_all_quantities returns True when all values are Quantity instances."""
        from units import Quantity  # type: ignore[import-not-found]
        from units.unit import factory as unit_factory  # type: ignore[import-not-found]
        from units.named_unit import NamedUnit  # type: ignore[import-not-found]
        from canteen.units_validation import is_all_quantities  # type: ignore[import-not-found]

        q1 = Quantity(10, unit_factory(NamedUnit.CUBIC_METER))
        q2 = Quantity(20, unit_factory(NamedUnit.CUBIC_METER))

        assert is_all_quantities(q1, q2) is True

    def test_is_all_quantities_false_for_mixed(self):
        """is_all_quantities returns False when values are mixed types."""
        from units import Quantity  # type: ignore[import-not-found]
        from units.unit import factory as unit_factory  # type: ignore[import-not-found]
        from units.named_unit import NamedUnit  # type: ignore[import-not-found]
        from canteen.units_validation import is_all_quantities  # type: ignore[import-not-found]

        q1 = Quantity(10, unit_factory(NamedUnit.CUBIC_METER))

        assert is_all_quantities(q1, 20.0) is False

    def test_is_all_volume_quantities_true_for_volumes(self):
        """is_all_volume_quantities returns True when all values are volume Quantities."""
        from units import Quantity  # type: ignore[import-not-found]
        from units.unit import factory as unit_factory  # type: ignore[import-not-found]
        from units.named_unit import NamedUnit  # type: ignore[import-not-found]
        from canteen.units_validation import is_all_volume_quantities  # type: ignore[import-not-found]

        q = Quantity(10, unit_factory(NamedUnit.CUBIC_METER))

        assert is_all_volume_quantities(q) is True

    def test_is_same_unit_and_value_base_true_for_same_units(self):
        """is_same_unit_and_value_base returns True when quantities share units."""
        from units import Quantity  # type: ignore[import-not-found]
        from units.unit import factory as unit_factory  # type: ignore[import-not-found]
        from units.named_unit import NamedUnit  # type: ignore[import-not-found]
        from canteen.units_validation import is_same_unit_and_value_base  # type: ignore[import-not-found]

        q1 = Quantity(10, unit_factory(NamedUnit.CUBIC_METER))
        q2 = Quantity(20, unit_factory(NamedUnit.CUBIC_METER))

        assert is_same_unit_and_value_base(q1, q2) is True

    def test_is_same_unit_and_value_base_false_for_non_quantity(self):
        """is_same_unit_and_value_base returns False when first arg is not a Quantity."""
        from canteen.units_validation import is_same_unit_and_value_base  # type: ignore[import-not-found]

        assert is_same_unit_and_value_base(10.0, 20.0) is False
