#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Import notes

This file allows to import json notes into db.

Project: HDN
Package: Backend
Title: Import notes
File: import_notes.py
Path: annotation/management/commands
Type: python
Started: 2020-04-26
Author(s): Daniele Metilli & Nicolo' Pratelli
State: in use

Version history.

    * 2020-04-26 Daniele Metilli
      First version
    * 2020-09-22 Nicolo' Pratelli
      Installed and imported glob library
      Read all json files and print content to terminal

This file is part of software developed by the Digital Libraries group
of NeMIS Laboratory, Institute of Information Science and Technologies
(ISTI-CNR), Pisa, Italy, for the IMAGO and HDN projects.
Further information at: https://hdn.dantenetwork.it
Copyright (C) 2020 ISTI-CNR, Nicolo' Pratelli & Daniele Metilli

This is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 3.0 of the License,
or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""

import os
import sys
import json
import glob
import time
import random
import re
from django.core import serializers
from django.core.management.base import BaseCommand
from annotation.models import Annotation, Commentary, Owner
from django.contrib.auth.models import User

# Base directory of Annotation app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# JSON file paths
NOTE_PATH = os.path.join(BASE_DIR, 'json/notes.json')

a = Annotation.objects
c = Commentary.objects
o = Owner.objects
u = User.objects

class SwitcherCantica(object):
    def cantica_to_number(self, argument):
        """Dispatch method"""
        method_name = str(argument)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda: "Invalid cantica")
        # Call the method as we return it
        return method()

    def Inferno(self):
        return 1

    def Purgatorio(self):
        return 2

    def Paradiso(self):
        return 3



# Commentary assignments
assignments = {
    'Alessandro Vellutello 1544' : 'anna.chisena',
	'Anonimo Fiorentino 1400[?]' : 'gaia.tomazzoli',
	'Anonimo Selmiano 1337[?]' : '', # non assegnato
	'Anonymus Lombardus 1325[?]' : '', # non assegnato
	'Baldassare Lombardi 1791-92' : 'futuro.torinese',
	'Benedetto Varchi 1545' : '', # non assegnato
	'Benvenuto da Imola 1375-80' : 'leyla.livraghi1',
	'Brunone Bianchi 1868' : 'anna.salvade',
	'Carlo Grabher 1934-36' : '', # non assegnato
	'Carlo Steiner 1921' : 'leonardo.canova',
	'C.H. Grandgent 1909-13' : '', # non assegnato
	'Chiose Cagliaritane 1370[?]' : '', # non assegnato
	'Chiose Vernon 1390[?]' : '', # non assegnato
	'Codice cassinese 1350-75[?]' : '', # non assegnato
	'Cristoforo Landino 1481' : 'giulia.gaimari.14',
	'Enrico Mestica 1921-22 [1909]' : '', # non assegnato
	'Ernesto Trucchi 1936' : '', # non assegnato
	'Francesco da Buti 1385-95' : 'leonardo.canova',
	'Francesco Torraca 1905' : '', # non assegnato
	'G.A. Scartazzini 1872-82 [2nd ed. 1900]' : 'anna.salvade',
	'G.A. Scartazzini and G. Vandelli 1929' : '', # non assegnato
	'Giacomo Poletto 1894' : 'cgiorgiopriolo',
	'Giovan Battista Gelli 1541-63' : 'giulia.gaimari.14',
	'Giuseppe Campi 1888-93' : 'futuro.torinese',
	'Graziolo Bambaglioli 1324' : 'giuseppeandrea.liberti',
	'Gregorio di Siena 1867' : '', # non assegnato
	'Guiniforto delli Bargigi 1440' : 'giulia.gaimari.14',
	'Henry Wadsworth Longfellow 1867' : 'francesca.speranza',
	'Hermann Oelsner 1899' : '', # non assegnato
	'Isidoro del Lungo 1926' : 'leyla.livraghi1',
	'Jacopo Alighieri 1322' : '', # non assegnato
	'Jacopo della Lana 1324-28' : 'giuseppeandrea.liberti',
	'Johannis de Serravalle 1416-17' : '', # non assegnato
	'John Ruskin 1903' : '', # non assegnato
	'John S. Carroll 1904' : '', # non assegnato
	'Lodovico Castelvetro 1570' : 'anna.chisena',
	"L'Ottimo Commento 1333" : 'giuseppeandrea.liberti',
	'Luigi Bennassuti 1864-68' : 'futuro.torinese',
	'Luigi Pietrobono 1949 [1924-30]' : 'giuseppeandrea.liberti',
	'Luigi Portirelli 1804-05' : '', # non assegnato
	'Niccolò Tommaseo 1837 [ed. of 1865]' : 'francesca.speranza',
	'Paolo Costa 1819-21' : '', # non assegnato
	'P. Gioachino Berthier 1892-97' : '', # non assegnato
	'Pier Francesco Giambullari 1538-48' : '', # non assegnato
	'Pietro Alighieri (1) 1340-42' : 'anna.chisena',
	'Pietro Alighieri (2) 1344-55[?]' : '', # non assegnato
	'P. Pompeo Venturi 1732' : '', # non assegnato
	'Raffaello Andreoli 1856' : 'cgiorgiopriolo',
	'The Rev. H.F. Tozer 1901' : '', # non assegnato
	'Tommaso Casini and S.A. Barbi 1921' : 'gaia.tomazzoli',
	'Torquato Tasso 1555-68' : '' # non assegnato
}




