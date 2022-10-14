for f in `ls -1 *.png`; do b=`basename $f .png`; python clean.py $f $b.proc.png; mv *.proc.png procesados/; done
