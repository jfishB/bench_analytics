import xml.etree.ElementTree as ET

try:
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    
    # Overall coverage
    line_rate = float(root.get('line-rate'))
    print(f"\n{'='*60}")
    print(f"OVERALL COVERAGE: {line_rate*100:.1f}%")
    print(f"{'='*60}\n")
    
    # Count files by coverage bracket
    brackets = {
        "100%": 0,
        "90-99%": 0,
        "80-89%": 0,
        "70-79%": 0,
        "60-69%": 0,
        "Below 60%": 0
    }
    
    files_below_100 = []
    
    for package in root.findall('.//package'):
        for cls in package.findall('.//class'):
            filename = cls.get('filename')
            file_line_rate = float(cls.get('line-rate'))
            cov_pct = file_line_rate * 100
            
            if cov_pct == 100:
                brackets["100%"] += 1
            elif cov_pct >= 90:
                brackets["90-99%"] += 1
                files_below_100.append((filename, cov_pct))
            elif cov_pct >= 80:
                brackets["80-89%"] += 1
                files_below_100.append((filename, cov_pct))
            elif cov_pct >= 70:
                brackets["70-79%"] += 1
                files_below_100.append((filename, cov_pct))
            elif cov_pct >= 60:
                brackets["60-69%"] += 1
                files_below_100.append((filename, cov_pct))
            else:
                brackets["Below 60%"] += 1
                files_below_100.append((filename, cov_pct))
    
    print("Coverage Distribution:")
    for bracket, count in brackets.items():
        print(f"  {bracket}: {count} files")
    
    print(f"\n{'='*60}")
    print(f"Files below 100% coverage ({len(files_below_100)}):")
    print(f"{'='*60}")
    
    # Sort by coverage (lowest first)
    files_below_100.sort(key=lambda x: x[1])
    
    for filename, cov_pct in files_below_100[:20]:  # Show top 20
        print(f"  {cov_pct:5.1f}% - {filename}")
    
    if len(files_below_100) > 20:
        print(f"  ... and {len(files_below_100) - 20} more files")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
