"""CSV and GeoJSON export utilities for survey points."""

import csv
import json
from io import StringIO
from typing import List, Dict, Any

class CSVExporter:
    """Export survey points to CSV format."""

    @staticmethod
    def export_survey_points(points: List[Dict[str, Any]]) -> str:
        """Export survey points to CSV string."""
        if not points:
            return ""

        output = StringIO()
        fieldnames = [
            'point_number', 'east', 'north', 'elevation',
            'pdop', 'hdop', 'vdop', 'satellite_count', 'description'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for point in points:
            row = {
                'point_number': point.get('point_number', ''),
                'east': f"{point.get('east', 0):.6f}",
                'north': f"{point.get('north', 0):.6f}",
                'elevation': f"{point.get('elevation', 0):.4f}",
                'pdop': f"{point.get('pdop', ''):.2f}" if point.get('pdop') else '',
                'hdop': f"{point.get('hdop', ''):.2f}" if point.get('hdop') else '',
                'vdop': f"{point.get('vdop', ''):.2f}" if point.get('vdop') else '',
                'satellite_count': point.get('satellite_count', ''),
                'description': point.get('description', ''),
            }
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def export_projects(projects: List[Dict[str, Any]]) -> str:
        """Export projects to CSV string."""
        if not projects:
            return ""

        output = StringIO()
        fieldnames = ['code', 'name', 'status', 'budget', 'spent', 'municipality', 'province', 'created_at']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for project in projects:
            row = {
                'code': project.get('code', ''),
                'name': project.get('name', ''),
                'status': project.get('status', ''),
                'budget': f"{project.get('budget', 0):.2f}",
                'spent': f"{project.get('spent', 0):.2f}",
                'municipality': project.get('municipality', ''),
                'province': project.get('province', ''),
                'created_at': project.get('created_at', ''),
            }
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def export_geojson(points: List[Dict[str, Any]]) -> str:
        """Export survey points to GeoJSON format."""
        features = []

        for point in points:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        point.get('east', 0),
                        point.get('north', 0),
                        point.get('elevation', 0)
                    ]
                },
                "properties": {
                    "point_number": point.get('point_number', ''),
                    "elevation": point.get('elevation', 0),
                    "pdop": point.get('pdop'),
                    "hdop": point.get('hdop'),
                    "vdop": point.get('vdop'),
                    "satellite_count": point.get('satellite_count'),
                    "description": point.get('description', '')
                }
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        return json.dumps(geojson, indent=2)
