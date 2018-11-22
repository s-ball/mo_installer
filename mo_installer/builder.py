from setuptools.command.build_py import build_py as _build_py
from distutils.command.build import build as _build
from distutils.cmd import Command

class build(_build):
    parent = _build
    def run(self):
        build_py.parent = (self.distribution.cmdclass["build_py"]
                           if ("build_py" in self.distribution.cmdclass)
                           else _build)
        self.parent.run(self)
        
class build_py(_build_py):
    def run(self):
        self.run_command("build_mo")
        self.parent.run(self)
        
    def get_outputs(self):
        build_mo = self.get_finalized_command("build_mo")
        return _build.get_outputs(self) + build_mo.get_outputs()


class build_mo(Command):
    def initialize_options(self):
        self.outputs = []

    def finalize_options(self):
        name = self.distribution.get_name()
        self.locale_src = self.distribution.locale_src
        if self.locale_src is None:
            self.locale_src = os.path.join(name, "locale")
        self.ensure_dirname("locale_src")
        self.locale_dir = self.distribution.locale_dir
        if self.locale_dir is None:
            self.locale_dir = os.path.join(name, "locale")
        self.ensure_dirname("locale_dir")

    def run(self):
        po_loc = re.compile(r"(.*)_(.*)\.po$")
        po = re.compile(r"(.*)\.po$")
        for locale in os.listdir(locale_src):
            if locale[0] == '.': continue
            path = os.path.join(local_src, locale)
            if os.is_dir(path):
                for file in os.listdir(path):
                    m = po.match(file)
                    if m:
                        self.process(os.path.join(path, file),
                                     m.group(1), locale)
            else:
                m = po_loc.match(file)
                if m:
                    self.process(path, m.group(1), m.group(2))

    def process(self, path, domain, locale):
        self.files.append(path)
        dest = os.path.join(self.build_lib, locale_dir, locale,
                            "LC_MESSAGES")
        self.mkpath(dest)
        if not self.dry_run:
            file = os.path.join(dest, domain + ".mo")
            msgfmt.make(path, file)
            
    def get_outputs(self):
        return self.outputs

def validate_src(dist, attr, value):
    if not os.isdir(value):
        raise DistutilsSetupError(
            "%r must be a directory (got %r)" % (attr,value)
            )

def validate_dir(dist, attr, value):
    pass
