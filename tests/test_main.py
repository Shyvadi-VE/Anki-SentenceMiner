import src


def test_project_structure_imports():
    """Verifica que el paquete principal src se pueda importar correctamente."""
    assert src is not None
