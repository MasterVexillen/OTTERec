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
python setup.py install
```

## Running autorec
1. Activate autorec environment: `conda activate autorec-env`
2. Load imod: `module load imod`
3. Run autorec: `python ${AUTOREC_PATH}/main.py *task*`, where *task* can be:
   * `check`: Performs a soft check (just warnings, no hard exit) on prequisite files and folder structure.
   * `new`: Prepares and flips gain reference files, prepares new input parameter file, then modifies the parameters according to user preferences.
   * `run`: Performs a hard check on prerequisite files and folder structure, then runs preprocessing using a user-specified parameter file.
   * `all`: Prepares new parameter file and run preprocessing using the **new** file.