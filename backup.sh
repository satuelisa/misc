#!/bin/bash
mount /dev/sdb2 /media/usb
now=$(date +"%m_%d_%Y")
mkdir /media/usb/backup_$now
cd /media/usb/backup_$now
tar -czvf cgi.tar.gz /usr/lib/cgi-bin/
tar -czvf tools.tar.gz /home/elisa/tools/
tar -czvf jobs.tar.gz /home/elisa/jobs/
tar -czvf teaching.tar.gz /var/www/html/elisa/teaching/
tar -czvf research.tar.gz /var/www/html/elisa/research/
pwd
ls -lh
df -h
cd
umount /dev/sdb2
