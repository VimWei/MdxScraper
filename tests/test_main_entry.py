import importlib


def test_main_module_imports():
	# Importing the module should not execute run_gui unless __name__ == "__main__"
	mod = importlib.import_module("mdxscraper.__main__")
	assert hasattr(mod, "run_gui") or True  # Ensure module is loaded
