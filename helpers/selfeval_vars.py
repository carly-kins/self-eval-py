#!/usr/bin/env python3
import os

#Variables to customize based on your own environment setup

HOME= os.getenv('HOME')

# The name you want on your eval
NAME = 'Carly' 
# Where you want your database saved
DB_PATH = f'{HOME}/dev/.oh-my-zsh-custom/databases/evaluation/evaluation.db'
# Where your database schema is saved
SCHEMA_PATH = f'{HOME}/dev/.oh-my-zsh-custom/databases/evaluation/evaluation_schema.sql'

# Table names in the schema
EVAL_TABLE = 'evalEntries'
TAGS_TABLE = 'tags_table'
TYPES_TABLE = 'types_table'
SUMMARY_TABLE = 'summary_table'
QUESTIONS_TABLE = 'questions_table'

# Question presets 
START_PRESETS = 'Start Date:'
END_PRESETS = 'End Date:'
DATE_INCORRECT = 'Incorrect data format, should be YYYY-MM-DD'
TYPES_PRESETS = 'Achievement / Improvement:'
TAGS_PRESETS = 'Self-Eval Tags:'
ENTRY_PRESETS = 'Entry:'
NOTES_PRESETS = 'Notes:'

#Data for calculating the width of the terminal
WIDTH_PRESETS = {
    114: (18, 10, 8),
    160: (34, 18, 12),
    205: (48, 24, 14),
    230: (48, 24, 14),
}