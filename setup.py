#  This file is part of OctoBot Node (https://github.com/Drakkar-Software/OctoBot-Node)
#  Copyright (c) 2025 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot. If not, see <https://www.gnu.org/licenses/>.
import os
import subprocess
import sys
from setuptools import find_packages
from setuptools import setup
from setuptools.command.sdist import sdist
from octobot_node import PROJECT_NAME, AUTHOR, VERSION

PACKAGES = find_packages(exclude=["tests", ])

# long description from README file
with open('README.md', encoding='utf-8') as f:
    DESCRIPTION = f.read()


REQUIRED = open('requirements.txt').readlines()
REQUIRES_PYTHON = '>=3.10'


class BuildUIAndSDist(sdist):    
    def run(self):
        self.announce('Running npm build before creating source distribution...', level=2)
        try:
            self.announce('Installing npm dependencies...', level=2)
            subprocess.check_call(['npm', 'install'], cwd=os.getcwd())
            subprocess.check_call(['npm', 'run', 'build'], cwd=os.getcwd())
            self.announce('npm build completed successfully', level=2)
        except subprocess.CalledProcessError as e:
            self.announce(f'Error running npm build: {e}', level=1)
            sys.exit(1)
        except FileNotFoundError:
            self.announce('npm not found. Skipping npm build step.', level=1)
                
        # Call the parent sdist run method
        super().run()


setup(
    name=PROJECT_NAME.lower().replace("-", "_"),
    version=VERSION,
    url='https://github.com/Drakkar-Software/OctoBot-Node',
    license='GPL-3.0',
    author=AUTHOR,
    author_email='contact@drakkar.software',
    description='OctoBot Node',
    py_modules=['start'],
    packages=PACKAGES,
    package_data={
        "": ["config/*"],
        "octobot_node.ui": ["dist/**/*"],
    },
    include_package_data=True,
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    tests_require=["pytest"],
    test_suite="tests",
    zip_safe=False,
    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,
    entry_points={
        'console_scripts': [
            PROJECT_NAME.replace("-", "_") + ' = octobot_node.cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.10',
    ],
    cmdclass={
        'sdist': BuildUIAndSDist,
    },
)
