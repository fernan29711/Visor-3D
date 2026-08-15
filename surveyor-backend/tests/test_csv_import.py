"""CSV import tests."""

import pytest
from app.api.v1.survey_points.csv_import import CSVImportParser

def test_parse_csv_basic():
    """Test basic CSV parsing."""
    csv_content = """point_number,east,north,elevation
P-001,327845.236,2165487.421,82.436
P-002,327850.123,2165490.456,83.120
P-003,327855.789,2165495.789,83.890
"""
    parser = CSVImportParser()
    points = parser.parse_csv(csv_content)

    assert len(points) == 3
    assert points[0]['point_number'] == 'P-001'
    assert points[0]['east'] == 327845.236
    assert points[0]['north'] == 2165487.421
    assert points[0]['elevation'] == 82.436

def test_parse_csv_alternative_columns():
    """Test CSV parsing with alternative column names."""
    csv_content = """ID,X,Y,Z
P-001,327845.236,2165487.421,82.436
P-002,327850.123,2165490.456,83.120
"""
    parser = CSVImportParser()
    points = parser.parse_csv(csv_content)

    assert len(points) == 2
    assert points[0]['point_number'] == 'P-001'
    assert points[0]['east'] == 327845.236

def test_parse_csv_with_gnss_metadata():
    """Test CSV parsing with GNSS metadata."""
    csv_content = """point_number,east,north,elevation,PDOP,HDOP,VDOP,Satellites
P-001,327845.236,2165487.421,82.436,2.5,1.8,2.0,12
P-002,327850.123,2165490.456,83.120,2.3,1.6,1.9,13
"""
    parser = CSVImportParser()
    points = parser.parse_csv(csv_content)

    assert len(points) == 2
    assert points[0]['pdop'] == 2.5
    assert points[0]['hdop'] == 1.8
    assert points[0]['satellite_count'] == 12

def test_validate_points_valid():
    """Test validation with valid points."""
    points = [
        {'point_number': 'P-001', 'east': 327845.236, 'north': 2165487.421, 'elevation': 82.436},
        {'point_number': 'P-002', 'east': 327850.123, 'north': 2165490.456, 'elevation': 83.120},
    ]
    parser = CSVImportParser()
    result = parser.validate_points(points)

    assert result['valid'] == True
    assert result['valid_count'] == 2
    assert result['error_count'] == 0
    assert len(result['errors']) == 0

def test_validate_points_missing_point_number():
    """Test validation with missing point numbers."""
    points = [
        {'point_number': '', 'east': 327845.236, 'north': 2165487.421, 'elevation': 82.436},
        {'point_number': 'P-002', 'east': 327850.123, 'north': 2165490.456, 'elevation': 83.120},
    ]
    parser = CSVImportParser()
    result = parser.validate_points(points)

    assert result['valid'] == False
    assert result['valid_count'] == 1
    assert result['error_count'] == 1

def test_validate_points_invalid_coordinates():
    """Test validation with invalid coordinates."""
    points = [
        {'point_number': 'P-001', 'east': 'invalid', 'north': 2165487.421, 'elevation': 82.436},
        {'point_number': 'P-002', 'east': 327850.123, 'north': 2165490.456, 'elevation': 83.120},
    ]
    parser = CSVImportParser()
    result = parser.validate_points(points)

    assert result['valid'] == False
    assert result['valid_count'] == 1
    assert result['error_count'] == 1

def test_parse_csv_with_delimiter():
    """Test CSV parsing with semicolon delimiter."""
    csv_content = """point_number;east;north;elevation
P-001;327845.236;2165487.421;82.436
P-002;327850.123;2165490.456;83.120
"""
    parser = CSVImportParser()
    points = parser.parse_csv(csv_content, delimiter=';')

    assert len(points) == 2
    assert points[0]['point_number'] == 'P-001'
    assert points[0]['east'] == 327845.236
