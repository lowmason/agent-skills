# Parcel bands

A parcel's band sets its postage. The band depends on the parcel's weight in whole grams.

## Rules

`band` returns `small` for a weight of up to 500 grams, 500 included.

`band` returns `medium` for a weight above 500 grams and up to 2000 grams, 2000 included.

`band` returns `large` for a weight above 2000 grams.
