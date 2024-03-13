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
2. run `install.sh`
```
./install.sh
```

## Usage
### Launching the Robot Servers
1. activate FCI in the robots
2. verify the enable switches (black emergency buttons) are depressed
3. start each robot server via the `launch_poly_server.sh` script<br>
*Note:* Robot Configs are specified in the `configs` folder
```
./launch_poly_server.sh <config_name (without .yaml)> <robot_name (as specified in the config)>
```

### Adding Custom Parameters to a Policy
parameters can be added like normal variables and have to be initialized as `torch.nn.Parameter`
```python
import torch
...

class CustomController(toco.PolicyModule):
    def __init__(self, <parameters>):
        super().__init__()

        self.<custom_parameter_name> = torch.nn.Parameter(<initial_value>)
    ...
```
It can then be modified during operation 
```python
<object_name>.update_current_policy({"<custom_parameter_name>" : <new_value>})
``` 

## Known Bugs
### Error while loading shared libraries: libPocoNet.so.60
**Work-Around**: add library path to LD_LIBRARY_PATH
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/<environment location>/<environment name>/lib
```
### Packages Missing after Reboot
Because Polymetis (Monometis) and MP_PyTorch are installed as editable packages pip creates symlinks that are lost after reboot.<br>
**Work-Around**: readd packages or reinstall the environment via `install.sh`

### GUI looks horrible
tkinter does not have nice fonts because of conda <br>
**Work-Around**: add a special tk package (see https://github.com/conda-forge/tk-feedstock/pull/40#issuecomment-1803067221)
```
conda install -c conda-forge tk=*=xft_*
```
Note: in zsh the * need to be escaped