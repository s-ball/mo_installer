from unittest import TestCase
from unittest.mock import Mock, patch
from mo_installer import builder
from mo_installer.builder import build, build_mo, build_py
from mo_installer.builder import validate_src, validate_dir
from distutils.dist import Distribution
from distutils.cmd import Command


class BuildTest(TestCase):
    def setUp(self):
        self.dist = Mock(Distribution)
        self.dist.verbose = 1
        self.dist.dry_run = 0
        self.dist.cmdclass = {}
        self.obj = build(self.dist)

    def test_no_previous(self):
        with patch("mo_installer.builder._build.run") as run:
            self.obj.run()
            run.assert_called_once_with(self.obj)
        self.assertEqual(builder._build_py, build_py.parent)
        self.assertEqual(build_py, self.dist.cmdclass["build_py"])

    def test_previous(self):
        self.dist.cmdclass["build_py"] = Command
        with patch("mo_installer.builder._build.run") as run:
            self.obj.run()
            run.assert_called_once_with(self.obj)
        self.assertEqual(Command, build_py.parent)
        self.assertEqual(build_py, self.dist.cmdclass["build_py"])

class BuildPyTest(TestCase):
    def setUp(self):
        self.dist = Mock(Distribution)
        self.dist.verbose = 1
        self.dist.dry_run = 0
        self.dist.cmdclass = {}
        self.obj = build_py(self.dist)

    def test_run(self):
        with patch("mo_installer.builder._build_py.run") as run, \
             patch("mo_installer.builder._build_py.run_command") as run_cmd:
            self.obj.run()
            run.assert_called_once_with(self.obj)
            run_cmd.assert_called_once_with("build_mo")
     
