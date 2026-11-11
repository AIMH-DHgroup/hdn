from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django.contrib.auth.models import User
import json as j
from django.db.models import Count, Q, Subquery, OuterRef, CharField, F
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models.functions import Cast, Coalesce

# Function to make text red
def red(text):
    return format_html(f'<span style="color: red;">{text}</span>')

# Function to truncate text
def truncate(text, length=50, suffix='...'):
    if len(text) <= 50:
        suffix = ''
    return f'{text[:length].strip()}{suffix}'


# Annotation admin
class AnnotationAdmin(admin.ModelAdmin):
    fields = ['id', 'commentary', 'body', 'dante_reference', 'owner', 'dante_fragment', 'citations', 'data']
    readonly_fields = ['id', 'commentary', 'body', 'dante_reference', 'owner', 'dante_fragment', 'citations']
    list_display = ['id', 'commentary', 'body', 'dante_reference', 'owner', 'dante_fragment', 'citations']
    actions = ['fix_json']

    # Action to fix bad JSON
    def fix_json(self, request, queryset):
        for obj in queryset:
            obj.data = j.loads(obj.data)
            obj.save()

    # Commentary field (IRI of commentary)
    def commentary(self, obj):
        if (isinstance(obj.data, str)):
            return red('Bad JSON')
        if obj.data and 'Commento' in obj.data['Nota']:
            return obj.data['Nota']['Commento']['Nome']
        return red('Missing field: Commento')

    # Body field (truncated string of note body)
    def body(self, obj):
        if (isinstance(obj.data, str)):
            return red('Bad JSON')
        if obj.data and 'BodyNota' in obj.data['Nota']:
            return truncate(obj.data['Nota']['BodyNota'])
        return red('Missing field: BodyNota')

    # Dante fragment field (string of Dante's text)
    def dante_fragment(self, obj):
        if (isinstance(obj.data, str)):
            return red('Bad JSON')
        if obj.data and 'FrammentoDante' in obj.data['Nota']:
            return obj.data['Nota']['FrammentoDante']
        return red('Missing field: FrammentoDante')

    # Dante fragment field (string of Dante's text)
    def owner(self, obj):
        if (isinstance(obj.data, str)):
            return red('Bad JSON')
        if obj.data and 'owner' in obj.data:
            return obj.data['owner']
        return red('Missing field: Owner')

    # Dante reference field (string containing cantica, canto, verso)
    def dante_reference(self, obj):
        if (isinstance(obj.data, str)):
            return red('Bad JSON')
        if obj.data and 'OperaDante' in obj.data['Nota']:
            cantica = obj.data['Nota']['OperaDante']['Cantica']
            canto = obj.data['Nota']['OperaDante']['Canto']
            verso = obj.data['Nota']['OperaDante']['Verso']
            return ', '.join([cantica, str(canto), str(verso)])
        return red('Missing field: OperaDante')

    # Citations field (string containing a list of citations)
    def citations(self, obj):
        if (isinstance(obj.data, str)):
            return red('Bad JSON')

        # Function to build a list from citation data
        def make_citation_string(index, citation):
            citationData = [f'Citation {index+1}']
            if 'FrammentoNota' in citation:
                citationData.append(f'• {truncate(citation["FrammentoNota"])}')
            else:
                citationData.append('• No annotation fragment')
            if 'TipoCitazione' in citation:
                citationData.append(f'• {citation["TipoCitazione"]}')
            else:
                citationData.append('• No citation type')
            if 'InfoCitazione' in citation:
                if 'Autore' in citation['InfoCitazione']:
                    citationData.append(f'• {citation["InfoCitazione"]["Autore"]}')
                else:
                    citationData.append('• No author')
                if 'Fonte' in citation['InfoCitazione']:
                    citationData.append(f'• {citation["InfoCitazione"]["Fonte"]}')
                else:
                    citationData.append('• No source')
                if 'TipoFonte' in citation['InfoCitazione']:
                    citationData.append(f'• {citation["InfoCitazione"]["TipoFonte"]}')
                else:
                    citationData.append('• No source type')
                if 'Area' in citation['InfoCitazione']:
                    citationData.append(f'• {citation["InfoCitazione"]["Area"]}')
                else:
                    citationData.append('• No area')
            else:
                citationData.append(red('• No info'))
            return '<br>'.join(citationData)

        # If citations exist, build the list
        if obj.data and 'Citazioni' in obj.data['Nota']:
            citations = obj.data['Nota']['Citazioni']
            if len(citations) > 0:
                citationStrings = [make_citation_string(index, cit) for index, cit in enumerate(citations)]
                return format_html('<br><br>'.join(citationStrings))

        return red('Missing field: Citazioni')

    # Allow HTML tags in fields
    body.allow_tags = True
    dante_fragment.allow_tags = True
    dante_reference.allow_tags = True
    citations.allow_tags = True

    # Give more readable name to action
    fix_json.short_description = 'Fix bad JSON'


