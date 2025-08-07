"""
This conftest.py sets up a mock environment that simulates the StreamController
application, allowing the plugin to be tested in isolation.
"""

import sys
from unittest.mock import MagicMock

# This top-level code runs once when pytest loads this conftest.py module.
# This is before it attempts to collect and import the test files, which is
# crucial for allowing `from src...` imports to succeed.


# 1. Create a mock for the PluginBase class that our plugin inherits from.
class MockPluginBase:
  def __init__(self):
    self.main_view = MagicMock()
    self.main_view.deck_controller.decks = {}
    self.PATH = "/fake/plugin/path"

  def add_action_holder(self, holder):
    pass

  def register(self, *args, **kwargs):
    pass


# 2. Create mock modules for the entire `src.backend.PluginManager` path.
#    This creates a "phantom" src package in memory.
mock_modules = {
  "src": MagicMock(),
  "src.backend": MagicMock(),
  "src.backend.PluginManager": MagicMock(),
  "src.backend.PluginManager.PluginBase": MagicMock(PluginBase=MockPluginBase),
  "src.backend.PluginManager.ActionHolder": MagicMock(ActionHolder=MagicMock()),
  "src.backend.PluginManager.ActionBase": MagicMock(ActionBase=object),
}

# 3. Inject the phantom package into Python's list of loaded modules.
sys.modules.update(mock_modules)
