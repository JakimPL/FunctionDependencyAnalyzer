from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from typing import List, Optional

from fda.importer.config import ImportConfig
from fda.importer.spec import ImportCondition, ImportItem, ImportStatement, ModuleSpec


class ImportResolver:
    def __init__(self, config: ImportConfig) -> None:
        self.config = config

    def collect_imports(self, ast_tree: ast.AST, current_module_path: Optional[Path] = None) -> List[ImportStatement]:
        collector = ImportCollector(self, current_module_path)
        collector.visit(ast_tree)
        return collector.imports

    def resolve_module_spec(self, module_name: str, from_path: Optional[Path] = None) -> Optional[ModuleSpec]:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return None

            origin = Path(spec.origin) if spec.origin else None
            submodule_locations = (
                [Path(loc) for loc in spec.submodule_search_locations] if spec.submodule_search_locations else []
            )

            return ModuleSpec(
                fqn=module_name,
                origin=origin,
                is_package=spec.submodule_search_locations is not None,
                submodule_search_locations=submodule_locations,
            )
        except (ModuleNotFoundError, ValueError, ImportError):
            return None

    def resolve_relative_import(self, level: int, module_name: Optional[str], from_path: Path) -> Optional[str]:
        if not from_path:
            return None

        parts = from_path.parts
        if level > len(parts):
            return None

        base_parts = parts[:-level] if level > 0 else parts
        base_module = ".".join(base_parts)

        if module_name:
            return f"{base_module}.{module_name}" if base_module else module_name
        return base_module

    def expand_wildcard_import(self, module_spec: ModuleSpec) -> List[str]:
        if not module_spec.origin or not module_spec.origin.exists():
            return []

        try:
            with open(module_spec.origin, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(module_spec.origin))

            all_names = self._extract_all_from_tree(tree)
            if all_names:
                return all_names

            return self._extract_public_names(tree)
        except Exception:
            return []

    def _extract_all_from_tree(self, tree: ast.AST) -> Optional[List[str]]:
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            names = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    names.append(elt.value)
                            return names
        return None

    def _extract_public_names(self, tree: ast.AST) -> List[str]:
        names = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    names.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        names.append(target.id)
        return names


class ImportCollector(ast.NodeVisitor):
    def __init__(self, resolver: ImportResolver, current_module_path: Optional[Path]) -> None:
        self.resolver = resolver
        self.current_module_path = current_module_path
        self.imports: List[ImportStatement] = []
        self.in_try_except = False
        self.current_condition: Optional[ImportCondition] = None

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            items = [
                ImportItem(
                    original_name=alias.name,
                    local_name=alias.asname if alias.asname else alias.name,
                )
            ]
            self.imports.append(
                ImportStatement(
                    target_module=alias.name,
                    items=items,
                    condition=self.current_condition,
                    lineno=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module_name = node.module or ""

        if node.level > 0 and self.current_module_path:
            module_name = (
                self.resolver.resolve_relative_import(node.level, node.module, self.current_module_path) or module_name
            )

        is_wildcard = any(alias.name == "*" for alias in node.names)

        if is_wildcard:
            self.imports.append(
                ImportStatement(
                    target_module=module_name,
                    items=[],
                    is_wildcard=True,
                    condition=self.current_condition,
                    lineno=node.lineno,
                )
            )
        else:
            items = [
                ImportItem(
                    original_name=alias.name,
                    local_name=alias.asname if alias.asname else alias.name,
                )
                for alias in node.names
            ]
            self.imports.append(
                ImportStatement(
                    target_module=module_name,
                    items=items,
                    condition=self.current_condition,
                    lineno=node.lineno,
                )
            )

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        old_condition = self.current_condition

        self.current_condition = ImportCondition(branch_type="try", exception_types=[])
        for stmt in node.body:
            self.visit(stmt)

        for handler in node.handlers:
            exc_types = []
            if handler.type:
                if isinstance(handler.type, ast.Name):
                    exc_types.append(handler.type.id)
                elif isinstance(handler.type, ast.Tuple):
                    for elt in handler.type.elts:
                        if isinstance(elt, ast.Name):
                            exc_types.append(elt.id)

            self.current_condition = ImportCondition(branch_type="except", exception_types=exc_types)
            for stmt in handler.body:
                self.visit(stmt)

        if node.orelse:
            self.current_condition = ImportCondition(branch_type="else", exception_types=[])
            for stmt in node.orelse:
                self.visit(stmt)

        self.current_condition = old_condition
