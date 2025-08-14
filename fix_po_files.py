#!/usr/bin/env python3
"""
Fix msgfmt errors in .po translation files.
Ensures msgid and msgstr have matching newlines at beginning and end.
"""

import os
import re

def fix_po_file(filepath):
    """Fix newline mismatches in a .po file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match msgid/msgstr pairs
    pattern = r'(msgid\s+")(.*?)("\s*\nmsgstr\s+")(.*?)(")'
    
    def fix_match(match):
        msgid_prefix = match.group(1)
        msgid_content = match.group(2)
        middle = match.group(3)
        msgstr_content = match.group(4)
        msgstr_suffix = match.group(5)
        
        # Check if msgid starts with \n
        msgid_starts_newline = msgid_content.startswith('\\n')
        # Check if msgid ends with \n
        msgid_ends_newline = msgid_content.endswith('\\n')
        
        # Fix msgstr to match msgid
        if msgid_starts_newline and not msgstr_content.startswith('\\n'):
            if msgstr_content:  # Only add if not empty
                msgstr_content = '\\n' + msgstr_content
        elif not msgid_starts_newline and msgstr_content.startswith('\\n'):
            msgstr_content = msgstr_content[2:]  # Remove \n
            
        if msgid_ends_newline and not msgstr_content.endswith('\\n'):
            if msgstr_content:  # Only add if not empty
                msgstr_content = msgstr_content + '\\n'
        elif not msgid_ends_newline and msgstr_content.endswith('\\n'):
            msgstr_content = msgstr_content[:-2]  # Remove \n
        
        return msgid_prefix + msgid_content + middle + msgstr_content + msgstr_suffix
    
    # Apply fixes
    fixed_content = re.sub(pattern, fix_match, content, flags=re.DOTALL)
    
    if fixed_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return True
    return False

# Find and fix all .po files
po_files = []
for root, dirs, files in os.walk('electrum/locale'):
    for file in files:
        if file.endswith('.po'):
            po_files.append(os.path.join(root, file))

fixed_count = 0
for po_file in po_files:
    if fix_po_file(po_file):
        print(f"Fixed: {po_file}")
        fixed_count += 1

print(f"\nFixed {fixed_count} .po files")