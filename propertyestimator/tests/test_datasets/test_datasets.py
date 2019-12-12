"""
Units tests for propertyestimator.datasets
"""
import json

from propertyestimator import unit
from propertyestimator.datasets import (
    CalculationSource,
    PhysicalPropertyDataSet,
    PropertyPhase,
)
from propertyestimator.properties import (
    Density,
    DielectricConstant,
    EnthalpyOfMixing,
    ExcessMolarVolume,
)
from propertyestimator.substances import Substance
from propertyestimator.tests.utils import (
    create_dummy_property,
    create_filterable_data_set,
)
from propertyestimator.thermodynamics import ThermodynamicState
from propertyestimator.utils.serialization import TypedJSONEncoder


def test_physical_property_state_methods():

    dummy_property = create_dummy_property(Density)
    property_state = dummy_property.__getstate__()

    recreated_property = Density()
    recreated_property.__setstate__(property_state)

    recreated_state = recreated_property.__getstate__()

    original_json = json.dumps(property_state, cls=TypedJSONEncoder)
    recreated_json = json.dumps(recreated_state, cls=TypedJSONEncoder)

    assert original_json == recreated_json


def test_physical_property_id_generation():

    dummy_property_1 = create_dummy_property(Density)
    dummy_property_2 = create_dummy_property(Density)

    assert dummy_property_1.id != dummy_property_2.id


def test_serialization():
    """A test to ensure that data sets are JSON serializable."""

    data_set = PhysicalPropertyDataSet()
    data_set.add_property(create_dummy_property(Density))

    data_set_json = data_set.json()

    parsed_data_set = PhysicalPropertyDataSet.parse_json(data_set_json)
    assert data_set.number_of_properties == parsed_data_set.number_of_properties

    parsed_data_set_json = parsed_data_set.json()
    assert parsed_data_set_json == data_set_json


def test_to_pandas():
    """A test to ensure that data sets are convertable to pandas objects."""

    source = CalculationSource("Dummy", {})

    pure_substance = Substance.from_components("C")
    binary_substance = Substance.from_components("C", "O")

    data_set = PhysicalPropertyDataSet()

    for temperature in [298 * unit.kelvin, 300 * unit.kelvin, 302 * unit.kelvin]:

        thermodynamic_state = ThermodynamicState(
            temperature=temperature, pressure=1.0 * unit.atmosphere
        )

        density_property = Density(
            thermodynamic_state=thermodynamic_state,
            phase=PropertyPhase.Liquid,
            substance=pure_substance,
            value=1 * unit.gram / unit.milliliter,
            uncertainty=0.11 * unit.gram / unit.milliliter,
            source=source,
        )

        dielectric_property = DielectricConstant(
            thermodynamic_state=thermodynamic_state,
            phase=PropertyPhase.Liquid,
            substance=pure_substance,
            value=1 * unit.dimensionless,
            uncertainty=0.11 * unit.dimensionless,
            source=source,
        )

        data_set.add_property(density_property)
        data_set.add_property(dielectric_property)

    for temperature in [298 * unit.kelvin, 300 * unit.kelvin, 302 * unit.kelvin]:

        thermodynamic_state = ThermodynamicState(
            temperature=temperature, pressure=1.0 * unit.atmosphere
        )

        enthalpy_property = EnthalpyOfMixing(
            thermodynamic_state=thermodynamic_state,
            phase=PropertyPhase.Liquid,
            substance=binary_substance,
            value=1 * unit.kilojoules / unit.mole,
            uncertainty=0.11 * unit.kilojoules / unit.mole,
            source=source,
        )

        excess_property = ExcessMolarVolume(
            thermodynamic_state=thermodynamic_state,
            phase=PropertyPhase.Liquid,
            substance=binary_substance,
            value=1 * unit.meter ** 3 / unit.mole,
            uncertainty=0.11 * unit.meter ** 3 / unit.mole,
            source=source,
        )

        data_set.add_property(enthalpy_property)
        data_set.add_property(excess_property)

    data_set_pandas = data_set.to_pandas()

    assert data_set_pandas is not None
    assert len(data_set_pandas) == 6


