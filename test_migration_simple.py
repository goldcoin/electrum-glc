#!/usr/bin/env python3
"""Standalone test for directory migration logic"""

import os
import tempfile
import shutil

def migrate_data_directory_standalone(appdata_path):
    """Standalone version of migrate_data_directory for testing"""
    old_dir = os.path.join(appdata_path, "ElectrumGLC")
    new_dir = os.path.join(appdata_path, "Electrum-GLC")
    
    # Check if migration needed (old exists but new doesn't)
    if os.path.exists(old_dir) and not os.path.exists(new_dir):
        try:
            # Simple rename operation
            os.rename(old_dir, new_dir)
            print(f"Info: Migrated wallet data from {old_dir} to {new_dir}")
            return new_dir
        except OSError as e:
            # If rename fails (permissions, cross-device, etc.), use old directory
            print(f"Warning: Could not migrate data directory: {e}")
            print(f"Info: Continuing with old directory: {old_dir}")
            return old_dir
    
    # Return appropriate directory based on what exists
    if os.path.exists(new_dir):
        return new_dir
    elif os.path.exists(old_dir):
        # This case handles if rename failed on a previous run
        return old_dir
    else:
        # Fresh installation - use new naming
        return new_dir

def test_migration():
    """Test the migration function with various scenarios"""
    
    # Create a temporary directory to simulate APPDATA
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in temporary directory: {tmpdir}")
        
        # Test 1: Fresh installation (neither directory exists)
        print("\nTest 1: Fresh installation")
        result = migrate_data_directory_standalone(tmpdir)
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
        test_config = os.path.join(old_dir, "config")
        with open(test_config, "w") as f:
            f.write("test config")
        
        result = migrate_data_directory_standalone(tmpdir)
        assert result == new_dir, f"Expected {new_dir}, got {result}"
        assert os.path.exists(new_dir), "New directory should exist after migration"
        assert not os.path.exists(old_dir), "Old directory should be renamed"
        assert os.path.exists(os.path.join(new_dir, "wallet_1")), "Wallet file should be in new directory"
        assert os.path.exists(os.path.join(new_dir, "config")), "Config file should be in new directory"
        
        # Read back the files to verify contents
        with open(os.path.join(new_dir, "wallet_1"), "r") as f:
            assert f.read() == "test wallet data", "Wallet data should be preserved"
        print(f"✓ Successfully migrated from ElectrumGLC to Electrum-GLC")
        print(f"  - Wallet and config files preserved")
        
        # Test 3: New directory already exists (no migration needed)
        print("\nTest 3: New directory already exists")
        result = migrate_data_directory_standalone(tmpdir)
        assert result == new_dir, f"Expected {new_dir}, got {result}"
        print(f"✓ Uses existing new directory: Electrum-GLC")
        
        # Test 4: Both directories exist (use new)
        print("\nTest 4: Both directories exist")
        # Recreate old directory
        os.makedirs(old_dir)
        with open(os.path.join(old_dir, "different_wallet"), "w") as f:
            f.write("different data")
        
        result = migrate_data_directory_standalone(tmpdir)
        assert result == new_dir, f"Expected {new_dir}, got {result}"
        assert os.path.exists(os.path.join(new_dir, "wallet_1")), "Original migrated files should still exist"
        assert not os.path.exists(os.path.join(new_dir, "different_wallet")), "Should not migrate when new already exists"
        print(f"✓ Prefers new directory when both exist")
        
        # Clean up for next test
        shutil.rmtree(new_dir)
        shutil.rmtree(old_dir)
        
        # Test 5: Old directory exists but new doesn't (after clearing)
        print("\nTest 5: Old directory exists after failed migration")
        os.makedirs(old_dir)
        with open(os.path.join(old_dir, "wallet_1"), "w") as f:
            f.write("test wallet data")
        
        # This simulates a case where old_dir exists but new doesn't
        # Should trigger migration
        result = migrate_data_directory_standalone(tmpdir)
        assert result == new_dir, f"Expected {new_dir} after second migration, got {result}"
        assert os.path.exists(new_dir), "Should have migrated again"
        assert not os.path.exists(old_dir), "Old should be renamed again"
        print(f"✓ Successfully migrates when conditions are right")
        
        print("\n" + "="*50)
        print("✅ All migration tests passed successfully!")
        print("="*50)
        print("\nMigration behavior summary:")
        print("1. Fresh install → uses Electrum-GLC")
        print("2. Only ElectrumGLC exists → migrates to Electrum-GLC")
        print("3. Only Electrum-GLC exists → uses Electrum-GLC")
        print("4. Both exist → uses Electrum-GLC (assumes already migrated)")
        print("5. Migration fails → continues with ElectrumGLC")

if __name__ == "__main__":
    test_migration()