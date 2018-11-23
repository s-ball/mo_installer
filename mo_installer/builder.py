from setuptools.command.build_py import build_py as _build_py
from distutils.command.build import build as _build
from distutils.cmd import Command
from distutils.errors import DistutilsSetupError
from .vendor import msgfmt
import os.path
import re

class build(_build):
    parent = _build
    def run(self):
        if "build_py" in self.distribution.cmdclass:
            p = self.distribution.cmdclass["build_py"]
            if p != build_py:
                build_py.parent = p
        self.distribution.cmdclass["build_py"] = build_py
        self.parent.run(self)
        
class build_py(_build_py):
    parent = _build_py
    def run(self):
        self.run_command("build_mo")
        self.parent.run(self)
        
    def get_outputs(self):
        build_mo = self.get_finalized_command("build_mo")
        return _build.get_outputs(self) + build_mo.get_outputs()


class build_mo(Command):
    description = "\"build\" mo gettext files form po ones"

    user_options = [
        ('locale-src', 's', "directory for po files"),
        ('locale-dir', 'd', "top level locale directory inside package"),
        ]

    def initialize_options(self):
        self.outputs = []
        self.build_lib = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib')
                                   )
        name = self.distribution.get_name()
        self.locale_src = self.distribution.locale_src
        if self.locale_src is None:
            self.locale_src = os.path.join(name, "locale")
        self.ensure_dirname("locale_src")
        self.locale_dir = self.distribution.locale_dir
        if self.locale_dir is None:
            self.locale_dir = os.path.join(name, "locale")

    def run(self):
        self.announce("Compiling from {} to {}".format(self.locale_src,
                                                       self.locale_dir))
        po_loc = re.compile(r"(.*)-(.*)\.po$")
        po = re.compile(r"(.*)\.po$")
        for locale in os.listdir(self.locale_src):
            if locale[0] == '.': continue
            path = os.path.join(self.locale_src, locale)
            if os.path.isdir(path):
                for file in os.listdir(path):
                    if file == "LC_MESSAGES" and os.path.isdir(
                        os.path.join(path, file)):
                        lcm = os.path.join(path, file)
                        for file in os.listdir(lcm):
                            m = po.match(file)
                            if m:
                                self.process(os.path.join(lcm, file),
                                             m.group(1), locale)
                    else:        
                        m = po.match(file)
                        if m:
                            self.process(os.path.join(path, file),
                                         m.group(1), locale)
            else:
                m = po_loc.match(locale)
                if m:
                    self.process(path, m.group(1), m.group(2))

    def process(self, path, domain, locale):
        dest = os.path.join(self.build_lib, self.locale_dir, locale,
                            "LC_MESSAGES")
        self.mkpath(dest)
        file = os.path.join(dest, domain + ".mo")
        self.outputs.append(file)
        if not self.dry_run:
            msgfmt.make(path, file)
            
    def get_outputs(self):
        return self.outputs

def validate_src(dist, attr, value):
    if not os.path.isdir(value):
        raise DistutilsSetupError(
            "%r must be a directory (got %r)" % (attr,value)
            )

def validate_dir(dist, attr, value):
    pass
