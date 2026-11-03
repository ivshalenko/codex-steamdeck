"""Regression for Decky/PyInstaller LD_LIBRARY_PATH leaking into Codex shells."""
import ast
import os
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

def sanitizer(path):
    tree=ast.parse(path.read_text())
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='clean_subprocess_environment')
    scope={'os':os}
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(path),'exec'),scope)
    return scope['clean_subprocess_environment']

class RuntimeEnvironmentTests(unittest.TestCase):
    def implementations(self):
        return [sanitizer(ROOT/'backend.py'),sanitizer(ROOT/'decky/main.py')]

    def test_decky_library_path_and_frozen_flags_are_removed(self):
        polluted={'PATH':'/usr/bin','HOME':'/home/deck','LD_LIBRARY_PATH':'/tmp/_MEI00000523kgzrDp',
                  '_PYI_ARCHIVE_FILE':'/home/deck/homebrew/services/PluginLoader','_PYI_PARENT_PROCESS_LEVEL':'1'}
        for clean in self.implementations():
            result=clean(polluted)
            self.assertEqual(result,{'PATH':'/usr/bin','HOME':'/home/deck'})
            self.assertIn('LD_LIBRARY_PATH',polluted)

    def test_existing_user_library_path_is_restored(self):
        for clean in self.implementations():
            result=clean({'_PYI_ARCHIVE_FILE':'PluginLoader','LD_LIBRARY_PATH':'/tmp/_MEI1:/opt/user/lib','LD_LIBRARY_PATH_ORIG':'/opt/user/lib'})
            self.assertEqual(result,{'LD_LIBRARY_PATH':'/opt/user/lib'})

    def test_normal_process_environment_is_preserved(self):
        normal={'PATH':'/bin','LD_LIBRARY_PATH':'/opt/custom/lib','LD_PRELOAD':'/opt/monitor.so','TERM':'xterm'}
        for clean in self.implementations():self.assertEqual(clean(normal),normal)

    def test_missing_pyinstaller_flag_still_catches_bundle_path(self):
        for clean in self.implementations():self.assertEqual(clean({'LD_LIBRARY_PATH':'/tmp/_MEI1','LD_LIBRARY_PATH_ORIG':''}),{})

if __name__=='__main__':unittest.main()
