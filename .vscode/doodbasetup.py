#!/usr/bin/env python3
from configparser import ConfigParser
from glob import glob
from os import path
from urllib.request import urlretrieve
import json
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
ROOT = path.abspath(path.join(DEST, "..", ".."))
ENV_FILE = path.join(ROOT, ".env")
SCAFFOLDING_NAME = path.basename(path.abspath(ROOT))
env = env_vars_from_file(ENV_FILE)

# Use the right Python version for current Doodba project
version = env.get("ODOO_MINOR")
if version in {"7.0", "8.0", "9.0", "10.0"}:
    executable = shutil.which("python2") or shutil.which("python")
else:
    executable = sys.executable
try:
    os.remove(path.join(DEST, "python"))
except FileNotFoundError:
    pass
os.symlink(executable, path.join(DEST, "python"))

# Enable development environment by default
try:
    os.symlink("devel.yaml", path.join(ROOT, "docker-compose.yml"), True)
except FileExistsError:
    pass

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

# Produce VSCode workspace
WORKSPACE = path.join(ROOT, "doodba.%s.code-workspace" % SCAFFOLDING_NAME)
try:
    with open(WORKSPACE) as fp:
        workspace_config = json.load(fp)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    workspace_config = {}
workspace_config["folders"] = []
addon_repos = glob(path.join(ROOT, "odoo", "custom", "src", "private"))
addon_repos += glob(path.join(
    ROOT, "odoo", "custom", "src", "*", ".git", ".."))
for subrepo in sorted(addon_repos):
    workspace_config["folders"].append({
        "path": path.abspath(subrepo)[len(ROOT) + 1:],
    })
# HACK https://github.com/microsoft/vscode/issues/37947 put top folder last
workspace_config["folders"].append({"path": "."})
with open(WORKSPACE, "w") as fp:
    json.dump(workspace_config, fp, indent=4)

# Final reminder
print("""
Setup finished:

- Configured to use {}
- Linters configured for Odoo {}
- Created doodba-devel.code-workspace file with present git subfolders

To have full Doodba VSCode support, remember to:

- Install the recommended extensions
- Install Python 2 and 3
- Install eslint
- Install pylint-odoo (both for Python 2 and 3)
- Install flake8 (both for Python 2 and 3)
- Load the created workspace file
- Execute this task again each time you add an addons subrepo

Enjoy 😃
""".format(executable, version))
