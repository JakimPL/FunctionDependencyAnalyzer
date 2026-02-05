from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict

from fda.importer.config import ImportConfig
from fda.importer.registry import ModuleRegistry
from fda.importer.resolver import ImportResolver
from fda.importer.spec import Module, ModuleAvailability, ModuleSpec, Symbol, SymbolKind
from fda.parser import parse_python_file
from fda.resolver import NameResolver


class ModuleAnalyzer:
    def __init__(self, project_root: Path, config: ImportConfig) -> None:
        self.project_root = project_root
        self.config = config
        self.registry = ModuleRegistry(config)
        self.import_resolver = ImportResolver(config)

    def __call__(self, filepath: Path) -> ModuleRegistry:
        return self.analyze_project(filepath)

    def analyze_module(self, filepath: Path) -> Module:
        tree = parse_python_file(str(filepath))

        module_name = self._filepath_to_module_name(filepath)

        imports = self.import_resolver.collect_imports(tree, filepath.parent)

        name_resolver = NameResolver(filepath)
        wrappers, _ = name_resolver.resolve(tree)

        module_spec = self.import_resolver.resolve_module_spec(module_name, filepath)
        if not module_spec:
            module_spec = ModuleSpec(
                fqn=module_name,
                origin=filepath,
                is_package=filepath.name == "__init__.py",
            )

        exports = self._extract_exports(tree, module_spec.fqn, wrappers)

        module = Module(
            spec=module_spec,
            ast_tree=tree,
            exports=exports,
            imports=imports,
            wrappers=wrappers,
            availability=ModuleAvailability.INSTALLED,
        )

        self.registry.register_module(module)

        for import_stmt in imports:
            if not self.registry.has(import_stmt.target_module):
                target_spec = self.import_resolver.resolve_module_spec(import_stmt.target_module)
                if target_spec and target_spec.origin:
                    if self.config.is_internal_module(target_spec.origin):
                        if not self.registry.is_pending(import_stmt.target_module):
                            self.registry.mark_pending(import_stmt.target_module)

        return module

    def analyze_project(self, entry_point: Path) -> ModuleRegistry:
        self.analyze_module(entry_point)

        while True:
            pending = list(self.registry.pending)
            if not pending:
                break

            for module_fqn in pending:
                self.registry.unmark_pending(module_fqn)

                spec = self.import_resolver.resolve_module_spec(module_fqn)
                if spec and spec.origin and self.config.is_internal_module(spec.origin):
                    try:
                        self.analyze_module(spec.origin)
                    except Exception as e:
                        print(f"Warning: Could not analyze {module_fqn}: {e}")

        cycles = self.registry.detect_cycles()
        if cycles:
            print(f"Warning: Detected {len(cycles)} import cycle(s):")
            for cycle in cycles:
                print(f"  {' -> '.join(cycle)}")

        return self.registry

    def _filepath_to_module_name(self, filepath: Path) -> str:
        try:
            relative = filepath.relative_to(self.project_root)
            parts = list(relative.parts[:-1])
            if relative.name != "__init__.py":
                parts.append(relative.stem)
            return ".".join(parts) if parts else relative.stem
        except ValueError:
            return filepath.stem

    def _extract_exports(self, tree: ast.AST, module_fqn: str, wrappers: Dict[Any, Any]) -> Dict[str, Symbol]:
        exports = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    wrapper = wrappers.get(node)
                    exports[node.name] = Symbol(
                        fqn=f"{module_fqn}.{node.name}",
                        kind=SymbolKind.FUNCTION,
                        wrapper=wrapper,
                        module_fqn=module_fqn,
                    )
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    wrapper = wrappers.get(node)
                    exports[node.name] = Symbol(
                        fqn=f"{module_fqn}.{node.name}",
                        kind=SymbolKind.CLASS,
                        wrapper=wrapper,
                        module_fqn=module_fqn,
                    )

        return exports
