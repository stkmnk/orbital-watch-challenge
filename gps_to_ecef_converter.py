"""
GPS to ECEF Converter
Converts geodetic coordinates (latitude, longitude, altitude) to ECEF coordinates
using the WGS-84 ellipsoid model with rounding.
"""

import math
import re
from typing import Tuple
from dataclasses import dataclass


@dataclass
class Coordinate:
    """Represents a 3D coordinate in space"""
    x: float
    y: float
    z: float


class WGS84:
    """WGS-84 ellipsoid parameters"""
    # Semi-major axis (Earth radius at equator) in meters
    A = 6378137.0
    # Flattening
    F = 1 / 298.257223563
    # Eccentricity squared
    E_SQ = 2 * F - F * F


class GPStoECEFConverter:
    """Converts GPS coordinates to ECEF coordinates"""
    
    @staticmethod
    def parse_dms_to_decimal(dms_string: str) -> float:
        """
        Convert DMS (Degrees Minutes Seconds) to decimal degrees
        Formula: degrees + minutes/60 + seconds/3600
        
        Args:
            dms_string: String like "90°3'28N" or "143°42'18W"
            
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
    def gps_to_ecef(latitude: float, longitude: float, altitude_km: float) -> Coordinate:
        """
        Convert GPS coordinates to ECEF coordinates using WGS-84
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            altitude_km: Altitude in kilometers
            
        Returns:
            Coordinate object with X, Y, Z in ECEF system (meters)
        
        Formula:
        1. Convert angles to radians: λ_rad = λ × π/180, φ_rad = φ × π/180
        2. Compute N = a / √(1 - e²·sin²(φ_rad))
        3. X = (N + h) · cos(φ_rad) · cos(λ_rad)
           Y = (N + h) · cos(φ_rad) · sin(λ_rad)
           Z = (N·(1 - e²) + h) · sin(φ_rad)
        """
        # Convert altitude from km to meters
        altitude_m = altitude_km * 1000.0
        
        # Convert angles to radians
        lat_rad = math.radians(latitude)
        lon_rad = math.radians(longitude)
        
        # Pre-calculate trigonometric values
        cos_lat = math.cos(lat_rad)
        sin_lat = math.sin(lat_rad)
        cos_lon = math.cos(lon_rad)
        sin_lon = math.sin(lon_rad)
        
        # Compute prime vertical radius of curvature (N)
        # N = a / √(1 - e²·sin²(φ_rad))
        N = WGS84.A / math.sqrt(1.0 - WGS84.E_SQ * sin_lat**2)
        
        # Compute ECEF coordinates
        x = (N + altitude_m) * cos_lat * cos_lon
        y = (N + altitude_m) * cos_lat * sin_lon
        z = (N * (1.0 - WGS84.E_SQ) + altitude_m) * sin_lat
        
        return Coordinate(x, y, z)
    
    @staticmethod
    def round_coordinate(coord: Coordinate, decimals: int = 2) -> Coordinate:
        """
        Round ECEF coordinates to specified decimal places
        
        Args:
            coord: Coordinate object
            decimals: Number of decimal places (default: 2)
            
        Returns:
            Coordinate object with rounded values
        """
        return Coordinate(
            round(coord.x, decimals),
            round(coord.y, decimals),
            round(coord.z, decimals)
        )


def test_conversion():
    """
    Test GPS to ECEF conversion with test data
    """
    print("=" * 80)
    print("GPS ZU ECEF KONVERTIERUNG - TESTDATEN")
    print("=" * 80)
    
    converter = GPStoECEFConverter()
    
    # Test case 1: Decimal format
    test_cases = [
        {
            'name': 'Test 1 (Dezimal)',
            'input': (11.628889, -145.839167, 1795.59),
            'expected': (-6625344.32, -4495961.62, 1639159.98),
            'is_dms': False
        },
        {
            'name': 'Test 2 (DMS Format)',
            'input': ('90°3\'28N', '143°42\'18W', 1245.93),
            'expected': (6214.0, 4563.8, 7602678.43),
            'is_dms': True
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 80)
        
        try:
            # Parse input
            if test['is_dms']:
                lat = converter.parse_dms_to_decimal(test['input'][0])
                lon = converter.parse_dms_to_decimal(test['input'][1])
                alt_km = test['input'][2]
                print(f"Input (DMS): Lat: {test['input'][0]}, Lon: {test['input'][1]}, Alt: {alt_km} km")
                print(f"Converted to Decimal: Lat: {lat:.6f}°, Lon: {lon:.6f}°, Alt: {alt_km} km")
            else:
                lat, lon, alt_km = test['input']
                print(f"Input (Decimal): Lat: {lat}°, Lon: {lon}°, Alt: {alt_km} km")
            
            # Convert to ECEF
            ecef = converter.gps_to_ecef(lat, lon, alt_km)
            print(f"\nECEF (unrounded):")
            print(f"  X: {ecef.x} m")
            print(f"  Y: {ecef.y} m")
            print(f"  Z: {ecef.z} m")
            
            # Round values
            ecef_rounded = converter.round_coordinate(ecef, decimals=2)
            print(f"\nECEF (gerundet auf 2 Dezimalstellen):")
            print(f"  X: {ecef_rounded.x} m")
            print(f"  Y: {ecef_rounded.y} m")
            print(f"  Z: {ecef_rounded.z} m")
            
            # Compare with expected
            expected_x, expected_y, expected_z = test['expected']
            print(f"\nErwartet:")
            print(f"  X: {expected_x} m")
            print(f"  Y: {expected_y} m")
            print(f"  Z: {expected_z} m")
            
            # Check differences
            diff_x = abs(ecef_rounded.x - expected_x)
            diff_y = abs(ecef_rounded.y - expected_y)
            diff_z = abs(ecef_rounded.z - expected_z)
            
            print(f"\nAbweichungen:")
            print(f"  ΔX: {diff_x:.2f} m")
            print(f"  ΔY: {diff_y:.2f} m")
            print(f"  ΔZ: {diff_z:.2f} m")
            
            # Tolerance check
            tolerance = 1.0  # 1 meter tolerance
            test_passed = (diff_x < tolerance and 
                          diff_y < tolerance and 
                          diff_z < tolerance)
            
            status = "✓ BESTANDEN" if test_passed else "✗ FEHLGESCHLAGEN"
            print(f"\nStatus: {status}")
            
            if not test_passed:
                all_passed = False
                
        except Exception as e:
            print(f"✗ FEHLER: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALLE TESTS BESTANDEN")
    else:
        print("✗ EINIGE TESTS FEHLGESCHLAGEN")
    print("=" * 80 + "\n")


def convert_from_file(input_file: str, output_file: str):
    """
    Convert GPS coordinates from CSV file to ECEF and save to output file
    
    Args:
        input_file: Path to input CSV file with columns: ID, Latitude, Longitude, Altitude
        output_file: Path to output file
    """
    converter = GPStoECEFConverter()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        results.append("ID\tLatitude\tLongitude\tAltitude(km)\tX(m)\tY(m)\tZ(m)\n")
        
        # Skip header
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 4:
                try:
                    obj_id = parts[0].strip()
                    lat_str = parts[1].strip()
                    lon_str = parts[2].strip()
                    alt_km = float(parts[3].strip())
                    
                    # Try to parse as DMS first, then as decimal
                    try:
                        lat = converter.parse_dms_to_decimal(lat_str)
                    except ValueError:
                        lat = float(lat_str)
                    
                    try:
                        lon = converter.parse_dms_to_decimal(lon_str)
                    except ValueError:
                        lon = float(lon_str)
                    
                    ecef = converter.gps_to_ecef(lat, lon, alt_km)
                    ecef_rounded = converter.round_coordinate(ecef, decimals=2)
                    
                    results.append(
                        f"{obj_id}\t{lat}\t{lon}\t{alt_km}\t"
                        f"{ecef_rounded.x}\t{ecef_rounded.y}\t{ecef_rounded.z}\n"
                    )
                except ValueError as e:
                    print(f"Fehler bei Zeile: {line.strip()}")
                    print(f"  {str(e)}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(results)
        
        print(f"✓ Konvertierung abgeschlossen. Ergebnisse in: {output_file}")
        
    except FileNotFoundError:
        print(f"✗ Eingabedatei nicht gefunden: {input_file}")
    except Exception as e:
        print(f"✗ Fehler bei der Konvertierung: {str(e)}")


def calculate_total_ecef(input_file: str) -> Tuple[float, float, float]:
    """
    Calculate the total sum of all ECEF coordinates from a CSV file
    
    Args:
        input_file: Path to input CSV file
        
    Returns:
        Tuple of (total_X, total_Y, total_Z) in kilometers
    """
    converter = GPStoECEFConverter()
    
    total_x = 0.0
    total_y = 0.0
    total_z = 0.0
    count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Skip header
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 4:
                try:
                    lat_str = parts[1].strip()
                    lon_str = parts[2].strip()
                    alt_km = float(parts[3].strip())
                    
                    # Try to parse as DMS first, then as decimal
                    try:
                        lat = converter.parse_dms_to_decimal(lat_str)
                    except ValueError:
                        lat = float(lat_str)
                    
                    try:
                        lon = converter.parse_dms_to_decimal(lon_str)
                    except ValueError:
                        lon = float(lon_str)
                    
                    ecef = converter.gps_to_ecef(lat, lon, alt_km)
                    
                    # Add to totals (convert from meters to kilometers)
                    total_x += ecef.x / 1000.0
                    total_y += ecef.y / 1000.0
                    total_z += ecef.z / 1000.0
                    count += 1
                    
                except ValueError as e:
                    print(f"⚠ Fehler beim Parsen der Zeile: {line.strip()}")
                    print(f"  {str(e)}")
        
        print(f"✓ {count} Koordinaten verarbeitet")
        return total_x, total_y, total_z
        
    except FileNotFoundError:
        print(f"✗ Eingabedatei nicht gefunden: {input_file}")
        return 0.0, 0.0, 0.0
    except Exception as e:
        print(f"✗ Fehler bei der Berechnung: {str(e)}")
        return 0.0, 0.0, 0.0


def main():
    """Main function"""
    import os
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Validate coordinate conversion with test data
    test_file = os.path.join(script_dir, "test_table.tsv")
    if os.path.exists(test_file):
        test_conversion()
    else:
        print(f"⚠ Hinweis: Test-Datei nicht gefunden: {test_file}\n")
    
    # Step 2: Process space_debris_positions.csv
    input_csv = os.path.join(script_dir, "space_debris_positions.csv")
    output_tsv = os.path.join(script_dir, "ecef_coordinates.tsv")
    
    if os.path.exists(input_csv):
        print("\n" + "=" * 80)
        print("KONVERTIERUNG DER SPACE DEBRIS POSITIONEN")
        print("=" * 80 + "\n")
        
        # Convert and save to file
        convert_from_file(input_csv, output_tsv)
        
        # Calculate total sum
        print("\n" + "=" * 80)
        print("BERECHNUNG DER GESAMTSUMME")
        print("=" * 80 + "\n")
        
        total_x, total_y, total_z = calculate_total_ecef(input_csv)
        
        print(f"\nGesamtsummen der ECEF-Koordinaten:")
        print(f"  Gesamt X: {total_x:.5f} km")
        print(f"  Gesamt Y: {total_y:.5f} km")
        print(f"  Gesamt Z: {total_z:.5f} km")
        
        # Calculate combined total
        combined_total = total_x + total_y + total_z
        print(f"\n  Kombinierte Summe (X+Y+Z): {combined_total:.5f} km")
        
        print("\n" + "=" * 80)
    else:
        print(f"\n⚠ Hinweis: space_debris_positions.csv nicht gefunden.")



if __name__ == "__main__":
    main()