class Command(BaseCommand):
    help = 'Imports notes into DB'

    # Define command-line options
    def add_arguments(self, parser):
        parser.add_argument('-p', '--path', dest='path', help='import notes from this path',
                            default=NOTE_PATH)
        parser.add_argument('-d', '--dryrun', dest='dry_run', help='run without writing to DB',
                            action='store_true', default=False)
        parser.add_argument('-o', '--overwrite', dest='overwrite', help='overwrite duplicate notes',
                            action='store_true', default=False)
        parser.add_argument('-x', '--delete', dest='delete', help='delete all notes from DB',
                            action='store_true', default=False)

    def handle(self, *args, **options):
        # Get command-line options
        opt_path = options.get('path')
        opt_dryrun = options.get('dry_run')
        opt_over = options.get('overwrite')
        opt_delete = options.get('delete')

        errors = []
        last_mod = time.time()

        files = [i for i in glob.glob(opt_path+'*')] 
        id_commentary = 0
         # Delete existing notes
        if opt_delete:
            a.all().delete()
            # c.all().delete()
            o.all().delete()
            print('   Deleted all notes from DB')

        total_notes = 0
        for f in sorted(files):

            id_commentary = id_commentary + 1
            # users = ["valentina", "daniele.metilli", "leyla.livraghi1", "gaia.tomazzoli", "carlo.meghini", "nicolo.pratelli"]
            # users = ["nicolo.pratelli"]
            # owner = random.choice(users)
            f_path = f.split("/")
            f_name = f_path[-1]

            try:
                print()

                # Import notes
                print('   Importing ' + f_name + ' notes...   ', end='')
                new_note_count = 0
                old_note_count = 0
                new_commentary_count = 0
                old_commentary_count = 0
                
                
                try:
                    # Load notes from JSON file
                    
                    with open(f) as note_file:

                        print()
                        
                        json_file = note_file.read()
                        # json_data = json.dumps(json_file)
                        data = json.loads(json_file)
                        number_of_note = 1
                        old_canto = 0
                        prev_line = ""
                        for note in data:
                            canto = note["Nota"]["OperaDante"]["Canto"]
                            if old_canto==0:
                                old_canto = canto
                            if old_canto != canto:
                                number_of_note = 1
                                old_canto = canto
                                prev_line = ""
                            # print(note)
                            cantica = SwitcherCantica()
                            cantica_number = cantica.cantica_to_number(note["Nota"]["OperaDante"]["Cantica"])
                            # print(cantica_number)
                            canto = note["Nota"]["OperaDante"]["Canto"]
                            if canto.isnumeric():
                                format_canto = canto #"{0:0=2d}".format(canto)
                                # print(format_canto)
                                format_number_of_note = "{0:0=3d}".format(number_of_note*10)
                                # print(format_number_of_note)

                                
                                if(re.search("\d+\s?-\s?\d+|\d+", note["Nota"]["OperaDante"]["Verso"])):
                                    prev_line = note["Nota"]["OperaDante"]["Verso"]
                                else:
                                    if(prev_line == ""):
                                        note["Nota"]["OperaDante"]["Verso"] = note["Nota"]["OperaDante"]["Verso"]
                                    else:
                                        note["Nota"]["OperaDante"]["Verso"] = prev_line
                                
                                note["Nota"]["Citazioni"] = []


                                dante_fragment = note["Nota"]["FrammentoDante"]

                                

                                note["Nota"]["FrammentoDanteDDP"] = dante_fragment
                                note["Nota"]["FrammentoDante"] = ""

                                commentary = note["Nota"]["Commento"]
                                
                                try:
                                    comm = c.get(data__name=commentary)
                                except Commentary.DoesNotExist:
                                    print(commentary)
                                

                                note_id = int(str(comm.data['id']) + str(cantica_number) + str(format_canto) + str(format_number_of_note))
                                # print(note_id)

                                note["Stato"] = "to-do"
                                note["LastMod"] = last_mod
                            
                                owner = assignments[commentary]
                                if owner == '':
                                    owner = 'not.assigned'
                                note["owner"] = owner
                                note["reviewer"] = owner
                                
                                try:
                                    user = u.get(username=owner)
                                except User.DoesNotExist:
                                    new_user = u.create_user(owner, '', 'hdn2021')
                                    if not opt_dryrun:
                                        new_user.save()

                                user = u.get(username=owner)

                                body_nota = note["Nota"]["BodyNota"]

                                if comm.data['name'] == "Torquato Tasso 1555-68":
                                    if(re.search("\s?Celani\)", dante_fragment )):
                                        body_nota = "<b>(ed." + dante_fragment + "</b> " + body_nota
                                        note["Nota"]["BodyNota"] = body_nota
                                        dante_fragment = ""
                                        note["Nota"]["FrammentoDanteDDP"] = dante_fragment
                               
                                body_nota = re.sub('^[,.:]?\s+-?-?\s?', '', body_nota)
                                body_nota = re.sub('^ec\.[,;:]?', '', body_nota)

                                #&laquo;
                                # body_nota = re.sub('<(?![i\\b\/])', '&laquo;', body_nota)
                                body_nota = re.sub('<(?=\s?\w\w)', '&laquo;', body_nota)

                                # #&raquo;
                                # body_nota = re.sub('>(?<![ib])', '&raquo;', body_nota) problema con le citazioni che si concludono con punteggiatura
                                # body_nota = re.sub('>(?<=\w\w)', '&raquo;', body_nota)
                                body_nota = re.sub('(?<=\w[\.,;!\)\?\w])>', '&raquo;', body_nota)

                                # &mdash;
                                body_nota = re.sub('--', '&mdash;', body_nota)

                                # sup
                                sup_regex = re.compile('\+[^~]+~') 
                                while(sup_regex.search(body_nota) is not None):
                                    sup = sup_regex.search(body_nota) 
                                    sup_text = sup.group(0)
                                    sup_tag = "<sup>"+sup_text[1:-1]+"</sup>"
                                    body_nota = body_nota[:sup.start()] +sup_tag+ body_nota[sup.end():]
                                    
                                    
                               
                                # print(body_nota)
                                

                                note["Nota"]["BodyNota"] = body_nota


                                # note["Nota"]["BodyNotaDDP"] = body_nota
                                # note["Nota"]["BodyNota"] = ""

                                # print(comm.data)

                                commentaryDict = {}
                                commentaryDict["Id"] = int(comm.data['id'])
                                commentaryDict["IRI"] = comm.data['iri']#str(id_commentary)
                                commentaryDict["Nome"] = comm.data['name'] #commentary
                                        
                                

                                note["Nota"]["Commento"] = commentaryDict

                                try:
                                    o.get(commentary=comm.data['name'], owner=user)
                                except Owner.DoesNotExist:
                                    new_owner = Owner(commentary=comm.data['name'], owner=user)
                                    if not opt_dryrun:
                                        new_owner.save()


                                # For each note in file
                                # for note in serializers.deserialize("json", json_load):
                                #     print(note)
                                # Check if commentary exists in DB
                                # try:
                                #     c.get(data__name=comm.data['name'])
                                # except Commentary.DoesNotExist:
                                #     commentary_json = {'id': comm_id, 'iri': iri, 'name': name}
                                #     new_commentary = Commentary(data=commentary_json)
                                #     if not opt_dryrun:
                                #         new_commentary.save()
                                #     new_commentary_count += 1
                                # else:
                                #     old_commentary_count += 1
                            
                                # Check if note exists in DB
                                try:
                                    a.get(pk=note_id)
                                except Annotation.DoesNotExist:
                                    if not opt_dryrun:
                                        # note.object.save()
                                        a.create(id=note_id, data=note)
                                    new_note_count += 1
                                else:
                                    if opt_over and not opt_dryrun:
                                        # note.object.save()
                                        a.create(id=note_id, data=note)
                                        new_note_count += 1
                                    old_note_count += 1
                                number_of_note = number_of_note + 1
                            else:
                                print("Excluded note")
                            
                except:
                    raise
                
                total_notes = total_notes + new_note_count 
                duplicate_notes = f', {old_note_count} duplicates' if old_note_count else ''
                print(f'Added {new_note_count} notes{duplicate_notes}')
                print()

                print(f'Added {new_commentary_count} commentaries')
                print()

                if errors:
                    print('\n'.join(errors))
                    print()

            # Exit gracefully in case of keyboard interrupt
            except KeyboardInterrupt:
                print('\n')
                sys.exit()
                
        print(f'Added {total_notes} notes')
