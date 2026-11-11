# Revisione prima della pubblicazione

Data: 11 novembre 2026.

## Materiale esaminato

La revisione riguarda lo ZIP `hdn.zip` e i documenti `Tool di annotazione HDN.docx` e `Struttura database HDN.docx` forniti con il progetto. I valori sensibili non vengono riportati in questo documento.

## Riscontri e correzioni

I numeri di riga si riferiscono ai file originali, prima delle modifiche.

| Posizione originale | Riscontro | Intervento nella copia da pubblicare |
| --- | --- | --- |
| `hdn/settings.py:23` | Chiave segreta Django in chiaro | Lettura da `DJANGO_SECRET_KEY`, obbligatoria e non vuota |
| `hdn/settings.py:91` | Password PostgreSQL in chiaro | Lettura da `DB_PASSWORD`; anche gli altri parametri DB sono configurabili |
| `postgres_backup.sh:10` | Password PostgreSQL incorporata in `PGPASSWORD` | Password letta dall'ambiente; percorsi quotati, arresto su errore e permessi limitati |
| `annotation/views.py`, vista `auth` | Token D4Science di esempio presente come costante e in un URL di esempio | Eliminata la costante inutilizzata e ripulito l'esempio |
| `Tool di annotazione HDN.docx` | Token D4Science nell'URL di autenticazione, anche nella destinazione di un hyperlink | Fornita una conversione Markdown con token rimosso da testo e link; originale escluso dal pacchetto |
| `annotation/views.py` e `hdn/d4sbackend.py` | Stampe dei token ricevuti; vista di prova con token nella risposta HTML | Rimosse le stampe dirette del valore e la sua visualizzazione nella risposta |
| `.svn/` | Copie storiche contenenti anche valori sensibili | Cartella SVN interamente esclusa |
| `docs/_build/` | Documentazione compilata con copie storiche degli esempi | Output compilato escluso; mantenuti i sorgenti |
| `.env/` ed `env/` | Ambienti Python già installati, con librerie e file di test | Esclusi e sostituiti da istruzioni per creare un ambiente nuovo |

Non sono emerse credenziali nel testo e nei collegamenti del documento `Struttura database HDN.docx`. I due DOCX non contengono immagini o oggetti incorporati; nella copia da pubblicare sono inclusi come documenti Markdown, senza i contenitori originali.

La ricerca ha prodotto anche corrispondenze nelle librerie distribuite: per esempio `.data-api` in Bootstrap è uno spazio dei nomi degli eventi e non una chiave di servizio. Le corrispondenze di questo tipo sono state distinte dalle credenziali del progetto. I file degli ambienti Python, inclusi esempi e fixture che possono assomigliare a chiavi, non sono distribuiti nel nuovo pacchetto.

## Altre modifiche alla configurazione

Il debug ora è disattivato per impostazione predefinita e gli host ammessi sono limitati a `localhost` e `127.0.0.1`. Le variabili documentate nel README permettono di configurare l'ambiente. I cookie richiedono HTTPS quando il debug è disattivato; l'attivazione del debug consente lo sviluppo locale HTTP. I percorsi statici non dipendono più da una directory assoluta del vecchio server.

È stato aggiunto `.gitignore` per configurazioni locali, ambienti Python, copie SVN, cache, dump, dati operativi e archivi. Il file `.env.example` contiene solo campi da compilare e valori non sensibili.

## Verifiche e portata

Sono stati cercati assegnamenti di password e segreti, token di provider comuni, chiavi private, token D4Science letterali e URL con credenziali. Sono stati esaminati i sorgenti del progetto, la documentazione, le parti XML e le destinazioni dei collegamenti dei DOCX, oltre a ricercare corrispondenze nell'archivio originale, incluse le copie SVN e le dipendenze. La scansione testuale dei file binari è parziale e non rappresenta una verifica di ogni formato binario.

Sulla copia finale sono stati controllati 1.973 file e la sintassi di 32 sorgenti Python, la sintassi Bash dello script di backup, la configurazione senza segreti predefiniti, la rimozione dei token noti e dei messaggi che ne stampavano direttamente il valore, e l'assenza delle directory escluse. Lo script di backup è stato verificato con un client `pg_dump` simulato, senza contattare database reali. È stato controllato che `.gitignore` escluda configurazione locale e backup e consenta `.env.example`.

Il parser Python attuale segnala avvisi preesistenti per sequenze di escape nelle espressioni regolari di `import_notes.py`; non impediscono la lettura sintattica, ma rientrano nel lavoro di aggiornamento del codice.

Non sono stati eseguiti installazione delle dipendenze, `manage.py check`, migrazioni, accesso al database, autenticazione D4Science o test funzionali dell'interfaccia. L'ambiente di revisione non dispone di Django né del database del progetto. Non è stata importata la cronologia SVN in Git, né creato o pubblicato un repository remoto.

La ricerca non ha individuato ulteriori credenziali del progetto nei file destinati alla pubblicazione. È una revisione statica mirata: non garantisce l'assenza assoluta di segreti sconosciuti, cifrati, codificati o presenti altrove e non costituisce un audit applicativo completo.

## Azioni ancora necessarie

1. Se ancora valide, sostituire la password PostgreSQL, rigenerare la chiave Django e revocare o rigenerare il token D4Science presente negli originali. Rimuovere un valore dal codice non lo revoca.
2. Pubblicare solo il contenuto del nuovo pacchetto; non aggiungere lo ZIP originale o i DOCX originali e non copiare `.svn/` nel repository.
3. Recuperare separatamente i JSON iniziali mancanti e verificare gli utenti e le assegnazioni richiesti dall'applicazione.
4. Prima del deployment, aggiornare le dipendenze storiche e verificare autenticazione, autorizzazioni e viste di prova. In particolare, restano token nelle query string, controlli di accesso non uniformi, `get_user` annidato nel backend e chiamate posizionali ad `authenticate` da verificare.
5. Controllare i file selezionati prima del primo commit e abilitare le protezioni GitHub disponibili. Se un segreto è già stato pubblicato altrove, ruotarlo e valutare anche la rimozione dalla relativa cronologia.

## Riferimenti

- [GitHub: rimozione di dati sensibili e rotazione dei segreti](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [GitHub: importare un progetto locale](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
