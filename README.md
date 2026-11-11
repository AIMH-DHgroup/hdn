# HDN — Tool di annotazione

Applicazione web per annotare le note dei commenti alla *Commedia* di Dante e collegare citazioni, fonti, autori, aree tematiche, personaggi e luoghi. Il backend usa Python, Django e PostgreSQL; l'interfaccia include Bootstrap, TinyMCE e Font Awesome. L'accesso all'interfaccia di annotazione integra i servizi D4Science.

Questa copia è stata preparata per la pubblicazione rimuovendo le credenziali incorporate, la copia SVN, gli ambienti Python e la documentazione compilata. Il codice resta una versione storica: la preparazione per GitHub non comprende l'aggiornamento delle dipendenze né una verifica completa dell'applicazione in esecuzione.

## Contenuto del repository

| Percorso | Contenuto |
| --- | --- |
| `annotation/models.py` | Modelli del database |
| `annotation/views.py` | Viste, annotazione, integrazione D4Science e Wikidata |
| `annotation/forms.py` | Form di annotazione |
| `annotation/admin.py` | Interfaccia di amministrazione |
| `annotation/urls.py` | URL dell'applicazione |
| `annotation/templates/` | Template HTML |
| `annotation/migrations/` | Migrazioni dello schema |
| `annotation/management/commands/` | Comandi di importazione ed esportazione |
| `hdn/settings.py` | Configurazione Django tramite variabili d'ambiente |
| `hdn/d4sbackend.py` | Backend di autenticazione D4Science |
| `static/` | Risorse frontend del progetto e librerie distribuite |
| `requirements/requirements.txt` | Dipendenze con versioni storiche |
| `docs/` | Sorgenti Sphinx e documentazione storica |
| `postgres_backup.sh` | Backup PostgreSQL senza password incorporata |
| `.env.example` | Modello di configurazione locale privo di segreti |

## Requisiti e stato del progetto

L'archivio originale contiene ambienti Python 3.6 e il file dei requisiti fissa `Django==3.0.7`, `psycopg2==2.8.4` e numerose librerie dell'epoca. Alcune migrazioni risultano generate con Django 3.1.3: l'ambiente originale non è quindi ricostruibile con certezza dal solo archivio. Le versioni fissate non costituiscono un ambiente attuale mantenuto.

Servono PostgreSQL, il client `psql`/`pg_dump`, le librerie di sviluppo PostgreSQL e un interprete compatibile con le dipendenze storiche. Il codice usa `django.contrib.postgres.fields.JSONField`: passare a una versione recente di Django richiede modifiche e migrazioni, non soltanto cambiare il numero di versione.

Le istruzioni seguenti descrivono un percorso di riproduzione in ambiente isolato Debian/Ubuntu. L'installazione e l'avvio non sono stati eseguiti durante la revisione; non esporre questa versione direttamente su Internet prima di aggiornare le dipendenze e verificare autenticazione e autorizzazioni.

## Preparazione locale

### 1. Installare PostgreSQL e gli strumenti di compilazione

```bash
sudo apt update
sudo apt install postgresql postgresql-client libpq-dev build-essential
sudo service postgresql start
```

Installare anche il supporto `venv` e gli header di sviluppo corrispondenti all'interprete Python scelto.

### 2. Creare ruolo e database

```bash
sudo -u postgres createuser --pwprompt --no-superuser --no-createdb --no-createrole hdn
sudo -u postgres createdb --owner=hdn hdn
```

Scegliere una password nuova quando viene richiesta. L'utente applicativo non necessita del ruolo di superutente PostgreSQL. Se ruolo o database esistono già, verificare la configurazione esistente prima di procedere.

### 3. Creare un ambiente Python

Dalla cartella che contiene `manage.py`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/requirements.txt
```

`python3` deve indicare un interprete compatibile con le dipendenze storiche; il Python di una distribuzione attuale potrebbe non esserlo. In caso di errore non rimuovere i vincoli di versione alla cieca: ricostruire un ambiente storico isolato oppure svolgere una migrazione esplicita a versioni supportate. Gli ambienti inclusi nello ZIP originale non vanno riutilizzati.

### 4. Configurare le variabili d'ambiente

```bash
cp .env.example .env
chmod 600 .env
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Aprire `.env`, incollare la chiave appena generata nel campo `DJANGO_SECRET_KEY` e compilare `DB_PASSWORD` con la password scelta. La chiave e la password devono restare sul proprio computer o nel sistema di gestione dei segreti del server.

