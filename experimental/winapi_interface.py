import abc
from ctypes import c_void_p, CFUNCTYPE, POINTER, cast
from typing import Any

from UniLoader.experimental.guid import GUID


class Interface(c_void_p):
    """Base class for COM-like interfaces that utilize virtual function tables.

    This class provides a mechanism to call virtual functions on COM interfaces
    through the virtual table pointer.
    """
    iid: GUID

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._virtual_functions: dict[str, tuple[int, CFUNCTYPE]] = {}

    def is_valid(self):
        """Check if the interface pointer is valid."""
        return self.value != 0 and self.value is not None

    @abc.abstractmethod
    def _register_functions(self) -> None:
        """Register virtual functions for this interface.

        Subclasses must implement this method to define their virtual table.
        """
        raise

    def _ensure_vtable(self):
        """Ensure the virtual function table is populated."""
        # Only register functions if the table is empty
        if hasattr(self, '_virtual_functions'):
            virtual_functions = self._virtual_functions
        else:
            virtual_functions = self._virtual_functions = {}
        if not virtual_functions:
            self._register_functions()

    def _vcall(self, name: str, *args) -> Any:
        """Call a virtual function by name with the given arguments.

        Args:
            name: The name of the virtual function to call
            *args: Arguments to pass to the function

        Returns:
            The result of the function call

        Raises:
            ValueError: If the interface pointer is null
        """
        if self.value == 0 or self.value is None:
            raise ValueError("Cannot call methods on a null interface pointer")

        self._ensure_vtable()
        index, func_proto = self._virtual_functions[name]

        vtbl_ptr = cast(self, POINTER(POINTER(c_void_p))).contents
        func = func_proto(vtbl_ptr[index])
        res = func(self, *args)
        if isinstance(res, Interface) and not res.is_valid():
            return None
        return res

    def _add_virtual_function(self, index: int, name: str, res_type: Any, args: list[Any]) -> None:
        """Register a virtual function in the vtable.

        Args:
            name: Name of the function
            index: Index in the vtable
            res_type: Return type of the function
            args: List of argument types
        """
        func_type = CFUNCTYPE(res_type, *(c_void_p, *args))
        self._virtual_functions[name] = (index, func_type)