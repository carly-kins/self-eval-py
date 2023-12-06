# Self-Eval CLI 

Foobar is a Python and SQL-Lite CLI to make keeping track of self evaluations a little easier! 

## Installation

Navigate to `requirements.txt` and run...

```bash
pip install -r requirements.txt
```
_Note: You are also going to need to create a `schema.sql` that is not included in this repo._

Once you have the needed dependencies
- Make the file `selfeval` executable with `chmod +x`
- Make sure to save/symlink to wherever you keep your shell scripts! 

## Usage
* `ls`: list all entries
    * `--csv`: display in csv format
    * `--doc`: display evaluation output in word format
    * `--last`: display entries from a specified date to now (ex. since last checkin)
    * `--between`: display entries between 2 specified dates
* `add`: add new entry
    * `--git`: add last git commit message as entry
    * `-n, --notes`: add notes to entry
* `rm`: add new entry
    * `id`: entry id (taken from `self-eval ls`)
* `update`: update entry
    * `id`: entry id (taken from `self-eval ls`)
    * `-e, --entry`: update entry
    * `-n, --notes`: update notes
    * `-t, --tags`: update tags
    * `-ty, --types`: update types
* `find`: find entries
    * `query`: search query
    * `--csv`: display in csv format
* `load`: load links from csv
    * `csv_file`: load links from csv

## Thank you

Based off of code from [Federico Menozzi](https://github.com/fmenozzi/env/blob/master/scripts/links) - Thanks Fed! 
