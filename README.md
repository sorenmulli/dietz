# Dietz

A hymnal-style online songbook with a minimalistic, phone-friendly UI on top of a catalogue of songs with rich metadata.

## Rules

(I) No LLMs: I will not use LLMs for this project, not even for research

(II) No Conventions: Pragramtism or curiosity only motivations for techincal decisions. No autoformatters nor linters.

## Features

- Minimalistic presentation of lyrics
- Multiple songbooks in one web-app.
- For each songbook, browse by category, by author, by year.

## Architecture

- Web-app: What about FastAPI serving Jinja2 docs.
- Catalogue: At-rest is JSONL, loaded into memory and indexed at application startup.

## Name

[Ludwig Dietz](https://salmer.dsl.dk/dietz-salmebog-1529/titelblad)
