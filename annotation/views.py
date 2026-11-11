"""

| **Project**: HDN
| **Package**: Backend
| **Title**: Views in Django
| **File**: views.py
| **Path**: annotation/
| **Type**: python
| **Started**: 2020-04-26
| **Author(s)**: Nicolo' Pratelli & Daniele Metilli
| **State**: in use

Version history.

2020-04-26 Nicolo' Pratelli & Daniele Metilli
    * First version

2020-05-07 Daniele Metilli
    * Added autocomplete

2020-06-16 Nicolo' Pratelli
    * Added multiple subject management

This file is part of software developed by the Digital Libraries group
of AIMH Laboratory, Institute of Information Science and Technologies
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

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.db.models import Count, Q
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.text import slugify
from django.forms.formsets import formset_factory
from django.contrib.auth import authenticate
from .forms import *
from .models import *
from urllib.error import HTTPError
import urllib.request
import json as j
import datetime
import time
import re



WD_ENTITY_URL = 'http://www.wikidata.org/entity/'
WD_SPARQL_URL = 'http://query.wikidata.org/sparql?query='
HDN_BASE_IRI = 'https://hdn.dantenetwork.it/resource/'
ANONYMOUS_IRI = 'http://www.wikidata.org/entity/Q4233718'
MISSING_IRI = 'https://hdn.dantenetwork.it/resource/author/missing'

def perc(num, tot):
    return round((num*100)/tot)

class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, YourCustomType):
            return str(obj)
        return super().default(obj)

# Per Cesare
# Controllare l'owner delle note e visualizzare solo i commenti posseduti dall'owner
@xframe_options_exempt
def get_commentaries(request):
    """Get list of commentaries assigned to a specific annotator and render the list in index.html

    Build index page, showing the commentaries assigne to an annotator.

    :param request: The request object used to generate this response
    :type request: Request
    :return: render the commentary list in index.html
    :rtype: HttpResponse
    """
    STYLE = "\"font-size: 1.5em; margin: 0 6% 0 6%; line-height: 150%\""
    
    def color(text, color):
        return f'<span style="color: {color};">{text}</span>'

    entry_response_strings = []
    
    try:
        token = request.GET['gcube-token']
    except MultiValueDictKeyError:
        token=request.session.get('gcube-token');
        
    if not token:
        raise Http404("Access denied")
    
   
   
    print ("got token")
    vreuser=""
    
    d4url = f'https://api.d4science.org/rest/2/people/profile?gcube-token={token}'

    try:
        with urllib.request.urlopen(d4url) as response:
            d4json = j.loads(response.read())
            
            if 'success' in d4json and d4json['success'] is True:
                print ('token is valid, user: '+d4json['result']['fullname'])
                try:
                    vreuser=d4json['result']['username']
                    usr = User.objects.get(username= vreuser)
                    print(f'User { d4json["result"]["username"]} exists in DB')
                except:
                    print(f'User {  d4json["result"]["username"]} does not exist in DB')
            else:
                print(f'User {  d4json["result"]["username"]} error in calling D4Science API')

    except HTTPError:
        print('Token is not valid')
    
    
    # notes = Annotation.objects.filter(data__owner=request.user.id) # prende solo le note di un owner
    notes = Annotation.objects.filter(data__owner=vreuser) # prende solo le note di un owner
    done = Count('data__Nota__Commento', filter=Q(data__Stato='done')) 
    commentaries = notes.values('data__Nota__Commento').order_by('data__Nota__Commento').annotate(count=Count('data__Nota__Commmento'), done=done)
    note_list = [{'idCommentary': obj['data__Nota__Commento']['Id'], 'Commentary': obj['data__Nota__Commento']['Nome'],
                'Count': obj['count'], 'Done': perc(obj['done'],obj['count'])} for obj in commentaries]
    context = {'note_list' : note_list}

    
    
    #return render(request, 'annotation/index.html', context)
    
    #cesare
    request.session['gcube-token'] = token
    response = render(request, 'annotation/index.html', context) # django.http.HttpResponse
    #response.set_cookie(key='gcube-token', value=token)
    return response
    
    #/cesare


# Per Cesare
# Controllare che la nota estratta sia posseduta dall'owner che fa la richiesta
@xframe_options_exempt
def get_last_note(request, commentary):
    """Get the commentary id and redirect to the last modified note

    From the url of a commentary, get the id of the commentary and chose the right note. 
    The right note is the last modified note, but if there are two or more notes with last update
    at the same time, get the first, order by id.

    :param request: The request object used to generate this response
    :type request: Request
    :param commentary: The id of the commentary
    :type commentary: int
    :return: redirect to the last modified note order by id
    :rtype: HttpResponse

    """
    # Get the last mod note
    id_last_mod_note = Annotation.objects.filter(data__Nota__Commento__Id=commentary).order_by('-data__LastMod','id')[0]
    #id_last_mod_note = Annotation.objects.filter(data__Nota__Commento__Id=commentary, data__owner=request.user.id).order_by('data__LastMod','id')[0]
    # print(id_last_mod_note.id)
    #url = '/django/annotation/'+str(commentary)+'/'+str(id_last_mod_note.id)
    url = '../'+str(commentary)+'/'+str(id_last_mod_note.id) +'/0' 
    return HttpResponseRedirect(url)


# Cesare
# Controllare che la nota sia posseduta dall'owner
#@login_required
#@permission_required('annotation.change_annotation', raise_exception=True)
@xframe_options_exempt
@csrf_exempt
def get_note(request, commentary, note_id, cookie = 1):
    """Get the note and build the form

    This view build the form, starting from note id. It get from db the note and buid the page.

    :param request: the request
    :type request: Request
    :param commentary: the id of the commentary
    :type commentary: int
    :param note_id: the id of the note
    :type note_id: int
    :return: build the form
    :rtype: HttpResponse or JsonResponse
    """
    print("****************************** test ***********************************************")
    #cesare 
    ustoken = request.session.get('gcube-token')
    myuser =  authenticate(ustoken)
    #'TOKEN_RIMOSSO')
    
    if myuser==None:
        raise Http404("Token not valid, access denied")
    
    #/cesare
    start = time.time()
        
    # if this is a POST request we need to process the form data
    json = "{}" # Create an empty json

    # Initialize the formsets, specifying the form and formset we want to use.
    CharacterFormSet = formset_factory(CharacterForm)
    TopographyFormSet = formset_factory(TopographyForm)
    ReferenceCommentatorsFormSet = formset_factory(ReferenceCommentatorsForm)
    FreeTextFormSet = formset_factory(FreeTextForm) 

    # Extract the note by id
    #note = Annotation.objects.filter(data__owner=request.user.id, pk=note_id)
    
    #cesare
    note = Annotation.objects.filter(data__owner=myuser.username, pk=note_id)
    #/cesare
   
    if(note):
        extract = note.get(pk=note_id)
        
        # Extract comment id from note id
        comm_number = int(str(note_id)[:5])
        # if len(str(note_id)) == 7:
        #     # if note_id length is 7, extract first digit
        #     comm_number = str(note_id)[:1] 
        # else:
        #     # if note_id length is 8, extract first two digit
        #     comm_number = str(note_id)[:2] 

        if Annotation.objects.filter(data__Nota__Commento__Id=comm_number, data__Nota__OperaDante__Cantica="Inferno").exists():
            inferno = True
        else:
            inferno = False
        if Annotation.objects.filter(data__Nota__Commento__Id=comm_number, data__Nota__OperaDante__Cantica="Purgatorio").exists():
            purgatorio = True
        else:
            purgatorio = False
        if Annotation.objects.filter(data__Nota__Commento__Id=comm_number, data__Nota__OperaDante__Cantica="Paradiso").exists():
            paradiso = True
        else:
            paradiso = False

        print(inferno)
        print(purgatorio)
        print(paradiso)
        

        # Extract next notes from db and take id of the next note
        next_el = Annotation.objects.filter(id__gt=note_id, data__Nota__Commento__Id=comm_number).order_by("id")   #note_id + 1
        if len(next_el) > 0:
            next_id = next_el[0].id
        else:
            next_id = note_id + 1
        print("Next id: " + str(next_id))
        # Next id (Una query che estrae gli id minori di quello, e prende il primo)
        prev_el = Annotation.objects.filter(id__lt=note_id, data__Nota__Commento__Id=comm_number).order_by("-id") #note_id - 1
        if len(prev_el) > 0:
            prev_id = prev_el[0].id
        else:
            prev_id = note_id - 1
        print("Prev id: " + str(prev_id))

        first_el = Annotation.objects.filter(data__Nota__Commento__Id=comm_number).order_by("id")
        # first_str = comm_number + "101000"
        first_id = first_el[0].id
        print("First id: " + str(first_id))
        # first = Annotation.objects.first()
        # first_id = first.id - 1
        last_el = Annotation.objects.filter(data__Nota__Commento__Id=comm_number).order_by("-id")
        # next_comm_number = int(comm_number) + 1
        last_id = last_el[0].id
        print("Last id: " + str(last_id))
        # last = Annotation.objects.last()
        # last_id = last.id + 1

        json = extract.data
        # id = extract.id
        nota = json # nota = j.loads(json)
        json_formatted_str = j.dumps(nota, indent=2)


        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            note_form = NoteForm(request.POST)
            citation_form = CitationForm(request.POST)
            reference_content_form = ReferenceContentForm(request.POST)
            reference_relationship_form = ReferenceRelationshipForm(request.POST)
            reference_form = ReferenceForm(request.POST)
            dante_text_form = DanteTextForm(request.POST)
            body_note_form = BodyNoteForm(request.POST)

            character_formset = CharacterFormSet(request.POST, request.FILES, prefix='character_set')
            reference_commentators_formset = ReferenceCommentatorsFormSet(request.POST, request.FILES, prefix='reference_commentator_set')
            topography_formset = TopographyFormSet(request.POST, request.FILES, prefix='topography_set')
            episode_formset = FreeTextFormSet(request.POST, request.FILES, prefix='episode_set')
            theme_formset = FreeTextFormSet(request.POST, request.FILES, prefix='theme_set')
            image_formset = FreeTextFormSet(request.POST, request.FILES, prefix='image_set')
            stylistic_feature_formset = FreeTextFormSet(request.POST, request.FILES, prefix='stylistic_feature_set')
            theory_formset = FreeTextFormSet(request.POST, request.FILES, prefix='theory_set')


            # Get old reference from db
            citazioniList = nota['Nota']['Citazioni']
            
            # Create dict for new reference
            citazioneDict = {}

            # Get values present in all reference kind
            # * NoteForm
            # * ReferenceRelationshipForm
            # * ReferenceForm

            # Get the values of NoteForm
            text_fragment = note_form['text_fragment'].value()
            reference_kind = note_form['reference_kind'].value()

            # Set te values of NoteForm
            citazioneDict['FrammentoNota'] = text_fragment
            citazioneDict['NaturaRiferimento'] = reference_kind

            # Get the values of ReferenceRelationshipForm
            relationship_text_source = reference_relationship_form['relationship_text_source'].value()
            reference_commentator = reference_relationship_form['reference_commentator'].value()
            if(reference_commentator):
                    if(reference_commentators_formset.is_valid()):
                        referenceCommentatorList = []
                        for reference_commentators_form in reference_commentators_formset:
                            referenceCommentatorDict = {}
                            referenceCommentatorDict["Rapporto"] = reference_commentators_form.cleaned_data['relationship_reference_commentator']
                            referenceCommentatorDict["Commento"] = reference_commentators_form.cleaned_data['commentator_iri']
                            referenceCommentatorList.append(referenceCommentatorDict) 
                        citazioneDict['RapportoCommentoCommentatore'] = referenceCommentatorList




            # Set the values of ReferenceRelationshipForm
            if(relationship_text_source!=""):
                citazioneDict['RapportoSoggettoOggetto'] = relationship_text_source

            # Get the values of ReferenceForm
            cited_source = reference_form['cited_source_iri'].value()
            cited_author = reference_form['cited_author_iri'].value()
            theme_area = reference_form['theme_area_iri'].value()
            source_text = reference_form['source_text'].value()
            source_place = reference_form['source_place'].value()
            source_url = reference_form['source_url'].value()
            free_note = reference_form['free_note'].value()  

            # Create dict for info in ReferenceForm
            infoCitazioneDict = {}

            # Set the values of Reference form
            infoCitazioneDict['Fonte'] = cited_source
            infoCitazioneDict['Autore'] = cited_author
            infoCitazioneDict['Area'] = theme_area
            infoCitazioneDict['TestoFonte'] = source_text
            infoCitazioneDict['LuogoFonte'] = source_place
            infoCitazioneDict['UrlFonte'] = source_url
            infoCitazioneDict['NotaFonte'] = free_note

            # Separate action in base on reference kind
            # * Citazione
            # * Loci paralleli
            # * Supporto esterno

            # Citation type is used only by citations
            if(reference_kind=="CITAZIONE"):
                # Get the citation type
                citation_type = citation_form['citation_type'].value()
                # Set the citation type
                citazioneDict['TipoCitazione'] = citation_type

            # Reference content is used by citations and loci paralleli
            if(reference_kind=="CITAZIONE" or reference_kind=="LOCI PARALLELI"):
                # Create dict for Reference content
                ReferenceContentDict = {}
                # Character
                character = reference_content_form['character'].value()
                if(character):
                    if(character_formset.is_valid()):
                        print(character_formset)
                        characterList = []
                        for character_form in character_formset:
                            try:
                                characterList.append(character_form.cleaned_data['quote_character_iri'])
                            except:
                                characterList.append("unidentified")
                        ReferenceContentDict['Personaggi'] = characterList
    

                # Episode
                episode = reference_content_form['episode'].value()
                if(episode):
                    if(episode_formset.is_valid()):
                        episodeList = []
                        for episode_form in episode_formset:
                            try:
                                episodeList.append(episode_form.cleaned_data['free_text'])
                            except:
                                episodeList.append("unidentified")
                        ReferenceContentDict['Episodi'] = episodeList

                # Theme
                theme = reference_content_form['theme'].value()
                if(theme):
                    if(theme_formset.is_valid()):
                        themeList = []
                        for theme_form in theme_formset:
                            try:
                                themeList.append(theme_form.cleaned_data['free_text'])
                            except:
                                themeList.append("unidentified")
                        ReferenceContentDict['Motivi'] = themeList

                # Image
                image = reference_content_form['image'].value()
                if(image):
                    if(image_formset.is_valid()):
                        imageList = []
                        for image_form in image_formset:
                            try:
                                imageList.append(image_form.cleaned_data['free_text'])
                            except:
                                imageList.append("unidentified")
                        ReferenceContentDict['Immagini'] = imageList

                # Stylistic_feature
                stylistic_feature = reference_content_form['stylistic_feature'].value()
                if(stylistic_feature):
                    if(stylistic_feature_formset.is_valid()):
                        stylistic_featureList = []
                        for stylistic_feature_form in stylistic_feature_formset:
                            try:
                                stylistic_featureList.append(stylistic_feature_form.cleaned_data['free_text'])
                            except:
                                stylistic_featureList.append("unidentified")
                        ReferenceContentDict['Stilemi'] = stylistic_featureList

                # Topography
                topography = reference_content_form['topography'].value()
                if(topography):
                    if(topography_formset.is_valid()):
                        topographyList = []
                        for topography_form in topography_formset:
                            topographyList.append(topography_form.cleaned_data['quote_topography_iri'])
                        ReferenceContentDict['Topografie'] = topographyList
                    else:
                        ReferenceContentDict['Topografie'] = ["unidentified"]

                # Theory
                theory = reference_content_form['theory'].value()
                if(theory):
                    if(theory_formset.is_valid()):
                        theoryList = []
                        for theory_form in theory_formset:
                            try:
                                theoryList.append(theory_form.cleaned_data['free_text'])
                            except:
                                theoryList.append("unidentified")
                        ReferenceContentDict['Teorie'] = theoryList


                citazioneDict['ContenutoCitazione'] = ReferenceContentDict

            
            citazioneDict['InfoCitazione'] = infoCitazioneDict


            citazioniList.append(citazioneDict)
            nota['Nota']['Citazioni'] = citazioniList


            lastMod = time.time() # datetime.datetime.now()
            # date_time = lastMod.strftime("%Y-%m-%d, %H:%M:%S")
            nota['LastMod'] = lastMod

            # annotationDict['Stato'] = "doing"
            nota['Stato'] = "doing" #nota['Stato']


            #json = j.dumps(annotationDict)
            Annotation.objects.filter(pk=note_id).update(data=nota)
        
            extract = Annotation.objects.get(pk=note_id)

            json = extract.data
            nota = json # nota = j.loads(json)
            json_formatted_str = j.dumps(nota, indent=2)
            # check whether it's valid:
            if note_form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                context = {
                    'json': json_formatted_str,
                    'data' : nota,
                    'note_id' : note_id,
                    'comment_id' : comm_number,
                    'next_id' : next_id, 
                    'prev_id' : prev_id,  
                    'first_id' : first_id, 
                    'last_id' : last_id,
                    'dante_text_form' : dante_text_form,
                    'body_note_form' : body_note_form,
                    'note_form': note_form,  
                    'citation_form': citation_form, 
                    'reference_content_form': reference_content_form, 
                    'reference_relationship_form': reference_relationship_form, 
                    'reference_form': reference_form, 
                    'character_formset' : character_formset,  
                    'reference_commentators_formset' : reference_commentators_formset,
                    'topography_formset' : topography_formset,
                    'episode_formset' : episode_formset,
                    'theme_formset' : theme_formset,
                    'image_formset' : image_formset,
                    'stylistic_feature_formset' : stylistic_feature_formset,
                    'theory_formset' : theory_formset,
                    'inferno' : inferno,
                    'purgatorio' : purgatorio,
                    'paradiso' : paradiso,
                    'cookie' : cookie

                }
            
                end = time.time()
                print(end - start)
                if request.is_ajax():
                    return JsonResponse({'json': json_formatted_str, 'data' : nota})
                else:
                    return render(request, 'annotation/note.html', context)
                    
            else:
                print(form.errors)

        # if a GET (or any other method) we'll create a blank form
        else:
            note_form = NoteForm()
            citation_form = CitationForm()
            reference_content_form = ReferenceContentForm()
            reference_relationship_form = ReferenceRelationshipForm()
            reference_form = ReferenceForm()
            dante_text_form = DanteTextForm()
            body_note_form = BodyNoteForm()

            character_formset = CharacterFormSet(prefix='character_set')
            reference_commentators_formset = ReferenceCommentatorsFormSet(prefix='reference_commentator_set')
            topography_formset = TopographyFormSet(prefix='topography_set')
            episode_formset = FreeTextFormSet(prefix='episode_set')
            theme_formset = FreeTextFormSet(prefix='theme_set')
            image_formset = FreeTextFormSet(prefix='image_set')
            stylistic_feature_formset = FreeTextFormSet(prefix='stylistic_feature_set')
            theory_formset = FreeTextFormSet(prefix='theory_set')

            context = {
                'json': json_formatted_str,
                'data' : nota,
                'note_id' : note_id,
                'comment_id' : comm_number,
                'next_id' : next_id, 
                'prev_id' : prev_id,  
                'first_id' : first_id, 
                'last_id' : last_id,
                'dante_text_form' : dante_text_form,
                'body_note_form' : body_note_form,
                'note_form': note_form,  
                'citation_form': citation_form, 
                'reference_content_form': reference_content_form, 
                'reference_relationship_form': reference_relationship_form, 
                'reference_form': reference_form, 
                'character_formset' : character_formset,  
                'reference_commentators_formset' : reference_commentators_formset,
                'topography_formset' : topography_formset,  
                'episode_formset' : episode_formset,
                'theme_formset' : theme_formset,
                'image_formset' : image_formset,
                'stylistic_feature_formset' : stylistic_feature_formset,
                'theory_formset' : theory_formset,
                'inferno' : inferno,
                'purgatorio' : purgatorio,
                'paradiso' : paradiso,
                'cookie' : cookie
            }
            end = time.time()
            print(end - start)
            return render(request, 'annotation/note.html', context)
    else:
        return render(request, 'annotation/error.html')

# Cesare
# Controllare che la nota sia posseduta dall'owner
#@login_required
def delete_reference(request, commentary, note_id, cit_id):
    """[summary]

    [extended_summary]

    :param request: [description]
    :type request: [type]
    :param note_id: [description]
    :type note_id: [type]
    :param cit_id: [description]
    :type cit_id: [type]
    :return: [description]
    :rtype: [type]
    """
    json = "{}"
    #cesare 
    ustoken=request.session.get('gcube-token')
    myuser =  authenticate(ustoken)
    if myuser==None:
        raise Http404("Token not valid, access denied")
    #\cesare

    extract = Annotation.objects.get(pk=note_id)

    json = extract.data
    nota = json # nota = j.loads(json)
    del nota['Nota']['Citazioni'][cit_id]
    lastMod = time.time()
    nota['LastMod'] = lastMod 
    json_formatted_str = j.dumps(nota, indent=2)
    Annotation.objects.filter(pk=note_id).update(data=nota)
    context = {'json': json_formatted_str, 'data' : nota}
    if request.is_ajax():
       	return JsonResponse({'json': json_formatted_str, 'data' : nota})
    else:
        return render(request, 'annotation/note.html', context)

# Cesare
# Controllare che la nota sia posseduta dall'owner
#@login_required
# @xframe_options_exempt
def save_reference(request, commentary, note_id, cit_id):
    json = "{}"
     #cesare 
    ustoken=request.session.get('gcube-token')
    myuser =  authenticate(ustoken)
    if myuser==None:
        raise Http404("Token not valid, access denied")
    #\cesare
    
    # Initialize the formsets, specifying the form and formset we want to use.
    CharacterFormSet = formset_factory(CharacterForm)
    TopographyFormSet = formset_factory(TopographyForm)
    ReferenceCommentatorsFormSet = formset_factory(ReferenceCommentatorsForm)
    FreeTextFormSet = formset_factory(FreeTextForm) 

    extract = Annotation.objects.get(pk=note_id)

    json = extract.data
    nota = json # nota = j.loads(json)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        note_form = NoteForm(request.POST)
        citation_form = CitationForm(request.POST)
        reference_content_form = ReferenceContentForm(request.POST)
        reference_relationship_form = ReferenceRelationshipForm(request.POST)
        reference_form = ReferenceForm(request.POST)
        
        character_formset = CharacterFormSet(request.POST, request.FILES, prefix='character_set')
        reference_commentators_formset = ReferenceCommentatorsFormSet(request.POST, prefix='reference_commentator_set')
        topography_formset = TopographyFormSet(request.POST, prefix='topography_set')
        episode_formset = FreeTextFormSet(request.POST, request.FILES, prefix='episode_set')
        theme_formset = FreeTextFormSet(request.POST, request.FILES, prefix='theme_set')
        image_formset = FreeTextFormSet(request.POST, request.FILES, prefix='image_set')
        stylistic_feature_formset = FreeTextFormSet(request.POST, request.FILES, prefix='stylistic_feature_set')
        theory_formset = FreeTextFormSet(request.POST, request.FILES, prefix='theory_set')
        
        # Create dict for new reference
        citazioneDict = {}

        # Get values present in all reference kind
        # * NoteForm
        # * ReferenceRelationshipForm
        # * ReferenceForm

        # Get the values of NoteForm
        text_fragment = note_form['text_fragment'].value()
        reference_kind = note_form['reference_kind'].value()

        # Set te values of NoteForm
        citazioneDict['FrammentoNota'] = text_fragment
        citazioneDict['NaturaRiferimento'] = reference_kind

        # Get the values of ReferenceRelationshipForm
        relationship_text_source = reference_relationship_form['relationship_text_source'].value()
        reference_commentator = reference_relationship_form['reference_commentator'].value()
        if(reference_commentator):
                if(reference_commentators_formset.is_valid()):
                    referenceCommentatorList = []
                    for reference_commentators_form in reference_commentators_formset:
                        referenceCommentatorDict = {}
                        referenceCommentatorDict["Rapporto"] = reference_commentators_form.cleaned_data['relationship_reference_commentator']
                        referenceCommentatorDict["Commento"] = reference_commentators_form.cleaned_data['commentator_iri']
                        referenceCommentatorList.append(referenceCommentatorDict) 
                    citazioneDict['RapportoCommentoCommentatore'] = referenceCommentatorList




        # Set the values of ReferenceRelationshipForm
        citazioneDict['RapportoSoggettoOggetto'] = relationship_text_source
        # citazioneDict['RapportoRiferimentiCommentatori'] = reference_commentator

        # Get the values of ReferenceForm
        cited_source = reference_form['cited_source_iri'].value()
        cited_author = reference_form['cited_author_iri'].value()
        theme_area = reference_form['theme_area_iri'].value()
        source_text = reference_form['source_text'].value()
        source_place = reference_form['source_place'].value()
        source_url = reference_form['source_url'].value()
        free_note = reference_form['free_note'].value()  

        # Create dict for info in ReferenceForm
        infoCitazioneDict = {}

        # Set the values of Reference form
        infoCitazioneDict['Fonte'] = cited_source
        infoCitazioneDict['Autore'] = cited_author
        infoCitazioneDict['Area'] = theme_area
        infoCitazioneDict['TestoFonte'] = source_text
        infoCitazioneDict['LuogoFonte'] = source_place
        infoCitazioneDict['UrlFonte'] = source_url
        infoCitazioneDict['NotaFonte'] = free_note

        # Separate action in base on reference kind
        # * Citazione
        # * Loci paralleli
        # * Supporto esterno

        # Citation type is used only by citations
        if(reference_kind=="CITAZIONE"):
            # Get the citation type
            citation_type = citation_form['citation_type'].value()
            # Set the citation type
            citazioneDict['TipoCitazione'] = citation_type

        # Reference content is used by citations and loci paralleli
        if(reference_kind=="CITAZIONE" or reference_kind=="LOCI PARALLELI"):
            # Create dict for Reference content
            ReferenceContentDict = {}

            # Character
            character = reference_content_form['character'].value()
            if(character):
                if(character_formset.is_valid()):
                    # print(character_formset)
                    characterList = []
                    for character_form in character_formset:
                        try:
                            characterList.append(character_form.cleaned_data['quote_character_iri'])
                        except:
                            characterList.append("unidentified")
                    ReferenceContentDict['Personaggi'] = characterList


            # Episode
            episode = reference_content_form['episode'].value()
            if(episode):
                if(episode_formset.is_valid()):
                    episodeList = []
                    for episode_form in episode_formset:
                        try:
                            episodeList.append(episode_form.cleaned_data['free_text'])
                        except:
                            episodeList.append("unidentified")
                    ReferenceContentDict['Episodi'] = episodeList

            # Theme
            theme = reference_content_form['theme'].value()
            if(theme):
                if(theme_formset.is_valid()):
                    themeList = []
                    for theme_form in theme_formset:
                        try:
                            themeList.append(theme_form.cleaned_data['free_text'])
                        except:
                            themeList.append("unidentified")
                    ReferenceContentDict['Motivi'] = themeList

            # Image
            image = reference_content_form['image'].value()
            if(image):
                if(image_formset.is_valid()):
                    imageList = []
                    for image_form in image_formset:
                        try:
                            imageList.append(image_form.cleaned_data['free_text'])
                        except:
                            imageList.append("unidentified")
                    ReferenceContentDict['Immagini'] = imageList

            # Stylistic_feature
            stylistic_feature = reference_content_form['stylistic_feature'].value()
            if(stylistic_feature):
                if(stylistic_feature_formset.is_valid()):
                    stylistic_featureList = []
                    for stylistic_feature_form in stylistic_feature_formset:
                        try:
                            stylistic_featureList.append(stylistic_feature_form.cleaned_data['free_text'])
                        except:
                            stylistic_featureList.append("unidentified")
                    ReferenceContentDict['Stilemi'] = stylistic_featureList

            # Topography
            topography = reference_content_form['topography'].value()
            if(topography):
                if(topography_formset.is_valid()):
                    topographyList = []
                    for topography_form in topography_formset:
                        topographyList.append(topography_form.cleaned_data['quote_topography_iri'])
                    ReferenceContentDict['Topografie'] = topographyList
                else:
                    ReferenceContentDict['Topografie'] = ["unidentified"]

            # Theory
            theory = reference_content_form['theory'].value()
            if(theory):
                if(theory_formset.is_valid()):
                    theoryList = []
                    for theory_form in theory_formset:
                        try:
                            theoryList.append(theory_form.cleaned_data['free_text'])
                        except:
                            theoryList.append("unidentified")
                    ReferenceContentDict['Teorie'] = theoryList

            citazioneDict['ContenutoCitazione'] = ReferenceContentDict   

        
        citazioneDict['InfoCitazione'] = infoCitazioneDict

        
        nota['Nota']['Citazioni'][cit_id] = citazioneDict

        lastMod = time.time()
        nota['LastMod'] = lastMod

        json_formatted_str = j.dumps(nota, indent=2)
        Annotation.objects.filter(pk=note_id).update(data=nota)

        if note_form.is_valid():
            context = {'json': json_formatted_str, 'data' : nota}
            print(context)
            if request.is_ajax():
                return JsonResponse({'json': json_formatted_str, 'data' : nota})
            else:
                return render(request, 'annotation/note.html', context)

# Tree view cantiche
#@login_required
# @xframe_options_exempt
def cantiche_tree(request, note_id, cantica_canto):
    #cesare 
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare
    
    struttura = {}
    cantiche = ["Inferno", "Purgatorio", "Paradiso"]
    cantica_canto_array = cantica_canto.split("-")
    cantica = cantica_canto_array[0]
    canto = cantica_canto_array[1]
    extract = Annotation.objects.get(pk=note_id)
    nota = extract.data
    commento = nota["Nota"]["Commento"]["Id"]
    note_commento =  Annotation.objects.filter(
            data__Nota__OperaDante__Cantica=cantica,
            data__Nota__OperaDante__Canto=canto,
            data__Nota__Commento__Id=commento,
            ).order_by('id')
    note = [{'id': obj.id,
                'data': obj.data} for obj in note_commento]
    return JsonResponse(note, safe=False)


# Cesare
# Controllare che la nota sia posseduta dall'owner
#@login_required
# @xframe_options_exempt
def change_state(request, note_id):
    
     #cesare 
    ustoken=request.session.get('gcube-token')
    myuser =  authenticate(ustoken)
    if myuser==None:
        raise Http404("Token not valid, access denied")
    #\cesare
    
    if request.GET.get('state'):
        state = request.GET['state']
        extract = Annotation.objects.get(pk=note_id)
        json = extract.data
        nota = json
        nota["Stato"] = state

        lastMod = time.time() # datetime.datetime.now()
        # date_time = lastMod.strftime("%Y-%m-%d, %H:%M:%S")
        nota['LastMod'] = lastMod

        json_formatted_str = j.dumps(nota, indent=2)
        Annotation.objects.filter(pk=note_id).update(data=nota)
        context = {'json': json_formatted_str, 'data' : nota}
        return JsonResponse({'json': json_formatted_str, 'data' : nota})

#@login_required
# @xframe_options_exempt
def save_dante_text(request, note_id):
    #cesare
    #ustoken=request.session.get('gcube-token')
    #myuser =  authenticate(ustoken)
    #if myuser==None:
    #    raise Http404("Token not valid, access denied")
    #\cesare
    # if 'text' in request.GET:
    #     text = request.GET['text']
    #     extract = Annotation.objects.get(pk=note_id)
    #     json = extract.data
    #     nota = json
    #     nota["Nota"]["FrammentoDante"] = text

    #     lastMod = time.time() # datetime.datetime.now()
    #     # date_time = lastMod.strftime("%Y-%m-%d, %H:%M:%S")
    #     nota['LastMod'] = lastMod

    #     json_formatted_str = j.dumps(nota, indent=2)
    #     Annotation.objects.filter(pk=note_id).update(data=nota)
    #     context = {'json': json_formatted_str, 'data' : nota}
    #     return JsonResponse({'json': json_formatted_str, 'data' : nota})
    # return JsonResponse({'error': 'Parameters missing'})
    
    if request.method == 'POST':
        text = j.loads(request.body)
        extract = Annotation.objects.get(pk=note_id)
        json = extract.data
        nota = json
        nota["Nota"]["FrammentoDante"] = text

        lastMod = time.time() # datetime.datetime.now()
        # date_time = lastMod.strftime("%Y-%m-%d, %H:%M:%S")
        nota['LastMod'] = lastMod

        json_formatted_str = j.dumps(nota, indent=2)
        Annotation.objects.filter(pk=note_id).update(data=nota)
        context = {'json': json_formatted_str, 'data' : nota}
        return JsonResponse({'json': json_formatted_str, 'data' : nota})
    return JsonResponse({'error': 'Parameters missing'})

#@login_required
# @xframe_options_exempt
# TO DEPRECATE ------------------
def save_body_note(request, note_id):
    #cesare
    #ustoken=request.session.get('gcube-token')
    #myuser =  authenticate(ustoken)
    #if myuser==None:
    #    raise Http404("Token not valid, access denied")
    #\cesare

    if 'text' in request.GET:
        text = request.GET['text']
        extract = Annotation.objects.get(pk=note_id)
        json = extract.data
        nota = json
        nota["Nota"]["BodyNota"] = text

        lastMod = time.time() # datetime.datetime.now()
        # date_time = lastMod.strftime("%Y-%m-%d, %H:%M:%S")
        nota['LastMod'] = lastMod

        json_formatted_str = j.dumps(nota, indent=2)
        Annotation.objects.filter(pk=note_id).update(data=nota)
        context = {'json': json_formatted_str, 'data' : nota}
        return JsonResponse({'json': json_formatted_str, 'data' : nota})
    return JsonResponse({'error': 'Parameters missing'})


# Author autocomplete
# @login_required
@xframe_options_exempt
def author_autocomplete(request):
    
     #cesare 
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare
    
    if request.GET.get('q'):
        query = request.GET['q']
        matches = Author.objects.filter(data__name__istartswith=query)[:10]
    else:
        matches = Author.objects.all()[:10]
    
    dataDict = [{'id': obj.data['iri'],
                'text': obj.data['name']} for obj in matches]
    return JsonResponse(dataDict, safe=False)


# Source autocomplete
#@login_required
@xframe_options_exempt
def source_autocomplete(request):
    
     #cesare 
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare
    
    if request.GET.get('q'):
        query = request.GET['q']
        if '$$' in query:
                queryElements = query.split('$$')
                if len(queryElements) > 1:
                          matches = Source.objects.filter(data__author__in=[queryElements[0],MISSING_IRI],
                                    data__title__istartswith=queryElements[1])[:10]
                else:
                          matches = Source.objects.filter(data__author__in=[queryElements[0],MISSING_IRI])[:10]
        else:
                matches = Source.objects.filter(data__title__istartswith=query)[:10]
    else:
        matches = Source.objects.all()[:10]
    
    dataDict = [{'id': obj.data['iri'],
                'text': obj.data['title'],
                'author': obj.data['author']} for obj in matches]
    return JsonResponse(dataDict, safe=False)


# Area autocomplete
#@login_required
@xframe_options_exempt
def area_autocomplete(request):
    
     #cesare 
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare
    
    if request.GET.get('q'):
        query = request.GET['q']
        matches = Area.objects.filter(data__name__istartswith=query)[:10]
    else:
        matches = Area.objects.all()[:10]
    dataDict = [{'id': obj.data['iri'],
                'text': obj.data['name']} for obj in matches]
    return JsonResponse(dataDict, safe=False)

# Character autocomplete
#@login_required
@xframe_options_exempt
def character_autocomplete(request):
    
     #cesare 
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare
    
    
    if request.GET.get('q'):
        query = request.GET['q']
        matches = Character.objects.filter(data__name__istartswith=query)[:10]
    else:
        matches = Character.objects.all()[:10]
    dataDict = [{'id': obj.data['iri'],
                'text': obj.data['name']} for obj in matches]
    return JsonResponse(dataDict, safe=False)

# Place autocomplete
# @login_required
@xframe_options_exempt
def place_autocomplete(request):

    #cesare
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare

    if request.GET.get('q'):
        query = request.GET['q']
        matches = Place.objects.filter(data__name__istartswith=query)[:10]
    else:
        matches = Place.objects.all()[:10]
    dataDict = [{'id': obj.data['iri'],
                'text': obj.data['name']} for obj in matches]
    return JsonResponse(dataDict, safe=False)

# Commentary autocomplete
#@login_required
@xframe_options_exempt
def commentary_autocomplete(request):

    #cesare
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare

    if request.GET.get('q'):
        query = request.GET['q']
        matches = Commentary.objects.filter(data__name__icontains=query)[:10]
    else:
        matches = Commentary.objects.all()[:10]
    dataDict = [{'id': obj.data['iri'],
                'text': obj.data['name']} for obj in matches]
    return JsonResponse(dataDict, safe=False)


# Make autocomplete response
def make_autocomplete_response(obj):
    # Response contains data field of object
    response = obj.data

    # Autocomplete expects these two fields
    response['id'] = obj.data['iri']
    
    response['text'] = obj.data['name'] if 'name' in obj.data else obj.data['title']

    # Type is needed to distinguish entities
    response['type'] = obj.__class__.__name__.lower()

    return response


# View for IRI resolution
#@login_required
@xframe_options_exempt
def entity_from_iri(request):
    #cesare
    # ustoken=request.session.get('gcube-token')
    # myuser =  authenticate(ustoken)
    # if myuser==None:
    #     raise Http404("Token not valid, access denied")
    #\cesare

    if request.GET.get('iri'):
        iri = request.GET['iri']
        obj = None

        # TODO: we could get the type from the IRI to make a more limited query
        for model in [Area, Author, Source, Character, Place, Commentary]:
            try:
                obj = model.objects.get(data__iri=iri)
            except model.DoesNotExist:
                pass
        if obj:
            response = make_autocomplete_response(obj)

            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'IRI not found in database'})
    return JsonResponse({'error': 'Parameters missing'})


# Insert author into DB
def insert_wd_author(iri, results, username):
    data = {'iri': iri, 'name': results[0]['itemLabel']['value']}
    data['user'] = username # to distinguish user-defined sources
    obj = Author(data=data)
    obj.save()
    return obj

# Insert source into DB
def insert_wd_source(iri, results, username):
    author_iri = MISSING_IRI # default: missing
    if 'author' in results[0]:
        author_iri = results[0]['author']['value']
        try:
            author = Author.objects.get(data__iri=author_iri)
        except Author.DoesNotExist:
            make_author_query(author_iri, username)
    data = {'iri': iri, 'title': results[0]['itemLabel']['value'], 'author': author_iri}
    data['user'] = username # to distinguish user-defined sources
    obj = Source(data=data)
    obj.save()
    return obj

# Insert character into DB
def insert_wd_character(iri, results, username):
    data = {'iri': iri, 'name': results[0]['itemLabel']['value']}
    data['user'] = username # to distinguish user-defined sources
    obj = Character(data=data)
    obj.save()
    return obj

# Insert place into DB
def insert_wd_place(iri, results, username):
    data = {'iri': iri, 'name': results[0]['itemLabel']['value']}
    data['user'] = username # to distinguish user-defined sources
    obj = Place(data=data)
    obj.save()
    return obj

# Make Wikidata request
def wikidata_request(query):
    # Request URL
    request_url = f'{WD_SPARQL_URL}{urllib.parse.quote(query)}&format=json'

    # Make request
    with urllib.request.urlopen(request_url) as response:
        results = j.loads(response.read())['results']['bindings']
        return results
    return None

# Make Wikidata query for author
def make_author_query(iri, username):
    qid = iri.split('/entity/')[1] # Wikidata ID starting with Q

    # Wikidata query
    wd_query = f'\nSELECT ?item ?itemLabel \n\
                WHERE {{ hint:Query hint:optimizer "None". \n\
                    BIND (wd:{qid} AS ?item) \n\
                    SERVICE wikibase:label {{ \n\
                        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],it,la,en" . \n\
                    }} \n\
                }}'

    # TODO import aliases for author
    # TODO import all works created by the author

    # Run Wikidata query
    query_results = wikidata_request(wd_query)

    if query_results:
        new_obj = insert_wd_author(iri, query_results, username)

        if new_obj:
            response = make_autocomplete_response(new_obj)

            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'Error while adding to DB'})
    return JsonResponse({'error': 'Error in Wikidata query'})

# Make Wikidata query for source
def make_source_query(iri, username):
    qid = iri.split('/entity/')[1] # Wikidata ID starting with Q

    # Wikidata query
    wd_query = f'\nSELECT ?item ?itemLabel ?author ?authorLabel \n\
                WHERE {{ hint:Query hint:optimizer "None". \n\
                    BIND (wd:{qid} AS ?item) \n\
                    OPTIONAL {{?item wdt:P50 ?author}} \n\
                    SERVICE wikibase:label {{ \n\
                        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],la,it,en" . \n\
                    }} \n\
                }}'

    # TODO import aliases for source

    # Run Wikidata query
    query_results = wikidata_request(wd_query)

    if query_results:
        new_obj = insert_wd_source(iri, query_results, username)

        if new_obj:
            response = make_autocomplete_response(new_obj)

            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'Error while adding to DB'})
    return JsonResponse({'error': 'Error in Wikidata query'})

# Make Wikidata query for character
def make_character_query(iri, username):
    qid = iri.split('/entity/')[1] # Wikidata ID starting with Q

    # Wikidata query
    wd_query = f'\nSELECT ?item ?itemLabel \n\
                WHERE {{ hint:Query hint:optimizer "None". \n\
                    BIND (wd:{qid} AS ?item) \n\
                    SERVICE wikibase:label {{ \n\
                        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],it,la,en" . \n\
                    }} \n\
                }}'

    # TODO import aliases for character

    # Run Wikidata query
    query_results = wikidata_request(wd_query)

    if query_results:
        new_obj = insert_wd_character(iri, query_results, username)

        if new_obj:
            response = make_autocomplete_response(new_obj)

            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'Error while adding to DB'})
    return JsonResponse({'error': 'Error in Wikidata query'})

# Make Wikidata query for place
def make_place_query(iri, username):
    qid = iri.split('/entity/')[1] # Wikidata ID starting with Q

    # Wikidata query
    wd_query = f'\nSELECT ?item ?itemLabel \n\
                WHERE {{ hint:Query hint:optimizer "None". \n\
                    BIND (wd:{qid} AS ?item) \n\
                    SERVICE wikibase:label {{ \n\
                        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],it,la,en" . \n\
                    }} \n\
                }}'

    # TODO import aliases for place

    # Run Wikidata query
    query_results = wikidata_request(wd_query)

    if query_results:
        new_obj = insert_wd_place(iri, query_results, username)

        if new_obj:
            response = make_autocomplete_response(new_obj)

            return JsonResponse(response)
        else:
            return JsonResponse({'error': 'Error while adding to DB'})
    return JsonResponse({'error': 'Error in Wikidata query'})

# Import Wikidata author
@xframe_options_exempt
def import_wikidata_author(request):
    #cesare
    #ustoken=request.session.get('gcube-token')
    #myuser =  authenticate(ustoken)
    #if myuser==None:
    #    raise Http404("Token not valid, access denied")
    #\cesare

    iri = request.GET.get('iri')
    if iri:
        try:
            obj = Author.objects.get(data__iri=iri)
        except Author.DoesNotExist:
            # If this is a Wikidata IRI...
            if iri.startswith(WD_ENTITY_URL):
                return make_author_query(iri, request.user.pk)
            else:
                return JsonResponse({'error': 'IRI is not from Wikidata'})
        else:
            response = make_autocomplete_response(obj)

            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Import Wikidata source
@xframe_options_exempt
def import_wikidata_source(request):
    #cesare
    #ustoken=request.session.get('gcube-token')
    #myuser =  authenticate(ustoken)
    #if myuser==None:
    #    raise Http404("Token not valid, access denied")
    #\cesare

    iri = request.GET.get('iri')
    if iri:
        try:
            obj = Source.objects.get(data__iri=iri)
        except Source.DoesNotExist:
            # If this is a Wikidata IRI...
            if iri.startswith(WD_ENTITY_URL):
                return make_source_query(iri, request.user.pk)
            else:
                return JsonResponse({'error': 'IRI is not from Wikidata'})
        else:
            response = make_autocomplete_response(obj)

            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Import Wikidata character
@xframe_options_exempt
def import_wikidata_character(request):
    #cesare
    #ustoken=request.session.get('gcube-token')
    #myuser =  authenticate(ustoken)
    #if myuser==None:
    #    raise Http404("Token not valid, access denied")
    #\cesare

    iri = request.GET.get('iri')
    if iri:
        try:
            obj = Character.objects.get(data__iri=iri)
        except Character.DoesNotExist:
            # If this is a Wikidata IRI...
            if iri.startswith(WD_ENTITY_URL):
                return make_character_query(iri, request.user.pk)
            else:
                return JsonResponse({'error': 'IRI is not from Wikidata'})
        else:
            response = make_autocomplete_response(obj)

            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Import Wikidata place
@xframe_options_exempt
def import_wikidata_place(request):
    #cesare
    #ustoken=request.session.get('gcube-token')
    #myuser =  authenticate(ustoken)
    #if myuser==None:
    #    raise Http404("Token not valid, access denied")
    #\cesare

    iri = request.GET.get('iri')
    if iri:
        try:
            obj = Place.objects.get(data__iri=iri)
        except Place.DoesNotExist:
            # If this is a Wikidata IRI...
            if iri.startswith(WD_ENTITY_URL):
                return make_place_query(iri, request.user.pk)
            else:
                return JsonResponse({'error': 'IRI is not from Wikidata'})
        else:
            response = make_autocomplete_response(obj)

            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Add user-defined author
@xframe_options_exempt
def add_new_author(request):
    name = request.GET.get('name')
    desc = request.GET.get('desc')
    if name:
        iri = f'{HDN_BASE_IRI}author/{slugify(name)}'
        try:
            obj = Author.objects.get(data__iri=iri)
        except Author.DoesNotExist:
            data = {'iri': iri, 'name': name, 'description': desc}
            data['user'] = request.user.pk # to distinguish user-defined authors
            obj = Author(data=data)
            obj.save()
        finally:
            response = make_autocomplete_response(obj)
            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Add user-defined source
@xframe_options_exempt
def add_new_source(request):
    title = request.GET.get('title')
    desc = request.GET.get('desc')
    if title:
        iri = f'{HDN_BASE_IRI}source/{slugify(title)}'
        try:
            obj = Source.objects.get(data__iri=iri)
        except Source.DoesNotExist:
            data = {'iri': iri, 'title': title, 'description': desc}
            data['author'] = MISSING_IRI # TODO let user add author (and area?)
            data['user'] = request.user.pk # to distinguish user-defined sources
            obj = Source(data=data)
            obj.save()
        finally:
            response = make_autocomplete_response(obj)
            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Add user-defined source
@xframe_options_exempt
def add_new_character(request):
    name = request.GET.get('name')
    desc = request.GET.get('desc')
    if name:
        iri = f'{HDN_BASE_IRI}character/{slugify(name)}'
        try:
            obj = Character.objects.get(data__iri=iri)
        except Character.DoesNotExist:
            data = {'iri': iri, 'name': name, 'description': desc}
            data['user'] = request.user.pk # to distinguish user-defined characters
            obj = Character(data=data)
            obj.save()
        finally:
            response = make_autocomplete_response(obj)
            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Add user-defined place
@xframe_options_exempt
def add_new_place(request):
    name = request.GET.get('name')
    desc = request.GET.get('desc')
    if name:
        iri = f'{HDN_BASE_IRI}place/{slugify(name)}'
        try:
            obj = Place.objects.get(data__iri=iri)
        except Place.DoesNotExist:
            data = {'iri': iri, 'name': name, 'description': desc}
            data['user'] = request.user.pk # to distinguish user-defined places
            obj = Place(data=data)
            obj.save()
        finally:
            response = make_autocomplete_response(obj)
            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Add user-defined commentary
@xframe_options_exempt
def add_new_commentary(request):
    name = request.GET.get('name')
    year = request.GET.get('year')
    if name and year:
        name_year = f'{name.strip()} {year.strip()}'
        iri = f'{HDN_BASE_IRI}commentary/{slugify(name_year)}'
        try:
            obj = Commentary.objects.get(data__iri=iri)
        except Commentary.DoesNotExist:
            data = {'iri': iri, 'name': name_year, 'owner': 'not.assigned'}
            data['user'] = request.user.pk # to distinguish user-defined commentaries
            obj = Commentary(data=data)
            obj.save()
        finally:
            response = make_autocomplete_response(obj)
            return JsonResponse(response)
    return JsonResponse({'error': 'Parameters missing'})

# Authentication view (for testing)
@xframe_options_exempt
def auth(request):
    STYLE = "\"font-size: 1.5em; margin: 0 6% 0 6%; line-height: 150%\""

    # Fake user Andrea Rossi

    def color(text, color):
        return f'<span style="color: {color};">{text}</span>'

    response_strings = []

    try:
        user = request.GET['id']
        token = request.GET['gcube-token']
    except MultiValueDictKeyError:
        raise Http404("Username or token not provided")

    d4url = f'https://api.d4science.org/rest/2/people/profile?gcube-token={token}'

    if not user or not token:
        raise Http404("Username or token not provided")

    response_strings.append(f"<br>User is: <b>{user}</b>")

    try:
        u = User.objects.get(username=user)
    except:
        response_strings.append(color(f'User <b>{user}</b> does not exist in DB<br>', 'red'))
    else:
        response_strings.append(color(f'User <b>{user}</b> exists in DB<br>', 'green'))
        if u.is_superuser:
            response_strings.append(f'• Is superuser')
      #  if u.user_permissions.all():
      #      for permission in u.user_permissions.all():
      #          response_strings.append(f'• Can edit: Commentary {permission.name}')
      #  else:
      #      response_strings.append(f'• Has no specific permissions')
      #      response.append(f'• Authorization denied')
      #      return False

    try:
        with urllib.request.urlopen(d4url) as response:
            d4json = j.loads(response.read())

        if 'success' in d4json and d4json['success'] is True:
            if d4json['result']['username'] == user:
                response_strings.append(color(f'<br>User <b>{user}</b> exists in D4Science<br>', 'green'))
                for key in d4json['result']:
                    response_strings.append(f'• {key}: {d4json["result"][key]}')
            else:
                response_strings.append(color(f'<br>Token exists in D4Science but username does not match (<b>{d4json["result"]["username"]}</b>)<br>', 'red'))
        else:
            response_strings.append(color(f'<br>User <b>{user}</b> does not exist in D4Science<br>', 'red'))

    except HTTPError:
        response_strings.append(color(f'<br>Token is wrong<br>', 'red'))

    return HttpResponse(f'<p style={STYLE}>{"<br>".join(response_strings)}')

@xframe_options_exempt
def getusers(request):
    print ('test')
    STYLE = "\"font-size: 1.5em; margin: 0 6% 0 6%; line-height: 150%\""
    
    def color(text, color):
        return f'<span style="color: {color};">{text}</span>'

    response_strings = []

    try:
        user = request.GET['id']
        token = request.GET['gcube-token']
    except MultiValueDictKeyError:
        raise Http404("Username or token not provided")
    
    d4url = f'https://api.d4science.org/rest/2/users/get-all-fullnames-and-usernames?gcube-token={token}'
    
    #d4url = f'https://api.d4science.org/rest/2/users/get-all-usernames?gcube-token={token}'


    if not user or not token:
        raise Http404("Username or token not provided")
    
    response_strings.append(f"<br>Provo...<b>{user}</b>")
    
    try:
        with urllib.request.urlopen(d4url) as response:
            d4json = j.loads(response.read())

        if 'success' in d4json and d4json['success'] is True:
            print (d4json['result'])
            for key in d4json['result']:
                response_strings.append(f'• {key}: {d4json["result"][key]}')
                try:
                    u = User.objects.get(username=key)
                except:
                    response_strings.append(color(f'User <b>{key}</b> does not exist in DB<br>', 'red'))
        else:
            response_strings.append(color(f'<br>User <b>{user}</b> error in calling D4Science API<br>', 'red'))

    except HTTPError:
        response_strings.append(color(f'<br>Token is wrong<br>', 'red'))
        
    return HttpResponse(f'<p style={STYLE}>{"<br>".join(response_strings)}')
    
