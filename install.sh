#!/bin/bash

############ Conda Environment ############
echo New Environment Name:
read envname

echo
echo "##############################"
echo Creating new conda environment $envname...
cd monometis
mamba env create -f polymetis/environment_cpu.yml -y
# because environment_cpu.yml sets the env name to "robo" a copy is created
conda create -n $envname --clone robo -y
# and the original env deleted
conda remove -n robo --all -y
eval "$(conda shell.bash hook)"
conda activate $envname

echo
echo "##############################"
echo Activating $envname
if [[ "$CONDA_DEFAULT_ENV" != "$envname" ]]
then
    echo Failed to activate conda environment.
    exit 1
fi

############ Polymetis (Monometis) Installation ############
echo
echo "##############################"
echo Preparing Polymetis Installation...
# compile stuff
./scripts/build_libfranka.sh
mkdir -p ./polymetis/build
cd ./polymetis/build
cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_FRANKA=ON
make -j
make_exit_status=$?
if [ $make_exit_status -ne 0 ]; then
    echo "Make failed with exit code $make_exit_status"
    exit $make_exit_status
fi
cd ../..

echo
echo "##############################"
echo Installing Polymetis...
pip install -e ./polymetis
cd ..

############ MP_Pytorch Installation############
echo
echo "##############################"
echo Installing MP_PyTorch...
pip install -e MP_PyTorch

echo
echo
echo Successfully installed.
echo
echo To activate your environment call:
echo conda activate $envname
exit 0