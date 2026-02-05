from pathlib import Path

from fda.importer import ImportConfig, ImportResolver, ModuleRegistry
from fda.importer.spec import ImportStatement, Module, ModuleAvailability, ModuleSpec, Symbol, SymbolKind
from fda.parser import parse_python_file
from fda.resolver import Scope


def test_import_resolver_collects_imports_from_ast() -> None:
    config = ImportConfig(project_root=Path("src"), scan_external=False)
    resolver = ImportResolver(config)
    tree = parse_python_file("examples/example.py")

    imports = resolver.collect_imports(tree)

    assert len(imports) > 0
    assert all(isinstance(imp, ImportStatement) for imp in imports)


def test_import_resolver_resolves_module_spec_for_installed_package() -> None:
    config = ImportConfig(project_root=Path("src"))
    resolver = ImportResolver(config)

    spec = resolver.resolve_module_spec("fda.importer")

    assert spec is not None
    assert spec.fqn == "fda.importer"
    assert spec.is_package is True
    assert spec.origin is not None


def test_import_resolver_returns_none_for_nonexistent_module() -> None:
    config = ImportConfig(project_root=Path("src"))
    resolver = ImportResolver(config)

    spec = resolver.resolve_module_spec("nonexistent_module_xyz_123")

    assert spec is None


def test_module_registry_detects_circular_dependencies() -> None:
    config = ImportConfig(project_root=Path("src"), scan_external=False)
    registry = ModuleRegistry(config)

    mod_a = Module(
        spec=ModuleSpec(fqn="a", origin=Path("a.py")),
        imports=[ImportStatement(target_module="b", items=[], lineno=1)],
        availability=ModuleAvailability.INSTALLED,
    )
    mod_b = Module(
        spec=ModuleSpec(fqn="b", origin=Path("b.py")),
        imports=[ImportStatement(target_module="a", items=[], lineno=1)],
        availability=ModuleAvailability.INSTALLED,
    )

    registry.register_module(mod_a)
    registry.register_module(mod_b)

    cycles = registry.detect_cycles()

    assert len(cycles) == 1
    assert "a" in cycles[0]
    assert "b" in cycles[0]


def test_module_registry_detects_no_cycles_in_acyclic_graph() -> None:
    config = ImportConfig(project_root=Path("src"), scan_external=False)
    registry = ModuleRegistry(config)

    mod_a = Module(
        spec=ModuleSpec(fqn="a", origin=Path("a.py")),
        imports=[ImportStatement(target_module="b", items=[], lineno=1)],
        availability=ModuleAvailability.INSTALLED,
    )
    mod_b = Module(
        spec=ModuleSpec(fqn="b", origin=Path("b.py")),
        imports=[],
        availability=ModuleAvailability.INSTALLED,
    )

    registry.register_module(mod_a)
    registry.register_module(mod_b)

    cycles = registry.detect_cycles()

    assert len(cycles) == 0


def test_scope_tracks_imported_symbols() -> None:
    scope = Scope()
    symbol = Symbol(fqn="module.func", kind=SymbolKind.FUNCTION, module_fqn="module")

    scope.import_symbol("func", symbol)
    resolved = scope.resolve_import("func")

    assert resolved is not None
    assert resolved.fqn == "module.func"
    assert resolved.kind == SymbolKind.FUNCTION


def test_scope_resolves_imported_symbols_from_parent_scope() -> None:
    parent_scope = Scope()
    child_scope = Scope(parent=parent_scope)
    symbol = Symbol(fqn="module.func", kind=SymbolKind.FUNCTION, module_fqn="module")

    parent_scope.import_symbol("func", symbol)
    resolved = child_scope.resolve_import("func")

    assert resolved is not None
    assert resolved.fqn == "module.func"


def test_scope_returns_none_for_unresolved_import() -> None:
    scope = Scope()

    resolved = scope.resolve_import("nonexistent")

    assert resolved is None


def test_dependency_graph_tracks_module_dependencies() -> None:
    config = ImportConfig(project_root=Path("src"), scan_external=False)
    registry = ModuleRegistry(config)

    mod_a = Module(
        spec=ModuleSpec(fqn="a", origin=Path("a.py")),
        imports=[ImportStatement(target_module="b", items=[], lineno=1)],
        availability=ModuleAvailability.INSTALLED,
    )
    mod_b = Module(
        spec=ModuleSpec(fqn="b", origin=Path("b.py")),
        imports=[],
        availability=ModuleAvailability.INSTALLED,
    )

    registry.register_module(mod_a)
    registry.register_module(mod_b)
    graph = registry.graph

    deps = graph.get_dependencies("a")

    assert "b" in deps


def test_dependency_graph_tracks_module_dependents() -> None:
    config = ImportConfig(project_root=Path("src"), scan_external=False)
    registry = ModuleRegistry(config)

    mod_a = Module(
        spec=ModuleSpec(fqn="a", origin=Path("a.py")),
        imports=[ImportStatement(target_module="b", items=[], lineno=1)],
        availability=ModuleAvailability.INSTALLED,
    )
    mod_b = Module(
        spec=ModuleSpec(fqn="b", origin=Path("b.py")),
        imports=[],
        availability=ModuleAvailability.INSTALLED,
    )

    registry.register_module(mod_a)
    registry.register_module(mod_b)
    graph = registry.graph

    dependents = graph.get_dependents("b")
    assert "a" in dependents


def test_import_config_identifies_internal_modules() -> None:
    config = ImportConfig(project_root=Path("/project/src"), scan_external=False)

    is_internal = config.is_internal_module(Path("/project/src/module.py"))
    is_external = config.is_internal_module(Path("/other/module.py"))

    assert is_internal is True
    assert is_external is False