# Area admin
class AreaAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'iri', 'data']
    readonly_fields = ['id', 'name', 'iri']
    list_display = ['id', 'name', 'iri']
    ordering = ['-data__id']

    # Name field (string)
    def name(self, obj):
        try:
            return obj.data['name']
        except KeyError:
            return red('Missing field: Name')

    # IRI field (IRI)
    def iri(self, obj):
        try:
            return format_html(f'<a href={obj.data["iri"]}>{obj.data["iri"]}</a>')
        except KeyError:
            return red('Missing field: IRI')


# Author admin
class AuthorAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'iri', 'data']
    readonly_fields = ['id', 'name', 'iri']
    list_display = ['id', 'name', 'added_by', 'iri']
    ordering = ['-data__id']

    def added_by(self, obj):
        try:
            if 'user' in obj.data:
                user = User.objects.get(id=obj.data['user'])
                return user.username
        except (KeyError, ValueError):
            return '?'

    # Name field (string)
    def name(self, obj):
        try:
            return obj.data['name']
        except (KeyError, TypeError):
            return red('Missing field: Name')

    # IRI field (IRI)
    def iri(self, obj):
        try:
            return format_html(f'<a href={obj.data["iri"]}>{obj.data["iri"]}</a>')
        except (KeyError, TypeError):
            return red('Missing field: IRI')

# Source admin
class SourceAdmin(admin.ModelAdmin):
    fields = ['id', 'title', 'iri', 'author', 'area', 'data']
    readonly_fields = ['id', 'title', 'iri', 'author', 'area']
    list_display = ['id', 'title', 'added_by', 'iri', 'author']#, 'area']
    ordering = ['-data__id']
    #actions = ['fix_iri']

    def added_by(self, obj):
        try:
            if 'user' in obj.data:
                user = User.objects.get(id=obj.data['user'])
                return user.username
        except (KeyError, ValueError):
            return '?'

    # Title field (string)
    def title(self, obj):
        try:
            return obj.data['title']
        except KeyError:
            return red('Missing field: Title')

    # IRI field (IRI)
    def iri(self, obj):
        try:
            return format_html(f'<a href={obj.data["iri"]}>{obj.data["iri"]}</a>')
        except KeyError:
            return red('Missing field: IRI')

    # Author field (author name retrieved from IRI)
    def author(self, obj):
        try:
            author_iri = obj.data['author']
            try:
                author = Author.objects.get(data__iri=author_iri)
            except Author.DoesNotExist:
                print(f'Missing author: {author_iri}')
                return red('Missing author: {author_iri}')
            else:
                return format_html(f'<a href="../author/{author.id}">{author.data["name"]}</a>')
        except KeyError:
            return red('Missing field: Author')

    # Area field (area name retrieved from IRI)
    def area(self, obj):
        try:
            area_iri = obj.data['area']
            try:
                area = Area.objects.get(data__iri=area_iri)
            except Area.DoesNotExist:
                return red('Missing area: {area_iri}')
            else:
                return format_html(f'<a href="../area/{area.id}">{area.data["name"]}</a>')
        except KeyError:
            return red('Missing field: Area')

    # In case we need to fix some IRIs
    def fix_iri(self, request, queryset):
        for obj in queryset:
            if obj.data["iri"].startswith('https://hdn.') and '/source' not in obj.data["iri"]:
                obj.data["iri"] = obj.data["iri"].replace('/resource/', '/resource/source/')
                obj.save()

    # Allow HTML tags in some fields
    iri.allow_tags = True
    title.allow_tags = True