def test_filter_by_property_types():
    """A test to ensure that data sets may be filtered by property type."""

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_property_types("Density")

    assert dummy_data_set.number_of_properties == 1

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_property_types("Density", "DielectricConstant")

    assert dummy_data_set.number_of_properties == 2


def test_filter_by_phases():
    """A test to ensure that data sets may be filtered by phases."""

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_phases(phases=PropertyPhase.Liquid)

    assert dummy_data_set.number_of_properties == 1

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_phases(
        phases=PropertyPhase(PropertyPhase.Liquid | PropertyPhase.Solid)
    )

    assert dummy_data_set.number_of_properties == 2

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_phases(
        phases=PropertyPhase(
            PropertyPhase.Liquid | PropertyPhase.Solid | PropertyPhase.Gas
        )
    )

    assert dummy_data_set.number_of_properties == 3


def test_filter_by_temperature():
    """A test to ensure that data sets may be filtered by temperature."""

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_temperature(
        min_temperature=287 * unit.kelvin, max_temperature=289 * unit.kelvin
    )

    assert dummy_data_set.number_of_properties == 1

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_temperature(
        min_temperature=287 * unit.kelvin, max_temperature=299 * unit.kelvin
    )

    assert dummy_data_set.number_of_properties == 2

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_temperature(
        min_temperature=287 * unit.kelvin, max_temperature=309 * unit.kelvin
    )

    assert dummy_data_set.number_of_properties == 3


def test_filter_by_pressure():
    """A test to ensure that data sets may be filtered by pressure."""

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_pressure(
        min_pressure=0.4 * unit.atmosphere, max_pressure=0.6 * unit.atmosphere
    )

    assert dummy_data_set.number_of_properties == 1

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_pressure(
        min_pressure=0.4 * unit.atmosphere, max_pressure=1.1 * unit.atmosphere
    )

    assert dummy_data_set.number_of_properties == 2

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_pressure(
        min_pressure=0.4 * unit.atmosphere, max_pressure=1.6 * unit.atmosphere
    )

    assert dummy_data_set.number_of_properties == 3


def test_filter_by_components():
    """A test to ensure that data sets may be filtered by the number of components."""

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_components(number_of_components=1)

    assert dummy_data_set.number_of_properties == 1

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_components(number_of_components=2)

    assert dummy_data_set.number_of_properties == 1

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_components(number_of_components=3)

    assert dummy_data_set.number_of_properties == 1


def test_filter_by_elements():
    """A test to ensure that data sets may be filtered by which elements their
    measured properties contain."""

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_elements("H", "C")

    assert dummy_data_set.number_of_properties == 1

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_elements("H", "C", "N")

    assert dummy_data_set.number_of_properties == 2

    dummy_data_set = create_filterable_data_set()
    dummy_data_set.filter_by_elements("H", "C", "N", "O")

    assert dummy_data_set.number_of_properties == 3


def test_filter_by_smiles():
    """A test to ensure that data sets may be filtered by which smiles their
    measured properties contain."""

    methanol_substance = Substance()
    methanol_substance.add_component(
        Substance.Component("CO"), Substance.MoleFraction(1.0)
    )

    ethanol_substance = Substance()
    ethanol_substance.add_component(
        Substance.Component("CCO"), Substance.MoleFraction(1.0)
    )

    property_a = create_dummy_property(Density)
    property_a.substance = methanol_substance

    property_b = create_dummy_property(Density)
    property_b.substance = ethanol_substance

    data_set = PhysicalPropertyDataSet()
    data_set.properties[methanol_substance.identifier] = [property_a]
    data_set.properties[ethanol_substance.identifier] = [property_b]

    data_set.filter_by_smiles("CO")

    assert data_set.number_of_properties == 1
    assert methanol_substance.identifier in data_set.properties
    assert ethanol_substance.identifier not in data_set.properties
