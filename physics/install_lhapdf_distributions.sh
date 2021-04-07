#!/usr/bin/bash -e

if [ "$EUID" -ne 0 ]; then
  echo "This script should be run as root."
  exit
fi

PDF_FOLDER="/usr/local/share/LHAPDF"
PDF_URL="http://lhapdfsets.web.cern.ch/lhapdfsets/current"
mkdir -p $PDF_FOLDER

install_pdf() {
  wget "${PDF_URL}/${1}.tar.gz" -O- | tar xz -C $PDF_FOLDER
}

install_pdf "CT10nlo"
install_pdf "cteq6l1"
