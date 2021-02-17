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
conda activate autorec-env`
conda install python scikit-build pandas
```

3. Build autorec
>  `cd autorec`
>  `python setup.py install`

## Running autorec
1. Activate autorec environment: `conda activate autorec-env`
1. Load imod: `module load imod`
2. Run autorec: `python ${AUTOREC_PATH}/main.py *task*`, where *task* can be:
