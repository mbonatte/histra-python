UNIVERSITÁ DEGLI STUDI DI PADOVA
DIPARTIMENTO DI INGEGNERIA CIVILE, EDILE E AMBIENTALE – I C E A
CORSO DI LAUREA MAGISTRALE IN INGEGNERIA CIVILE
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO
SISMICO DI EDIFICI ESISTENTI IN MURATURA
MODELLAZIONE NUMERICA DELLE PARETI
```
Studente: Nicola Bertin matr. 1057114
```
```
Relatore: Prof. Ing. Roberto Scotta
```
```
Correlatore: Ing. Davide Trutalli
```
ANNO ACCADEMICO 2014/2015
3
Sommario
1 INTRODUZIONE DELL’ELABORATO ............................................................................... 7
2 IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA .................................... 10
2.1 Gli elementi strutturali .................................................................................................... 10
2.2 Comportamento elementi orizzontali: fasce di piano ..................................................... 13
2.3 Comportamento elementi orizzontali: diaframmi di piano ............................................. 14
2.4 Comportamento elementi verticali: Pannelli murari sollecitati fuori piano ................... 15
2.5 Comportamento elementi verticali: Pannelli murari sollecitati nel proprio piano.......... 17
2.6 Criteri di resistenza per i diversi meccanismi di collasso nel proprio piano .................. 19
2.6.1 Meccanismo di schiacciamento/ribaltamento ......................................................... 20
2.6.2 Meccanismo di rottura a taglio per fessurazione diagonale.................................... 23
2.6.3 Meccanismo di rottura per scorrimento .................................................................. 27
2.7 L’utilizzo di tiranti per il rinforzo di strutture in muratura ............................................. 28
2.7.1 Contributo dei tiranti per l’aumento di resistenza nel piano................................... 29
2.7.2 Contributo dei tiranti per l’aumento di resistenza fuori dal piano .......................... 30
3 IL MACROMODELLO PROPOSTO .................................................................................... 32
3.1 Introduzione.................................................................................................................... 32
```
3.2 Elemento pannello (comportamento piano) ................................................................... 35
```
3.2.1 Elementi rigidi ........................................................................................................ 40
3.2.2 Taratura molle muratura ......................................................................................... 40
3.2.3 Comportamento flessionale .................................................................................... 41
3.2.4 Comportamento a taglio per fessurazione diagonale .............................................. 48
3.2.5 Comportamento a taglio-scorrimento ..................................................................... 56
4 CALIBRAZIONE MOLLE DELLA MURATURA .............................................................. 63
4.1 Dati generali della muratura ........................................................................................... 63
4.2 Modellazione e simulazioni numeriche .......................................................................... 68
4.2.1 Truss infinitamente rigidi ....................................................................................... 69
4.3 Calibrazione molle maschio murario.............................................................................. 70
4.3.1 Calibrazione molle assiali....................................................................................... 70
4
4.3.2 Calibrazione molle diagonali ................................................................................. 73
4.3.3 Calibrazione molle trasversali ................................................................................ 77
4.3.4 Validazione del singolo maschio murario .............................................................. 79
4.4 Calibrazione molle fascia di piano ................................................................................. 88
4.4.1 Valutazione tiranti .................................................................................................. 91
4.4.2 Calibrazione molle orizzontali spandrel................................................................. 94
4.4.3 Calibrazione molle diagonali spandrel ................................................................... 96
4.4.4 Calibrazione molle verticali spandrel..................................................................... 99
4.5 Calibrazione beam per il fuori piano............................................................................ 101
5 TIPOLOGIE DI RINFORZO DEI SOLAI E MODELLAZIONE ...................................... 105
5.1 Calibrazione dei solai ................................................................................................... 106
5.2 Brevi cenni sul solaio con doppio tavolato a 45° ......................................................... 108
5.2.1 Prova sperimentale solaio .................................................................................... 109
5.2.2 Modello Numerico del solaio ............................................................................... 109
5.3 Brevi cenni sul solaio con soletta in c.a. ...................................................................... 111
5.3.1 Prova sperimentale solaio .................................................................................... 112
5.3.2 Modello Numerico del solaio ............................................................................... 112
6 ESEMPIO PARETE DI 4.5m NEL PIANO X-Y ................................................................ 114
6.1 Molle Maschio Primo .................................................................................................. 117
6.2 Molle Fascia di Piano................................................................................................... 119
6.3 Molle Maschio Secondo............................................................................................... 121
6.4 Calibrazione molle diagonali superiori elastiche ......................................................... 123
6.5 Comportamento globale della parete ........................................................................... 125
7 CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m ........................................................... 126
7.1 Geometria della parete e del solaio .............................................................................. 128
7.2 Modello Time-History ................................................................................................. 130
7.2.1 Accelerogrammi usati .......................................................................................... 132
7.3 Caso studio 1a: edificio 4.5x5m con solaio flessibile .................................................. 134
7.3.1 Analisi dei carichi e masse sismiche .................................................................... 134
5
7.3.2 Time History......................................................................................................... 138
7.3.3 Comportamento globale della parete .................................................................... 139
7.4 Caso studio 1b: edificio 4.5x5m con solaio rigido ....................................................... 144
7.4.1 Analisi dei carichi e masse sismiche .................................................................... 144
7.4.2 Time History......................................................................................................... 146
7.4.3 Comportamento globale della parete .................................................................... 147
7.5 Conclusioni caso studio 1 ............................................................................................. 150
8 CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI .......................... 152
8.1 Geometria della parete e del solaio............................................................................... 155
8.2 Caso studio 2a: edificio di pianta 13.5x10m con solaio flessibile ................................ 158
8.2.1 Analisi dei carichi e masse sismiche .................................................................... 158
8.2.2 Analisi Time-History ............................................................................................ 163
8.2.3 Considerazioni del caso studio 2a ........................................................................ 182
8.2.4 Riepilogo dei risultati del caso studio 2a .............................................................. 184
8.3 Caso studio 2b: edificio di pianta 13.5x10m con solaio rigido .................................... 185
8.3.1 Analisi dei carichi e masse sismiche .................................................................... 185
8.3.2 Time History......................................................................................................... 187
8.3.3 Considerazioni del caso studio 2b ........................................................................ 208
8.3.4 Riepilogo dei risultati del caso studio 2b.............................................................. 210
8.4 Conclusioni del caso studio 2 ....................................................................................... 211
9 CONCLUSIONI ................................................................................................................... 217
9.1 Breve riepilogo della modellazione trattata .................................................................. 217
9.2 Considerazioni finali .................................................................................................... 220
9.3 Sviluppi futuri............................................................................................................... 222
RIFERIMENTI BIBLIOGRAFICI .............................................................................................. 224
INDICE DELLE FIGURE ........................................................................................................... 226
6
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
7
1 INTRODUZIONE DELL’ELABORATO
La numerosa presenza di edifici storici in muratura, anche di natura monumentale, sul
territorio nazionale ha portato, soprattutto negli ultimi anni, ad interventi di
ristrutturazione e riqualificazione del patrimonio architettonico italiano.
Le opere eseguite nel corso degli anni, hanno avuto come obiettivo il consolidamento
statico delle strutture per renderle idonee a resistere in sicurezza ai carichi statici indotti
dalle nuove destinazioni d’uso a cui gli edifici sono stati assoggettati.
In seguito agli eventi sismici che hanno colpito alcune regioni del nostro paese negli
ultimi anni è diventato sempre più attuale il tema del miglioramento sismico degli edifici
esistenti.
Le tecniche di miglioramento sismico applicate dai progettisti prevedono interventi di
consolidamento e irrigidimento nel piano degli orizzontamenti e delle strutture di
copertura allo scopo di assicurare una migliore distribuzione delle forze orizzontali tra gli
elementi murari sismo-resistenti.
Un ulteriore intervento che mira a migliorare la risposta sismica degli edifici esistenti
consiste nella solidarizzazione dei solai e delle strutture di copertura alla scatola muraria
allo scopo di eliminare i cinematismi fuori piano, problematica ricorrente che si è
manifestata in numerosi edifici colpiti dai recenti eventi sismici.
La composizione dei solai, in particolare la loro rigidezza di piano e il grado di
connessione alle murature perimetrali, è uno dei principali parametri che influenza la
risposta globale degli edifici in esame. Questo significa che il loro compito è quello di
stabilizzare le pareti investite dal sisma fuori piano ad evitare ribaltamenti delle stesse,
riportare alle pareti di controvento le azioni orizzontali e dissipare energia preservando il
più possibile le strutture murarie verticali.
È importante quindi la corretta progettazione degli interventi di consolidamento dei
diaframmi e in particolare la corretta valutazione della rigidezza da assegnare agli stessi
in modo da ottenere dei risultati verosimili. Questo risulta essere un dato assai incerto
confermato dalla molteplicità di valori sperimentali proposti nella letteratura specifica.
Ad oggi i professionisti non hanno a disposizione risultati scientifici per una corretta
valutazione della rigidezza nel piano dei solai lignei esistenti o rinforzati e
INTRODUZIONE DELL’ELABORATO
8
dell’interazione tra gli orizzontamenti o coperture e le murature d’ambito. Risulta
pertanto complicato esprimersi sull’efficacia di un intervento di consolidamento.
Il lavoro svolto non si pone come obiettivo la stima della rigidezza di piano dei solai, che
verrà desunta da valori sperimentali, ma bensì quello di studiare l’interazione tra i solai e
le murature d’ambito al variare della tipologia di intervento di consolidamento del solaio
con riferimento alle tecniche e ai materiali maggiormente impiegati e diffusi.
Il lavoro di tesi di seguito esposto analizzerà un edificio a pianta rettangolare
caratterizzato da differenti rigidezze dei diaframmi orizzontali. Nel presente elaborato
verrà analizzato in maggior dettaglio il comportamento della muratura. Il metodo
utilizzato per la modellazione della stessa è la modellazione a macroelementi, in quanto
ritenuto uno dei più vicini alla realtà.
Più nello specifico, è stato generato mediante Notepad++ una schematizzazione
opportuna che permette la costruzione di un modello strutturale tridimensionale di un
```
edificio a un piano con caratteristiche geometriche (lunghezza dei muri, lunghezza dei
```
singoli maschi murari e delle singole fasce di piano, lunghezza degli elementi del solaio e
```
lunghezza delle molle utilizzate) e strutturali (molle dei singoli elementi di muratura e
```
```
del solaio ligneo), entrambe ricavate dal confronto con dati di prove di laboratorio.
```
Successivamente, questo codice è stato introdotto nel programma di analisi sismica
OpenSees, software sviluppato da University of California, Berkeley per simulare le
prestazioni dei sistemi strutturali e geotecnici sottoposti a terremoti.
Per la calibrazione del modello, esso verrà analizzato per mezzo di analisi statiche non
```
lineari (Push-Over) e analisi cicliche. Il comportamento globale dell’edificio sottoposto
```
ad azione sismica verrà studiato mediante analisi dinamiche non lineari con impiego di
```
accelerogrammi (Time-History).
```
Il presente lavoro di tesi sarà poi ampliato con diverse tipologie di solaio nell’elaborato
di M. Tonon, dal titolo “Effetti del rinforzo di solai in legno nel miglioramento sismico di
edifici esistenti in muratura - modellazione numerica dei solai”.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
9
```
Come è descritto nella pubblicazione “Cyclic behaviour of brick masonry walls” (di G.
```
```
Magenes e G. M. Calvi):
```
“La valutazione della vulnerabilità sismica di costruzioni esistenti è stata riconosciuta
come uno dei maggiori problemi sia per l’elevato numero di costruzioni costruite prima
dello sviluppo di codici sismici razionali, sia per la bassa conoscenza delle proprietà dei
materiali utilizzati per una risposta sismica del singolo elemento e della struttura globale.
Quindi, è più importante che i modelli che verranno usati per la simulazione numerica di
```
queste costruzioni abbiano delle leggi costitutive raffinate per ogni elemento (strutturale
```
```
e di connessione) piuttosto che rappresentino l’esatta configurazione geometrica.”
```
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
10
2 IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
In questo capitolo vengono esaminati gli aspetti più significativi che intervengono nella
caratterizzazione della risposta di un edificio in muratura soggetto ad azioni sismiche. In
particolare si porrà in evidenza come i vari aspetti costruttivi condizionano in modo
rilevante il comportamento globale della struttura sia in termini di resistenza ultima che
in termini di meccanismo di collasso. Verranno inoltre descritti i principali meccanismi di
collasso di pannelli murari soggetti a forze orizzontali nel piano e fuoripiano.
2.1 Gli elementi strutturali
Nello studio di un edificio in muratura, più di qualsiasi altra tipologia costruttiva, è
fondamentale un attento esame delle caratteristiche meccaniche e costruttive di ciascun
elemento che compone la costruzione.
Nell’esaminare il comportamento strutturale dell’edificio è conveniente individuare
alcune parti fondamentali in cui si può immaginare convenzionalmente suddiviso
l’edificio. In una prima classificazione essenziale l’edificio può essere suddiviso in pareti
verticali ed orizzontamenti. Le pareti verticali a loro volta possono essere suddivise in
maschi murari e fasce di piano. Gli orizzontamenti possono essere piani oppure costituiti
da strutture voltate spingenti o a spinta eliminata dalla presenza di catene.
Nell’esaminare le strutture verticali, è inoltre di fondamentale importanza verificare la
qualità degli collegamenti tra muri trasversali in corrispondenza degli angoli, cantonali.
Gli orizzontamenti costituiscono un elemento essenziale perché sono il principale
elemento che influenza il comportamento globale della struttura.
La presenza di orizzontamenti di piano collegati efficacemente ai muri perimetrali serve
a garantire un comportamento cosiddetto “scatolare” dell’edificio limitando l’instaurarsi
di possibili meccanismi di ribaltamento delle pareti fuori dal proprio piano.
Chiaramente è inteso che un solaio anche se rigido, per assolvere a tale funzione, deve
essere efficacemente ammorsato alle pareti. Ecco che la presenza di cordoli di piano per
una struttura in muratura, soprattutto negli edifici di nuova progettazione, diviene un
elemento di importanza primaria.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
11
Nelle tipologie costruttive meno recenti è frequente l’uso di solai in legno o di
orizzontamenti realizzati mediante volte. La prima tipologia in molti casi riesce a
garantire un ammorsamento sufficiente soltanto in corrispondenza delle pareti su cui
risultano caricati i solai. Le pareti non direttamente caricate dai solai risultano invece
ammorsate alla struttura soltanto in corrispondenza dei cantonali e, in condizioni
sismiche, tale collegamento può in alcuni casi risultare inadeguato.
La presenza di orizzontamenti costituiti da strutture voltate in genere può garantire un
comportamento scatolare in condizioni sismiche soltanto se la spinta derivante dalle
azioni orizzontali delle volte risulta essere contrastata dalla presenza di catene
```
(altrimenti la presenza di strutture spingenti può, in alcuni casi, favorire il ribaltamento
```
```
fuori piano delle pareti su cui risultano ordite le volte).
```
La risposta delle pareti dell’edificio è fortemente condizionata dalla rigidezza delle fasce
di piano e dalla eventuale presenza di cordoli e/o architravi. La rigidezza, la resistenza e
la duttilità di queste, infatti, determinano le effettive condizioni di vincolo cui sono
soggetti i maschi murari.
E’ evidente che la presenza dei cordoli di piano oltre a garantire un comportamento
d’insieme dei maschi murari determina un sostanziale irrigidimento delle fasce di piano
che in assenza di cordoli risultano invece essere elementi su cui si concentra il
danneggiamento in seguito ad eventi sismici. In presenza di fasce rigide e resistenti il
danneggiamento si determina invece in corrispondenza dei maschi murari determinando
nel complesso un organismo strutturale più resistente, come si avrà modo di osservare
nei successivi capitoli.
Nella valutazione della vulnerabilità sismica di un edificio in muratura e nella definizione
di un modello strutturale per la simulazione della risposta dinamica in ogni caso non
bisogna prescindere da un attenta analisi della tipologia muraria e dei particolari
costruttivi allo scopo di individuare le possibili cause di innesco di meccanismi locali di
danno che negli edifici storici sono, in genere, la prima causa di collasso strutturale.
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
12
La resistenza sismica di un edificio in muratura il cui comportamento si può ritenere
scatolare è prevalentemente associata alla rigidezza, alla resistenza e alla duttilità delle
pareti nel proprio piano in quanto i meccanismi di ribaltamento delle pareti fuori piano e
```
di collasso parziale di porzioni superficiali dell’edificio (detti meccanismi di primo modo),
```
risultano in genere impediti dalla presenza di cordoli di piano o di catene.
In assenza di cordoli di piano e/o di incatenamenti sufficienti a garantire un
comportamento d’insieme delle pareti, caratterizzati da ampie pareti libere, le principali
cause del collasso strutturale in seguito ad eventi sismici sono dovute all’innescarsi dei
cosiddetti meccanismi di primo modo che nella maggior parte dei casi determinano
collassi parziali di porzioni anche significative dell’edificio.
E’ chiaro che vi possono essere situazioni intermedie in cui i meccanismi di collasso delle
pareti fuori piano sono conseguenti a un progressivo danneggiamento delle pareti e
degli ammorsamenti in corrispondenza dei cantonali durante l’evoluzione della risposta
sismica.
Per quanto detto, nell’esaminare il comportamento delle pareti murarie è importante
distinguere il caso di pareti sollecitate nel proprio piano e il caso di pareti sollecitate
fuori-piano. Nel seguito verrà brevemente descritto il differente comportamento della
muratura in relazione alla direzione della sollecitazione e alle condizioni di vincolo della
parete stessa.
Si può comunque facilmente individuare anche in un edificio in muratura tre principali
elementi costruttivi sismo resistenti:
- Elementi orizzontali: fasce di piano;
- Elementi orizzontali: diaframmi di piano (solai);
- Elementi verticali: maschi murari.
Tali elementi risultano essere di fatto i componenti che governano il comportamento
globale della struttura unitamente al grado di connessione tra essi.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
13
2.2 Comportamento elementi orizzontali: fasce di piano
La risposta sismica di strutture in muratura semplice è influenzata dal comportamento
```
delle fasce di piano (nell’elaborato questi elementi sono chiamati “spandrel”), come
```
```
dimostrato anche da simulazioni numeriche e di osservazione post-terremoto (Magenes
```
```
et al.). Fino a poco tempo fa, la comprensione del comportamento sismico di queste
```
componenti strutturali non era supportata da adeguate campagne sperimentali. Solo
negli ultimi anni sono stati effettuati alcuni programmi sperimentali con lo scopo di
studiare il comportamento ciclico di travi di muratura, realizzate in mattoni o blocchi
forati in piano.
```
Il termine fascia di piano (o trave in muratura) definisce la porzione di muro che collega
```
due moli adiacenti attraverso un'apertura. Questi elementi risultano spesso danneggiati
durante un evento sismico e, in generale, sono i primi componenti strutturali in cui si
```
formano crepe in edifici di muratura non rinforzata (URM). Gli elementi spandrel
```
influenzano significativamente le caratteristiche forza/deformazione di una struttura in
muratura per la loro azione di inquadratura e accoppiamento. Riconoscendo che i
maschi murari sono gli elementi più importanti sia per portare il carico verticale che per
la resistenza all'azione sismica, non è tuttavia generalmente corretto trascurare la
presenza di questi elementi e il loro ruolo che permette di aumentare la rigidezza. Le
prestazioni di una parete multipiano potrebbero cambiare significativamente a causa del
```
comportamento delle fasce di piano. Un'analisi (classica) avente come ipotesi quella di
```
trascurare il contributo delle travi di muratura sulla rigidezza globale, potrebbe portare a
sottovalutare o sopravvalutare la capacità dell’intero sistema strutturale.
Figura 2-1: Effetto del diverso grado di accoppiamento fornito dalle travi di muratura
```
sulla distribuzione dei momenti: fasce flessibili (a), intermedie (b) e rigide (c) (Tomaževič,
```
```
1999)
```
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
14
La figura 2.1 mostra che un diverso grado di accoppiamento offerto dalle fasce di piano
può introdurre un comportamento strutturale completamente diverso in termini di
taglio, diagrammi di momento e meccanismo di collasso. In particolare, la figura mostra
```
le due condizioni estreme (ideali) di fasce infinitamente flessibili (a) e infinitamente
```
```
rigide (c), corrispondenti rispettivamente a meccanismi di tipo mensola (collegati da
```
```
bielle) e di tipo telaio.
```
2.3 Comportamento elementi orizzontali: diaframmi di piano
I diaframmi orizzontali, come anticipato, hanno il compito di ridistribuire la forza sismica
tra gli elementi resistenti verticali e tale capacità dipende notevolmente dalla tipologia
di solaio presente nell’edificio. Una principale divisione in due macro categorie di solaio
può essere eseguita in funzione alla loro rigidezza di piano o tagliante, distinguendo
```
quindi:
```
- Solai rigidi
- Solai flessibili
```
La presenza in una struttura muraria di diaframma rigido (ad esempio con soletta in CLS
```
```
o lignea) permette le adeguate connessioni tra elementi verticali e il comportamento
```
“scatolare” della struttura, ridistribuendo la forza sismica orizzontale in maniera
proporzionale alla rigidezza degli elementi resistenti. Questo comporta di conseguenza
che l’elemento verticale più rigido assorba una maggiore aliquota di sforzo orizzontale
rispetto agli altri.
```
Diversamente un diaframma flessibile (ad esempio un solaio ligneo semplice) non
```
garantisce più la risposta globale della struttura all’azione simica, presentando un
comportamento analogo ad una trave in appoggio con deformabilità flessionale e
tagliante allo stesso tempo.
Gli appoggi vengono considerati non cedevoli in quanto gli elementi resistenti verticali
hanno rigidezza ben maggiore se comparata a quella del solaio. La ridistribuzione delle
forze orizzontali tra gli elementi verticali avviene in funzione di un’area di influenza e il
comportamento del solaio sarà, in termini di spostamenti, amplificato rispetto a quello
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
15
delle murature le quali rispondono direttamente all’accelerazione agente. Inoltre un
solaio di tale tipo non è in grado di distribuire le azioni torsionali che si generano quando
il centro di taglio non coincide con il centro di massa dell’edificio.
Figura 2-2: Influenza delle connessioni tra gli elementi
2.4 Comportamento elementi verticali: Pannelli murari sollecitati fuori
piano
Il meccanismo di collasso fuori piano è da riferirsi a fenomeni locali innescati da azioni
ortogonali agli elementi murari. Infatti, i pannelli murari offrono una minore resistenza
alle azioni ortogonali. Questo è dovuto oltre alla bassa resistenza del materiale, anche
alla mancanza di collegamenti lungo il perimetro dell’elemento e tra gli elementi stessi.
Questo comporta la presenza di un unico vincolo alla base della muratura così da indurre
un comportamento di corpo rigido o un comportamento flessionale tipo trave.
I principali meccanismi di collasso fuori piano sono:
- Ribaltamento
- Ribaltamento composto
- Flessione verticale
- Flessione orizzontale
L’osservazione dei danni in edifici in muratura a seguito di vari eventi sismici, ha
confermato che meccanismi locali di ribaltamento fuori piano si attivano molto spesso
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
16
per azioni orizzontali ben inferiori alle capacità resistenti nel piano, coinvolgendo nel
movimento intere pareti, porzioni di pannelli, parti sommitali ed angolate in funzione
della configurazione geometrica, dei vincoli e delle azioni sollecitanti. Allo stesso tempo
è stato verificato che la presenza di buoni collegamenti tra gli elementi resistenti
verticali ed orizzontali realizzati secondo regole di buona pratica costruttiva hanno
spesso evitato questo meccanismo di rottura.
Figura 2-3: Esempio di collasso per ribaltamento
Figura 2-4: Esempio di collasso per flessione verticale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
17
Figura 2-5: Diversa risposta sismica degli edifici in muratura
2.5 Comportamento elementi verticali: Pannelli murari sollecitati nel
proprio piano
Nello studio di pannelli murari soggetti a forze orizzontali vengono, in genere, presi in
considerazione due condizioni di vincolo della sezione di testa: il caso di estremo
superiore libero e il caso di estremo superiore impedito di ruotare. Questi
rappresentano due casi limite della reale condizione di vincolo dei pannelli inseriti in uno
schema strutturale complesso.
Si distinguono tre principali meccanismi di collasso nel proprio piano:
- rottura per schiacciamento/ribaltamento
- rottura a taglio per fessurazione diagonale
- rottura per scorrimento
Nel seguito verrà fornita una descrizione di detti meccanismi. Verranno altresì esposti
alcuni criteri di rottura presenti in letteratura che consentono di valutare la resistenza di
pannelli murari isolati.
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
18
Figura 2-6: Esempi di rottura per fessurazione diagonale, flessione, scorrimento
Nel caso che il pannello si trovi inserito in un edificio, oltre all’uso di tali criteri di rottura,
diviene di fondamentale importanza valutare in maniera corretta il tipo di vincolo che il
resto della struttura offre al pannello in esame.
```
Pannelli murari caratterizzati da bassi valori del rapporto B/H (pareti snelle) e soggetti a
```
piccoli carichi assiali presentano una risposta di tipo prevalentemente flessionale. Nel
collasso di tali pareti il fenomeno della parzializzazione della sezione ha un ruolo
primario e si perviene a un meccanismo di rottura per schiacciamento e/o ribaltamento.
```
Nel caso di pareti tozze o soggette ad elevati carichi assiali (per esempio i maschi murari
```
```
dei piani bassi di un edificio) il comportamento è fondamentalmente di tipo tagliante. In
```
questo caso la parzializzazione della sezione è fortemente limitata dalla
precompressione dovuta al carico assiale e viene evidenziata la deformabilità a taglio.
La risposta di una parete che presenta un comportamento di tipo flessionale è
caratterizzata da cicli di isteresi molto stretti. Al limite, se il pannello murario viene
schematizzato come un corpo rigido e il suolo come un vincolo elastico unilatero, si
ottiene un comportamento elastico non-lineare, caratterizzato da un ciclo di isteresi
nullo. Sperimentalmente è inoltre possibile osservare come all’aumentare del numero di
cicli non si ha un sensibile degrado di rigidezza o di resistenza.
In un pannello in cui nella risposta complessiva la componente di tipo tagliante risulta
prevalente rispetto a quella flessionale, si riscontrano cicli di isteresi piuttosto contenuti
```
fino al raggiungimento di un valore di picco della forza (Vmax), in corrispondenza del
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
19
quale, come verrà meglio descritto nei capitoli successivi, avviene la formazione di
fessure diagonali. Oltre tale valore si osserva un significativo degrado sia della rigidezza
che della resistenza e cicli di isteresi molto ampi.
Nelle figure sottostanti sono rappresentati i due diversi comportamenti appena descritti.
```
Figura 2-7: Tipi di comportamento di un pannello; (a) snello; (b) tozzo.
```
2.6 Criteri di resistenza per i diversi meccanismi di collasso nel proprio
piano
I meccanismi di collasso di un pannello murario sollecitato nel proprio piano, come detto
all’inizio del presente paragrafo, sono essenzialmente di tre tipi:
- schiacciamento/ribaltamento,
- rottura a taglio per scorrimento,
- rottura a taglio per fessurazione diagonale.
Dal punto di vista del quadro fessurativo tali meccanismi risultano molto diversi tra loro.
Nel caso di collasso per flessione, le fessure sono concentrate in corrispondenza delle
sezioni estreme incastrate, in prevalenza si assisterà a fessure per trazione, più rari i
fenomeni di plasticizzazione per compressione.
Nel caso di rottura per fessurazione diagonale si assisterà alla formazione di due evidenti
fessure diagonali.
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
20
Infine nel caso di collasso per scorrimento le fessure si concentreranno lungo i giunti di
malta in corrispondenza di uno dei lati del pannello.
In figura sottostante sono riportati i tre possibili meccanismi di collasso appena citati.
```
Figura 2-8: Meccanismi di collasso nel piano: pressoflessione (a), taglio-fessurazione
```
```
diagonale (b), taglio-scorrimento (c)
```
2.6.1 Meccanismo di schiacciamento/ribaltamento
Le forze orizzontali agenti sul pannello murario inducono un momento flettente che
varia linearmente lungo l’altezza della parete. Questo produce tensioni normali di
compressione e di trazione. Tali sollecitazioni risultano massime in corrispondenza delle
sezioni di estremità della parete.
Se le tensioni di compressione superano la resistenza a compressione della muratura si
verifica uno schiacciamento in corrispondenza della parte compressa della sezione
trasversale della parete.
Pur non pervenendo allo schiacciamento della muratura, può verificarsi il ribaltamento
del pannello, o di una porzione di esso, a causa della progressiva parzializzazione della
sezione che porta l’asse neutro in prossimità del bordo compresso con un progressivo
degrado della rigidezza fino all’incapacità di sostenere ulteriori incrementi di carico. Per
quanto riguarda il meccanismo di schiacciamento, la formulazione di un criterio di
rottura risulta abbastanza semplice. A tale scopo si consideri un pannello caricato da uno
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
21
sforzo assiale costante P eccentrico rispetto all’asse geometrico e da una forza di taglio
V.
Figura 2-9 : Pannello caricato da sforzo normale eccentrico e forza orizzontale
Si immagini di modellare la muratura come un materiale elastico lineare fino alla rottura
a compressione e non reagente a trazione. Ammettendo tali ipotesi la condizione di
rottura coincide con il raggiungimento della tensione massima ammissibile a
```
compressione (σc) in corrispondenza dello spigolo del pannello. La distribuzione di
```
tensioni lineare, per semplicità, viene qui sostituita con una distribuzione uniforme di
intensità ridotta, come riportato in figura sopra. Imponendo l’equilibrio alla rotazione
attorno al punto medio della sezione di base, si ha:
```
( )
```
```
essendo:
```
- σc la resistenza a compressione della muratura;
- H0 l’altezza del punto di nullo del diagramma del momento flettente;
- P il carico normale agente sul pannello;
- B, H e t rispettivamente larghezza, altezza e spessore della parete;
- p la tensione media di compressione p=P/B*t;
- einf,u l’eccentricità del risultante dei carichi nella sezione di base del pannello
nella condizione limite di schiacciamento.
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
22
Da questa espressione è possibile ricavare il taglio che determina lo schiacciamento:
```
( )
```
Nella quale è stato posto αv = H0/B. Tale parametro prende il nome di coefficiente di
taglio e costituisce una misura del grado di vincolo opposto dal resto della struttura nei
confronti del pannello. Tuttavia è possibile prevedere modelli costitutivi più complessi,
come ad esempio un legame di tipo parabola-rettangolo a compressione e limitata
resistenza a trazione.
Il meccanismo di ribaltamento di un pannello può avvenire secondo modalità differenti a
seconda della qualità della malta. Nel caso di una muratura realizzata con malta di
buone caratteristiche il pannello si comporta come un blocco rigido che ruota intorno a
```
uno spigolo di base (in figura sottostante, caso a). In presenza di malta di qualità
```
scadente o in totale assenza di questa e nel caso di pannelli tozzi, come mostrato da
studi sperimentali su murature di blocchi squadrati, il collasso avviene attraverso il
distacco e la rotazione di una porzione di parete delimitata da una direzione inclinata.
Gli studi condotti hanno mostrato come l’angolo di inclinazione α di tale direzione
dipende dalla geometria della parete e dalla tessitura dei mattoni. Ovviamente il
verificarsi di tali meccanismi parziali riduce il taglio ultimo del pannello murario.
```
Figura 2-10: Meccanismi di ribaltamento nel piano: (a) globale da blocco rigido; (b) e (c)
```
parziali.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
23
Il valore del taglio ultimo per ribaltamento si può calcolare risolvendo un problema di
analisi limite. Considerando meccanismi parziali come quelli indicati nelle figure b e c è
possibile calcolare il moltiplicatore a collasso al variare dell’angolo α. Il minimo di tali
moltiplicatori costituisce l’effettivo moltiplicatore a collasso.
In aggiunta alla rotazione rigida, è possibile tener conto in maniera semplificata di un
parziale schiacciamento della muratura considerando come centro di rotazione,
rientrato 5 – 10 cm rispetto allo spigolo.
2.6.2 Meccanismo di rottura a taglio per fessurazione diagonale
Il meccanismo di rottura a taglio per fessurazione diagonale si realizza quando le
sollecitazioni di taglio provocano la formazione di fessure diagonali che partono dalla
zona centrale del pannello per poi estendersi. La formazione di tali fessure si determina
in corrispondenza delle direzioni principali cui corrispondono le massime tensioni di
compressione, in quanto alla direzione ortogonale sono associate le trazioni massime.
Figura 2-11: rottura per taglio-fessurazione diagonale di edifici esistenti in muratura
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
24
Uno dei criteri presenti in letteratura per valutare la capacità ultima a taglio di una
parete è dovuto a Turnsek e Cacovic. Scaturito dall’osservazione dei risultati di diverse
prove sperimentali, tale criterio si basa sull’assunzione che la rottura avviene quando la
tensione principale di trazione, nella zona centrale del pannello, eguaglia la resistenza a
trazione della muratura.
La formula che esprime tale criterio si ricava facilmente, ammettendo una distribuzione
parabolica delle tensioni tangenziali lungo la sezione del pannello, con valore massimo
pari a 1.5*V/A in corrispondenza dell’asse baricentrico. Da semplici considerazioni sullo
stato tensionale, si ricava infatti l’espressione della tensione principale di trazione in
corrispondenza proprio dell’asse del pannello, di seguito riportata:
```
√ √( ) ( )
```
```
essendo:
```
- σt la tensione principale di trazione;
- P lo sforzo normale agente sul pannello;
- p la pressione media;
- V il taglio agente;
- B e t la base e lo spessore del pannello;
- A=B*t la sezione trasversale.
A questo punto eguagliando tale espressione con la resistenza convenzionale a trazione,
l’espressione del taglio ultimo assume la forma:
√
Il termine σtu rappresenta la resistenza a trazione della muratura. Tale parametro in
linea teorica è una grandezza locale, anche se in quest’ambito deve essere interpretato
come un parametro di tipo globale. Per marcare il carattere macroscopico e non locale
del parametro σtu, questo spesso viene indicato come resistenza convenzionale a
trazione.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
25
L’espressione soprariportata viene spesso riscritta in funzione di τk che rappresenta la
```
tensione tangenziale media in condizioni ultime (Vd/A) in assenza di sforzo normale, e
```
non in termini di σtu.
```
E’ facile notare che tali parametri sono legati dalla relazione τk=σtu/1.5; la formula
```
precedente diviene quindi:
√
Il parametro τk presenta il vantaggio di avere un riscontro fisico più immediato rispetto
alla tensione convenzionale a trazione. Se ad esempio si esegue una prova di taglio su un
```
campione di muratura (in assenza di sforzo normale), basta dividere il valore del taglio
```
ultimo che si registra per la sezione trasversale del pannello esaminato e si determina τk.
Successivamente fu proposto da Turnsek e Sheppard di sostituire al fattore 1.5 presente
nelle formule soprariportate un parametro b dipendente dal rapporto geometrico B/H
del pannello.
In sostituzione delle formule sopra si ha, quindi:
√
√
Tra tutti i criteri presenti in letteratura per la determinazione del parametro b, qui si cita
quello dovuto a Benedetti e Tomazevic:
- b = 1 per H/B < 1 ;
- b = H/B per 1 < H/B < 1.5 ;
- b = 1.5 per H/B > 1.5 .
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
26
Più recentemente, un criterio di rottura alternativo per murature di blocchi squadrati è
stato proposto da Magenes e Calvi. In tale formulazione viene distinto il caso di
```
fessurazione diagonale dovuta al cedimento dei giunti di malta (taglio ultimo V1) e il caso
```
```
di fessurazione diagonale per rottura dei mattoni (taglio ultimo V2):
```
```
(̅ )
```
```
( ) √̅
```
Nelle quali:
- fbt indica la resistenza a trazione dei mattoni;
- B, t la base e lo spessore della parete;
- c, μ coesione e coefficiente di attrito della malta;
- αv = H0/B; con H0 il punto di nullo del diagramma dei momenti;
- β = è un coefficiente che può essere assunto da 2 a 3.
Si noti come l’espressione di V2, relativa al caso di rottura dei mattoni, sia l’equivalente
dell’espressione di Cacovic nella quale è stato introdotto il coefficiente di taglio αv che
dipende dalla condizione di vincolo del pannello. Inoltre nell’espressione sopra, la
resistenza a taglio è legata esclusivamente alla resistenza dei mattoni proprio perché si
suppone che siano questi a giungere a rottura.
Nel caso di muratura in pietrame è comunque preferibile continuare a utilizzare le
formule iniziali nelle quali è possibile introdurre un parametro convenzionale di
resistenza.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
27
2.6.3 Meccanismo di rottura per scorrimento
Il meccanismo di rottura per scorrimento si realizza in seguito alla formazione di piani di
scorrimento lungo i letti di malta nelle sezioni di estremità della parete.
Figura 2-12: rottura per taglio-scorrimento di edifici esistenti in muratura
Il criterio di rottura tradizionalmente utilizzato è quello di Mohr-Coulomb. Secondo tale
criterio, la tensione tangenziale ultima viene espressa come somma di un termine
```
costante c (coesione) e di un termine proporzionale alla tensione di compressione media
```
nella sezione :
```
(̅ )
```
Il coefficiente di proporzionalità μ prende il nome di coefficiente di attrito.
Al fine di determinare il taglio ultimo corrispondente, è possibile supporre una
```
distribuzione uniforme e integrare l’equazione su tutta la zona di contatto (B’*t). Si
```
ottiene l’espressione:
```
( )
```
che fornisce il taglio che determina lo scorrimento della parete.
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
28
2.7 L’utilizzo di tiranti per il rinforzo di strutture in muratura
I contenuti del presente paragrafo sono presi dal sito darioflaccovio.it.
I tiranti in acciaio costituiscono una delle tecniche di consolidamento più antiche ed
efficaci per rinforzare gli edifici in muratura. Poiché spesso gli edifici in muratura sono
antichi, sono soggetti anche al vincolo da parte della sovrintendenza, solitamente restia
```
a molte delle tecniche di consolidamento note in letteratura (soprattutto se prevedono
```
```
l’uso di calcestruzzo). In questi casi una delle tecniche che ottiene spesso il parere
```
favorevole della sovrintendenza è quella con tiranti metallici.
Le applicazioni dei tiranti sono molteplici:
- per incrementare la resistenza di una parete nel proprio piano;
- per ridurre la possibilità di ribaltamento fuori dal piano;
- per ridurre le spinte statiche di strutture spingenti (archi, volte, tetti, ecc.).
I pregi dei tiranti:
- sono semplici da mettere in opera;
- non alterano lo stato tensionale delle costruzioni;
- sono anche relativamente economici;
- non richiedono manodopera specializzata.
I tiranti sono elementi metallici costituiti da un cavo e da una chiave. Il tirante entra in
```
funzione quando sottoposto a sforzi di trazione (si può verificare per esempio quando
```
```
una parete tende a ribaltare). Affinché il sistema sia in equilibrio, il cavo del tirante deve
```
essere in grado di sopportare la forza di trazione a cui viene sottoposto. Tale forza viene
trasmessa alla chiave, la quale essendo a contatto con la muratura deve essere in grado
di sopportare la tensione di contatto tra la chiave e muratura. Infine anche la muratura
```
deve resistere alle azioni trasmesse dalla chiave (occorre evitare il distacco della parte di
```
```
muratura a contatto con la chiave).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
29
In definitiva, data una forza di trazione a cui deve essere sottoposto il tirante, il sistema
```
si mantiene in equilibrio se resiste il cavo (Tt), se resiste la muratura (Tm) e se resiste la
```
```
chiave (Tc).
```
In altri termini la resistenza del sistema tirante è data dal valore minimo delle tre
precedenti quantità:
```
( )
```
In un progetto di consolidamento, l’obiettivo è quello di incrementare gli indicatori di
rischio di una costruzione. In altri termini, edifici carenti dal punto di vista della
resistenza nei confronti delle azioni esterne devono essere consolidati per aumentarne
la resistenza.
```
Le verifiche che generalmente si fanno per edifici in muratura sono di tipo globale (si
```
analizza la struttura nel suo complesso dove tutti gli elementi contribuiscono in funzione
```
della propria resistenza) e di tipo locale (le singole pareti si considerano a sé stanti e se
```
```
ne valuta la resistenza in funzione della azioni esterne che ci gravano). A differenza di
```
```
altre tecniche di consolidamento (alcune sono adatte per incrementare la resistenza dal
```
punto di vista dell’analisi globale, altre invece sono adatte per incrementare quella
```
dell’analisi locale), i tiranti possono essere utilizzati per incrementare sia la resistenza di
```
analisi di tipo globale che locale.
2.7.1 Contributo dei tiranti per l’aumento di resistenza nel piano
I tiranti costituiscono un’ottima tecnica di consolidamento per incrementare la
resistenza di una parete nel proprio piano. Nel caso in cui la parete è priva di tiranti, il
```
comportamento può essere assimilato a quello riportato in a) di figura sottostante,
```
```
mentre se presenti i tiranti, a quello riportato in b) della stessa figura.
```
IL COMPORTAMENTO SISMICO DI EDIFICI IN MURATURA
30
Figura 2-13: Comportamento nel piano della parete senza e con tiranti
In assenza di tiranti il comportamento della parete è assimilabile a quello a mensola,
mentre se presenti, il comportamento è assimilabile a quello di un telaio.
I tiranti cambiano radicalmente il comportamento di una parete nel proprio piano,
```
tendendo a ridurre le sollecitazioni nei maschi murari (generalmente i momenti flettenti
```
```
sono molto più contenuti). Di contro aumentano le sollecitazioni nelle fasce di piano le
```
quali devono essere sottoposte a verifica.
2.7.2 Contributo dei tiranti per l’aumento di resistenza fuori dal piano
I tiranti costituiscono un’ottima tecnica di consolidamento anche per le verifiche fuori
dal piano di una parete. È intuitivo immaginare il migliore comportamento della parete
quando consolidata con tiranti. A titolo di esempio, se l’edificio non presenta il
consolidamento, sotto gli effetti dinamici ogni parete tende a ruotare
indipendentemente rispetto alle altre assumendo un cosiddetto comportamento “a
```
carciofo” (vedi a) di figura sottostante), mentre la presenza del consolidamento implica
```
```
uno spostamento tendenzialmente uniforme e unidirezionale per tutti gli elementi (vedi
```
```
b) della stessa figura).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
31
Figura 2-14: Comportamento fuori piano della parete con e senza tiranti
I tiranti contribuiscono a migliorare diverse tipologie di meccanismi locali, in particolare:
- a ribaltamento semplice
- a flessione verticale
- a flessione orizzontale
- a ribaltamento composto
- a ribaltamento del timpano.
Per ognuna di queste tipologie di meccanismo, il consolidamento contribuisce,
attraverso delle forze stabilizzanti la cui entità è funzione delle dimensioni degli stessi
tiranti, ad aumentare gli indicatori di rischio e quindi a ridurre la vulnerabilità
dell’edificio. In altri termini, attraverso la verifica si valuta la resistenza necessaria per
raggiungere un determinato valore dell’indicatore di rischio e si progettano di
conseguenza le varie parti del tirante.
IL MACROMODELLO PROPOSTO
32
3 IL MACROMODELLO PROPOSTO
3.1 Introduzione
Hilsdorf in un suo report del 1972 definisce la muratura come un “materiale composto
con proprietà diverse da quelle dei componenti”. Tale definizione appare tra le più
appropriate in quanto con il termine muratura ci si riferisce genericamente a tutte le
possibili tipologie di manufatti murari le cui caratteristiche geometriche, meccaniche e
costitutive rivestono un’ampia variabilità che produce differenze di comportamento
anche significative. Ciò che tuttavia è comune a tutte le tipologie murarie, se assimilate
ad una materiale composto, è la scarsa resistenza a trazione rispetto alla resistenza a
compressione e tale caratteristica ha caratterizzato nel corso dei secoli l’architettura
degli edifici in muratura la cui evoluzione più recente è stata fortemente condizionata
dall’introduzione del calcestruzzo armato.
L’interesse strutturale verso le murature può essere associato sia a ragioni storiche e di
rilievo architettonico, orientate alla comprensione e allo studio delle tecniche costruttive
del passato, che a ragioni più propriamente computazionali, rivolte alla definizione di
modelli numerici per la simulazione della risposta statica e dinamica di una costruzione
con struttura portante in muratura. I due aspetti sebbene apparentemente diversi sono
in realtà intimamente connessi. Infatti, in un edificio in muratura gli aspetti costruttivi,
rivestono un’importanza fondamentale nella definizione di un modello strutturale
attendibile. Pertanto, quando ci si riferisce ad edifici esistenti, oltre alla caratterizzazione
meccanica della muratura, che può essere basata sui risultati di indagini sperimentali,
assume un ruolo fondamentale il rilievo di dettaglio del manufatto murario con
particolare attenzione alla tessitura muraria, ai collegamenti tra i muri trasversali, alla
rigidezza e alla qualità degli orizzontamenti, alla presenza di architravi o cordoli, alla
presenza di strutture spingenti e di eventuali catene, alle trasformazioni che hanno
interessato l’edificio nel corso degli anni, etc.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
33
Nella definizione di un modello numerico orientato alla simulazione della risposta statica
e dinamica di un edificio in muratura generalmente si considera la muratura come un
solido omogeneo le cui caratteristiche devono essere tali da poter rappresentare una
porzione di muratura nel suo insieme prescindendo dalla eterogeneità della tessitura
muraria. Pertanto una caratterizzazione meccanica di un solido murario, attraverso dei
parametri significativi di rigidezza e resistenza, è da intendersi come rappresentativa di
un comportamento di insieme di un solido ideale pensato omogeneizzato. La scelta del
modello da adottare non può prescindere da una conoscenza di dettaglio dell’edificio ed
è strettamente legata ai meccanismi di crisi che s’intendono simulare.
In una modellazione in cui si analizza esclusivamente il comportamento del maschio
murario nel proprio piano vengono ignorati i meccanismi di crisi per ribaltamento della
```
muratura fuori dal piano, nonostante questi in molti casi (soprattutto per gli edifici
```
```
storici), risultino i meccanismi di collasso più probabili nel caso di un evento sismico.
```
La scelta di un modello inappropriato per la modellazione del comportamento sismico di
un edificio in muratura può condurre a risultati palesemente errati ed orientare la
progettazione strutturale ad interventi di rinforzo che in alcuni casi possono anche
risultare inutili o addirittura peggiorativi.
Prendendo spunto dalle modellazioni semplificate esistenti, nella tesi viene proposto un
macro-elemento piano per lo studio degli edifici in muratura. Questo modello
bidimensionale, pensato per lo studio della risposta delle murature nel proprio piano, è
costituito da un quadrilatero articolato i cui vertici incernierati sono collegati da molle
diagonali non lineari e i cui lati sono collegati agli altri macro-elementi mediante delle
interfacce costituite da un numero finito di molle non lineari con limitata resistenza a
trazione.
Nella sua definizione piana tale macromodello si colloca come miglior compromesso tra i
```
metodi semplificati tradizionali (modelli a telaio), e i metodi accurati (elementi finiti non
```
```
lineari), coniugando i vantaggi dell’uno e dell’altro.
```
IL MACROMODELLO PROPOSTO
34
```
Figura 3-1: Il macro-elemento di base per la modellazione della muratura: (a)
```
```
configurazione indeformata; (b) configurazione deformata (“Manuale teorico”)
```
Il macro-elemento piano ha tuttavia il limite di non considerare contestualmente
l’instaurarsi di eventuali meccanismi di primo modo associati al collasso fuori-piano delle
pareti.
La modellazione proposta è stata implementata per mezzo del software di calcolo
OpenSees, programma sviluppato da University of California, Berkeley per simulare le
prestazioni dei sistemi strutturali e geotecnici sottoposti a terremoti. Il codice di calcolo
consente l’implementazione del macro-elemento in campo statico e dinamico non-
lineare.
Nel presente elaborato, sono state effettuate analisi statiche e dinamiche non lineari
con riferimento a casi studio che sono stati oggetto di ricerca teorica e sperimentale. In
particolare per la taratura delle molle e per la verifica del comportamento dell’intero
maschio murario si sono confrontati i dati sperimentali ricavati da ricerche
```
dell’Università degli Studi di Pavia (“Cyclic behaviour of brick Masonry walls” di Magenes
```
```
e Calvi).
```
Recentemente questo nuovo approccio di modellazione per macro-elementi,
implementato nel software 3DMacro, è stato applicato sia in ambito professionale che
accademico.
Per il dimensionamento dei singoli elementi e per la parte teorica usata nel presente
elaborato di tesi ci si riferisce al “Manuale Teorico 3DMacro” del Gruppo Sismica S.R.L. .
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
35
```
3.2 Elemento pannello (comportamento piano)
```
Il modello concepito per la simulazione del comportamento delle murature quando
sollecitate nel proprio piano è rappresentato da un modello meccanico equivalente in
cui una porzione di muratura viene schematizzata mediante un quadrilatero articolato i
cui vertici sono collegati da molle diagonali non lineari e i cui lati rigidi interagiscono con
```
i lati degli altri macro-elementi (o con altri elementi) mediante delle interfacce discrete
```
con limitata resistenza a trazione.
Figura 3-2: Interazione tra un pannello e gli elementi limitrofi mediante letti di molle
```
(“Manuale teorico”)
```
Pertanto il modello si può pensare suddiviso in due elementi principali: un elemento
pannello costituito dal quadrilatero articolato e da un elemento di interfaccia costituito
da un insieme discreto di molle che determinano l’interazione non lineare con i
quadrilateri eventualmente adiacenti o con i supporti esterni.
```
Figura 3-3: Pannello (“Manuale teorico”)
```
Le molle diagonali dell’elemento pannello hanno il compito di simulare la deformabilità
a taglio della muratura.
IL MACROMODELLO PROPOSTO
36
```
Figura 3-4: molle trasversali e molle a scorrimento (“Manuale teorico”)
```
Le molle non lineari, nel loro insieme, dovranno simulare i meccanismi di collasso della
muratura nel proprio piano. Il numero delle molle in ciascuna interfaccia è arbitrario, e
```
viene scelto in base al grado di dettaglio della soluzione che si intende ottenere; è
```
importante notare che all’aumentare del numero di molle non corrisponde un aumento
```
del numero di gradi di libertà necessari alla descrizione della cinematica del sistema;
```
tuttavia aumenta l’onere computazionale associato alla non linearità delle molle stesse.
La figura sopra riporta uno schema meccanico relativo al comportamento piano
dell’interfaccia. In esso si può osservare una fila di molle ortogonali all’interfaccia e la
molla trasversale per la modellazione dello scorrimento nel piano.
È importante sottolineare che non vengono formulate ipotesi a priori né sulla
dislocazione degli elementi di interfaccia, né sui lati lungo i quali un pannello può
interagire con altri pannelli. Il modello prevede la presenza di una interfaccia ogni
qualvolta un pannello abbia un lato, o una porzione di esso, in comune con un altro
pannello o con un supporto esterno.
Questo modo di procedere permette di modellare agevolmente schemi strutturali dalle
geometrie anche complesse e irregolari.
Un aspetto originale del modello è rappresentato dal fatto che il pannello è interagente
lungo ciascuno dei suoi lati. Tale circostanza determina numerosi vantaggi in quanto
consente una modellazione efficiente delle fasce di piano in cui l’eventuale azione di
confinamento agisce in direzione orizzontale, rende agevole la modellazione tra la
```
muratura ed altri elementi (ad es. cordoli di piano o pilastri) ed inoltre consente di
```
modellare una parete di muratura attraverso una mesh di macro-elementi.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
37
```
Figura 3-5: Muratura modellata mediante una mesh di macro-elementi (“Manuale
```
```
teorico”)
```
La possibilità di suddividere l’elemento murario in una mesh di più elementi più piccoli
sembrerebbe ricalcare la filosofia tipica dei modelli agli elementi finiti, tuttavia risulta
utile evidenziare alcuni aspetti. Innanzitutto l’utilizzo di una mesh di macro-modelli
rappresenta una possibilità e non una necessità, come nel caso dei modelli agli elementi
finiti. In questo caso un singolo macro-elemento è già concepito per simulare la risposta
```
del pannello murario che rappresenta, a prescindere dalla sua estensione; una mesh più
```
fitta consente una descrizione più dettagliata della cinematica, oltre alla possibilità di
cogliere con maggiore accuratezza il meccanismo di collasso.
Data una generica parete muraria, a partire dalla sua specifica geometria è possibile
individuare un numero di pannelli murari minimo che la compongono. Si può tuttavia
decidere di schematizzare ognuno di essi mediante un singolo macroelemento oppure
suddividerli, tutti o solo alcuni, in più macroelementi.
L’irregolarità geometrica e di disposizione delle aperture può costituire senz’altro un
esempio in cui il ricorso a una mesh più fitta rispetto a quella di base può essere
auspicabile non tanto ai fini della valutazione della curva di capacità della struttura,
quanto invece al fine di una più corretta valutazione del meccanismo di collasso.
IL MACROMODELLO PROPOSTO
38
Figura 3-6: Modellazione di un prototipo di parete mediante due differenti mesh:
```
discretizzazione della parete (S. Caddemi, I. Caliò et al.)
```
Il collasso di un elemento murario caricato verticalmente e sollecitato nel proprio piano
mediante azioni orizzontali crescenti si manifesta secondo tre possibili meccanismi già
visti nel capitolo 2.5.
```
Richiamata la Figura 2-8: Meccanismi di collasso nel piano: pressoflessione (a), taglio-
```
```
fessurazione diagonale (b), taglio-scorrimento (c) in cui si rappresentano i tre diversi
```
meccanismi di rottura di un pannello murario, la corrispondente rappresentazione di tali
meccanismi con il modello numerico adottato è fornita in figura sottostante.
```
Figura 3-7: Simulazione dei meccanismi di collasso nel piano di un pannello murario: (a)
```
```
rottura per schiacciamento/ribaltamento; (b) rottura a taglio per fessurazione diagonale;
```
```
(c) rottura a taglio per scorrimento. (S. Caddemi, I. Caliò et al.)
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
39
Nei successivi paragrafi della presente tesi, per ogni singola molla del pannello ci sarà
```
una parte descrittiva per la taratura della stessa e un confronto tra i dati teorici (ricavati
```
```
dalla parte descrittiva per mezzo di tabulati Excel) e quelli ottenuti dal modello
```
implementato nel già citato software OpenSees.
IL MACROMODELLO PROPOSTO
40
3.2.1 Elementi rigidi
Nel modello scelto per gli elementi asta del quadrilatero, i quali danno le dimensioni al
```
pannello stesso, si è scelto di adottare elementi truss infinitamente rigidi (essi non si
```
dovranno deformare in quanto gli unici spostamenti accettati nel modello sono quelli
```
degli elementi resistenti, ovvero delle molle).
```
```
OSS: In questa tesi si è scelto di utilizzare questi elementi infinitamente rigidi anche se
```
sarebbe stato meglio considerare questi elementi deformabili assialmente. In questo
modo, le molle di interfaccia si potrebbero considerare come rigide e che tengano conto
```
solo della resistenza invece che della deformabilità (mentre nelle molle diagonali si
```
considererebbe sempre sia la deformabilità a taglio sia la possibilità di rottura a taglio
```
fessurazione).
```
3.2.2 Taratura molle muratura
Di seguito vengono descritti tutti i legami costitutivi presi in considerazione per la
modellazione del comportamento meccanico degli elementi murari.
Ciascun legame costitutivo, impiegato per descrivere il comportamento di un materiale,
```
verrà ereditato dagli elementi resistenti (molle) che nel modello discreto equivalente
```
rappresentano gli elementi che concentrano in sé le proprietà meccaniche del continuo
che simulano.
Verranno quindi descritte le procedure di taratura delle molle non lineari atte alla
determinazione dei parametri meccanici delle stesse, affinché il comportamento del
modello discreto sia equivalente a quello reale dei materiali pensati come continui.
Tutti i legami costitutivi sono di tipo monoassiale, poiché il modello impiega solo
elementi monodimensionali per tenere in conto le non linearità. Tale circostanza
rappresenta senz’altro un enorme vantaggio sia dal punto di vista della semplicità di
modellazione che da quello numerico.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
41
Il materiale muratura, visto come un continuo omogeneo, viene modellato utilizzando
legami costitutivi differenti per i diversi aspetti del suo comportamento: flessione, taglio
e scorrimento. Ciò avviene tramite i corrispondenti legami costitutivi descritti nel
seguito. Ciascuna molla del sistema discreto erediterà il legame costitutivo del
corrispondente modello continuo, in termini monoassiali, e i suoi parametri meccanici
vanno determinati a partire dai parametri meccanici e dalla geometria del modello
continuo tramite le procedure di taratura.
Per ciascuno dei tre principali comportamenti della muratura verranno descritti i
possibili legami costitutivi utilizzati, e poi le procedure di taratura che, a partire dalle
legge monoassiali dei materiali, consentono di ottenere le proprietà delle corrispondenti
molle non lineari.
3.2.3 Comportamento flessionale
Nel seguito si descrivono i legami costitutivi utili per la simulazione del comportamento
flessionale di pannelli murari. In particolare vengono presi in considerazione il
comportamento elastico lineare e quello elastico perfettamente plastico.
Successivamente vengono descritte le procedura per ottenere le proprietà delle molle di
interfaccia trasversali, tenendo conto di tali possibili comportamenti costitutivi.
Si modella un continuo elastoplastico perfetto con diverso comportamento a trazione e
a compressione e con limite agli spostamenti. Esso viene assegnato mediante la
definizione del legame monoassiale σ-ε.
Dunque, si deve assegnare:
- E modulo di deformazione normale;
- σc, σt limiti di resistenza a compressione e trazione;
- εc, εt limiti nelle deformazioni a compressione e trazione.
IL MACROMODELLO PROPOSTO
42
```
Figura 3-8: Legame costitutivo elasto-plastico (“Manuale teorico”)
```
Non appena viene raggiunto un limite di deformazione si ha una rottura fragile, a
seguito della quale il materiale si scarica completamente dal carico cui risulta soggetto
prima della rottura.
Il comportamento isteretico presenta uno scarico orientato all’origine per il
comportamento a trazione e scarico con rigidezza iniziale nel caso di compressione. Al
raggiungimento degli spostamenti ultimi, sia a trazione che a compressione,
corrisponderà la rottura dell’elemento.
Figura 3-9: Legame utilizzato per il comportamento assiale/flessionale della muratura.
```
(“Manuale teorico”)
```
Vengono previsti due comportamenti post-rottura differenti:
- Comportamento simmetrico: viene utilizzato per la modellazione di materiali
simmetrici a trazione e compressione. In questo caso a seguito di una rottura, sia
a compressione che a trazione l’elemento, oltre ad essere scaricato, perde ogni
capacità di resistere a ulteriori carichi, e viene quindi rimosso dal modello.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
43
- Comportamento di tipo fessurante: nel caso in cui viene raggiunto il limite di
rottura a compressione l’elemento viene rimosso dal modello. In caso di rottura
a trazione il materiale perde la possibilità di resistere a successivi carichi a
```
trazione (materiale fessurato), continua a poter resistere a compressione nel
```
```
momento in cui viene ripristinato il contatto tra gli elementi (modello crush and
```
```
cracking).
```
```
Figura 3-10: Legame elastoplastico di tipo fratturante (a) materiale non fratturato;
```
```
(b)materiale fratturato. (“Manuale teorico”)
```
3.2.3.1 Procedura di taratura
L’interfaccia deve simulare sia il comportamento assiale-flessionale dei pannelli che
collega, sia lo scorrimento che può avvenire tra due elementi contigui. In particolare, il
comportamento assiale/flessionale viene simulato mediante le molle trasversali mentre
lo scorrimento viene modellato mediante una molla posta in direzione dell’interfaccia
```
(scorrimento nel piano), chiamata molla tangenziale.
```
Le caratteristiche delle molle di interfaccia dipendono dalle caratteristiche della
muratura di entrambi i pannelli a contatto.
L’assegnazione inoltre avviene mediante la definizione delle curve relative alla direzioni
principali del materiale che sono le uniche direzioni per la quali sono note le curve di
carico.
Le operazioni di taratura delle molle trasversali di interfaccia portano alla
determinazione dei parametri costitutivi delle suddette: K, Fyc, Fyt, uc, ut, in funzione dei
parametri del modello continuo: E, εyc εyt, σyc σyt. Per tali parametri resta inteso che si
riferiscono alla direzione ortogonale all’interfaccia esaminata.
IL MACROMODELLO PROPOSTO
44
Dato che nelle molle trasversali è concentrata la deformabilità assiale e flessionale dei
pannelli, le proprietà meccaniche di queste dovranno essere ricavate a partire dalle
caratteristiche di entrambi i pannelli a contatto con l’interfaccia. Costituiranno eccezione
```
i casi di interfacce che collegano i pannelli a un supporto esterno; in questo caso infatti
```
le molle di interfaccia faranno riferimento solo al pannello murario.
Figura 3-11: Legame costitutivo e parametri caratteristici delle molle flessionali di
```
interfaccia (“Manuale teorico”)
```
La procedura che si esegue per trasferire le proprietà della muratura dei pannelli alle
molle di interfaccia consta di due fasi: nella prima le caratteristiche di deformabilità di
```
ciascuna fibra di un pannello murario vengono simulate da un’unica molla; in seguito
```
all’accostamento di due pannelli si vengono a creare due molle disposte in serie, ognuna
```
delle quali si riferisce a un pannello; nella seconda fase viene determinata la molla
```
equivalente alle due disposte in serie che rappresenterà la molla di interfaccia, come
mostrato in figura.
Figura 3-12: Procedura di concentrazione delle caratteristiche della muratura alle molle
```
delle interfacce (“Manuale teorico”)
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
45
La prima fase, in cui le caratteristiche di ogni pannello vengono concentrate in molle
```
disposte lungo i suoi lati (Kp), avviene imponendo l’equivalenza in termini di spostamenti
```
```
tra il modello discreto soggetto a un carico monoassiale (F) agente ortogonalmente
```
all’interfaccia e una lastra omogenea caratterizzata dal modulo di elasticità normale E,
soggetto a una distribuzione di pressione esterna p=N/A uniforme, dove A rappresenta
l’area trasversale del pannello.
Figura 3-13: Equivalenza tra il modello continuo e il modello discreto per la
```
determinazione delle rigidezze Kp (“Manuale teorico”)
```
La soluzione del problema elastico associato al modello continuo prevede unicamente
una distribuzione di tensioni normali uniforme in tutto il corpo, di intensità uguale alla
pressione esterna. Al fine di ricavare le caratteristiche di una singola molla si potrà fare
riferimento a una fibra di muratura, considerata isolata dal resto, di area trasversale pari
all’area di influenza di una singola molla determinata dagli interassi longitudinale e
```
trasversale (λ, λt) e altezza pari a metà di quella del pannello misurata in direzione
```
```
ortogonale all’interfaccia (L/2).
```
Uguagliando le rigidezze assiali offerte dal modello continuo e quella relativa a ciascuna
delle due molle Kp disposte in serie, si ottiene immediatamente:
dove si è indicato con E il modulo elastico della muratura relativamente alla direzione di
carico considerata.
A partire dalle tensioni limite della muratura nella direzione considerata, le
corrispondenti forze di snervamento delle molle si ottengono dalla semplice
considerazione di equivalenza:
IL MACROMODELLO PROPOSTO
46
che equivale ad assumere una distribuzione uniforme di tensioni corrispondente all’area
di influenza della molla.
Immaginando di concentrare la deformabilità di metà pannello, e assumendo uno stato
deformativo uniforme lungo l’altezza, si ha:
A questo punto sono noti tutti i parametri delle molle Kp relative ai singoli pannelli. I
parametri definitivi si ricavano considerando le due molle in serie, si ha pertanto:
Relativamente alla forza di snervamento della molla complessiva, questa sarà
ovviamente data dalla più piccola delle forze di snervamento relative ai pannelli
connessi.
```
Al fine di caratterizzare la muratura devono essere quindi assegnate le grandezze (E, εyc
```
```
εyt, σyc σyt) relative a ciascuna direzione principale della muratura. Tali quantità possono
```
```
essere determinate a partire dalle caratteristiche dei componenti (malta e mattoni)
```
```
tramite delle tecniche di omogeneizzazione oppure tramite delle prove in situ (o in
```
```
laboratorio). In particolare i moduli di elasticità e la resistenze a compressione possono
```
essere determinate con prove di compressione monoassiale, condotte con doppi
martinetti piatti, condotte parallelamente e ortogonalmente ai giunti di malta.
```
Più complicata risulta la problematica della determinazione della resistenza a trazione;
```
per murature non regolari costituite da pietrame informe o nel caso di murature regolari
di mattoni limitatamente alla direzione ortogonale ai giunti di malta, la resistenza a
trazione può essere paragonata alla resistenza a trazione della malta poiché le fessure
coinvolgono quasi esclusivamente i giunti di malta.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
47
Figura 3-14: Fessure per trazione in una muratura regolare caricata ortogonalmente ai
```
ricorsi (“Manuale teorico”)
```
Nel caso di muratura di mattoni e direzione di carico ortogonale ai giunti di malta la
resistenza a trazione della muratura è legata allo scorrimento lungo i giunti di malta.
```
Figura 3-15: Rottura a trazione per scorrimento lungo i giunti di malta (“Manuale
```
```
teorico”)
```
La muratura in questo caso presenta una resistenza e duttilità a trazione ben maggiore
di qualsiasi altra direzione, tale considerazione è quindi da tenere presente al momento
dell’attribuzione dei parametri costitutivi della muratura. Tale meccanismo di resistenza
a trazione tra l’altro è quello che si verifica in corrispondenza degli ammorsamenti tra le
pareti e rappresenta probabilmente il maggiore vincolo contro il ribaltamento delle
pareti.
IL MACROMODELLO PROPOSTO
48
3.2.4 Comportamento a taglio per fessurazione diagonale
Nel seguito si descrivono i legami costitutivi utili per la simulazione del comportamento
a taglio per fessurazione diagonale di pannelli murari. In particolare viene solo nominato
```
il comportamento alla Coulomb (verrà analizzato in seguito nel capitolo delle molle a
```
```
scorrimento) e verrà trattato ora solo quello alla Cacovic. Successivamente vengono
```
descritte le procedure per ottenere le proprietà delle molle diagonali dei pannelli
murari.
3.2.4.1 Materiale alla Cacovic
Nonostante il criterio di Cacovic sia stato formulato appositamente per le murature ed in
particolare per la resistenza nei confronti del meccanismo di collasso a taglio per
fessurazione diagonale, esso fa riferimento a pannelli murari soggetti a sforzo normale
solo lungo una direzione. Nel modello proposto, invece, ciascun pannello può essere
affiancato lungo ciascun lato da altri elementi e quindi ricevere sforzi di compressione in
corrispondenza di entrambe le coppie di lati paralleli. Nel seguito viene proposta
un’estensione del criterio di Cacovic che tiene conto proprio di tale circostanza.
L’ipotesi di base, analogamente a quella del criterio generale, è che la rottura per
```
fessurazione diagonale avvenga quando la massima tensione di trazione (lungo la
```
```
direzione principale) raggiunge il valore di resistenza convenzionale a trazione della
```
muratura. In precedenza è stato evidenziato come tale parametro debba intendersi a
livello macroscopico.
Si consideri nel seguito un pannello soggetto a due distinti sforzi di compressione,
indicati rispettivamente con P1 e P2, e a una forza tagliante V. Si indicano inoltre con A1 e
A2 le aree trasversali relative ai lati in cui sono applicati P1 e P2.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
49
```
Figura 3-16: Schema di carico di un pannello murario (“Manuale teorico”)
```
Continuando ad ammettere una distribuzione parabolica per le tensioni tangenziali e
una distribuzione uniforme per le tensioni normali, in corrispondenza del centro del
pannello lungo le giaciture paralleli ai lati si avrà uno stato tensionale caratterizzato dalle
```
tensioni normali p1=P1/A1, p2=P2/A2 (positive se di compressione) e da una tensione
```
tangenziale τ*=1.5·T/A1.
```
Figura 3-17: Rappresentazione dello stato tensionale nel piano di Mohr (“Manuale
```
```
teorico”)
```
Omettendo per brevità i passaggi, l’espressione della tensione principale di trazione
```
risulta:
```
```
√( )
```
```
Ponendo la tensione principale (pt) pari alla resistenza convenzionale a trazione (σtu), si
```
ottiene il valore limite di τ*:
√
IL MACROMODELLO PROPOSTO
50
Ricordando che vale
dove con τu e τk vengono indicate rispettivamente la tensione media ultima in condizioni
correnti e in assenza di compressione di confinamento. Si ha:
```
√ ( )
```
L’espressione appena ricavata viene riscritta come funzione di snervamento di un
generico solido monodimensionale utilizzando la notazione già adottata in precedenza,
cioè indicando con σ il parametro di tensione, con σy la resistenza a snervamento, con c
```
il termine di resistenza costante (non dipendente dallo stato dell’elemento) e con p1 e p2
```
i due parametri di stato. Sostituendo infine al coefficiente 1.5, il coefficiente b già
descritto in precedenza per tenere conto dei pannelli tozzi, si avrà:
```
√ ( )
```
In alternativa per rendere più semplice la modellazione si può fare comunque
riferimento al criterio limitando ad uno solo il parametro di stato:
```
√( )
```
3.2.4.2 Procedura di taratura
Le molle diagonali dei pannelli devono simulare il comportamento a taglio della
muratura, e il meccanismo di rottura che devono riprodurre è quello di rottura per
fessurazione diagonale.
Al fine di semplificare il più possibile il problema, ad ognuna delle due molle diagonali
viene attribuito un opportuno legame elasto-plastico di tipo simmetrico a trazione e
compressione.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
51
I parametri necessari alla caratterizzazione della muratura sono: il modulo di
```
deformazione tangenziale (G), la pendenza del ramo di softening (a sforzo di
```
```
compressione costante) (Gt), la resistenza media a taglio in assenza di sforzo normale
```
```
(τk).
```
Per quanto riguarda i criteri di snervamento in questa tesi verranno utilizzati quelli alla
```
Cacovic (si sarebbero potuti prendere anche quelli alla Coulomb).
```
```
La resistenza a taglio ultima del pannello (Tu), considerando una distribuzione uniforme
```
```
di tensioni tangenziali in tutta l’area trasversale del pannello (At), si otterrà
```
semplicemente moltiplicando la tensione tangenziale ultima per At:
```
( ) ( )
```
dove con p e P vengono indicati rispettivamente la tensione media e lo sforzo di
compressione cui è soggetto il pannello.
```
Figura 3-18: Pannello soggetto a una forza tagliante (“Manuale teorico”)
```
Considerando le espressioni dei criteri di snervamento scritte in precedenza, e
considerando che valgono le espressioni:
si ha:
- Criterio alla Coulomb: ( )
- Criterio alla Cacovic: √ ( )
IL MACROMODELLO PROPOSTO
52
o in alternativa, utilizzando un solo parametro di stato:
√
Fino ad ora si è parlato genericamente di compressione media del pannello: tale
parametro tuttavia va opportunamente definito. Nel più generale dei casi, quello cioè di
un pannello interagente lungo tutti i quattro lati, si avranno quattro diversi sforzi di
compressione.
Figura 3-19: Definizione del parametro di compressione media per un pannello
```
(“Manuale teorico”)
```
Nel caso si stia utilizzando un criterio di collasso caratterizzato da un unico parametro di
compressione media, questo verrà determinato come la media tra i quattro valori
```
presenti:
```
```
( )
```
Nel caso di criterio alla Cacovic con due parametri, ciascuno di essi verrà determinato in
maniera analoga facendo la media tra i due valori che si riferiscono a ciascuna coppia di
lati opposti.
In entrambi i casi, i criteri verranno utilizzati includendo un incrudimento di tipo
cinematico con α>0. Tale parametro viene determinato in funzione della rigidezza di
```
softening (Gt):
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
53
```
Per quanto riguarda lo spostamento ultimo del pannello (δu), coerentemente con
```
quanto proposto da Magenes e Calvi, esso si esprime in termini di deformazione
```
angolare ultima (γu) della muratura.
```
Le molle diagonali ereditano tutte le caratteristiche appena descritte, e i parametri che
```
ne caratterizzano il legame costitutivo sono: la rigidezza iniziale (k), la rigidezza del ramo
```
```
di softening a sforzo di compressione costante (kt), la forza di snervamento in assenza di
```
```
sforzo normale (Fy0), la forza di snervamento corrente (Fy) funzione della compressione
```
media cui risulta soggetto il pannello.
Di seguito si riportano i grafici relativi al legame costitutivo e al comportamento
isteretico, con riferimento a un ciclo di carico a compressione costante.
```
Figura 3-20: Legame attribuito alle molle diagonali; (a) legame carico spostamento; (b)
```
```
ciclo isteretico, a sforzo normale nullo (“Manuale teorico”)
```
I parametri meccanici delle molle vengono determinati in relazione alle caratteristiche
meccaniche della muratura imponendo una equivalenza in termini di spostamenti tra il
pannello visto come un continuo elastico e omogeneo, e il modello discreto equivalente,
composto dal quadrilatero articolato e le molle diagonali, soggetti entrambi a una
sollecitazione di puro taglio, come riportato in figura.
```
Figura 3-21: Equivalenza a taglio tra il modello continuo e il modello discreto (“Manuale
```
```
teorico”)
```
IL MACROMODELLO PROPOSTO
54
La soluzione del modello continuo a lastra, prevede unicamente una distribuzione di
```
tensioni tangenziali uniforme; è facile verificare che il drift tra le due facce opposte del
```
solido risulta:
Con riferimento al modello discreto con analogo spostamento del modello continuo,
l’allungamento e la forza relativi a ciascuna molla diagonale risultano:
```
Figura 3-22: Deformazioni nel sistema continuo e discreto (“Manuale teorico”)
```
Nelle precedenti espressioni si è indicato con At l’area trasversale del pannello relativa
alla forza tagliante T, con αp l’angolo formato tra tale superficie e la diagonale, con Hp
l’altezza del pannello ossia la dimensione ortogonale ad At.
Considerando inoltre che i due sistemi sono soggetti alla medesima forza di taglio e che
nel sistema discreto vi è la contemporanea presenza di due molle, si ha:
```
( )
```
Sostituendo quest’ultima nell’espressione dello spostamento del modello discreto, si
```
ottiene:
```
```
( )
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
55
da cui si ricava la rigidezza di ciascuna molla diagonale:
```
( )
```
Analogamente la rigidezza del ramo di softening risulta:
```
( )
```
Tutte le formule sopra riportate naturalmente sono valide nell’ipotesi che entrambe le
molle abbiano un legame costitutivo simmetrico rispetto all’origine.
Ricavando l’espressione della forza di snervamento della molla si ha:
```
( )
```
```
( )
```
```
( )
```
```
( )
```
Infine per quanto riguarda lo spostamento ultimo delle molle si ottiene:
```
( )
```
IL MACROMODELLO PROPOSTO
56
3.2.5 Comportamento a taglio-scorrimento
Oltre alla simulazione del comportamento presso-flessionale, l’elemento interfaccia ha
una seconda e altrettanto principale funzione che è la gestione degli scorrimenti tra
pannelli a contatto tra loro. Questi comportamenti sono governati complessivamente da
una molla non lineare che considera gli effetti dello scorrimento nel piano. E’ possibile
inserire altre due molle che regolano lo scorrimento fuori piano nel caso in cui il
comportamento sia tridimensionale.
Il comportamento a scorrimento per sua natura è un comportamento ad attrito, ossia di
tipo rigido plastico, la cui forza limite corrente può essere facilmente determinata con
un criterio di snervamento alla Coulomb.
3.2.5.1 Materiale alla Coulomb
Si modella un continuo elastico-plastico isotropo soggetto a uno stato tensionale
monoassiale con comportamento simmetrico a trazione e a compressione, superficie di
snervamento alla Coulomb e limite nelle deformazioni.
Nel modello proposto tale materiale verrà utilizzato per simulare sia il comportamento a
```
scorrimento della muratura (potrebbe essere utilizzato anche per il comportamento a
```
```
taglio-fessurazione della muratura come detto precedentemente).
```
Con E e εu vengono indicati rispettivamente il modulo di deformazione normale che
caratterizza la fase elastica e il valore ultimo delle deformazioni oltre il quale si verifica la
rottura del materiale.
Il limite della fase elastica viene fissato da uno criterio alla Coulomb di tipo degradante,
della quale viene riportata l’espressione della tensione ultima e della superficie di
```
snervamento:
```
| |
```
( ) ( )
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
57
```
dove:
```
- σ tensione agente;
- N variabile di stato rappresentativa dello stato di compressione dell’elemento;
- c termine di coesione;
- μ=tg(φ) tangente dell’angolo di attrito interno;
- H parametro di incrudimento;
- valore assoluto della deformazione plastica cumulata dello stesso segno della
tensione agente.
La superficie, nel piano σ-N si presenta nella classica forma del dominio alla Coulomb
come mostra la figura sotto riportata.
```
Figura 3-23: Dominio alla Coulomb incrudente nel piano N,σ (“Manuale teorico”)
```
Va tuttavia puntualizzato che il legame implementato fa riferimento solo a stati
tensionali piani. σ è infatti l’unico parametro di tensione, mentre N è una variabile di
stato che da una misura della compressione cui risulta soggetto l’elemento considerato
e la cui definizione varierà di volta in volta.
Al fine di prevedere un degrado della resistenza all’aumentare dell’escursione in campo
plastico è stato introdotto un termine di incrudimento di tipo cinematico, proporzionale
alle deformazioni plastiche accumulate:
IL MACROMODELLO PROPOSTO
58
Il parametro α rappresenta un parametro del modello e deve essere opportunamente
assegnato. Nel caso di α>0 l’incrudimento cinematico risulta essere negativo. Poiché tale
incrudimento viene fatto dipendere dalla deformazione cumulata, quantità mai
decrescente, i progressivi decrementi della resistenza possono essere di volta in volta
sommati. Inoltre la plasticizzazione in un verso non condiziona la resistenza del verso
opposto.
Considerando un processo di carico monotono a N costante, al variare di α si avrà un
andamento della curva di carico di tipo elasto-plastico con incrudimento variabile.
```
Figura 3-24: Legame σ-ε a N costante e α variabile (“Manuale teorico”)
```
Agevolmente può essere determinata la relazione che lega il parametro α con la
pendenza Et:
3.2.5.2 Procedura di taratura
La muratura viene quindi caratterizzata da due parametri di resistenza: uno che
```
rappresenta la coesione (c), o resistenza in assenza di tensioni normali, e l’altro l’angolo
```
```
di attrito interno (φ). Tale coppia di parametri si riferisce a una determinata superficie di
```
scorrimento. Coerentemente con quanto visto per il comportamento a flessione, anche
nel caso del comportamento a scorrimento è necessario tenere conto del carattere
ortotropo della muratura. Basti infatti pensare al diverso comportamento tra lo
scorrimento lungo i letti di malta e lungo la direzioni ad essi ortogonale. Vengono quindi
attribuiti due valori differenti di coesione e angolo di attrito interno per ciascuna
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
59
direzione principale del materiale. Nel seguito con c e φ vengono indicati genericamente
i valori relativi alla superficie di scorrimento coincidente con l’interfaccia.
La tensione limite di scorrimento media si esprime nella forma:
dove p rappresenta la tensione di compressione media agente lungo la superficie
dell’interfaccia.
Indicando con At l’area trasversale effettivamente a contatto tra le due superfici, la forza
limite che provoca lo scorrimento si può scrivere nella forma:
```
Figura 3-25: Scorrimento lungo i giunti di malta (“Manuale teorico”)
```
dove con P viene indicato lo sforzo di compressione agente in corrispondenza della
superficie dell’interfaccia.
Ciò equivale ad avere supposto una distribuzione di tensioni tangenziali uniformi in tutta
l’area a contatto.
Sia il valore di P che quello dell’area di contatto fra i pannelli sono variabili durante
l’analisi. In particolare, ad un’area di contatto nulla corrisponde una resistenza a
scorrimento anch’essa nulla.
Il legame a scorrimento viene considerato non incrudente e non degradante. Viene
previsto un comportamento isteretico caratterizzato da scarico con rigidezza iniziale.
Non viene previsto uno spostamento limite oltre il quale la molla debba essere scaricata.
IL MACROMODELLO PROPOSTO
60
Le molle di interfaccia poste per simulare lo scorrimento, possono essere caratterizzate
mediante un legame elastico perfettamente plastico con limite allo snervamento alla
Coulomb. La figura sottostante riporta lo schema meccanico equivalente di una molla
allo scorrimento.
Figura 3-26: Schema meccanico del comportamento a scorrimento dell’interfaccia,
```
limitatamente al caso piano (“Manuale teorico”)
```
I parametri meccanici delle molle si ricavano direttamente dalle caratteristiche della
```
muratura, considerando per ciascuna la propria area di influenza (Ac), coincidente con
```
l’intera sezione per la molla a scorrimento nel piano.
```
Figura 3-27: Aree di influenza delle molle a scorrimento nel piano (“Manuale teorico”)
```
La resistenza della molla dipende dalla porzione reagente dell’area di influenza in quanto
```
realmente a contatto tra i due pannelli (Am). Tale area varia al procedere del processo di
```
```
carico e viene determinata considerando le molle trasversali attive (dimensionate per
```
```
preso-flessione) ricadenti nell’area di influenza della molla in esame. Per molle inattive si
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
61
intendono le molle che si trovano in fase di trazione e che hanno raggiunto limite ultimo
di deformazione per cui totalmente scariche.
Analogamente, lo sforzo di compressione Pm relativo a ciascuna molla a scorrimento
viene calcolato come somma delle forze agenti nelle molle attive ricadenti all’interno
dell’area di influenza della molla, conteggiando sia le forze di compressione che di
```
trazione. La resistenza ultima di ciascuna molla (Tm) sarà quindi data da:
```
Nel caso in cui tutte le molle trasversali dell’area di influenza di una molla a scorrimento
divengono inattive, questa viene scaricata dal carico cui risulta soggetta e il suo stato
viene portato allo stato iniziale.
Per quanto riguarda la rigidezza iniziale da attribuire alla molla a scorrimento nel piano,
si possono seguire due approcci. Il primo consiste nel riconoscere tale rigidezza come
rappresentativa del comportamento iniziale, di tipo elastico delle superfici di
```
scorrimento ossia dei giunti di malta; in tal caso definendo con Gm il modulo tangenziale
```
relativo al giunto di malta, con Am il valore corrente dell’area a contatto, e con hm lo
spessore medio dei giunti, la rigidezza da attribuire alla molla a scorrimento risulta:
In ogni caso la determinazione della rigidezza da attribuire alla molla a scorrimento nel
piano sembra essere quanto mai una operazione incerta, come anche l’eventuale
determinazione del modulo G della malta o dello spessore dei giunti. Inoltre
percorrendo tale approccio, la rigidezza delle molle a rigore deve dipendere dall’area
attuale di contatto e quindi dovrebbe essere variabile durante l’analisi.
L’alternativa che appare più auspicabile, almeno dal punto di vista applicativo, è quella
di impostare un valore di rigidezza sufficientemente alto rispetto alle altre rigidezze del
IL MACROMODELLO PROPOSTO
62
modello in modo da ripristinare, in modo numerico, un comportamento di tipo rigido-
plastico.
È importante puntualizzare che gli elementi resistenti a scorrimento sono elementi
monodimensionali e quindi nelle interfacce gli scorrimenti plastici corrispondono alle
deformazioni plastiche delle molle a scorrimento, che non sono associate a nessuna
deformazione plastica in direzione trasversale.
```
Figura 3-28: Cinematica a scorrimento dell’interfaccia (“Manuale teorico”)
```
Così facendo si perde inevitabilmente la possibilità di modellare qualsiasi fenomeno di
dilatanza rappresentativa di possibili fenomeni di ingranamento delle superfici soggette
allo scorrimento.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
63
4 CALIBRAZIONE MOLLE DELLA MURATURA
In seguito, si presenta la calibrazione delle molle del modello con alcune modifiche
rispetto alla teoria riportata nei capitoli precedenti. Nella modellazione, infatti, si è
ritenuto computazionalmente più semplice attuare alcune variazioni ottenendo
comunque buoni risultati.
4.1 Dati generali della muratura
Per le seguenti calibrazioni delle molle utilizzate nel modello, si è preso come
```
riferimento la pubblicazione “Cyclic behaviour of brick masonry walls” (di G. Magenes e
```
G. M. Calvi). In essa è presentata un’indagine del comportamento sismico di strutture
esistenti in muratura attraverso test di taglio e compressione.
Nell’articolo sono presenti quattro diversi cicli isteretici corrispondenti a quattro diverse
prove eseguite in laboratorio su muri aventi le caratteristiche di murature esistenti, con
```
larghezza di w=1.50m, spessore di t=0.38m e altezza variabile (due provini hanno altezza
```
```
di h=2.00m e due con h=3.00m). Inoltre, per ogni muro con altezza diversa si hanno due
```
```
differenti sotto casi in base al carico verticale agente (σ=1.20MPa oppure σ=0.40MPa).
```
```
Gli unici parametri della muratura presenti nell’articolo sono i seguenti (gli altri
```
parametri che verranno presentati nel proseguo del presente elaborato, si sono ricavati
```
dal confronto tra i dati sperimentali delle prove e quelli numerici del modello):
```
```
Figura 4-1: tabella con parametri di resistenza del provino (da Magenes et Calvi)
```
CALIBRAZIONE MOLLE DELLA MURATURA
64
```
I test (distruttivi) sono stati eseguiti come in figura 4-2: la forza verticale (costante) è
```
stata applicata prima della forza orizzontale ciclica e nel provino è stata bloccata ogni
```
possibile rotazione (condizioni di doppio pendolo in sommità).
```
```
Figura 4-2: schema dei test distruttivi in laboratorio (da Magenes et Calvi)
```
OSS. Nel modello numerico analizzato nella tesi si è deciso di non inserire vincoli in
```
sommità (ovvero si è trattato il muro come mensola, incastrato alla base) per tenere in
```
conto anche del possibile ribaltamento: si sono ottenuti così dei risultati analoghi a
```
quelli di laboratorio nei due casi con carichi verticali elevati (ovvero nel caso di pannelli
```
```
tozzi in cui la rottura avviene per taglio-fessurazione diagonale) mentre negli altri due
```
```
casi si hanno cicli isteretici diversi in quanto si ottiene una tipologia di rottura (per
```
```
ribaltamento) non tenuta in conto dalle prove.
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
65
Di seguito si rappresentano le varie prove ottenute in laboratorio sulle quali ci si è basati
per la taratura dei parametri della muratura esistente, utilizzati nel presente elaborato
di tesi:
- Muro MI1, h=2.00m e σm=1.20MPa: la rottura individuata da questa prova di
laboratorio è del tipo taglio-fessurazione diagonale.
Figura 4-3: legame taglio alla base-scorrimento in sommità del muro MI1 analizzato in
```
laboratorio (da Magenes et Calvi)
```
- Muro MI2, h=2.00m e σm=0.40MPa: la rottura individuata da questa prova di
laboratorio è del tipo taglio-scorrimento, con fessure nei giunti di malta alla base
del provino. Da questa prova, si è ottenuto un coefficiente di attrito che varia tra
0.57 e 0.65. Come detto precedentemente, nel modello numerico si è ricavata
una rottura per ribaltamento del maschio murario.
Figura 4-4: legame taglio alla base-scorrimento in sommità del muro MI2 analizzato in
```
laboratorio (da Magenes et Calvi)
```
CALIBRAZIONE MOLLE DELLA MURATURA
66
- Muro MI3, h=3.00m e σm=1.20MPa: la rottura individuata da questa prova di
laboratorio è del tipo taglio-fessurazione diagonale.
Figura 4-5: legame taglio alla base-scorrimento in sommità del muro MI3 analizzato in
```
laboratorio (da Magenes et Calvi)
```
- Muro MI4, h=3.00m e σm=0.40MPa: la rottura individuata da questa prova di
laboratorio è del tipo taglio-fessurazione diagonale. Come detto
precedentemente, nel modello numerico si è ricavata una rottura per
ribaltamento del maschio murario.
Figura 4-6: legame taglio alla base-scorrimento in sommità del muro MI4 analizzato in
```
laboratorio (da Magenes et Calvi)
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
67
Si sono, quindi, ottenuti i seguenti parametri per le caratteristiche della muratura
esistente utilizzati per tutti gli esempi e casi studio del presente elaborato di tesi:
resist media a compressione della muratura fu -7.92 Mpa
resist a trazione della muratura ft 0.1 Mpa
```
mod elast normale muratura (a σ=0,33fu) E 2910 Mpa
```
deform ultima compressione=3*εcy εcu 3*εcy adim
deform ultima trazione=1,5*εty εtu 1,5*εty adim
resist media a taglio a compressione nulla τ0 0.1 Mpa
mod elast tangenziale muratura G 875 Mpa
20%*G Gt 175 Mpa
coeff di coesione c 0.2 Mpa
coeff di attrito φ 0.5 adim
peso specifico muratura w 24 KN/m3
Alcuni di questi parametri sono stati presi coerentemente a quanto è riportato nelle
```
Norme Tecniche per le Costruzioni (tabella C8A.2.1) e letteratura (P.Cirone, 2011).
```
Il peso specifico della muratura è stato preso elevato considerando la presenza di
intonaci e pacchetti termici vari.
CALIBRAZIONE MOLLE DELLA MURATURA
68
4.2 Modellazione e simulazioni numeriche
OpenSees è un software di tipo Open Source che permette di creare applicazioni agli
elementi finiti per simulare la risposta di sistemi strutturali e geotecnici soggetti
all’azione sismica e ad altre sollecitazioni.
Nel caso in esame tutte le strutture sono state modellate con elementi
monodimensionali di tipo truss a comportamento lineare e non lineare, e di tipo beam a
comportamento elastico per simulare il fuoripiano delle pareti murarie perpendicolari al
sisma.
Nello specifico, per la muratura nel piano si sono presi i seguenti elementi:
- truss infinitamente rigidi, per tutti gli elementi della parete che svolgono i
compiti di dare la geometria al macroelemento e scaricare i carichi verticali
```
agenti direttamente sulle molle assiali;
```
- truss con una certe legge costitutiva isteretica (denominati “Hysteretic Material”
da “OpenSees Command Language Manual” S. Mazzoni, F. McKenna, M.H. Scott,
```
G.L. Fenves, et al. 2007), per tutti gli elementi del macroelemento che svolgono il
```
```
compito di deformarsi, di rompersi e di caratterizzare la risposta del muro (molle
```
```
assiali, trasversali e diagonali). Per questi Hysteretic Material, la calibrazione è
```
stata effettuata replicando numericamente la prova sperimentale e
confrontando i risultati in termini di cicli forza spostamento. Questo comando è
usato per costruire un materiale con legge isteretica bilineare uniassiale che
permette di considerare il pinching per forza e deformazione, il danno in
funzione della duttilità e dell’energia dissipata, e il degrado di resistenza in
funzione della duttilità. I parametri da calibrare sono quelli che definiscono le
curve riportate in figura sottostante. Altri parametri consentono di tener conto
dei degradi. Per la definizione di tutti i parametri e approfondimenti, si rimanda
```
al manuale del software (S. Mazzoni, F. McKenna, M.H. Scott, G.L. Fenves, et al.,
```
```
“OpenSees Command Language Manual”, 2007).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
69
```
Figura 4-7: Definizione del modello Hysteretic Material nel manuale OpenSees (da S.
```
```
Mazzoni, F.McKenna, et al.)
```
4.2.1 Truss infinitamente rigidi
Per la modellazione di questi elementi, si sono utilizzati degli elementi elastici
monodimensionali con rigidezza elevata, di modo che le deformazioni della muratura
siano dovute solamente agli elementi “molla” che analizzeremo nei paragrafi successivi.
Nel modello si sono inseriti, quindi, i seguenti parametri:
CALIBRAZIONE MOLLE DELLA MURATURA
70
4.3 Calibrazione molle maschio murario
4.3.1 Calibrazione molle assiali
Per la calibrazione di questa tipologia di molle ci si è riferito a “Manuale Teorico
3DMacro” del Gruppo Sismica S.R.L. già citato nei capitoli precedenti. Esse sono state
dimensionate per i meccanismi di rottura a presso-flessione e ribaltamento.
Per mezzo di una procedura implementata per mezzo di un foglio di calcolo Excel, si
sono ricavati tutti i vari parametri poi inseriti nel modello in funzione delle
caratteristiche meccaniche e geometriche del singolo maschio murario.
Si è ottenuto, quindi:
- legame σ-ε delle molle assiali:
σ c -7.92 Mpa
σ t 0.1 Mpa
E 2910 Mpa
εcy -0.003 adim
ε cu -0.008 adim
ε ty 0.00003 adim
ε tu 0.00005 adim
-10
-8
-6
-4
-2
0
2
-0.009 -0.004 0.001
```
tensione normale (MPa)
```
```
Deformazione (mm/mm)
```
legame costitutivo
legame
costitutivo
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
71
- legame F-s delle molle assiali (valori inseriti nel modello utilizzato):
Molle
t 380 mm
λ=w/2 750 mm
A molla 285000 mm2
Fcu -2257.2 kN
Ftu 28.5 kN
Ucu -12.247 mm
Ucy -4.082 mm
Uty 0.052 mm
Utu 0.0773 mm
```
Come si evince dal legame costitutivo soprariportato, la muratura (e quindi le molle
```
```
assiali) hanno bassissima resistenza a trazione e un’elevata resistenza a compressione.
```
-3000
-2000
-1000
0
1000
-13 -8 -3
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
legame costitutivo molle assiali
legame
costitutivo
molle…
CALIBRAZIONE MOLLE DELLA MURATURA
72
Nel modello si sono inseriti, quindi, i seguenti parametri:
Per considerare il taglio massimo per il ribaltamento del singolo maschio murario, si è
calcolato il taglio ultimo e momento ultimo dalla semplice formula dell’equilibrio alla
rotazione del pannello murario in un nodo alla base.
```
Si è ricavato quanto segue (questo è il caso della prova MI4):
```
VALORI REALI DEL RIBALTAMENTO DEL PANNELLO
Pppannello -41.04 kN
Ntot -269.04 kN
w 1500 mm
t 380 mm
σ0 -0.472 N/mm2
fc -7.92 N/mm2
Mult -187.633 kNm
Tult -62.544 kN
Mult con resist traz -230.383 kNm
Tult con resist traz -76.794 kN
I seguenti, invece, sono i valori ultimi che ci si aspetta di ritrovare nel modello:
RIBALT MODELLO
Mult con resist traz -244.53 kNm
Tult con resist traz -81.51 kN
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
73
Come si può osservare dalle tabelle sopra rappresentate, il modello non considera la
```
reazione di compressione eccentrica (sono state inserite solo due molle assiali in
```
```
corrispondenza dei nodi alla base), la quale diminuirebbe il Tult (quindi il modello è
```
```
approssimato). Si nota, infatti, che il taglio ultimo del modello è superiore del taglio
```
```
ultimo reale di 5 kN (e quindi la parete del modello resiste maggiormente rispetto alla
```
```
parete reale).
```
Per una maggiore realisticità del modello, si sarebbe potuto inserire un maggior numero
di molle alla base, ognuna con un’area di influenza diversa. Non è stato fatto ciò per
diminuire l’onere computazionale del modello e perché comunque i risultati ottenuti
non si discostano eccessivamente dalla realtà.
4.3.2 Calibrazione molle diagonali
Per la calibrazione di questa tipologia di molle ci si è riferito a “Manuale Teorico
3DMacro” del Gruppo Sismica S.R.L. già citato nei capitoli precedenti. Esse saranno
dimensionate per il meccanismo di rottura a taglio-fessurazione diagonale.
Si è, inoltre, considerato l’articolo di Magenes e Calvi il quale sostiene: “Nel caso di
rottura per taglio, si suppone che nell’elemento abbiano luogo deformazioni taglianti
plastiche -come illustrato in figura sottostante- in cui viene posto un limite alla
```
deformazione angolare θ= ψ+ γ (chord rotation), oltre il quale la resistenza si annulla. La
```
deformazione angolare θ è espressa come somma della deformazione flessionale ψ e di
quella a taglio γ. *…+ si assume che il limite θu sia pari allo 0.5% dell’altezza del maschio
murario”.
Figura 4-8: deformazioni angolari pertinenti all’estremo i di un elemento “beam-column”
```
(da Magenes et Calvi)
```
CALIBRAZIONE MOLLE DELLA MURATURA
74
Figura 4-9: in una prova a taglio su pannello murario in cui si mantiene il parallelismo
```
delle basi, si ha che: θi=θj=θ=δ/H (da Magenes et Calvi)
```
Per mezzo di una procedura implementata per mezzo di un foglio di calcolo Excel, si
sono ricavati tutti i vari parametri poi inseriti nel modello in funzione delle
caratteristiche meccaniche e geometriche del singolo maschio murario.
Come detto in precedenza, per la valutazione del taglio ultimo di progetto si è adottato il
Criterio di Turnsek-Cacovic in funzione del carico verticale P agente nel pannello e della
geometria dello stesso. Dato che s’inseriscono due molle diagonali per pannello, il carico
```
verticale è stato calcolato come somma del carico esterno (nel modello finale sarà quello
```
```
dovuto al solaio) con la metà del peso del maschio murario. Inoltre, come già detto nei
```
capitoli precedenti, si è tenuto conto per mezzo di un coefficiente correttivo “b” della
```
geometria del pannello, ovvero se il maschio è snello (b=1.5) o tozzo (b=1.0), con i vari
```
sottocasi intermedi.
A titolo di esempio, si riporta la determinazione delle molle diagonali nella prova MI3:
CRITERIO ALLA CACOVIC
coeff b 1.5 adim
At 570000 mm2
τ0 0.1 Mpa
φ 0.5 adim
τk 0.1 Mpa
Tk 57 kN
```
Tu(P) 175.501 kN
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
75
Molle diagonali ambo reagenti
G 875 Mpa
Gt 175 Mpa
δy 1.056 mm
angolo diag 1.107 rad
allung molla y 0.472 mm
num molle diagonali 2
Kel 415625 N/mm
Ksoft 83125 N/mm
Fy 196.216 kN
```
θu (deform ang ultima) 0.005 da Magenes-Calvi 0,5%*H
```
allung ult molla 6.708 mm
Fu 120 kN
Il legame F-s di queste molle sarà, quindi, del tipo:
-300
-200
-100
0
100
200
300
-9 -7 -5 -3 -1 1 3 5 7 9
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
legame costitutivo molle diagonali
legame
costitutivo
molle diagonali
CALIBRAZIONE MOLLE DELLA MURATURA
76
```
Nel modello (sempre per il caso MI3) si sono inseriti, quindi, i seguenti parametri:
```
Si è inserito il parametro “beta=0.8”, indice di danno della muratura: infatti, appena la
```
muratura inizia a fessurare, ci sarà un degrado di resistenza (il valore “0.8” si è ricavato
```
ad hoc di modo che i risultati da modello coincidano con quelli della prova
```
sperimentale). Il danneggiamento entrerà in gioco solo dopo che il taglio agente avrà
```
superato il valore di picco del legame costitutivo della muratura, ovvero appena essa
inizierà a fessurarsi.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
77
4.3.3 Calibrazione molle trasversali
Per la calibrazione di questa tipologia di molle ci si è riferito a “Manuale Teorico
3DMacro” del Gruppo Sismica S.R.L. già citato nei capitoli precedenti. Esse saranno
dimensionate per il meccanismo di rottura a taglio-scorrimento.
Come detto in precedenza, per la valutazione del taglio ultimo di progetto si è adottato il
Criterio di resistenza di Mohr-Coulomb in funzione del carico verticale P agente nel
```
pannello, della geometria dello stesso e di vari parametri della muratura (quali il
```
```
coefficiente di attrito e la coesione). Dato che s’inseriscono due molle trasversali per
```
```
pannello, il carico verticale è stato calcolato come somma del carico esterno (nel
```
```
modello finale sarà quello dovuto al solaio) con l’intero peso del maschio murario. L’area
```
di influenza della singola molla, però, è stata presa come metà dell’area di base del
maschio murario.
A titolo di esempio, si riporta la determinazione delle molle trasversali della prova MI2:
ATTRITO MOHR COULOMB
coesione c 0.2 N/mm2
Am 570000 mm2
coeff attrito φ 0.5
PPparete 27.36 kN
Pm 255.36 kN
num molle 2
```
Tm(P) 120.84 kN
```
δ max 10 mm
CALIBRAZIONE MOLLE DELLA MURATURA
78
Le molle trasversali seguiranno, dunque, la seguente legge F-s:
```
Nel modello (sempre per il caso MI2) si sono inseriti, quindi, i seguenti parametri:
```
Per le molle trasversali si è deciso di inserire due molle con legge costitutiva simmetrica.
Altrimenti, si sarebbe potuto inserire un'unica molla con caratteristiche resistenti
“doppie”.
OSS. Si sarebbe potuta assegnare una legge costitutiva in funzione del carico P agente
```
nel modello, ovvero “collegare” la risposta delle molle trasversali (dovuta all’attrito di
```
```
Mohr-Coulomb) alla reazione agente nelle molle assiali. Infatti, qualora le molle assiali
```
```
fossero in trazione, la muratura resisterebbe poco a taglio-scorrimento (le NTC08
```
indicano che la resistenza in questo caso può essere assunta pari alla coesione della sola
```
malta). Anche per questo motivo, oltre che per il già citato motivo del collasso per
```
ribaltamento, sarebbe stato opportuno inserire un letto di molle assiali alla base del
singolo maschio murario. Come già descritto, ciò non è stato fatto per diminuire l’onere
computazionale.
-150
-100
-50
0
50
100
150
-16 -14 -12 -10 -8 -6 -4 -2 0 2 4 6 8 10 12 14 16
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
legame costitutivo molle trasversali
legame
costitutivo
molle…
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
79
4.3.4 Validazione del singolo maschio murario
```
Di seguito, si confrontano i risultati dei modelli dei maschi murari (per mezzo di
```
```
un’analisi ciclica) con i relativi casi delle prove sperimentali già descritte
```
precedentemente. Per ogni prova, si è analizzata la risposta della singola molla per
```
determinare la tipologia di rottura del maschio (si riporta per semplicità il grafico della
```
```
sola molla che entra in crisi).
```
```
4.3.4.1 Muro MI1 (h=2.00m e σm=1.20MPa):
```
Si nota che il muro così modellato ha un comportamento molto simile alla prova
sperimentale. Come notato sperimentalmente, anche nel modello numerico il muro
raggiunge la rottura per taglio-fessurazione diagonale.
-300
-200
-100
0
100
200
300
-20 -15 -10 -5 0 5 10 15 20
```
Taglio alla base (kN)
```
```
Spostamento in sommità (mm)
```
Andamento prova MI1
Serie2
CALIBRAZIONE MOLLE DELLA MURATURA
80
```
Di seguito, si nota (linea rossa) l’andamento delle molle diagonali del modello in
```
```
confronto con l’andamento previsto in fase di calibrazione (linea blu).
```
Come si evince dal grafico sopra riportato, il maschio così progettato si rompe per
fessurazione diagonale.
```
4.3.4.2 Muro MI2 (h=2.00m e σm=0.40MPa)
```
Si nota come in questo caso la rottura del modello numerico avvenga per ribaltamento
mentre quella ricavata sperimentalmente avveniva per taglio-scorrimento alla base. Ciò
è dovuto al fatto che sono stati utilizzati vincoli diversi per le due prove: in laboratorio si
-250
-200
-150
-100
-50
0
50
100
150
200
250
-15 -10 -5 0 5 10 15
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
legame costitutivo molle diagonali
andamento
teorico molla
diagonale
molla diagonale
modello
-300
-200
-100
0
100
200
300
-20 -15 -10 -5 0 5 10 15 20
```
Taglio alla base (kN)
```
```
Spostamento in sommità (mm)
```
Andamento prova MI2
Serie2
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
81
è usato un sistema incastro-doppio pendolo mentre nel modello numerico si è preso un
sistema incastro-estremo libero, in quanto si è voluto considerare anche il possibile
ribaltamento del pannello.
Si nota, inoltre, che la parte “elastica” è molto simile tra i due casi.
La rottura della parete modellata era stata comunque prevista giacché si era calcolato
```
come taglio ultimo (inferiore sia al taglio ultimo per fessurazione-diagonale che per il
```
```
taglio-scorrimento):
```
RIBALT TEORICO MODELLO
Mult senza resist traz -191.52 kNm
Tult senza resist traz -95.76 kN
Mult con resist traz -234.27 kNm
Tult con resist traz -117.135 kN
```
Dal modello, infatti, si è ricavato come valore di taglio alla base (valori molto simili a
```
```
quelli teorici calcolati):
```
RIBALT CALCOLATO DA MODELLO
Tult con resist traz -117.238 kN
Tult senza resist traz -95.7841 kN
CALIBRAZIONE MOLLE DELLA MURATURA
82
```
4.3.4.3 Muro MI3 (h=3.00m e σm=1.20MPa)
```
Si nota che il muro così modellato ha un comportamento molto simile alla prova
sperimentale. Come notato sperimentalmente, anche nel modello numerico il muro
raggiunge la rottura per taglio-fessurazione diagonale.
```
Di seguito, si nota (linea blu) l’andamento delle molle diagonali del modello in confronto
```
```
con l’andamento previsto in fase di calibrazione (linea rossa).
```
Come si evince dal grafico sopra riportato, il maschio così progettato si rompe per
fessurazione diagonale.
-300
-200
-100
0
100
200
300
-20 -15 -10 -5 0 5 10 15 20
```
Taglio alla base (kN)
```
```
Spostamento in sommità (mm)
```
Andamento prova MI3
Serie2
-250
-200
-150
-100
-50
0
50
100
150
200
250
-15 -10 -5 0 5 10 15
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
legame costitutivo molle diagonali
molla diagonale
modello
andamento
teorico molla
diagonale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
83
OSS. Dato che questo è il caso di un muro di altezza 3.00m, larghezza 1.50m e spessore
0.38m, esso verrà poi adottato per il modello di edificio più grande. In seguito si farà
anche un confronto tra l’energia dissipata dal caso sperimentale e l’energia dissipata dal
modello numerico, il tutto per convalidare maggiormente il modello pensato.
```
4.3.4.4 Muro MI4 (h=3.00m e σm=0.40MPa)
```
Si nota anche in questo caso come la rottura del modello numerico avvenga per
ribaltamento mentre quella ricavata sperimentalmente avveniva per taglio-scorrimento
```
alla base (analogamente al caso MI2 per un motivo di vincoli alle estremità).
```
RIBALT TEORICO MODELLO
Mult senza resist traz -201.78 kNm
Tult senza resist traz -67.26 kN
Mult con resist traz -244.53 kNm
Tult con resist traz -81.51 kN
```
Dal modello, infatti, si è ricavato come valore di taglio alla base (valori molto simili a
```
```
quelli teorici calcolati):
```
RIBALT CALCOLATO DA MODELLO
Tult con resist traz -81.5732 kN
Tult senza resist traz -67.2712 kN
-300
-200
-100
0
100
200
300
-20 -15 -10 -5 0 5 10 15 20
```
Taglio alla base (kN)
```
```
Spostamento in sommità (mm)
```
Andamento muro MI4
Serie2
CALIBRAZIONE MOLLE DELLA MURATURA
84
4.3.4.5 Confronto smorzamento del muro MI3
Nel presente paragrafo, si vuole validare la modellazione numerica attraverso un
confronto tra valori di smorzamento col caso sperimentale. Nell’analisi ciclica si sono
individuati degli spostamenti simili a quelli della prova sperimentale, in modo tale da
avere dei cicli confrontabili. Dapprima si determina, quindi, lo smorzamento ν di ogni
mezzo ciclo del modello numerico, attraverso la formula:
In cui:
- = energia dissipata, area racchiusa all’interno delle curve di un mezzo ciclo;
- = energia potenziale, area ottenuta dalla formula ( ) ( ) .
Si è calcolato, quindi, per il modello numerico:
CALCOLO SMORZAMENTO EQUIVALENTE
MEZZO
CICLO
calcolo Ed calcolo Ep smorzamento
step Ed tot Ed half cycle step disp Force Ep 
0 123 4.29 0.00 73 4.16 175.36 364.74 0.00%
1 222 9.49 5.20 173 -4.16 -175.36 364.74 0.23%
2 323 10.98 1.48 273 4.16 175.36 364.74 0.06%
3 422 12.69 1.71 373 -4.16 -175.36 364.74 0.07%
4 523 14.17 1.48 473 4.16 175.36 364.74 0.06%
5 622 15.89 1.71 573 -4.16 -175.36 364.74 0.07%
6 819 623.73 607.84 721 8.15 153.99 627.78 15.42%
7 1014 1320.47 696.74 917 -8.15 -153.99 627.78 17.67%
8 1211 1632.95 312.48 1113 8.15 153.99 627.78 7.93%
9 1406 1940.46 307.51 1309 -8.15 -153.99 627.78 7.80%
10 1603 2252.94 312.48 1505 8.15 153.99 627.78 7.93%
11 1798 2560.45 307.51 1701 -8.15 -153.99 627.78 7.80%
12 2105 3675.96 1115.51 1952 12.73 129.51 824.29 21.55%
13 2410 4852.10 1176.14 2258 -12.73 -129.51 824.29 22.72%
14 2717 5578.79 726.69 2564 12.73 129.51 824.29 14.04%
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
85
15 3022 6298.96 720.17 2870 -12.73 -129.51 824.29 13.91%
16 3329 7025.65 726.69 3176 12.73 129.51 824.29 14.04%
17 3634 7745.82 720.17 3482 -12.73 -129.51 824.29 13.91%
18 4025 9079.04 1333.22 3830 16.22 110.81 898.90 23.62%
19 4414 10431.45 1352.41 4220 -16.22 -110.81 898.90 23.96%
20 4805 11424.38 992.93 4610 16.22 110.81 898.90 17.59%
21 5194 12410.80 986.42 5000 -16.22 -110.81 898.90 17.47%
22 5585 13403.73 992.93 5390 16.22 110.81 898.90 17.59%
23 5974 14390.14 986.42 5780 -16.22 -110.81 898.90 17.47%
Le righe in verde sono state quindi confrontate con i valori dei cicli corrispondenti alla
prova sperimentale.
Per mezzo di Autocad, si è calcolato il valore dello smorzamento equivalente di questi
cicli sperimentali, ottenendo:
```
Figura 4-10: ciclo isteretico sperimentale della prova MI3; in giallo i quattro mezzi cicli
```
oggetto di analisi.
CALIBRAZIONE MOLLE DELLA MURATURA
86
```
Figura 4-11: mezzo ciclo “0”; in rosso la curva sperimentale, in nero il risultato numerico
```
```
Figura 4-12: mezzo ciclo “6”; in rosso la curva sperimentale, in nero il risultato numerico
```
```
Figura 4-13: mezzo ciclo “12”; in rosso la curva sperimentale, in nero il risultato numerico
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
87
```
Figura 4-14: mezzo ciclo “18”; in rosso la curva sperimentale, in nero il risultato numerico
```
Infine, dal confronto tra risultati numerici con quelli sperimentali si evince che lo
smorzamento equivalente per i quattro mezzi cicli oggetto di analisi è simile, ovvero:
MEZZO
CICLO
Smorzamento ν
MODELLO
Smorzamento ν
SPERIMENTALE
0 0.00% 5.26%
6 15.42% 15.06%
12 21.55% 18.06%
18 23.62% 20.15%
Da un’analisi dei risultati appena trovati, quindi, il modello numerico ha risultati simili
alla prova sperimentale e il modello creato è stato ritenuto accettabile.
CALIBRAZIONE MOLLE DELLA MURATURA
88
4.4 Calibrazione molle fascia di piano
Come da §4.5.4 “Organizzazione Strutturale” delle NTC’08: “I pannelli murari sono
considerati resistenti anche alle azioni orizzontali quando hanno una lunghezza non
```
inferiore a 0,3 volte l’altezza di interpiano; essi svolgono funzione portante, quando sono
```
sollecitati prevalentemente da azioni verticali, e svolgono funzione di controvento,
quando sollecitati prevalentemente da azioni orizzontali. Ai fini di un adeguato
comportamento statico e dinamico dell’edificio, tutte le pareti devono assolvere, per
quanto possibile, sia la funzione portante sia la funzione di controventamento.”
Per questo motivo, si sono modellate le fasce di piano come pareti che resistono ai
```
carichi orizzontali e al solo peso proprio (il solaio scarica tutti i carichi verticali
```
```
direttamente sui pannelli murari portanti).
```
Figura 4-15: esempi di danni in fasce di piano dovuti a sisma in edifici esistenti in
muratura semplice
Le fasce di piano “sono elementi deformabili della parete collocate tra due aperture
verticali. Il loro contributo nella resistenza sismica di una parete è notevole e può essere
preso in considerazione solo se all’interno della fascia stessa è presente un elemento in
```
grado di resistere a trazione (cordolo, tirante, architrave bene ammorsata, ecc.).” (M.
```
```
Vinci, 2014).
```
Per questo secondo motivo, si è deciso di considerare la presenza di tiranti in acciaio:
essi, come vedremo, sono stati dimensionati dimodoché il taglio che le fasce di piano
riescono a sopportare sia maggiore del taglio ultimo per fessurazione diagonale dei
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
89
pannelli murari portanti. In tal modo, si vuole concentrare la rottura della struttura solo
sulla rottura dei singoli maschi murari.
```
Figura 4-16: comportamento della parete con fasce di piano senza (a) e con (b)
```
```
resistenza e rigidezza flessionale (da edificiinmuratura.it)
```
Come si evince dalla figura 4-16, nel caso in cui non si considera la resistenza e rigidezza
flessionale della fascia, si attivano meccanismi di ribaltamento dei maschi nel piano.
Per le molle utilizzate per simulare la fascia di piano, si è deciso di riadattare le formule
teoriche per le molle del maschio, cambiando, però, le caratteristiche di resistenza per il
carattere ortotropo della muratura.
In accordo al §7.8.2.2.4 delle NTC08 “Travi in Muratura”: “La verifica di travi di
accoppiamento in muratura ordinaria, in presenza di azione assiale orizzontale nota,
viene effettuata in analogia a quanto previsto per i pannelli murari verticali. Qualora
```
l’azione assiale non sia nota dal modello di calcolo (ad es. quando l’analisi è svolta su
```
```
modelli a telaio con l’ipotesi di solai infinitamente rigidi nel piano), ma siano presenti, in
```
prossimità della trave in muratura, elementi orizzontali dotati di resistenza a trazione
```
(catene, cordoli), i valori delle resistenze possono essere assunti non superiori ai valori di
```
seguito riportati ed associati ai meccanismi di rottura per taglio o per pressoflessione.”
CALIBRAZIONE MOLLE DELLA MURATURA
90
```
Figura 4-17: sollecitazioni agenti sulla fascia di piano (spandrel).
```
La resistenza a taglio Vt di travi di accoppiamento in muratura ordinaria in presenza di un
cordolo di piano o di un architrave resistente a flessione efficacemente ammorsato alle
estremità, può essere calcolata in modo semplificato come:
```
dove:
```
- h è l’altezza della sezione della trave;
- fvd0 = fvk0/γM è la resistenza di calcolo a taglio in assenza di compressione.
Il massimo momento resistente, associato al meccanismo di pressoflessione, sempre in
presenza di elementi orizzontali resistenti a trazione in grado di equilibrare una
compressione orizzontale nelle travi in muratura, può essere valutato come
Dove
- Hp è il minimo tra la resistenza a trazione dell’elemento teso disposto
```
orizzontalmente ed il valore 0,4fhd*ht;
```
- fhd=fhk/γM è la resistenza di calcolo a compressione della muratura in direzione
```
orizzontale (nel piano della parete). Per il valore di fhk ci si è riferiti a valori
```
```
realistici: in molti testi viene attribuito il valore del 50% della resistenza a
```
```
compressione verticale (intuitivamente, la resistenza a compressione orizzontale
```
sarà inferiore a quella verticale in quanto non ci sarà l’effetto di “incatenamento”
```
dei vari mattoni e la compressione sarà parallela ai letti di malta).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
91
La resistenza a taglio, associata a tale meccanismo, può essere calcolata come
Dove
- l è la luce libera della trave in muratura.
Figura 4-18: Sollecitazioni di pressoflessione agenti sulla fascia di piano e andamento
```
tensioni (possibile rottura per fessurazione diagonale).
```
Il valore della resistenza a taglio per l’elemento trave in muratura ordinaria è assunto
pari al minimo tra Vt e Vp.
4.4.1 Valutazione tiranti
Come precedentemente scritto nel capitolo 2.7, i tiranti costituiscono un’ottima tecnica
di consolidamento per incrementare la resistenza di una parete nel proprio piano.
```
Figura 4-19: il ribaltamento dei pannelli murari (con Tult) è impedito dai tiranti
```
CALIBRAZIONE MOLLE DELLA MURATURA
92
Per il dimensionamento dei tiranti da inserire, si adotta il Principio dei Lavori Virtuali.
Basandoci sulla figura soprariportata, si ricava:
```
( )
```
Infine, ci si riconduce a:
Figura 4-20: pannello con tiranti inseriti alle estremità dello spandrel.
Si ottiene, quindi, uguagliando Mult=h’*Fy :
```
( )
```
A titolo di esempio, si riporta il foglio Excel con i risultati del dimensionamento dei tiranti
ottenuti per il caso studio un edificio di 13.5x10 m2 che verrà analizzato in seguito:
T ultimo pannello 87,065 kN
Taglio ultimo minimo calcolato in precedenza
```
(tra fessurazione diagonale e ribaltamento)
```
```
Fy=Tu*H/(2*H') 130,5975 kN da Mu=H'*Fy e da Fult*H*(ϑ)=2*Mu*(ϑ)
```
Fy,min per fila 130,5975 kN
Amin per fila 474,9 mm2
num tiranti per fila 1
fyd 275 Mpa
Φ min 24,58986498 mm
Φ progetto 26 mm
A sing fila 530,9291585 mm2
Atot 1061,858317 mm2
Fy trefoli tot 292,0110372 kN
Fy trefoli per fila 146,0055186 kN
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
93
Figura 4-21: dimensionamento tiranti e capochiave da programma di edificiinmuratura.it
Nel modello numerico, per considerare la presenza dei tiranti, verranno inserite delle
```
forze esterne di valore Fy (pari alla resistenza a snervamento dei tiranti) affinché le
```
“molle orizzontali spandrel” che vedremo nei capitoli successivi, rimangano sempre
compresse. Inoltre, con queste forze verranno dimensionate le “molle diagonali e
```
verticali spandrel” come se fossero delle forze di compressione che agevolano (per
```
```
mezzo dell’attrito) le resistenze a taglio delle fasce di piano.
```
```
OSS: Ricapitolando, le forze che entrano in gioco nel modello numerico per le fasce di
```
piano sono:
- peso proprio della fascia di piano;
- forze orizzontali Fy date dai tiranti.
CALIBRAZIONE MOLLE DELLA MURATURA
94
4.4.2 Calibrazione molle orizzontali spandrel
Esse saranno dimensionate per il meccanismo di rottura a presso-flessione.
Come detto nel capitolo 4.4, per la resistenza a compressione della muratura in
direzione orizzontale fh si assume il 50% della resistenza a compressione in direzione
```
verticale (fu). Quindi, si hanno i seguenti valori di resistenza per le fasce di piano:
```
Fasce di piano
```
fh=50%*fu fhd -3,96 Mpa
```
φ tiranti φ 26 mm
A singola tiranti A 530,9291585 mm2
fyd fyd 275 Mpa
forza da applicare nel modello F 146005,5186 N
Le “molle orizzontali spandrel” sono state tarate per tenere in conto del comportamento
```
flessionale della fascia di piano (e, quindi, per la compressione e per la trazione
```
```
dell’elemento). Analogamente al caso delle “molle assiali” del maschio murario (con
```
```
resistenza a compressione dimezzata), si ricavano i seguenti valori per la legge
```
costitutiva che sono stati poi inseriti nel modello:
σ c -3,96 Mpa
σ t 0,1 Mpa
E 2910 Mpa
ε cy -0,0014 adim
ε cu -0,0041 adim
ε ty 0,00003 adim
ε tu 0,00005 adim -5
-4
-3
-2
-1
0
1
-0.005 -2E-17
```
Tensione assiale (MPa)
```
```
deformazione (mm/mm)
```
legame costitutivo
legame
costitutivo
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
95
Da questi valori, si sono ricavati i seguenti dati F-s poi implementati nel modello
```
numerico:
```
molle parte compressa molle parte tesa
t 380 mm t 380 mm
```
λ (=h/2) 500 mm λ (=h/2) 500 mm
```
A infl molla 190000 mm2 A infl molla 190000 mm2
Fcu -752,4 kN Ftu 19000 kN
Ucu -6,116 mm Utu 0,077 mm
Ucy -2,039 mm Uty 0,051 mm
Figura 4-22: in rosso, le molle orizzontali spandrel
-800
-600
-400
-200
0
200
-8 -6 -4 -2 0 2
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle orizzontali spandrel
legame
costitutivo
molle…
CALIBRAZIONE MOLLE DELLA MURATURA
96
Nel modello si sono inseriti, quindi, i seguenti parametri:
Anche in questo caso, come nel caso dei singoli maschi murari, le fasce di piano
potrebbero andare in crisi per ribaltamento. Come si vede dalla tabella sottostante,
però, grazie all’inserimento dei tiranti questa modalità di rottura è molto improbabile
che avvenga giacché il taglio ultimo così ricavato è molto elevato:
fyd 275 Mpa
Atot tiranti 1061,858 mm2
Fsnerv tiranti 292,011 kN
0.4fhd*h*t 601,92 kN
Hp 292,011 kN
h 1000 mm
t 380 mm
Mu 146,039 kNm
l 1498 mm
```
Vult=2*Mu/l 194,978 kN
```
4.4.3 Calibrazione molle diagonali spandrel
Esse saranno dimensionate per il meccanismo di rottura a taglio-fessurazione diagonale.
Si passa ora alla calibrazione delle “molle diagonali spandrel”. Anche in questo caso,
come nel caso delle molle diagonali tarate per il singolo maschio murario, si utilizza il
metodo di Turnsek-Cacovic. In questo caso, però, le molle vengono tarate considerando
come carico agente sulla fascia di piano, le forze dovute ai due tiranti Fy le quali
comprimono la fascia e aumentano così la resistenza a taglio-fessurazione diagonale.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
97
Analogamente al pannello murario portante, si ricava il taglio ultimo a taglio
fessurazione diagonale pari a:
CRITERIO ALLA CACOVIC
coeff b 1 adim
At 380000 mm2
τ0 0,1 Mpa
φ 0,5 adim
τk 0,1 Mpa
Tk 38 kN
Ftiranti 292,011 kN
```
Tu(P) 111,984 kN
```
Si ricavano, quindi, i seguenti risultati per le molle diagonali:
Molle diagonali ambo reagenti
G 875 Mpa
Gt 175 Mpa
Δ y 0,505 mm
angolo diag 0,589 rad
allung molla y 0,42 mm
num molle diagonali 2
Kel 240336,321 N/mm
Ksoft 48067,264 N/mm
Fy 67,322 kN
```
γ u (deform ang ultima) 0,005
```
allung ult molla 6,23 mm
Fu 33,661 kN
Ksoft, reale 5793,718 N/mm
Il legame F-s di queste molle sarà, quindi, del tipo:
-80
-60
-40
-20
0
20
40
60
80
-9 -7 -5 -3 -1 1 3 5 7 9
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle diagonali spandrel
legame
costitutivo
molle
diagonali
CALIBRAZIONE MOLLE DELLA MURATURA
98
Figura 4-23: in rosso, le molle diagonali spandrel
Nel modello si sono inseriti, quindi, i seguenti parametri:
Anche in questo caso, si è inserito il parametro “beta=0.8” il quale è indice di danno
della muratura: infatti, appena la fascia di piano inizia a fessurare, ci sarà un degrado di
```
resistenza (il valore “0.8” si è ricavato ad hoc di modo che i risultati da modello
```
```
coincidano con quelli della la prova sperimentale). Il danneggiamento entrerà in gioco
```
solo dopo che il taglio agente avrà superato il valore di picco del legame costitutivo della
muratura, ovvero appena essa inizierà a fessurarsi.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
99
4.4.4 Calibrazione molle verticali spandrel
Esse saranno dimensionate per il meccanismo di rottura a taglio-scorrimento.
Per la taratura di queste molle si è utilizzato, come per il caso delle molle traversali del
maschio murario, l’attrito alla Mohr-Coulomb nella quale entrano in gioco le forze Fy dei
tiranti come forze di compressione. La resistenza a taglio in senso verticale è stata
maggiorata tramite un coefficiente giacché la muratura resiste molto bene a taglio
scorrimento in senso verticale, considerando anche un effetto di “incatenamento” tra i
vari mattoni.
Il taglio ultimo per scorrimento è stato ricavato come:
ATTRITO MOHR COULOMB
coesione c 0,2 N/mm2
Am 380000 mm2
coeff attrito phi 0,5
Ftiranti 146,006 kN
Pm 146,006 kN
coeff maggiorativo per taglio verticale 10
num molle 2
```
Tm(P) 745,014 kN
```
delta max 7,49 mm
Le molle verticali spandrel seguiranno, dunque, la seguente legge F-s:
-1000
-500
0
500
1000
-16 -6 4 14
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle verticali spandrel
legame
costitutivo
molle
verticali
spandrel
CALIBRAZIONE MOLLE DELLA MURATURA
100
Figura 4-24: in rosso, le molle verticali spandrel
Nel modello si sono inseriti, quindi, i seguenti parametri:
Per le molle verticali spandrel si è deciso di inserire due molle con legge costitutiva
simmetrica. Altrimenti, si sarebbe potuto inserire un'unica molla con caratteristiche
resistenti “doppie”.
OSS. Come già scritto nella presente tesi per le molle trasversali del maschio murario,
anche in questo caso si sarebbe potuta assegnare una legge costitutiva in funzione del
carico P agente nel modello, ovvero “collegare” la risposta delle molle verticali spandrel
```
(dovuta all’attrito di Mohr-Coulomb) alla reazione agente nelle molle orizzontali
```
```
spandrel (per presso-flessione). Si sarebbe inoltre potuto aumentare il numero di molle
```
orizzontali spandrel per avere una migliore precisione sul numero di molle in trazione e
in compressione. Ciò non è stato fatto per diminuire l’onere computazionale del
modello.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
101
4.5 Calibrazione beam per il fuori piano
Per la calibrazione dei beam fuori-piano, si fa riferimento alle formule delle NTC’08 per il
momento ultimo delle murature nel fuori piano. La seguente modellazione di questi
beam è, dunque, cautelativa ma comunque necessaria per avere un’ulteriore resistenza
della muratura e minori spostamenti del solaio.
Questi elementi saranno inseriti in corrispondenza dei nodi laterali del solaio non
vincolati dai due muri laterali resistenti al sisma e saranno tarati, quindi, in base alla loro
area di influenza. Di conseguenza, più il solaio è discretizzato, più il modello sarà
realistico giacché ci saranno diversi beam che contribuiscono alla resistenza nel fuori
piano.
```
Dalle NTC’08 (capitolo 7.8.2.2.3 “Pressoflessione fuori piano”) si ha che: “Il valore del
```
momento di collasso per azioni perpendicolari al piano della parete è calcolato
assumendo un diagramma delle compressioni rettangolare, un valore della resistenza
pari a 0,85 fd e trascurando la resistenza a trazione della muratura.”
```
Di conseguenza, si ottiene la seguente formula (simile alla verifica a pressoflessione nel
```
```
piano, in cui si è sostituito lo spessore “t” alla larghezza “l”):
```
```
( ) ( )
```
```
Dove:
```
- Mult: è il momento corrispondente al collasso per pressoflessione;
- l: è la larghezza complessiva alla parete (inclusiva della zona tesa);
- t: è lo spessore della zona compressa della parete;
- σ0: è la tensione normale media, riferita all’area totale della sezione (σ0=P/(lt),
```
con P forza assiale agente positiva se di compressione). Se P è di trazione, Mult=0;
```
- fd=fk/γM: è la resistenza a compressione di calcolo della muratura.
CALIBRAZIONE MOLLE DELLA MURATURA
102
Dopo aver calcolato il valore del momento ultimo della parete in muratura, si è passati,
quindi, alla taratura dei parametri che saranno inseriti nel modello.
Per le caratteristiche inerziali da inserire nel modello, si valuta la rigidezza del sistema
```
come se fosse una mensola (incastrata alla base e libera in sommità) con un momento
```
esterno applicato pari a Mult:
Figura 4-25: schema utilizzato per la rigidezza dei beam assegnati al modello
La struttura è perciò isostatica e, dunque, il diagrammi dei momenti è costante.
I valori di vA e ϕA possono essere ricavati dal Principio dei Lavori Virtuali, ottenendo
quindi i seguenti risultati:
```
ovvero:
```
-M
φA
vA
φA
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
103
```
Infine, si è ricavato il valore del momento di inerzia (unica incognita) da inserire nel
```
modello tale per cui con il momento ultimo ricavato precedentemente tramite le Norme
Tecniche, si raggiunga uno spostamento ultimo della muratura fuori piano vA pari a
```
dove h=altezza del muro (3m) e =deformazione angolare ultima assunta pari
```
allo 0.1%.
Per il calcolo del carico verticale agente, si è considerato metà peso proprio del muro
```
non portante (lungo 5m ma preso con una lunghezza di influenza pari 2.5m),
```
supponendo che al centro del muro vi sia una fascia di piano alta 1m e lunga 1.5m.
Essendo il muro non portante, non è stato calcolato alcun carico verticale aggiuntivo
dovuto al solaio, trascurando così l’effetto dell’ingranamento sugli spigoli della scatola
muraria.
Dunque, sono stati ricavati i seguenti valori:
t 380 mm
```
l metà parete (l di influenza) 2500 mm
```
σ0 0.032 N/mm2
fk 7.92 N/mm2
Mu 5820053.583 Nmm
E 2910 N/mm2
```
ϑu (deform ang ultima) 0.001
```
h altezza 3000 mm
v spost ultimo fuori piano 3.00 mm
```
I=momento d’inerzia 3000027620 mm4
```
Tu 1.940 kN
```
Da “OpenSees Command Language Manual” (di S. Mazzoni, F. McKenna, M.H. Scott, G.L.
```
```
Fenves, et al. 2007), si è scelto di utilizzare come materiale: “Elastic Beam Column
```
Element”, ovvero i beam per il fuori piano della muratura sono stati modellati come
elastici lineari. Per la definizione di tutti i parametri e approfondimenti sul materiale
scelto, si rimanda al manuale del software.
CALIBRAZIONE MOLLE DELLA MURATURA
104
Nel modello si sono inseriti, quindi, i seguenti parametri:
OSS. L’ipotesi che il beam per il fuori piano rimanga in campo elastico è sicuramente
un’approssimazione soprattutto perché esso continuerà a deformarsi per qualsiasi
valore di spostamento del solaio.
Ciò è accettabile in quanto è stata prevista la presenza di tiranti anche per i muri non
portanti i quali daranno una resistenza a trazione aggiuntiva non considerata nella
formula da Normativa. Inoltre, come si vedrà nei casi studio del presente elaborato, si è
notato che questi beam per il fuori piano avranno una spostamento in sommità di molto
```
inferiore allo spostamento limite per il ribaltamento del pannello nel fuori piano (pari a
```
```
circa metà dello spessore).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
105
5 TIPOLOGIE DI RINFORZO DEI SOLAI E MODELLAZIONE
In questo capitolo verranno analizzate brevemente le tipologie di rinforzi di solai in legno
utilizzate poi nel seguito del presente elaborato.
Per una trattazione più dettagliata riguardo la modellazione del solaio e per un maggior
numero di tipologie di rinforzo, si rimanda all’elaborato di tesi di M. Tonon dal titolo:
“Effetti del rinforzo di solai in legno nel miglioramento sismico di edifici esistenti in
muratura - modellazione numerica dei solai”.
Nella presente tesi si è voluto studiare il comportamento della muratura considerando in
particolare due diverse tipologie di consolidamento di solai lignei, comunemente
utilizzate nelle ristrutturazioni di edifici storici, i quali si diversificano per il grado di
irrigidimento che conferiscono al solaio stesso:
- Solaio rinforzato con doppio tavolato in legno a 45°;
- Solaio rinforzato con soletta in calcestruzzo armato.
Si sono scelte queste tipologie di rinforzo per rappresentare i due casi limite, ovvero la
```
stessa struttura verrà analizzata sia con solaio flessibile (col tavolato in legno a 45°) che
```
```
con solaio rigido (con soletta in calcestruzzo). Per le tipologie di solaio con rigidezze
```
intermedie si rimanda nuovamente al già citato elaborato di M. Tonon.
```
Figura 5-1: le due tipologie di consolidamento analizzate (da Piazza, Baldessari et al.)
```
Per entrambe queste due tipologie di consolidamento si sono valutate le rispettive
caratteristiche riproducendone il comportamento, confrontandosi con delle prove
TIPOLOGIE DI RINFORZO DEI SOLAI E MODELLAZIONE
106
```
cicliche effettuate dall’Università di Trento (Piazza, Baldessari e Tomasi, 2008: “The Role
```
```
of in-plane floor stiffness in the seismic behaviour of traditional buildings”).
```
OSS. Come si vedrà in seguito, entrambe le tipologie di rinforzo rendono il solaio
abbastanza rigido. Si rimanda nuovamente all’elaborato di tesi di M. Tonon per lo studio
di solai più flessibili.
5.1 Calibrazione dei solai
La modellazione dei solai viene effettuata con l’ausilio del programma Opensees in cui si
è schematizzato il solaio di dimensioni in pianta di 5,00X4,00 m suddividendolo in moduli
```
rettangolari di lati 2,5X1,5 m realizzati tramite truss infinitamente rigidi (già analizzati nei
```
```
capitoli precedenti). Ogni modulo è caratterizzato da una molla diagonale a cui sono
```
state attribuite le caratteristiche del solaio studiato.
Il solaio così definito è stato vincolato tramite l’applicazione di due cerniere nei nodi alle
estremità del lato di lunghezza maggiore di 5,00 m così da riprodurre fedelmente le
condizioni di vincolo della prova sperimentale.
```
Figura 5-2: schema della prova sperimentale (da Piazza, Baldessari et al.)
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
107
Il comportamento della specifica tipologia di solaio è stato attribuito alle molle diagonali
le quali sono state definite attraverso una subroutine che definisce il ciclo di Peanching4.
I valori del ciclo di Peanching4 sono stati definiti a partire dai dati della prova
sperimentale in modo tale che le molle siano in grado di riprodurre il più fedelmente
possibile il comportamento del solaio osservato nella prova sperimentale.
```
Figura 5-3: Definizione del modello Pinching4 (da S.Mazzoni et al.)
```
```
Questo elemento, preso dal manuale OpenSees (S. Mazzoni et al., 2007) è stato
```
utilizzato per la caratterizzazione delle molle del solaio. Esso è stato scelto perché
permette la modellazione di materiali che rappresentano una risposta carico-
spostamento “pinched” e che mostrano un degrado di resistenza e di rigidezza sotto
carichi ciclici, come nei solai trattati.
TIPOLOGIE DI RINFORZO DEI SOLAI E MODELLAZIONE
108
5.2 Brevi cenni sul solaio con doppio tavolato a 45°
Questo primo metodo di consolidazione del solaio consiste nella realizzazione di una
soletta lignea mediante la posa di un ulteriore tavolato, composto da tavole aventi
sezione 20X3 cm, disposto a 45° rispetto la direzione longitudinale della travatura
esistente. La connessione tra i due tavolati è stata realizzata mediante viti φ6X90 mm:
sono state utilizzate due viti per ogni intersezione tra tavole appartenenti ai due diversi
livelli di tavolato.
Nella tabella sottostante sono riportate sinteticamente tutte le caratteristiche
geometriche e dei materiali utilizzati nella realizzazione di questa tipologia di solaio.
Figura 5-4: Tabella riassuntiva delle caratteristiche del solaio rinforzato con tavolato 45°
```
(da Piazza, Baldessari et al.)
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
109
5.2.1 Prova sperimentale solaio
Dalla prova sperimentale dell’Università di Trento, si è studiato il seguente ciclo
isteretico della tipologia di solaio in analisi, il quale rappresenta la relazione tra forza
applicata e il corrispondente spostamento in mezzeria del solaio:
Figura 5-5: Ciclo di carico-spostamento della prova sperimentale del solaio rinforzato con
```
tavolato a 45° (da Piazza, Baldessari et al.)
```
5.2.2 Modello Numerico del solaio
Come anticipato, i valori caratterizzanti le molle del modello numerico sono stati definiti
a partire dai dati ottenuti dalla prova sperimentale.
Per la modellazione delle molle diagonali del solaio, sono stati tarati così i seguenti
```
parametri per mezzo del programma Excel (il ciclo sperimentale non ha un
```
```
comportamento simmetrico perciò si sono analizzati i due singoli cicli):
```
TIPOLOGIE DI RINFORZO DEI SOLAI E MODELLAZIONE
110
Per la definizione del comportamento del solaio vengono infine definiti i valori
rappresentanti il ciclo di Pinching, ottenuti considerando un comportamento del solaio il
più vicino possibile a quello derivante dalla prova sperimentale.
Per mezzo di questi parametri, inseriti nel calcolatore, si sono ottenuti i risultati visibili
```
dalla figura 5-6: il modello del solaio appena descritto (curva rossa) è rappresentativo sia
```
qualitativamente che quantitativamente del comportamento del solaio della prova
sperimentale.
Figura 5-6: Ciclo isteretico del modello del solaio con tavolato a 45°
Δx F Δl ΔN Δx F Δl ΔN
0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
2.00 80.00 1.25 32.02 2.00 80.00 1.25 32.02
12.00 190.00 7.50 76.04 12.00 190.00 7.50 76.04
46.00 370.00 28.74 148.07 46.00 370.00 28.74 148.07
55.00 30.00 34.36 12.01 55.00 30.00 34.36 12.01
VALORI SPERIMENTALI VALORI OPENSEES
CICLO POSITIVO CICLO NEGATIVO
VALORI SPERIMENTALI VALORI OPENSEES
rDispP 0.37 rDispN 0.24
rForceP 0.27 rForceN 0.25
uForceP -0.07 uForceN -0.03
CICLO DI PINCHING4
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
111
5.3 Brevi cenni sul solaio con soletta in c.a.
Questa tipologia di rinforzo del solaio è una delle prime adottate in ordine cronologico e
```
si basa sul metodo proposto da Turrini e Piazza (1983) consistente nella realizzazione di
```
una soletta di calcestruzzo armato al di sopra dell’assito esistente.
Di seguito, è riportato un breve riassunto dell tipologia di rinforzo adottata nella prova.
La soletta di calcestruzzo è di spessore di 5 cm e viene collegata alle travi componenti il
solaio tramite barre di acciaio edile oppure, di recente utilizzo, mediante connettori di
tipo piolo/rampone di diverse fattezze e produzioni. Per completare l’opera è necessario
ancorare la soletta alla muratura esistente disponendo barre in acciaio edile B450C di
diametro 16 mm in parte annegate nel getto di calcestruzzo n parte infisse nel muro con
angolazione negativa di 45°. In particolare l’infissione nella muratura avviene previa
foratura della muratura stessa con riempimento di malta bi-componente ad alta
resistenza.
Le caratteristiche del solaio in esame sono riportate nella seguente tabella riassuntiva.
Figura 5-7: Tabella riassuntiva delle caratteristiche del solaio rinforzato con soletta in c.a.
```
(da Piazza, Baldessari et al.)
```
TIPOLOGIE DI RINFORZO DEI SOLAI E MODELLAZIONE
112
5.3.1 Prova sperimentale solaio
Dalla prova sperimentale dell’Università di Trento, si è studiato il seguente ciclo
isteretico della tipologia di solaio in analisi, il quale rappresenta la relazione tra forza
applicata e il corrispondente spostamento in mezzeria del solaio:
Figura 5-8: Ciclo di carico-spostamento della prova sperimentale del solaio rinforzato con
```
soletta in calcestruzzo armato (da Piazza, Baldessari et al.)
```
Come si po’ osservare dal grafico questa tipologia di consolidazione del solaio risulta
essere più rigida della precedente con rinforzo con tavolato a 45°.
5.3.2 Modello Numerico del solaio
Come anticipato, i valori caratterizzanti le molle del modello numerico sono stati definiti
a partire dai dati ottenuti dalla prova sperimentale. Per un miglior dettaglio della
modellazione numerica del solaio, si rimanda alla già citata tesi di M.Tonon.
Per la modellazione delle molle diagonali del solaio, sono stati tarati così i seguenti
```
parametri per mezzo del programma Excel (il ciclo sperimentale non ha un
```
```
comportamento simmetrico perciò si sono analizzati i due singoli cicli):
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
113
Per la definizione del comportamento del solaio vengono infine definiti i valori
rappresentanti il ciclo di Pinching, ottenuti considerando un comportamento del solaio il
più vicino possibile a quello derivante dalla prova sperimentale.
Per mezzo di questi parametri, inseriti nel calcolatore, si sono ottenuti i risultati visibili
```
nella figura 5-9: il modello del solaio appena descritto (curva rossa) è rappresentativo sia
```
qualitativamente che quantitativamente del comportamento del solaio della prova
sperimentale.
Figura 5-9: Ciclo isteretico del modello del solaio con tavolato a 45°
Δx F Δl ΔN Δx F Δl ΔN
0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
0.50 43.00 0.31 17.21 -0.30 -43.00 -0.19 -17.21
3.70 280.00 2.31 112.05 -1.50 -250.00 -0.94 -100.05
7.00 385.00 4.37 154.08 -5.20 -450.00 -3.25 -180.09
12.50 385.00 7.81 154.08 -10.50 -450.00 -6.56 -180.09
CICLO POSITIVO CICLO NEGATIVO
VALORI SPERIMENTALI VALORI OPENSEES VALORI SPERIMENTALI VALORI OPENSEES
rDispP 0.2 rDispN 0.18
rForceP 0.26 rForceN 0.22
uForceP -0.11 uForceN -0.1
CICLO DI PINCHING4
ESEMPIO PARETE DI 4.5m NEL PIANO X-Y
114
6 ESEMPIO PARETE DI 4.5m NEL PIANO X-Y
```
Nel presente paragrafo, si presenta la modellazione di un muro di lunghezza 4.5m (nel
```
```
piano) comprensivo di due maschi murari di lunghezza 1.5m e altezza 3m cadauno,
```
collegati in sommità da una fascia di piano di lunghezza di 1.5m e altezza 1m. Si è
```
prevista, infatti, la presenza di un apertura di altezza 2m (per un’eventuale finestra o
```
```
porta).
```
Per questo esempio, si è eseguita un’analisi di tipo Push-over con uno spostamento
```
massimo in sommità pari a 20mm (valore limite del collasso del maschio murario).
```
```
Nel proseguo della presente tesi, questo modulo (maschio + fascia di piano + maschio)
```
sarà ripetuto per tutta la lunghezza del muro.
Per questo esempio, ci si è rifatti alla prova sperimentale MI3 già vista nei capitoli
```
precedenti. Come carico verticale agente nei nodi dei soli maschi murari (si veda figura
```
```
sottostante), si è preso come da prova una compressione di σm=1.20MPa, pari a 342KN
```
su ogni nodo. A questo carico esterno è stato sommato il peso proprio del singolo
maschio e un aliquota del peso proprio della fascia di piano.
```
Figura 6-1: Macromodello utilizzato per l’esempio; in nero, la numerazione dei nodi e le
```
```
quote (in mm); in blu, la numerazione dei truss infinitamente rigidi inseriti nel modello.
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
115
Per un motivo puramente di programmazione, è stato creato un distacco infinitesimale
```
tra i blocchi (maschio/fascia di piano) e tra maschio e vincoli. Ciò è stato fatto per
```
```
consentire l’inserimento delle molle assiali (le molle trasversali hanno comunque un
```
```
angolo molto piccolo). Analogamente, la fascia di piano è stata ridotta in lunghezza di
```
1mm per parte per poter inserire le rispettive molle di collegamento con i due maschi
murari.
In figura 6-2, si sono rappresentate le molle implementate nell’esempio. Esse hanno i
seguenti colori:
- molle assiali in azzurro;
- molle trasversali in verde;
- molle diagonali in blu;
- molle verticali spandrel in viola;
- molle orizzontali spandrel in nero;
- molle diagonali spandrel in rosso.
Figura 6-2: molle implementate nel modello
ESEMPIO PARETE DI 4.5m NEL PIANO X-Y
116
OSS. La numerazione di tutti i nodi e di tutti gli elementi servirà, come vedremo, sia per
la modellazione che per i file di output del programma con i quali si potrà osservare
```
(mediante foglio di calcolo) la tipologia di rottura e il comportamento dell’intero muro.
```
In questo capitolo, per semplicità, non si mostreranno i dati di input inseriti per la
```
modellazione delle singole molle (comunque già presenti nei capitoli precedenti).
```
Dal capitolo 6.1 verrà rappresentato lo “sfruttamento” della singola molla del singolo
elemento per mezzo di grafici Excel. Tutto ciò si farà solo per quest’esempio per una
```
migliore chiarezza espositiva (nei successivi saranno rappresentati solo i grafici più
```
```
caratteristici).
```
```
La muratura è stata modellata con i seguenti parametri di resistenza (valori ricavati dalle
```
```
prove sperimentali viste nei capitoli precedenti per murature esistenti):
```
resist media a compressione della muratura fu -7.92 Mpa
resist a trazione della muratura ft 0.1 Mpa
```
mod elast normale muratura (a σ=0,33fu) E 2910 Mpa
```
deform ultima compressione=3*εcy εcu 3*εcy adim
deform ultima trazione=1,5*εty εtu 1,5*εty adim
resist media a taglio a compressione nulla τ0 0.1 Mpa
mod elast tangenziale muratura G 875 Mpa
20%*G Gt 175 Mpa
coeff di coesione c 0.2 Mpa
coeff di attrito φ 0.5 adim
peso specifico muratura w 24 kN/m3
fasce di piano
```
fhd=50%*fu fhd -3.96 Mpa
```
φ tiranti φ 16 mm
A singola tiranti A 201.0619298 mm2
fyd fyd 275 Mpa
forza da applicare nel modello F 55292.0307 N
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
117
6.1 Molle Maschio Primo
- Molle assiali:
Da questo grafico Forza assiale-spostamento si evince che le molle di quest’elemento
rimangono sempre compresse e in ramo elastico, ovvero non c’è rottura per presso-
flessione né per ribaltamento.
- Molle trasversali:
Da questo grafico Forza assiale-spostamento si evince che le molle di quest’elemento
rimangono in ramo elastico, ovvero non c’è rottura per taglio-scorrimento.
-2500
-2000
-1500
-1000
-500
0
500
-14.5 -9.5 -4.5 0.5
```
Sforzo Assiale (kN)
```
```
Deformazione (mm)
```
molle assiali maschio 1
legame costitutivo
molle verticali
elemento 25
elemento 26
-400
-200
0
200
400
-20 -10 0 10 20
```
Sforzo assiale (kN)
```
```
Deformazione (mm
```
molle trasversali maschio 1
legame costitutivo
molle orizzontali
elemento 29
elemento 30
ESEMPIO PARETE DI 4.5m NEL PIANO X-Y
118
- Molle diagonali:
Da questo grafico Forza assiale-spostamento si evince che le molle diagonali sono
```
entrate in crisi, ovvero il maschio primo si fessura diagonalmente (si ha rottura per
```
```
taglio-fessurazione diagonale).
```
OSS. Si è notato che le molle diagonali delle zone di intersezione fra maschi murari e
fasce di accoppiamento rimangono nel ramo elastico.
Nel capitolo 6.4, esse saranno denominate “molle diagonali superiori” e verranno
modellate con elementi elastici per diminuire l’onere computazionale del modello.
-150
-100
-50
0
50
100
150
-6 -4 -2 0 2 4 6
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle diagonali maschio 1
Serie1
elemento 33
elemento 34
elemento 35
elemento 36
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
119
6.2 Molle Fascia di Piano
- Molle orizzontali spandrel:
Da questo grafico Forza assiale-spostamento si evince che le molle orizzontali spandrel
sono entrate in crisi, ovvero lo spandrel si rompe per trazione nell’elemento 48, ovvero il
taglio dovuto al sisma supera la forza di snervamento dei trefoli. Il tratto discendente
della curva viola in figura, significa che l’elemento continua a resistere a compressione.
- Molle verticali spandrel:
Da questo grafico Forza assiale-spostamento si evince che le molle di quest’elemento
rimangono ampiamente in ramo elastico, ovvero non c’è rottura per taglio-scorrimento
tra maschi e fascia di piano.
-1200
-1000
-800
-600
-400
-200
0
200
-10 -8 -6 -4 -2 0 2
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle orizzontali spandrel
elemento 45
elemento 46
elemento 47
elemento 48
-600
-400
-200
0
200
400
600
-16 -6 4 14
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle verticali spandrel
elemento 49
elemento 50
elemento 51
elemento 52
ESEMPIO PARETE DI 4.5m NEL PIANO X-Y
120
- Molle diagonali spandrel:
Da questo grafico Forza assiale-spostamento si evince che le molle diagonali spandrel
hanno iniziato a fessurare ma non hanno raggiunto la rottura.
OSS. Da questi grafici delle “molle spandrel” si intuisce che i tiranti sono dimensionati in
```
modo ottimale dato che entrano in crisi contemporaneamente sia i maschi murari (come
```
```
osservato nel capitolo precedente e come vedremo nel capitolo successivo) che la fascia
```
di piano.
-100
-50
0
50
100
-9 -7 -5 -3 -1 1 3 5 7 9
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle diagonali spandrel
legame costitutivo molle
diagonali
elemento 53
elemento 54
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
121
6.3 Molle Maschio Secondo
- Molle assiali:
Da questo grafico Forza assiale-spostamento si evince che le molle di quest’elemento
rimangono sempre compresse e in ramo elastico, ovvero non c’è rottura per presso-
flessione né per ribaltamento, analogamente al “maschio primo”.
- Molle trasversali:
Da questo grafico Forza assiale-spostamento si evince che le molle di quest’elemento
rimangono in ramo elastico, ovvero non c’è rottura per taglio-scorrimento,
analogamente al “maschio primo”.
-2500
-2000
-1500
-1000
-500
0
500
-14.5 -9.5 -4.5 0.5
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle assiali maschio 2
legame costitutivo
molle verticali
elemento 27
elemento 28
-300
-200
-100
0
100
200
300
-20 -10 0 10 20
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle trasversali maschio 2
legame costitutivo
molle orizzontali
elemento 31
elemento 32
ESEMPIO PARETE DI 4.5m NEL PIANO X-Y
122
- Molle diagonali:
Da questo grafico Forza assiale-spostamento si evince che le molle diagonali sono
```
entrate in crisi, ovvero il maschio secondo si fessura diagonalmente (si ha rottura per
```
```
taglio-fessurazione diagonale).
```
OSS. Dal confronto tra questo grafico e quello del “maschio primo” si nota il fatto che il
maschio 1 si fessura diagonalmente prima in quanto ha degli spostamenti maggiori: ciò è
dovuto al fatto che il taglio agente sulla fascia di piano è maggiore della resistenza a
snervamento dei tiranti inseriti e lo spandrel si fessura.
Ciò si è potuto osservare solo perché l’analisi è di tipo pushover. Se si fosse eseguita
```
un’analisi diversa (ad esempio un’analisi ciclica), le molle diagonali dei maschi si
```
sarebbero comportate allo stesso modo.
-150
-100
-50
0
50
100
150
-6 -4 -2 0 2 4 6
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle diagonali maschio 2
Serie1
elemento 39
elemento 40
elemento 41
elemento 42
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
123
6.4 Calibrazione molle diagonali superiori elastiche
Figura 6-3: cerchiate in rosso, molle diagonali superiori analizzate nel presente paragrafo
Dai risultati dell’analisi Pushover dell’esempio si è notato, inoltre, che le molle diagonali
della parte superiore dei maschi murari in figura sopra rimangono sempre nel ramo
elastico.
Infatti si sono ottenuti come risultati per le molle diagonali superiori i seguenti:
-60
-40
-20
0
20
40
60
-6 -4 -2 0 2 4 6
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
Molle diagonali superiori maschio 1 - PushOver
Serie1
elemento 37
elemento 38
ESEMPIO PARETE DI 4.5m NEL PIANO X-Y
124
Come precedentemente affermato, si nota dal grafico soprastante che entrambe le
molle diagonali delle zone di intersezione fra maschi murari e fasce di accoppiamento
rimangono in campo elastico.
Ciò ha riscontri anche nella realtà in quanto la maggior parte delle strutture in muratura
che collassano per taglio-fessurazione diagonale denotano la formazione di fessure solo
nella parte centrale delle pareti.
Per questo motivo, per ridurre ulteriormente l’onere computazionale del modello
implementato dal programma di calcolo OpenSees, si è deciso di inserire per le molle
diagonali “superiori” un legame costitutivo elastico.
```
Le molle sono state tarate con un legame costitutivo del tipo in figura (linea rossa) di
```
modo che seguano il tratto elastico delle altre molle:
Nel modello queste molle sono state inserite nel seguente linguaggio:
```
Nel prosieguo della presente tesi (anche per gli esempi successivi) si utilizzerà questa
```
tipologia di materiale per le molle diagonali superiori di tutti maschi murari
```
(controllando comunque che le molle rimangano all’interno del range elastico).
```
-60
-40
-20
0
20
40
60
-10 -8 -6 -4 -2 0 2 4 6 8 10
```
sforzo assiale (kN)
```
```
Deformazione (mm)
```
Molle diagonali maschio
comportamento reale
comportamento elastico
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
125
6.5 Comportamento globale della parete
Di seguito si riporta il grafico Taglio-spostamento dell’intero muro di 4.5m. Nel grafico è
```
presente in ascissa lo spostamento in sommità (ci si è riferiti al nodo 24 del “maschio
```
```
primo”) e in ordinata il taglio alla base, preso come somma di tutte le reazioni in X dei
```
nodi alla base di entrambi i maschi murari.
Dal grafico si nota che gli spostamenti della prima parte della curva sono negativi.
Questo dipende dal fatto che si sono inserite nel modello delle forze di compressione Fy
dovute ai trefoli, le quali deformano le molle orizzontali dello spandrel.
Un’altra osservazione che si può fare riguardo a questi risultati, è che la forza di taglio
massima che può essere sopportata dal muro analizzato è all’incirca pari alla somma
delle forze ultime di taglio-fessurazione diagonale dei due maschi murari. Infatti, si è
```
ricavato:
```
```
2 x Taglio ultimo singolo maschio (valore calcolato) 351.0015 kN
```
```
Tmax alla base (valore ricavato da modello) 345.84 kN
```
Da ciò si osserva che il modello implementato è affidabile in quanto i valori teorici e
```
quelli numerici si discostano di poco (presumibilmente per il fatto che in realtà la fascia
```
```
di piano non è infinitamente rigida ma bensì si deforma).
```
-50.00
0.00
50.00
100.00
150.00
200.00
250.00
300.00
350.00
400.00
-5.00 0.00 5.00 10.00 15.00 20.00 25.00
```
Taglio alla base (KN)
```
```
Displacement in sommità (mm)
```
Andamento muro 4.5m - Pushover
modello
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
126
7 CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
Nel presente paragrafo, si presenta la modellazione di un piccolo edificio di pianta
```
4.5x5m con due muri laterali di lunghezza 4.5m (entrambi i muri con ai lati due maschi
```
```
murari collegati da una fascia di piano, come nell’esempio precedente) e il solaio in
```
legno ad un’altezza di 3m.
Il presente caso studio è stato analizzato in due modi in base alla tipologia di rinforzo del
```
solaio:
```
- Solaio rinforzato con doppio tavolato in legno a 45°;
- Solaio rinforzato con soletta in calcestruzzo armato.
Inoltre, i carichi verticali assegnati sono stati ricavati per mezzo di un’analisi dei carichi
con una combinazione di carico sismico come da NTC’08. I due muri laterali sono
entrambi paralleli all’asse X, asse lungo il quale si sono applicate le sollecitazioni da
sisma.
Figura 7-1: pianta dell’edificio e direzione sisma
```
Quindi, sono stati tarati dei beam con caratteristiche meccaniche e di resistenza (già
```
```
analizzate nel capitolo 4.5) per considerare anche la presenza di pareti parallele all’asse
```
Y nel fuori-piano della muratura che riducono gli spostamenti del solaio.
Nell’esempio, sono state assegnate le masse sismiche in corrispondenza dei nodi del
solaio e in sommità dei maschi, in modo da applicare un’unica analisi di tipo Time-
History.
Direzione del sisma
```
(sisma lungo X)
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
127
L’edificio analizzato ha la seguente geometria:
Geometria singolo muro Geometria solaio
h altezza muro 3000 mm lunghezza singolo pannello 1500 mm
w larghezza singolo
pannello 1500 mm
larghezza singolo pannello
del solaio 2500 mm
spessore 380 mm lunghezza solaio 4500 mm
num maschi murari 2 larghezza solaio 5000 mm
l lunghezza totale muro 4500 mm num nodi angolo 4
num nodi massa sismica 4 num nodi laterali muro 4
num nodi angolo 2 num nodi laterali solaio 2
num nodi centrali 2 num nodi centrali 2
altezza spandrel 1000 mm
larghezza spandrel 1500 mm
num spandrel nel muro 1
num muri 2
```
Per il caso in esame, si sono presi i seguenti valori di resistenza della muratura (valori
```
```
ricavati dalle prove sperimentali viste nei capitoli precedenti per murature esistenti):
```
resist media a compressione della muratura fu -7.92 Mpa
resist a trazione della muratura ft 0.1 Mpa
```
mod elast normale muratura (a σ=0,33fu) E 2910 Mpa
```
deform ultima compressione=3*εcy εcu 3*εcy adim
deform ultima trazione=1,5*εty εtu 1,5*εty adim
resist media a taglio a compressione nulla τ0 0.1 Mpa
mod elast tangenziale muratura G 875 Mpa
20%*G Gt 175 Mpa
coeff di coesione c 0.2 Mpa
coeff di attrito φ 0.5 adim
peso specifico muratura w 24 kN/m3
```
Per le fasce di piano si sono utilizzati, invece, i seguenti valori (i tiranti sono stati
```
```
dimensionati col metodo precedentemente definito):
```
Fasce di piano
```
fhd=50%*fu fhd -3.96 Mpa
```
Φ tiranti Φ 18 mm
Atiranti A 254.4690049 mm2
fyd fyd 275 Mpa
num forze n 2
forza da applicare nel modello F 69978.97636 N
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
128
7.1 Geometria della parete e del solaio
Di seguito si riportano le figure 7-2 e 7-3 della parete inserita nel modello:
Figura 7-2: Macromodello utilizzato per l’esempio
Figura 7-3: molle implementate nel modello
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
129
In figura 7-4 si riporta le dimensioni, la numerazione dei nodi, la numerazione dei truss
infinitamente rigidi e quella degli elementi molla del solaio.
Figura 7-4: discretizzazione del solaio
Figura 7-5: immagine 3D dell’edificio in analisi
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
130
7.2 Modello Time-History
Fra le analisi sismiche proposte dalla Normativa Italiana, la più completa e realistica al
fine di valutare gli effetti indotti da un terremoto risulta essere l’analisi dinamica non
lineare, comunemente denominata Time History, in quanto si cerca di ricreare la
risposta della struttura sottoposta ad azione variabile nel tempo. Si parla di analisi non
lineare in quanto si vanno a determinare le capacità della struttura di entrare in campo
plastico e quindi di valutare il grado di dissipazione energetica che la struttura riesce a
fornire. Per effettuare questo tipo di analisi si necessita di una corretta distribuzione
delle masse in gioco e soprattutto di un set di accelerogrammi in grado di definire la
variazione di accelerazione al terreno in modo da determinare con buona probabilità
quale sia l’azione che porta al collasso strutturale.
Si è proceduto quindi andando a determinare un accelerogramma di partenza il quale
verrà via via amplificato in modo da aumentare progressivamente l’azione agente al
terreno e quindi valutare le condizioni degli elementi strutturali al crescere della
forzante.
Tale tipo di analisi per l’esempio trattato non rispetta ciò che la Normativa impone in
quanto si utilizza un solo tipo di accelerogramma, si scala quindi l’accelerazione massima
che avrà luogo sempre allo stesso istante senza utilizzare altre forme di azione
```
sollecitante al terreno. Infatti, per le NTC’08 (§ 7.3.5 “Risposta alle diverse componenti
```
```
dell’azione sismica ed alla variabilità spaziale del moto”): “Se la risposta viene valutata
```
mediante analisi dinamica con integrazione al passo, in campo lineare o non lineare, le
```
due componenti accelerometriche orizzontali (e quella verticale, ove necessario) sono
```
applicate simultaneamente a formare un gruppo di accelerogrammi e gli effetti sulla
struttura sono rappresentati dai valori medi degli effetti più sfavorevoli ottenuti dalle
analisi, se si utilizzano almeno 7 diversi gruppi di accelerogrammi, dai valori più
sfavorevoli degli effetti, in caso contrario. In nessun caso si possono adottare meno di tre
gruppi di accelerogrammi”.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
131
La legislatura italiana ed europea, come riportato in precedenza, impone di utilizzare
almeno 3 accelerogrammi se si considera la situazione più sfavorevole, oppure 7
considerando la media dei valori di sollecitazione ottenuti.
Data la natura di questo elaborato che non si pone di effettuare una verifica sismica di
un edificio ma solo di determinarne le capacità dissipative, si utilizzerà un unico
accelerogramma per il caso studio 1 di edificio di pianta 4.5x5m, e tre accelerogrammi
per il caso studio 2 di edificio di pianta 13.5x10m.
Gli accelerogrammi utilizzati sono stati ricavati come segue.
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
132
7.2.1 Accelerogrammi usati
Per fare ciò si è utilizzato il programma SIMQKE_GR e, in base a quanto definito
```
dall’Eurocodice 8 (§ 3.2.3.1.2 “Accelerogrammi teorici”), si è supposto terreno di tipo A,
```
```
zona sismica 1 ( ) e un coefficiente di smorzamento pari a . Si è
```
utilizzata una durata del sisma di 20 secondi.
Figura 7-6: file di input inseriti nel programma SIMQKE-GR
Si è ricavato il seguente spettro elastico:
Figura 7-7: spettro elastico ricavato da programma SIMQKE-GR
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
133
```
I tre accelerogrammi ricavati da questi dati (per questo esempio si è utilizzato solo il
```
primo accelerogramma, mentre per gli esempi dei capitoli successivi si sono adottati
```
tutti e tre) sono i seguenti:
```
Figura 7-8: grafico della TH-1 da SIMQKE-GR
Figura 7-9: grafico della TH-2 da SIMQKE-GR
Figura 7-10: grafico della TH-3 da SIMQKE-GR
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
134
7.3 Caso studio 1a: edificio 4.5x5m con solaio flessibile
7.3.1 Analisi dei carichi e masse sismiche
```
Le Norme Tecniche per le Costruzioni (§3.2.4, “Combinazione dell’azione sismica con le
```
```
altre azioni”) affermano che: “Gli effetti dell'azione sismica saranno valutati tenendo
```
conto delle masse associate ai seguenti carichi gravitazionali:
∑
Dove i valori dei coefficienti sono riportati nella Tabella 2.5.I”.
Figura 7-11: tabella 2.5.I delle NTC08 – valori dei coefficienti di combinazione.
Dalla tabella soprastante si è preso, quindi, come massa sismica la somma dei pesi
```
permanenti e il 30% del carico da calpestio (che per Normativa è pari a Qk1=2KN/m2).
```
Dati generali
γ muratura 24 kN/m3
g 9.806 m/sec2
massa muratura 2.447481 t/m3
Pesi solaio
q calpestio 2 kN/m2
Ψ2j calpestio 0.3
peso solaio1 3 kN/m2
massa solaio1+calpestio 0.367122 t/m2
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
135
Si è considerato, inoltre, per il valore della massa sismica in corrispondenza dei nodi
```
della muratura anche la massa di metà muro (quindi, massa di metà maschio murario +
```
```
massa della fascia di piano).
```
Si sono ottenute, dunque, le seguenti aliquote di massa per i nodi d’angolo e per i nodi
```
centrali della muratura (denominati “nodi laterali muratura”):
```
Massa da muratura
metà area singolo maschio murario 2250000 mm2
area spandrel 1500000 mm2
spessore muri 380 mm
volume muratura afferente nodi angolo 0.4275 m3
volume muratura afferente nodi laterali 0.7125 m3
massa muratura nodi angolo 1.046298185 t
massa muratura nodi laterali muro 1.743830308 t
Le aliquote di area del solaio afferenti ai diversi nodi del modello, sono:
```
Massa da solai (PP+calpestio)
```
area solaio totale 22.5 m2
area solaio afferente nodi angolo 0.9375 m2
area solaio afferente nodi laterali muro 1.875 m2
area solaio afferente nodi laterali solaio 1.875 m2
area solaio afferente nodi centrali solaio 3.75 m2
Infine si sono sommate le masse così ricavate, ottenendo:
Massa solaio + calpestio + muratura
massa nodi angolo m_ang 1.390475 t
massa nodi laterali muro m_lat_mur 2.432184 t
massa nodi laterali solaio m_lat_sol 0.688354 t
massa solaio nodi centrali m_centr 1.376708 t
Naturalmente, poiché nella presente tesi si vuole analizzare la resistenza di un edificio
esistente al sisma in un’unica direzione, nel modello saranno inserite queste masse sono
```
in direzione del sisma (ovvero in direzione X).
```
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
136
Figura 7-12: nomenclatura dei nodi
Questi valori sono stati in seguito inseriti nel modello come segue:
Inoltre, per l’analisi Time-History saranno assegnate delle forze puntuali verticali agenti
```
sui nodi superiori dei maschi murari (oltre alle già citate forze orizzontali dovute
```
```
all’inserimento dei trefoli). Esse sono state ricavate con lo stesso procedimento per aree
```
di influenza osservato in precedenza per le masse, con alcune differenze:
- si assegna l’intero peso proprio del muro (e non più solo metà massa del maschio
```
murario);
```
Massa nodi laterali
muro
Massa nodi d’angolo
Massa nodi laterali
solaio
Massa solaio
nodi centrali
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
137
- la forza verticale assegnata per i nodi d’angolo calcolata in questo modo (con le
```
aree di influenza) è stata maggiorata considerando l’effetto di “incatenamento”
```
```
che si ha con il muro perpendicolare (quello non portante). Per questo motivo, la
```
forza ricavata precedentemente è stata sommata al peso proprio di metà muro
```
perpendicolare (considerando il peso dell’altra metà di muro come una forza
```
```
verticale aggiuntiva al nodo d’angolo dell’altra parete).
```
Questo secondo punto è stato reso necessario in quanto dal modello si è notato che i
```
maschi tendevano a ribaltare (cosa non verosimile anche per la presenza, appunto, delle
```
```
pareti perpendicolari).
```
Si sono ottenute di conseguenza le seguenti forze verticali, inserite nel modello:
CARICHI per nodo solaio + calpestio + muratura
```
PP muro (maschi+fasce) 95.76 kN
```
PP solaio+calpestio 112.5 kN
Ptot struttura 304.02 kN
Pmuro laterale 85.5 kN
P nodi angolo set P_vert_ang -110835 N
P nodi centrali set P_vert_centr -50670 N
Questi valori sono stati inseriti nel modello come segue:
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
138
7.3.2 Time History
```
Per l’analisi seguente, si è considerato un unico accelerogramma (TH_1) già analizzato
```
nel capitolo 7.2.1.
Nel modello si è inserito il seguente linguaggio di calcolo per l’analisi Time-History:
Il valore cerchiato in rosso in figura è il coefficiente amplificativo dell’accelerazione
utilizzata nel modello.
```
Tutto ciò permette di ricavare la PGA (Peak Ground Acceleration) di progetto per i
```
diversi casi in analisi.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
139
7.3.3 Comportamento globale della parete
In seguito all’analisi Time-History, si è osservato che il modello analizzato entra in crisi
per una PGA superiore a 1.16 g. Per una PGA superiore, il modello non arriva a
convergenza giacché il maschio si rompe per taglio-fessurazione diagonale.
```
Si riportano i seguenti grafici dell’andamento delle molle (per semplicità vengono
```
```
riportati i grafici più caratteristici):
```
- molle diagonali dei maschi murari (dal grafico si nota che queste molle vanno in
crisi, ovvero il maschio murario si rompe per fessurazione diagonale se
```
sollecitato da un sisma con PGA=1.16 g):
```
- molle diagonali della fascia di piano (dal grafico si nota che queste molle vengono
```
molto sollecitate ma rimangono sempre in campo elastico):
```
-60
-40
-20
0
20
40
60
-6 -4 -2 0 2 4 6
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle diagonali maschio 1
Serie1
elemento 33
elemento 34
-100
-50
0
50
100
-10.00 -5.00 0.00 5.00 10.00
```
Sforzo assiale (kN)
```
```
Deformazione (mm)
```
molle diagonali spandrel
elemento 53
elemento 54
legame costitutivo
molle diagonali
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
140
```
OSS: Dai grafici sopra, si deduce che i tiranti sono stati dimensionati in modo corretto
```
affinché avvenga prima la rottura per taglio fessurazione diagonale del maschio rispetto
alla rottura della fascia di piano.
- Elementi beam per il fuori-piano: come si osserva dal grafico sottostante, i beam
elastici dimensionati per dare un ulteriore rigidezza nel fuori-piano hanno uno
spostamento massimo di 13.27 mm. Questo valore è ritenuto accettabile in
quanto lo spostamento ultimo per il ribaltamento fuori dal piano della muratura
```
è pari a metà dello spessore (ovvero pari a 160 mm). L’andamento è il seguente:
```
OSS. Tutti gli altri elementi sono rimasti in ramo elastico, ovvero non sono avvenute
altre tipologie di rottura nel maschio murario. Per una migliore chiarezza espositiva,
questi elementi non vengono riportati nel presente elaborato.
-15
-10
-5
0
5
10
15
```
-20 -10 0 10 20Taglio (KN)
```
```
Spostamento in sommità (mm)
```
Andamento Beam elastici per il fuori piano
beam
elastico
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
141
```
Di seguito si riporta il grafico F-s del muro dell’esempio trattato (i due muri hanno
```
```
ottenuto, com’era da aspettarsi perché simmetrici, risultati analoghi):
```
Dal grafico riportato sopra si nota che la parete non è rimasta nel ramo elastico e,
quindi, contribuisce anch’essa alla dissipazione energetica del sisma.
Confrontando il taglio massimo ricavato dal modello con quello calcolato per la verifica a
```
taglio fessurazione diagonale (per i due maschi della parete) si osserva che i risultati
```
sono molto simili:
Tmax modello 165.90 kN
Tmax design 168.522 kN
-200.00
-150.00
-100.00
-50.00
0.00
50.00
100.00
150.00
200.00
-15 -10 -5 0 5 10 15
```
Taglio alla base del maschio (KN)
```
```
Spostamento in sommità del maschio (mm)
```
Comportamento dell'intero muro
muro
edificio
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
142
Si riporta, inoltre, il grafico della “storia” degli spostamenti in sommità del muro. Esso
avviene tra 0 e 20 sec: nel modello si è voluto indagare il comportamento del muro fino
25 sec, volendo osservare come si comporta la muratura anche negli istanti successivi.
```
Si può notare che gli spostamenti massimi del muro (per una PGA di 1.16 g) sono
```
inferiori al limite massimo del singolo maschio:
disp max modello 11.53 mm
disp max design 16.05 mm
Per una PGA superiore, il modello non arriva a convergenza giacché il maschio si rompe
per taglio-fessurazione diagonale.
OSS. Nel grafico si sono rappresentati gli spostamenti nell’asse parallelo a quello del
sisma dei nodi agli estremi del muro. Essi si discostano in quanto nel modello si sono
inserite delle forze orizzontali costanti dovute ai trefoli: per questo motivo si è inserito
```
nel grafico anche l’andamento degli spostamenti medi della parete (rappresenta il reale
```
```
spostamento del muro).
```
-15
-10
-5
0
5
10
15
0 500 1000 1500 2000 2500
```
Displacement (mm)
```
```
Time (ms)
```
Time History 1 Muratura
disp nodo 9
disp nodo 24
disp medi
parete
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
143
Di seguito, si riporta il grafico in cui in ascissa si riporta lo spostamento del nodo centrale
del solaio in [mm] e in ordinata è presente il taglio alla base dell’intero edificio in *kN]
```
(come somma dei tagli dei due muri):
```
```
Di seguito, si rappresentano gli spostamenti del nodo centrale del solaio (in viola) e gli
```
```
spostamenti della parete (in verde):
```
Si può osservare che inizialmente il solaio ha spostamenti più elevati rispetto a quelli dei
```
muri (perché più flessibile). In seguito, però, la parete inizia a fessurare e ad avere una
```
rigidezza simile a quella del solaio fino a ottenere spostamenti paragonabili a quelli del
nodo centrale.
-400
-300
-200
-100
0
100
200
300
400
-15 -10 -5 0 5 10 15
```
Taglio alla base dell'edificio (KN)
```
```
Spostamento del nodo centrale del solaio (mm)
```
Forza-Spostamento
forza-spostamento
-15
-10
-5
0
5
10
15
0 500 1000 1500 2000 2500
```
Displacement (mm)
```
```
Time (ms)
```
Time History 1 Muratura
disp solaio
nodo centrale
```
(mm)
```
disp medi
parete
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
144
7.4 Caso studio 1b: edificio 4.5x5m con solaio rigido
7.4.1 Analisi dei carichi e masse sismiche
Si è calcolato un nuovo valore di massa sismica, considerando l’aumento di peso proprio
del solaio dovuto dall’introduzione della soletta di 5cm di calcestruzzo rispetto al caso
studio 1a. La tipologia di rinforzo del solaio in legno con soletta in calcestruzzo è stata
definita precedentemente nel capitolo 5.3.
Dati generali
γ muratura 24 kN/m3
g 9.806 m/sec2
massa muratura 2.447481 t/m3
Pesi solaio
q calpestio 2 kN/m2
Ψ2j calpestio 0.3
peso solaio 4.25 kN/m2
massa solaio+calpestio 0.4946 t/m2
Seguendo lo stesso procedimento trattato nel caso studio 1a precedente, si sono ricavati
i seguenti valori di massa sismica, in seguito inseriti nel modello:
massa solaio 5 + calpestio + muratura
Massa nodi angolo m_ang 1.51 t
Massa nodi laterali muro m_lat_mur 2.671 t
massa nodi laterali solaio m_lat_sol 0.927 t
massa solaio nodi centrali m_centr 1.855 t
Naturalmente, poiché nella presente tesi si vuole analizzare la resistenza di un edificio
esistente al sisma in un’unica direzione, nel modello saranno inserite queste masse sono
```
in direzione del sisma (ovvero in direzione X).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
145
Figura 7-13: nomenclatura dei nodi
Per l’analisi delle forze verticali, si è seguito il medesimo procedimento ricavato nel caso
studio 1a, ottenendo:
CARICHI per nodo solaio 5+ calpestio + muratura
```
PP muro (maschi+fasce) 95.76 kN
```
```
PP solaio+calpestio (senza phi) 140.625 kN
```
Ptot struttura 332.145 kN
Pmuro laterale 102.6 kN
P nodi angolo set P_vert_ang -130278.75 N
P nodi centrali set P_vert_centr -55357.5 N
Massa nodi laterali
muro
Massa nodi d’angolo
Massa nodi laterali
solaio
Massa solaio
nodi centrali
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
146
7.4.2 Time History
```
Per l’analisi seguente, si è considerato un unico accelerogramma (TH_1) già analizzato
```
nel capitolo 7.2.1.
Nel modello si è inserito il seguente linguaggio di calcolo per l’analisi Time-History:
Il valore cerchiato in rosso in figura è il coefficiente amplificativo dell’accelerazione
utilizzata nel modello.
```
Tutto ciò permette di ricavare la PGA (Peak Ground Acceleration) di progetto per i
```
diversi casi in analisi.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
147
7.4.3 Comportamento globale della parete
In seguito all’analisi Time-History, si è osservato che il modello analizzato entra in crisi
per una PGA superiore a 1.02 g. Per una PGA superiore, il modello non arriva a
convergenza giacché il maschio si rompe per taglio-fessurazione diagonale.
Per questo caso studio 1b, non si riportano i grafici dell’andamento delle molle per una
```
migliore chiarezza espositiva (le molle che vanno in crisi sono le molle diagonali della
```
```
pareti murarie).
```
```
Di seguito si riporta il grafico F-s del muro dell’esempio trattato (i due muri hanno
```
```
ottenuto, com’era da aspettarsi perché simmetrici, risultati analoghi):
```
Dal grafico riportato sopra si nota che la parete non è rimasta nel ramo elastico e,
quindi, contribuisce anch’essa alla dissipazione energetica del sisma.
Confrontando il taglio massimo ricavato dal modello con quello calcolato per la verifica a
```
taglio fessurazione diagonale (per i due maschi della parete) si osserva che i risultati
```
sono molto simili:
Tmax modello 170.20 kN
Tmax design 172.6982 kN
-200.00
-150.00
-100.00
-50.00
0.00
50.00
100.00
150.00
200.00
-20 -15 -10 -5 0 5 10 15
Taglio alla base del maschio
```
Spostamento in sommità del maschio (mm)
```
Comportamento della parete
muro
edificio
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
148
Si riporta, inoltre, il grafico della “storia” degli spostamenti in sommità del muro. Esso
avviene tra 0 e 20 sec: nel modello si è voluto indagare il comportamento del muro fino
25 sec, volendo osservare come si comporta la muratura anche negli istanti successivi.
Per una PGA superiore, il modello non arriva a convergenza giacché il maschio si rompe
per taglio-fessurazione diagonale.
Di seguito, si riporta il grafico in cui in ascissa si riporta lo spostamento del nodo centrale
del solaio in [mm] e in ordinata è presente il taglio alla base dell’intero edificio in *KN+
```
(come somma dei tagli dei due muri):
```
-20
-15
-10
-5
0
5
10
15
0 500 1000 1500 2000 2500
```
Displacement (mm)
```
```
Time (ms)
```
Time History 1 Muratura
disp parete
-400
-300
-200
-100
0
100
200
300
400
-20 -10 0 10 20
```
Taglio alla base dell'edificio (KN)
```
```
Spostamento del nodo centrale del solaio (mm)
```
Forza-Spostamento
forza-
spostamento
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
149
```
Di seguito, si rappresentano gli spostamenti del nodo centrale del solaio (in viola) e gli
```
```
spostamenti della parete (in verde):
```
Si può notare come gli spostamenti del nodo centrale del solaio e quelli delle pareti
laterali siano molto simili. Ciò è dovuto al fatto che il solaio in legno rinforzato con
soletta in calcestruzzo ha una rigidezza elevata, tale da far compire i medesimi
spostamenti a pareti e solaio.
-20
-15
-10
-5
0
5
10
15
0 500 1000 1500 2000 2500
```
Displacement (mm)
```
```
Time (ms)
```
Time History 1 Muratura
disp solaio
nodo
centrale
```
(mm)
```
disp medi
parete
CASO STUDIO 1: EDIFICIO DI PIANTA 4.5x5m
150
7.5 Conclusioni caso studio 1
Di seguito si presenta il confronto dell’andamento degli spostamenti di pareti e solaio al
variare della PGA.
Figura 7-14: Andamento medio delle pareti per le due tipologie di solaio
Analizzando ciò che mostra il grafico precedente, si nota con interesse che, nel caso di
solaio flessibile, le pareti sono sollecitate dal sisma in maniera minore rispetto al caso
con solaio rigido, ovvero si fessureranno per valori di PGA più elevate.
Il collasso nel caso di consolidamento con soletta in calcestruzzo avviene per valori di
PGA leggermente più bassi: i consolidamenti con tavolato a 45° collassano per
accelerazioni più elevate, sintomo di una maggior, seppur lieve, capacità dissipativa.
In figura 7-15, si rappresenta l’andamento degli spostamenti del nodo centrale del solaio
al variare della PGA per le due diverse tipologie di rinforzo.
0
2
4
6
8
10
12
14
16
18
20
0.75 0.85 0.95 1.05 1.15
```
Spostamento (mm)
```
```
PGA (1/g)
```
Andamento parete
muro solaio
flessibile
muro solaio
rigido
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
151
Figura 7-15: Andamento medio del solaio nei due casi analizzati
Anche in questo caso si nota come il solaio con tavolato a 45° collassa a valori più elevati
di accelerazione di picco.
Di seguito si rappresenta l’andamento della massima differenza degli spostamenti tra il
nodo centrale del solaio e le pareti laterali al variare dell’accelerazione di picco.
Figura 7-16: Andamento medio del solaio nei due casi analizzati
Si nota subito che per entrambi i casi 1a e 1b la differenza tra spostamenti del solaio e
spostamenti della parete rimane pressoché costante al variare della PGA. Tuttavia, la
differenza degli spostamenti nel caso 2a è più elevata rispetto a quella del caso 2b,
sintomo della minore rigidezza del solaio.
0
2
4
6
8
10
12
14
16
18
20
0.75 0.85 0.95 1.05 1.15
```
Spostamento (mm)
```
```
PGA (1/g)
```
Andamento solaio
solaio
flessibile
solaio rigido
0
1
2
3
4
5
6
0.75 0.85 0.95 1.05 1.15
```
Spostamento (mm)
```
```
PGA (1/g)
```
Differenza spostamento solaio - parete
solaio
flessibile
solaio
rigido
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
152
8 CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE
MURI
Nel presente paragrafo, si presenta la modellazione di un edificio di pianta 13.5x10m
```
con due pareti laterali e una parete centrale di lunghezza 13.5m (ogni muro avrà la
```
medesima geometria, lo stesso numero di maschi -cinque- e di fasce di piano -quattro-,
ma diverse caratteristiche di resistenza in quanto diversi sono i carichi verticali tra muro
```
centrale e muri laterali) e il solaio in legno ad un’altezza di 3m.
```
Anche nel presente “caso studio 2”, l’edificio è stato analizzato in due modi in base alla
tipologia di rinforzo del solaio:
- Solaio rinforzato con doppio tavolato in legno a 45°;
- Solaio rinforzato con soletta in calcestruzzo armato.
I carichi verticali assegnati sono stati ricavati per mezzo di un’analisi dei carichi con una
combinazione di carico sismico come da NTC’08. Le tre pareti sono parallele all’asse X,
asse lungo il quale si sono applicate le sollecitazioni da sisma.
Figura 8-1: pianta dell’edificio e direzione sisma
```
Quindi, sono stati tarati dei beam con caratteristiche meccaniche e di resistenza (già
```
```
analizzate nel capitolo 4.5) per considerare anche la presenza di pareti parallele all’asse
```
Y nel fuori-piano della muratura che riducono gli spostamenti del solaio.
Direzione del
```
sisma (sisma
```
```
lungo X)
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
153
Nell’esempio, sono state assegnate le masse sismiche in corrispondenza dei nodi del
solaio e in sommità dei maschi, in modo da applicare un’unica analisi di tipo Time-
History.
L’edificio analizzato ha la seguente geometria:
Geometria singolo muro Geometria solaio
h altezza muro 3000 mm lunghezza singolo pannello 1500 mm
w larghezza singolo
pannello muratura 1500 mm
larghezza singolo pannello solaio
in legno 2500 mm
spessore 380 mm lunghezza solaio 13500 mm
num maschi murari 5 larghezza solaio 10000 mm
l lunghezza totale muro 13500 mm num nodi angolo 4
num nodi massa sismica 10 num nodi laterali muro 16
num nodi angolo 2 num nodi laterali solaio 6
num nodi centrali 8
num nodi laterali solaio su muro/i
centrale/i 2
altezza fasce di piano 1000 mm
```
num nodi centrali (senza muro
```
```
centrale) 16
```
larghezza spandrel 1500 mm
num nodi centrali su muro/i
centrale/i 8
num spandrel nel muro 4
num muri 3
```
Per il caso in esame, si sono presi i seguenti valori di resistenza della muratura (valori
```
```
ricavati dalle prove sperimentali viste nei capitoli precedenti per murature esistenti):
```
resist media a compressione della muratura fu -7.92 Mpa
resist a trazione della muratura ft 0.1 Mpa
```
mod elast normale muratura (a σ=0,33fu) E 2910 Mpa
```
deform ultima compressione=3*εcy εcu 3*εcy adim
deform ultima trazione=1,5*εty εtu 1,5*εty adim
resist media a taglio a compressione nulla τ0 0.1 Mpa
mod elast tangenziale muratura G 875 Mpa
20%*G Gt 175 Mpa
coeff di coesione c 0.2 Mpa
coeff di attrito φ 0.5 adim
peso specifico muratura w 24 kN/m3
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
154
```
Per le fasce di piano si sono utilizzati, invece, i seguenti valori (i tiranti sono stati
```
```
dimensionati col metodo precedentemente definito):
```
Fasce di piano
```
fhd=50%*fu fhd -3.96 Mpa
```
φ tiranti φ 26 mm
A singola tiranti A 530.929 mm2
fyd fyd 275 Mpa
forza da applicare nel modello F 146005.519 N
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
155
8.1 Geometria della parete e del solaio
Figura 8-2: Qui a lato, si rappresentano le
quote della parete di 13.5 m, la
numerazione dei nodi e la numerazione dei
```
truss infinitamente rigidi (in verde) inseriti
```
nel modello di OpenSees.
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
156
Figura 8-3: Qui a lato, si rappresenta la
```
numerazione delle molle (sia dei maschi che
```
```
delle fasce di piano) e la numerazione dei
```
nodi inseriti nel modello di OpenSees.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
157
In figura 8-4 si riportano le dimensioni, la numerazione dei nodi, la numerazione dei
truss infinitamente rigidi e quella degli elementi molla del solaio.
Figura 8-4: discretizzazione del solaio in analisi
Figura 8-5: immagine 3D dell’edificio
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
158
8.2 Caso studio 2a: edificio di pianta 13.5x10m con solaio flessibile
8.2.1 Analisi dei carichi e masse sismiche
Come nel caso studio 1, si è ricavato:
Dati generali
γ muratura 24 kN/m3
g 9.806 m/sec2
massa muratura 2.447481 t/m3
Pesi solaio
q calpestio 2 kN/m2
Ψ2j calpestio 0.3
peso solaio1 3 kN/m2
massa solaio1+calpestio 0.367122 t/m2
massa solaio 1 + calpestio + muratura
massa nodi angolo set m_lat_murlat 1.390 t
massa nodi laterali muro set m_centr_murlat 2.432 t
massa nodi laterali solaio set m_lat_SOL 0.688 t
massa nodi centrali solaio set m_centr_SOL 1.377 t
massa nodi centrali su muro centrale set m_centr_murcentr 3.121 t
massa nodi laterali solaio su muro centrale set m_lat_murcentr 1.735 t
Le masse sismiche sono state inserite nel calcolatore come segue:
Figura 8-6: nomenclatura dei nodi
Massa nodi laterali
muro centrale
Massa nodi centrali
muro centrale
Massa nodi
laterali muro
Massa
nodi
d’angolo
Massa nodi laterali
solaio
Massa nodi
centrali solaio
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
159
Questi valori sono stati in seguito inseriti nel modello come segue:
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
160
Saranno assegnate, inoltre, delle forze puntuali verticali agenti sui nodi superiori dei
```
maschi murari (oltre alle già citate forze orizzontali dovute all’inserimento dei tiranti).
```
Esse sono state ricavate con lo stesso procedimento per aree di influenza osservato in
precedenza per le masse, con alcune differenze:
- si assegna l’intero peso proprio del muro (e non più solo metà massa del maschio
```
murario);
```
- la forza verticale assegnata per i nodi d’angolo calcolata in questo modo (con le
```
aree di influenza) è stata maggiorata considerando l’effetto di “incatenamento”
```
```
che si ha con il muro perpendicolare (quello non portante). Per questo motivo, la
```
forza ricavata precedentemente è stata sommata al peso proprio di metà muro
```
perpendicolare (considerando il peso dell’altra metà di muro come una forza
```
```
verticale aggiuntiva al nodo d’angolo dell’altra parete).
```
Questo secondo punto è stato reso necessario in quanto dal modello si è notato che i
```
maschi tendevano a ribaltare (cosa non verosimile anche per la presenza, appunto, delle
```
```
pareti perpendicolari).
```
Si sono ottenute di conseguenza le seguenti forze verticali, inserite nel modello:
CARICHI per nodo solaio 1 + calpestio + muratura
```
PP muro (maschi+fasce) 259.92 kN
```
```
PP solaio+calpestio (senza phi) 675 kN
```
Ptot struttura 1454.76 kN
Pmuro asse z per pareti laterali 85.5 kN
Pmuro asse z per parete centrale 171 kN
P nodi angolo pareti laterali P_vert_ang_murlat -112440 N
P nodi centrali pareti laterali P_vert_centr_murlat -53880 N
P nodi angolo parete centrale P_vert_ang_murcentr -224880 N
P nodi centrali parete centrale P_vert_centr_murcentr -107760 N
OSS. Dato che si hanno carichi diversi tra muri laterali e muro centrale, si sono calcolate
```
due tipologie diverse di molle diagonali e trasversali (in quanto esse variano in funzione
```
```
del carico verticale). Le molle assiali che sono funzione solo delle caratteristiche
```
meccaniche della muratura, restano invariate.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
161
Poiché i carichi verticali sono diversi, varia anche la resistenza a taglio ultimo del singolo
muro. Per questo motivo si sarebbero dovuti calcolare due differenti tipologie di tiranti
per muri laterali e muro centrale. Per una migliore chiarezza espositiva e per diminuire
```
l’onere computazionale del modello (giacché si sarebbero dovute calcolare due diverse
```
```
tipologie di molla per ogni elemento della fascia di piano) si è preferito l’utilizzo della
```
stessa quantità di armatura per tutti e tre i muri.
I tiranti sono stati, quindi, calcolati per il taglio ultimo del muro centrale, valore di taglio
più elevato.
T ult pann 83.94 kN
```
Fy=Tu*H/(2*H') 125.91 kN
```
Fy,min per fila 125.91 kN
Amin per fila 457.855 mm2
num tiranti per fila 1
fyd 275 Mpa
φ min 24.145 mm
φ progetto 26 mm
A sing fila 530.929 mm2
Atot 1061.858 mm2
Fy tiranti tot 292.011 kN
Fy tiranti per fila 146.006 kN
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
162
Questi valori sono stati inseriti nel modello come segue:
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
163
8.2.2 Analisi Time-History
Per l’analisi seguente, si sono considerati i tre accelerogrammi analizzati nel capitolo
7.2.1.
Nel modello, sarà inserito il seguente linguaggio per l’analisi Time-History:
In figura precedente, cerchiato in rosso, c’è il nome dell’accelerogramma inserito nel
```
modello: si cambierà volta per volta per l’analisi di tutti e tre i casi.
```
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
164
8.2.2.1 Time History – TH1
Per questo accelerogramma TH1, il caso studio entra in crisi per un’accelerazione di
picco PGA superiore all’1.0 g.
Si riportano di seguito i cicli isteretici delle pareti analizzate nel modello:
Dai grafici soprariportati si può notare come le sollecitazioni sismiche gravino
maggiormente sul muro centrale: esso, infatti, è il più sollecitato ed è quello che entrerà
in crisi. Si può notare che, mentre le pareti laterali hanno poca dissipazione energetica
```
dato che rimangono pressoché in campo elastico (in seguito si osserverà il
```
```
comportamento delle molle), il muro centrale entra abbondantemente in campo
```
plastico.
-500
-400
-300
-200
-100
0
100
200
300
400
500
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti laterali
parete
laterale
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico parete centrale
parete
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
165
Dal successivo grafico si può notare quanto appena affermato: l’area racchiusa dalla
linea blu è molto più ampia di quella racchiusa dalla linea rossa.
Di seguito, si passa ad analizzare il comportamento delle molle più sollecitate, al fine di
analizzare la tipologia di rottura raggiunta. Non si riportano i grafici di ogni elemento per
una migliore chiarezza espositiva dell’elaborato.
- Molle diagonali della parete centrale/maschio centrale:
Come si denota dal grafico, queste molle saranno quelle che si romperanno. Da ciò si
deduce che l’edificio entra in crisi per taglio-fessurazione diagonale della parete
centrale.
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti
parete
centrale
paretelaterale
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio centrale
elemento
101000
elemento
102000
Serie1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
166
- Molle diagonali della parete centrale/maschio laterale:
Si nota come anche queste molle entrano in crisi: ciò è significativo del fatto che le fasce
di piano e i trefoli inseriti collegano efficacemente tutti i maschi della parete, facendoli
lavorare tutti allo stesso modo.
- Molle diagonali spandrel della parete centrale:
Si nota che le fasce di piano del muro centrale non fessurano poiché le molle diagonali
spandrel rimangono sempre nel ramo elastico. Ciò significa che i tiranti sono stati
dimensionati ottimamente, giacché queste molle vengono sfruttate quasi fino al limite
elastico, senza però superarlo.
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio laterale
elemento
89000
elemento
90000
Serie1
-80
-60
-40
-20
0
20
40
60
80
-9 -4 1 6
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali spandrel 2000
elemento
151000
elemento
152000
legame
costitutivo
molle
diagonali
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
167
- Molle diagonali delle pareti laterali/maschio laterale:
Si nota, come già affermato, che i muri laterali iniziano a fessurarsi diagonalmente
```
(superano il limite elastico) ma non raggiungono la rottura: prima, infatti, si romperà il
```
muro centrale.
Infine, si è analizzata la storia degli spostamenti di solaio, muri laterali e muro centrale:
- Spostamenti solaio:
```
Lo spostamento massimo del nodo centrale del solaio (tra parete laterale e muro
```
```
centrale) è pari a 12.66 mm.
```
-60
-40
-20
0
20
40
60
-10.00 -8.00 -6.00 -4.00 -2.00 0.00 2.00 4.00 6.00 8.00 10.00
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali pareti laterali/maschio laterale
elemento
89
elemento
90
legame
costitutivo
molle
diagonali
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
168
- Spostamenti muri laterali:
Si osserva, come prevedibile per simmetria, che i due muri laterali si comportano allo
stesso modo. Essi si spostano al massimo di 6.59 mm. Si può notare come rimanga una
deformazione residua pari a 0.27 mm per la fessurazione della parete.
- Spostamenti muro centrale:
Lo spostamento massimo del muro centrale è pari a 14.54 mm. Si può notare ancora una
deformazione residua di 0.52 mm dovuta alla fessurazione della parete.
-8
-6
-4
-2
0
2
4
6
8
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
laterale 1
muro
laterale 2
-20
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
169
- Confronto tra i vari spostamenti (in un periodo tra 10 e 15 sec):
Si può notare come gli spostamenti del solaio e del muro centrale siano molto simili,
mentre quelli delle pareti laterali siano più bassi degli altri.
Questo grafico, inoltre, comprova che la tipologia di solaio analizzata è flessibile in
quanto gli spostamenti delle pareti laterali e quelli del muro centrale sono molto diversi
```
(anche se comunque mantengono gli stessi versi). Ad esempio, da un solo rapido
```
```
confronto tra gli spostamenti di picco (6.59 mm dei muri laterali contro i 14.54 mm della
```
```
parete centrale) si denota una differenza di più del doppio degli spostamenti.
```
OSS. Ci aspetteremo che questa differenza di spostamenti sia molto meno pronunciata
```
nel caso di solaio rigido (caso studio 2b).
```
-15
-10
-5
0
5
10
15
10 11 12 13 14 15
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio1
muro
laterale 1
muro
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
170
8.2.2.2 Time History – TH2
Per questo accelerogramma TH2, il caso studio entra in crisi per un’accelerazione di
picco PGA superiore allo 0.95 g.
Si riportano di seguito i cicli isteretici delle pareti analizzate nel modello:
Dai grafici soprariportati si può notare come le sollecitazioni sismiche gravino
maggiormente sul muro centrale: esso, infatti, è il più sollecitato ed è quello che entrerà
in crisi. Si può notare che, mentre le pareti laterali hanno poca dissipazione energetica
```
dato che rimangono pressoché in campo elastico (in seguito si osserverà il
```
-500
-400
-300
-200
-100
0
100
200
300
400
500
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti laterali
parete
lateral
e
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico parete centrale
parete
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
171
```
comportamento delle molle), il muro centrale entra abbondantemente in campo
```
plastico.
Dal successivo grafico si può notare quanto appena affermato: l’area racchiusa dalla
linea rossa è molto più ampia di quella racchiusa dalla linea blu.
Di seguito, si passa ad analizzare il comportamento delle molle più sollecitate, al fine di
analizzare la tipologia di rottura raggiunta. Non si riportano i grafici di ogni elemento per
una migliore chiarezza espositiva dell’elaborato.
- Molle diagonali della parete centrale/maschio laterale:
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti
parete
centrale
parete
laterale
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio laterale
elemento
89
elemento
90
Serie1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
172
Come si denota dal grafico, queste molle saranno quelle che si romperanno. Da ciò si
deduce che l’edificio entra in crisi per taglio-fessurazione diagonale della parete
centrale.
OSS. Si è visto dallo studio delle altre molle diagonali della parete centrale che tutte
```
entrano in crisi (tranne naturalmente le molle diagonali superiori che rimangono nel
```
```
ramo elastico): ciò è significativo del fatto che le fasce di piano e i tiranti inseriti
```
collegano efficacemente tutti i maschi della parete, facendoli lavorare tutti allo stesso
modo.
- Molle diagonali spandrel della parete centrale:
Si nota che le fasce di piano del muro centrale non fessurano poiché le molle diagonali
spandrel rimangono sempre nel ramo elastico. Ciò significa che i tiranti sono stati
dimensionati ottimamente, giacché queste molle vengono sfruttate quasi fino al limite
elastico, senza però superarlo.
-80
-60
-40
-20
0
20
40
60
80
-9 -4 1 6
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali spandrel 2000
elemento
151
elemento
152
legame
costitutiv
o molle
diagonali
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
173
- Molle diagonali delle pareti laterali/maschio laterale:
Si nota, come già affermato, che i muri laterali iniziano a fessurarsi diagonalmente
```
(superano il limite elastico) ma non raggiungono la rottura: prima, infatti, si romperà il
```
muro centrale.
Infine, si è analizzata la storia degli spostamenti di solaio, muri laterali e muro centrale:
- Spostamenti solaio:
```
Lo spostamento massimo del nodo centrale del solaio (tra parete laterale e muro
```
```
centrale) è pari a 14.06 mm.
```
-60
-40
-20
0
20
40
60
-10.00 -8.00 -6.00 -4.00 -2.00 0.00 2.00 4.00 6.00 8.00 10.00
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali pareti laterali/maschio laterale
elemento
89
elemento
90
legame
costitutiv
o molle
diagonali
-20
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
174
- Spostamenti muri laterali:
Si osserva, come prevedibile per simmetria, che i due muri laterali si comportano allo
stesso modo. Essi si spostano al massimo di 9.87 mm. Si può notare come rimanga una
deformazione residua pari a 0.85 mm per la fessurazione della parete.
- Spostamenti muro centrale:
Lo spostamento massimo del muro centrale è pari a 15.69 mm. Si può notare ancora una
deformazione residua di 0.68 mm dovuta alla fessurazione della parete.
-15
-10
-5
0
5
10
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
laterale
1
muro
laterale
2
-20
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
175
- Confronto tra i vari spostamenti (in un periodo tra 10 e 15 sec):
Analogamente alla TH1, si può notare come gli spostamenti del solaio e del muro
centrale siano molto simili, mentre quelli delle pareti laterali siano più bassi degli altri.
Questo grafico, inoltre, comprova che la tipologia di solaio analizzata è flessibile in
quanto gli spostamenti delle pareti laterali e quelli del muro centrale sono molto diversi
```
(anche se comunque mantengono gli stessi versi). Ad esempio, da un solo rapido
```
```
confronto tra gli spostamenti di picco (9.87 mm dei muri laterali contro i 15.69 mm della
```
```
parete centrale) si denota una differenza degli spostamenti (inferiore rispetto a quella
```
```
riscontrata nella TH1).
```
OSS. Ci aspetteremo che questa differenza di spostamenti sia molto meno pronunciata
```
nel caso di solaio rigido (caso studio 2b).
```
-15
-10
-5
0
5
10
15
10 11 12 13 14 15
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio1
muro
laterale 1
muro
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
176
8.2.2.3 Time History – TH3
Per questo accelerogramma TH3, il caso studio entra in crisi per un’accelerazione di
picco PGA superiore allo 0.95 g.
Si riportano di seguito i cicli isteretici delle pareti analizzate nel modello:
Dai grafici soprariportati si può notare come tutti e tre i muri siano sollecitati dal sisma.
Si osserva che, in questo caso anche le pareti laterali aiutino la dissipazione energetica
dato che anch’esse seguono una traiettoria più ampia rispetto ai casi precedenti. Il muro
centrale è anche in questo caso in campo plastico.
-500
-400
-300
-200
-100
0
100
200
300
400
500
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti laterali
parete
laterale
-600
-400
-200
0
200
400
600
-30 -20 -10 0 10 20
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico parete centrale
parete
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
177
Dal successivo grafico si può notare quanto appena affermato: l’area racchiusa dalla
linea rossa è ancora più ampia di quella racchiusa dalla linea blu, però in questo caso si
nota che la dissipazione energetica dei muri laterali non può essere trascurata.
Di seguito, si passa ad analizzare il comportamento delle molle più sollecitate, al fine di
analizzare la tipologia di rottura raggiunta. Non si riportano i grafici di ogni elemento per
una migliore chiarezza espositiva dell’elaborato.
- Molle diagonali della parete centrale/maschio laterale:
-600
-400
-200
0
200
400
600
-20 -10 0 10 20
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti
parete
centrale
parete
laterale
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio laterale
elemento
89000
elemento
90000
Serie1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
178
Come si denota dal grafico, queste molle saranno quelle che si romperanno. Da ciò si
deduce che l’edificio entra in crisi per taglio-fessurazione diagonale della parete
centrale. Si capisce che si è raggiunto il punto limite oltre il quale la muratura perde
notevolmente di resistenza e avviene la rottura.
OSS. Si è visto dallo studio delle altre molle diagonali della parete centrale che tutte
```
entrano in crisi (tranne naturalmente le molle diagonali superiori che rimangono nel
```
```
ramo elastico): ciò è significativo del fatto che le fasce di piano e i tiranti inseriti
```
collegano efficacemente tutti i maschi della parete, facendoli lavorare tutti allo stesso
modo.
- Molle diagonali spandrel della parete centrale:
Si nota che le fasce di piano del muro centrale non fessurano poiché le molle diagonali
spandrel rimangono sempre nel ramo elastico. Ciò significa che i tiranti sono stati
dimensionati ottimamente, giacché queste molle vengono sfruttate quasi fino al limite
elastico, senza però superarlo.
-80
-60
-40
-20
0
20
40
60
80
-9 -4 1 6
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali spandrel 2000
elemento
151000
elemento
152000
legame
costitutivo
molle
diagonali
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
179
- Molle diagonali delle pareti laterali/maschio laterale:
Si nota, come già affermato, che i muri laterali si fessurano diagonalmente, superando il
limite elastico in un modo più pronunciato rispetto alle Time-History precedenti.
Infine, si è analizzata la storia degli spostamenti di solaio, muri laterali e muro centrale:
- Spostamenti solaio:
```
Lo spostamento massimo del nodo centrale del solaio (tra parete laterale e muro
```
```
centrale) è pari a 18.24 mm.
```
-60
-40
-20
0
20
40
60
-10.00 -8.00 -6.00 -4.00 -2.00 0.00 2.00 4.00 6.00 8.00 10.00
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali pareti laterali/maschio laterale
elemento
89
elemento
90
legame
costitutivo
molle
diagonali
-20
-10
0
10
20
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
180
- Spostamenti muri laterali:
Si osserva, come prevedibile per simmetria, che i due muri laterali si comportano allo
stesso modo. Essi si spostano al massimo di 13.98 mm. Si può notare come rimanga una
deformazione residua pari a 1.65 mm per la fessurazione della parete.
- Spostamenti muro centrale:
Lo spostamento massimo del muro centrale è pari a 18.99 mm. Si può notare ancora una
deformazione residua di 1.76 mm dovuta alla fessurazione della parete.
-20
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
laterale
1
muro
laterale
2
-25
-20
-15
-10
-5
0
5
10
15
20
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
181
- Confronto tra i vari spostamenti (in un periodo tra 10 e 15 sec):
Analogamente alla TH1 e alla TH2, si può notare come gli spostamenti del solaio e del
muro centrale siano molto simili, mentre quelli delle pareti laterali siano più bassi degli
altri, anche se in un modo meno pronunciato dei casi precedenti. Ciò si deve dal fatto
che nell’intervallo analizzato, i muri laterali si sono già fessurati e quindi hanno diminuito
la loro rigidezza, causando così maggiori spostamenti.
OSS. Ci aspetteremo che questa differenza di spostamenti sia meno pronunciata nel caso
```
di solaio rigido (caso studio 2b).
```
-20
-10
0
10
10 11 12 13 14 15
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio1
muro
laterale 1
muro
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
182
8.2.3 Considerazioni del caso studio 2a
Nel presente paragrafo, si valuta l’andamento degli spostamenti di muri laterali, muro
centrale e solaio al variare della PGA, fino al valore di accelerazione di picco ultima
```
ricavata precedentemente. I valori di spostamento e di accelerazione di picco (calcolati
```
```
per ogni accelerogramma utilizzato) sono stati poi mediati al fine di ottenere
```
l’andamento medio dell’elemento analizzato. In seguito, gli andamenti medi di questo
caso studio saranno confrontati con i corrispondenti valori del caso studio con solaio
rigido.
Figura 8-7: Andamento dei muri laterali per i 3 accelerogrammi e andamento medio
Analizzando ciò che mostra la figura 8-7, si nota nuovamente come i maschi laterali
vengano poco sollecitati dal sisma. Infatti, essi hanno spostamenti molto al di sotto dei
limiti studiati.
0
2
4
6
8
10
12
14
16
18
0.5 0.6 0.7 0.8 0.9 1 1.1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento muro laterale
TH1 solaio flessibile
TH2 solaio flessibile
TH3 solaio flessibile
MEDIA solaio
flessibile
limite spostamento
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
183
Figura 8-8: Andamento del muro centrale per i 3 accelerogrammi e andamento medio
In figura 8-8 viene confermato quanto detto in precedenza, cioè si nota la capacità del
solaio flessibile di resistere a PGA elevate senza collassare, dissipando energia prima di
trasferirla ai muri laterali.
Si nota, infatti, che la parete centrale ha spostamenti molto più elevati dei muri laterali,
spostamenti che superano quelli limite per la rottura.
Figura 8-9: Andamento del solaio per i 3 accelerogrammi e andamento medio
```
Dalla figura 8-9 si nota come gli spostamenti del solaio (nel nodo centrale) siano poco
```
più bassi rispetto agli spostamenti del muro centrale.
0
2
4
6
8
10
12
14
16
18
20
0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento muro centrale
TH1 solaio flessibile
TH2 solaio flessibile
TH3 solaio flessibile
MEDIA solaio
flessibile
0
2
4
6
8
10
12
14
16
18
20
0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento solaio
TH1 solaio flessibile
TH2 solaio flessibile
TH3 solaio flessibile
MEDIA solaio
flessibile
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
184
8.2.4 Riepilogo dei risultati del caso studio 2a
Si è osservato nel presente caso studio 2a di un edificio esistente con solaio flessibile
```
che:
```
- La tipologia di rottura raggiunta dalla struttura è di tipo taglio-fessurazione
```
diagonale della parete centrale per ogni TH analizzata;
```
- Si sono notate significative differenze di spostamento tra muro centrale e muri
```
laterali, sintomo della poca rigidezza del solaio;
```
- In due delle tre analisi TH si è notato che i muri laterali erano poco sollecitati dal
sisma, ovvero si deformavano poco e avevano un comportamento pressoché
```
elastico;
```
- Le molle diagonali superiori dei singoli maschi sono rimaste sempre nel ramo
```
elastico, come previsto;
```
- Le fasce di piano e i tiranti inseriti sono stati dimensionati in modo corretto
```
affinché le pareti resistessero fino al taglio ultimo dei singoli maschi murari (le
```
```
fasce di piano sono rimaste sempre nel ramo elastico senza fessurarsi).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
185
8.3 Caso studio 2b: edificio di pianta 13.5x10m con solaio rigido
8.3.1 Analisi dei carichi e masse sismiche
Come nel caso studio 2a, si è ricavato:
Dati generali
γ muratura 24 kN/m3
g 9.806 m/sec2
massa muratura 2.447481 t/m3
Pesi solaio
q calpestio 2 kN/m2
Ψ2j calpestio 0.3
peso solaio5 4.25 kN/m2
massa solaio5+calpestio 0.494595 t/m2
massa solaio 5 + calpestio + muratura
massa solaio nodi angolo m_lat_murlat 1.51 t
massa solaio nodi laterali muro m_centr_murlat 2.671 t
massa solaio nodi laterali solaio m_lat_SOL 0.927 t
massa solaio nodi centrali solaio m_centr_SOL 1.855 t
massa solaio nodi centrali su muro centrale m_centr_murcentr 3.599 t
massa solaio nodi laterali solaio su muro centrale m_lat_murcentr 1.974 t
Le masse sismiche sono state inserite nel calcolatore come segue:
Figura 8-10: nomenclatura dei nodi
Massa nodi laterali
muro centrale
Massa nodi centrali
muro centrale
Massa nodi
laterali muro
Massa
nodi
d’angolo
Massa nodi
centrali solaio
Massa nodi laterali
solaio
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
186
Si sono ottenute di conseguenza le seguenti forze verticali, inserite nel modello:
CARICHI per nodo solaio 5+ calpestio + muratura
```
PP muro (maschi+fasce) 259.92 kN
```
PP solaio+calpestio 843.75 kN
Ptot struttura 1623.51 kN
Pmuro asse z per pareti laterali 85.5 kN
Pmuro asse z per parete centrale 171 kN
P nodi angolo pareti laterali P_vert_ang_murlat -115565 N
P nodi centrali pareti laterali P_vert_centr_murlat -60130 N
P nodi angolo parete centrale P_vert_ang_murcentr -231130 N
P nodi centrali parete centrale P_vert_centr_murcentr -120260 N
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
187
8.3.2 Time History
8.3.2.1 Time History – TH1
Per questo accelerogramma TH1, il caso studio entra in crisi per un’accelerazione di
picco PGA superiore allo 0.8 g.
Si riportano di seguito i cicli isteretici delle pareti analizzate nel modello:
Dai grafici soprariportati si può notare come le sollecitazioni sismiche gravino in egual
modo sia sulle pareti laterali che sul muro centrale. Si può notare in questo caso studio
con solaio rigido che tutti i muri vengono “sfruttati” appieno, fessurandosi. Si ha, quindi,
-500
-400
-300
-200
-100
0
100
200
300
400
500
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti laterali
parete
laterale
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico parete centrale
parete
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
188
```
una maggiore dissipazione energetica da parte delle pareti (ma una minore dissipazione
```
```
da parte del solaio rigido) dato che tutti i muri entrano abbondantemente in campo
```
```
plastico (in seguito si osserverà il comportamento delle molle).
```
Dal successivo grafico si può notare quanto appena affermato: le pareti entrano in
```
campo plastico (le pareti laterali, come si nota, hanno una minore resistenza a taglio-
```
```
fessurazione diagonale dato che sopportano carichi verticali inferiori).
```
Di seguito, si passa ad analizzare il comportamento delle molle più sollecitate, al fine di
analizzare la tipologia di rottura raggiunta. Non si riportano i grafici di ogni elemento per
una migliore chiarezza espositiva dell’elaborato.
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti
parete
centrale
paretelaterale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
189
- Molle diagonali della parete centrale/maschio centrale:
Come si denota dal grafico, queste molle saranno quelle che si romperanno. Da ciò si
deduce che la parete centrale entra in crisi per taglio-fessurazione diagonale.
- Molle diagonali della parete centrale/maschio laterale:
```
Si nota come anche queste molle entrano in crisi (in maniera quasi analoga al maschio
```
```
centrale analizzato prima): ciò è significativo del fatto che le fasce di piano e i tiranti
```
inseriti collegano efficacemente tutti i maschi della parete, facendoli lavorare tutti allo
stesso modo.
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio centrale
elemento
101000
elemento
102000
Serie1
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio laterale
elemento
89000
elemento
90000
Serie1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
190
- Molle diagonali spandrel della parete centrale:
Si nota che le fasce di piano del muro centrale non fessurano poiché le molle diagonali
spandrel rimangono sempre nel ramo elastico. Ciò significa che i tiranti sono stati
dimensionati ottimamente, giacché queste molle vengono sfruttate quasi fino al limite
elastico, senza però superarlo.
- Molle diagonali delle pareti laterali/maschio laterale:
Si nota, come già affermato, che anche le pareti laterali entrano in crisi e si fessurano
diagonalmente in maniera del tutto analoga al muro centrale. Si capisce che nel caso
analizzato il solaio distribuisce le sollecitazioni da sisma su tutte le pareti, “sfruttandole”
tutte allo stesso modo.
-80
-60
-40
-20
0
20
40
60
80
-9 -4 1 6
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali spandrel 2000
elemento
151000
elemento
152000
legame
costitutivo
molle
diagonali
-60
-40
-20
0
20
40
60
-10.00 -8.00 -6.00 -4.00 -2.00 0.00 2.00 4.00 6.00 8.00 10.00
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali pareti laterali/maschio laterale
elemento
89
elemento
90
legame
costitutivo
molle
diagonali
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
191
Infine, si è analizzata la storia degli spostamenti di solaio, muri laterali e muro centrale:
- Spostamenti solaio:
```
Lo spostamento massimo del nodo centrale del solaio (tra parete laterale e muro
```
```
centrale) è pari a 13.88 mm.
```
- Spostamenti muri laterali:
Si osserva, come prevedibile per simmetria, che i due muri laterali si comportano allo
```
stesso modo. Essi si spostano al massimo di 13.71 mm (rispetto ai 6.59 mm del caso
```
```
studio precedente). Si può notare come rimanga una deformazione residua pari a 0.93
```
mm per la fessurazione della parete.
-20
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio
cls
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
laterale 1
muro
laterale 2
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
192
- Spostamenti muro centrale:
Lo spostamento massimo del muro centrale è pari a 13.81 mm, molto simile allo
spostamento massimo ottenuto per il solaio e per le pareti laterali. Si può notare ancora
una deformazione residua di 0.82 mm dovuta alla fessurazione della parete.
-20
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
193
- Confronto tra i vari spostamenti (in un periodo tra 10 e 15 sec):
```
Si può notare come gli spostamenti del solaio e delle pareti siano quasi sovrapposti (non
```
sono completamente sovrapposti perché in realtà il solaio non è infinitamente rigido ma
```
bensì può deformarsi).
```
Questo grafico, inoltre, comprova che la tipologia di solaio analizzata è rigida in quanto
gli spostamenti delle pareti laterali e quelli del muro centrale sono quasi identici. Ad
```
esempio, da un solo rapido confronto tra gli spostamenti di picco (13.71 mm dei muri
```
```
laterali contro i 13.81 mm della parete centrale) si denota una differenza risibile di un
```
decimo di millimetro.
OSS. Si nota già una differenza rispetto al caso studio 2a in quanto in questo caso la
```
rottura avviene su tutte le pareti (nel caso precedente avveniva, invece, solo nella
```
```
parete centrale). Inoltre, in questo caso si nota come la struttura si muova tutta assieme
```
con un piano rigido, con differenze massime di spostamento molto basse.
-15
-10
-5
0
5
10
15
10 11 12 13 14 15
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio cls
muro
laterale 1
muro
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
194
8.3.2.2 Time History – TH2
Per questo accelerogramma TH2, il caso studio entra in crisi per un’accelerazione di
picco PGA superiore allo 0.85 g.
Si riportano di seguito i cicli isteretici delle pareti analizzate nel modello:
Dai grafici soprariportati si può notare come le sollecitazioni sismiche gravino in egual
modo sia sulle pareti laterali che sul muro centrale. Si può notare che in questo caso
studio con solaio rigido, tutti i muri vengono “sfruttati” appieno, fessurandosi. In questo
caso si ha una maggiore dissipazione energetica dato che tutti i muri entrano
-500
-400
-300
-200
-100
0
100
200
300
400
500
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti laterali
parete
laterale
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15 20
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico parete centrale
parete
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
195
```
abbondantemente in campo plastico (in seguito si osserverà il comportamento delle
```
```
molle).
```
Dal successivo grafico si può notare quanto appena affermato: le pareti entrano tutte in
```
campo plastico (le pareti laterali, come si nota, hanno una minore resistenza a taglio-
```
```
fessurazione diagonale dato che sopportano carichi verticali inferiori).
```
Di seguito, si passa ad analizzare il comportamento delle molle più sollecitate, al fine di
analizzare la tipologia di rottura raggiunta. Non si riportano i grafici di ogni elemento per
una migliore chiarezza espositiva dell’elaborato.
-600
-400
-200
0
200
400
600
-20 -15 -10 -5 0 5 10 15 20
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti
parete
centrale
paretelaterale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
196
- Molle diagonali della parete centrale/maschio centrale:
Come si denota dal grafico, queste molle saranno quelle che si romperanno. Da ciò si
deduce che la parete centrale entra in crisi per taglio-fessurazione diagonale.
- Molle diagonali della parete centrale/maschio laterale:
Si nota come anche queste molle entrano in crisi con spostamenti di poco maggiori
rispetto al maschio centrale analizzato prima: ciò è significativo del fatto che le fasce di
piano e i tiranti inseriti collegano efficacemente tutti i maschi della parete, facendoli
lavorare tutti allo stesso modo.
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio centrale
elemento
101000
elemento
102000
Serie1
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio laterale
elemento
89000
elemento
90000
Serie1
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
197
- Molle diagonali spandrel della parete centrale:
Si nota che le fasce di piano del muro centrale non fessurano poiché le molle diagonali
spandrel rimangono sempre nel ramo elastico. Ciò significa che i tiranti sono stati
dimensionati ottimamente, giacché queste molle vengono sfruttate quasi fino al limite
elastico, senza però superarlo.
- Molle diagonali delle pareti laterali/maschio laterale:
Si nota, come già affermato, che anche le pareti laterali entrano in crisi e si fessurano
diagonalmente in maniera del tutto analoga al muro centrale. Si capisce che nel caso
analizzato il solaio rigido distribuisce le sollecitazioni da sisma su tutte le pareti,
“sfruttandole” tutte allo stesso modo.
-80
-60
-40
-20
0
20
40
60
80
-9 -4 1 6
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali spandrel 2000
elemento
151000
elemento
152000
legame
costitutivo
molle
diagonali
-60
-40
-20
0
20
40
60
-10.00 -8.00 -6.00 -4.00 -2.00 0.00 2.00 4.00 6.00 8.00 10.00
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali pareti laterali/maschio laterale
elemento
89
elemento
90
legame
costitutivo
molle
diagonali
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
198
Infine, si è analizzata la storia degli spostamenti di solaio, muri laterali e muro centrale:
- Spostamenti solaio:
```
Lo spostamento massimo del nodo centrale del solaio (tra parete laterale e muro
```
```
centrale) è pari a 15.57 mm.
```
- Spostamenti muri laterali:
Si osserva, come prevedibile per simmetria, che i due muri laterali si comportano allo
stesso modo. Essi si spostano al massimo di 14.71 mm. Si può notare come rimanga una
deformazione residua pari a 0.27 mm per la fessurazione della parete.
-20
-15
-10
-5
0
5
10
15
20
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio
cls
-15
-10
-5
0
5
10
15
20
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
laterale 1
muro
laterale 2
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
199
- Spostamenti muro centrale:
Lo spostamento massimo del muro centrale è pari a 15.21 mm, molto simile allo
spostamento massimo ottenuto per il solaio e per le pareti laterali. Si può notare ancora
una deformazione residua di 0.33 mm dovuta alla fessurazione della parete.
-20
-15
-10
-5
0
5
10
15
20
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
200
- Confronto tra i vari spostamenti (in un periodo tra 10 e 15 sec):
```
Si può notare come gli spostamenti del solaio e delle pareti siano quasi sovrapposti (non
```
sono completamente sovrapposti perché in realtà il solaio non è infinitamente rigido ma
```
bensì può deformarsi).
```
Questo grafico, inoltre, comprova che la tipologia di solaio analizzata è rigida in quanto
gli spostamenti delle pareti laterali e quelli del muro centrale sono quasi identici. Ad
```
esempio, da un solo rapido confronto tra gli spostamenti di picco (14.71 mm dei muri
```
```
laterali contro i 15.21 mm della parete centrale) si denota una differenza risibile di
```
qualche decimo di millimetro.
OSS. Si nota già una differenza rispetto al caso studio 2a con solaio flessibile, in quanto
```
in questo caso la rottura avviene su tutte le pareti (nel caso studio precedente avveniva,
```
```
invece, solo nella parete centrale). Inoltre, in questo caso si nota come la struttura si
```
muova tutta assieme con un piano rigido, con differenze massime di spostamento molto
basse.
-15
-10
-5
0
5
10
15
20
10 11 12 13 14 15
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio cls
muro
laterale 1
muro
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
201
8.3.2.3 Time History – TH3
Per questo accelerogramma TH3, il caso studio entra in crisi per un’accelerazione di
picco PGA superiore allo 0.75 g.
Si riportano di seguito i cicli isteretici delle pareti analizzate nel modello:
Dai grafici soprariportati si può notare nuovamente come le sollecitazioni sismiche
gravino in egual modo sia sulle pareti laterali che sul muro centrale. Si può notare che in
questo caso studio con solaio rigido, tutti i muri vengono “sfruttati” appieno,
fessurandosi. In questo caso si ha una maggiore dissipazione energetica dato che tutti i
-500
-400
-300
-200
-100
0
100
200
300
400
500
-20 -15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti laterali
parete
laterale
-600
-400
-200
0
200
400
600
-15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico parete centrale
parete
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
202
```
muri entrano abbondantemente in campo plastico (in seguito si osserverà il
```
```
comportamento delle molle).
```
Dal successivo grafico si può notare quanto appena affermato: le pareti entrano in
```
campo plastico (le pareti laterali, come si nota, hanno una minore resistenza a taglio-
```
```
fessurazione diagonale dato che sopportano carichi verticali inferiori).
```
Di seguito, si passa ad analizzare il comportamento delle molle più sollecitate, al fine di
analizzare la tipologia di rottura raggiunta. Non si riportano i grafici di ogni elemento per
una migliore chiarezza espositiva dell’elaborato.
-600
-400
-200
0
200
400
600
-15 -10 -5 0 5 10 15
```
Taglio alla base (KN)
```
```
Spostamento in sommità (mm)
```
Ciclo isteretico pareti
parete
centrale
paretelaterale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
203
- Molle diagonali della parete centrale/maschio centrale:
Come si denota dal grafico, queste molle saranno quelle che si romperanno. Da ciò si
deduce che la parete centrale entra in crisi per taglio-fessurazione diagonale.
- Molle diagonali della parete centrale/maschio laterale:
```
Si nota come anche queste molle entrano in crisi (in maniera quasi analoga al maschio
```
```
centrale analizzato prima): ciò è significativo del fatto che le fasce di piano e i tiranti
```
inseriti collegano efficacemente tutti i maschi della parete, facendoli lavorare tutti allo
stesso modo.
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio centrale
elemento
101000
elemento
102000
Serie1
-80
-60
-40
-20
0
20
40
60
80
-10 -5 0 5 10
```
Sforzo Normale (KN)
```
```
Spostamento assiale (mm)
```
Molle diagonali parete centrale/maschio laterale
elemento
89000
elemento
90000
Serie1
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
204
- Molle diagonali spandrel della parete centrale:
Si nota che le fasce di piano del muro centrale non fessurano poiché le molle diagonali
spandrel rimangono sempre nel ramo elastico. Ciò significa che i tiranti sono stati
dimensionati ottimamente, giacché queste molle vengono sfruttate quasi fino al limite
elastico, senza però superarlo.
- Molle diagonali delle pareti laterali/maschio laterale:
Si nota, come già affermato, che anche le pareti laterali entrano in crisi e si fessurano
diagonalmente in maniera del tutto analoga al muro centrale. Si capisce che nel caso
analizzato il solaio rigido distribuisce le sollecitazioni da sisma su tutte le pareti,
“sfruttandole” tutte allo stesso modo.
-80
-60
-40
-20
0
20
40
60
80
-9 -4 1 6
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali spandrel 2000
elemento
151000
elemento
152000
legame
costitutivo
molle
diagonali
-60
-40
-20
0
20
40
60
-10.00 -8.00 -6.00 -4.00 -2.00 0.00 2.00 4.00 6.00 8.00 10.00
```
Sforzo Assiale (KN)
```
```
Spostamento Assiale (mm)
```
Molle diagonali pareti laterali/maschio laterale
elemento
89
elemento
90
legame
costitutivo
molle
diagonali
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
205
Infine, si è analizzata la storia degli spostamenti di solaio, muri laterali e muro centrale:
- Spostamenti solaio:
```
Lo spostamento massimo del nodo centrale del solaio (tra parete laterale e muro
```
```
centrale) è pari a 13.72 mm.
```
- Spostamenti muri laterali:
Si osserva, come prevedibile per simmetria, che i due muri laterali si comportano allo
stesso modo. Essi si spostano al massimo di 12.95 mm. Si può notare come rimanga una
deformazione residua pari a 0.51 mm per la fessurazione della parete.
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio
cls
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
laterale 1
muro
laterale 2
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
206
- Spostamenti muro centrale:
Lo spostamento massimo del muro centrale è pari a 13.16 mm, molto simile allo
spostamento massimo ottenuto per il solaio e per le pareti laterali. Si può notare ancora
una deformazione residua di 0.64 mm dovuta alla fessurazione della parete.
-15
-10
-5
0
5
10
15
0 5 10 15 20 25
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
muro
centrale
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
207
- Confronto tra i vari spostamenti (in un periodo tra 10 e 15 sec):
```
Si può notare come gli spostamenti del solaio e delle pareti siano quasi sovrapposti (non
```
sono completamente sovrapposti perché in realtà il solaio non è infinitamente rigido ma
```
bensì può deformarsi).
```
Questo grafico, inoltre, comprova che la tipologia di solaio analizzata è rigida in quanto
gli spostamenti delle pareti laterali e quelli del muro centrale sono quasi identici. Ad
```
esempio, da un solo rapido confronto tra gli spostamenti di picco (12.95 mm dei muri
```
```
laterali contro i 13.16 mm della parete centrale) si denota una differenza risibile di
```
qualche decimo di millimetro.
OSS. Come già osservato in precedenza, anche in questo esempio si denota una
differenza rispetto al caso studio 2a con solaio flessibile in quanto in questo caso la
```
rottura avviene su tutte le pareti (nel caso studio precedente avveniva, invece, solo nella
```
```
parete centrale). Inoltre, in questo caso si nota come la struttura si muova tutta assieme
```
con un piano rigido, con differenze massime di spostamento molto basse.
-15
-10
-5
0
5
10
15
10 11 12 13 14 15
```
Spostamenti (mm)
```
```
Time (sec)
```
Time History
solaio cls
muro
laterale 1
muro
centrale
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
208
8.3.3 Considerazioni del caso studio 2b
Nel presente paragrafo, si valuta l’andamento degli spostamenti di muri laterali, muro
centrale e solaio al variare della PGA, fino al valore di accelerazione di picco ultima
```
ricavata precedentemente. I valori di spostamento e di accelerazione di picco (calcolati
```
```
per ogni accelerogramma utilizzato) sono stati poi mediati al fine di ottenere
```
l’andamento medio dell’elemento analizzato. In seguito, gli andamenti medi di questo
caso studio saranno confrontati con i corrispondenti valori del caso studio con solaio
flessibile.
Figura 8-11: Andamento dei muri laterali per i 3 accelerogrammi e andamento medio
Analizzando ciò che mostra la figura 8-11, si nota nuovamente come i maschi laterali
vengano sollecitati dal sisma, raggiungendo anch’essi spostamenti vicini a quelli limite
studiati.
0
2
4
6
8
10
12
14
16
18
0.4 0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento muro laterale
TH1 solaio rigido
TH2 solaio rigido
TH3 solaio rigido
MEDIA solaio rigido
limite spostamento
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
209
Figura 8-12: Andamento del muro centrale per i 3 accelerogrammi e andamento medio
In figura 8-12 è confermato quanto detto in precedenza, cioè si nota che gli spostamenti
del muro centrale siano molto simili a quelli delle pareti laterali: ciò dipende dalla
elevata rigidità del solaio in calcestruzzo, la quale non permette una elevata dissipazione
energetica del sisma.
Figura 8-13: Andamento del solaio per i 3 accelerogrammi e andamento medio
```
Dalla figura 8-13 si nota che gli spostamenti del solaio (nel nodo centrale) siano molto
```
simili agli spostamenti delle pareti.
0
2
4
6
8
10
12
14
16
18
0.4 0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento muro centrale
TH1 solaio rigido
TH2 solaio rigido
TH3 solaio rigido
MEDIA solaio rigido
limite spostamento
0
2
4
6
8
10
12
14
16
18
0.4 0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento solaio
TH1 solaio rigido
TH2 solaio rigido
TH3 solaio rigido
MEDIA solaio rigido
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
210
8.3.4 Riepilogo dei risultati del caso studio 2b
Si è osservato nel presente caso studio 2b di un edificio esistente con solaio rigido che:
- La tipologia di rottura raggiunta dalla struttura è di tipo taglio-fessurazione
```
diagonale sia delle pareti laterali che di quella centrale per ogni TH analizzata;
```
- Si sono notate basse differenze di spostamento tra muro centrale e muri laterali,
```
sintomo dell’elevata rigidezza del solaio;
```
- In tutte le analisi TH si è notato che i muri laterali e la parete centrale
```
fessuravano, ovvero si deformavano molto;
```
- Le molle diagonali superiori dei singoli maschi sono rimaste sempre nel ramo
```
elastico anche in questo caso studio, come previsto;
```
- Le fasce di piano e i tiranti inseriti sono stati dimensionati in modo corretto
```
affinché le pareti resistessero fino al taglio ultimo dei singoli maschi murari (le
```
```
fasce di piano sono rimaste sempre nel ramo elastico senza fessurarsi).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
211
8.4 Conclusioni del caso studio 2
Di seguito si riporta un confronto tra i due casi studio 2a e 2b appena esaminati
considerando quattro fattori: modalità di collasso, differenza di spostamenti tra pareti
laterali e parete centrale, PGA di rottura ricavate dalle diverse analisi, confronto tra
andamento dei grafici PGA-spostamento medi per muri laterali, parete centrale e solaio.
Per quanto riguarda le modalità di collasso, si è ottenuto:
- Nel caso 2a di struttura con solaio flessibile, si ha una rottura della parete
centrale per taglio fessurazione diagonale mentre le altre pareti iniziano a
```
fessurarsi ma non collassano;
```
- Nel caso 2b di struttura con solaio rigido, si ha una rottura contemporanea delle
pareti laterali e della parete centrale per taglio fessurazione diagonale.
Per quanto riguarda la differenza di spostamento tra pareti laterali e parete centrale, si è
```
ottenuto:
```
- Nel caso studio 2a di struttura con solaio flessibile, si hanno differenze di
spostamento elevate, ovvero le pareti laterali si spostano molto meno rispetto
```
alla parete centrale;
```
- Nel caso studio 2b di struttura con solaio rigido, si hanno differenze di
spostamento molto più basse, ovvero le pareti laterali hanno spostamenti simili a
quelli della parete centrale.
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
212
Per quanto riguarda la valutazione delle PGA ultime dei due diversi casi, si osserva che le
PGA di rottura ricavate nel caso di solaio flessibile sono più elevate rispetto a quelle con
solaio in calcestruzzo. Ciò è dovuto al fatto che l’aumento di peso del solaio dovuto alla
```
soletta di calcestruzzo aumenta la resistenza a taglio ultima della struttura (quindi, essa
```
resiste a un taglio maggiore rispetto al caso con solaio consolidato con il solo tavolato a
```
45°) ma aumenta anche la massa sismica inserita nel modello. Per questo motivo, la
```
struttura con solaio in calcestruzzo collassa per un’accelerazione di picco al suolo minore
dell’altro caso.
OSS. Le accelerazioni di picco così ricavate sono molto alte per ambo i casi studio. Ciò è
```
dovuto al fatto che la struttura è molto semplice (a un singolo piano).
```
0
0.2
0.4
0.6
0.8
1
1.2
TH1 TH2 TH3 MEDIA
```
PGA ULTIMA DA MODELLO (a/g))
```
Confronto PGA ultima dei due casi studio
SOLAIO
TAVOLATO 45°
SOLAIO CLS
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
213
Per il confronto dell’andamento degli spostamenti di muri laterali, muro centrale e
solaio al variare della PGA, in questo capitolo si utilizzano i valori medi ricavati in
precedenza.
Figura 8-14: Andamento medio dei muri laterali per i due casi studio
Analizzando ciò che mostra la figura 8-14, si nota con interesse che, nel caso di solaio
flessibile, i muri laterali sono sollecitati dal sisma in maniera minore rispetto al caso con
solaio rigido. Come già affermato, le pareti laterali del solaio con tavolato a 45°
```
difficilmente si romperanno per prime (cosa che non si può di certo dire per il caso con
```
```
solaio in calcestruzzo).
```
Il collasso nel caso di consolidamento con soletta in calcestruzzo avviene per valori di
PGA leggermente più bassi: i consolidamenti con tavolato a 45° collassano, quindi, per
accelerazioni più elevate.
0
2
4
6
8
10
12
14
16
18
0.4 0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento muro laterale
MEDIA solaio
rigido
MEDIA solaio
flessibile
limite
spostamento
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
214
Figura 8-15: Andamento medio del muro centrale per i due casi studio
In figura 8-15 viene confermato quanto detto in precedenza, cioè si nota la capacità del
solaio più flessibile di resistere a PGA più elevate senza collassare e dissipando energia
prima di trasferirla alle pareti.
Figura 8-16: Andamento medio del solaio per i due casi studio
In figura 8-16 si rappresenta l’andamento degli spostamenti del nodo centrale dei due
solai al variare della PGA per i due casi studio analizzati. Come si può osservare i due
solai hanno un andamento quasi uguale per PGA basse. Successivamente, però, si nota
come il solaio con tavolato a 45° collassa a valori più elevati di accelerazione di picco
```
(come precedentemente affermato).
```
0
2
4
6
8
10
12
14
16
18
0.4 0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento muro centrale
MEDIA solaio rigido
MEDIA solaio
flessibile
limite spostamento
0
2
4
6
8
10
12
14
16
0.4 0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (a/g)
```
Andamento solaio
MEDIA solaio rigido
MEDIA solaio
flessibile
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
215
Infine, di seguito si riporta l’andamento della differenza di spostamento tra il nodo
centrale del solaio con le pareti dei casi studio 2a e 2b.
Ci si è riferiti sempre ai valori mediati tra i tre accelerogrammi.
Figura 8-17: Differenza di spostamenti tra solaio e muri laterali
Si può notare, come già affermato, che nel caso di solaio flessibile si hanno diversi
spostamenti tra il nodo centrale solaio e muro laterale. Nel caso studio 2b, invece, si
nota come le differenze di spostamenti siano molto basse e costanti.
0
1
2
3
4
5
6
7
8
9
0.4 0.5 0.6 0.7 0.8 0.9 1
```
Spostamento (mm)
```
```
PGA (1/g)
```
Differenza spostamenti nodo centrale solaio - muro
laterale
MEDIA solaio
rigido
MEDIA solaio
flessibile
CASO STUDIO 2: EDIFICIO DI PIANTA 13.5x10m CON TRE MURI
216
In figura 8-18 si raffigura lo spostamento differenziale tra il nodo centrale del solaio e la
parete centrale.
Figura 8-18: Differenza di spostamenti tra solaio e muro centrale
Si nota subito che per entrambi i casi 2a e 2b la differenza rimane pressoché costante al
variare della PGA.
Tuttavia, la differenza degli spostamenti nel caso 2a è più elevata rispetto a quella del
caso 2b, sintomo della minore rigidezza del solaio.
OSS. Come affermato in precedenza nel capitolo 5, le due tipologie di rinforzo trattate
nel presente elaborato sono entrambe rigide. Infatti, come osservato da tesi precedenti
```
(A. Lonardi, 2015), anche il solaio in legno rinforzato con tavolato a 45° è molto rigido.
```
Si rimanda quindi alla tesi di M. Tonon per l’utilizzo di solai più flessibili.
0
0.5
1
1.5
2
2.5
0.4 0.6 0.8 1
```
Spostamento (mm)
```
```
PGA (1/g)
```
Differenza spostamenti nodo centrale solaio - muro
centrale
MEDIA solaio
rigido
MEDIA solaio
flessibile
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
217
9 CONCLUSIONI
9.1 Breve riepilogo della modellazione trattata
In primo luogo, si sono modellate le molle del singolo maschio murario in funzione delle
diverse modalità di collasso dello stesso. Gli elementi sono stati calibrati nel modo
```
seguente:
```
- Le molle assiali del singolo maschio murario sono state modellate in modo da
```
considerare la rottura per pressoflessione;
```
- Le molle trasversali del singolo maschio murario sono state modellate in modo
da considerare la rottura per taglio-scorrimento alla base per mezzo della teoria
```
di Coulomb;
```
- Le molle diagonali del singolo maschio murario sono state modellate in modo da
considerare la rottura per taglio-fessurazione diagonale per mezzo della teoria di
Turnsek-Cacovic. Per diminuire l’onere computazionale del modello, le molle
diagonali superiori del maschio murario sono state modellate con un elemento
```
elastico (si è controllato caso per caso che esse non superassero il limite
```
```
elastico).
```
Iterativamente e cercando di ottenere i risultati ottenuti da prove di laboratorio, si sono
ottenute così le caratteristiche di resistenza per edifici esistenti in muratura, utilizzate in
seguito nei modelli.
In seconda istanza, si sono modellate le molle della fascia di piano in modo del tutto
```
analogo alle molle del maschio murario (considerando le stesse possibili modalità di
```
```
rottura).
```
Si sono, inoltre, dimensionati i tiranti da inserire nell’edificio esistente in modo tale da
```
raggiungere dapprima il taglio ultimo dei singoli maschi murari (ovvero, i tiranti
```
```
permettono alla struttura di non ribaltarsi e alle fasce di rimanere in campo elastico).
```
Questi sono stati in seguito inseriti nel modello come forze puntuali uguali e opposte
pari alla forza limite di snervamento dei trefoli inseriti. Esse permettono così alle “molle
orizzontali spandrel” di non essere mai in trazione e aumentano le resistenze della fascia
CONCLUSIONI
218
di piano sia per quanto riguarda la rottura a taglio fessurazione diagonale delle “molle
diagonali spandrel” sia per quanto riguarda la rottura a taglio scorrimento delle “molle
verticali spandrel”.
Successivamente, si sono dimensionati i beam per il fuori-piano della muratura
utilizzando il momento ultimo dato dalle NTC’08. Essi sono stati inseriti nel piano
perpendicolare al sisma in corrispondenza dei nodi di bordo del solaio, per considerare
un ulteriore aggiunta di resistenza allo spostamento del solaio.
Nell’analisi dei carichi e delle masse sismiche, si sono considerate le combinazioni di
carico sismiche come da Normativa.
Per le masse sismiche si sono considerati i seguenti carichi:
- Il carico dovuto al peso proprio del solaio (in base alla diversa tipologia di solaio
```
trattata);
```
- Il 30% del carico da calpestio (come da Norme Tecniche per le Costruzioni);
- La metà del peso proprio della muratura.
Queste masse sono state inserite in ogni nodo del solaio in funzione dell’area di
```
influenza (l’aliquota di massa delle pareti murarie, naturalmente, è stata assegnata solo
```
```
ai nodi che collegano solaio e maschi murari). Esse sono state, quindi, inserite nel
```
modello solo in direzione del sisma, ovvero nella direzione parallela alle pareti
```
(direzione X).
```
Per i carichi verticali assegnati ai nodi superiori delle pareti murarie si sono considerati:
- Il carico dovuto al peso proprio del solaio (in base alla diversa tipologia di solaio
```
trattata);
```
- Il 30% del carico da calpestio (come da Norme Tecniche per le Costruzioni);
- La totalità del peso proprio della muratura;
- Per i nodi d’angolo delle pareti in muratura si è considerata un’aggiunta di carico
verticale dovuta al peso proprio di parte del muro nella direzione perpendicolare
alla parete considerata, tenendo in conto del realistico “incatenamento” delle
```
pareti nell’angolo (essa eviterà che avvenga il ribaltamento del muro).
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
219
In sede di modellazione, sono stati inseriti i seguenti vincoli:
- Vincoli di tipo incastro per tutti i nodi alla base (sia per le pareti murarie che per i
```
beam per il fuori piano);
```
- Vincoli di tipo carrello per tutti i nodi delle pareti murarie in direzione
```
perpendicolare al muro (altrimenti si avevano problemi nel passaggio dal 2D al
```
```
3D per la presenza dei truss i quali danno resistenza solo nel piano);
```
- Vincoli di tipo carrello per tutti i nodi dei solai in direzione perpendicolare al
```
solaio (altrimenti si avevano problemi nel passaggio dal 2D al 3D per la presenza
```
```
dei truss i quali danno resistenza solo nel piano);
```
- I nodi di collegamento tra solaio e parete non sono stati vincolati;
- Nei nodi di collegamento tra solaio e beam per il fuori piano sono stati inseriti
degli “equal dof” che permettono di collegare degli elementi beam con gli
elementi truss. Con questo comando, si assegnano gli stessi spostamenti del
solaio ai beam per il fuori piano.
In seguito, si sono eseguite delle analisi cicliche e analisi Pushover per la modellazione
delle pareti nel piano, assegnando gli spostamenti ai nodi superiori delle pareti. Per
un’ulteriore validazione del modello utilizzato, si sono confrontati i valori di
smorzamento del modello con dei cicli isteretici di una maschio murario con la stessa
geometria.
Infine, si è passati a delle analisi di tipo Time History per i casi studio degli edifici in tre
dimensioni.
CONCLUSIONI
220
9.2 Considerazioni finali
Dal presente elaborato di tesi, in base ai risultati ottenuti dai diversi casi studio si è
evinto che:
- Tra le due tipologie di rinforzo di solai lignei analizzate, il consolidamento
migliore per le tipologie di edificio studiate è quello per mezzo di un tavolato
ligneo inclinato di 45°. Esso, infatti, ha ottenuto risultati migliori sia per i valori di
accelerazione ultima di picco, sia per quanto riguarda gli spostamenti di solaio,
muri laterali e muro centrale, i quali, a parità di PGA, sono sempre inferiori a
```
quelli del caso di rinforzo con soletta in calcestruzzo;
```
- Un aumento di rigidezza dell’orizzontamento migliora l’effetto scatolare della
```
struttura (ovvero tutte le pareti si spostano allo stesso modo) ma può implicare,
```
come nel caso analizzato di soletta in calcestruzzo, un aumento di peso e, quindi,
di massa sismica. Tutto ciò può essere sia favorevole alla struttura in quanto
l’aumento del carico verticale aumenta la resistenza a taglio delle pareti, sia
sfavorevole in quanto un aumento di massa sismica comporta un aumento di
```
spostamenti nel caso di sisma;
```
- Dal caso studio 2 si è osservato che nel caso di consolidamento con tavolato a
45°, il solaio dissipa energia e che le pareti laterali si spostano meno rispetto alla
```
parete centrale;
```
- L’introduzione di tiranti aumenta la resistenza della parete nel proprio piano
giacché rende le fasce di piano più resistenti: esse permettono il comportamento
“a telaio” del muro, con una migliore distribuzione dei carichi orizzontali su tutti i
maschi. I tiranti, inoltre, evitano che zone critiche come le fasce di piano possano
```
fessurare (e quindi rompersi) prima dei maschi, evitando così un prematuro
```
collasso strutturale.
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
221
Infine, si possono trarre le seguenti valutazioni in riferimento alla modellazione a
```
macroelementi:
```
- Il comportamento della singola molla riproduce fedelmente il comportamento
della muratura esistente, in base a un confronto con prove sperimentali di
```
provini aventi le stesse dimensioni e carichi;
```
- La modellazione scelta può essere migliorata (si veda capitolo 9.3) in quanto non
```
tiene conto di possibili rotture nel fuori piano della muratura;
```
- Si sono ottenuti risultati che potrebbero riprodurre le reali modalità di collasso
sismico. Infatti, si è osservato che la rottura avviene sempre per taglio
fessurazione diagonale nella zona centrale del maschio murario, risultato spesso
riscontrato in strutture in muratura a seguito di un sisma.
Per questi motivi, la modellazione analizzata è ritenuta affidabile e con molti margini di
miglioramento.
CONCLUSIONI
222
9.3 Sviluppi futuri
In questo capitolo si presentano alcune proposte per il miglioramento del presente
```
elaborato di tesi (alcuni dei seguenti punti saranno trattati nella tesi di M. Tonon “Effetti
```
del rinforzo di solai in legno nel miglioramento sismico di edifici esistenti in muratura -
```
modellazione numerica dei solai”):
```
- Migliore discretizzazione del solaio in modo tale da inserire un maggior numero
```
di masse per rendere il tutto il più realistico possibile;
```
- In seguito a una migliore discretizzazione del solaio si può, inoltre, aumentare il
numero di beam per il fuori piano delle pareti non portanti e perpendicolari al
```
sisma;
```
- Analizzare casi studio con solai con diverse rigidezze rispetto ai casi studio trattati
```
nel presente elaborato (ad esempio utilizzando un solaio con tavolato semplice
```
```
flessibile);
```
- Modellazione di un edificio a due piani;
- Studio delle connessioni tra solaio e parete murarie;
- Ampliare il tema del fuori piano, inserendo dei beam nelle pareti portanti, ovvero
```
nelle pareti parallele al sisma;
```
- Modellazione delle molle delle pareti non portanti (e relative masse nelle altre
```
direzioni) di modo da poter studiare il problema anche con sisma nelle altre
```
```
direzioni;
```
- …
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
223
RIFERIMENTI BIBLIOGRAFICI
224
RIFERIMENTI BIBLIOGRAFICI
- G. Magenes e G.M. Calvi, “Cyclic Behaviour of Brick Masonry Walls”, 1992;
- Piazza, Baldessari e Tomasi, “The Role of in-plane floor stiffness in the seismic
```
behaviour of traditional buildings”, 2008;
```
- tesi di dottorato di C. Baldessarri, “In-plane behaviour of differently refurbished
```
timber floors”, 2010;
```
- M. Vinci, “I tiranti in acciaio nel calcolo delle costruzioni in muratura”, Dario
```
Flaccovio editore, 2014;
```
- F. Graziotti, G. Magenes, A. Penna, “Experimental cyclic behaviour of stone
```
masonry spandrels”, 2012;
```
- K. Beyer, “Peak and residual strengths of brick masonry spandrels”, 2012;
- G. Magenes, G.M. Calvi, “In-Plane seismic response of brick masonry walls”;
- S. Caddemi, I. Caliò, F. Cannizzaro, P. Colajanni, B. Pantò, G.Ricciardi, “Un
approccio innovativo per la modellazione degli edifici in muratura intelaiata.
```
Applicazione ad un caso di studio”;
```
- S. Mazzoni, F. Mckenna, M.H. Scott, G.L. Fenves, et al., “OpenSees Command
```
Language Manual”, 2007;
```
- “Manuale teorico” da programma “3DMacro-il software per le murature”;
- M. Tomazevic, M. Lutman, L. Petkovic, “Seismic behavior of masonry walls:
```
experimental simulation”;
```
- tesi di L. De Tomasi, “Modelli numerici per l’analisi sismica di edifici in muratura
```
con solai lignei”, 2014;
```
- tesi di dottorato di B. Pantò “La modellazione sismica degli edifici in muratura –
```
Un approccio innovativo su un macro-elemento spaziale”;
```
- “Norme Tecniche per le Costruzioni 2008”;
- “Circ. esplicativa NTC 2008 n° 617” del 02_02_2009;
- “Eurocodice 1: Basi di calcolo ed azioni sulle strutture”;
- “Eurocodice 6: Progettazione delle strutture di muratura”;
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
225
- L. Boscotrecase, F. Piccarreta,“Edifici in muratura in zona sismica”;
- M. Boscolo Bielo,“Progettazione antisismica con le NTC”;
- P. Cirone, “Restauro strutturale delle murature”.
INDICE DELLE FIGURE
226
INDICE DELLE FIGURE
Figura 2-1: Effetto del diverso grado di accoppiamento fornito dalle travi di muratura sulla
```
distribuzione dei momenti: fasce flessibili (a), intermedie (b) e rigide (c) (Tomaževič, 1999) ..... 13
```
Figura 2-2: Influenza delle connessioni tra gli elementi ................................................................ 15
Figura 2-3: Esempio di collasso per ribaltamento.......................................................................... 16
Figura 2-4: Esempio di collasso per flessione verticale ................................................................. 16
Figura 2-5: Diversa risposta sismica degli edifici in muratura ...................................................... 17
Figura 2-6: Esempi di rottura per fessurazione diagonale, flessione, scorrimento ........................ 18
```
Figura 2-7: Tipi di comportamento di un pannello; (a) snello; (b) tozzo. ...................................... 19
```
```
Figura 2-8: Meccanismi di collasso nel piano: pressoflessione (a), taglio-fessurazione diagonale
```
```
(b), taglio-scorrimento (c) .............................................................................................................. 20
```
Figura 2-9 : Pannello caricato da sforzo normale eccentrico e forza orizzontale .......................... 21
```
Figura 2-10: Meccanismi di ribaltamento nel piano: (a) globale da blocco rigido; (b) e (c) parziali.
```
....................................................................................................................................................... 22
Figura 2-11: rottura per taglio-fessurazione diagonale di edifici esistenti in muratura ................. 23
Figura 2-12: rottura per taglio-scorrimento di edifici esistenti in muratura ................................... 27
Figura 2-13: Comportamento nel piano della parete senza e con tiranti........................................ 30
Figura 2-14: Comportamento fuori piano della parete con e senza tiranti ..................................... 31
```
Figura 3-1: Il macro-elemento di base per la modellazione della muratura: (a) configurazione
```
```
indeformata; (b) configurazione deformata (“Manuale teorico”) .................................................. 34
```
```
Figura 3-2: Interazione tra un pannello e gli elementi limitrofi mediante letti di molle (“Manuale
```
```
teorico”) ......................................................................................................................................... 35
```
```
Figura 3-3: Pannello (“Manuale teorico”) ..................................................................................... 35
```
```
Figura 3-4: molle trasversali e molle a scorrimento (“Manuale teorico”) ..................................... 36
```
```
Figura 3-5: Muratura modellata mediante una mesh di macro-elementi (“Manuale teorico”) ...... 37
```
Figura 3-6: Modellazione di un prototipo di parete mediante due differenti mesh: discretizzazione
```
della parete (S. Caddemi, I. Caliò et al.).......................................................................................... 38
```
```
Figura 3-7: Simulazione dei meccanismi di collasso nel piano di un pannello murario: (a) rottura
```
```
per schiacciamento/ribaltamento; (b) rottura a taglio per fessurazione diagonale; (c) rottura a
```
```
taglio per scorrimento. (S. Caddemi, I. Caliò et al.) ........................................................................ 38
```
```
Figura 3-8: Legame costitutivo elasto-plastico (“Manuale teorico”) ............................................. 42
```
```
Figura 3-9: Legame utilizzato per il comportamento assiale/flessionale della muratura. (“Manuale
```
```
teorico”) ......................................................................................................................................... 42
```
```
Figura 3-10: Legame elastoplastico di tipo fratturante (a) materiale non fratturato; (b)materiale
```
```
fratturato. (“Manuale teorico”) ...................................................................................................... 43
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
227
Figura 3-11: Legame costitutivo e parametri caratteristici delle molle flessionali di interfaccia
```
(“Manuale teorico”) ........................................................................................................................ 44
```
Figura 3-12: Procedura di concentrazione delle caratteristiche della muratura alle molle delle
```
interfacce (“Manuale teorico”) ....................................................................................................... 44
```
Figura 3-13: Equivalenza tra il modello continuo e il modello discreto per la determinazione delle
```
rigidezze Kp (“Manuale teorico”) ................................................................................................... 45
```
Figura 3-14: Fessure per trazione in una muratura regolare caricata ortogonalmente ai ricorsi
```
(“Manuale teorico”) ........................................................................................................................ 47
```
```
Figura 3-15: Rottura a trazione per scorrimento lungo i giunti di malta (“Manuale teorico”) ....... 47
```
```
Figura 3-16: Schema di carico di un pannello murario (“Manuale teorico”) ................................. 49
```
```
Figura 3-17: Rappresentazione dello stato tensionale nel piano di Mohr (“Manuale teorico”) ..... 49
```
```
Figura 3-18: Pannello soggetto a una forza tagliante (“Manuale teorico”) .................................... 51
```
```
Figura 3-19: Definizione del parametro di compressione media per un pannello (“Manuale
```
```
teorico”) .......................................................................................................................................... 52
```
```
Figura 3-20: Legame attribuito alle molle diagonali; (a) legame carico spostamento; (b) ciclo
```
```
isteretico, a sforzo normale nullo (“Manuale teorico”) .................................................................. 53
```
```
Figura 3-21: Equivalenza a taglio tra il modello continuo e il modello discreto (“Manuale
```
```
teorico”) .......................................................................................................................................... 53
```
```
Figura 3-22: Deformazioni nel sistema continuo e discreto (“Manuale teorico”) .......................... 54
```
```
Figura 3-23: Dominio alla Coulomb incrudente nel piano N,ζ (“Manuale teorico”)..................... 57
```
```
Figura 3-24: Legame ζ -ε a N costante e α variabile (“Manuale teorico”) ..................................... 58
```
```
Figura 3-25: Scorrimento lungo i giunti di malta (“Manuale teorico”) .......................................... 59
```
Figura 3-26: Schema meccanico del comportamento a scorrimento dell’interfaccia, limitatamente
```
al caso piano (“Manuale teorico”) .................................................................................................. 60
```
```
Figura 3-27: Aree di influenza delle molle a scorrimento nel piano (“Manuale teorico”) ............. 60
```
```
Figura 3-28: Cinematica a scorrimento dell’interfaccia (“Manuale teorico”) ................................ 62
```
```
Figura 4-1: tabella con parametri di resistenza del provino (da Magenes et Calvi) ....................... 63
```
```
Figura 4-2: schema dei test distruttivi in laboratorio (da Magenes et Calvi) ................................. 64
```
Figura 4-3: legame taglio alla base-scorrimento in sommità del muro MI1 analizzato in
```
laboratorio (da Magenes et Calvi) .................................................................................................. 65
```
Figura 4-4: legame taglio alla base-scorrimento in sommità del muro MI2 analizzato in
```
laboratorio (da Magenes et Calvi) .................................................................................................. 65
```
Figura 4-5: legame taglio alla base-scorrimento in sommità del muro MI3 analizzato in
```
laboratorio (da Magenes et Calvi) .................................................................................................. 66
```
Figura 4-6: legame taglio alla base-scorrimento in sommità del muro MI4 analizzato in
```
laboratorio (da Magenes et Calvi) .................................................................................................. 66
```
INDICE DELLE FIGURE
228
```
Figura 4-7: Definizione del modello Hysteretic Material nel manuale OpenSees (da S. Mazzoni,
```
```
F.McKenna, et al.) ......................................................................................................................... 69
```
```
Figura 4-8: deformazioni angolari pertinenti all’estremo i di un elemento “beam-column” (da
```
```
Magenes et Calvi) .......................................................................................................................... 73
```
Figura 4-9: in una prova a taglio su pannello murario in cui si mantiene il parallelismo delle basi,
```
si ha che: θi=θj=θ=δ/H (da Magenes et Calvi) ............................................................................... 74
```
```
Figura 4-10: ciclo isteretico sperimentale della prova MI3; in giallo i quattro mezzi cicli oggetto
```
di analisi. ........................................................................................................................................ 85
```
Figura 4-11: mezzo ciclo “0”; in rosso la curva sperimentale, in nero il risultato numerico ......... 86
```
```
Figura 4-12: mezzo ciclo “6”; in rosso la curva sperimentale, in nero il risultato numerico ......... 86
```
```
Figura 4-13: mezzo ciclo “12”; in rosso la curva sperimentale, in nero il risultato numerico ....... 86
```
```
Figura 4-14: mezzo ciclo “18”; in rosso la curva sperimentale, in nero il risultato numerico ....... 87
```
Figura 4-15: esempi di danni in fasce di piano dovuti a sisma in edifici esistenti in muratura
semplice ......................................................................................................................................... 88
```
Figura 4-16: comportamento della parete con fasce di piano senza (a) e con (b) resistenza e
```
```
rigidezza flessionale (da edificiinmuratura.it)................................................................................ 89
```
```
Figura 4-17: sollecitazioni agenti sulla fascia di piano (spandrel). ................................................ 90
```
Figura 4-18: Sollecitazioni di pressoflessione agenti sulla fascia di piano e andamento tensioni
```
(possibile rottura per fessurazione diagonale). .............................................................................. 91
```
```
Figura 4-19: il ribaltamento dei pannelli murari (con Tult) è impedito dai tiranti .......................... 91
```
Figura 4-20: pannello con tiranti inseriti alle estremità dello spandrel. ......................................... 92
Figura 4-21: dimensionamento tiranti e capochiave da programma di edificiinmuratura.it .......... 93
Figura 4-22: in rosso, le molle orizzontali spandrel....................................................................... 95
Figura 4-23: in rosso, le molle diagonali spandrel ......................................................................... 98
Figura 4-24: in rosso, le molle verticali spandrel......................................................................... 100
Figura 4-25: schema utilizzato per la rigidezza dei beam assegnati al modello .......................... 102
```
Figura 5-1: le due tipologie di consolidamento analizzate (da Piazza, Baldessari et al.) ............ 105
```
```
Figura 5-2: schema della prova sperimentale (da Piazza, Baldessari et al.) ................................ 106
```
```
Figura 5-3: Definizione del modello Pinching4 (da S.Mazzoni et al.) ........................................ 107
```
```
Figura 5-4: Tabella riassuntiva delle caratteristiche del solaio rinforzato con tavolato 45° (da
```
```
Piazza, Baldessari et al.) .............................................................................................................. 108
```
Figura 5-5: Ciclo di carico-spostamento della prova sperimentale del solaio rinforzato con
```
tavolato a 45° (da Piazza, Baldessari et al.) ................................................................................. 109
```
Figura 5-6: Ciclo isteretico del modello del solaio con tavolato a 45° ........................................ 110
```
Figura 5-7: Tabella riassuntiva delle caratteristiche del solaio rinforzato con soletta in c.a. (da
```
```
Piazza, Baldessari et al.) .............................................................................................................. 111
```
EFFETTI DEL RINFORZO DI SOLAI IN LEGNO NEL MIGLIORAMENTO SISMICO DI
EDIFICI ESISTENTI IN MURATURA – MODELLAZIONE NUMERICA DELLE PARETI
229
Figura 5-8: Ciclo di carico-spostamento della prova sperimentale del solaio rinforzato con soletta
```
in calcestruzzo armato (da Piazza, Baldessari et al.) .................................................................... 112
```
Figura 5-9: Ciclo isteretico del modello del solaio con tavolato a 45° ......................................... 113
```
Figura 6-1: Macromodello utilizzato per l’esempio; in nero, la numerazione dei nodi e le quote (in
```
```
mm); in blu, la numerazione dei truss infinitamente rigidi inseriti nel modello. ......................... 114
```
Figura 6-2: molle implementate nel modello ............................................................................... 115
Figura 6-3: cerchiate in rosso, molle diagonali superiori analizzate nel presente paragrafo ........ 123
Figura 7-1: pianta dell’edificio e direzione sisma ........................................................................ 126
Figura 7-2: Macromodello utilizzato per l’esempio ..................................................................... 128
Figura 7-3: molle implementate nel modello ............................................................................... 128
Figura 7-4: discretizzazione del solaio ......................................................................................... 129
Figura 7-5: immagine 3D dell’edificio in analisi ......................................................................... 129
Figura 7-6: file di input inseriti nel programma SIMQKE-GR .................................................... 132
Figura 7-7: spettro elastico ricavato da programma SIMQKE-GR .............................................. 132
Figura 7-8: grafico della TH-1 da SIMQKE-GR.......................................................................... 133
Figura 7-9: grafico della TH-2 da SIMQKE-GR.......................................................................... 133
Figura 7-10: grafico della TH-3 da SIMQKE-GR........................................................................ 133
Figura 7-11: tabella 2.5.I delle NTC08 – valori dei coefficienti di combinazione. ...................... 134
Figura 7-12: nomenclatura dei nodi ............................................................................................. 136
Figura 7-13: nomenclatura dei nodi ............................................................................................. 145
Figura 7-14: Andamento medio delle pareti per le due tipologie di solaio .................................. 150
Figura 7-15: Andamento medio del solaio nei due casi analizzati ............................................... 151
Figura 7-16: Andamento medio del solaio nei due casi analizzati ............................................... 151
Figura 8-1: pianta dell’edificio e direzione sisma ........................................................................ 152
Figura 8-2: Qui a lato, si rappresentano le quote della parete di 13.5 m, la numerazione dei nodi
```
e la numerazione dei truss infinitamente rigidi (in verde) inseriti nel modello di OpenSees....... 155
```
```
Figura 8-3: Qui a lato, si rappresenta la numerazione delle molle (sia dei maschi che delle fasce
```
```
di piano) e la numerazione dei nodi inseriti nel modello di OpenSees. ....................................... 156
```
Figura 8-4: discretizzazione del solaio in analisi.......................................................................... 157
Figura 8-5: immagine 3D dell’edificio ......................................................................................... 157
Figura 8-6: nomenclatura dei nodi ............................................................................................... 158
Figura 8-7: Andamento dei muri laterali per i 3 accelerogrammi e andamento medio ................ 182
Figura 8-8: Andamento del muro centrale per i 3 accelerogrammi e andamento medio .............. 183
Figura 8-9: Andamento del solaio per i 3 accelerogrammi e andamento medio .......................... 183
Figura 8-10: nomenclatura dei nodi ............................................................................................. 185
Figura 8-11: Andamento dei muri laterali per i 3 accelerogrammi e andamento medio .............. 208
INDICE DELLE FIGURE
230
Figura 8-12: Andamento del muro centrale per i 3 accelerogrammi e andamento medio ........... 209
Figura 8-13: Andamento del solaio per i 3 accelerogrammi e andamento medio........................ 209
Figura 8-14: Andamento medio dei muri laterali per i due casi studio ........................................ 213
Figura 8-15: Andamento medio del muro centrale per i due casi studio ..................................... 214
Figura 8-16: Andamento medio del solaio per i due casi studio .................................................. 214
Figura 8-17: Differenza di spostamenti tra solaio e muri laterali ................................................ 215
Figura 8-18: Differenza di spostamenti tra solaio e muro centrale .............................................. 216