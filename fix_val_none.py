#!/usr/bin/env python3
"""
Script to find and fix potential None attribute errors
where val.get() is called on a None object.
"""

import os
import re

def fix_files():
    """Find and fix potential val.get() on None issues"""
    
    # Common patterns that might have this issue
    patterns_to_check = [
        (r'(\s+)(\w+)\s*=\s*val\.get\((.*?)\)\s+or\s+\(\)',
         r'\1\2 = val.get(\3) or () if val else ()'),
        (r'(\s+)(\w+)\s*=\s*val\.get\((.*?)\)',
         r'\1\2 = val.get(\3) if val else None'),
    ]
    
    files_fixed = []
    
    for root, dirs, files in os.walk('electrum'):
        # Skip test and vendor directories
        if 'test' in root or '_vendor' in root:
            continue
            
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    original = content
                    for pattern, replacement in patterns_to_check:
                        content = re.sub(pattern, replacement, content)
                    
                    if content != original:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        files_fixed.append(filepath)
                        print(f"Fixed: {filepath}")
                
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return files_fixed

if __name__ == "__main__":
    fixed = fix_files()
    if fixed:
        print(f"\nFixed {len(fixed)} files")
    else:
        print("No files needed fixing")