#/bin/bash

path=.
idx=-1
for fin in `ls ${path} | grep rates_plot`; do
    ((idx++))
    fout=${fin:0:-4}_edited.pdf
    foutList[${idx}]=${path}/${fout}
    finList[${idx}]=${path}/${fin}
    echo "Editing ${fin} into ${fout}"
    python editPDF.py ${path}/${fin} ${path}/${fout}
done
nfiles=$((idx+1))

echo "Check edited files:"
for ((i=0; i<nfiles; i++)); do
    evince ${foutList[${i}]} &
done

read -p "Do you wish to replace plots? [y/n]  " replacePlots
if [ "$replacePlots" = "y" ]; then
    for ((i=0; i<nfiles; i++)); do
        # Convert into ps and back into pdf because there can be
        # "encoding issues" and this "re-encodes" the pdf nicely
        fout=${foutList[${i}]}
        f=${fout:0:-4}
        pdftops ${f}.pdf ${f}.ps
        ps2pdf ${f}.ps ${f}.pdf
        rm ${f}.ps
        mv ${foutList[${i}]} ${finList[${i}]}
    done
else
    for ((i=0; i<nfiles; i++)); do
        rm ${foutList[${i}]}
    done
fi

