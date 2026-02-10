from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import networkx as nx
from anytree import PreOrderIter

from pydepgraph.config import ImporterConfig
from pydepgraph.exceptions import PDGImportError
from pydepgraph.importer.graph import ImportGraph
from pydepgraph.node import AST
from pydepgraph.specification import (
    ImportPath,
    Module,
    ModuleCategory,
    ModuleSource,
    OriginType,
    SysPaths,
    is_spec_origin_valid,
)
from pydepgraph.tools import logger
from pydepgraph.types import Pathlike


class ModuleRegistry:
    def __init__(
        self,
        config: ImporterConfig,
        project_root: Pathlike,
        package: str,
    ) -> None:
        self.config = config
        self.project_root = Path(project_root).resolve()
        self.package = package
        self.modules: Dict[str, Module] = {}
        self.graph: ImportGraph = ImportGraph()
        self.filepath: Optional[Path] = None

    def __call__(self, filepath: Path) -> Union[nx.DiGraph[str], nx.DiGraph[Module]]:
        if len(self.graph) == 0 or self.filepath != filepath:
            self._create_graph(filepath)

        assert self.graph is not None, "Graph should have been created at this point"
        return self.graph(self.config.node_format)

    def _create_graph(self, filepath: Path) -> None:
        self.graph = ImportGraph()
        self.filepath = filepath

        root = self._create_root(filepath)
        self.graph.add_node(root)

        processed: Set[Optional[Path]] = {None}
        self.modules = {root.name: root}
        new_modules: Set[Module] = {root}

        while new_modules:
            module = new_modules.pop()
            if module.origin in processed:
                continue

            self._collect_new_modules(
                module,
                new_modules,
                processed,
            )

    def analyze_file(
        self,
        filepath: Path,
        base_path: Path,
        package: str,
        processed: Optional[Set[Optional[Path]]] = None,
    ) -> Dict[str, Module]:
        """
        Analyze a Python file to extract all imported module paths,
        and return their corresponding file paths.
        """
        tree = AST(filepath)
        module_source = ModuleSource(origin=filepath, base_path=base_path, package=package)
        import_paths = self._collect_imports(module_source, tree, processed=processed)
        return self._collect_modules(module_source, import_paths)

    def analyze_module(
        self,
        module: Module,
        processed: Optional[Set[Optional[Path]]] = None,
    ) -> Dict[str, Module]:
        """
        Analyze a module to extract all imported module paths,
        and return their corresponding file paths.
        """
        if not self._check_if_should_scan(module, processed=processed):
            return {}

        assert module.origin is not None
        return self.analyze_file(
            module.origin,
            module.base_path,
            module.top_level_module,
            processed=processed,
        )

    def _check_if_should_scan(
        self,
        module: Module,
        processed: Optional[Set[Optional[Path]]] = None,
    ) -> bool:
        if module.origin_type != OriginType.PYTHON:
            return False

        category = module.get_category(self.project_root)
        if not self.config.scan_stdlib and category == ModuleCategory.STDLIB:
            return False

        if not self.config.scan_external and category == ModuleCategory.EXTERNAL:
            return False

        assert module.origin is not None
        processed = processed or set()
        if module.origin in processed:
            return False

        return True

    def _collect_imports(
        self,
        module_source: ModuleSource,
        tree: AST,
        processed: Optional[Set[Optional[Path]]] = None,
    ) -> List[ImportPath]:
        module_paths: Dict[ImportPath, None] = {}
        import_paths = self._collect_import_paths(tree)
        for import_path in import_paths:
            module_path = self._resolve(module_source, import_path, processed)
            if module_path is not None:
                module_paths[module_path] = None

        return list(module_paths.keys())

    def _collect_import_paths(
        self,
        tree: AST,
    ) -> List[ImportPath]:
        import_paths: Dict[ImportPath, None] = {}
        for node in PreOrderIter(tree.root):
            if node.type in (ast.Import, ast.ImportFrom):
                import_node = node.ast
                new_paths = {import_path.get_module_path() for import_path in ImportPath.from_ast(import_node)}
                import_paths.update({path: None for path in new_paths})

        return list(import_paths.keys())

    def _collect_modules(
        self,
        module_source: ModuleSource,
        module_paths: List[ImportPath],
    ) -> Dict[str, Module]:
        modules: Dict[str, Module] = {}
        for module_path in module_paths:
            module = self._get_module_from_import_path(
                module_source,
                module_path,
            )
            if module is not None:
                modules[module.name] = module

        return modules

    def _get_module_from_import_path(
        self,
        module_source: ModuleSource,
        module_path: ImportPath,
    ) -> Optional[Module]:
        try:
            spec = module_source.get_spec(module_path)
            package_spec = module_source.get_package_spec(module_path)
        except (ImportError, ModuleNotFoundError, ValueError) as error:
            logger.warning(
                "Could not resolve import path '%s' in module '%s': %s",
                module_path,
                module_source.module.name,
                error,
            )
            return None

        try:
            package = package_spec.name if package_spec is not None else None
            return Module.from_spec(spec, package=package)
        except PDGImportError as import_error:
            logger.debug(
                "%s: %s [%s]",
                import_error.__class__.__name__,
                spec.name,
                import_error,
            )
            return None

    def _create_root(self, filepath: Path) -> Module:
        root_source = ModuleSource(
            origin=filepath,
            base_path=self.project_root,
            package=self.package,
        )

        return root_source.module

    def _collect_new_modules(
        self,
        module: Module,
        new_modules: Set[Module],
        processed: Set[Optional[Path]],
    ) -> None:
        processed.add(module.origin)
        imported_modules = self.analyze_module(module)
        for imported_module_name, imported_module in imported_modules.items():
            if imported_module_name not in self.modules:
                self.modules[imported_module_name] = imported_module

            target_module = self.modules[imported_module_name]
            self.graph.add_edge(module, target_module)
            new_modules.add(target_module)

    def _resolve(
        self,
        module_source: ModuleSource,
        path: ImportPath,
        processed: Optional[Set[Optional[Path]]] = None,
    ) -> Optional[ImportPath]:
        processed = processed or set()
        try:
            spec = module_source.get_spec(path, validate_origin=True)
            if not is_spec_origin_valid(spec.origin):
                return None
        except (ImportError, ModuleNotFoundError, ValueError, PDGImportError) as error:
            logger.debug(
                "%s: %s",
                error.__class__.__name__,
                error,
            )
            return None

        origin = Path(spec.origin) if spec.origin is not None else None
        if origin is None or origin in processed:
            return None

        return SysPaths.resolve(spec, base_path=module_source.base_path)
