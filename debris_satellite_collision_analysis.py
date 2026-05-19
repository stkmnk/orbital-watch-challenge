"""
Debris-Satellite Collision Analysis
Reads debris and satellite positions, converts debris to ECEF,
and identifies collision risks based on proximity.
"""

import math
import re
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class Coordinate:
    """Represents a 3D coordinate in space"""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Coordinate') -> float:
        """Calculate Euclidean distance to another coordinate in meters"""
        return math.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )


class WGS84:
    """WGS-84 ellipsoid parameters"""
    A = 6378137.0
    F = 1 / 298.257223563
    E_SQ = 2 * F - F * F


class GPStoECEFConverter:
    """Converts GPS coordinates to ECEF coordinates"""
    
    @staticmethod
    def parse_dms_to_decimal(dms_string: str) -> float:
        """
        Convert DMS (Degrees Minutes Seconds) to decimal degrees
        
        Args:
            dms_string: String like "90°3'28N" or "143°42'18W"
            
        Returns:
            Decimal degrees (negative for S/W)
        """
        pattern = r"(\d+)°(\d+)'([\d.]+)([NSEW])"
        match = re.match(pattern, dms_string.strip())
        
        if not match:
            raise ValueError(f"Invalid DMS format: {dms_string}")
        
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        direction = match.group(4)
        
        decimal = degrees + minutes / 60.0 + seconds / 3600.0
        
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
            Coordinate object with X, Y, Z in meters
        """
        altitude_m = altitude_km * 1000.0
        
        lat_rad = math.radians(latitude)
        lon_rad = math.radians(longitude)
        
        cos_lat = math.cos(lat_rad)
        sin_lat = math.sin(lat_rad)
        cos_lon = math.cos(lon_rad)
        sin_lon = math.sin(lon_rad)
        
        N = WGS84.A / math.sqrt(1.0 - WGS84.E_SQ * sin_lat**2)
        
        x = (N + altitude_m) * cos_lat * cos_lon
        y = (N + altitude_m) * cos_lat * sin_lon
        z = (N * (1.0 - WGS84.E_SQ) + altitude_m) * sin_lat
        
        return Coordinate(x, y, z)


class CollisionAnalyzer:
    """Analyzes collisions between debris and satellites"""
    
    def __init__(self, collision_threshold_m: float = 1000.0):
        """
        Initialize collision analyzer
        
        Args:
            collision_threshold_m: Distance threshold in meters (default: 1000 m = 1 km)
        """
        self.collision_threshold_m = collision_threshold_m
        self.debris_objects = []
        self.satellites = []
        self.collisions = []
    
    def read_debris_positions(self, filepath: str):
        """
        Read space debris positions from CSV file (with DMS coordinates)
        
        Args:
            filepath: Path to CSV file
        """
        converter = GPStoECEFConverter()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    try:
                        obj_id = parts[0].strip()
                        lat_str = parts[1].strip()
                        lon_str = parts[2].strip()
                        alt_km = float(parts[3].strip())
                        
                        # Parse DMS to decimal
                        try:
                            lat = converter.parse_dms_to_decimal(lat_str)
                        except ValueError:
                            lat = float(lat_str)
                        
                        try:
                            lon = converter.parse_dms_to_decimal(lon_str)
                        except ValueError:
                            lon = float(lon_str)
                        
                        # Convert to ECEF
                        ecef = converter.gps_to_ecef(lat, lon, alt_km)
                        
                        self.debris_objects.append({
                            'id': obj_id,
                            'latitude': lat,
                            'longitude': lon,
                            'altitude_km': alt_km,
                            'ecef': ecef
                        })
                    except (ValueError, IndexError) as e:
                        print(f"⚠ Erro ao processar linha de debris: {line.strip()}")
                        print(f"  {str(e)}")
            
            print(f"✓ {len(self.debris_objects)} objetos de debris lidos")
            
        except FileNotFoundError:
            print(f"✗ Arquivo não encontrado: {filepath}")
        except Exception as e:
            print(f"✗ Erro ao ler arquivo de debris: {str(e)}")
    
    def read_satellite_positions(self, filepath: str):
        """
        Read satellite positions from CSV file (with ECEF coordinates)
        
        Args:
            filepath: Path to CSV file with X_m, Y_m, Z_m columns
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    try:
                        sat_id = parts[0].strip()
                        x_m = float(parts[1].strip())
                        y_m = float(parts[2].strip())
                        z_m = float(parts[3].strip())
                        
                        self.satellites.append({
                            'id': sat_id,
                            'ecef': Coordinate(x_m, y_m, z_m)
                        })
                    except (ValueError, IndexError) as e:
                        print(f"⚠ Erro ao processar linha de satélite: {line.strip()}")
                        print(f"  {str(e)}")
            
            print(f"✓ {len(self.satellites)} satélites lidos")
            
        except FileNotFoundError:
            print(f"✗ Arquivo não encontrado: {filepath}")
        except Exception as e:
            print(f"✗ Erro ao ler arquivo de satélites: {str(e)}")
    
    def analyze_collisions(self):
        """Analyze all debris-satellite pairs for collisions"""
        print(f"\n⏳ Analisando colisões entre {len(self.debris_objects)} debris e {len(self.satellites)} satélites...")
        
        collision_count = 0
        
        for debris in self.debris_objects:
            for satellite in self.satellites:
                distance = debris['ecef'].distance_to(satellite['ecef'])
                
                if distance < self.collision_threshold_m:
                    collision_count += 1
                    self.collisions.append({
                        'debris_id': debris['id'],
                        'satellite_id': satellite['id'],
                        'distance_m': distance
                    })
        
        print(f"✓ {collision_count} pares de colisão detectados")
        return collision_count
    
    def calculate_total_collision_distance(self) -> float:
        """
        Calculate the sum of all collision distances
        
        Returns:
            Total distance in meters
        """
        total_distance = sum(collision['distance_m'] for collision in self.collisions)
        return total_distance
    
    def get_satellites_at_risk(self) -> Dict[str, List[Dict]]:
        """
        Get dictionary of satellites with debris within collision threshold
        
        Returns:
            Dictionary mapping satellite ID to list of debris fragments
        """
        satellites_at_risk = {}
        
        for collision in self.collisions:
            sat_id = collision['satellite_id']
            if sat_id not in satellites_at_risk:
                satellites_at_risk[sat_id] = []
            
            satellites_at_risk[sat_id].append({
                'debris_id': collision['debris_id'],
                'distance_m': collision['distance_m']
            })
        
        return satellites_at_risk
    
    def print_collision_report(self):
        """Print detailed collision report"""
        if not self.collisions:
            print("\n✓ Nenhuma colisão detectada. Todos os objetos estão seguros.")
            return
        
        print("\n" + "=" * 90)
        print("RELATÓRIO DE COLISÕES")
        print("=" * 90)
        
        satellites_at_risk = self.get_satellites_at_risk()
        
        print(f"\n⚠️  {len(satellites_at_risk)} SATÉLITES EM RISCO")
        print(f"    {len(self.collisions)} PARES DE COLISÃO DETECTADOS\n")
        
        total_distance = self.calculate_total_collision_distance()
        print(f"Distância Total de Todas as Colisões: {total_distance:.2f} metros\n")
        
        # Sort satellites by number of debris
        sorted_sats = sorted(satellites_at_risk.items(), 
                           key=lambda x: len(x[1]), 
                           reverse=True)
        
        for i, (sat_id, debris_list) in enumerate(sorted_sats[:10], 1):  # Top 10 satellites
            sorted_debris = sorted(debris_list, key=lambda x: x['distance_m'])
            print(f"{i}. Satélite {sat_id}: {len(debris_list)} fragmentos de debris próximos")
            
            for debris in sorted_debris[:5]:  # Show top 5 closest debris
                print(f"   - {debris['debris_id']}: {debris['distance_m']:.2f} m")
            
            if len(sorted_debris) > 5:
                print(f"   ... e mais {len(sorted_debris) - 5} fragmentos")
            print()
        
        print("=" * 90)


def main():
    """Main function"""
    import os
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    debris_file = os.path.join(script_dir, "space_debris_positions.csv")
    satellite_file = os.path.join(script_dir, "satellite_positions.csv")
    
    print("=" * 90)
    print("ANÁLISE DE COLISÕES ENTRE DEBRIS E SATÉLITES")
    print("=" * 90 + "\n")
    
    analyzer = CollisionAnalyzer(collision_threshold_m=1000.0)  # 1 km threshold
    
    # Read data
    print("Lendo dados...")
    analyzer.read_debris_positions(debris_file)
    analyzer.read_satellite_positions(satellite_file)
    
    # Analyze collisions
    print()
    analyzer.analyze_collisions()
    
    # Print report
    analyzer.print_collision_report()
    
    # Calculate and display total distance
    total_distance = analyzer.calculate_total_collision_distance()
    print(f"\n📊 RESUMO FINAL")
    print(f"   Total de Debris: {len(analyzer.debris_objects)}")
    print(f"   Total de Satélites: {len(analyzer.satellites)}")
    print(f"   Pares de Colisão: {len(analyzer.collisions)}")
    print(f"   Soma de Distâncias: {total_distance:.2f} metros")
    print("=" * 90)


if __name__ == "__main__":
    main()
