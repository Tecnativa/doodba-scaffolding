#!/usr/bin/env python3
from __future__ import print_function

from configparser import ConfigParser
from os import path
from urllib.request import urlretrieve
import os
import shutil
import sys

try:
    from compose.config.environment import env_vars_from_file
except ImportError:
    print(
        "Execute `pip3 install docker-compose` to enable Python "
        "version autoguessing in Doodba projects",
        file=sys.stderr,
    )

PYLINT_CONFIGS = (
    "maintainer-quality-tools/master/travis/cfg/travis_run_pylint_pr.cfg",
    "maintainer-quality-tools/master/travis/cfg/travis_run_pylint.cfg",
    "maintainer-quality-tools/master/travis/cfg/travis_run_pylint_beta.cfg",
)
CONFIGS = PYLINT_CONFIGS + (
    "maintainer-quality-tools/master/travis/cfg/travis_run_flake8.cfg",
    "pylint-odoo/master/pylint_odoo/examples/.jslintrc",
)
DEST = path.join(path.dirname(__file__), "doodba")
ENV_FILE = path.join(DEST, "..", "..", ".env")
env = env_vars_from_file(ENV_FILE)

# Use the right Python version for current Doodba project
version = env.get("ODOO_MINOR")
if version in {"8.0", "9.0", "10.0"}:
    executable = shutil.which("python2") or shutil.which("python")
else:
    executable = sys.executable
try:
    os.remove(path.join(DEST, "python"))
except FileNotFoundError:
    pass
os.symlink(executable, path.join(DEST, "python"))

# Download linter configs
for config in CONFIGS:
    urlretrieve(
        "https://raw.githubusercontent.com/OCA/" + config,
        path.join(DEST, path.basename(config)),
    )

# Produce merged pylint config
baseparser = ConfigParser()
baseparser.read(path.join(DEST, path.basename(PYLINT_CONFIGS[0])))
for config in PYLINT_CONFIGS[1:]:
    parser = ConfigParser()
    parser.read(path.join(DEST, path.basename(config)))
    baseparser["MESSAGES CONTROL"]["enable"] += \
        "," + parser["MESSAGES CONTROL"]["enable"]
# No duplicated commas
baseparser["MESSAGES CONTROL"]["enable"] = \
    baseparser["MESSAGES CONTROL"]["enable"].replace(",,", ",")
# Add Doodba specific stuff
baseparser["ODOOLINT"]["valid_odoo_versions"] = version
with open(path.join(DEST, "doodba_pylint.cfg"), "w") as config:
    baseparser.write(config)

# Final reminder
print("""
Setup finished:

- Configured to use {}
- Linters configured for Odoo {}

To have full Doodba VSCode support, remember to:

- Install the recommended extensions
- Install Python 2 and 3
- Install eslint
- Install pylint-odoo (both for Python 2 and 3)
- Install flake8 (both for Python 2 and 3)

Enjoy :)
""".format(executable, version))