| Variabile | Significato | Valore predefinito nel codice |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Chiave segreta Django | Obbligatoria e non vuota |
| `DJANGO_DEBUG` | Abilita il debug; solo per sviluppo locale | `false` |
| `DJANGO_ALLOWED_HOSTS` | Host ammessi separati da virgole | `localhost,127.0.0.1` |
| `DB_NAME` | Nome database | `hdn` |
| `DB_USER` | Ruolo PostgreSQL | `hdn` |
| `DB_PASSWORD` | Password PostgreSQL | Variabile obbligatoria |
| `DB_HOST` | Host PostgreSQL | `localhost` |
| `DB_PORT` | Porta PostgreSQL | `5432` |
| `DJANGO_STATIC_ROOT` | Destinazione di `collectstatic` | `staticfiles/` nel progetto |

Il file `.env` non viene caricato automaticamente da Django. In Bash caricarlo nella sessione prima dei comandi di gestione:

```bash
set -a
source .env
set +a
```

Eseguire questi comandi solo su un `.env` locale fidato: `source` interpreta il contenuto come codice shell. Il modello abilita `DJANGO_DEBUG=true` per lo sviluppo locale; il valore predefinito nel codice resta `false`. Con debug disattivato i cookie di sessione e CSRF richiedono HTTPS.

### 5. Preparare il database e avviare lo sviluppo

