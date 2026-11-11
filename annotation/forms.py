"""
| **Project**: HDN
| **Package**: Backend
| **Title**: Forms in Django
| **File**: forms.py
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

2020-08-20 Nicolo' Pratelli
    * Created classes BaseCharacterFormSet and CharacterForm

2020-09-16 Nicolo' Pratelli
    * Created classes BaseEpisodeFormSet and EpisodeForm

2020-09-17 Nicolo' Pratelli
    * Added class BaseFreeTextFormSet and FreeTexctForm
    * Renamed all variable names in english and completed documentation

2020-10-20 Nicolo' Pratelli
    * Deleted class BaseEpisodeFormSet 
    * Deleted class BaseCharacterFormSet
    * Deleted class BaseCharacterFormSet 
    * Deleted class BaseFreeTextFormSet


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

from django import forms
from django.forms.formsets import BaseFormSet
from docopt import docopt


TIPO_CITAZIONE =( 
    ("CONCORDANZA STRINGENTE", "Concordanza stringente"), 
    ("CITAZIONE ESPLICITA", "Citazione esplicita"), 
    ("CONCORDANZA GENERICA", "Concordanza generica"), 
)
"""
Type of reference

Type of reference can be:

* **strict**, if the reference is indicated by a scholar, and refers to a specific work as in ‘SIMANUCA: it is the bread of the angels, themannaas called in the Old Testament (Ps. 77,25 Panem angelorum manducavit homo)’;
* **explicit**, if the reference is explicitly made by Dante, as in ‘As the Philosopher says at the beginning of the First Philosophy’, where the Philosopher is Aristotle and the First Philosophy is Metaphysics;
* **generic**, if the reference is indicated by a scholar, and refers to a concept (e.g. ‘Medievalcomments to Aristotle’s works’).

An internal reference cannot be generic. While it can be explicit or stringent.
"""


NATURA_RIFERIMENTO = (
    ("", "---------"),
    ("CITAZIONE", "Citazione"),
    ("LOCI PARALLELI", "Loci paralleli"),
    ("SUPPORTO ESTERNO", "Supporto esterno"),
)
"""
Reference kind

We call Reference the most general type of reference to another text or tradition for the purpose of exegesis. 
A reference is expressed in Italian by a statement such as:

* Dice A che la conoscenza su B si può arricchire grazie a C     

where is it:

* A is a fragment of text that asserts the reference and is therefore called the "source" of the reference; the source typically belongs to a commentary;
* B is a fragment of text that is clarified by the reference and is therefore called the "subject" of the reference; in our case, the subject belongs to a Dante's work;
* C is the object of the reference.

Within the category of references, we find three distinct sub-categories: external supports, loci paralleli and citations.

The most specific case of reference, and the category at the center of our ontology, is the **Citation**: 
the relationship between the text-subject and the text-object, as established by the source, is not merely explanatory, 
but implies a relationship of derivation. A Citation is expressed in Italian by a sentence like:

* Dice A che B cita C (= Dice A che la conoscenza su B si può arricchire grazie a C perché B cita C, e dunque per capire B dobbiamo riconoscere questa Citation)

The loci paralleli are the cases in which the source identifies in an object-text an idea, a character, 
a style that are used in a similar way to the subject-text, and which therefore clarify the subject-text, 
without implying that there is derivation (there can be simple polygenesis). A commentary generally puts 
forward a parallel place for identification or explanatory purposes.

* Dice A che la conoscenza su B si può arricchire grazie a C perché B e C sono simili

External supports are the cases in which the source identifies an object-text that serves to support 
its interpretation of the subject-text. A commentary cites External Support for demonstration purposes, 
for example to argue that the author of the subject-text may or may not know a certain text.

* Dice A che la conoscenza su B si può arricchire grazie a C perché C sostiene l’ipotesi interpretativa di A a proposito di B    

"""


RAPPORTO_TESTO_FONTE = (
    ("", "---------"),
    ("CONFERMA", "Conferma"),
    ("CONTRADDICE", "Contraddice"),
    ("ESTENDE", "Estende"),
)
"""
Taking up CiTO, we will consider the following reports:

