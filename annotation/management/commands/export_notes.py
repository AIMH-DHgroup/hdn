#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
from django.core import serializers
from django.core.management.base import BaseCommand
from annotation.models import Annotation

# Base directory of Annotation app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# JSON file paths
NOTE_PATH = os.path.join(BASE_DIR, 'json/notes.json')

a = Annotation.objects

class Command(BaseCommand):
    help = 'Exports notes from DB'

    # Define command-line options
    def add_arguments(self, parser):
        parser.add_argument('-p', '--path', dest='path', help='export notes to this path',
                            default=NOTE_PATH)

    def handle(self, *args, **options):
        # Get command-line options
        opt_path = options.get('path')

        errors = []

        try:
            print()

            # Export notes
            print('   Exporting notes...   ', end='')
            exported_note_count = 0
            
            try:
                # Notes to be exported
                notes = serializers.serialize('json', a.all())

                # Write notes to JSON file
                with open(opt_path, 'w') as note_file:
                    note_file.write(notes)
            except:
                raise

            print(f'Exported {a.all().count()} notes')
            print()

            if errors:
                print('\n'.join(errors))
                print()

        # Exit gracefully in case of keyboard interrupt
        except KeyboardInterrupt:
            print('\n')
            sys.exit()
