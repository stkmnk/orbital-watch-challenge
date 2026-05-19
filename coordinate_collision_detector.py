"""
Satellite Position and Space Debris Collision Detection System
Converts GPS coordinates to ECEF coordinates and detects potential collisions
"""

import math
import re
from typing import Tuple, List, Dict
from dataclasses import dataclass


@dataclass
class Coordinate:
    """Represents a 3D coordinate in space"""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Coordinate') -> float:
        """Calculate Euclidean distance to another coordinate"""
        return math.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )


class WGS84:
    """WGS84 ellipsoid parameters"""
    # Semi-major axis (Earth radius at equator) in meters
    A = 6378137.0
    # Semi-minor axis (Earth radius at poles) in meters
    B = 6356752.314245
    # Eccentricity squared
    E_SQ = (A**2 - B**2) / A**2
    # Flattening
    F = (A - B) / A


class CoordinateConverter:
    """Converts between coordinate systems"""
    
    @staticmethod
    def parse_dms_to_decimal(dms_string: str) -> float:
        """
        Convert DMS (Degrees Minutes Seconds) to decimal degrees
        Formula: degrees + minutes/60 + seconds/3600
        
        Args:
            dms_string: String like "11°37'44N" or "145°50'21W"
            
        Returns:
            Decimal degrees (negative for S/W)
        """
        # Pattern to match: degrees°minutes'seconds[direction]
        pattern = r"(\d+)°(\d+)'([\d.]+)([NSEW])"
        match = re.match(pattern, dms_string.strip())
        
        if not match:
            raise ValueError(f"Invalid DMS format: {dms_string}")
        
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        direction = match.group(4)
        
        # Calculate decimal degrees
        decimal = degrees + minutes / 60.0 + seconds / 3600.0
        
        # Apply sign based on direction
        if direction in ['S', 'W']:
            decimal = -decimal
            
        return decimal
    
    @staticmethod
    def gps_to_ecef(latitude: float, longitude: float, height: float = 0.0) -> Coordinate:
        """
        Convert GPS coordinates (latitude, longitude, height) to ECEF coordinates
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            height: Height above mean sea level in meters (default: 0)
            
        Returns:
            Coordinate object with X, Y, Z in ECEF system
        """
        # Convert degrees to radians
        lat_rad = math.radians(latitude)
        lon_rad = math.radians(longitude)
        
        # Calculate N (radius of curvature in prime vertical)
        sin_lat = math.sin(lat_rad)
        N = WGS84.A / math.sqrt(1.0 - WGS84.E_SQ * sin_lat**2)
        
        # Calculate ECEF coordinates
        x = (N + height) * math.cos(lat_rad) * math.cos(lon_rad)
        y = (N + height) * math.cos(lat_rad) * math.sin(lon_rad)
        z = (N * (1.0 - WGS84.E_SQ) + height) * sin_lat
        
        return Coordinate(x, y, z)


class CollisionDetector:
    """Detects potential collisions between debris and satellites"""
    
    def __init__(self, collision_threshold: float = 1000.0):
        """
        Initialize collision detector
        
        Args:
            collision_threshold: Distance threshold for collision alert in meters
        """
        self.collision_threshold = collision_threshold
        self.collisions = []
    
    def check_collision(self, debris: Coordinate, satellite: Coordinate, 
                       debris_id: str = "Debris", satellite_id: str = "Satellite") -> bool:
        """
        Check if debris and satellite are within collision threshold
        
        Args:
            debris: ECEF coordinate of space debris
            satellite: ECEF coordinate of satellite
            debris_id: Identifier for debris
            satellite_id: Identifier for satellite
            
        Returns:
            True if collision risk detected
        """
        distance = debris.distance_to(satellite)
        
        if distance < self.collision_threshold:
            self.collisions.append({
                'debris_id': debris_id,
                'satellite_id': satellite_id,
                'distance_m': distance,
                'debris_ecef': debris,
                'satellite_ecef': satellite
            })
            return True
        
        return False
    
    def get_collision_report(self) -> str:
        """Generate a formatted collision report"""
        if not self.collisions:
            return "No collisions detected. All objects are safe."
        
        report = f"⚠️  COLLISION ALERT: {len(self.collisions)} collision(s) detected!\n"
        report += "=" * 70 + "\n\n"
        
        for i, collision in enumerate(self.collisions, 1):
            report += f"Collision {i}:\n"
            report += f"  Debris ID: {collision['debris_id']}\n"
            report += f"  Satellite ID: {collision['satellite_id']}\n"
            report += f"  Distance: {collision['distance_m']:.2f} meters\n"
            report += f"  Debris ECEF: ({collision['debris_ecef'].x:.2f}, "
            report += f"{collision['debris_ecef'].y:.2f}, "
            report += f"{collision['debris_ecef'].z:.2f})\n"
            report += f"  Satellite ECEF: ({collision['satellite_ecef'].x:.2f}, "
            report += f"{collision['satellite_ecef'].y:.2f}, "
            report += f"{collision['satellite_ecef'].z:.2f})\n"
            report += "-" * 70 + "\n"
        
        return report


