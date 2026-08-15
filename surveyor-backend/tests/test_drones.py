"""Tests for drone flight and 3D model endpoints."""

import pytest
from datetime import datetime
from app.api.v1.drones.routes import router
from app.db.models_drone import DroneFlight, DronePhoto, Model3D, DroneFlightStatus
from app.schemas.drones import (
    DroneFlightCreate,
    DronePhotoCreate,
    Model3DCreate,
)


@pytest.fixture
def drone_flight_data():
    """Sample drone flight data."""
    return {
        "flight_name": "Survey Flight 1",
        "drone_model": "DJI Phantom 4 Pro",
        "pilot_name": "John Doe",
        "flight_date": datetime.utcnow().isoformat(),
        "flight_duration_minutes": 45,
        "altitude_meters": 120,
        "area_coverage_hectares": 50.5,
        "ground_resolution_cm": 2.5,
        "weather_conditions": "Clear skies",
        "notes": "Initial survey flight",
    }


@pytest.fixture
def drone_photo_data():
    """Sample drone photo data."""
    return {
        "photo_name": "IMG_0001.jpg",
        "photo_url": "https://example.com/photos/IMG_0001.jpg",
        "thumbnail_url": "https://example.com/photos/IMG_0001_thumb.jpg",
        "file_size_mb": 5.2,
        "resolution_width": 5472,
        "resolution_height": 3648,
        "gps_latitude": 18.9712,
        "gps_longitude": -70.6404,
        "gps_altitude_meters": 120,
        "capture_time": datetime.utcnow().isoformat(),
        "notes": "Test photo",
    }


@pytest.fixture
def model_3d_data(test_flight_id):
    """Sample 3D model data."""
    return {
        "flight_id": test_flight_id,
        "model_name": "Orthomosaic Model 1",
        "model_type": "orthomosaic",
        "file_format": "geotiff",
        "file_url": "https://example.com/models/model_1.tif",
        "coverage_area_hectares": 50.5,
        "resolution_cm": 2.5,
        "coordinate_system": "WGS84",
        "min_elevation": 100,
        "max_elevation": 250,
    }


def test_create_flight(admin_token, client):
    """Test creating a drone flight."""
    response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["flight_name"] == "Test Flight"
    assert data["drone_model"] == "DJI Phantom 4"
    assert data["status"] == "completed"
    assert "id" in data
    assert "created_at" in data


