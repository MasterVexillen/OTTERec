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
        packages=["OTTERec"],
        install_requires=[],
        entry_points={
            "console_scripts": [
                "OTTERec.check=OTTERec.main:check",
                "OTTERec.run=OTTERec.main:run",
                "OTTERec.new=OTTERec.main:new_revamp",
                "OTTERec.validate=OTTERec.main:validate_revamp",
                "OTTERec.lookup=OTTERec.preprocessing.params:params_lookup",
            ]
        }
    )

if __name__ == '__main__':
    main()
