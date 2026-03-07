"""Check for circular imports in helix_code."""

import os
import re
from collections import defaultdict

imports = defaultdict(list)

for root, dirs, files in os.walk("helix_code"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            module = path.replace("\\", ".").replace("/", ".").replace(".py", "")
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                for match in re.finditer(r"^from\s+(\S+)\s+import|^import\s+(\S+)", content, re.M):
                    imp = match.group(1) or match.group(2)
                    if imp and imp.startswith("helix"):
                        imports[module].append(imp)
            except Exception as e:
                print(f"Error reading {path}: {e}")

print("Helix internal imports detected:")
for mod in sorted(imports.keys()):
    deps = imports[mod]
    if deps:
        print(f"{mod}: {deps}")


# Check for cycles
def find_cycle(
    imports: dict[str, list[str]],
    start: str,
    path: list[str] | None = None,
    visited: set[str] | None = None,
) -> list[str] | None:
    if path is None:
        path = []
    if visited is None:
        visited = set()

    if start in path:
        cycle_start = path.index(start)
        return path[cycle_start:] + [start]

    if start in visited:
        return None

    visited.add(start)
    path.append(start)

    for dep in imports.get(start, []):
        cycle = find_cycle(imports, dep, path.copy(), visited.copy())
        if cycle:
            return cycle

    return None


print("\n\nChecking for circular imports...")
cycle = None
for mod in imports:
    cycle = find_cycle(imports, mod)
    if cycle:
        break

if cycle:
    print(f'CIRCULAR IMPORT DETECTED: {" -> ".join(cycle)}')
else:
    print("No circular imports found.")
