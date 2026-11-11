> Documento storico convertito dal DOCX fornito. I token sono stati rimossi. Le istruzioni aggiornate e i limiti verificati sono nel [README](../../README.md).


## Tool di annotazione HDN

Il tool di annotazione di HDN è sviluppato in linguaggio Python ed è basato sulla libreria Django. È costituito da una web application che si interfaccia con un database PostgreSQL.

Le istruzioni di installazione di PostgreSQL sono relative agli ambienti Debian/Ubuntu, ma quelle che seguono dovrebbero funzionare su qualunque sistema Unix.

### Installazione PostgreSQL

PostgreSQL ([https://www.postgresql.org](https://www.postgresql.org)) è il database che utilizziamo in HDN. È un database relazionale, che però può anche essere usato in modo simile a un document-based database in quanto supporta la definizione di campi JSON.

1. Installare PostgreSQL usando apt:

> sudo apt-get install postgresql

2. Se non vengono installati automaticamente può essere necessario installare anche:

> sudo apt-get install postgresql-client postgresql-client-common 

  postgresql-common postgresql-contrib

3. Installare libpq e psycopg usando apt:

> sudo apt-get install libpq-dev python-psycopg2

4. Avviare postgresql: sudo service postgresql start

5. Controllare se il client postgres funziona: sudo -u postgres -i

6. Creare un utente:

> createuser --interactive --pwprompt

> Enter name of role to add: inserire un nome utente

> Enter password for new role: inserire una password

> Enter it again: reinserire la medesima password

> Shall the new role be a superuser? (y/n) Inserire “y”

7. Creare un DB: 

> createdb hdn

#### Installazione phpPgAdmin (opzionale)

#### [phpPgAdmin](http://phppgadmin.sourceforge.net) è l’interfaccia di amministrazione di PostgreSQL. Installarla non è indispensabile, perché è possibile gestire il DB direttamente da Django, ma è comunque utile averla nel caso fosse necessario eseguire qualche operazione direttamente sul DB.

#### 1. Installare phpPgAdmin usando apt:

> sudo apt-get install phppgadmin

2. Il file di configurazione principale è in: /etc/phppgadmin/config.inc.php

3. Il file di configurazione Apache è in: /etc/apache2/conf-available/phppgadmin.conf

4. Se Django gira in locale non dovrebbe essere necessario modificare questi file, altrimenti bisogna sostituire la direttiva Require local con Allow from all nel file di Apache.

5. In caso di installazione su server, riavviare Apache: sudo apachectl restart

6. L’interfaccia web è accessibile al seguente indirizzo: http://localhost:8888/phppgadmin

### Collegamento a SVN

Il repository SVN che utilizziamo si trova sul server Dante2, al seguente indirizzo: [http://dante2.isti.cnr.it/svn/DanteRepo1/hdnDevelop](http://dante2.isti.cnr.it/svn/DanteRepo1/hdnDevelop). Per accedere al repository è necessario inserire nome utente e password.

1. Scaricare da SVN la cartella del progetto: svn checkout http://dante2.isti.cnr.it/svn/DanteRepo1/hdnDevelop

2. Entrare nella directory: cd hdnDevelop

### Installazione moduli Python

I moduli Python vengono installati in un [virtual environment](https://docs.python.org/3/tutorial/venv.html), in questo modo il progetto è auto-contenuto e più facilmente portabile.

1. Creare un nuovo virtual environment (quello presente su SVN non funziona correttamente), lanciando da terminale il comando: python3 -m venv newenv

2. Controllare se la variabile PYTHONPATH è vuota: echo $PYTHONPATH

3. Se la variabile non è vuota, modificare lo script di attivazione ./newenv/bin/activate per evitare conflitti, aggiungendo come prima riga del file: unset PYTHONPATH

4. Attivare il virtual environment: source ./newenv/bin/activate

2. Aggiornare pip (non usare mai sudo nel virtual environment): pip3 install -U pip 

3. Installare Django: pip3 install django

4. Installare Asgiref: pip3 install asgiref

5. In caso di problemi con Asgiref, installare il seguente pacchetto:

> sudo apt install build-essential

6. Installare psycopg2: pip3 install psycopg2

7. Installare FontAwesome: pip3 install fontawesome

### Configurazione progetto Django

[Django](https://www.djangoproject.com) è la libreria che utilizziamo per gestire sia l’interfaccia utente del tool, sia il backend e la comunicazione con il DB. In caso di dubbi, fare riferimento alla [documentazione di Django](https://docs.djangoproject.com/en/3.0/).

1. Le impostazioni di Django si trovano nel file ./hdn/settings.py, che va così modificato:

- Alla riga 82, inserire il nome del DB: 'hdn'

- Alla riga 83, inserire il proprio nome utente PostgreSQL

- Alla riga 84, inserire la propria password PostgreSQL

2. In caso di installazione su server (in locale no), occorre attivare la direttiva STATIC_ROOT e poi lanciare il comando python3 manage.py collectstatic per fare in modo che tutti i file statici (anche quelli dell’admin) vengano serviti correttamente

3. Creare un superuser per Django: python3 manage.py createsuperuser

4. Lanciare i due comandi seguenti per aggiornare il DB:

> python3 manage.py makemigrations

> python3 manage.py migrate

5. Lanciare il server di sviluppo di Django: python3 manage.py runserver

6. Provare ad accedere all’admin di Django: [http://localhost:8000](http://localhost:8000/admin/)[/admin](http://localhost:8000/admin/) (inserire le credenziali del superuser creato al punto 3)

7. L’interfaccia utente è accessibile al seguente indirizzo: [http://localhost:8000/annotation](http://localhost:8000/annotation/)

8. Se in seguito è necessario uscire dal virtual environment, lanciare il comando: deactivate

### Installazione plugin per authorization

I due plugin che stiamo valutando per implementare le funzionalità di authorization sono [Django Rules](https://github.com/dfunckt/django-rules) e [Django Guardian](https://github.com/django-guardian/django-guardian). Per installarli, procedere come segue:

1. Se non si è già nel virtual environment, attivarlo: source ./env/bin/activate

2. Installare Django Rules nel virtual environment: pip3 install rules

3. Installare Django Guardian nel virtual environment: pip3 install django-guardian

4. Per attivare le due librerie, modificare il file hdn/settings.py come indicato nelle rispettive istruzioni di installazione.

### Importazione dati di default

Nella cartella json che si trova in annotation sono presenti dei file JSON con alcuni dati di default che possono essere importati nel DB. Basta lanciare i seguenti comandi:

> python3 manage.py import_iri

> python3 manage.py import_notes

Gli script corrispondenti si trovano nella cartella annotation/management/commands. Lo script import_iri importa gli autori, le fonti e le aree tematiche. Lo script import_notes importa alcune note di esempio (esiste anche uno script export_notes per esportarle).

Conviene inoltre aggiungere dall’interfaccia di amministrazione ([http://localhost:8000/admin/auth/user/](http://localhost:8000/admin/auth/user/)) uno o più utenti che non siano superuser, ad esempio l’utente fittizio andrea.rossi che Massimiliano ha creato nel VRE.

### Struttura del progetto Django

hdnDevelop è la cartella principale del progetto, e contiene le seguenti sottocartelle e file:

- annotation contiene i file di configurazione del tool di annotazione

- env è un virtual environment di prova (ignorarlo)

- hdn contiene i file di configurazione generale del progetto (es. settings.py)

- manage.py è uno script che viene usato per gestire il progetto Django

- newenv è il virtual environment creato durante l’installazione

- static è la cartella da cui vengono serviti i file statici dal server di sviluppo

L’applicazione vera e propria si trova nella cartella annotation, che a sua volta contiene:

- admin.py è la configurazione dell’interfaccia di amministrazione

- forms.py è la configurazione dei form utilizzati nel tool

- management contiene degli script utili che vengono lanciati da terminale

- models.py è la configurazione dei modelli Django, corrispondenti alle tabelle del DB

- test.py serve per gestire il testing

- views.py contiene le viste del tool di annotazione

- apps.py definisce il nome dell’applicazione

- json contiene i file JSON che importiamo nel DB

- migrations contiene dei file che servono per modificare la struttura del DB

- templates contiene dei template che usiamo per le viste

- urls.py contiene la configurazione degli URL gestiti da Django

### Viste del tool di annotazione

[Questa sezione è incompleta]

La maggior parte del codice del tool si trova nel file views.py. Al momento, la prima vista che viene caricata è una IndexView statica (riga 33 di views.py, riga 8 di urls.py), ma dobbiamo sostituirla con una vista dinamica di selezione dei commenti assegnati all’utente. Cliccando su uno dei commenti, si passa alla vista get_note (riga 61 di views.py, riga 11 di urls.py) che contiene il form di inserimento dati.

### Vista di autenticazione

In fondo al file views.py (riga 588) c’è una vista di prova che chiama le API di D4Science e verifica se l’utente corrispondente esiste nel DB oppure no. Si tratta della vista auth, che è accessibile in questo modo:

[http://localhost:8000/annotation/auth?id=andrea.rossi&gcube-token=TOKEN_RIMOSSO](http://localhost:8000/annotation/auth?id=andrea.rossi&gcube-token=TOKEN_RIMOSSO)

Questa vista è scollegata dall’autenticazione di Django (si tratta semplicemente di un test). Bisognerebbe fare in modo che questi controlli vengano eseguiti dal backend di autenticazione (v. sezione Backend di autenticazione) al primo accesso al tool, e possibilmente anche a ogni operazione successiva che viene svolta dall’utente.

### Controllo dei login e dei permessi

Sulla maggior parte delle viste contenute nel file views.py è presente un decorator @login_required ([documentazione](https://docs.djangoproject.com/en/3.0/topics/auth/default/#the-login-required-decorator)), che fa sì che non sia possibile accedere alle viste senza aver preventivamente fatto il login. Questo controllo viene gestito automaticamente da Django.

È possibile sostituire il decorator @login_required con @permission_required, che controlla anche i permessi utente ([documentazione](https://docs.djangoproject.com/en/3.0/topics/auth/default/#the-permission-required-decorator)), in questo modo:

@permission_required('annotation.change_annotation', raise_exception=True)

Però questo controlla soltanto che l’utente abbia il permesso globale di modificare le note, mentre non esegue alcun controllo sulla ownership della singola nota.

### Backend di autenticazione

### Nel file hdn/backend.py c’è un esempio di backend di autenticazione, che può essere attivato in hdn/settings.py (riga 134). Questo semplice backend dovrebbe controllare se l’utente possiede una specifica nota (andando a guardare un campo Owner nel JSON della nota), e in questo caso consentirne la modifica.

Se attivato, il backend viene caricato correttamente, ma purtroppo al momento non funziona perché @permission_required non gli passa in input il singolo oggetto, e quindi non riesce a eseguire il controllo. Per farlo bisognerebbe definire un nuovo decorator.

Pare che il plugin [Django Guardian](https://github.com/django-guardian/django-guardian) adotti proprio questo approccio: definisce un backend di autenticazione per controllare la ownership degli oggetti ([qui il codice](https://github.com/django-guardian/django-guardian/blob/devel/guardian/backends.py)). Poi ridefinisce @permission_required per fargli passare l’oggetto al backend ([qui il codice](https://github.com/django-guardian/django-guardian/blob/devel/guardian/decorators.py)).

### Struttura del database PostgreSQL

Il database è attualmente strutturato in cinque tabelle:

- Annotation contiene le note

- Source contiene le fonti primarie citate da Dante

- Author contiene gli autori delle fonti primarie

- Area contiene le aree tematiche

- Commentary contiene i commenti

Ciascuna delle tabelle ha due sole colonne: id, un identificatore (numero intero); data, che contiene tutti i dati in formato JSON. In questo modo, la struttura del DB è più leggera e flessibile e i dati possono essere importati/esportati più facilmente usando JSON.

Le tabelle sono state create nel DB direttamente da Django, secondo lo schema definito nel file models.py. Il campo JSON invece viene popolato da noi (e dagli utenti del tool). Dall’[interfaccia di amministrazione](http://localhost:8000/admin/) di Django è possibile visualizzare e modificare tutte le tabelle.

Le sezioni che seguono descrivono la struttura del JSON (colonna data) delle varie tabelle.

### JSON della tabella Annotation

Al momento, la struttura del JSON relativo alla nota è la seguente:

{

"Nota": {

"FrammentoDante": STRING

"BodyNota": STRING,

"Commento": STRING,

"OperaDante": {

"Cantica": STRING,

"Canto": INT,

"Verso": INT,

},

"Citazioni": [

{

"FrammentoNota": STRING,

"TipoCitazione": STRING,

"InfoCitazione": {

"Fonte": IRI,

"Autore": IRI,

"Area": IRI,

}

],

},

"Stato": STRING,

"LastMod": DATE

}

Questa struttura corrisponde ai campi della scheda di annotazione (eccetto alcuni campi aggiuntivi che sono in fase di implementazione), e ricalca in parte quella del precedente progetto DanteSources.

Tramite il tool, l’utente ha la possibilità di modificare tutto ciò che si trova nell’attributo Nota, mentre Stato e LastMod sono metadati che vengono gestiti dal sistema. Qui si potrebbe aggiungere un campo Owner per associare alla nota l’utente che ha il permesso di modificarla.

### JSON della tabella Source

La struttura del JSON relativo alla fonte è la seguente:

{

"ire": IRI,

"title": STRING,

"author": IRI,

"area": IRI

}

### JSON della tabella Author

La struttura del JSON relativo all’autore è la seguente:

{

"iri": IRI,

"name": STRING

}

### JSON della tabella Area

La struttura del JSON relativo all’area tematica è la seguente:

{

"iri": IRI,

"name": STRING

}

### JSON della tabella Commentary

La struttura del JSON relativo al commento è la seguente:

{

"iri": IRI,

"name": STRING

}

### Tabella User

La tabella User è una tabella di default di Django, che è possibile visualizzare dall’interfaccia di amministrazione al seguente indirizzo: [http://localhost:8000/admin/auth/user/](http://localhost:8000/admin/auth/user/).

Per ogni utente, la tabella contiene i seguenti campi:

- Username

- Password (criptata con SHA256)

- First Name

- Last Name

- Email

- Permissions

- Last login

- Date joined

Per quanto riguarda le Permissions, è possibile definire:

- Active (se l’utente va considerato attivo oppure no)

- Staff status (l’utente può accedere all’interfaccia di amministrazione)

- Superuser status (l’utente ha automaticamente tutti i permessi)

- Groups (a quali gruppi appartiene l’utente)

- User permissions (quali tabelle può modificare l’utente)

Il campo Groups potrebbe essere utilizzato per distinguere i gruppi (v. sezione Tabella Group).

Purtroppo invece le User permissions non fanno al caso nostro, perché agiscono a livello di tabella e non a livello della singola riga. Quindi è possibile dare all’utente il permesso di modificare tutte le note o nessuna, ma non uno specifico sottoinsieme di note.

Purtroppo non è possibile salvare il token di D4Science o altri dati direttamente nella tabella User. Se vogliamo farlo, bisogna creare un modello aggiuntivo in models.py (e quindi una nuova tabella nel DB) che associa questi dati all’utente, come spiegato qui: [https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#extending-the-existing-user-model](https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#extending-the-existing-user-model).

### Tabella Group

La tabella Group è una tabella di default di Django, che è possibile visualizzare dall’interfaccia di amministrazione al seguente indirizzo: [http://localhost:8000/admin/auth/group](http://localhost:8000/admin/auth/group). Potremmo utilizzarla per gestire i gruppi (es. Annotatore, Revisore).
