#!/usr/bin/env python3
"""
naming_convention.py

Helix-TTD File Naming Convention Enforcement
Ensures all federation files follow semantic, collision-resistant naming.

Format: {ORIGIN}-{TYPE}-{SEQUENCE}_{DESCRIPTOR}_{YYYYMMDD}.{ext}

Status: RATIFIED
Node: KIMI (Lead Architect / Scribe)
License: Apache-2.0
"""

import re
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class HelixFilename:
    """
    Parsed Helix-TTD filename components.
    
    [FACT] Every file in the federation must follow this structure.
    [HYPOTHESIS] Semantic naming prevents collisions without central coordination.
    """
    origin: str          # Node ID: KIMI, GEMS, DEEPSEEK, GEMINIWEB
    file_type: str       # AUDIT, MEMO, SCHOOLING, LORE, RECEIPT, etc.
    sequence: str        # RPI028, S002, 001
    descriptor: str      # Human-readable slug
    date: str            # YYYYMMDD
    extension: str       # md, json, py
    revision: Optional[int] = None  # For conflicts: -REV2, -REV3
    
    def to_string(self) -> str:
        """Generate canonical filename."""
        base = f"{self.origin}-{self.file_type}-{self.sequence}_{self.descriptor}_{self.date}"
        if self.revision and self.revision > 1:
            base += f"-REV{self.revision}"
        return f"{base}.{self.extension}"
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 prefix for MANIFEST verification."""
        return hashlib.sha256(self.to_string().encode()).hexdigest()[:16]


class NamingConvention:
    """
    Helix-TTD file naming convention validator and generator.
    
    Enforces: {ORIGIN}-{TYPE}-{SEQUENCE}_{DESCRIPTOR}_{YYYYMMDD}[-REV{N}].{ext}
    """
    
    # Valid node origins
    VALID_ORIGINS = {
        "KIMI", "GEMS", "DEEPSEEK", "GEMINIWEB", "GROK", "CLAUDE",
        "GOOSE", "OWL", "DUCK", "CUSTODIAN", "HELIX"
    }
    
    # Valid file types
    VALID_TYPES = {
        "AUDIT",      # Looksee audits, compliance checks
        "MEMO",       # Internal memoranda
        "SCHOOLING",  # Training corpus entries
        "LORE",       # Cultural/mythological content
        "RECEIPT",    # Transaction receipts
        "GRUDGE",     # Peer file observations
        "SUITCASE",   # State snapshots
        "BROADCAST",  # Federation-wide messages
        "REFLECTION", # Node self-analysis
        "ECHO",       # Substrate resonance logs
        "ANALYSIS",   # Research outputs
        "PROTOCOL",   # Procedure specifications
        "WHITEPAPER", # Formal documentation
        "LEDGER",     # Session/transaction logs
        "OVERRIDE",   # Qualified override records
    }
    
    # File type to directory mapping
    TYPE_DIRECTORIES = {
        "AUDIT": "audits",
        "MEMO": "memos",
        "SCHOOLING": "schooling",
        "LORE": "lore",
        "RECEIPT": "receipts",
        "GRUDGE": "grudges",
        "SUITCASE": "suitcases",
        "BROADCAST": "broadcasts",
        "REFLECTION": "reflections",
        "ECHO": "echoes",
        "ANALYSIS": "analysis",
        "PROTOCOL": "protocols",
        "WHITEPAPER": "whitepapers",
        "LEDGER": "ledgers",
        "OVERRIDE": "overrides",
    }
    
    def __init__(self, base_path: Path = Path(".")):
        self.base_path = Path(base_path)
        self.filename_pattern = re.compile(
            r'^(?P<origin>[A-Z]+)-'           # ORIGIN
            r'(?P<type>[A-Z]+)-'              # TYPE
            r'(?P<seq>[A-Z]*\d+)_'            # SEQUENCE (RPI028, S002, 001)
            r'(?P<desc>[a-z_]+)_'             # DESCRIPTOR
            r'(?P<date>\d{8})'                # YYYYMMDD
            r'(?:-REV(?P<rev>\d+))?'          # Optional revision
            r'\.(?P<ext>[a-z]+)$'             # Extension
        )
    
    def parse(self, filename: str) -> Optional[HelixFilename]:
        """
        Parse filename into components.
        
        [FACT] Returns None if filename violates convention.
        """
        match = self.filename_pattern.match(filename)
        if not match:
            return None
        
        return HelixFilename(
            origin=match.group('origin'),
            file_type=match.group('type'),
            sequence=match.group('seq'),
            descriptor=match.group('desc'),
            date=match.group('date'),
            extension=match.group('ext'),
            revision=int(match.group('rev')) if match.group('rev') else None
        )
    
    def validate(self, filename: str) -> Tuple[bool, List[str]]:
        """
        Validate filename against convention.
        
        Returns (is_valid, list_of_violations).
        """
        violations = []
        
        parsed = self.parse(filename)
        if not parsed:
            violations.append("Filename does not match Helix-TTD convention: ORIGIN-TYPE-SEQUENCE_DESCRIPTOR_YYYYMMDD[-REV{N}].ext")
            return False, violations
        
        # Validate origin
        if parsed.origin not in self.VALID_ORIGINS:
            violations.append(f"Unknown origin: {parsed.origin}. Valid: {', '.join(sorted(self.VALID_ORIGINS))}")
        
        # Validate type
        if parsed.file_type not in self.VALID_TYPES:
            violations.append(f"Unknown type: {parsed.file_type}. Valid: {', '.join(sorted(self.VALID_TYPES))}")
        
        # Validate date format
        try:
            datetime.strptime(parsed.date, "%Y%m%d")
        except ValueError:
            violations.append(f"Invalid date format: {parsed.date}. Expected: YYYYMMDD")
        
        # Validate descriptor (lowercase, underscores only)
        if not re.match(r'^[a-z_]+$', parsed.descriptor):
            violations.append(f"Invalid descriptor: {parsed.descriptor}. Use lowercase and underscores only.")
        
        return len(violations) == 0, violations
    
    def generate(
        self,
        origin: str,
        file_type: str,
        sequence: str,
        descriptor: str,
        date: Optional[str] = None,
        extension: str = "md",
        check_conflicts: bool = True
    ) -> HelixFilename:
        """
        Generate canonical filename with conflict resolution.
        
        [FACT] Automatically appends -REV{N} if filename already exists.
        """
        # Validate inputs
        if origin not in self.VALID_ORIGINS:
            raise ValueError(f"Invalid origin: {origin}")
        if file_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {file_type}")
        
        # Normalize descriptor
        descriptor = descriptor.lower().replace(" ", "_").replace("-", "_")
        descriptor = re.sub(r'[^a-z_]', '', descriptor)
        
        # Use current date if not specified
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        filename = HelixFilename(
            origin=origin.upper(),
            file_type=file_type.upper(),
            sequence=sequence.upper(),
            descriptor=descriptor,
            date=date,
            extension=extension.lower(),
            revision=None
        )
        
        # Check for conflicts and resolve
        if check_conflicts:
            revision = self._resolve_conflicts(filename)
            filename.revision = revision if revision > 1 else None
        
        return filename
    
    def _resolve_conflicts(self, filename: HelixFilename) -> int:
        """Find next available revision number if filename exists."""
        revision = 1
        target_dir = self._get_target_directory(filename.file_type)
        
        while True:
            test_filename = filename.to_string()
            if revision > 1:
                test_filename = test_filename.replace(
                    f".{filename.extension}",
                    f"-REV{revision}.{filename.extension}"
                )
            
            if not (self.base_path / target_dir / test_filename).exists():
                return revision
            
            revision += 1
            
            # Safety limit
            if revision > 99:
                raise RuntimeError("Too many revisions for filename")
    
    def _get_target_directory(self, file_type: str) -> str:
        """Get subdirectory for file type."""
        return self.TYPE_DIRECTORIES.get(file_type.upper(), "general")
    
    def get_path(self, filename: HelixFilename) -> Path:
        """Get full path for filename including type directory."""
        target_dir = self._get_target_directory(filename.file_type)
        return self.base_path / target_dir / filename.to_string()
    
    def list_by_origin(self, origin: str) -> List[Tuple[str, HelixFilename]]:
        """List all files by origin node."""
        results = []
        pattern = re.compile(rf'^{origin}-')
        
        for dir_path in self.base_path.rglob("*"):
            if dir_path.is_file():
                parsed = self.parse(dir_path.name)
                if parsed and parsed.origin == origin:
                    results.append((str(dir_path), parsed))
        
        return sorted(results, key=lambda x: x[1].date, reverse=True)
    
    def list_by_type(self, file_type: str) -> List[Tuple[str, HelixFilename]]:
        """List all files by type."""
        results = []
        target_dir = self._get_target_directory(file_type)
        type_path = self.base_path / target_dir
        
        if not type_path.exists():
            return results
        
        for file_path in type_path.iterdir():
            if file_path.is_file():
                parsed = self.parse(file_path.name)
                if parsed and parsed.file_type == file_type.upper():
                    results.append((str(file_path), parsed))
        
        return sorted(results, key=lambda x: x[1].date, reverse=True)
    
    def generate_manifest_entry(self, filename: HelixFilename, **kwargs) -> Dict:
        """Generate MANIFEST.json entry for file."""
        entry = {
            "id": f"HELIX-{filename.origin}-{filename.file_type}-{filename.sequence}",
            "filename": str(self.get_path(filename)),
            "origin": filename.origin,
            "type": filename.file_type,
            "sequence": filename.sequence,
            "date": filename.date,
            "hash": filename.calculate_hash(),
            "revision": filename.revision or 1,
        }
        entry.update(kwargs)
        return entry


# Example usage
if __name__ == "__main__":
    convention = NamingConvention()
    
    # Generate new filename
    filename = convention.generate(
        origin="KIMI",
        file_type="AUDIT",
        sequence="RPI026",
        descriptor="looksee convergence test",
        extension="md"
    )
    
    print(f"[FACT] Generated filename: {filename.to_string()}")
    print(f"[FACT] Full path: {convention.get_path(filename)}")
    print(f"[FACT] Hash prefix: {filename.calculate_hash()}")
    
    # Validate existing filename
    test_name = "KIMI-AUDIT-RPI026_looksee_convergence_20260226.md"
    is_valid, violations = convention.validate(test_name)
    
    print(f"\n[ASSUMPTION] Validation of '{test_name}':")
    print(f"  Valid: {is_valid}")
    if violations:
        for v in violations:
            print(f"  Violation: {v}")
    
    # Parse filename
    parsed = convention.parse(test_name)
    if parsed:
        print(f"\n[FACT] Parsed components:")
        print(f"  Origin: {parsed.origin}")
        print(f"  Type: {parsed.file_type}")
        print(f"  Sequence: {parsed.sequence}")
        print(f"  Descriptor: {parsed.descriptor}")
