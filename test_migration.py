#!/usr/bin/env python3
"""Test script for directory migration from ElectrumGLC to Electrum-GLC"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add electrum to path for import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_migration():
    """Test the migration function with various scenarios"""
    
    # Create a temporary directory to simulate APPDATA
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in temporary directory: {tmpdir}")
        
        # Override APPDATA for testing
        original_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = tmpdir
        
        try:
            # Import after setting environment
            from electrum.util import migrate_data_directory
            
            # Test 1: Fresh installation (neither directory exists)
            print("\nTest 1: Fresh installation")
            result = migrate_data_directory()
            expected = os.path.join(tmpdir, "Electrum-GLC")
            assert result == expected, f"Expected {expected}, got {result}"
            print(f"✓ Fresh install uses new directory: {result}")
            
            # Test 2: Old directory exists, new doesn't (migration needed)
            print("\nTest 2: Migration from old to new")
            old_dir = os.path.join(tmpdir, "ElectrumGLC")
            new_dir = os.path.join(tmpdir, "Electrum-GLC")
            
            # Create old directory with test data
            os.makedirs(old_dir)
            test_file = os.path.join(old_dir, "wallet_1")
            with open(test_file, "w") as f:
                f.write("test wallet data")
            
            result = migrate_data_directory()
            assert result == new_dir, f"Expected {new_dir}, got {result}"
            assert os.path.exists(new_dir), "New directory should exist after migration"
            assert not os.path.exists(old_dir), "Old directory should be renamed"
            assert os.path.exists(os.path.join(new_dir, "wallet_1")), "Wallet file should be in new directory"
            print(f"✓ Successfully migrated from {old_dir} to {new_dir}")
            
            # Test 3: New directory already exists (no migration needed)
            print("\nTest 3: New directory already exists")
            # Directory already exists from Test 2
            result = migrate_data_directory()
            assert result == new_dir, f"Expected {new_dir}, got {result}"
            print(f"✓ Uses existing new directory: {result}")
            
            # Test 4: Both directories exist (use new)
            print("\nTest 4: Both directories exist")
            # Recreate old directory
            os.makedirs(old_dir)
            result = migrate_data_directory()
            assert result == new_dir, f"Expected {new_dir}, got {result}"
            print(f"✓ Prefers new directory when both exist: {result}")
            
            # Clean up for next test
            shutil.rmtree(new_dir)
            shutil.rmtree(old_dir)
            
            # Test 5: Migration fails (simulate permission error)
            print("\nTest 5: Migration fails (simulated)")
            os.makedirs(old_dir)
            os.makedirs(new_dir)  # This will cause rename to fail
            shutil.rmtree(new_dir)  # Remove it
            
            # Create old directory
            os.makedirs(old_dir)
            test_file = os.path.join(old_dir, "wallet_1")
            with open(test_file, "w") as f:
                f.write("test wallet data")
            
            # Make new_dir as a file to cause rename to fail
            with open(new_dir, "w") as f:
                f.write("blocking file")
            
            result = migrate_data_directory()
            assert result == old_dir, f"Expected {old_dir} on failure, got {result}"
            print(f"✓ Falls back to old directory on migration failure: {result}")
            
            print("\n✅ All tests passed!")
            
        finally:
            # Restore original APPDATA
            if original_appdata:
                os.environ["APPDATA"] = original_appdata
            elif "APPDATA" in os.environ:
                del os.environ["APPDATA"]

if __name__ == "__main__":
    test_migration()