import xml.etree.ElementTree as ET
import os

try:
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    print("Parsed coverage.xml successfully")
    
    classes = root.findall('.//class')
    print(f"Found {len(classes)} classes")

    with open('coverage_report_parsed.txt', 'w') as f:
        f.write(f"{'File':<60} {'Coverage':<10} {'Missing Lines'}\n")
        f.write("-" * 100 + "\n")
        
        for package in root.findall('.//package'):
            for cls in package.findall('.//class'):
                filename = cls.get('filename')
                line_rate = float(cls.get('line-rate'))
                
                if line_rate < 1.0:
                    missing_lines = []
                    for line in cls.findall('.//line'):
                        if line.get('hits') == '0':
                            missing_lines.append(line.get('number'))
                    
                    missing_str = ",".join(missing_lines)
                    # Truncate missing string if too long
                    if len(missing_str) > 30:
                        missing_str = missing_str[:27] + "..."
                        
                    f.write(f"{filename:<60} {line_rate*100:6.1f}%    {missing_str}\n")
    print("Report written to coverage_report_parsed.txt")

except Exception as e:
    print(f"Error parsing coverage.xml: {e}")
