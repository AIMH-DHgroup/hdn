Installazione moduli Python
============================

I moduli Python vengono installati in un virtual environment, in questo modo il progetto è auto-contenuto e più facilmente portabile.

1. Creare un nuovo virtual environment (quello presente su SVN non funziona correttamente), lanciando da terminale il comando: ``python3 -m venv newenv``
2. Controllare se la variabile PYTHONPATH è vuota: ``echo $PYTHONPATH``
3. Se la variabile non è vuota, modificare lo script di attivazione ``./newenv/bin/activate`` per evitare conflitti, aggiungendo come prima riga del file: ``unset PYTHONPATH``
4. Attivare il virtual environment: ``source ./newenv/bin/activate``
5. Aggiornare pip (non usare mai sudo nel virtual environment): ``pip3 install -U pip``
6. Installare Django: ``pip3 install django``
7. Installare Asgiref: ``pip3 install asgiref``
8. In caso di problemi con Asgiref, installare il seguente pacchetto:

.. code-block::

    sudo apt install build-essential

9. Installare psycopg2: ``pip3 install psycopg2``
10. Installare FontAwesome: ``pip3 install fontawesome``
