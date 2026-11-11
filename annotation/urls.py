from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # index view
    path('', views.get_commentaries, name='index'),

    # first note of commentary
    path('<int:commentary>/', views.get_last_note, name='first_note'),

    # note views
    path('<int:commentary>/<int:note_id>/', views.get_note, name='note'),
    path('<int:commentary>/<int:note_id>/<int:cookie>', views.get_note, name='note'),

    # citation views
    path('<int:commentary>/<int:note_id>/delete/<int:cit_id>/', views.delete_reference, name='delete_reference'),
    path('<int:commentary>/<int:note_id>/save/<int:cit_id>/', views.save_reference, name='save_reference'),

    # autocomplete views
    path('author', views.author_autocomplete, name='author_autocomplete'),
    path('source', views.source_autocomplete, name='source_autocomplete'),
    path('area', views.area_autocomplete, name='area_autocomplete'),
    path('character', views.character_autocomplete, name='character_autocomplete'),
    path('place', views.place_autocomplete, name='place_autocomplete'),
    path('commentary', views.commentary_autocomplete, name='commentary_autocomplete'),

    # entity from IRI
    path('entity', views.entity_from_iri, name='entity_from_iri'),

    # import from Wikidata
    path('import-author', views.import_wikidata_author, name='import_wikidata_author'),
    path('import-source', views.import_wikidata_source, name='import_wikidata_source'),
    path('import-character', views.import_wikidata_character, name='import_wikidata_character'),
    path('import-place', views.import_wikidata_place, name='import_wikidata_place'),

    # add user-defined resources
    path('add-author', views.add_new_author, name='add_new_author'),
    path('add-source', views.add_new_source, name='add_new_source'),
    path('add-character', views.add_new_character, name='add_new_character'),
    path('add-place', views.add_new_place, name='add_new_place'),
    path('add-commentary', views.add_new_commentary, name='add_new_commentary'),

    # change state of note
    path('state/<int:note_id>', views.change_state, name='change_state'),

    # save dante text
    path('saveDanteText/<int:note_id>', views.save_dante_text, name='save_dante_text'),

    # save body note TO DEPRECATE ---------------
    path('saveBodyNote/<int:note_id>', views.save_body_note, name='save_body_note'),

    # structure for tree view
    path('tree/<int:note_id>/<slug:cantica_canto>', views.cantiche_tree, name='cantiche_tree'),

    # login view
    path('accounts/', include('django.contrib.auth.urls')),
    

    # authentication view
    path('auth', views.auth, name='auth'),
     # getusers view
    path('getusers/pippo', views.getusers, name='getusers'),
    
]
