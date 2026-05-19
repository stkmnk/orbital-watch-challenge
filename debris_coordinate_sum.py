"""
Space Debris Coordinate Analysis
Reads space debris positions, converts DMS to decimal, and performs mathematical operations
"""

import csv
from coordinate_collision_detector import CoordinateConverter
from typing import List, Tuple


class DebrisAnalyzer:
    """Analyzes space debris coordinate data"""
    
    def __init__(self, csv_filepath: str):
        """
        Initialize analyzer with CSV file
        
        Args:
            csv_filepath: Path to CSV file with debris positions
        """
        self.csv_filepath = csv_filepath
        self.converter = CoordinateConverter()
        self.debris_data = []
        self.decimal_coordinates = []
    
    def read_csv(self) -> List[dict]:
        """
        Read space debris data from CSV file
        
        Returns:
            List of dictionaries containing debris data
        """
        data = []
        try:
            with open(self.csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            self.debris_data = data
            return data
        except FileNotFoundError:
            print(f"Error: CSV file not found: {self.csv_filepath}")
            return []
        except Exception as e:
            print(f"Error reading CSV: {str(e)}")
            return []
    
    def convert_coordinates(self) -> List[Tuple[str, float, float]]:
        """
        Convert all DMS coordinates to decimal
        
        Returns:
            List of tuples (debris_id, decimal_latitude, decimal_longitude)
        """
        self.decimal_coordinates = []
        
        for debris in self.debris_data:
            try:
                debris_id = debris['DebrisID']
                lat_dms = debris['Lat']
                lon_dms = debris['Long']
                
                # Convert DMS to decimal
                lat_decimal = self.converter.parse_dms_to_decimal(lat_dms)
                lon_decimal = self.converter.parse_dms_to_decimal(lon_dms)
                
                self.decimal_coordinates.append((debris_id, lat_decimal, lon_decimal))
                
            except Exception as e:
                print(f"Error converting coordinates for {debris.get('DebrisID', 'Unknown')}: {str(e)}")
                continue
        
        return self.decimal_coordinates
    
    def calculate_sums(self) -> Tuple[float, float]:
        """
        Calculate sum of all latitude and longitude values
        
        Returns:
            Tuple of (latitude_sum, longitude_sum)
        """
        if not self.decimal_coordinates:
            return 0.0, 0.0
        
        lat_sum = sum(coord[1] for coord in self.decimal_coordinates)
        lon_sum = sum(coord[2] for coord in self.decimal_coordinates)
        
        return lat_sum, lon_sum
    
    def calculate_product(self, lat_sum: float, lon_sum: float) -> float:
        """
        Calculate the product of latitude sum and longitude sum
        
        Args:
            lat_sum: Sum of all latitude values
            lon_sum: Sum of all longitude values
            
        Returns:
            Product of the two sums
        """
        return lat_sum * lon_sum
    
    def print_detailed_report(self):
        """Print detailed report of all conversions"""
        print("=" * 100)
        print("WELTRAUMSCHROTT KOORDINATEN-ANALYSE - DETAILLIERTER BERICHT")
        print("=" * 100)
        print(f"\n{'DebrisID':<10} {'DMS Latitude':<20} {'Decimal Lat':<15} {'DMS Longitude':<20} {'Decimal Lon':<15}")
        print("-" * 100)
        
        for debris in self.debris_data:
            debris_id = debris['DebrisID']
            lat_dms = debris['Lat']
            lon_dms = debris['Long']
            
            # Find corresponding decimal coordinates
            decimal_entry = next((x for x in self.decimal_coordinates if x[0] == debris_id), None)
            
            if decimal_entry:
                lat_dec = decimal_entry[1]
                lon_dec = decimal_entry[2]
                print(f"{debris_id:<10} {lat_dms:<20} {lat_dec:<15.6f} {lon_dms:<20} {lon_dec:<15.6f}")
        
        print("\n" + "=" * 100)
    
    def print_summary(self):
        """Print summary report"""
        if not self.decimal_coordinates:
            print("No coordinates to analyze.")
            return
        
        lat_sum, lon_sum = self.calculate_sums()
        product = self.calculate_product(lat_sum, lon_sum)
        
        print("\n" + "=" * 100)
        print("WELTRAUMSCHROTT KOORDINATEN-ANALYSE - ZUSAMMENFASSUNG")
        print("=" * 100)
        
        print(f"\nAnzahl der Weltraumschrott-Objekte: {len(self.decimal_coordinates)}")
        
        print(f"\n--- BREITENGRADE (LATITUDE) ---")
        print(f"Summe aller Breitengrad-Werte: {lat_sum:.6f}°")
        print(f"Durchschnitt: {lat_sum / len(self.decimal_coordinates):.6f}°")
        
        print(f"\n--- LÄNGENGRADE (LONGITUDE) ---")
        print(f"Summe aller Längengrad-Werte: {lon_sum:.6f}°")
        print(f"Durchschnitt: {lon_sum / len(self.decimal_coordinates):.6f}°")
        
        print(f"\n--- MULTIPLIKATION ---")
        print(f"Produkt (Latitude-Summe × Longitude-Summe):")
        print(f"  {lat_sum:.6f} × {lon_sum:.6f} = {product:.6f}")
        
        print("\n" + "=" * 100)


def main():
    """Main function"""
    import os
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "space_debris_positions.csv")
    
    # Create analyzer
    analyzer = DebrisAnalyzer(csv_file)
    
    # Step 1: Read CSV file
    print("Step 1: Reading CSV file...")
    debris_data = analyzer.read_csv()
    if not debris_data:
        print("Failed to read CSV file. Exiting.")
        return
    print(f"✓ Successfully read {len(debris_data)} debris records.\n")
    
    # Step 2: Convert coordinates
    print("Step 2: Converting DMS coordinates to decimal...")
    converted = analyzer.convert_coordinates()
    print(f"✓ Successfully converted {len(converted)} coordinate pairs.\n")
    
    # Step 3: Calculate sums
    print("Step 3: Calculating sums...")
    lat_sum, lon_sum = analyzer.calculate_sums()
    print(f"✓ Latitude sum: {lat_sum:.6f}°")
    print(f"✓ Longitude sum: {lon_sum:.6f}°\n")
    
    # Step 4: Calculate product
    print("Step 4: Calculating product...")
    product = analyzer.calculate_product(lat_sum, lon_sum)
    print(f"✓ Product: {product:.6f}\n")
    
    # Print detailed report
    analyzer.print_detailed_report()
    
    # Print summary
    analyzer.print_summary()


if __name__ == "__main__":
    main()
