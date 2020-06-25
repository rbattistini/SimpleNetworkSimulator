# A simple network simulation

Progetto realizzato per l'esame di *Programmazione di Reti*.

L'obiettivo è quello di simulare un'architettura Server-Router-Client come mostrato nella seguente immagine:

![A picture of the network](resources/server_router_client.png)

## Features

### Feature richieste

- Il server deve tenere traccia dei client che entrano e che escono dalla rete.

- Quando un client (attivo in rete) vuole inviare un messaggio ad un altro client, dovrà inviare il messaggio al server il quale consegnerà il messaggio al destinatario solo se il client destinatario è attivo, in alternativa restituirà un messaggio al mittente indicando che il client destinatario non è online.

- Gli headers IP ed Ethernet dovranno essere considerati nella versione semplificata ossia composti dai soli indirizzamenti IP e Mac Address

### Feature aggiuntive

- Le specifiche riguardanti le entità che formano il network sono memorizzate in un file di configurazione apposito. 
  Sono disponibili due versioni del network, `network_basic` è stato impiegato per i test iniziali mentre `network` rappresenta l'architettura richiesta dalla traccia. 
  In generale a ciascun router può essere legato un numero arbitrario di client.

- Le arp table dei router non contengono infomazioni relative ai client. Sono state perciò implementati i meccanismi di ARP request e ARP reply per permettere ai router di ricavare informazioni sull'indirizzo mac associato a ciascun client.

## Panoramica

L'interazione con l'utente avviene esclusivamente tramite terminale.
Si inseriscono degli identificativi numerici ai quali corrispondono i possibili comandi da eseguire.

Per la descrizione dei singoli comandi si rimanda alla sezione di aiuto accessibile a riga di comando.

Ogni comando effettuato provoca una serie di azioni che sono registrate su un file di log. Il nome di questo file è `messages.log`.

Per poter capire cosa accade nel corso della simulazione bisogna consultare quel file.

Per implementare l'architettura si è scelto di impiegare più thread.
In particolare ogni client al momento del lancio avrà un thread per l'ascolto dei messaggi. Lo stesso vale per il server.

Per quanto riguarda il router è necessario distinguere tra due casi:
- se si tratta del router principale, ovvero del router collegato direttamente al server, allora è creato un solo thread all'inizio per stabilire le connessioni con l'altro router e il server. Dopodiché qualsiasi interazione con il router richiede la creazione di un apposito thread. Il router mette a disposizione la possibilità di creare un thread per richiedere una connessione (creato dai client) e di creare una thread per inviare un messaggio (creato sia dagli host che dal router). Stabilita la connessione o inviato il messaggio il thread si chiude.
-  se si tratta del router secondario, ovvero del router collegato indirettamente al server, allora si crea un thread per l'ascolto dei messaggi da parte del router principale. In ogni caso i client per comunicare con il router creano un apposito thread.


## Avviare la simulazione

Per prima cosa si controlli se i requisiti sono rispettati.

Per lanciare la simulazione bisogna eseguire lo script principale `cli.py` 

In ambiente Unix, dopo aver lanciato il comando `chmod`, basta lanciare sul terminale:

`sudo ./cli.py`

Su Windows si può lanciare impiegando Idle ad esempio.

## Fermare la simulazione

Basta premere la combinazione di tasti `CTRL+C`, o alternativamente selezionare il comando `Quit` sul terminale.

In entrambi i casi sarà lanciata una procedura di pulizia che chiederà a tutti i thread attivi di terminare, con la garanzia che termineranno in breve tempo, e di chiudere le tutte le connessioni aperte.

Talvolta questa procedura potrebbe richiedere qualche secondo.

## Requisiti

Il programma è stato sviluppato con il seguente interprete Python:
Python interpreter 3.8.2 64-bit

L'unica libreria aggiuntiva richiesta è PyYAML per la lettura del file di configurazione,
può essere installata con il seguente comando:

`pip install pyyaml`