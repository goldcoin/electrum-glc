#!/usr/bin/env python3
"""
Build Verification System for Electrum-GLC
Ensures deterministic builds produce expected outputs
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class BuildVerifier:
    """Verifies build outputs match expected hashes."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def calculate_sha256(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_file(self, filepath: Path, expected_hash: str) -> bool:
        """Verify a single file matches its expected hash."""
        if not filepath.exists():
            self.errors.append(f"Missing file: {filepath}")
            return False
        
        actual_hash = self.calculate_sha256(filepath)
        if actual_hash != expected_hash:
            self.errors.append(
                f"Hash mismatch for {filepath.name}:\n"
                f"  Expected: {expected_hash}\n"
                f"  Got:      {actual_hash}"
            )
            return False
        
        print(f"✓ Verified: {filepath.name}")
        return True
    
    def verify_directory(self, directory: Path, expected_files: Dict[str, str]) -> bool:
        """Verify all files in a directory match expected hashes."""
        all_valid = True
        
        # Check for expected files
        for filename, expected_hash in expected_files.items():
            filepath = directory / filename
            if not self.verify_file(filepath, expected_hash):
                all_valid = False
        
        # Check for unexpected files
        actual_files = set(f.name for f in directory.iterdir() if f.is_file())
        expected_filenames = set(expected_files.keys())
        unexpected = actual_files - expected_filenames
        
        if unexpected:
            self.warnings.append(
                f"Unexpected files found: {', '.join(sorted(unexpected))}"
            )
        
        return all_valid
    
    def load_expected_hashes(self, filepath: Path) -> Dict[str, str]:
        """Load expected hashes from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if "outputs" in data:
            return data["outputs"]
        elif "files" in data:
            return data["files"]
        else:
            # Assume flat structure
            return data
    
    def generate_hash_file(self, directory: Path, output_path: Path):
        """Generate a hash file for all files in a directory."""
        hashes = {}
        
        for filepath in sorted(directory.iterdir()):
            if filepath.is_file():
                hashes[filepath.name] = self.calculate_sha256(filepath)
        
        with open(output_path, 'w') as f:
            json.dump(hashes, f, indent=2, sort_keys=True)
        
        print(f"Generated hash file: {output_path}")
    
    def compare_builds(self, dir1: Path, dir2: Path) -> bool:
        """Compare two build directories for reproducibility."""
        print(f"\nComparing builds:")
        print(f"  Build 1: {dir1}")
        print(f"  Build 2: {dir2}")
        
        files1 = {f.name: self.calculate_sha256(f) 
                  for f in dir1.iterdir() if f.is_file()}
        files2 = {f.name: self.calculate_sha256(f) 
                  for f in dir2.iterdir() if f.is_file()}
        
        # Check for missing files
        only_in_1 = set(files1.keys()) - set(files2.keys())
        only_in_2 = set(files2.keys()) - set(files1.keys())
        
        if only_in_1:
            self.errors.append(f"Files only in build 1: {', '.join(sorted(only_in_1))}")
        if only_in_2:
            self.errors.append(f"Files only in build 2: {', '.join(sorted(only_in_2))}")
        
        # Compare common files
        common_files = set(files1.keys()) & set(files2.keys())
        mismatches = []
        
        for filename in sorted(common_files):
            if files1[filename] != files2[filename]:
                mismatches.append(filename)
                self.errors.append(
                    f"Hash mismatch for {filename}:\n"
                    f"  Build 1: {files1[filename]}\n"
                    f"  Build 2: {files2[filename]}"
                )
            else:
                print(f"  ✓ {filename} matches")
        
        if not self.errors:
            print("\n✓ Builds are reproducible!")
            return True
        else:
            print(f"\n✗ Builds differ in {len(mismatches)} files")
            return False
    
    def verify_signature(self, filepath: Path, signature_path: Path) -> bool:
        """Verify GPG signature of a file."""
        # This would use gpg to verify signatures
        # For now, just check that signature file exists
        if not signature_path.exists():
            self.warnings.append(f"No signature found for {filepath.name}")
            return False
        
        # TODO: Implement actual GPG verification
        print(f"  ℹ Signature verification not yet implemented for {filepath.name}")
        return True
    
    def report(self):
        """Print verification report."""
        print("\n" + "=" * 60)
        print("BUILD VERIFICATION REPORT")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All verifications passed!")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point for build verification."""
    parser = argparse.ArgumentParser(description="Verify Electrum-GLC build outputs")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify build outputs")
    verify_parser.add_argument("--expected", required=True, type=Path,
                              help="Path to expected hashes JSON file")
    verify_parser.add_argument("--actual", required=True, type=Path,
                              help="Path to directory with actual build outputs")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate hash file")
    generate_parser.add_argument("--directory", required=True, type=Path,
                                help="Directory to generate hashes for")
    generate_parser.add_argument("--output", required=True, type=Path,
                                help="Output JSON file path")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two builds")
    compare_parser.add_argument("--build1", required=True, type=Path,
                               help="First build directory")
    compare_parser.add_argument("--build2", required=True, type=Path,
                               help="Second build directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    verifier = BuildVerifier()
    
    if args.command == "verify":
        expected = verifier.load_expected_hashes(args.expected)
        success = verifier.verify_directory(args.actual, expected)
        verifier.report()
        sys.exit(0 if success else 1)
    
    elif args.command == "generate":
        verifier.generate_hash_file(args.directory, args.output)
    
    elif args.command == "compare":
        success = verifier.compare_builds(args.build1, args.build2)
        verifier.report()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()