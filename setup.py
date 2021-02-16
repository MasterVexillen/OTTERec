"""
Copyright (C) 2021 Neville Bor-yior Yee

This code is distributed under the MIT license
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
    )

if __name__ == '__main__':
    main()

            
