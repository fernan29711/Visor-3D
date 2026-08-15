"""CSV import utilities for survey points."""

import csv
from io import StringIO
from typing import List, Dict, Any

class CSVImportParser:
    """Parse survey points from CSV data."""

    @staticmethod
    def parse_csv(content: str, delimiter: str = ',') -> List[Dict[str, Any]]:
        """Parse CSV content and return list of point dictionaries."""
        points = []
        reader = csv.DictReader(StringIO(content), delimiter=delimiter)

        for row in reader:
            if not row or all(v is None or v == '' for v in row.values()):
                continue

            point = {
                'point_number': row.get('point_number') or row.get('Punto') or row.get('ID'),
                'east': float(row.get('east') or row.get('E') or row.get('X') or 0),
                'north': float(row.get('north') or row.get('N') or row.get('Y') or 0),
                'elevation': float(row.get('elevation') or row.get('Z') or row.get('elev') or 0),
            }

            # Optional GNSS metadata
            if 'pdop' in row or 'PDOP' in row:
                point['pdop'] = float(row.get('pdop') or row.get('PDOP') or 0)
            if 'hdop' in row or 'HDOP' in row:
                point['hdop'] = float(row.get('hdop') or row.get('HDOP') or 0)
            if 'vdop' in row or 'VDOP' in row:
                point['vdop'] = float(row.get('vdop') or row.get('VDOP') or 0)
            if 'satellite_count' in row or 'Satellites' in row:
                point['satellite_count'] = int(row.get('satellite_count') or row.get('Satellites') or 0)
            if 'description' in row or 'Description' in row:
                point['description'] = row.get('description') or row.get('Description') or ''

            points.append(point)

        return points

    @staticmethod
    def validate_points(points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate parsed points and return validation result."""
        errors = []
        valid_points = []

        for idx, point in enumerate(points, start=1):
            point_errors = []

            if not point.get('point_number'):
                point_errors.append(f"Row {idx}: Missing point number/ID")

            try:
                east = float(point.get('east', 0))
                north = float(point.get('north', 0))
            except (ValueError, TypeError):
                point_errors.append(f"Row {idx}: Invalid coordinates")

            if point_errors:
                errors.extend(point_errors)
            else:
                valid_points.append(point)

        return {
            'valid': len(errors) == 0,
            'valid_points': valid_points,
            'errors': errors,
            'total': len(points),
            'valid_count': len(valid_points),
            'error_count': len(errors)
        }
