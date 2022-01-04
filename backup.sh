#!/bin/bash

#First the database backups on the remote server
SOURCE=/mnt/HC_Volume_4113275
DEST=backups
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

lftp -u kartoza, sftp://plugins.qgis.org -e "mirror $REMOVE_FILE $SOURCE $DEST; bye"

#Next the plugin backups on the remote server
SOURCE=/mnt/HC_Volume_4113256/packages
DEST=static
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

lftp -u kartoza, sftp://plugins.qgis.org -e "mirror $REMOVE_FILE $SOURCE $DEST; bye"


#Next the style backups on the remote server
SOURCE=/mnt/HC_Volume_4113256/styles
DEST=styles
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

lftp -u kartoza, sftp://plugins.qgis.org -e "mirror $REMOVE_FILE $SOURCE $DEST; bye"
