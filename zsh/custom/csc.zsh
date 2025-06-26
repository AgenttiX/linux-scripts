#!/usr/bin/env zsh

csc-info-all() {
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

    module list

    echo "Currently running Slurm jobs:"
    squeue -u $USER

    echo "Slurm info:"
    sinfo
}

if [ -d "/scratch/project_462000956/${USER}/summerschool" ]; then
    alias summerschool="cd /scratch/project_462000956/${USER}/summerschool; clear"
fi