# Commentary admin
class CommentaryAdmin(admin.ModelAdmin):
    fields = ['id', 'iri', 'name', 'owner', 'notes', 'to_do', 'doing', 'done', 'data']
    readonly_fields = ['id', 'iri', 'name', 'owner', 'notes', 'to_do', 'doing', 'done']
    list_display = ['id', 'iri', 'name', 'owner','notes', 'to_do', 'doing', 'done']

    def get_queryset(self, request):
        qs = super().get_queryset(request).annotate(cname=KeyTextTransform('name', 'data'))
        annot = Annotation.objects.annotate(cname=KeyTextTransform('Nome', KeyTextTransform('Commento', KeyTextTransform('Nota', 'data'))))
        annot_all = annot.filter(cname=OuterRef('cname'))
        annot_todo = annot_all.filter(Q(data__Stato='to-do'))
        annot_doing = annot_all.filter(Q(data__Stato='doing'))
        annot_done = annot_all.filter(Q(data__Stato='done'))
        total = Subquery(annot_all.values('cname').annotate(tot=Count('pk')).order_by().values('tot')[:1])
        to_do = Subquery(annot_todo.values('cname').annotate(tot=Count('pk')).order_by().values('tot')[:1])
        doing = Subquery(annot_doing.values('cname').annotate(tot=Count('pk')).order_by().values('tot')[:1])
        done = Subquery(annot_done.values('cname').annotate(tot=Count('pk')).order_by().values('tot')[:1])
        return qs.annotate(total=total, to_do=to_do, doing=doing, done=done)

    # IRI field (IRI)
    def iri(self, obj):
        try:
            return format_html(f'<a href={obj.data["iri"]}>{obj.data["iri"]}</a>')
        except KeyError:
            return red('Missing field: IRI')
    
    def owner(self, obj):
        note = Annotation.objects.filter(data__Nota__Commento__Nome=obj.data['name'])[:1]
        if note:
            return note[0].data['owner']
        return 'Not assigned'

    def to_do(self, obj):
        try:
            return obj.to_do
        except KeyError:
            return red('Missing field: to_do')
    
    def doing(self, obj):
        try:
            return obj.doing        
        except KeyError:
            return red('Missing field: doing')
    
    def done(self, obj):
        try:
            return obj.done       
        except KeyError:
            return red('Missing field: done')
    
    def notes(self, obj):
        try:
            return obj.total                
        except KeyError:
            return red('Missing field: notes')

    # Author field (author name retrieved from IRI)
    def name(self, obj):
        try:
            if 'user' in obj.data and obj.data['user']:
                user_warning = red(f"[added by {obj.data['user']}]")
                return format_html(f'{obj.data["name"]} {user_warning}')
            else:
                return obj.data['name']
        except KeyError:
            return red('Missing field: name')



# Owner admin
class OwnerAdmin(admin.ModelAdmin):
    fields = ['commentary', 'owner']
    list_display = ['commentary', 'owner']
    readonly_fields = ['commentary']
    # fields = ['commentary', 'name', 'owner', 'username']
    # readonly_fields = ['name', 'username']
    # list_display =  ['commentary', 'name', 'owner', 'username']

    # Commentary field (commentary name name retrieved from id)
    def response_change(self, request, obj):
        # perfom my actions
        notes = Annotation.objects.filter(data__Nota__Commento__Nome=obj.commentary)
        for note in notes:
            # print(obj.owner.get_username())
            # note.data['owner'] = obj.owner.id
            note.data['owner'] = obj.owner.get_username()
            Annotation.objects.filter(pk=note.id).update(data=note.data)
        return super(OwnerAdmin, self).response_change(request, obj)

class CharacterAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'iri', 'data']
    readonly_fields = ['id', 'name', 'iri']
    list_display = ['id', 'name', 'added_by', 'iri']
    ordering = ['-data__id']

    def added_by(self, obj):
        try:
            if 'user' in obj.data:
                user = User.objects.get(id=obj.data['user'])
                return user.username
        except (KeyError, ValueError):
            return '?'

    # Name field (string)
    def name(self, obj):
        try:
            return obj.data['name']
        except KeyError:
            return red('Missing field: Name')

    # IRI field (IRI)
    def iri(self, obj):
        try:
            return format_html(f'<a href={obj.data["iri"]}>{obj.data["iri"]}</a>')
        except KeyError:
            return red('Missing field: IRI')

class PlaceAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'iri', 'data']
    readonly_fields = ['id', 'name', 'iri']
    list_display = ['id', 'name', 'added_by', 'iri']
    ordering = ['-data__id']

    def added_by(self, obj):
        try:
            if 'user' in obj.data:
                user = User.objects.get(id=obj.data['user'])
                return user.username
        except (KeyError, ValueError):
            return '?'

    # Name field (string)
    def name(self, obj):
        try:
            return obj.data['name']
        except KeyError:
            return red('Missing field: Name')

    # IRI field (IRI)
    def iri(self, obj):
        try:
            return format_html(f'<a href={obj.data["iri"]}>{obj.data["iri"]}</a>')
        except KeyError:
            return red('Missing field: IRI')

# Register all admins
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Commentary, CommentaryAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Place, PlaceAdmin)

