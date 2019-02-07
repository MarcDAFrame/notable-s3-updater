#!/bin/sh
#create directories
mkdir ~/.notable
#moves the pyfile there
mv ./notablechanges.py ~/.notable/
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "* * * * * /usr/local/bin/python3 ~/.notable/notablechanges.py > /tmp/listener.log 2>&1" >> mycron
#install new cron file
crontab mycron
rm mycron