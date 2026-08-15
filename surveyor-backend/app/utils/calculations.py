"""Topographic and geometric calculations."""

import math
from typing import Tuple, List

class SurveyCalculations:
    """Topographic calculations."""

    @staticmethod
    def distance_horizontal(
        east1: float,
        north1: float,
        east2: float,
        north2: float
    ) -> float:
        """Calculate horizontal distance between two points."""
        de = east2 - east1
        dn = north2 - north1
        return math.sqrt(de**2 + dn**2)

    @staticmethod
    def distance_inclined(
        east1: float,
        north1: float,
        elev1: float,
        east2: float,
        north2: float,
        elev2: float
    ) -> float:
        """Calculate inclined distance between two points."""
        horizontal = SurveyCalculations.distance_horizontal(east1, north1, east2, north2)
        dz = elev2 - elev1
        return math.sqrt(horizontal**2 + dz**2)

    @staticmethod
    def azimuth(
        east1: float,
        north1: float,
        east2: float,
        north2: float
    ) -> float:
        """Calculate azimuth (bearing) from point 1 to point 2 in degrees."""
        de = east2 - east1
        dn = north2 - north1

        if dn == 0 and de == 0:
            return 0

        azimuth_rad = math.atan2(de, dn)
        azimuth_deg = math.degrees(azimuth_rad)

        # Convert to 0-360 range
        if azimuth_deg < 0:
            azimuth_deg += 360

        return azimuth_deg

    @staticmethod
    def bearing_to_quadrant(azimuth: float) -> str:
        """Convert azimuth to quadrant bearing (e.g., N 45° E)."""
        azimuth = azimuth % 360

        if azimuth <= 90:
            angle = azimuth
            return f"N {angle:.2f}° E"
        elif azimuth <= 180:
            angle = 180 - azimuth
            return f"S {angle:.2f}° E"
        elif azimuth <= 270:
            angle = azimuth - 180
            return f"S {angle:.2f}° W"
        else:
            angle = 360 - azimuth
            return f"N {angle:.2f}° W"

    @staticmethod
    def polygon_area(points: List[Tuple[float, float]]) -> float:
        """Calculate area of polygon using shoelace formula."""
        if len(points) < 3:
            return 0

        area = 0
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            area += x1 * y2 - x2 * y1

        return abs(area) / 2

    @staticmethod
    def polygon_perimeter(points: List[Tuple[float, float]]) -> float:
        """Calculate perimeter of polygon."""
        if len(points) < 2:
            return 0

        perimeter = 0
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            perimeter += dist

        return perimeter

    @staticmethod
    def slope_angle(horizontal: float, vertical: float) -> float:
        """Calculate slope angle in degrees."""
        if horizontal == 0:
            return 90 if vertical > 0 else -90
        return math.degrees(math.atan(vertical / horizontal))

    @staticmethod
    def grade_percentage(horizontal: float, vertical: float) -> float:
        """Calculate grade as percentage."""
        if horizontal == 0:
            return 0
        return (vertical / horizontal) * 100

    @staticmethod
    def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
        """Convert DMS (Degrees, Minutes, Seconds) to decimal degrees."""
        return degrees + minutes / 60 + seconds / 3600

    @staticmethod
    def decimal_to_dms(decimal: float) -> Tuple[int, int, float]:
        """Convert decimal degrees to DMS."""
        degrees = int(decimal)
        minutes_decimal = (decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60
        return degrees, minutes, seconds

    @staticmethod
    def angle_difference(azimuth1: float, azimuth2: float) -> float:
        """Calculate smallest angle between two azimuths."""
        diff = abs(azimuth2 - azimuth1)
        if diff > 180:
            diff = 360 - diff
        return diff

    @staticmethod
    def coordinate_offset(
        east: float,
        north: float,
        distance: float,
        azimuth: float
    ) -> Tuple[float, float]:
        """Calculate new coordinates given distance and azimuth."""
        azimuth_rad = math.radians(azimuth)
        new_east = east + distance * math.sin(azimuth_rad)
        new_north = north + distance * math.cos(azimuth_rad)
        return new_east, new_north
