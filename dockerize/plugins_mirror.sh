#!/bin/bash

SOURCE=/home/backups/backups/test
DEST=$1
OBJECTIVE=$2
REMOVE_FILE=$3

shopt -s nocasematch
if [ -z "$OBJECTIVE" ]
then
	OBJECTIVE='DOWNLOAD'
elif [[ $OBJECTIVE == 'upload' ]]; then
	#statements
	OBJECTIVE='UPLOAD'
	TEMP=$SOURCE
	SOURCE=$DEST
	DEST=$TEMP
else
	OBJECTIVE='DOWNLOAD'
fi
if [[ $REMOVE_FILE == 'True' ]]; then
	REMOVE_FILE='-e'
else
	REMOVE_FILE=''
fi
shopt -u nocasematch

echo 'Source :' $SOURCE
echo 'Destination :' $DEST
echo 'Objective :' $OBJECTIVE

lftp -u kartoza, sftp://plugins.qgis.org -e "mirror $REMOVE_FILE -R $SOURCE $DEST; bye"