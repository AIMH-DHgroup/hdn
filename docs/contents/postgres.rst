Installazione PostgreSQL
========================

`PostgreSQL <https://www.postgresql.org>` è il database che utilizziamo in HDN. È un database relazionale, che però può anche essere usato in modo simile a un document-based database in quanto supporta la definizione di campi JSON.

1. Installare PostgreSQL usando apt:

.. code-block::
    
    sudo apt-get install postgresql

2. Se non vengono installati automaticamente può essere necessario installare anche:

.. code-block::
    
    sudo apt-get install postgresql-client postgresql-client-common postgresql-common postgresql-contrib

3. Installare libpq e psycopg usando apt:

.. code-block::
    
    sudo apt-get install libpq-dev python-psycopg2

4. Avviare postgresql: 

.. code-block::

    sudo service postgresql start

5. Controllare se il client postgres funziona: 

.. code-block::
    
    sudo -u postgres -i

6. Creare un utente:

.. code-block::
    
    createuser --interactive --pwprompt
    Enter name of role to add: inserire un nome utente
    Enter password for new role: inserire una password
    Enter it again: reinserire la medesima password
    Shall the new role be a superuser? (y/n) Inserire “y”

7. Creare un DB: 

.. code-block::

    createdb hdn

Installazione phpPgAdmin (opzionale)
------------------------------------

phpPgAdmin è l’interfaccia di amministrazione di PostgreSQL. Installarla non è indispensabile, perché è possibile gestire il DB direttamente da Django, 
ma è comunque utile averla nel caso fosse necessario eseguire qualche operazione direttamente sul DB.

1. Installare phpPgAdmin usando apt:

.. code-block::

    sudo apt-get install phppgadmin

2. Il file di configurazione principale è in: ``/etc/phppgadmin/config.inc.php``
3. Il file di configurazione Apache è in: ``/etc/apache2/conf-available/phppgadmin.conf``
4. Se Django gira in locale non dovrebbe essere necessario modificare questi file, altrimenti bisogna sostituire la direttiva Require local con Allow from all nel file di Apache.
5. In caso di installazione su server, riavviare Apache: 

.. code-block::

    sudo apachectl restart

6. L’interfaccia web è accessibile al seguente indirizzo: http://localhost:8888/phppgadmin