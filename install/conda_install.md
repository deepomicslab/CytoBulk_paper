# CytoBulk Installation — Conda Version

## 1.1 Conda installation (recommended)

First, clone the CytoBulk repository:

```bash
git clone git@github.com:kristaxying/CytoBulk.git
cd CytoBulk
```

Then create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate cytobulk
pip install -e .
```

This will install all Python dependencies specified in `environment.yml` and install CytoBulk in editable mode.

## 1.2 Install Giotto in R (required for marker detection)

CytoBulk uses Giotto for marker detection. You need to install it in R.

Open R or RStudio and run:

```r
library(devtools)  # if not installed: install.packages('devtools')
library(remotes)   # if not installed: install.packages('remotes')
remotes::install_github("RubD/Giotto")
```

### Giotto Reference

For more information about Giotto installation and usage, see:
- https://giottosuite.readthedocs.io/en/master/gettingstarted.html

## 1.3 Verify Installation

To verify the installation was successful:

```bash
# In Python (with conda environment activated)
conda activate cytobulk
python -c "import cytobulk; print(cytobulk.__version__)"
```

You should see the CytoBulk version printed without errors.

## 1.4 Troubleshooting

### Issue: rpy2 installation fails with "command 'gcc' failed"

If you encounter an error during `conda env create -f environment.yml` that looks like:

```
ERROR: Failed to build 'rpy2' when getting requirements to build wheel
...
FileNotFoundError: [Errno 2] No such file or directory: 'gcc'
...
distutils.compilers.C.errors.CompileError: command 'gcc' failed: No such file or directory
```

**Cause:** This error occurs because the system lacks required C compilers (gcc) needed to build rpy2 from source.

**Solution:** Install the compilers using conda:

```bash
conda install -c conda-forge compilers make pkg-config
```

After installation, verify that gcc is available:

```bash
which gcc && gcc --version
```

You should see the path to gcc and its version information. Then retry the environment creation:

```bash
conda env create -f environment.yml
```
