"""Tests for geospatial API endpoints."""

import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from app.db.models import Project, SurveyPoint, Parcel, Client
from app.db.models_drone import DroneFlight, DronePhoto, DroneFlightStatus


def test_project_map_data(client_token, client, db, test_organization_id):
    """Test retrieving complete map data for a project."""
    client_record = db.query(Client).first()
    project = Project(
        id=uuid4(),
        organization_id=test_organization_id,
        code="TEST-MAP-001",
        name="Test Map Project",
        client_id=client_record.id,
        location=None,
        status="completed"
    )
    db.add(project)
    db.commit()

    response = client.get(
        f"/api/v1/geospatial/projects/{project.id}/map-data",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert "project_name" in data
    assert "survey_points" in data
    assert "parcels" in data
    assert "drone_coverage" in data
    assert isinstance(data["survey_points"], list)


def test_project_map_data_not_found(client_token, client):
    """Test map data for non-existent project."""
    fake_id = uuid4()
    response = client.get(
        f"/api/v1/geospatial/projects/{fake_id}/map-data",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 404


def test_project_bounds(client_token, client, db, test_organization_id, test_user_id):
    """Test retrieving project geographic bounds."""
    client_record = db.query(Client).first()
    project = Project(
        id=uuid4(),
        organization_id=test_organization_id,
        code="TEST-BOUNDS-001",
        name="Test Bounds Project",
        client_id=client_record.id,
        location=None,
        status="completed"
    )
    db.add(project)
    db.commit()

    survey_point = SurveyPoint(
        id=uuid4(),
        project_id=project.id,
        point_number="P001",
        east=Decimal("19.0000"),
        north=Decimal("-69.0000"),
        elevation=Decimal("100.00"),
        geometry=None,
        created_by_user_id=test_user_id
    )
    db.add(survey_point)
    db.commit()

    response = client.get(
        f"/api/v1/geospatial/projects/{project.id}/bounds",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "north" in data
    assert "south" in data
    assert "east" in data
    assert "west" in data
    assert isinstance(data["north"], float)


def test_survey_points_geojson(client_token, client, db, test_organization_id, test_user_id):
    """Test retrieving survey points as GeoJSON."""
    client_record = db.query(Client).first()
    project = Project(
        id=uuid4(),
        organization_id=test_organization_id,
        code="TEST-POINTS-001",
        name="Test Points Project",
        client_id=client_record.id,
        location=None,
        status="completed"
    )
    db.add(project)
    db.commit()

    for i in range(3):
        point = SurveyPoint(
            id=uuid4(),
            project_id=project.id,
            point_number=f"P{i:03d}",
            east=Decimal(f"19.{i}"),
            north=Decimal(f"-69.{i}"),
            elevation=Decimal(f"{100 + i * 10}.00"),
            geometry=None,
            created_by_user_id=test_user_id
        )
        db.add(point)
    db.commit()

    response = client.get(
        f"/api/v1/geospatial/projects/{project.id}/survey-points-geojson",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 3
    for feature in data["features"]:
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        assert "properties" in feature
        assert feature["properties"]["type"] == "survey_point"


def test_parcels_geojson(client_token, client, db, test_organization_id):
    """Test retrieving parcels as GeoJSON."""
    client_record = db.query(Client).first()
    project = Project(
        id=uuid4(),
        organization_id=test_organization_id,
        code="TEST-PARCELS-001",
        name="Test Parcels Project",
        client_id=client_record.id,
        location=None,
        status="completed"
    )
    db.add(project)
    db.commit()

    for i in range(2):
        parcel = Parcel(
            id=uuid4(),
            project_id=project.id,
            parcel_number=f"PAR-{i:03d}",
            owner_name=f"Owner {i}",
            area=Decimal("1000.00"),
            municipality="Santo Domingo",
            province="Santo Domingo"
        )
        db.add(parcel)
    db.commit()

    response = client.get(
        f"/api/v1/geospatial/projects/{project.id}/parcels-geojson",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2
    for feature in data["features"]:
        assert feature["properties"]["type"] == "parcel"
        assert "parcel_number" in feature["properties"]


def test_drone_coverage_geojson(client_token, client, db, test_organization_id):
    """Test retrieving drone coverage as GeoJSON."""
    client_record = db.query(Client).first()
    project = Project(
        id=uuid4(),
        organization_id=test_organization_id,
        code="TEST-DRONE-001",
        name="Test Drone Project",
        client_id=client_record.id,
        location=None,
        status="completed"
    )
    db.add(project)
    db.commit()

    flight = DroneFlight(
        id="flight-001",
        organization_id=str(test_organization_id),
        project_id=str(project.id),
        flight_name="Test Flight",
        flight_date=datetime.utcnow(),
        status=DroneFlightStatus.COMPLETED,
        altitude_meters=100.0,
        area_coverage_hectares=50.0,
        ground_resolution_cm=2.5,
        total_photos=100
    )
    db.add(flight)
    db.commit()

    for i in range(4):
        photo = DronePhoto(
            id=f"photo-{i:03d}",
            organization_id=str(test_organization_id),
            flight_id="flight-001",
            photo_name=f"photo_{i}.jpg",
            photo_url=f"https://example.com/photos/{i}.jpg",
            gps_latitude=19.0 + (i * 0.001),
            gps_longitude=-69.0 + (i * 0.001),
            gps_altitude_meters=100.0
        )
        db.add(photo)
    db.commit()

    response = client.get(
        f"/api/v1/geospatial/projects/{project.id}/drone-coverage-geojson",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0
    for feature in data["features"]:
        assert feature["properties"]["type"] == "drone_coverage"


def test_all_map_features(client_token, client, db, test_organization_id, test_user_id):
    """Test retrieving all map features combined."""
    client_record = db.query(Client).first()
    project = Project(
        id=uuid4(),
        organization_id=test_organization_id,
        code="TEST-ALL-001",
        name="Test All Features Project",
        client_id=client_record.id,
        location=None,
        status="completed"
    )
    db.add(project)
    db.commit()

    survey_point = SurveyPoint(
        id=uuid4(),
        project_id=project.id,
        point_number="P001",
        east=Decimal("19.0000"),
        north=Decimal("-69.0000"),
        geometry=None,
        created_by_user_id=test_user_id
    )
    db.add(survey_point)

    parcel = Parcel(
        id=uuid4(),
        project_id=project.id,
        parcel_number="PAR-001",
        owner_name="Test Owner",
        area=Decimal("1000.00")
    )
    db.add(parcel)
    db.commit()

    response = client.get(
        f"/api/v1/geospatial/projects/{project.id}/map-features",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "survey_points" in data
    assert "parcels" in data
    assert "drone_coverage" in data
    assert data["survey_points"]["type"] == "FeatureCollection"
    assert data["parcels"]["type"] == "FeatureCollection"


def test_map_requires_authentication(client):
    """Test map endpoints require authentication."""
    fake_id = uuid4()
    endpoints = [
        f"/api/v1/geospatial/projects/{fake_id}/map-data",
        f"/api/v1/geospatial/projects/{fake_id}/bounds",
        f"/api/v1/geospatial/projects/{fake_id}/survey-points-geojson",
        f"/api/v1/geospatial/projects/{fake_id}/parcels-geojson",
        f"/api/v1/geospatial/projects/{fake_id}/drone-coverage-geojson",
        f"/api/v1/geospatial/projects/{fake_id}/map-features",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401
