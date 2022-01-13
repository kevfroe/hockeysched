#!/bin/bash

crontab -l > crontab_new 
echo "0 * * * * /home/pi/Documents/hockeysched/scripts/hockeysched.sh > /home/pi/Documents/hockeysched/logs/hockeysched.txt" >> crontab_new
echo "" >> crontab_new
crontab crontab_new
rm crontab_new
