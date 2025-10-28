"""
Setup file for Ritiko Patient Email Plugin
"""
import json
import os
import sys
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install


# Read plugin metadata
plugin_json_path = Path(__file__).parent / "plugin.json"
with open(plugin_json_path) as f:
    PLUGIN_METADATA = json.load(f)


class LicenseValidatingInstall(install):
    """Custom install command that validates licenses for paid plugins."""

    def run(self):
        is_paid = PLUGIN_METADATA.get("is_paid", False)

        if is_paid:
            license_key = os.getenv("PLUGIN_LICENSE_KEY")

            if not license_key:
                self.announce("\n" + "=" * 70, level=1)
                self.announce("ERROR: License Key Required", level=1)
                self.announce("=" * 70, level=1)
                self.announce(
                    f"\nThis is a paid plugin: {PLUGIN_METADATA['name']}\n",
                    level=1,
                )
                self.announce("Installation requires a valid license.\n", level=1)
                self.announce(
                    f"  export PLUGIN_LICENSE_KEY=your_key\n"
                    f"  pip install {PLUGIN_METADATA.get('id', 'ritiko-patient-email-plugin')}\n",
                    level=1,
                )
                self.announce("=" * 70 + "\n", level=1)
                sys.exit(1)

        install.run(self)


setup(
    name=PLUGIN_METADATA.get("id", "ritiko-patient-email-plugin"),
    version=PLUGIN_METADATA.get("version", "1.0.0"),
    description=PLUGIN_METADATA.get("description", "Patient Email Plugin"),
    long_description=PLUGIN_METADATA.get("description", ""),
    author=PLUGIN_METADATA.get("author", "Ritiko Development Team"),
    author_email=PLUGIN_METADATA.get("email", "dev@ritiko.com"),
    url=PLUGIN_METADATA.get("url", "https://github.com/dedanritiko/ritiko-patient-email-plugin"),
    license="AGPL-3.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "Django>=3.2,<5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-django>=4.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    cmdclass={"install": LicenseValidatingInstall},
    python_requires=">=3.8",
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="ritiko plugin patient email django",
)
