class PythonSample:
    def undocumented_method(self, x: int, y: str):
        pass
        
    def documented_method(self):
        """This is documented."""
        return True

def undocumented_function(a, b):
    print(a, b)

def documented_function():
    """Has a docstring."""
    pass