def read_test_file(filepath: str) -> List[Tuple[str, str]]:
    """
    Read test data from TSV file
    
    Args:
        filepath: Path to TSV file
        
    Returns:
        List of (dms_coordinate, decimal_coordinate) tuples
    """
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Skip header
        for line in lines[1:]:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                data.append((parts[0], parts[1]))
    return data


def validate_conversion(filepath: str):
    """
    Validate DMS to decimal conversion using test data
    
    Args:
        filepath: Path to test TSV file
    """
    print("=" * 70)
    print("VALIDIERUNG DER KOORDINATEN-UMWANDLUNG")
    print("=" * 70)
    
    converter = CoordinateConverter()
    test_data = read_test_file(filepath)
    
    all_valid = True
    
    for dms_str, expected_decimal_str in test_data:
        try:
            expected_decimal = float(expected_decimal_str)
            calculated_decimal = converter.parse_dms_to_decimal(dms_str)
            
            # Check if values match (allow small floating point differences)
            difference = abs(calculated_decimal - expected_decimal)
            is_valid = difference < 0.000001
            
            status = "✓ PASS" if is_valid else "✗ FAIL"
            
            print(f"\n{status}")
            print(f"  Input (DMS): {dms_str}")
            print(f"  Expected: {expected_decimal:.6f}")
            print(f"  Calculated: {calculated_decimal:.6f}")
            print(f"  Difference: {difference:.9f}")
            
            if not is_valid:
                all_valid = False
                
        except Exception as e:
            print(f"\n✗ ERROR: {dms_str}")
            print(f"  Exception: {str(e)}")
            all_valid = False
    
    print("\n" + "=" * 70)
    if all_valid:
        print("✓ ALLE UMWANDLUNGEN SIND KORREKT")
    else:
        print("✗ EINIGE UMWANDLUNGEN SIND FEHLERHAFT")
    print("=" * 70 + "\n")


def example_collision_detection():
    """
    Example of collision detection between space debris and satellites
    """
    print("=" * 70)
    print("BEISPIEL: KOLLISIONSERKENNUNG ZWISCHEN WELTRAUMSCHROTT UND SATELLITEN")
    print("=" * 70)
    
    converter = CoordinateConverter()
    detector = CollisionDetector(collision_threshold=2000000)  # 2000 km
    
    # Example: Space debris at specific GPS coordinates
    debris_lat = 51.5074  # London
    debris_lon = -0.1278
    debris_height = 400000  # 400 km altitude (ISS approximate altitude)
    
    print(f"\nWeltraumschrott Position (GPS):")
    print(f"  Latitude: {debris_lat}°")
    print(f"  Longitude: {debris_lon}°")
    print(f"  Height (MSL): {debris_height} m")
    
    debris_ecef = converter.gps_to_ecef(debris_lat, debris_lon, debris_height)
    
    print(f"\nWeltraumschrott Position (ECEF):")
    print(f"  X: {debris_ecef.x:.2f} m")
    print(f"  Y: {debris_ecef.y:.2f} m")
    print(f"  Z: {debris_ecef.z:.2f} m")
    
    # Example: Satellite positions (in ECEF coordinates)
    # These would normally come from a tracking system
    satellites = [
        ("ISS", Coordinate(3771613.0, -492167.0, 5126003.0)),  # Approximate ISS position
        ("GOES-16", Coordinate(42164169.0, 0.0, 0.0)),  # Geostationary satellite
        ("NOAA-18", Coordinate(-4625923.0, 4348073.0, -213573.0)),  # Polar orbit satellite
    ]
    
    print(f"\nSatellit Positionen (ECEF):")
    for sat_id, sat_coord in satellites:
        distance = debris_ecef.distance_to(sat_coord)
        print(f"  {sat_id}: X={sat_coord.x:.2f}, Y={sat_coord.y:.2f}, Z={sat_coord.z:.2f}")
        print(f"    Distanz zum Schrott: {distance:.2f} m ({distance/1000:.2f} km)")
        detector.check_collision(debris_ecef, sat_coord, "Debris_001", sat_id)
    
    print("\n" + detector.get_collision_report())


def main():
    """Main function"""
    import os
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, "test_table.tsv")
    
    # Step 1: Validate coordinate conversion
    if os.path.exists(test_file):
        validate_conversion(test_file)
    else:
        print(f"Warnung: Test-Datei nicht gefunden: {test_file}")
    
    # Step 2: Example collision detection
    example_collision_detection()


if __name__ == "__main__":
    main()
