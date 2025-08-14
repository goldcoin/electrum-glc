#!/usr/bin/env python3
"""Test script to verify checkpoint functionality"""

import json
import sys

def verify_checkpoints():
    """Verify the checkpoints file is properly formatted and contains expected data"""
    
    print("Checkpoint Verification Test")
    print("=" * 50)
    
    # Load checkpoints
    with open('electrum/checkpoints.json', 'r') as f:
        checkpoints = json.load(f)
    
    print(f"Total checkpoints: {len(checkpoints)}")
    
    # Check format
    if not all(isinstance(cp, list) and len(cp) == 2 for cp in checkpoints):
        print("ERROR: Invalid checkpoint format!")
        return False
    
    # Get first and last checkpoints
    first = checkpoints[0]
    last = checkpoints[-1]
    
    print(f"\nFirst checkpoint:")
    print(f"  Height: {first[1]:,}")
    print(f"  Hash: {first[0][:32]}...")
    
    print(f"\nLast checkpoint:")
    print(f"  Height: {last[1]:,}")
    print(f"  Hash: {last[0][:32]}...")
    
    # Calculate approximate sync time
    current_height = 2332511  # From the latest data
    sync_blocks = current_height - last[1]
    sync_days = sync_blocks / 720  # ~720 blocks per day with 2 min block time
    
    print(f"\nSync requirement:")
    print(f"  Blocks to sync: {sync_blocks:,}")
    print(f"  Approximate days: {sync_days:.1f}")
    print(f"  Approximate months: {sync_days/30:.1f}")
    
    # Verify heights are increasing
    heights = [cp[1] for cp in checkpoints]
    if heights != sorted(heights):
        print("ERROR: Checkpoint heights are not in ascending order!")
        return False
    
    # Check for duplicates
    if len(set(heights)) != len(heights):
        print("ERROR: Duplicate heights found!")
        return False
    
    print("\n✓ All checkpoint validations passed!")
    print("\nExpected behavior when wallet starts:")
    print(f"1. Wallet should start syncing from block {last[1]:,}")
    print(f"2. Should download ~{sync_blocks:,} blocks ({sync_days:.1f} days of data)")
    print("3. No need to sync from genesis or block 725,000")
    
    return True

if __name__ == "__main__":
    success = verify_checkpoints()
    sys.exit(0 if success else 1)