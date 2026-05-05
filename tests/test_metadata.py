"""Tests for the metadata module."""
from canteen.metadata import MetaData, MetaDataPlusRange, XYMetaData


def test_metadata_default_initialization():
    """Test MetaData initializes with empty defaults."""
    md = MetaData()
    assert md.name == ""
    assert md.description == ""


def test_metadata_with_values():
    """Test MetaData with custom name and description."""
    md = MetaData(name="TestMap", description="A test map")
    assert md.name == "TestMap"
    assert md.description == "A test map"


def test_metadataplusrange_with_custom_range():
    """Test MetaDataPlusRange with custom range values."""
    md = MetaDataPlusRange(
        name="PoolMap",
        description="Pool elevation to volume",
        range_=(0.0, 1000.0)
    )
    assert md.name == "PoolMap"
    assert md.description == "Pool elevation to volume"
    assert md.range_ == (0.0, 1000.0)


def test_xymetadata_complete():
    """Test XYMetaData with all fields populated."""
    md = XYMetaData(
        name="Outlet Curve",
        description="Flow vs elevation",
        xname="elevation",
        yname="flow",
        domain=(100.0, 200.0),
        range_=(0.0, 5000.0)
    )
    assert md.name == "Outlet Curve"
    assert md.description == "Flow vs elevation"
    assert md.xname == "elevation"
    assert md.yname == "flow"
    assert md.domain == (100.0, 200.0)
    assert md.range_ == (0.0, 5000.0)


def test_inheritance_chain():
    """Test that MetaDataPlusRange inherits from MetaData."""
    md = MetaDataPlusRange(name="Test", description="Desc")
    assert isinstance(md, MetaData)
    assert hasattr(md, 'range_')
