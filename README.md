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

## Known Bugs
### Error while loading shared libraries: libPocoNet.so.60
**Work-Around**: add library path to LD_LIBRARY_PATH
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/miniconda3/envs/<environment name>/lib
```
### Packages Missing after Reboot
Because Polymetis (Monometis) and MP_PyTorch are installed as editable packages pip creates symlinks that are lost after reboot.<br>
**Work-Around**: readd packages or reinstall the environment via `install.sh`
