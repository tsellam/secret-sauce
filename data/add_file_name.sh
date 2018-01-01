#!/bin/bash
awk -F, '{if (NR > 1) {print $0 ",\"s"  NR-2 ".wav\""} else {print $0 ",file"}}' $1  > $2
