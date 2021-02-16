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
        entry_points={
            "console_scripts": [
                "autorec.check_struct=autorec.command_line.prep:check_struct",
                "autorec.make_gain=autorec.command_line:make_gain",
                "autorec.new_config=autorec.command_line:new_config",
            ]
        },
    )

if __name__ == '__main__':
    main()

            