* Palinodia/contradiction
* Extension/reworking
* Confirmation/homology 
"""


"""
Define the formsets for Personaggio (Character), Episodio (Episode), Topografia (Topography) and plain text for
the other fields of Natura del riferimento. Then we define formset of Riferimenti
ad altri commentatori.
"""

class CharacterForm(forms.Form):
    """Form for individual character

    The character formset defines a form that can iterate multiple characters in a single citation consisting of a 
    text field with auto-completion for the character name and a text field for the character's iris, automatically 
    completed by drawing the iris associated with that character from the db.
    """
    # character mentioned by Dante to a specific source
    quote_character = forms.CharField(required=False, max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "autocomplete",
                "autocomplete" : "off",
                "data-url": "../../character",
                "data-toggle": "popover",
                "data-trigger": "focus",
                "data-noresults-text": "Nessun risultato",
                "title": "Personaggio citato",
                "data-content": "Seleziona il personaggio citato. Inserisci i primi caratteri del \
                                personaggio per filtrare i risultati. Se non trovi \
                                il personaggio nella lista, <a href='#' class='add-character-btn'>clicca qui</a> \
                                per aggiungerne uno nuovo."
            }))
    # IRI of character mentioned by Dante to a specific source
    quote_character_iri = forms.CharField(required=False, widget=forms.HiddenInput())


class TopographyForm(forms.Form):
    """Form for individual topography

    The topography formset defines a form that can iterate multiple topographies in a single citation consisting of
    a text field with auto-completion for the topography name and a text field for the topography's iris, automatically
    completed by drawing the iris associated with that topography from the db.
    """
    # behind Dante's mention of a place a literary memory acts
    quote_topography = forms.CharField(required=False, max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "autocomplete",
                "autocomplete" : "off",
                "data-url": "../../place",
                "data-toggle": "popover",
                "data-trigger": "focus",
                "data-noresults-text": "Nessun risultato",
                "title": "Luogo citato",
                "data-content": "Seleziona il luogo citato. Inserisci i primi caratteri \
                                del luogo per filtrare i risultati. Se non trovi \
                                il luogo nella lista, <a href='#' class='add-place-btn'>clicca qui</a> \
                                per aggiungerne uno nuovo."
            }))
    # IRI of that place
    quote_topography_iri = forms.CharField(required=False, widget=forms.HiddenInput())


"""

"""
class ReferenceCommentatorsForm(forms.Form):
    """Form for individual relation between reference and commentator

    Reference to another commentators formset defines a form that can iterate multiple reference to another commentator 
    in a single citation consisting of a select field (Palinodia/contradiction, Extension/reworking, Confirmation/homology); 
    a text field with auto-completion for the commentator name and a text field for the commentator's iris, 
    automatically completed by drawing the iris associated with that character from the db.                    
    """
    # the relationship between a reference and commentator
    relationship_reference_commentator = forms.ChoiceField(choices=RAPPORTO_TESTO_FONTE) # is the same choices of relationship between text and source
    # the name of commentator
    commentator = forms.CharField(required=False, max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "autocomplete",
                "autocomplete" : "off",
                "data-url": "../../commentary", # Cambiare il l'url con la view che estrae il commentatori (o i commenti)
                "data-toggle": "popover",
                "data-trigger": "focus",
                "data-noresults-text": "Nessun risultato",
                "title": "Commento citato",
                "data-content": "Seleziona il commento citato. Inserisci i primi caratteri del \
                                nome del commentatore per filtrare i risultati. Se non trovi \
                                il commento nella lista, <a href='#' class='add-comm-btn'>clicca qui</a> \
                                per aggiungerne uno nuovo."
            }))
    # IRI of commentator
    commentator_iri = forms.CharField(required=False, widget=forms.HiddenInput())

"""

