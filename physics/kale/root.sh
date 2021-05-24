#!/bin/sh -e

# Based on the instructions at
# https://www.mv.helsinki.fi/home/slehti/ComputingMethodsInHEP/ComputingMethodsInHEP.html

export ROOTSYS=/cvmfs/cms.cern.ch/slc7_amd64_gcc820/lcg/root/6.20.06-bcolbf/
export PATH=cvmfs/cms.cern.ch/share/overrides/bin:/wrk/users/slehti/CMSSW_11_1_7/bin/slc7_amd64_gcc820:/wrk/users/slehti/CMSSW_11_1_7/external/slc7_amd64_gcc820/bin:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/cms/cmssw/CMSSW_11_1_7/bin/slc7_amd64_gcc820:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/cms/cmssw/CMSSW_11_1_7/external/slc7_amd64_gcc820/bin:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/llvm/9.0.1-bcolbf3/bin:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/gcc/8.2.0-bcolbf/bin:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/lcg/root/6.14.09-pafccj5//bin:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/cms/cmssw/CMSSW_10_6_20/external/slc7_amd64_gcc820/bin/python:.:/cvmfs/cms.cern.ch/common:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/cms/cmssw/CMSSW_10_6_20/external/slc7_amd64_gcc820/bin/python:.:/cvmfs/cms.cern.ch/common:/usr/lib/qt-3.3/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/dell/srvadmin/bin:.
export LD_LIBRARY_PATH=/wrk/users/slehti/CMSSW_10_6_20/biglib/slc7_amd64_gcc820:/wrk/users/slehti/CMSSW_10_6_20/lib/slc7_amd64_gcc820:/wrk/users/slehti/CMSSW_10_6_20/external/slc7_amd64_gcc820/lib:/\ cvmfs/cms.cern.ch/slc7_amd64_gcc820/cms/cmssw/CMSSW_10_6_20/biglib/slc7_amd64_gcc820:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/cms/cmssw/CMSSW_10_6_20/lib/slc7_amd64_gcc820:/cvmfs/cms.cern.ch/slc7_amd64_\ gcc820/cms/cmssw/CMSSW_10_6_20/external/slc7_amd64_gcc820/lib:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/llvm/7.1.0-pafccj/lib64:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/gcc/8.2.0-pafccj/lib\ 64:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/gcc/8.2.0-pafccj/lib:/cvmfs/cms.cern.ch/slc7_amd64_gcc820/external/cuda/10.1.105-pafccj2/drivers