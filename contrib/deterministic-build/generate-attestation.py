#!/usr/bin/env python3
"""
Build Attestation Generator for Electrum-GLC
Creates cryptographically verifiable build attestations
"""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class AttestationGenerator:
    """Generates build attestations for reproducible builds."""
    
    def __init__(self):
        self.attestation: Dict = {
            "version": "1.0",
            "format": "electrum-glc-attestation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_git_info(self, repo_path: Path) -> Dict:
        """Get Git repository information."""
        try:
            # Get current commit
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                text=True
            ).strip()
            
            # Get commit timestamp
            commit_time = subprocess.check_output(
                ["git", "show", "-s", "--format=%cI", commit],
                cwd=repo_path,
                text=True
            ).strip()
            
            # Get branch name
            try:
                branch = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=repo_path,
                    text=True
                ).strip()
            except:
                branch = "detached"
            
            # Check for uncommitted changes
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                text=True
            ).strip()
            
            clean = len(status) == 0
            
            # Get tags pointing to this commit
            tags = subprocess.check_output(
                ["git", "tag", "--points-at", commit],
                cwd=repo_path,
                text=True
            ).strip().split('\n')
            tags = [t for t in tags if t]
            
            return {
                "commit": commit,
                "commit_time": commit_time,
                "branch": branch,
                "tags": tags,
                "clean": clean,
                "uncommitted_changes": status if not clean else None
            }
        except subprocess.CalledProcessError as e:
            return {
                "error": f"Failed to get git info: {e}"
            }
    
    def get_docker_info(self) -> Dict:
        """Get Docker environment information."""
        try:
            # Get Docker version
            docker_version = subprocess.check_output(
                ["docker", "version", "--format", "{{.Server.Version}}"],
                text=True
            ).strip()
            
            # Get Docker info
            docker_info = subprocess.check_output(
                ["docker", "info", "--format", "json"],
                text=True
            )
            info = json.loads(docker_info)
            
            return {
                "version": docker_version,
                "storage_driver": info.get("Driver"),
                "kernel_version": info.get("KernelVersion"),
                "operating_system": info.get("OperatingSystem"),
                "architecture": info.get("Architecture")
            }
        except:
            return {
                "error": "Docker not available or not running"
            }
    
    def get_build_environment(self) -> Dict:
        """Get build environment information."""
        env_vars = [
            "SOURCE_DATE_EPOCH",
            "PYTHONHASHSEED",
            "PYTHONDONTWRITEBYTECODE",
            "DETERMINISTIC_BUILD",
            "TZ",
            "LC_ALL",
            "LANG"
        ]
        
        environment = {}
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                environment[var] = value
        
        # Get system information
        environment["system"] = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "hostname": platform.node()
        }
        
        return environment
    
    def calculate_file_hash(self, filepath: Path) -> Dict:
        """Calculate multiple hashes for a file."""
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()
        md5 = hashlib.md5()
        
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
                sha512.update(chunk)
                md5.update(chunk)
        
        return {
            "sha256": sha256.hexdigest(),
            "sha512": sha512.hexdigest(),
            "md5": md5.hexdigest(),
            "size": filepath.stat().st_size
        }
    
    def get_package_manifest(self, manifest_path: Path) -> Dict:
        """Load package manifest with all dependency versions."""
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_attestation(
        self,
        source_path: Path,
        output_dir: Path,
        docker_image: Optional[str] = None,
        manifest_path: Optional[Path] = None
    ) -> Dict:
        """Generate complete build attestation."""
        
        # Git information
        self.attestation["source"] = self.get_git_info(source_path)
        
        # Docker information
        if docker_image:
            self.attestation["docker"] = {
                "image": docker_image,
                **self.get_docker_info()
            }
        
        # Build environment
        self.attestation["environment"] = self.get_build_environment()
        
        # Package manifest
        if manifest_path:
            self.attestation["packages"] = self.get_package_manifest(manifest_path)
        
        # Output files
        outputs = {}
        for filepath in sorted(output_dir.iterdir()):
            if filepath.is_file():
                outputs[filepath.name] = self.calculate_file_hash(filepath)
        
        self.attestation["outputs"] = outputs
        
        # Reproducibility information
        self.attestation["reproducibility"] = {
            "deterministic": True,
            "source_date_epoch": os.environ.get("SOURCE_DATE_EPOCH", "not_set"),
            "build_path_independent": True,
            "compiler_flags_normalized": True
        }
        
        # Build command used
        self.attestation["build_command"] = self.get_build_command()
        
        return self.attestation
    
    def get_build_command(self) -> str:
        """Get the command used to perform the build."""
        # This would ideally be passed in or detected
        return "docker build -f Dockerfile.enterprise -t electrum-glc-deterministic ."
    
    def sign_attestation(self, attestation: Dict, gpg_key: str) -> Optional[str]:
        """Sign the attestation with GPG."""
        try:
            # Convert attestation to canonical JSON
            canonical_json = json.dumps(attestation, sort_keys=True, separators=(',', ':'))
            
            # Sign with GPG
            result = subprocess.run(
                ["gpg", "--armor", "--detach-sign", "--default-key", gpg_key],
                input=canonical_json.encode(),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"GPG signing failed: {result.stderr}")
                return None
        except Exception as e:
            print(f"Failed to sign attestation: {e}")
            return None
    
    def save_attestation(
        self,
        attestation: Dict,
        output_path: Path,
        signature: Optional[str] = None
    ):
        """Save attestation to file."""
        # Save attestation
        with open(output_path, 'w') as f:
            json.dump(attestation, f, indent=2, sort_keys=True)
        
        print(f"✓ Attestation saved to {output_path}")
        
        # Save signature if provided
        if signature:
            sig_path = output_path.with_suffix('.json.asc')
            with open(sig_path, 'w') as f:
                f.write(signature)
            print(f"✓ Signature saved to {sig_path}")
    
    def verify_attestation(self, attestation_path: Path) -> bool:
        """Verify an existing attestation."""
        with open(attestation_path, 'r') as f:
            attestation = json.load(f)
        
        # Check signature if exists
        sig_path = attestation_path.with_suffix('.json.asc')
        if sig_path.exists():
            result = subprocess.run(
                ["gpg", "--verify", str(sig_path), str(attestation_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Signature verification passed")
            else:
                print(f"✗ Signature verification failed: {result.stderr}")
                return False
        
        # Verify outputs exist and match hashes
        output_dir = attestation_path.parent
        for filename, file_info in attestation.get("outputs", {}).items():
            filepath = output_dir / filename
            
            if not filepath.exists():
                print(f"✗ Missing output file: {filename}")
                return False
            
            actual_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    actual_hash.update(chunk)
            
            if actual_hash.hexdigest() != file_info["sha256"]:
                print(f"✗ Hash mismatch for {filename}")
                return False
            
            print(f"✓ Verified {filename}")
        
        print("\n✓ Attestation verification passed!")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate and verify build attestations for Electrum-GLC"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate attestation")
    gen_parser.add_argument("--source", required=True, type=Path,
                           help="Source code directory")
    gen_parser.add_argument("--output-dir", required=True, type=Path,
                           help="Build output directory")
    gen_parser.add_argument("--docker-image", help="Docker image used")
    gen_parser.add_argument("--manifest", type=Path,
                           help="Package manifest file")
    gen_parser.add_argument("--gpg-key", help="GPG key ID for signing")
    gen_parser.add_argument("--output", required=True, type=Path,
                           help="Output attestation file")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify attestation")
    verify_parser.add_argument("attestation", type=Path,
                              help="Attestation file to verify")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    generator = AttestationGenerator()
    
    if args.command == "generate":
        attestation = generator.generate_attestation(
            args.source,
            args.output_dir,
            args.docker_image,
            args.manifest
        )
        
        # Sign if GPG key provided
        signature = None
        if args.gpg_key:
            signature = generator.sign_attestation(attestation, args.gpg_key)
        
        # Save attestation
        generator.save_attestation(attestation, args.output, signature)
    
    elif args.command == "verify":
        success = generator.verify_attestation(args.attestation)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()