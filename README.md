# autorec
A program suite to automate cryoET image reconstruction under DLS workflow

## Installations

### Prerequisites
- Python >= 3.8
- scikit-build
- pandas
- miniconda

### Procedures
1. Git clone git repo

2. Create virtual environment in miniconda
```
conda create -n autorec-env
conda activate autorec-env
conda install python scikit-build pandas
```

3. Build autorec
```
cd autorec
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