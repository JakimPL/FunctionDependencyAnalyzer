"""
An example for module import static analysis.
This file contains various import statements that should be correctly parsed
and analyzed by the tool, including imports in different scopes and conditional imports.
"""

from typing import TYPE_CHECKING, Any, Callable

from package.module.submodule import *
from package.module.submodule import function as imported_function

if TYPE_CHECKING:
    from package.module import SomeType

if not TYPE_CHECKING:
    from package.module import SomeRuntimeClass

    import_dependencies_dynamically()

elif some_condition or another_condition:
    from package.module import SomeOtherRuntimeClass as SomeRuntimeClass
else:
    from package.module import SomeFallbackRuntimeClass as SomeRuntimeClass

try:
    import some_optional_dependency
    from some_optional_dependency.module import OptionalClass
except ImportError:
    import alternative_dependency as some_optional_dependency
    from alternative_dependency.module import AlternativeClass as OptionalClass

    def importing_function() -> None:
        from some_importing_functions import useless_function

        return

    def useless_importing_function() -> None:
        from useless_importing_functions import useless_function

        return

    importing_function()
else:
    from else_fallback import ElseFallbackClass, else_fallback_function

    instance = ElseFallbackClass()
    instance.else_fallback_function()
finally:
    from final_dependency.module import final_function


def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    import implicit_package

    implicit_package.use_implicit_package()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from implicit_package import implicit_module

        result = imported_function()
        result = implicit_package.general_function(result)
        implicit_module.do_something(result)

        return func(*args, **kwargs)

    return wrapper


def regular_function(instance: Any) -> Any:
    import regular_import
    from regular_import import RegularClass

    instance = SomeRuntimeClass()
    value = some_optional_dependency.CONSTANT
    result = RegularClass(instance, value)
    return regular_import.some_regular_function(result)


@decorator
def function(object1: Any, object2: Any) -> Any:
    import inside_function
    from inside_function import InsideFunctionClass

    instance = InsideFunctionClass(object1)
    runtime_class_instance = SomeRuntimeClass(object2)
    return inside_function.some_function(instance, runtime_class_instance)


class MyClass:
    import inside_class
    from inside_class import InsideClassClass

    inside_class.use_inside_class()

    def method(self) -> Any:
        import inside_method
        from inside_method import InsideMethodClass

        instance = InsideMethodClass()
        return inside_method.some_method(instance)

    @staticmethod
    def static_method() -> Any:
        import inside_static_method
        from inside_static_method import InsideStaticMethodClass

        instance = InsideStaticMethodClass()
        return inside_static_method.some_static_method(instance)

    @decorator
    def decorated_method(self) -> Any:
        from inside_decorated_method import InsideDecoratedMethodClass, context_manager

        with context_manager():
            instance = InsideDecoratedMethodClass()
            return inside_decorated_method.some_decorated_method(instance)
