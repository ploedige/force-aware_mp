# Force-Aware Movement Primitives

## Installation
### Prerequisites
  - [Anaconda](https://www.anaconda.com) or [Miniconda](https://docs.anaconda.com/free/miniconda/) installed
  - [Mamba](https://mamba.readthedocs.io) installed
  
### Step-by-Step guide
1. clone repo with submodules
```bash
git clone --recursive https://github.com/ploedige/force-aware_mp.git
```
2. make `install.sh` executable
```bash
chmod +x install.sh
```
3. run `install.sh`
```
./install.sh
```

## Solved Problems
- error while loading shared libraries: libPocoNet.so.60
  - Solution: add library path to LD_LIBRARY_PATH
  ```bash
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/miniconda3/envs/<environment name>/lib
  ```