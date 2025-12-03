import xml.etree.ElementTree as ET

try:
    tree = ET.parse('coverage.xml')  # nosec
    root = tree.getroot()
    
    # Find simulator/views.py
    for package in root.findall('.//package'):
        for cls in package.findall('.//class'):
            filename = cls.get('filename')
            if 'simulator/views.py' in filename:
                print(f"\n=== {filename} ===")
                line_rate = float(cls.get('line-rate'))
                print(f"Coverage: {line_rate*100:.1f}%\n")
                
                # Get all lines
                all_lines = {}
                for line in cls.findall('.//line'):
                    line_num = int(line.get('number'))
                    hits = int(line.get('hits'))
                    all_lines[line_num] = hits
                
                # Group missing lines
                missing = [num for num, hits in sorted(all_lines.items()) if hits == 0]
                
                with open('views_coverage_details.txt', 'w') as f:
                    f.write(f"=== {filename} ===\n")
                    f.write(f"Coverage: {line_rate*100:.1f}%\n\n")
                    f.write(f"Missing lines ({len(missing)}):\n")
                    f.write(str(missing) + "\n")
                print(f"Written to views_coverage_details.txt")
                
except Exception as e:
    print(f"Error: {e}")
