#!/usr/bin/env zsh

cluster-info() {
    # Puhti and Mahti
    if command -v csc-workspaces &> /dev/null; then
      csc-workspaces
      csc-info
    fi

    # LUMI
    if command -v lumi-workspaces &> /dev/null; then
      lumi-workspaces
      # lumi-quota  # This is included in lumi-workspaces
      # lumi-allocations  # This is included in lumi-workspaces
      lumi-ldap-userinfo
    fi

    if command -v module &> /dev/null; then
        module list
    fi
    if command -v sinfo &> /dev/null; then
        echo "Currently running Slurm jobs:"
        squeue -u $USER

        echo "Slurm info:"
        sinfo
    fi
    if command -v numactl &> /dev/null; then
        echo "Numactl info:"
        numactl --hardware
    fi
    echo "Module locations:"
    env | egrep ^EBROOT

    top -b -n 1 -u $UID
}

# CSC Summer School 2025 on LUMI
if [ -d "/scratch/project_462000956/${USER}/summerschool" ]; then
    alias summerschool="cd /scratch/project_462000956/${USER}/summerschool; clear"
fi