def test_list_flights(admin_token, client):
    """Test listing drone flights."""
    response = client.get(
        "/api/v1/drones/flights",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_flights_with_pagination(admin_token, client):
    """Test listing flights with skip and limit."""
    response = client.get(
        "/api/v1/drones/flights?skip=0&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_flight(admin_token, client):
    """Test getting a specific flight."""
    # First create a flight
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Get the flight
    response = client.get(
        f"/api/v1/drones/flights/{flight_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == flight_id
    assert data["flight_name"] == "Test Flight"
    assert "photos" in data


def test_update_flight(admin_token, client):
    """Test updating a flight."""
    # Create a flight
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Update the flight
    response = client.patch(
        f"/api/v1/drones/flights/{flight_id}",
        json={
            "flight_name": "Updated Flight",
            "status": "completed",
            "total_photos": 150,
            "processed_photos": 150,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["flight_name"] == "Updated Flight"
    assert data["total_photos"] == 150


def test_delete_flight(admin_token, client):
    """Test deleting a flight."""
    # Create a flight
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Delete the flight
    response = client.delete(
        f"/api/v1/drones/flights/{flight_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204


def test_add_photo_to_flight(admin_token, client):
    """Test adding a photo to a flight."""
    # Create a flight first
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Add a photo
    response = client.post(
        f"/api/v1/drones/flights/{flight_id}/photos",
        json={
            "photo_name": "IMG_0001.jpg",
            "photo_url": "https://example.com/photos/IMG_0001.jpg",
            "thumbnail_url": "https://example.com/photos/IMG_0001_thumb.jpg",
            "file_size_mb": 5.2,
            "resolution_width": 5472,
            "resolution_height": 3648,
            "gps_latitude": 18.9712,
            "gps_longitude": -70.6404,
            "gps_altitude_meters": 120,
            "capture_time": "2024-01-15T10:05:00",
            "notes": "Test photo",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["photo_name"] == "IMG_0001.jpg"
    assert data["flight_id"] == flight_id
    assert data["gps_latitude"] == 18.9712


def test_get_flight_photos(admin_token, client):
    """Test getting photos for a flight."""
    # Create a flight
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Add a photo
    client.post(
        f"/api/v1/drones/flights/{flight_id}/photos",
        json={
            "photo_name": "IMG_0001.jpg",
            "photo_url": "https://example.com/photos/IMG_0001.jpg",
            "file_size_mb": 5.2,
            "resolution_width": 5472,
            "resolution_height": 3648,
            "gps_latitude": 18.9712,
            "gps_longitude": -70.6404,
            "gps_altitude_meters": 120,
            "capture_time": "2024-01-15T10:05:00",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Get photos
    response = client.get(
        f"/api/v1/drones/flights/{flight_id}/photos",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_create_3d_model(admin_token, client):
    """Test creating a 3D model."""
    # Create a flight first
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Create 3D model
    response = client.post(
        "/api/v1/drones/models-3d",
        json={
            "flight_id": flight_id,
            "model_name": "Orthomosaic Model 1",
            "model_type": "orthomosaic",
            "file_format": "geotiff",
            "file_url": "https://example.com/models/model_1.tif",
            "coverage_area_hectares": 25.0,
            "resolution_cm": 2.5,
            "coordinate_system": "WGS84",
            "min_elevation": 100,
            "max_elevation": 250,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["model_name"] == "Orthomosaic Model 1"
    assert data["model_type"] == "orthomosaic"
    assert data["flight_id"] == flight_id


def test_get_flight_3d_models(admin_token, client):
    """Test getting 3D models for a flight."""
    # Create a flight
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Create 3D model
    client.post(
        "/api/v1/drones/models-3d",
        json={
            "flight_id": flight_id,
            "model_name": "Orthomosaic Model 1",
            "model_type": "orthomosaic",
            "file_format": "geotiff",
            "file_url": "https://example.com/models/model_1.tif",
            "coverage_area_hectares": 25.0,
            "resolution_cm": 2.5,
            "coordinate_system": "WGS84",
            "min_elevation": 100,
            "max_elevation": 250,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Get models for flight
    response = client.get(
        f"/api/v1/drones/flights/{flight_id}/models-3d",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_project_3d_models(admin_token, client, test_project_id):
    """Test getting 3D models for a project."""
    # Create a flight with project_id
    create_response = client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "project_id": test_project_id,
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    flight_id = create_response.json()["id"]

    # Create 3D model
    client.post(
        "/api/v1/drones/models-3d",
        json={
            "flight_id": flight_id,
            "project_id": test_project_id,
            "model_name": "Orthomosaic Model 1",
            "model_type": "orthomosaic",
            "file_format": "geotiff",
            "file_url": "https://example.com/models/model_1.tif",
            "coverage_area_hectares": 25.0,
            "resolution_cm": 2.5,
            "coordinate_system": "WGS84",
            "min_elevation": 100,
            "max_elevation": 250,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Get models for project
    response = client.get(
        f"/api/v1/drones/projects/{test_project_id}/models-3d",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_drone_summary(admin_token, client):
    """Test getting drone activity summary."""
    # Create a flight
    client.post(
        "/api/v1/drones/flights",
        json={
            "flight_name": "Test Flight",
            "drone_model": "DJI Phantom 4",
            "pilot_name": "Pilot 1",
            "flight_date": "2024-01-15T10:00:00",
            "flight_duration_minutes": 30,
            "altitude_meters": 100,
            "area_coverage_hectares": 25.0,
            "ground_resolution_cm": 2.0,
            "weather_conditions": "Clear",
            "notes": "Test",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Get summary
    response = client.get(
        "/api/v1/drones/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_flights" in data
    assert "completed_flights" in data
    assert "total_photos_captured" in data
    assert "total_area_covered_hectares" in data
    assert "total_3d_models" in data
    assert "models_by_type" in data


def test_drone_endpoints_require_authentication(client):
    """Test that drone endpoints require authentication."""
    response = client.get("/api/v1/drones/flights")
    assert response.status_code == 401

    response = client.post(
        "/api/v1/drones/flights",
        json={"flight_name": "Test"},
    )
    assert response.status_code == 401


def test_get_nonexistent_flight(admin_token, client):
    """Test getting a non-existent flight returns 404."""
    response = client.get(
        "/api/v1/drones/flights/nonexistent-id",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


def test_add_photo_to_nonexistent_flight(admin_token, client):
    """Test adding photo to non-existent flight returns 404."""
    response = client.post(
        "/api/v1/drones/flights/nonexistent-id/photos",
        json={
            "photo_name": "IMG_0001.jpg",
            "photo_url": "https://example.com/photos/IMG_0001.jpg",
            "file_size_mb": 5.2,
            "resolution_width": 5472,
            "resolution_height": 3648,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
