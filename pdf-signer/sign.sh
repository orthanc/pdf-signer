#! /bin/sh

BASE_DIR="$(dirname "$0")"
INPUT_FILE="${1}"
AMMOUNT="${2}"
DATE="${3:-$(date -Idate)}"

YEAR="${DATE%%-*}"
REM="${DATE#*-}"
MONTH="${REM%%-*}"
DAY="${REM#*-}"

cat "${INPUT_FILE}" |
	"${BASE_DIR}/cpdf-binaries-master/Linux-Intel-32bit/cpdf" -add-text "${AMMOUNT}" -pos-left '290 598' -stdin 1 -stdout |
	"${BASE_DIR}/cpdf-binaries-master/Linux-Intel-32bit/cpdf" -add-text "${DAY}" -pos-left '367 549' -stdin 1 -stdout |
	"${BASE_DIR}/cpdf-binaries-master/Linux-Intel-32bit/cpdf" -add-text "${MONTH}" -pos-left '387 549' -stdin 1 -stdout |
	"${BASE_DIR}/cpdf-binaries-master/Linux-Intel-32bit/cpdf" -add-text "${YEAR}" -pos-left '407 549' -stdin 1 -stdout |
	"${BASE_DIR}/cpdf-binaries-master/Linux-Intel-32bit/cpdf" -add-text "${DAY}" -pos-left '442 104' -stdin 2 -stdout |
	"${BASE_DIR}/cpdf-binaries-master/Linux-Intel-32bit/cpdf" -add-text "${MONTH}" -pos-left '462 104' -stdin 2 -stdout |
	"${BASE_DIR}/cpdf-binaries-master/Linux-Intel-32bit/cpdf" -add-text "${YEAR}" -pos-left '482 104' -stdin 2 -stdout \
	> "$(dirname "$INPUT_FILE")/$DATE-$(basename "$INPUT_FILE")"