"""
class FreeTextForm(forms.Form):
    """Form for individual relation between reference and commentator

    FreeTextForm is implemented for all contents of citation that not necessarily have an IRI.
    It is important that there are no repetitions. We match the corrects corrispondations between fields and db in views.py and in app.js. 
    """
    # a free text that contains a string that identify the content of citation
    free_text = forms.CharField(required=False, max_length=100)

class CitationForm(forms.Form):
    """Form for the citation property    
    """
    # type of refernce (generic, strict, explicit)
    citation_type = forms.ChoiceField(label="Tipo citazione", choices=TIPO_CITAZIONE)

class ReferenceContentForm(forms.Form):
    """Form for the content of reference

    The content of reference is characterized according to a two-level subdivision. 
    The first level is the one proposed by Gabriella Albanese as a typology of Dante's exegesis, 
    while the second level includes the categories proposed by Gaia.

    1. Textual correspondences (explicit and/or implicit references to textual places by linguistic and stylistic coincidence: lexicon, morphology, syntax etc.). These are further divided into:
        * Immagine (image) the commentator identifies an image present in a source as a precedent for a description or conceptualization of Dante
        * Stilema (stylistic feature) the commentator identifies a linguistic and/or rhetorical precedent for a Dante expression

    2. Thematic correspondences (explicit and/or implicit references to textual places by thematic coincidence: places, characters, events etc.). These are further divided into:
        * Personaggio (character) the commentator links a character mentioned by Dante to a specific source
        * Episodio (episode) the commentator identifies a literary episode at the basis of a Dante reference
        * Topografia (topography) the commentator believes that behind Dante's mention of a place a literary memory acts

    3. Conceptual correspondences (explicit and / or implicit references to textual places by conceptual coincidence: hypotheses, theses, theories, opinions etc.). These are further divided into:
        * Motivo (theme) the commentator identifies in a precise source the precedent for the development of a Dante theme
        * Teoria (theory) the commentator identifies a theoretical passage at the basis of a passage from Dante's discourse
               
    """
    # the commentator links a character mentioned by Dante to a specific source
    character = forms.BooleanField(label="Personaggio", required=False, widget=forms.CheckboxInput())
    # the commentator identifies a literary episode at the basis of a Dante reference
    episode = forms.BooleanField(label="Episodio", required=False, widget=forms.CheckboxInput())
    # the commentator identifies in a precise source the precedent for the development of a Dante theme
    theme = forms.BooleanField(label="Motivo", required=False, widget=forms.CheckboxInput())
    # the commentator identifies an image present in a source as a precedent for a description or conceptualization of Dante
    image = forms.BooleanField(label="Immagine", required=False, widget=forms.CheckboxInput())
    # the commentator identifies a linguistic and/or rhetorical precedent for a Dante expression
    stylistic_feature = forms.BooleanField(label="Stilema", required=False, widget=forms.CheckboxInput())
    # the commentator believes that behind Dante's mention of a place a literary memory acts 
    topography = forms.BooleanField(label="Topografia", required=False, widget=forms.CheckboxInput())
    # the commentator identifies a theoretical passage at the basis of a passage from Dante's discourse
    theory = forms.BooleanField(label="Teoria", required=False, widget=forms.CheckboxInput())

    # Nel vecchio sistema era configurato come un MultipleChoiceField, in cui si prendevano i campi come choices da CONTENUTO_RIFERIMENTO
    # contenuto_riferimento = forms.MultipleChoiceField(label="Contenuto del riferimento", choices=CONTENUTO_RIFERIMENTO, widget=forms.CheckboxSelectMultiple())
    


class NoteForm(forms.Form):
    """Note Form

    This class contains the general form fields, that is the kind of the reference and the fragment of the note, common to all the references.
    """
    # text fragment of the note
    text_fragment = forms.CharField(label="Frammento nota*", required=False, widget=forms.Textarea(
        attrs={
            'rows': 5,
            'class':'tiny-mce',
        }))
    # kind of reference
    reference_kind = forms.ChoiceField(label="Natura del riferimento*", choices=NATURA_RIFERIMENTO)


class ReferenceRelationshipForm(forms.Form):
    """Reference relationship form
    
    This class contains the relationships between text and source and relationship between text and other commentator         
    """
    # relationship between subject and object
    relationship_text_source = forms.ChoiceField(label="Rapporto testo fonte", required=False, choices=RAPPORTO_TESTO_FONTE)
    # reference to other citation 
    reference_commentator = forms.ChoiceField(label="Riferimenti ad altri commentatori", required=False, widget=forms.CheckboxInput())

class ReferenceForm(forms.Form):  
    """ Reference form

    This class contain the information about reference like name, author, theme area, text and url of source (and respective iris) 
    and a free note by the author of the annotation    
    """
    # title of cited source
    cited_source = forms.CharField(label="Fonte citata", required=False, max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "autocomplete",
                "autocomplete" : "off",
                "data-url": "../../source",
                "data-toggle": "popover",
                "data-trigger": "focus",
                "data-noresults-text": "Nessun risultato",
                "title": "Fonte citata",
                "data-content": "Seleziona la fonte citata. Inserisci i primi caratteri del \
                                titolo della fonte per filtrare i risultati. Se non trovi \
                                la fonte nella lista, <a href='#' class='add-source-btn'>clicca qui</a> \
                                per aggiungerne una nuova."
            }))
    # cited source iri
    cited_source_iri = forms.CharField(required=False, widget=forms.HiddenInput())
    # author of the cited source
    cited_author = forms.CharField(label="Autore citato", required=False, max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "autocomplete",
                "autocomplete" : "off",
                "data-url": "../../author",
                "data-toggle": "popover",
                "data-trigger": "focus",
                "data-noresults-text": "Nessun risultato",
                "title": "Autore citato",
                "data-content": "Seleziona l'autore citato. Inserisci i primi caratteri del \
                                nome dell'autore per filtrare i risultati. Se non trovi \
                                l'autore nella lista, <a href='#' class='add-author-btn'>clicca qui</a> \
                                per aggiungerne uno nuovo."
            }))
    # iri of author of the cited source
    cited_author_iri = forms.CharField(required=False, widget=forms.HiddenInput())
    # theme area of the cited source
    theme_area = forms.CharField(label='Area tematica', required=False, max_length=100, widget=forms.TextInput(
        attrs={
            "class": "autocomplete",
            "autocomplete" : "off",
            "data-url": "../../area",
            "data-toggle": "popover",
            "data-trigger": "focus",
            "data-noresults-text": "Nessun risultato",
            "title": "Area tematica",
            "data-content": "Seleziona l'area tematica. Inserisci i primi caratteri del \
                            nome dell'area per filtrare i risultati."
        }))
    # iri of theme area of the cited source
    theme_area_iri = forms.CharField(required=False, widget=forms.HiddenInput())
    # text of cited source
    source_text = forms.CharField(label="Testo della fonte", required=False, widget=forms.Textarea(
        attrs={
            'rows': 3,
        }))
    # Place where the source is
    source_place = forms.CharField(label="Luogo della fonte", required=False, widget=forms.Textarea(
        attrs={
            'rows': 1,
        }))
    # url of cited source
    source_url = forms.URLField(label="Link alla fonte", required=False)
    # free annotator note 
    free_note = forms.CharField(label="Note", required=False, widget=forms.Textarea(
        attrs={
            'rows': 3,
        }))

class DanteTextForm(forms.Form):
    """Dante text Form

    This class contains the text form field that permit to user to insert the text of commedia when text is missing
    """
    # text fragment of the note
    dante_text = forms.CharField(label="Testo dantesco", widget=forms.Textarea(
        attrs={
            'rows': 2,
        }))

class BodyNoteForm(forms.Form):
    """Body note Form

    This class contains the text form field that permit to user to insert the body of the note if is wrong or empty
    """
    # text fragment of the note
    body_note = forms.CharField(label="Corpo della nota", widget=forms.Textarea(
        attrs={
            'rows': 10,
        }))