```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Le migrazioni sono già incluse: `makemigrations` serve quando si modificano i modelli, non come normale passo di installazione.

- Amministrazione: <http://localhost:8000/admin/>
- Annotazione: <http://localhost:8000/annotation/>

Il superutente creato permette l'accesso all'admin. L'interfaccia di annotazione richiede invece un token D4Science valido, un utente corrispondente nel database locale e dati assegnati all'utente: il solo login nell'admin non basta. I dati iniziali non sono inclusi.

Il server `runserver` serve per sviluppo. Per un'installazione su server occorrono una configurazione WSGI/ASGI, HTTPS e la distribuzione degli statici; `python manage.py collectstatic` li raccoglie in `STATIC_ROOT` sotto il prefisso `/django-static/`.

## Database

Lo schema effettivo è definito dai modelli e dalle migrazioni, che prevalgono sulle descrizioni storiche allegate.

| Modello | Campi principali |
| --- | --- |
| `Annotation` | `id` intero lungo fornito dall'applicazione; `data` JSON |
| `Author` | `id` automatico; `data` JSON |
| `Source` | `id` automatico; `data` JSON |
| `Area` | `id` automatico; `data` JSON |
| `Commentary` | `id` automatico; `data` JSON |
| `Place` | `id` automatico; `data` JSON |
| `Character` | `id` automatico; `data` JSON |
| `Owner` | `id` automatico; `commentary` testuale; `owner` collegato a `auth.User` |

Si aggiungono le tabelle standard Django per utenti, gruppi, permessi e sessioni. Il campo `data` delle note contiene `Nota` e metadati come lo stato e l'assegnatario. Nell'importatore attuale `Nota.Commento` viene costruito come oggetto con `Id`, `IRI` e `Nome`: i vecchi esempi che lo rappresentano come semplice stringa o IRI non descrivono completamente il codice corrente.

## Importazione ed esportazione

La cartella `annotation/json/`, citata nei documenti, **non è presente nell'archivio ricevuto**. I dati devono essere recuperati separatamente e verificati prima dell'uso. La cartella è esclusa da Git per evitare pubblicazioni involontarie di dati operativi.

- `python manage.py import_iri`: importa, per impostazione predefinita, i file `areas.json`, `authors.json`, `sources.json`, `characters.json`, `places.json` e `commentaries.json` da `annotation/json/`. Offre opzioni per selezionare i tipi di risorsa.
- `python manage.py import_notes --path /percorso/note/`: tratta `--path` come prefisso di ricerca (`path + '*'`); una cartella con slash finale permette di selezionare i file al suo interno. Verificare formato dei dati e utenti richiesti prima dell'importazione.
- `python manage.py export_notes --path exports/notes.json`: esporta tutte le annotazioni in formato di serializzazione Django. Creare prima la cartella con `mkdir -p exports`.

Usare `python manage.py <comando> --help` per le opzioni. Gli importatori possono cancellare o modificare dati: provarli su un database di test con backup. In particolare `import_notes --delete` cancella annotazioni e assegnazioni `Owner`; non abbinarlo a `--dryrun`, perché la cancellazione nel codice precede i controlli di simulazione. L'export Django non è garantito compatibile direttamente con il formato richiesto dall'importatore.

## Backup

Dopo aver esportato le variabili d'ambiente:

```bash
bash postgres_backup.sh
```

Il backup viene scritto in `backups/` accanto allo script, oppure in `BACKUP_DIR` se impostata. Lo script usa `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT`; crea file con permessi limitati e si interrompe in caso di errore. I dump non devono essere aggiunti al repository.

## Documentazione

- [Tool di annotazione HDN](docs/fonti/tool-annotazione-hdn.md): conversione testuale del documento Word, con token rimosso anche dai link.
- [Struttura database HDN](docs/fonti/struttura-database-hdn.md): documento storico di progettazione, non una descrizione completa dello schema attuale.
- [Revisione prima della pubblicazione](docs/REVISIONE_PUBBLICAZIONE.md): riscontri, correzioni e limiti della verifica.

I sorgenti Sphinx originali sono in `docs/`. Con le dipendenze installate e le variabili d'ambiente caricate si può tentare la compilazione con `make -C docs html`; il risultato `docs/_build/` è escluso da Git. I vecchi testi possono contenere istruzioni superate: per configurazione e credenziali seguire questo README.

## Sicurezza e limiti residui

Le credenziali originarie vanno sostituite se ancora valide: password PostgreSQL, chiave Django e token D4Science di esempio. Rimuoverle da questa copia non revoca i valori originali né elimina copie precedentemente condivise.

La preparazione ha rimosso anche le stampe dirette dei token e la loro visualizzazione nella risposta della vista di prova. Rimangono aspetti che richiedono una revisione applicativa prima del deployment: token trasmessi nella query string, viste di prova `auth` e `getusers`, controlli di accesso non uniformi e dipendenze storiche. Il backend D4Science contiene inoltre un `get_user` annidato dentro `authenticate` e alcune viste chiamano `authenticate` con il token come argomento posizionale: questi comportamenti non sono stati modificati e richiedono verifica funzionale.

Non inserire mai token reali negli URL degli esempi, nei messaggi di commit, nelle issue o nella documentazione. Non caricare su GitHub lo ZIP originale né i DOCX originali; le versioni testuali ripulite sono già incluse.

## Pubblicazione su GitHub

1. Estrarre la cartella `hdn` del pacchetto ripulito. Aprire il terminale in questa cartella, dove si trova `manage.py`.
2. Su <https://github.com/new> creare un repository chiamato, per esempio, `hdn`. Scegliere la visibilità desiderata e lasciare disattivata la creazione iniziale di README, `.gitignore` e licenza: i file del progetto vengono caricati dal computer.
3. Inizializzare Git e controllare i file selezionati:

   ```bash
   git init -b main
   git add .
   git status --short
   git diff --cached --stat
   git diff --cached -- hdn/settings.py postgres_backup.sh .env.example
   ```

   Verificare che non compaiano `.env`, ambienti Python, `.svn`, backup o allegati originali. Se si è creato `.env`, `git check-ignore .env` deve indicare che viene ignorato.

4. Creare il commit e collegare il repository, sostituendo `TUO-UTENTE` e, se necessario, il nome `hdn`:

   ```bash
   git commit -m "Importa codice HDN e documentazione"
   git remote add origin https://github.com/TUO-UTENTE/hdn.git
   git push -u origin main
   ```

   Se Git richiede nome ed email, configurarli prima del commit con `git config user.name "Il tuo nome"` e `git config user.email "la-tua-email"`. Per HTTPS usare l'autenticazione GitHub tramite gestore credenziali o token personale; la password dell'account non è utilizzabile per il push. In alternativa usare un URL SSH dopo aver configurato la propria chiave. Non incorporare mai il token nell'URL del remote.

5. Aprire il repository su GitHub e verificare che il README sia visibile. Abilitare secret scanning e push protection se disponibili per il repository.

Per gli aggiornamenti successivi: `git add <file>`, `git commit -m "Descrizione"`, `git push`. Se un segreto viene pubblicato per errore, revocarlo o ruotarlo subito; cancellarlo soltanto dall'ultimo file non lo elimina dalla cronologia Git.

## Licenza e attribuzioni

Diversi sorgenti dichiarano copyright ISTI-CNR e gli autori indicati nelle intestazioni, con licenza GNU GPL versione 3 o successiva. Le intestazioni sono state conservate. Nell'archivio non è presente un file `LICENSE` generale con il testo integrale: completarlo coerentemente con le indicazioni dei titolari prima di un rilascio formale. Le librerie frontend mantengono le proprie licenze nei file distribuiti; non applicare loro automaticamente una nuova licenza.

## Riferimenti

- [Django: versioni e supporto](https://www.djangoproject.com/download/)
- [Django: campi PostgreSQL storici](https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/)
- [GitHub: pubblicare codice locale](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [GitHub: rimuovere dati sensibili](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
