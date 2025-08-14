#!/usr/bin/env python3
"""
Enterprise Package Mirror Creation System for Electrum-GLC
This script creates a local, immutable package mirror for deterministic builds.
"""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import tempfile
import shutil

class PackageMirror:
    """Manages the local package mirror for deterministic builds."""
    
    def __init__(self, mirror_path: Path):
        self.mirror_path = mirror_path
        self.manifest_path = mirror_path / "manifest.json"
        self.packages_path = mirror_path / "packages"
        self.python_wheels_path = self.packages_path / "python" / "wheels"
        self.python_source_path = self.packages_path / "python" / "source"
        self.wine_path = self.packages_path / "wine"
        self.verification_path = self.packages_path / "verification"
        
        # Create directory structure
        for path in [self.python_wheels_path, self.python_source_path, 
                     self.wine_path, self.verification_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def load_manifest(self) -> Dict:
        """Load or create the package manifest."""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0",
            "packages": {},
            "wine": {},
            "python": {}
        }
    
    def save_manifest(self, manifest: Dict):
        """Save the package manifest with proper formatting."""
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        print(f"✓ Manifest saved to {self.manifest_path}")
    
    def calculate_sha256(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def download_file(self, url: str, dest_path: Path, expected_hash: Optional[str] = None) -> bool:
        """Download a file and verify its hash."""
        print(f"  Downloading {url}")
        
        try:
            # Download to temporary file first
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                urllib.request.urlretrieve(url, tmp_file.name)
                
                # Verify hash if provided
                if expected_hash:
                    actual_hash = self.calculate_sha256(Path(tmp_file.name))
                    if actual_hash.lower() != expected_hash.lower():
                        print(f"  ✗ Hash mismatch for {url}")
                        print(f"    Expected: {expected_hash}")
                        print(f"    Got:      {actual_hash}")
                        os.unlink(tmp_file.name)
                        return False
                
                # Move to destination
                shutil.move(tmp_file.name, dest_path)
                print(f"  ✓ Downloaded to {dest_path}")
                return True
                
        except Exception as e:
            print(f"  ✗ Failed to download {url}: {e}")
            return False
    
    def process_requirements_file(self, req_file: Path) -> List[Tuple[str, str, str]]:
        """Parse requirements file and extract package info."""
        packages = []
        
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # Parse package line
            if '==' in line:
                # Handle multi-line entries
                full_line = line
                while i + 1 < len(lines) and lines[i + 1].strip().startswith('--hash='):
                    i += 1
                    full_line += ' ' + lines[i].strip()
                
                # Extract package name and version
                parts = full_line.split('==')
                name = parts[0].strip()
                
                # Extract version and hash
                version_parts = parts[1].split()
                version = version_parts[0].strip(' \\')
                
                # Extract hash
                hash_value = None
                for part in full_line.split():
                    if part.startswith('--hash=sha256:'):
                        hash_value = part.replace('--hash=sha256:', '')
                        break
                
                if hash_value:
                    packages.append((name, version, hash_value))
            
            i += 1
        
        return packages
    
    def mirror_python_packages(self, requirements_dir: Path):
        """Mirror all Python packages from requirements files."""
        print("\n=== Mirroring Python Packages ===")
        
        manifest = self.load_manifest()
        
        # Process all requirements files
        req_files = [
            "requirements.txt",
            "requirements-build-base.txt",
            "requirements-build-wine.txt",
            "requirements-binaries.txt",
            "requirements-hw.txt"
        ]
        
        all_packages = []
        for req_file in req_files:
            req_path = requirements_dir / req_file
            if req_path.exists():
                print(f"\nProcessing {req_file}...")
                packages = self.process_requirements_file(req_path)
                all_packages.extend(packages)
        
        # Remove duplicates
        seen = set()
        unique_packages = []
        for pkg in all_packages:
            key = f"{pkg[0]}-{pkg[1]}"
            if key not in seen:
                seen.add(key)
                unique_packages.append(pkg)
        
        print(f"\nFound {len(unique_packages)} unique packages to mirror")
        
        # Download packages
        for name, version, expected_hash in unique_packages:
            pkg_key = f"{name}-{version}"
            
            # Skip if already mirrored and hash matches
            if pkg_key in manifest.get("packages", {}):
                if manifest["packages"][pkg_key]["hash"] == expected_hash:
                    print(f"✓ {pkg_key} already mirrored")
                    continue
            
            print(f"\nMirroring {name}=={version}")
            
            # Try wheel first, then source
            success = False
            
            # Try to download wheel
            wheel_filename = f"{name.replace('-', '_')}-{version}-py3-none-any.whl"
            wheel_url = f"https://files.pythonhosted.org/packages/py3/{name[0]}/{name}/{wheel_filename}"
            wheel_path = self.python_wheels_path / wheel_filename
            
            # Special case for packages with known wheel URLs
            if name == "pip" and version == "24.0":
                wheel_url = "https://files.pythonhosted.org/packages/8a/6a/19e9fe04fca059ccf770861c7d5721ab4c2aebc539889e97c7977528a53b/pip-24.0-py3-none-any.whl"
            elif name == "setuptools" and version == "69.0.3":
                wheel_url = "https://files.pythonhosted.org/packages/55/3a/5121b58b578a598b269537e09a316ad2594d6aafab0798e96bfb817fd954/setuptools-69.0.3-py3-none-any.whl"
            
            if self.download_file(wheel_url, wheel_path, expected_hash):
                success = True
                manifest["packages"][pkg_key] = {
                    "name": name,
                    "version": version,
                    "hash": expected_hash,
                    "type": "wheel",
                    "filename": wheel_filename,
                    "path": str(wheel_path.relative_to(self.mirror_path))
                }
            else:
                # Try source distribution
                source_filename = f"{name}-{version}.tar.gz"
                source_url = f"https://files.pythonhosted.org/packages/source/{name[0]}/{name}/{source_filename}"
                source_path = self.python_source_path / source_filename
                
                # For some packages, we might need to check PyPI API
                if not success:
                    try:
                        # Get package info from PyPI
                        api_url = f"https://pypi.org/pypi/{name}/{version}/json"
                        with urllib.request.urlopen(api_url) as response:
                            data = json.loads(response.read())
                            
                        # Find the right file
                        for file_info in data.get("urls", []):
                            if file_info["digests"]["sha256"] == expected_hash:
                                file_url = file_info["url"]
                                file_name = file_info["filename"]
                                
                                if file_name.endswith(".whl"):
                                    dest_path = self.python_wheels_path / file_name
                                else:
                                    dest_path = self.python_source_path / file_name
                                
                                if self.download_file(file_url, dest_path, expected_hash):
                                    success = True
                                    manifest["packages"][pkg_key] = {
                                        "name": name,
                                        "version": version,
                                        "hash": expected_hash,
                                        "type": "wheel" if file_name.endswith(".whl") else "source",
                                        "filename": file_name,
                                        "path": str(dest_path.relative_to(self.mirror_path))
                                    }
                                    break
                    except Exception as e:
                        print(f"  Failed to fetch from PyPI API: {e}")
            
            if not success:
                print(f"  ✗ Failed to mirror {name}=={version}")
            else:
                self.save_manifest(manifest)
    
    def mirror_wine_components(self):
        """Mirror Wine and Python installers for Windows build."""
        print("\n=== Mirroring Wine Components ===")
        
        manifest = self.load_manifest()
        
        # Python 3.11.9 MSI files
        python_version = "3.11.9"
        python_components = [
            ("core.msi", "a4c6e9c8c35c847b3ccb2c1e9e3a34de6e0e3ce09e4ad4b7a94ad5a3e7c09c8f"),
            ("dev.msi", "b5e3e7d8c9f8d7a8c5f9e8a7d6c5b4a3e2d1c0b9a8e7d6c5b4a3e2d1c0b9a8e7"),
            ("exe.msi", "c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7"),
            ("lib.msi", "d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8"),
            ("pip.msi", "e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9"),
            ("tools.msi", "f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0")
        ]
        
        # Note: These hashes are placeholders - we need to get the actual hashes
        print(f"\nNote: Wine component mirroring requires manual download of Python MSI files")
        print(f"Please download Python {python_version} MSI files from python.org")
        
        manifest["wine"]["python_version"] = python_version
        manifest["wine"]["components"] = []
        
        self.save_manifest(manifest)
    
    def verify_mirror(self) -> bool:
        """Verify all packages in the mirror match their expected hashes."""
        print("\n=== Verifying Package Mirror ===")
        
        manifest = self.load_manifest()
        all_valid = True
        
        for pkg_key, pkg_info in manifest.get("packages", {}).items():
            pkg_path = self.mirror_path / pkg_info["path"]
            
            if not pkg_path.exists():
                print(f"✗ Missing: {pkg_key}")
                all_valid = False
                continue
            
            actual_hash = self.calculate_sha256(pkg_path)
            if actual_hash != pkg_info["hash"]:
                print(f"✗ Hash mismatch: {pkg_key}")
                print(f"  Expected: {pkg_info['hash']}")
                print(f"  Got:      {actual_hash}")
                all_valid = False
            else:
                print(f"✓ Verified: {pkg_key}")
        
        return all_valid


def main():
    """Main entry point for package mirror creation."""
    
    # Setup paths
    script_dir = Path(__file__).parent
    mirror_dir = script_dir / "mirror"
    requirements_dir = script_dir
    
    print("=== Electrum-GLC Package Mirror Creator ===")
    print(f"Mirror directory: {mirror_dir}")
    
    # Create mirror manager
    mirror = PackageMirror(mirror_dir)
    
    # Mirror Python packages
    mirror.mirror_python_packages(requirements_dir)
    
    # Mirror Wine components (placeholder for now)
    mirror.mirror_wine_components()
    
    # Verify mirror
    if mirror.verify_mirror():
        print("\n✓ Package mirror created successfully!")
    else:
        print("\n✗ Package mirror has errors. Please fix before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()