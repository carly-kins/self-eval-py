#!/usr/bin/env python3

import csv
import sqlite3
import selfeval_vars
import selfeval_generate

import sys
import questionary
import subprocess

from pyutils import now_utc, strftime_format, fzf

FORMAT = '%Y-%m-%d'

def create_or_open_db():
    with open(selfeval_vars.SCHEMA_PATH, 'r') as schema_file:
        schema = schema_file.read()
    con = sqlite3.connect(selfeval_vars.DB_PATH)
    cur = con.cursor()
    cur.executescript(schema)
    con.commit()
    return con, cur

def list_array(table):
    con, cur = create_or_open_db()
    rows = cur.execute(f' SELECT * FROM {table};').fetchall()
    con.close()
    
    array = []
    for row in rows:
        if table == selfeval_vars.TYPES_TABLE: 
            ( _, entry ) = row
        else: 
            ( _, entry, _, _ ) = row
        array.append(entry)
    return array

TYPES_Q = questionary.select(selfeval_vars.TYPES_PRESETS,choices=list_array(selfeval_vars.TYPES_TABLE))
TAGS_Q = questionary.checkbox(selfeval_vars.TAGS_PRESETS,choices=list_array(selfeval_vars.TAGS_TABLE))
ENTRY_Q = questionary.text(selfeval_vars.ENTRY_PRESETS)
NOTES_Q = questionary.text(selfeval_vars.NOTES_PRESETS)

def entry_exists(id):
    con, cur = create_or_open_db()
    res = cur.execute('SELECT COUNT(*) FROM evalEntries WHERE id = ?', (id,))
    count, = res.fetchone()
    con.close()
    return count == 1

def stringify_row(row):
    id, entry, types, notes, tags, date_added = row
    return f'{id} {entry} {types} {notes} {tags} {date_added}'

def list_entries(args):
    con, cur = create_or_open_db()
    query = ''

    if 'last' in args and args.last:
        date = questionary.text(selfeval_vars.START_PRESETS, validate=lambda text: True if strftime_format(text) else selfeval_vars.DATE_INCORRECT ).ask()
        query = f'''
            SELECT * FROM {selfeval_vars.EVAL_TABLE} WHERE DATE(date_added) BETWEEN '{date}' AND '{now_utc()}';
        '''   
    elif 'between' in args and args.between:
        date_start = questionary.text(selfeval_vars.START_PRESETS, validate=lambda text: True if strftime_format(text) else selfeval_vars.DATE_INCORRECT ).ask()
        date_end = questionary.text(selfeval_vars.END_PRESETS, validate=lambda text: True if strftime_format(text) else selfeval_vars.DATE_INCORRECT ).ask()
        query = f'''
            SELECT * FROM {selfeval_vars.EVAL_TABLE} WHERE DATE(date_added) BETWEEN '{date_start}' AND '{date_end}';
        ''' 
    else:
        query = f'''
            SELECT * FROM {selfeval_vars.EVAL_TABLE};
        '''  
    res = cur.execute(query)
    rows = res.fetchall()
    con.close()

    if not rows:
        return
    if 'csv' in args and args.csv:
        selfeval_generate.csv_output(rows)
    elif 'doc' in args and args.doc:
        selfeval_generate.doc_output(rows)
    else:
        selfeval_generate.print_result_table(rows)

def add_entry(args):
    con, cur = create_or_open_db()
    types = ''
    tags = ''
    query = f'''
        INSERT INTO evalEntries (rowid, entry, types, notes, tags, date_added)
        VALUES (NULL, ?, ?, ?, ?, ?);
    '''
    if args.git: 
        types = TYPES_Q.ask()
        tags = str(TAGS_Q.ask())
        notes = selfeval_vars.NOTES_Q.ask() if args.notes else ''
        try:
            git = subprocess.run(['git', 'log', '-1', '--pretty=%B'], capture_output=True, text=True, check=True)
            git_string = git.stdout.strip()
        except subprocess.CalledProcessError as e:
            # Handle errors, if any
            print(f"Error: {e}")
            return None
        cur.execute(query, (git_string, types, notes, tags, now_utc()))
    else: 
        types = TYPES_Q.ask()
        entry = ENTRY_Q.ask()
        tags = str(TAGS_Q.ask())
        notes = NOTES_Q.ask() if args.notes else ''
        cur.execute(query, (entry, types, notes, tags, now_utc()))
    con.commit()
    con.close()

def remove_entry(args):
    if not entry_exists(args.id):
        print(f'Entry id {args.id} not found')
        sys.exit(1)
    con, cur = create_or_open_db()
    cur.execute(f'DELETE FROM {selfeval_vars.EVAL_TABLE} WHERE id = ?', (args.id,))
    con.commit()
    con.close()

def update(data, col, table, args, question, tags):
    if not tags: 
        e = question
        data.execute(f'UPDATE {table} SET {col} = ? WHERE id = ?', (e, args))
    else:
        new_t = question
        if '%t' in new_t:
            # %t represents the existing tags and is used to make easier modifications.
            old_t, = data.execute(f'SELECT {col} FROM {table} WHERE id = ?', (args,)).fetchone()
            new_t = new_t.replace('%t', old_t)
        data.execute(f'UPDATE {table} SET {col} = ? WHERE id = ?', (new_t, args))

def update_entry(args):
    if not entry_exists(args.id):
        print(f'Entry id {args.id} not found')
        sys.exit(1)
    con, cur = create_or_open_db()
    if not args.entry and not args.notes and not args.tags:
        print('Must update at least one of entry, notes, tags')
        sys.exit(1)
    if args.entry:
        update(cur, 'entry', selfeval_vars.EVAL_TABLE, args.id, ENTRY_Q.ask(), False)
    if args.notes:
        update(cur, 'notes', selfeval_vars.EVAL_TABLE, args.id, NOTES_Q.ask(), False)
    if args.tags:
        update(cur, 'tags', selfeval_vars.EVAL_TABLE, args.id, str(TAGS_Q.ask()), True)
    if args.types:
        update(cur, 'types', selfeval_vars.EVAL_TABLE, args.id, TYPES_Q.ask(), False)
    con.commit()
    con.close()

def find_entry(args):
    con, cur = create_or_open_db()
    if args.query:
        res = cur.execute('SELECT rowid, * FROM evalEntries_fts(?) ORDER BY rank;', (args.query,)) # I ain't touching virtual table stuff 
        rows = res.fetchall()
    else:
        res = cur.execute(f'SELECT * FROM {selfeval_vars.EVAL_TABLE};')
        rows = res.fetchall()
        stringified_rows_to_rows = {stringify_row(row): row for row in rows}
        fzf_input = stringified_rows_to_rows.keys()
        fzf_selection = fzf(fzf_input)
        if fzf_selection:
            rows = [stringified_rows_to_rows[fzf_selection]]
        else:
            rows = []
    con.close()
    if not rows:
        return
    if args.csv:
        selfeval_generate.csv_output(rows)
    else:
        selfeval_generate.print_result_table(rows)

def load_entries(args):
    with open(args.csv_file, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        data = []
        for row in reader:
            if not row:
                continue
            _, entry, types, notes, tags, date_added = row
            print(f'Loading {entry}...')
            data.append({
                "entry": entry,
                "types": types,
                "notes": notes,
                "tags": tags,
                "date_added": date_added,
            })
        con, cur = create_or_open_db()
        cur.executemany(
            'INSERT INTO evalEntries VALUES(NULL, :entry, :types, :notes, :tags, :date_added);',
            data
        )
        con.commit()
        con.close()