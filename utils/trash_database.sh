#!/usr/bin/env bash
if [ x$BASH = x ] || [ ! $BASH_VERSINFO ] || [ $BASH_VERSINFO -lt 4 ]; then
  echo "Error: Must use bash version 4+." >&2
  exit 1
fi
set -ue

Usage="Usage: \$ $(basename $0)"

APPS="traffic myadmin notepad"
GENERATED_BY_REGEX='# Generated by Django [0-9.]+ on [0-9-]+ [0-9:]+$'

function main {
  if [[ $# -ge 1 ]] && [[ $1 == '-h' ]]; then
    fail "$Usage"
  fi

  if ! [[ -f db.sqlite3 ]]; then
    fail "Error: db.sqlite3 not present."
  fi

  # Move the old database to a .bak file.
  if [[ -f db.sqlite3.bak ]]; then
    trash db.sqlite3.bak
  fi
  mv db.sqlite3 db.sqlite3.bak

  # Delete migrations for each app.
  for app in $APPS; do
    echo "Deleting migrations for $app.."
    for migration in $app/migrations/[0-9][0-9][0-9][0-9]_*.py; do
      if [[ -f $migration ]]; then
        echo "Deleting $migration.."
        trash $app/migrations/[0-9][0-9][0-9][0-9]_*.py
      fi
    done
  done

  # Re-generate a new migration for each app.
  for app in $APPS; do
    echo "Making migration for $app.."
    python3 manage.py makemigrations $app
  done

  for app in $APPS; do
    migration=$app/migrations/0001_initial.py
    if [[ $(git diff -U0 $migration | wc -l) == 7 ]]; then
      echo "Fixing generated timestamp line in $migration.."
      old_line=$(git diff $migration | grep -E "^-$GENERATED_BY_REGEX" | tail -c +2)
      sed -E "s/^$GENERATED_BY_REGEX/$old_line/" $migration > $migration.new
      mv $migration.new $migration
    fi
  done

  # Create a new database and commit migrations to it.
  echo "Migrating database.."
  python3 manage.py migrate
}

# DELETE FROM traffic_visit;
# DELETE FROM traffic_visitor;
# DELETE FROM traffic_user;
# ALTER SEQUENCE traffic_visit_id_seq RESTART WITH 1;
# ALTER SEQUENCE traffic_visitor_id_seq RESTART WITH 1;
# ALTER SEQUENCE traffic_user_id_seq RESTART WITH 1;

function fail {
  echo "$@" >&2
  exit 1
}

main "$@"
