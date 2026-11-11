> Documento storico convertito dal DOCX fornito. I token sono stati rimossi. Le istruzioni aggiornate e i limiti verificati sono nel [README](../../README.md).


## Struttura database HDN

### 1. Database

Il database è attualmente strutturato in un’unica tabella Annotation contenente le note, con due sole colonne: id, un numero intero che identifica la nota; data, che contiene le informazioni relative alle note in formato JSON secondo lo schema riportato nella sezione seguente.

Bisogna aggiungere due nuove tabelle: Source, per le fonti primarie citate da Dante, e Author, per gli autori delle fonti primarie. Così come la tabella Annotation, queste due tabelle dovranno contenere entrambe una colonna id e una colonna data.

In teoria si potrebbe anche aggiungere solo una tabella Author, senza tabella Source, e inserire tutte le fonti dentro il relativo autore, ma sarebbe un po’ scomodo perché esistono numerose fonti senza autore o con autori multipli. Mi sembra preferibile avere due tabelle separate.

Bisogna poi decidere se aggiungere anche una tabella per le aree tematiche oppure no. La differenza rispetto ad autori e fonti è che la lista delle aree tematiche dovrebbe essere fissa e non modificabile dagli utenti. Però mi sono accorto che le aree che abbiamo in DanteSources non provengono tutte dal Soggettario Nazionale, alcune le avevamo aggiunte noi.

### 2. JSON della tabella Annotation

Attualmente, il form di annotazione salva i dati in un JSON con la seguente struttura:

"Nota": {

"Testo": STRING,

"Body": STRING,

"Source": {

"Libro": INT,

"Capitolo": INT,

"Paragrafo": INT

},

"Selettore": {

"start": INT,

"end": INT

},

"Citazione": {

"Frammento": STRING,

"Tipo": STRING,

"InfoOperaCitata": {

"OperaURI": IRI,

"TitoloOpera": STRING,

"Autore": {

"Name": STRING,

"URI": IRI

},

"Area": IRI,

"TipoOpera": STRING

}

}

}

Rispetto alla versione attuale, occorre fare alcune modifiche per supportare meglio le funzionalità di HDN e rendere meno ambigui i nomi dei campi.

Bisognerebbe anche decidere se lasciare i campi in italiano oppure tradurli in inglese: se vogliamo renderli visibili (anche solo come opzione) nel tool di annotazione allora forse è meglio l’italiano, altrimenti si potrebbe anche tradurre tutto in inglese. Voi che dite?

Proporrei comunque le seguenti modifiche:

- Sostituire il campo Testo con FrammentoDante, per maggiore chiarezza

- Sostituire il campo Body con BodyNota, anche questo per chiarezza

- Aggiungere un campo Commento, che è un IRI e indica il commento alla Commedia da cui estraiamo le note

- Sostituire il campo Source con OperaDante. Questo campo contiene le informazioni relative a cantica, canto e verso della Commedia. La cantica è una stringa (Inferno, Paradiso, Purgatorio), mentre canto e verso sono numeri interi

- Sostituire il campo Citazione con Citazioni e trasformarlo in un array (una nota può contenere più citazioni)

- Nella citazione, sostituire il campo Frammento con FrammentoCitazione, per distinguerlo meglio dal frammento dantesco

- Nella citazione, sostituire il campo Tipo con TipoCitazione, per chiarezza

- Nella citazione, sostituire il campo TipoOpera con TipoFonte, perché si tratta di una fonte primaria

- Nella citazione, sostituire il campo InfoOperaCitata con InfoCitazione, perché in certi casi non è citata un’opera specifica, ma solo un autore o un’area tematica

- Nella citazione, semplificare il campo InfoCitazione togliendo i sottocampi TitoloOpera e Name e lasciando solo gli IRI relativi all’autore, alla fonte e all’area tematica tutti allo stesso livello. Possiamo recuperare le informazioni relative a nomi e titoli dalle tabelle Author e Source. Se le conserviamo anche qui dentro diventa scomodo sincronizzarle

Un’altra cosa da decidere è se togliere il selettore, visto che concretamente in DanteSources non ci è mai servito → lo togliamo

Inoltre, quando avremo il sistema di autenticazione funzionante dovremo conservare per ogni nota anche l’ID dell’annotatore. Questo lo terrei esterno, allo stesso livello del campo Nota, e penso che sarebbe utile riportare anche la data di modifica. Comunque questo non è urgente e possiamo decidere come implementarlo una volta che avremo l’autenticazione.

