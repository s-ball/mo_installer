from pyfakefs.fake_filesystem_unittest import TestCase
import os.path
import shutil

from unittest.mock import Mock, patch
from mo_installer import builder
from mo_installer.builder import build, build_mo, build_py
from mo_installer.builder import validate_src, validate_dir
from distutils.dist import Distribution
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError

class BuildMoTest(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.add_real_directory(os.path.dirname(__file__),
                                   target_path = "/orig")
        self.dist = Mock(Distribution)
        self.dist.verbose = 1
        self.dist.dry_run = 0
        self.dist.cmdclass = {}
        self.dist.get_name = Mock(return_value="tst")
        self.dist.locale_src = None
        self.dist.locale_dir = None
        self.obj = build_mo(self.dist)
        self.obj.initialize_options()
        self.fs.create_dir("/tst/locale")
        self.fs.create_dir("/build")
        self.obj.build_lib = "/build"

    def tearDown(self):
        pass

    def test_finalize_no_options(self):
        self.obj.finalize_options()
        self.assertEqual(os.path.join("tst", "locale"), self.obj.locale_src)
        self.assertEqual(os.path.join("tst", "locale"), self.obj.locale_dir)
        
    def test_finalize_with_options(self):
        self.dist.locale_src = "/orig"
        self.obj.finalize_options()
        self.assertEqual(os.path.join("tst", "locale"), self.obj.locale_dir)
        self.assertEqual("/orig", self.obj.locale_src)

    def test_finalize_no_isdir(self):
        self.dist.locale_src = "foo"
        self.obj.finalize_options()
        self.obj.run()
        self.assertEqual(0, len(self.obj.get_outputs()))

    def test_process(self):
        self.obj.finalize_options()
        self.obj.process("/orig/msg-fr.po", "tst", "fr")
        self.assertTrue(os.path.exists(
            "/build/tst/locale/fr/LC_MESSAGES/tst.mo"))
        self.assertEqual([os.path.join("/build", "tst", "locale", "fr",
                                       "LC_MESSAGES", "tst.mo")],
                         self.obj.outputs)

    def test_run_po_top(self):
        self.dist.locale_src = "/orig"
        self.obj.finalize_options()
        with patch("mo_installer.builder.msgfmt.make") as make:
            self.obj.run()
            make.assert_called_once_with(
                os.path.join("/orig", "msg-fr.po"),
                os.path.join("/build", "tst", "locale", "fr",
                             "LC_MESSAGES", "msg.mo")
            )

    def test_run_po_loc(self):
        self.dist.locale_src = "/src"
        self.fs.create_dir("/src/fr")
        shutil.copyfile("/orig/msg-fr.po", "/src/fr/msg.po")
        self.obj.finalize_options()
        with patch("mo_installer.builder.msgfmt.make") as make:
            self.obj.run()
            make.assert_called_once_with(
                os.path.join("/src", "fr", "msg.po"),
                os.path.join("/build", "tst", "locale", "fr",
                             "LC_MESSAGES", "msg.mo")
            )

    def test_run_po_loc_msg(self):
        self.dist.locale_src = "/src"
        self.fs.create_dir("/src/fr/LC_MESSAGES")
        shutil.copyfile("/orig/msg-fr.po", "/src/fr/LC_MESSAGES/msg.po")
        self.obj.finalize_options()
        with patch("mo_installer.builder.msgfmt.make") as make:
            self.obj.run()
            make.assert_called_once_with(
                os.path.join("/src", "fr", "LC_MESSAGES", "msg.po"),
                os.path.join("/build", "tst", "locale", "fr",
                             "LC_MESSAGES", "msg.mo")
            )

    def test_get_outputs(self):
        self.dist.locale_src = "/src"
        self.fs.create_dir("/src/fr_FR")
        shutil.copyfile("/orig/msg-fr.po", "/src/fr_FR/msg.po")
        shutil.copyfile("/orig/msg-fr.po", "/src/msg-fr_BE.po")
        self.fs.create_dir("/build2")
        self.obj.build_lib = "/build2"
        self.obj.finalize_options()
        with patch("mo_installer.builder.msgfmt.make") as make:
            self.obj.run()
            self.assertEqual(2, make.call_count)
        out = self.obj.get_outputs()
        self.assertEqual(2, len(out))
        self.assertTrue(os.path.join("/build2", "tst", "locale", "fr_FR",
                                     "LC_MESSAGES", "msg.mo") in out)

        self.assertTrue(os.path.join("/build2", "tst", "locale", "fr_BE",
                                     "LC_MESSAGES", "msg.mo") in out)

