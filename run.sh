#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

VMARC="$1"
OUTDIR="$2"

if [ "$VMARC" != "" ] && [ ! -f "$VMARC" ]; then
    echo "'$VMARC' finnes ikke"
fi
if [ "$OUTDIR" != "" ] && [ ! -d "$OUTDIR" ]; then
    echo "'$OUTDIR' finnes ikke"
fi
if [ ! -f "$VMARC" ] || [ ! -d "$OUTDIR" ]; then
    echo "bruk: ./run.sh </path/to/data.vmarc.txt> <output_dir>"
    exit 1
fi

GENRE_TEMP_MARC="/tmp/genre.marc"
GENRE_TEMP_CSV="/tmp/genre.csv"

echo "lager $GENRE_TEMP_MARC..."
cat "$VMARC" | grep "^.\(001\|245\|655\)" > $GENRE_TEMP_MARC

echo "lager $GENRE_TEMP_CSV..."
if [ -f "$GENRE_TEMP_CSV" ]; then
    rm "$GENRE_TEMP_CSV"
fi
IDENTIFIER=""
TITLE=""
GENRE=""
TOTAL_BOOKS="`cat "$VMARC" | grep "^.\(001\)" | wc -l`"
COUNT=0
while read line; do
    
    TAG="`echo $line | sed 's/^.\(...\).*$/\1/'`"
    if [ "$TAG" = "001" ]; then
        BOOK_COUNTER=$((BOOK_COUNTER+1))
        if [ "$(($BOOK_COUNTER % 1000))" = "0" ]; then
            echo "$BOOK_COUNTER av $TOTAL_BOOKS katalogposter behandlet"
        fi
        
        if [ "$IDENTIFIER" != "" ]; then
            echo "\"$GENRE\",\"$IDENTIFIER\",\"$TITLE\"" >> $GENRE_TEMP_CSV
            IDENTIFIER=""
            TITLE=""
            GENRE=""
        fi
        IDENTIFIER="`echo $line | sed 's/^....0*//' | sed 's/"/""/g'`"
    elif [ "$TAG" = "245" ]; then
        TITLE="`echo $line | grep '\$a' | sed 's/.*\$a//' | sed 's/\$.*//' | sed 's/"/""/g'`"
    elif [ "$TAG" = "655" ]; then
        GENRE="`echo $line | grep '\$a' | sed 's/.*\$a//' | sed 's/\$.*//' | sed 's/"/""/g'`"
    fi
done < "$GENRE_TEMP_MARC"
if [ "$IDENTIFIER" != "" ]; then
    echo "\"$GENRE\",\"$IDENTIFIER\",\"$TITLE\"" >> $GENRE_TEMP_CSV
fi

echo "lager XML..."
python3 $DIR/build-xml.py $GENRE_TEMP_CSV $OUTDIR

echo "Sjanger-XML ligger nå ferdig i '$OUTDIR'."
