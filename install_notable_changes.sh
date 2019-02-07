#!/bin/sh
#create directories
mkdir ~/.notable
#moves the pyfile there
mv ./notablechanges.py ~/.notable/
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "* * * * * sh /usr/local/bin/python3 ~./.notable/notablechanges.py" >> mycron
#install new cron file
crontab mycron
rm mycron