Intanto la versione modificata sarebbe così:

"Nota": {

"FrammentoDante": STRING,

"BodyNota": STRING,

"Commento": IRI,

"OperaDante": {

"Cantica": STRING,

"Canto": INT,

"Verso": INT

},

"Citazioni": [

{

"FrammentoNota": STRING,

"TipoCitazione": STRING,

"InfoCitazione": {

"Fonte": IRI,

"Autore": IRI,

"Area": IRI,

"TipoFonte": STRING

}

}

]

}

### 3. JSON della tabella Author

La tabella Author contiene una colonna id e una colonna data. Per la colonna id potrebbe essere una buona idea usare direttamente l’IRI (invece che creare ID numerici), anche per facilitare le query. La colonna data dovrà invece essere in formato JSON, con i seguenti campi:

{

"IRIAutore": IRI,

"NomeAutore": STRING

}

### 4. JSON della tabella Source

La tabella Source contiene una colonna id e una colonna data. Per la colonna id potrebbe essere una buona idea usare direttamente l’IRI (invece che creare ID numerici), anche per facilitare le query. La colonna data dovrà invece essere in formato JSON, con i seguenti campi:

{

"IRIFonte": IRI,

"TitoloFonte": STRING,

"AutoreFonte": IRI,

"AreaFonte": IRI

}

Rispetto alla tabella Author, la tabella Source aggiunge i campi relativi all’autore e all’area tematica della fonte, che per le opere già inserite in DanteSources abbiamo a disposizione.

### 5. Popolamento delle tabelle Author e Source

Attualmente, le informazioni relative agli autori e alle fonti di DanteSources sono conservate in un file JSON (oltre che in RDF nel [triple store](https://dantesources.dantenetwork.it/sparql) interrogabile via SPARQL). Gli autori contenuti nel JSON sono 197, mentre le fonti sono 438.

Sul totale degli autori, 166 (84%) hanno un IRI DBpedia, mentre gli altri 31 (16%) hanno un IRI definito da noi, perché non erano presenti in DBpedia. Sul totale delle fonti, solo 130 (30%) hanno un IRI DBpedia, mentre le restanti 308 (70%) hanno un IRI definito da noi.

Ci conviene passare a Wikidata, che ci offre un numero di autori e fonti più grande di quello di DBpedia e ci dà anche la possibilità di inserirne di nuovi. Ho quindi eseguito un mapping fra le entità di DBpedia e quelle di Wikidata (molto semplice da fare con una query SPARQL sull’[endpoint di DBpedia](https://dbpedia.org/sparql), perché ogni entità DBpedia contiene un link a Wikidata). Ad esempio:

SELECT ?iri

WHERE {

<http://dbpedia.org/resource/Avicenna> owl:sameAs ?iri .

FILTER CONTAINS (STR(?iri), "wikidata.org")

}

In questo modo ho sostituito tutti gli IRI DBpedia con i corrispondenti IRI Wikidata. Poi ho scritto del codice Python per mappare in modo semi-automatico le entità rimanenti, eseguendo una query sull’[endpoint di Wikidata](https://query.wikidata.org) sulla base del nome o titolo e approvando ogni match in modo interattivo. Ho usato query simili a questa, ma selezionando più lingue invece che solo l’italiano:

SELECT distinct ?item ?itemLabel ?itemDescription

WHERE {

?item wdt:P31/wdt:P279* Q5 .

{?item rdfs:label "Avicenna"@it .}

UNION {?item skos:altLabel "Avicenna"@it .}

SERVICE wikibase:label {bd:serviceParam wikibase:language "it"}

}

In questo modo sono riuscito a collegare a Wikidata diversi altri autori e fonti, per un totale di 185 autori su 197 (94%) e 196 fonti su 438 (45%). Credo che gli autori siano tutti quelli presenti in Wikidata, invece per le fonti è possibile che ce ne sia qualche altra che non ho trovato. Per quanto riguarda i rimanenti 12 autori e 242 fonti che avevano IRI nostri, ho modificato i vecchi IRI per utilizzare il nuovo dominio hdn.dantenetwork.it.

Visto che gli autori mancanti sono pochi, potremmo inserirli noi in Wikidata e utilizzare gli IRI così generati. Per le fonti invece bisogna decidere se inserirle tutte in Wikidata oppure attivare un servizio di risoluzione IRI sul nostro server (come avevamo fatto per le narrazioni).
