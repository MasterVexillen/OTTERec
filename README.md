# autorec
A program to automate cryoET image reconstruction under DLS workflow

## Installation

1. Git clone repo
```
git clone https://github.com/MasterVexillen/autorec.git
cd autorec
```

2. Create virtual environment in miniconda and pre-install packages
```
conda create -n autorec-env
conda activate autorec-env
conda install --file requirements.txt
```

3. Build autorec
```
python setup.py develop
```

## Running autorec
1. Activate autorec environment and load imod
```
conda activate autorec-env
module load imod
```
2. Run autorec
```
autorec.TASK [option]
```
where `TASK` can be:
   * `lookup`: Prints out essential information about a given parameter. *option* is the parameter in the old format or new `GROUP.NAME` format, but must be present.
   * `check`: Performs check on prequisite files and folder structure.
   * `new`: Prepares and flips gain reference files, prepares new input parameter file, then modifies the parameters according to user preferences.
   * `validate`: Validates a given YAML configuration file. *option* is the name of the YAML file to be validated.
   * `run`: Performs a hard check on prerequisite files and folder structure, then runs preprocessing using a user-specified parameter file.
