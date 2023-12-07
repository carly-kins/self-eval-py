-- Create main content table for evaluation and a full-text search index table.
create table if not exists evalEntries (
    id integer primary key,
    entry text not null unique,
    types text,
    notes text,
    tags text,
    date_added text not null
);
create virtual table if not exists evalEntries_fts using fts5(
    content=evalEntries,
    tokenize='porter trigram',
    entry,
    types,
    notes,
    tags,
    date_added
);
create table if not exists types_table (
    types_id integer primary key,
    types text not null unique
);
create table if not exists tags_table (
    tags_id integer primary key,
    tags text not null unique,
    tags_description text not null unique,
    summary text
);
create table if not exists summary_table (
    summary_id integer primary key,
    summary text not null unique
);
create table if not exists questions_table (
    questions_id integer primary key,
    question_title text not null unique,
    question_desc text not null unique,
    types_id integer
);

-- Triggers to keep the FTS index up-to-date.
create trigger if not exists evalEntries_after_insert after insert on evalEntries begin
    insert into evalEntries_fts(rowid, entry, types, notes, tags, date_added)
    values (new.rowid, new.entry, new.types, new.notes, new.tags, new.date_added);
end;
create trigger if not exists evalEntries_after_delete after delete on evalEntries begin
    insert into evalEntries_fts(evalEntries_fts, rowid, entry, types, notes, tags, date_added)
    values ('delete', old.rowid, old.entry, old.types, old.notes, old.tags, old.date_added);
end;
create trigger if not exists evalEntries_after_update after update on evalEntries begin
    insert into evalEntries_fts(evalEntries_fts, rowid, entry, types, notes, tags, date_added)
    values ('delete', old.rowid, old.entry, old.types, old.notes, old.tags, old.date_added);
    insert into evalEntries_fts(rowid, entry, types, notes, tags, date_added)
    values (new.rowid, new.entry, new.types, new.notes, new.tags, new.date_added);
end;
