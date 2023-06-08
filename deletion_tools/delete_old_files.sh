#!/bin/bash

directory=$1

usage() {
  echo -e "\033[1mSYNOPSIS\033[0m"
  echo -e "\tdelete_old_files.sh DIRECTORY_NAME NUMBER_OF_DAYS [ACTION]"
  echo -e "\n\033[1mOPTIONS\033[0m"
  echo -e "    \033[1mACTION\033[0m"
  echo -e "        If no action, will delete files!"
  echo -e "        ls\tList files to be deleted"
}

if [ -z $1 ]; then
  usage
  exit 1
fi

if [ -z $2 ]; then
  usage
  exit 1
fi

if [ -z $3 ]; then
  action="-delete"
elif [ "$3" == "ls" ]; then
  action=''
else
  action="-$3"
fi

if [ ! -d ${directory} ]; then
  echo "${directory} is not a directory!"
  exit 1
fi

find ${directory} -type f -mtime +$2 ${action}

