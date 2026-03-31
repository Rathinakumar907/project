def compare_output(expected: str, actual: str) -> bool:
    """
    Safely compare expected and actual outputs for code evaluation.
    Handles multiline strings, floating point numbers, and trailing/leading whitespaces.
    """
    expected_str = str(expected) if expected is not None else ""
    actual_str = str(actual) if actual is not None else ""
    
    # Remove \r (carriage return) and BOM
    expected_str = expected_str.replace('\r', '').replace('\xef\xbb\xbf', '').strip()
    actual_str = actual_str.replace('\r', '').replace('\xef\xbb\xbf', '').strip()
    
    print("\n--- DEBUG COMPARISON ---")
    print(f"Expected: {repr(expected)}")
    print(f"Actual: {repr(actual)}")
    print(f"Normalized Expected: {repr(expected_str)}")
    print(f"Normalized Actual: {repr(actual_str)}")
    print("------------------------\n")
    
    if expected_str == actual_str:
        return True
        
    expected_lines = [line.strip() for line in expected_str.splitlines() if line.strip()]
    actual_lines = [line.strip() for line in actual_str.splitlines() if line.strip()]
    
    # If line counts differ, try a flat word-by-word comparison
    if len(expected_lines) != len(actual_lines):
        e_words = expected_str.split()
        a_words = actual_str.split()
        if len(e_words) != len(a_words):
            return False
            
        for e_w, a_w in zip(e_words, a_words):
            if e_w == a_w:
                continue
            if e_w.lower() == a_w.lower():
                continue
            try:
                if abs(float(e_w) - float(a_w)) < 0.0001:
                    continue
                else:
                    return False
            except ValueError:
                return False
        return True

    # Line by line comparison
    for e_line, a_line in zip(expected_lines, actual_lines):
        if e_line == a_line:
            continue
        
        # Word by word comparison for this line
        e_words = e_line.split()
        a_words = a_line.split()
        
        if len(e_words) != len(a_words):
            return False
            
        for e_w, a_w in zip(e_words, a_words):
            if e_w == a_w:
                continue
            if e_w.lower() == a_w.lower():
                continue
            try:
                if abs(float(e_w) - float(a_w)) < 0.0001:
                    continue
                else:
                    return False
            except ValueError:
                return False
                
    return True
