"""
Copyright (C) 2021 Rosalind Franklin Institute

This code is distributed under the ApacheV2 license
"""
from skbuild import setup

def main():
    """
    Setup the package
    """

    setup(
        package_dir={"": "src"},
        packages=["autorec"],
        install_requires=[],
        entry_points={
            "console_scripts": [
                "autorec.check=autorec.main:check",
                "autorec.run=autorec.main:run",
                "autorec.new=autorec.main:new_revamp",
                "autorec.validate=autorec.main:validate_revamp",
                "autorec.lookup=autorec.preprocessing.params:params_lookup",
            ]
        }
    )

if __name__ == '__main__':
    main()
