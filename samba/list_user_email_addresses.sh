#!/usr/bin/env bash
set -euo pipefail

# Get the email addresses of users who have logged in with SSH since a specified number of days ago.

if [ "$#" -eq 0 ]; then
  DAYS=30
elif [ "$#" -eq 1 ]; then
  DAYS=$1
else
  echo "Wrong number of arguments. Usage: $0 [days]"
  echo "The optional argument \"days\" specifies how many days back to look for user logins."
fi

DATE=$(date --date "-${DAYS} days" -I)
echo "Looking for users who have logged in with SSH since ${DATE}. This requires sudo access."
USERS=$(sudo journalctl -u ssh --since "${DATE}" | grep "Accepted" | awk '{print $9}' | sort --unique)

echo "Searching the LDAP directory for email addresses of the users."
EMAILS=$(for USERNAME in $USERS; do
  ldapsearch "(cn=${USERNAME})" mail | awk '/^mail:/ {print $2}'
done | sort --unique)

echo "Email addresses of users who logged in since ${DATE}:"
echo "${EMAILS}"
