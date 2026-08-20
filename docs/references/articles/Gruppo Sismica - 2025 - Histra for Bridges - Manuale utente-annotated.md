# MANUALE UTENTE
Copyright of Gruppo Sismica s.r.l.
ITALY
25
Manuale Utente HISTRA INDICE
Update number 20251013_01
Del 13/10/2025
______________________________________________________
HISTRA Arches and Vaults ed HISTRA BRIDGES sono prodotti da:
Viale Andrea Doria, 27
95125 Catania
```
Telefono: +39 095 504749
```
```
Email: info@grupposismica.it
```
```
Web: www.grupposismica.it
```
Supporto tecnico:
Servizio assistenza tecnica tramite Tickets su
```
https://www.grupposismica.it/supporto
```
Assistenza telefonica: +39 095 504749
Proprietà letteraria riservata
Gruppo Sismica s.r.l. © Ottobre 2011
Si ringraziano coloro che hanno collaborato alla
stesura del presente manuale.
Manuale Utente HISTRA INDICE
INDICE
1 INTRODUZIONE 7
1.1 Su questo manuale 7
2 GESTIONE DEL MODELLO 8
2.1 Elementi computazionali 8
2.1.1 Macro-elemento a quattro nodi: Quad 10
2.1.2 Macro-elemento a tre nodi: Vertex 10
2.1.3 Elemento truss 11
2.1.4 Elemento fiber 11
2.1.5 Sistemi di coordinate 13
2.1.6 Gradi di libertà 13
2.1.7 Principi generali per la discretizzazione in mesh 13
2.1.8 Considerazioni di modellazione 15
3 Installazione e aggiornamento di HISTRA 17
3.1 Primo accesso 17
3.1.1 Note per i vecchi utenti 19
3.1.2 Gruppo Sismica Licensing 19
3.1.3 Pagina personale My Account 22
4 CREAZIONE DI UN NUOVO MODELLO 27
4.1 Modelli strutturali da Wizard in HISTRA Arches and Vaults 27
4.2 Modelli strutturali da Wizard in HISTRA BRIDGES 29
5 HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI
INPUT 30
5.1 DEFINIZIONE DELLA GEOMETRIA MEDIANTE WIZARD 30
5.1.1 GLI ARCHI 31
5.1.2 LE VOLTE 32
5.1.3 Creazione di un modello tramite .dxf 41
6 HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT 43
6.1 DEFINIZIONE DELLA GEOMETRIA DEL PONTE 45
```
6.1.1 Caratteristiche generali (General) 46
```
Manuale Utente HISTRA INDICE
```
6.1.2 Definizione geometria spalle (Left/Right abutment) 52
```
```
6.1.3 Definizione geometria campate (Span N) 55
```
6.1.4 Caratteristiche geometriche della pila 56
6.1.5 Backfill 59
6.2 DEFINIZIONE DEI MATERIALI 60
6.2.1 Material > Masonry materials 60
6.2.2 Material > Steel materials 71
6.2.3 Material > Fiber materials 72
6.2.4 Material > Geothecnical materials 73
6.3 DEFINIZIONE DEI CARICHI 74
6.3.2 Loads > Vehicles loads 80
6.3.3 Loads > Area loads 83
6.3.4 Loads > Line loads 85
6.3.5 Loads > Point loads 85
6.4 DEFINIZIONE DEGLI SCHEMI DI CARICO 87
6.5 DEFINIZIONE E ASSEGNAZIONE DELLE COMBINAZIONE DI CARICO ANALISI 92
7 AREA DI LAVORO 93
7.1 MENU CONTESTUALE 94
7.2 MENU PRINCIPALE 95
7.3 MENU COMANDI RAPIDI 96
7.4 BARRA DELLE INFORMAZIONI 100
7.5 FINESTRA DELLE PROPRIETA' DEL MODELLO 101
8 MENU PRINCIPALE 103
8.1 FILE 103
8.1.1 New 103
8.1.2 Open 103
8.1.3 Recent files 103
8.1.4 Save 103
8.1.5 Save as 104
8.1.6 Close 104
8.1.7 Open log file 104
8.1.8 Import dxf 104
8.1.9 Export dxf 105
8.2 MODEL 106
Manuale Utente HISTRA INDICE
8.2.1 Info 106
8.2.2 Advanced options 108
8.2.3 Update computational model 110
8.2.4 Select 110
8.3 VIEW 111
8.3.1 Number of views 112
8.3.2 Geometric/Computational 112
8.3.3 Show all 113
8.3.4 Show only selected elements 113
8.3.5 Show only elements in groups 113
8.3.6 Hide selected elements 114
8.3.7 Show only elements in group 114
8.3.8 Invert visibility 114
8.3.9 View options 114
8.3.10 Color according to 116
8.3.11 View direction 117
8.4 DEFINE 117
8.4.1 Materiali 118
8.4.2 Definizione dei carichi 118
8.4.3 Schema 130
8.4.4 Load combination 131
8.4.5 Analyses 132
Group Objects 146
8.5 DRAW 147
8.6 EDIT 148
8.7 RUN 150
8.7.1 Toolbar dei comandi 151
8.7.2 Tabella di selezione delle analisi 151
8.7.3 Log di output delle analisi 152
8.7.4 Anteprima della curva di carico 152
8.8 RESPONSE 152
8.8.1 Stress / Strain 154
8.8.2 Interface 155
8.8.3 Truss 157
8.8.4 Plot push-over curve F-U / λ-U 158
Manuale Utente HISTRA INDICE
8.8.5 Plot response curve 159
8.8.6 Plot Influence Line 161
8.9 CHECKS 162
8.10 REPORT 162
8.10.1 Word Reports 162
8.10.2 Excel Tables 170
8.11 HELP 170
Manuale Utente HISTRA INTRODUZIONE
1 INTRODUZIONE
HISTRA è il software per la modellazione strutturale 3D ed analisi non lineare di strutture in muratura a
geometria curva. La strategia di modellazione consente di simulare la risposta inelastica della struttura
```
mediante un innovativo approccio per macro-elementi discreti (DMEM), basato su un macro-elemento
```
3D a geometria curva, nato per simulare il comportamento non lineare delle strutture voltate in muratura
```
(Caliò et al.).
```
L'approccio utilizzato consente di ottenere un grado di accuratezza nella risposta confrontabile con altri
approcci di modellazione avanzati FEM, pur richiedendo un basso onere computazionale, poiché i gradi
di libertà del modello non sono proporzionali al numero dei nodi, ma al numero dei macro-elementi in
cui la struttura viene discretizzata.
Ciascun Macro-Elemento è rappresentativo del comportamento strutturale di una porzione solida mu-
raria e possiede 6 gradi di libertà di corpo rigido ed 1 grado di libertà di deformabilità a taglio. Questi
interagiscono tra loro mediante interfacce discretizzate in links non lineari, calibrati mediante un ap-
proccio a fibre, che permettono di simulare la risposta inelastica della muratura attraverso legami costi-
tutivi isteretici, asimmetrici nella resistenza e nella legge costitutiva, che possono prevedere un degrado
nella resistenza in accordo all'energia di frattura assunta o rilasciata dalla muratura.Con HISTRA è pos-
sibile analizzare la diffusione della frattura nella muratura, grazie ad interfacce non lineari che consen-
tono la simulazione di tali meccanismi di rottura ed alle procedure numeriche avanzate a controllo di
forza e di spostamento.
1.1 Su questo manuale
Questo manuale descrive i concetti teorici alla base delle funzionalità di modellazione e di analisi, l’in-
terfaccia grafica e le caratteristiche d’uso offerta da HISTRA.
HISTRA BRIDGES e HISTRA Arches and Vaults sono i due pacchetti di cui si compone HISTRA. Ciascun
pacchetto è costituito da un sistema completamente autonomo e integrato per modellare e analizzare
strutture di un particolare tipo:
- HISTRA Arches and Vaults: per strutture in muratura a carattere monumentale che molto spesso
```
si compongono di elementi a geometria curva come archi, volte e cupole;
```
- HISTRA BRIDGES: per ponti sia carrabili che ferroviari.
Nel manuale si farà riferimento ad HISTRA in generale quando ci si riferisce a caratteristiche, funziona-
lità ed opzioni uguali in entrambi in pacchetti. Si farà specifico riferimento a HISTRA BRIDGES o ad HI-
STRA Arches and Vaults in caso di funzionalità specifiche.
È’ fondamentale leggere questo manuale e assimilare gli assunti e le procedure utilizzate dal porgramma
di calcolo. L’utente deve comunque possedere una buona padronanza delle problematiche connesse con
l’ingegneria strutturale e sismica e deve conoscere i principi base delle strutture murarie e degli altri
materiali impiegati, per non incorrere a gravi errori dovuti ad una modellazione improprio che molto
spesso non possono essere individuati dal programma.
Manuale Utente HiStrA GESTIONE DEL MODELLO
2 GESTIONE DEL MODELLO
In questo capitolo vengono descritti gli elementi computazionali utilizzati dal software HISTRA, vengono
chiariti i sistemi di coordinate e i gradi di libertà tipici dell’approccio a macro-elementi discreti imple-
mentato in HISTRA. Vengono inoltre definiti i principi generali per la creazione della mesh di cui l’utente
ha pieno controllo.
Per analizzare e verificare una struttura utilizando HISTRA in generale sono necessari i seguenti pas-
```
saggi:
```
1. Creare o modificare un modello che definisca correttamente la geoemtria della struttura da analiz-
```
zare. La creazione di un modello può avvenire tramite importazione di un modello CAD (.dxf) o tramite
```
input parametrico. La procedura di input parametrico, semplice e intuitiva, consente di generare in pochi
click il modello di calcolo tridimensionale, considerando le diverse tipologie strutturali, quali archi, volte,
cupole, ponti ad arco multi-campata considerando l’interazione terreno-struttura ed eventuali sistemi
```
di rinforzo, quali catene, fibre (FRP, FRCM).
```
2. Eseguire le analisi. Il software dispone di un potente solutore a matrici sparse, sviluppato da ricercatori
dell'Università di Catania, che permette l'esecuzione di analisi statiche non lineari a controllo di forza e
spostamento, per la valutazione della capacità portante della struttura in condizioni statiche e sismiche.
In particolare sono implementate:
 l'analisi modale, per la caratterizzazione dinamica dei modi e delle frequenze proprie di vibrare della
```
struttura;
```
 l'analisi statica non lineare incrementale a controllo di forza, monotona o di tipo ciclico, basata sul
```
metodo di Newton-Raphson standard o modificato;
```
 l'analisi statica non lineare incrementale a controllo di spostamento, monotona o di tipo ciclico, ba-
sata sul metodo di Arc Length ovvero con il metodo Control-Displacement.
Le analisi statiche non lineari incrementali possono essere eseguite attivando la routine di LineSearch,
secondo le procedure Interpolated, RegulaFalsi, Bisection, Secant.
3. Esaminare i risultati delle analisi. La lettura dei risultati, consente una chiara visione della risposta
globale e locale di ciascuna fibra, mediante opportune mappe di colore in termini di tensioni, deforma-
zioni, deformazioni plastiche, indicatori di danno, sia nelle viste 3D, che con grafici 2D. I risultati ottenuti
possono essere esportati in tabelle con files formato .XLS ed in grafici nei formati standard più comuni.
4. Ottenere una relazione di calcolo. La presenza di un report automatico, conseente la generazione au-
tomatica del relazione di calcolo , comprendente tutti gli input e gli output richiesti dalla normativa per
la versione Histra Bridges Rail.
2.1 Elementi computazionali
HISTRA implementa il macro-elemento irregolare, sviluppato presso l’Università di Catania, apposita-
mente concepito per simulare i meccanismi di rottura di pannelli murari. Tale macro-elemento viene
rappresentato attraverso un semplice schema meccanico equivalente, costituito da un quadrilatero ar-
```
ticolato (deformabile a taglio), interagente con gli altri macro-elementi mediante interfacce nonlineari,
```
Manuale Utente HISTRA GESTIONE DEL MODELLO
9
orientabili nello spazio1. Esso riesce a cogliere tutti i meccanismi di collasso principali della muratura per
presso flessione, taglio e scorrimento.
Le interfacce discrete, che regolano il comportamento non lineare membranale, torsionale e a scorri-
mento, sono costituite da un letto di molle, calibrate mediante un approccio a fibre. Le porzioni di mura-
tura, modellate mediante macro-elementi, vengono discretizzate in fibre, caratterizzate da un legame
costitutivo nonlineare. Ciascuna fibra, sostituita da una molla nonlineare, interagisce con l’interfaccia
posta tra due macro-elementi. Le molle nonlineari, che regolano il comportamento membranale tra due
porzioni murarie, ciascuna modellata mediante macro-elementi, risultano combinate in serie e sostituite
da un’unica molla equivalente. Il meccanismo di rottura per scorrimento viene simulato attraverso molle
nonlineari contenute nel piano dell’interfaccia. Infine, il meccanismo di rottura per taglio con fessura-
zione diagonale del pannello murario è simulato mediante una molla diagonale nonlineare.
Le procedure automatizzate di mesh consentono la discretizzazione per macro-elementi di superfici
curve.
Il software HISTRA implementa anche macro-elementi solidi, a tre nodi, adatti alla modellazione di por-
```
zioni a geometria più complessa, non rappresentabili con macro-elementi a quattro nodi (Figura 2.1).
```
```
Figura 2.1 - A sinistra (a) suddivisione di una cupola in porzioni omogenee; a destra (b) modello a macro-elementi
```
equivalente
```
Gli elementi computazionali definibili sono i macro-elementi a quattro nodi (quad), i macro-elementi a
```
```
tre nodi (vertex), gli elementi finiti truss, utili per modellare gli elementi di rinforzo (tiranti, catene), e gli
```
elementi fiber per la simulazione dei rinforzi in FRP.
Alla definizione della geometria del modello corrisponde un modello computazionale, sul quale vengono
condotte le analisi numeriche.
Il macro-elemento è in grado di simulare i comportamenti meccanici tipici di elementi in muratura delle
strutture a geometria curva con un approccio in cui la risposta membranale e flessionale è governata da
una discretizzazione per fibre lungo le direzioni principali dell'elemento, mentre la risposta tagliante e
torsionale viene simulata macroscopicamente da un numero discreto di links non lineari.
```
1 Caliò, Cannizzaro, Marletta (2010), “A discrete element for modeling masonry vaults”. Adv. Mater. Res. 133-134, 447-452.
```
Manuale Utente HISTRA GESTIONE DEL MODELLO
10
2.1.1 Macro-elemento a quattro nodi: Quad
Il macro-elemento a 4 nodi, detto quad, è un quadrilatero articolato irregolare con lati rigidi, i cui vertici
coincidono con i vertici del concio e la cui deformazione nel piano è controllata da un link non lineare
posto lungo una delle sue diagonali. L'interazione con gli altri quadrilateri e/o con i supporti esterni è
affidata a interfacce spaziali, in generale inclinate rispetto al piano del quadrilatero, in cui risulta dispo-
sto un numero discreto di links non lineari sia in direzione ortogonale che nel piano delle interfacce
stesse.
I due principali elementi del modello sono pertanto un elemento quadrilatero, costituito appunto da un
quadrilatero articolato, e da un elemento interfaccia destinato alla caratterizzazione dell'interazione tra
i quadrilateri e con i supporti esterni.
Il link diagonale del quadrilatero è inserito per la simulazione della deformabilità a taglio nel proprio
piano. Ogni quadrilatero è definito, oltre che dalle coordinate geometriche dei suoi vertici, anche dalle
quattro normali alla superficie e dagli spessori dell'elemento curvo in corrispondenza degli stessi vertici.
L'inclinazione e la forma dell'interfaccia vengono determinate proprio a partire dalle normali alla super-
ficie e dagli spessori nei punti iniziale e finale della stessa interfaccia. Nei links delle interfacce vengono
concentrate la deformabilità membranale e flessionale della porzione di muratura considerata, oltre alla
deformabilità torsionale e al controllo dell'attivazione dei meccanismi di scorrimento. I gradi di libertà
di un elemento quad sono 7: le 3 traslazioni e le 3 rotazioni del centro di massa nello spazio rispetto al
sistema di riferimento globale, più 1 scorrimento angolare dovuto alla deformabilità a taglio nel piano
del macro-elemento.
Figura 2.2 – Macro-elemento a 4 nodi
2.1.2 Macro-elemento a tre nodi: Vertex
```
Il macro-elemento a 3 nodi, detto vertex, è un macro-elemento rigido (non deformabile nel suo piano)
```
nato per far fronte alle esigenze di modellazione di strutture a geometria curva e irregolare, poiché non
sempre è possibile l'uso esclusivo di elementi quadrangolari. Questi elementi consentono la modella-
zione di zone come quella in chiave di una cupola o quelle di intersezione tra superfici che sono parti di
volta composta, che risultano spesso decisive per cogliere il danneggiamento nelle strutture murarie a
geometria curva.
Manuale Utente HISTRA GESTIONE DEL MODELLO
11
Questi elementi sono individuati da tre nodi e risultano quindi costituiti, in analogia con l'elemento quadran-
golare, da tre interfacce rigide. Tale condizione impedisce di articolare l'elemento con la conseguente impos-
sibilità di cogliere la deformabilità a taglio nel proprio piano della porzione di muratura modellata con un
elemento vertex. Tale approssimazione può essere tuttavia ritenuta accettabile, sia perché l'utilizzo di questi
elementi può essere limitato a piccole zone della struttura, sia perché il meccanismo di rottura prevalente è
generalmente quello membranale e pertanto l'introduzione degli elementi a tre nodi non comporta una signi-
ficativa perdita di accuratezza della soluzione.
L'interazione degli elementi speciali triangolari può avvenire sia tra elementi dello stesso tipo, sia con even-
tuali quadrilateri con i quali vengono condivisi dei lati, sia con vincoli esterni. Ad ogni modo l'interazione av-
viene mediante gli stessi elementi di interfaccia descritti per l'interazione tra elementi quadrangolari. I para-
metri lagrangiani necessari per descrivere la cinematica dell'elemento si riducono a 6, per l'assenza di defor-
mabilità a taglio nel proprio piano: le 3 traslazioni e le 3 rotazioni attorno al centro di massa rispetto ai tre assi
del sistema di riferimento globale.
Figura 2.3 – Macro-elemento a 3 nodi
2.1.3 Elemento truss
L'elemento truss consiste di un unico elemento finito dotato di sei gradi di libertà, tre traslazioni dei nodi
di estremità rispetto al sistema di riferimento globale. Questo tipo di elemento può resistere a sforzi
```
assiali di trazione e/o di compressione e può essere introdotto per modellare elementi di rinforzo (ti-
```
```
rante, catena) nell'elemento strutturale voltato.
```
2.1.4 Elemento fiber
L'elemento fiber è un elemento computazionale a 4 nodi, dotato di 6 gradi di libertà di corpo rigido, che
consente di modellare gli elementi di rinforzo in FRP o FRCM.
```
La strategia di modellazione proposta è basata sugli studi condotti da Caddemi et al. (cfr. [1], [2]) su volte
```
in muratura rinforzate con compositi in FRP e consiste nel discretizzare la volta in muratura in una mesh
```
di macro-elementi curvi (Quad), e da elementi computazionali detti Fiber (Fiber Macro-Element) per la
```
```
modellazione del composito in FRP (Figura 2.4). La modellazione dell’interazione tra il composito in FRP
```
e il supporto murario è reso possibile attraverso interfacce capaci di simulare i meccanismi di modo 1,
dovuti al distacco normale alla superficie di interfaccia, e di modo 2, causati dallo scorrimento per dela-
minazione del rinforzo in direzione tangente alla superficie dell’interfaccia.
Manuale Utente HISTRA GESTIONE DEL MODELLO
12
```
Il meccanismo di modo 1 (Figura 2.5a) viene modellato mediante un letto di molle normali al piano dell’in-
```
terfaccia, ciascuna delle quali ha un legame costitutivo non lineare fratturante calibrato mediante un
approccio a fibre sulle proprietà geometriche e meccaniche della muratura e del rinforzo.
```
Il meccanismo di modo 2 (Figura 2.5b) viene modellato mediante molle parallele al piano dell’interfaccia,
```
caratterizzate da un legame costitutivo non-lineare fratturante, calibrato anch’esso mediante un ap-
proccio a fibre sulle proprietà geometriche e meccaniche della muratura e del rinforzo.
Figura 2.4 – Strategia di modellazione del rinforzo di volte in muratura mediante applicazione di FRP
Figura 2.5 – Interazione in direzione normale e per scorrimento all’interfaccia tra rinforzo e support in muratura.
Figura 2.6 – Modello di calcolo
Manuale Utente HISTRA GESTIONE DEL MODELLO
13
```
Figura 2.7 – a) e b) Scorrimento del rinforzo sulla muratura, c) Distacco per sollevamento del rinforzo dalla muratura di
```
support
2.1.5 Sistemi di coordinate
I sistemi di coordinate sono utilizzati per posizionare parti diverse del modello geometrico, definire la
direzioni di carichi, spostamenti, sollecitazioni e tensioni.
Tutti i sistemi di coordinate del modello sono definiti facendo capo a un unico sistema di coordinate
globali. Ciascun elemento del modello è dotato di un proprio sistema di coordinate locali. Tutti i sistemi
di coordinate sono tridimensionali, destrorsi e cartesiani. L’asse Z è asuunto verticale, con direzione po-
sitiva verso l’alto. Il carico di peso proprio agisce sempre verso il basso, in direzione -Z.
Gli assi X, Y, e Z del sistema di coordinate globali sono perpendicalari tra loro e soddisfano la regola della
mano destra. Il piano XY è orizzontale.
2.1.6 Gradi di libertà
L’approccio di modellazione implementato nel software HISTRA prevede l’uso di macro-elementi quali
elementi computazionali. A differenza dei tipici approcci agli elementi finiti in cui i gradi di libertà fanno
riferimento ai singoli nodi dei singoli elementi finiti, nell’approccio a macro-elementi discreti i gradi di
```
libertà sono associati direttamente al macro-elemento (e non ai singoli nodi di esso). In particolare i gradi
```
```
di libertà del macro-elemento irregolare a quattro nodi (Quad) sono sette e corrispondono alle sei com-
```
```
ponenti di spostamento nello spazio (tre traslazione e tre rotazioni) e allla componente che ne definisce
```
```
la deformabilità a taglio nel piano. I grazi di liibertà del macro-elemento a tre nodi (Vertex) sono invece
```
sei in quanto esso è rigido nel proprio piano per conformazione geometrica e corrispondo alle sei com-
ponenti di spostamento nello spazio.
2.1.7 Principi generali per la discretizzazione in mesh
La discretizzazione avviene attraverso una mesh più o meno fitta di elementi ognuno dei quali rappre-
sentativo di una porzione di muratura. Nel caso di porzioni murarie a geometria curva, la discretizzazione
può avvenire considerando una griglia di linee curve, utili a determinare la suddivisione della struttura
in macro-conci. Nella suddivisione occorre tener presente che il singolo concio dovrà essere rappresen-
tato da un macro-elemento solido che, nella sua formulazione geometrica, individua un piano deforma-
```
bile a taglio coincidente con il piano medio del macro-elemento, individuato dai suoi nodi; pertanto i
```
risultati saranno tanto più accurati quanto più il piano deformabile a taglio del macro-elemento risulterà
```
(c)
```
Manuale Utente HISTRA GESTIONE DEL MODELLO
14
vicino alla superficie media del concio. Il numero degli elementi deve, in qualunque caso essere suffi-
ciente a descriviere la geometria della struttura: per linee e contorni dritti anche un numero abbastanza
limitato di elementi è sufficienti, per linee e superfici curve è oppurtuno utilizzare un numero maggiore
di elementi.
```
Le superfici curve semplici o composte, possono essere ricondotte a superfici cilindriche (con curva di-
```
```
rettrice di varia natura) o superfici di rivoluzione. Nel caso delle superfici cilindriche è possibile indivi-
```
duare nella direzione della retta generatrice e nelle curve parallele alla curva direttrice le due direzioni
```
principali secondo cui costruire una griglia di suddivisione della superficie (Figura 2.8).
```
Figura 2.8 - Generatrici e direttrici di una volta cilindrica.
Nel caso delle superfici di rivoluzione, i due fasci di linee intersecanti sono rappresentati dalle linee di
```
intersezione della superficie con dei piani ortogonali all’asse di rivoluzione da un lato (paralleli), come
```
mostrato in Figura 2.9, e da quelle di intersezione tra piani contenenti l’asse di rivoluzione e la superficie
```
stessa (meridiani o curve di profilo) dall’altro (Figura 2.9).
```
Figura 2.9 - Generatrici e direttrici di una cupola.
In tutti questi casi è sempre possibile determinare una suddivisione della superficie in elementi qua-
drangolari, per i quali è possibile dimostrare che i vertici di ciascuno di essi giacciono su un piano. Ele-
menti triangolari si rendono necessari per le superfici di rivoluzione se le linee di profilo convergono in
```
un punto (caso di curva di profilo che si interseca con l’asse di rivoluzione), e nel caso di volte composte
```
```
(nelle zone di intersezione tra le superfici).
```
Rispetto a un classico approccio agli elementi finiti nonlineari, il modello implementato in HISTRA pre-
senta numerosi vantaggi qui di seguito riassunti:
Manuale Utente HISTRA GESTIONE DEL MODELLO
15
```
1) La filosofia di discretizzazione per macro-conci consente di mantenere un livello di dettaglio di model-
```
```
lazione contenuto; questo consente di contenere i tempi di calcolo anche per modelli complessi (e co-
```
```
munque di mantenerli più basso rispetto ad approcci classici)
```
```
2) L'adozione delle nonlinearità avviene attraverso legami monoassiali (mediante link nonlineari) senza
```
```
far ricorso a complesse leggi costitutive bi o tri-dimensionali; questo migliora la robustezza e la stabilità
```
numerica delle analisi
I legami costitutivi adottati sono specifici per il solido murario, e consentono di cogliere i meccanismi
```
di collasso tipici di queste tipologie strutturali (fessurazione, scorrimenti, meccanismo di taglio per fes-
```
```
surazione diagonale).
```
2.1.8 Considerazioni di modellazione
Ai fini della creazione del modello geometrico e e del conseguente modello strutturale va posta l’atten-
zione ad alcuni aspetti di modellazione particolari.
I contorni di un elemento, e di conseguenza i suoi nodi, devono essere posizioni in corrispondenza di
punti, linee o superfici di discontinuità. Per discontinuità si intende:
- Discontinuità strutturale, come angoli e spigoli. In questi casi bisogna porre attenzione al collega-
mento tra elementi perpendicolari e adiacenti. È necassario infatti porre attenzione al fatto che,
```
considerando gli spessori strutturali (si ricorda che il macro-elemento approssima il piano medio
```
```
dell’elemento strutturale), i due elementi siano adiacenti.
```
- Cambiamenti nelle proprietà del materiale. Ogni materiale va assegnato al singolo elemento. Due
materiali diversi e adiacenti devono corrispondere a due diversi macro-elementi adiacenti.
- Cambiamenti di spessore o di altre proprietà geometriche. Ogni macro-elemento può essere a tre o
```
a quattro nodi (un diverso numero di nodi non è ammissibile), ad ogni nodo del singolo macro-ele-
```
```
mento può essere assegnato uno spessore. Cambiamenti bruschi di spessore (come nicchie, ingros-
```
```
samenti delle pareti murarie, ecc.) vanno modellati separando i macro-elementi nel punto in cui
```
cambia lo spessore.
INTERFACCIA
ELEMENTO COMPUTA-
```
ZIONALE (QUAD)
```
Manuale Utente HISTRA GESTIONE DEL MODELLO
16
Bibliografia Capitolo 2
[1] S. Caddemi, I. Caliò, F. Cannizzaro, P.B. Lourenco, B. Pantò “FRP-reinforced masonry structures: numerical
modeling by means of a new discrete element approach”, COMPDYN 2017, 6th ECCOMAS Thematic Con-
ference on Computational Methods in Structural Dynamics and Earthquake Engineering, M. Papadraka-
```
kis, M. Fragiadakis (eds.), Rhodes Island, Greece, 15–17 June 2017.
```
[2] Bartolomeo Pantò, Francesco Cannizzaro, Salvatore Caddemi, Ivo Caliò, César Chácara E Paulo B. Lou-
renço - “Nonlinear Modelling of Curved Masonry Structures after Seismic Retrofit through FRP Reinforc-
ing”, Buildings 2017, 7, 79.
[3] M. Malena, G. De Felice, “Debonding of composites on a curved masonry substrate: Experimental results
```
and analytical formulation”, Composite Structures 112(2014), p.194–206
```
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
3 INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
Gruppo Sismica ha messo a disposizione dei propri utenti una procedura di gestione delle licenze dei
programmi da gestire con il sistema di licensing integrato sul sito web Gruppo Sismica. Tale procedura
consente una migliore e più semplice gestione dell’installazione ed aggiornamento delle licenze di tutti
i software, utilizzando un unico set di credenziali, valide per tutti i prodotti.
3.1 Primo accesso
Per attivare la licenza occorre:
1. Accedere all’area utente all’indirizzo https://www.grupposismica.it/my-account/,
utilizzando le credenziali personali:
Nome utente o indirizzo email: xxxxxxxxxxxxxx@xxxxxxxxxxx.xx
```
Password: XXXXXXXXXXX
```
```
Nel caso di password dimenticata, effetturare la procedura di recupero password (cfr. § 3.1.2.2)
```
```
Nel caso di nuovo utente, effettuare la procedura di registrazione (cfr. § 3.1.2.3)
```
2. Dalla pagina “My Account” effettuare il Download del software, dalla sezione “Down-
load”, cliccando in corrispondenza della versione da scaricare.
3. Scaricare il software, installarlo e avviarlo
4. Attivare il prodotto inserendo la chiave di attivazione ricevuto per email e dis-
ponibile anche dalla pagina “My Account” alla sezione “Licenze”
Figura 3.1 - – Step 1: Accesso all’area utente.
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
18
Figura 3.2 - Step 2: Download del software
Figura 3.3 - - Step 3: Installazione del software
Figura 3.4 -. Step 4: Attivazione della licenza
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
19
3.1.1 Note per i vecchi utenti
```
È importante ricordare che il vecchio sistema di licensing (mediante Gruppo Sismica Manager e) non è
```
più operativo.
```
Per chi dispone ancora di licenze attivate con il vecchio software di gestione licenze (Gruppo Sismica
```
```
Manager), si raccomanda, prima di procedere con l'attivazione delle nuove licenze, di disattivare le vec-
```
chie licenze 3DMacro, mediante il vecchio sistema GS Manager. Questa procedura è fondamentale af-
finchè la nuova licenza venga correttamente attivata.
3.1.2 Gruppo Sismica Licensing
Il sistema di gestione licenze, abbonamenti e attivazioni è progettato per essere semplice, intuitivo e
completamente integrato con il sito web di Gruppo Sismica. Esso consente di:
```
□ Gestire licenze e abbonamenti direttamente dall’area personale del sito;
```
□ Selezionare versioni e add-on con un processo guidato che accompagna
```
dalla scelta del prodotto al pagamento e all’attivazione;
```
```
□ Attivare o rinnovare i software in maniera rapida e sicura;
```
□ Provare facilmente le nuove release o i software in arrivo, per restare sem-
```
pre aggiornati sulle innovazioni Gruppo Sismica;
```
□ Inviare eventuali richieste di assistenza e/o informazioni, mediante una ge-
stione di ticket-online.
Di seguito si riportano tutte le informazioni necessarie per una migliore navigazione ed utilizzo del por-
tale online.
3.1.2.1 Accesso alla pagina personale
È possibile accedere al pagina personale “My Account” dal sito web di Gruppo Sismica seguendo il link
```
https://www.grupposismica.it/my-account/.
```
Dalla sezione “Accedi”inserire le credenziali:
□ Nome utente o indirizzo email
□ Password
3.1.2.2 Recupero password
Se non si ricorda o non si ha a disposizione la Password, è possibile rigenerarla cliccando su “Password
dimenticata?”. Inserire l’email e cliccare sul pulsante “Resettare la password”: verrà inviata una email
```
all’indirizzo indicato (v. Figura 5.4)
```
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
20
Figura 3.5 - -. Recupero password
Figura 3.6 - - Recupero password
Accedere alla propria casella di posta elettronica e seguire il link riportato sulla email2 per resettare la
password. Cliccando sul link, il sistema reindirizza alla finestra su cui devono essere inseriti i nuovi dati
```
per la registrazione. Indicare la nuova password3; e cliccare su “Salva”.
```
2 Controllare anche la casella di posta indesiderata.
3 La Password deve contenere almeno un numero, un carattere maiuscolo, uno minuscolo, ed un carattere speciale come ! " ? $ % ^ & .
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
21
Figura 3.7 - - Conferma nuova password
Dopo aver completato la procedura, verrà mostrato un messaggio di conferma “La tua password è stata
reipostata con successo” e si verrà indirizzati all’area personale “My Account”.
3.1.2.3 Nuovi Utenti
Per i nuovi utenti è possibile registrarsi al portale mediante la sezione “Registrati” inserendo un indirizzo
email al quale verrà inviato un link per l’impostazione di una password.
Accedere alla propria casella di posta elettronica e seguire il link riportato sulla email per impostare la
```
password. Cliccando sul link, il sistema reindirizza alla finestra (Errore. L'origine riferimento non è stata
```
```
trovata.) su cui devono essere inseriti i dati per la registrazione. Indicare la nuova password e cliccare
```
su “Salva”.
Figura 3.8 - - Creazione nuova password
Dopo aver completato la procedura, verrà mostrato un messaggio di conferma “La tua password è stata
reipostata con successo” e si verrà indirizzati all’area personale “My Account”.
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
22
3.1.3 Pagina personale My Account
La schermata principale del sito web “My Account” di Gruppo Sismica è costituita da:
□ Bacheca
□ Ordini
□ Download
□ Indirizzo
□ Metodi di pagamento
□ Dettagli account
□ Licenze
□ Ticket
□ Abbonamenti
□ Esci
Figura 3.9 - -. Pagina personale “My Account”
Dal menu a sinistra è possibile accedere alle varie sezioni, le cui funzionalità e contenuti vengono chi-
arite nei successivi paragrafi.
Ordini
Nella pagina Ordini è riportato l’elenco degli ordini effettuati.
Nella schermata sono presenti le seguenti voci:
□ Ordine: Tag dell’ordine effettuato.
□ Data: Data in cui è effettuato l’ordine.
□ Stato: Stato attuale dell’ordine.
□ Totale: Importo totale dell’ordine.
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
23
□ Azioni: Cliccando su “Visualizza” consente di visualizzare i Dettagli dell’or-
dine, gli Abbonamenti correlati, l’Indirizzo di fatturazione e di effettuare i
Download.
Figura 3.10 - My account - Ordini
Download
Nella pagina Download è riportato l’elenco dei prodotti che è possibile scaricare.
Nella schermata sono presenti le seguenti voci:
□ Prodotto: Nome del software.
□ Download rimanenti: Numero di downoad che è ancora possibile eseguire.
□ Scadenza: Eventuale scadenza del download.
□ Scarica: Consente di scaricare il file di installazione del software nella ver-
sione indicata.
Indirizzo
Nella pagina Indirizzo di fatturazione sono riportati gli indiizzi che saranno usati come predefiniti nella
pagina di riepilogo dell’ordine. Inoltre, cliccando sulla voce “Modifica Indirizzo di fatturazione”, è pos-
sibile modificarlo.
Metodi di pagamento
Nella pagina Metodi di pagamento sono riportati i metodi di pagamento registrati ed è possibile ag-
giungerne di nuovi.
Dettagli
Dalla schermata Dettagli account è possibile accedere ai dati personali e modificarli.
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
24
Figura 3.11 - Dettagli account
È possibile visualizzare e modificare: Nome, Cognome, Nome visualizzato e indirizzo email. Inoltre, è
presente una sezione apposita per la modifica della password.
Per modificare la password, bisogna inserire la Password attuale, indicare e ripetere la Nuova Password4
e cliccare, infine, sul tasto “Salva le modifiche”.
Licenze
```
Nella pagina Licenze è riportato l’elenco delle licenze software intestate all’utente (Errore. L'origine ri-
```
```
ferimento non è stata trovata.).
```
Figura 3.12 - Elenco licenze.
Nella tabella presente vengono indicate le seguenti voci:
□ Prodotto: Nome del software e durata della licenza.
□ Stato: Attiva / Disattivata.
□ Postazioni: Numero di postazioni in cui è attivata la licenza e numero di po-
stazioni totali disponibili.
Cliccando su Gestisci è possibile accedere alle seguenti informazioni:
4 La password deve contenere almeno un numero, un carattere maiuscolo, uno minuscolo, ed un carattere speciale tra ! % * ? & . Se la
password non supera il controllo viene rilasciato un alert dal sistema.
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
25
□ Abbonamento: Tag dell’abbonamento da cui è possibile accedere alle in-
formazioni sull’abbonamento sottoscritto e ai costi.
□ Chiave: Chiave di attivazione della licenza. Viene trasmessa per email
quando si richiede la attivazione/disattivazione del prodotto.
□ Stato: Stato della licenza: Attiva / Disattivata.
□ Validità: Durata della licenza.
□ Scadenza: Data di scadenza della licenza d’uso del software.
□ Versione: Versione del softare a cui permette di avere accesso la licenza. Ad
esempio Extended, Startup, etc…
□ Addons: Eventuali pacchetti aggiuntivi.
Inoltre, nella parte inferiore della schermata, per ogni postazione in cui è attiva la licenza, è indicato:
□ Hostname: Nome PC su cui risulta attiva la licenza software.
□ OS: Sistema Operativo del PC su cui risulta attiva la licenza software.
□ Luogo: Nome del luogo in cui risulta attiva la licenza software.
□ Data attivazione: Data di attivazione della licenza d’uso del software.
□ Ultima sincronizzazione: Data di ultima sincronizzazione.
Inoltre, è possibile disattivare o attivare le licenze attive sulla macchina.
Figura 3.13 - Gestione licenza
Tickets
Dalla pagina Ticket è possibile chiedere assistenza e visualizzare lo stato delle precedenti richieste.
Il sistema di gestione dell’assistenza, garantisce un contatto diretto ed un’efficace interazione tra il nos-
tro staff e l’utenza.
Manuale Utente INSTALLAZIONE E AGGIORNAMENTO DI HISTRA
26
Abbonamenti
Nella pagina Abbonamenti è riportato l’elenco degli abbonamenti attivi.
Nella schermata sono presenti le seguenti voci:
□ Abbonamento: Tag dell’abbonamento attivo e nome del software.
□ Data di inizio: Data di inzio dell’abbonamento.
□ Importo ricorrente: Importo da pagare con la frequenza indicata.
□ Termina il: Data di fine dell’abbonamento.
□ Stato: Stato dell’abbonamento.
Figura 3.14 - Abbonamenti
Esci
Cliccando la voce Esci verrà eseguita la disconnessione dalla pagina personale “My Account
Manuale Utente CREAZIONE DI UN NUOVO MODELLO
4 CREAZIONE DI UN NUOVO MODELLO
L’analisi di un modello strutturale prevede come primo passaggio la creazione del modello geometrico
tridimensionale. Tale modello geometrico sarà poi trasformato in modello computazionale dal software
```
(sia che si tratti di HISTRA BRIDGES sia che si tratti di HISTRA Arches and Vaults) in maniera automatica.
```
La creazione del modello può avvenire o in maniera manuale, importando un file .dxf, creato mediante
```
software CAD utilizzando elementi “3Dface” (in italiano “Faccia3D”) o PolygonMesh per modellare su-
```
perfici piane, o per modellare oggetti 3D utilizzando l’elemento PolyfaceMesh, per modellare il singolo
macro-elemento a tre o quattro nodi, oppure in maniera guidata e parametrica tramite Wizard.
```
All'avvio di HISTRA (o selezionando il menu File e cliccando New), si aprirà in maniera automatica la
```
finestra “HISTRA Wizard”. l’utente dovrà scegliere attraverso la finestra “HISTRA Wizard”, in Figura 4.1,
una delle opzioni per la creazione del modello, disponibili in questo pannello generale di lavoro.
In generale la finistra di Wizard è organizzata nel seguente modo: sul lato sinistro della finestra, al fine
di avviare un nuovo modello, sono disponibili numerose tipologie di modelli strutturali cui poter acce-
dere. Se si seleziona una di queste tipologie, l’utente dovrà fornire le caratteristiche geometriche
```
dell’elemento strutturale (vedi paragrafi successivi per i dettagli), in maniera guidata e parametrica.
```
Sulla parte destra sono disponibili altre informazioni, tra cui la versione del software utilizzata e altre
opzioni. È possibile infatti aprire un modello già creato e i modelli recentemente creati e utilizzati ven-
gono mostrati in un elenco in ordine cronologico.
In alto a destra viene anche indicato la disponibilità di una versione più aggiornata. Cliccando sulla cor-
rispondente icona si accederà al pannello di controllo HISTRA Manager dal quale sarà possibile aggior-
nare la versione.
Immediatamente sotto è possibile aprire un modello esistente generico o uno a scelta tra quelli recenti.
I modelli strutturali presenti per la procedura di input guidata sono diversi se si tratta di HISTRA BRIDGES
o di HISTRA Arches and Vaults.
4.1 Modelli strutturali da Wizard in HISTRA Arches and Vaults
Nel caso di HISTRA Arches and Vaults i modelli strutturali che possono essere creati tramite input para-
metrico sono:
Arco
Volta a botte
Volta a crociera
Manuale Utente CREAZIONE DI UN NUOVO MODELLO
28
Volta a vela
Volta a padiglione
Volta a specchio
Cupola
Figura 4.1 - Schermata principale HISTRA Arches and Vaults Wizard per la creazione di un nuovo modello
Manuale Utente CREAZIONE DI UN NUOVO MODELLO
29
4.2 Modelli strutturali da Wizard in HISTRA BRIDGES
Nel caso di HISTRA BRIDGES possono invece essere creati mediante procedura di input parametrico:
```
Ponti ferroviari (Rail)
```
```
Ponti stradali (Road)
```
Figura 4.2 - Schermata principale HISTRA BRIDGES Wizard per la creazione di un nuovo modello
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
5 HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
HISTRA Arches and Vaults è il software dedicato alla modellazione e l’analisi non lineare di strutture a
carattere storico e monumentale. La piattaforma informatica è basata su un approccio innovativo sia per
```
le procedure di input degli elementi strutturali (basati su procedure semplificate e parametrizzate), sia
```
per l'originale approccio di modellazione adottato, su cui sono basate le procedure di calcolo.
5.1 DEFINIZIONE DELLA GEOMETRIA MEDIANTE WIZARD
HISTRA Arches and Vaults fornisce all’utente un valido supporto per l’impostazione generale del mo-
dello di studio attraverso una interfaccia semplice e intuitiva.
La procedura guidata di input parametrico, semplice ed intuitiva, consente di generare in pochi click il
modello di calcolo, considerando le diverse tipologie geometriche di archi, volte, cupole ricorrenti. L'u-
tente dovrà fornire in pochi passaggi i parametri geometrici e meccanici che caratterizzano la struttura
Con HISTRA Arches and Vaults è possibile modellare facilmente e velocemente le varie tipologie strut-
turali a geometria curva, comunemente presenti negli edifici storici. Un accurato algoritmo di meshing
genera il modello computazionale automaticamente, a partire dall’input geometrico.
E’ inoltre possibile inserire i tiranti e le catene, impiegati per il rinforzo strutturale degli edifici storici
```
(compatibilmente con la tipologia di elemento considerato).
```
```
La caratterizzazione dei materiali e la definizione dei parametri geometrici (quali spessore, caratteristi-
```
```
che d’inerzia, proprietà resistenti) descrivono ciascun oggetto geometrico, determinandone il compor-
```
tamento strutturale.
Oltre ad utilizzare l’input semplificato mediante la procedura guidata di wizard, è anche possibile creare
```
il modello in HISTRA importando la geometria da un modello dxf (cfr. § 8.1.8).
```
Figura 5.1 – Creazione del modello geometrico di una volta, mediante lo strumento di Wizard.
La generazione degli elementi strutturali avviene in automatico: il programma genera ad ogni variazione
della geometria il “modello computazionale”, sul quale vengono eseguite le analisi.
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
31
```
(a) (b)
```
```
Figura 5.2 - A sinistra (a) vista del modello geometrico di una volta a crociera; a destra (b) vista del modello compu-
```
tazionale equivalente.
5.1.1 GLI ARCHI
Le strutture ad arco possono essere modellate mediante assemblaggio di un insieme di macro-elementi
quad. È possibile orientare i macro-elementi in modo da ottenere una geometria a sezione variabile dalla
sezione di imposta a quella di chiave e posizionare una catena ad una certa altezza dal piano di imposta
```
come elemento di rinforzo per aumentarne la capacità di resistenza dell'elemento (cfr. 5.1.1.1).
```
5.1.1.1 Creazione di un arco
Per generare un arco occorre compilare i seguenti riquadri:
Figura 5.3 – Input parametrico delle caratteristiche geometriche di un arco
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
32
Figura 5.4 - Schermata di riferimento per la creazione del modello geometrico di un arco
□ Arc parameters
o Definizione della geometria generale:
```
 L=distanza, sul piano d’imposta dell’arco, misurata tra i paramenti d’intradosso;
```
```
 f=freccia dell’arco tra piano d’imposta e intradosso della sezione di chiave dell’arco;
```
```
 t0=spessore dell’arco sul piano d’imposta;
```
```
 t1=spessore dell’arco sulla sezione di chiave;
```
```
 w=profondità dell’arco;
```
o Shape, forma geometrica dell’arco:
```
 Ellipse;
```
```
 Parabolic;
```
o Lmax=lunghezza massima degli elementi utilizzata per la discretizzazione dell’arco nel modello
```
computazionale;
```
o Selezionare l’opzione Has truss per generare un tirante di rinforzo:
```
 Ztruss=altezza di posizione del rinforzo misurata a partire dalla sezione d’imposta;
```
□ Left wall
o Selezionare Left wall per generare la parete di sinistra:
```
 L1top=spessore della parete di sinistra in testa;
```
```
 L1bot=spessore della parete di sinistra al piede;
```
```
 H1=altezza della parete di sinistra;
```
 S1=distanza tra l’intradosso dell’arco sulla sezione d’imposta di sinistra e il paramento
```
interno della parete di sinistra;
```
□ Right wall
o Selezionare Right wall per generare la parete di destra:
```
 L2top=spessore della parete di destra in testa;
```
```
 L2bot=spessore della parete di destra al piede;
```
```
 H2=altezza della parete di destra;
```
 S2=distanza tra l’intradosso dell’arco sulla sezione di imposta di destra e il paramento
```
interno della parete di destra;
```
Lo schema quotato dell’arco è mostrato in Figura 5.4.
5.1.2 LE VOLTE
Mediante la schermata wizard è possibile introdurre nel modello geometrico le forme più ricorrenti di
strutture a volta. Anche in questo caso è possibile orientare i macro-elementi in modo da avere una
geometria a sezione variabile dal piano di imposta al piano in chiave della volta, ed ottenere dei ringrossi
ai bordi dell'elemento.
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
33
È possibile scegliere la tipologia di struttura voltata da definire geometricamente tra le seguenti:
```
 Barrel vault (cfr. 5.1.2.1);
```
```
 Cross vault (cfr. 5.1.2.2);
```
```
 Domical vault (cfr. 5.1.2.3);
```
```
 Cloister vault (cfr. 5.1.2.4);
```
```
 Cloister vault intersected with an horizontal plane (cfr. 5.1.2.5);
```
5.1.2.1 Creazione di una volta a botte
Per generare una volta a botte occorre compilare i seguenti riquadri:
Figura 5.5 – Input parametrico delle caratteristiche geometriche di una volta a botte.
Figura 5.6 - Schermata di riferimento per la creazione del modello geometrico di una volta a botte
□ Barrel vault parameters
o Definizione della geometria generale:
 L=distanza sul piano d’imposta dell’arco, sezione retta della volta, misurata tra i para-
```
menti d’intradosso;
```
```
 f=freccia dell’arco, sezione retta della volta;
```
```
 t0=spessore della volta sul piano d’imposta;
```
```
 t1=spessore della volta sulla sezione di chiave;
```
```
 w=profondità della volta a botte;
```
o Shape, la forma geometrica dell’arco, sezione retta della volta:
```
 Ellipse;
```
```
 Parabolic;
```
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
34
o Lmax= lunghezza massima degli elementi utilizzata per la discretizzazione della volta a botte nel
```
modello computazionale;
```
□ Left wall
o Selezionare Left wall per generare la parete di sinistra:
```
 H1=altezza della parete di sinistra;
```
```
 L1top=spessore della parete di sinistra in testa;
```
```
 L1bot=spessore della parete di sinistra al piede;
```
 S1=distanza tra l’intradosso della volta sulla sezione d’imposta di sinistra e il para-
```
mento interno della parete di sinistra;
```
□ Right wall
o Selezionare Right wall per generare la parete di destra:
```
 H2=altezza della parete di destra;
```
```
 L2top=spessore della parete di destra in testa;
```
```
 L2bot=spessore della parete di destra al piede;
```
 S2=distanza tra l’intradosso della volta sulla sezione di imposta di destra e il para-
```
mento interno della parete di destra;
```
□ Lateral archs
o Selezionare Lateral archs per generare gli archi di estremità della volta:
```
 w’=profondità dei ringrossi degli archi di estremità della volta;
```
```
 T0=spessore degli archi di estremità, ai bordi della volta a botte, sul piano d’imposta;
```
 T1=spessore degli archi di estremità, ai bordi della volta a botte, sulla sezione di chiave.
Lo schema quotato della volta a botte è mostrato in Figura 5.6.
5.1.2.2 Creazione di una volta a crociera
Per generare una volta a crociera occorre compilare i seguenti riquadri:
Figura 5.7 – Input parametrico delle caratteristiche geometriche di una volta a crociera.
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
35
Figura 5.8 - Schermata di riferimento per la creazione del modello geometrico di una volta a crociera
□ Cross vault parameters
o Definizione della geometria generale:
 L1=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 1 della volta;
```
 L2=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 2 della volta;
```
```
 f=freccia tra piano di imposta e intradosso della sezione di chiave della volta;
```
```
 t0=spessore della volta sulla sezione d’imposta;
```
```
 t1=spessore della volta sulla sezione di chiave;
```
o Deselezionare l’opzione Plan is rectangular per definire una geometria in pianta non rettango-
```
lare:
```
 L3=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 3 della volta;
```
 L4=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 4 della volta;
```
 L5=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso
```
sulla diagonale della volta;
```
o Lmax= lunghezza massima degli elementi utilizzata per la discretizzazione della volta a crociera
```
nel modello computazionale;
```
□ Lateral archs parameters
o Selezionare Lateral archs parameters per generare gli archi laterali:
```
 Wp=profondità degli archi ai lati della volta;
```
```
 Tp0=spessore degli archi ai lati della volta sul piano d’imposta;
```
```
 Tp1=spessore degli archi ai lati della volta sul piano di chiave;
```
 Selezionare il pulsante Archs are aligned to extrados se gli archi ai lati sono alliniati
```
all’estradosso della volta;
```
□ Piers
o Selezionare l’opzione Piers per generare i piedritti di appoggio:
```
 Hi=altezza dei piedritti;
```
```
 Ti=spessore dei piedritti;
```
□ Diagonal archs
o Selezionare Diagonal archs per generare gli archi diagonali:
```
 Wd=spessore degli archi diagonali;
```
```
 Td0=spessore degli archi diagonali sul piano di imposta;
```
```
 Td1=spessore degli archi diagonali sul piano di chiave;
```
 Selezionare il pulsante Archs are aligned to extrados se gli archi diagonali sono alli-
niati all’estradosso della volta.
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
36
□ Truss
o Selezionare l’opzione per generare elementi catena lungo ogni lato della volta
 Truss on each side of the vault.
Lo schema quotato della volta a crociera è mostrato in Figura 5.8.
5.1.2.3 Creazione di una volta a vela
Per generare una volta a vela occorre compilare i seguenti riquadri:
Figura 5.9 - Input parametrico delle caratteristiche geometriche di una volta a vela.
Figura 5.10 - Schermata di riferimento per la creazione del modello geometrico di una volta a vela
□ Domical vault parameters
o Definizione della geometria generale:
 L1=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 1 della volta;
```
```
 D1=proiezione dello spessore dei piedritti sul lato 1;
```
 L2=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 2 della volta;
```
 D2=proiezione dello spessore dei piedritti sul lato 2.
```
 f=freccia tra piano di imposta e intradosso della sezione di chiave della volta;
```
```
 t0=spessore della volta nella sezione d’imposta;
```
```
 t1=spessore della volta nella sezione di chiave;
```
o Lmax= lunghezza massima degli elementi utilizzata per la discretizzazione della volta a vela nel
```
modello computazionale;
```
□ Piers
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
37
o Selezionare l’opzione Piers per generare i piedritti di appoggio:
```
 Hi=altezza dei piedritti;
```
```
 Ti=spessore dei piedritti;
```
□ Truss
o Selezionare l’opzione per generare elementi catena lungo ogni lato della volta
 Truss on each side of the vault.
Lo schema quotato della volta a vela è mostrato in Figura 5.10.
5.1.2.4 Creazione di una volta a padiglione
Per generare una volta a padiglione occorre compilare i seguenti riquadri:
Figura 5.11 - Input parametrico delle caratteristiche geometriche di una volta a padiglione.
Figura 5.12 - Schermata di riferimento per la creazione del modello geometrico di una volta a padiglione
□ Cloister vault parameters
o Definizione della geometria generale:
 L1=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 1 della volta;
```
 L2=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 2 della volta;
```
```
 f=freccia tra piano di imposta e intradosso della sezione di chiave della volta;
```
```
 t0=spessore della volta sul piano di imposta;
```
```
 t1=spessore della volta sul piano di chiave;
```
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
38
o Deselezionare l’opzione Plan is rectangular per definire una geometria in pianta non rettango-
```
lare:
```
 L3=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 3 della volta;
```
 L4=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 4 della volta;
```
 L5=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso
sulla diagonale della volta.
o Lmax= lunghezza massima degli elementi utilizzata per la discretizzazione della volta a padi-
```
glione nel modello computazionale;
```
□ Base walls
o Selezionare l’opzione Piers per generare i piedritti di appoggio:
```
 Hi=altezza dei piedritti;
```
```
 Ti=spessore dei piedritti;
```
Lo schema quotato della volta a padiglione è mostrato in Figura 5.12.
5.1.2.5 Creazione di una volta a specchio
Per generare una volta a specchio occorre compilare i seguenti riquadri:
Figura 5.13 - Input parametrico delle caratteristiche geometriche di una volta a specchio.
Figura 5.14 - Schermata di riferimento per la creazione del modello geometrico di una volta a specchio
□ Cloister vault intersected with an horizontal plane parameters
o Definizione della geometria generale:
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
39
 L1=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 1 della volta;
```
 L2=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 2 della volta;
```
```
 f=freccia tra piano di imposta e intradosso della sezione di chiave della volta;
```
```
 t0=spessore della volta sul piano di imposta;
```
```
 t1=spessore della volta sul piano di chiave;
```
 dR=distanza in pianta tra il paramento interno di un lato di bordo della volta e l’intra-
dosso del punto di piegatura della copertura, della volta ribassata.
o Deselezionare il pulsante Plan is rectangular per definire una geometria in pianta non rettan-
```
golare:
```
 L3=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 3 della volta;
```
 L4=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso del
```
lato 4 della volta;
```
 L5=distanza, sul piano d’imposta della volta, misurata tra i paramenti d’intradosso
```
sulla diagonale della volta;
```
o Lmax= lunghezza massima degli elementi utilizzata per la discretizzazione dalla volta a specchio
```
nel modello computazionale;
```
□ Base walls
o Selezionare l’opzione Piers per generare i piedritti della volta:
```
 Hi=altezza dei piedritti;
```
```
 Ti=spessore dei piedritti;
```
Lo schema quotato della volta specchio è mostrato in Figura 5.14.
5.1.2.6 Creazione di una cupola
La cupola può essere schematizzata mediante le quattro parti mostrate in Figura 5.15:
```
 tamburo di base > Drum bottom;
```
```
 cupola > Dome;
```
```
 tamburo della lanterna > Drum top;
```
 cupola della lanterna > Dome top.
Drum top - Tamburo della
lanterna
Dome top - Cupola
della lanterna
Dome - Cupola
Drum bottom – Tamburo di base
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
40
Figura 5.15 – Parti costituenti una cupola
Per generare una cupola occorre compilare i seguenti riquadri, ciascuno corrispondenti alle parti in cui
essa viene schematizzata:
Figura 5.16 - Schermata di riferimento per la creazione del modello geometrico di una cupola
□ General parameters
o Definizione della geometria generale:
```
 R1=raggio del tamburo di base in direzione 1;
```
```
 R2=raggio del tamburo di base in direzione 2;
```
o Lmax= lunghezza massima degli elementi utilizzata per la discretizzazione della cupola nel mo-
```
dello computazionale;
```
□ Dome
o Caratteristiche geometriche della cupola:
 R3 Dir, per la selezione della direzione principale 1 o 2:
```
 Dir 1;
```
```
 Dir 2;
```
```
 R3=raggio in testa cupola;
```
```
 H2=altezza della cupola;
```
```
 t2=spessore sul piano d’imposta della cupola;
```
 t3=spessore in cima alla cupola in corrispondenza dell’attacco col tamburo della lan-
```
terna;
```
□ Drum bottom
o Selezionare l’opzione Drum bottom per definire la geometria del tamburo di base:
```
 H1=altezza del tamburo di base;
```
```
 t0=spessore del tamburo di base al piede;
```
```
 t1=spessore del tamburo di base in testa;
```
o Selezionare l'opzione Windows in drum bottom per definire la geometria di eventuali aperture
nel tamburo di base:
```
 Nb=numero di aperture;
```
```
 α=angolazione dell’apertura;
```
```
 Hb1=altezza della finestra dal piede del tamburo di base;
```
```
 Hb2=altezza in testa della finestra dal piede del tamburo di base;
```
□ Drum top
o Selezionare l'opzione Drum top per definire la geometria del tamburo della lanterna:
```
 H3=altezza del tamburo della lanterna;
```
```
 t4=spessore del tamburo della lanterna al piede;
```
```
 t5=spessore del tamburo della lanterna in testa;
```
Manuale Utente HISTRA HISTRA ARCHES AND VAULTS: PROCEDURA GUIDATA DI INPUT
41
o Selezionare l'opzione Windows in drum top per definire la geometria di eventuali aperture nel
tamburo della lanterna:
```
 Nt=numero di aperture;
```
```
 β=angolazione dell’apertura;
```
```
 Ht1=altezza della finestra dal piede del tamburo della lanterna;
```
```
 Ht2=altezza in testa della finestra dal piede del tamburo della lanterna;
```
□ Dome top
o Selezionare l'opzione Dome top per definire la geometria della cupola della lanterna:
```
 H4=freccia della cupola della lanterna;
```
```
 t6=spessore al piano d’imposta della cupola della lanterna;
```
 t7=spessore al piano in chiave della cupola della lanterna.
Lo schema geometrico quotato del modello cupola è mostrato in Figura 5.16.
5.1.3 Creazione di un modello tramite .dxf
Nel caso di HISTRA Arches and Vaults, c’è anche la possibilità che si importi un modello geometrico,
modellato all’esterno tramite software CAD in formato .dxf.
A tale opzione si accede cliccando, dalla finestra “HISTRA Wizard” il tasto DXF.
Elemento facciata
Quando si seleziona questa opzione viene generato un nuovo modello e consentita l'importazione della
mesh da file .dxf. In questo caso la mesh predisposta in ambiente CAD sarà quella effettiva, e sarà valida,
senza limitazioni di dimensioni nè numero di elementi, per una parete piana. Questo implica che tutti gli
elementi giaceranno sullo stesso piano, ma il modello di calcolo sarà a tutti gli effetti tridimensionale e
consentirà analisi nel piano e fuori piano.
Bisogna prestare attenzione alla creazione in ambiente CAD del modello: in particolare ogni songolo
```
elemento va modellato con un elemento noto come “3Dface” in ambiente CAD (o “Faccia3D” in italiano).
```
```
Tali elementi sono elementi piani a tre o quattro nodi (una volta importati saranno letti rispettivamente
```
```
come vertex o quad). Bisogna prestare attenzione che ogni elemento 3Dface abiamo i nodi tutti giacenti
```
```
nello stesso piano e che tra un elemento e quello adiacente ci sia coincidenza nodale (o che almeno la
```
```
distanza tra i due nodi sia sotto una certa tolleranza che può essere gestita dall’utente). L’utente può
```
```
gestire il valore di tolleranza accettato mediante il Menù Model  Advanced options (Paragrafo 8.2.2).
```
E’ possibile anche importare come Polyface Mesh che consente di associare alla mesh elementi di tipo
Quad/Vertex, o di tipo Solid.
Manuale Utente HiStrA HISTRA FOR BRIDGES: PROCEDURA GUIDATA DI INPUT
6 HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
HISTRA BRIDGES fornisce all’utente un valido supporto per l’impostazione generale del modello di pro-
getto, attraverso un'interfaccia semplice ed intuitiva. Con la procedura guidata di “Wizard” è possibile
inizializzare facilmente un nuovo modello ed impostarne tutte le caratteristiche, mediante un semplice
input parametrico.
Figura 6.1 – Finestra di avvio programma o crea nuovo modello. Selezionare la tipologia di ponte Rail Bridge o Road
Bridge,
```
All'avvio di HISTRA BRIDGES (o creando un nuovo modello da menu File > New), si apre una finestra in
```
cui è possibile selezionare la tipologia di ponte che si vuole modellare: Rail BRIDGES avvia la procedura
guidata di input per i ponti ferroviari, mentre Road Bridge avvia quella per i ponti stradali. La procedura
guidata di input consente passo-passo di creare e definire:
```
 Modello geometrico del ponte (Geometry) mediante l’input dei parametri geometrici degli elementi che
```
```
lo compongono (campate, spalle, pile);
```
```
 Materiali (Material);
```
```
 Carichi (Loads);
```
```
 Schemi di carico corrispondenti alle azioni variabili di traffico (Schema)
```
```
 Analisi (Analysis).
```
Il software dispone di librerie avanzate per la gestione dei carichi e delle combinazioni, allineate alle
normative vigenti, sia per ponti stradali che ferroviari.
L'input dei dati avviene per successivi step e la navigazione delle finestre di input viene guidata auto-
maticamente.
```
La finestra di Wizard è composta come segue. In alto il menu dei bottoni relativi a Geometria (Geometry),
```
```
Materiali (Material), Carichi (Loads), Schemi di carico (Schema) e Analisi (Analysis). Ciascuno consente
```
di accedere alla specifica sezione.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
44
```
Per poter navigare attraverso la finestra di Wizard ed accedere alle varie sezioni (Geometria, Materiali,
```
```
Carichi, Schemi di carico e Analisi) è possibile muoversi con i pulsanti Next e Back, posti in basso a destra.
```
```
Il pulsante Cancel consente di uscire dalla procedura guidata di input (in tal caso nessuno dei dati inseriti
```
```
verrà salvato) e di tornare nell'ambiente principale del programma.
```
Il pulsante OK invece consente di confermare i dati inseriti ed avvia la generazione automatica del mo-
dello geometrico e computazionale del ponte, visualizzato sulla finestra principale del programma.
Con Main menu è possibile tornare sulla finestra di avvio di HISTRA BRIDGES.
Figura 6.2 - Schermata generale Wizard di HISTRA BRIDGES, per l'input geometrico di un ponte ferroviario – Rail
Bridge
Figura 6.3 - Schermata generale Wizard di HISTRA BRIDGES, per l'input geometrico di un ponte stradale – Road
Bridge
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
45
6.1 DEFINIZIONE DELLA GEOMETRIA DEL PONTE
La definizione della Geometria si articola attraverso l'input delle caratteristiche geometriche di tutte le
parti e/o degli elementi che lo costituiscono.
L’ambiente di definizione della Geometria è costituito da una struttura multi-schede. Queste ultime si
attivano via via, per successivi passi di input, cliccando sul bottone Next, posto in basso a destra.
Questa procedura consente di usufruire di particolari controlli automatici di coerenza e congruenza dei
dati geometrici inseriti: dopo avere effettuato l'input di tutti i dati di una specifica scheda, cliccando sul
bottone Next, vengono attivate le successive schede di input da compilare, in funzione dei dati prece-
dentemente inseriti.
Se la label di una scheda viene evidenziata in rosso, il programma segnala una mancata coerenza di alcuni
dati geometrici precedentemente inseriti e che devono quindi essere editati. Accedendo alla scheda i campi
```
corrispondenti (errati o non coerenti) vengono a loro volta evidenziati, in modo da poterli individuare im-
```
mediatamente ed editare.
Accedendo all’ambiente "Geometry" sono visualizzabili solo cinque schede di input, e nello specifico:
```
"General" (con le caratteristiche generali della carreggiata), "Left abutment:AB1" (spalla sinistra) e
```
```
"Span1:S1" (Campata 1); "Right abutment:AB2" (spalla destra); “Backfill” (Stratigrafia) (v. Figura 6.4).
```
Da questo ambiente in particolare è possibile caratterizzare:
 Sezione trasversale, con definizione della con definizione dell’ampiezza di corsie, banchine, parapetti
```
o eventuali spazi di separazione tra le corsie, tenendo conto della presenza di carico viaggiante (stradale
```
```
o ferroviario) e dell’eventuale pendenza longitudinale del ponte ed inclinazione in pianta dell’asse lon-
```
gitudinale.
 Pile e spalle, a sezione costante o variabile, caratterizzate da semplici parametri geometrici della se-
zione trasversale, l’altezza, l’allineamento rispetto alla campata del ponte, il materiale e le caratteristi-
che della fondazione, tenendo conto anche dell’interazione terreno-struttura delle terre ai fianchi di
```
spalle e pile (spinta attiva e passiva);
```
```
 Campate, assegnando tutti i parametri che caratterizzano la geometria della volta (luce, freccia, sezione, etc.);
```
 Profilo stratigrafico, anche con altezza variabile, dei rinfianchi e del riempimento gravante sulle volte
del ponte, definendone la geometria e caratterizzandone il materiale.
L’anteprima della sezione trasversale del ponte è disponibile nella area grafica in fondo alla finestra, da
cui è possibile visualizzare, step by step, il modello che si sta creando, mentre con i tasti "+" e "-" in alto
```
a destra consentono di aggiungere o eliminare una campata (Span) (prima o dopo quella in selezione).
```
```
Aggiungendo una o più campate, le pile corrispondenti vengono aggiunte automaticamente (Pile) (v.
```
```
Figura 6.5).
```
Se nessuna scheda "Span" è stata selezionata, viene rilasciato un messaggio, che suggerisce di selezio-
nare una scheda "Span", per poter aggiungere gli elementi desiderati.
```
Per eliminare una campata (Span) e la relativa pila, basta selezionare la scheda corrispondente (Span) e
```
cliccare sul pulsante "-".
Man mano che geometria viene definita, la sezione longitudinale del ponte viene rappresentata nello
```
spazio sottostante. (v. Figura 6.6).
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
46
```
Figura 6.4 - Etichette delle schede di input e pulsanti "+" e "-" (aggiungi/elimina schede)
```
```
Figura 6.5 - Aggiungi una campata al ponte (add span before o add span after)
```
Figura 6.6 – Anteprima della sezione longitudinale di un ponte multi-campata
```
6.1.1 Caratteristiche generali (General)
```
La prima scheda “General” consente di assegnare tutte le caratteristiche generali che riguardano la geome-
tria del ponte e che condizionano i criteri di generazione della mesh, come meglio specificato al capitolo
introduttivo. Nella tabella Definition of the BRIDGES cross-section vengono definite le proprietà geome-
triche della sezione trasversale del ponte e della carreggiata, ovvero la composizione della sede stradale
```
(o ferroviaria) con le dimensioni di ciascuna porzione che la costituisce: ad esempio parapetti, banchine,
```
corsie o binari, spazi di separazione tra le corsie o margini, etc... E’ altresì possibile tenere conto della
presenza e posizione di carichi viaggianti, attivando le voci corrispondenti: “Train Load” per ponti ferro-
```
viari, o assegnando lo schema di carico per i ponti stradali (Schemi da a 5… secondo la definizione di cui
```
```
al par. 5.1.3.3.5 e Figura 5.1.2 delle NTC2018).
```
```
In funzione delle dimensioni delle singole porzioni (corsie, margini, banchine, etc.) di cui si compone la
```
sezione trasversale, la larghezza del ponte risulta automaticamente definita.
Il software propone di default una configurazione articolata secondo i criteri di normativa. Per i ponti
ferroviari, ad esempio, due banchine laterali e tre corsie convenzionali, separate tra loro da uno spazio
```
per ponti stradali, oppure unico binario, due margini laterali e parapetti per ponti ferroviari (v. Figura
```
```
6.8); per ponti stradali viene proposta di default la configurazione con due corsie e area rimanente. Cia-
```
```
scuna corsia, di larghezza pari a tre metri (cfr. par. 5.1.3.3.5 delle NTC2018), è composta da tre porzioni. In
```
Figura 6.11 un esempio di definizione della sezione trasversale del ponte, costituito da due corsie carra-
bili e area
Per inserire una nuova riga alla tabella Definition of the BRIDGES cross-section, portarsi su una riga della
```
tabella e cliccare sul tasto "+" (aggiungi riga). La riga sarà aggiunta dopo quella selezionata.
```
```
Per eliminare una riga esistente, invece, basta selezionare la riga e cliccare sul tasto "-" (elimina riga).
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
47
```
E' possibile anche spostare ciascuna riga (traslando ciascuna parte della sezione trasversale del ponte)
```
all’interno della tabella, utilizzando i pulsanti "su" e "giù".
Figura 6.7 – Scheda General – assegnazione delle caratteristiche generali
```
 Max mesh length > massima lunghezza degli elementi computazionali (quad) nella direzione trasversale
```
e longitudinale del ponte. Questo parametro concorre ad individuare il criterio di discretizzazione in
```
mesh degli elementi geometrici, per la creazione del modello computazionale;
```
 Inclination angle of the abutments/piers > angolo di inclinazione della spalla o della pila, nel piano xy,
```
rispetto all’asse longitudinale del ponte;
```
```
 Slope of the bridge > pendenza (rapportata a 100) della sezione longitudinale del ponte. Ad esempio 0.01
```
```
esprime una pendenza del 1%;
```
 Width of the bridge at top section of the piles > se il ceck “custom” è attivo è possibile assegnare e per-
```
sonalizzare la larghezza trasversale del ponte in corrispondenza della sezione in testa delle pile;
```
 Width of the BRIDGES at impost level of the arches > larghezza del ponte alla quota dell’imposta delle
```
volte (questo campo non è editabile, ma il valore contenuto si aggiorna automaticamente, in funzione
```
```
delle larghezze di ciascuna porzione di carreggiata, assegnate nella soprastante tabella Roadway);
```
```
6.1.1.1 Definizione della sezione trasversale per ponti ferroviari (Rail BRIDGES)
```
Per i ponti ferroviari, la definizione della sezione trasversale del ponte viene effettuata inserendo i se-
guenti parametri:
Figura 6.8 – Esempio di definizione della sezione trasversale, per ponti ferroviari
```
 Name > nome della parte o porzione di carreggiata (Parapetto, Banchina, Corsia o Binario, Margine, etc.);
```
```
 Decription > Descrizione della parte o porzione sezione trasversale;
```
```
 Lane Width > Larghezza della corsia/binario o in generale della porzione della sezione trasversale;
```
```
 Wall height > Altezza dell’eventuale parapetto;
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
48
 Wall material > Materiale di cui è composto il parapetto, se definito
 Train Load > Presenza di carico viaggiante. Se selezionato consente di considerare la presenza carichi
viaggianti. La presenza del carico viaggiante viene rappresentata anche nella sottostante area grafica,
nella anteprima della sezione trasversale del ponte. Ad esempio viene rappresentato nella sezione una
```
immagine del convoglio o del veicolo (v. Figura 6.2).
```
Inoltre è possibile assegnare eventuali diverse larghezze del ponte, in corrispondenza della sezione in
```
testa alle spalle (v. figura Figura 6.9 – B) e personalizzare le proprietà di natura computazionale del mo-
```
dello di calcolo:
A - Larghezza trasversale del ponte costante B - Larghezza trasversale del ponte varia-
bile, con allargamento in corrispondenza
della sezione di appoggio delle spalle.
Figura 6.9 – Caratterizzazione della larghezza trasversale del ponte
Per i ponti ferroviari è possibile scegliere dal combobox 'Apply as' la distribuzione di carico equivalente
```
all'azione da traffico ferroviario secondo una distribuzione di carico di linea (line load) ovvero secondo
```
```
una distribuzione di carichi concentrati (vehicle load) che saranno applicati in accordo agli schemi di
```
```
carico definiti (cfr § 6.4). Inoltre è possibile selezionare dal combobox 'Type of load' il relativo carico
```
presente in archivio in accordo al tipo di distribuzione di carico selezionato, rendendo personalizzabile
la definizione degli schemi di carico.
Figura 6.10 - Scheda General – assegnazione del tipo di carico
```
6.1.1.2 Definizione della sezione trasversale per ponti stradali (Road BRIDGES)
```
La definizione della sezione trasversale dei ponti stradali richiede la suddivisione del ponte in
corsie convenzionali. Le azioni da traffico stradale possono essere rappresentate mediante un set di ca-
richi concentrati applicati in corrispondenza degli assali del veicolo secondo i modelli di carico da traf-
```
fico suggeriti dalle norme (vedi Figura 6.55, Figura 6.56). Tali azioni possono essere definite come Vehicle
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
49
```
Loads; i punti di applicazione delle forze concentrate sul piano carrabile saranno individuati attraverso
```
```
la definizione degli schemi di carico (vedi par.6.4).
```
Ciascuna corsia convenzionale può essere modellata discretizzando la stessa in una o più componenti
della sezione al fine di condizionare la generazione della mesh. In tal senso, in funzione della discretiz-
zazione della corsia convenzionale, l’utente dovrà applicare, nella componente centrale il carico Vehicle
```
Load (Qik, vd. NTC18), mentre il carico qik uniformemente distribuito su tutte le componenti.
```
Per i ponti stradali, la definizione della sezione trasversale del ponte viene effettuata inserendo i se-
guenti parametri:
Figura 6.11 – Esempio di definizione della sezione trasversale, per ponti stradali
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
50
```
Figura 6.12 – Schema e numerazione corsie secondo le NTC2018 (cfr- figura 5.1.1 par. 5.1.3.3.2)
```
```
 Name > nome della parte o porzione di carreggiata (corsia o porzione di corsia, parte rimanente, etc.);
```
```
 Decription > Descrizione della parte o porzione sezione trasversale;
```
 Lane Width > Larghezza della porzione di sezione trasversale. la larghezza della corsia dovrà essere di-
scretizzata in un numero dispari di porzioni in modo da identificare una porzione centrale a cui applicare
```
il carico tandem Qik oltre al carico uniformemente distribuito qik (figura. 5.1.2 delle NTC2018);
```
```
 Wall height > Altezza dell’eventuale parapetto;
```
```
 Wall material > Materiale di cui è composto il parapetto, se definito;
```
 Schema 1, Schema 2, … Schema 5 > Schemi di carico di cui al par. 5.1.3.3.5 delle NTC2018. La presenza del
carico mobile corrispondente a un determinato schema viene assegnata selezionando la voce Load ap-
```
plied (per gli schemi di carico da 2 a 5) oppure, per lo schema 1, assegnando il carico corrispondente -
```
```
Lane1, Lane2, etc… (cfr. figura 5.1.2 delle NTC2018).
```
La presenza del carico viaggiante viene rappresentata anche nella sottostante area grafica, con l’ante-
prima della sezione trasversale del ponte.
Nel groupbox Group of action è possibile assegnare il Gruppo di azioni secondo la definizione della
Tabella 5.1.IV delle NTC2018. Selezionando la voce si generano tutti gli schemi associati al gruppo di
```
azioni corrispondente. Ogni gruppo di azioni di carico ammette più schemi di carico (cfr. Schema § 6.4).
```
Si veda tabella 5.1.IV di normativa sotto riportata. In funzione del gruppo di azioni considerato, i carichi
```
vengono assunti con il loro valore caratteristico o frequente. (v. Figura 6.15).
```
Figura 6.13 – Assegnazione dei Gruppi di azioni secondo le NTC2018, Tabella 5.1.IV.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
51
```
Figura 6.14 – Disposizione dei carichi mobili - Schemi di carico 1 – 5 (dimensioni in m) – Figura 5.1.2 delle NTC2018
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
52
Figura 6.15 – Gruppi di azioni dovute al traffico- Tabella 5.1.IV delle NTC2018.
```
6.1.2 Definizione geometria spalle (Left/Right abutment)
```
```
Accedendo alle schede Left abutment (AB1) e Right abutment (AB2) vengono assegnate tutte le caratte-
```
```
ristiche geometriche delle spalle del ponte (sinistra e destra).
```
Durante l’input dei dati geometrici, nella rappresentazione grafica in basso viene raffigurata la sezione
```
trasversale del ponte ed individuati interattivamente i parametri geometrici che si stanno editando (v.
```
```
Figura 6.16).
```
```
Per definire i parametri geometrici di ciascun elemento del ponte (spalla, pila, campata) è sufficiente
```
selezionare l’elemento nell’area grafica e accedendo automaticamente alla scheda di input.
Figura 6.16 - Rappresentazione grafica della sezione trasversale del ponte e individuazione interattiva dei parame-
tri geometrici della spalla
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
53
```
I parametri geometrici richiesti per l’input delle spalle sono i seguenti (Figura 6.19):
```
□ Abutment parameters:
```
o Height, H = altezza della spalla, misurata dall'estradosso della fondazione;
```
o w1, w3 = allargamenti della sezione trasversale alla base della spalla, misurata lungo la dire-
```
zione trasversale del ponte. Questi parametri possono assumere valore nullo;
```
o w2 = larghezza della sezione trasversale in testa della spalla, misurata nella direzione trasver-
sale rispetto allo sviluppo del ponte. Questo dato deve essere sempre maggiore o al massimo
```
uguale alla larghezza del ponte (Width of the BRIDGES, assegnato nella scheda General). Se w2
```
```
risulta inferiore a Wbridge, la cella (come anche il nome della scheda) viene evidenziata in rosso.
```
o Width, W = larghezza della sezione trasversale alla base della spalla, misurata lungo la direzione
trasversale del ponte. Questo parametro non è editabile, ma assume il valore ottenuto dalla
```
somma di w1, w2 e w3;
```
o b1, b3 = allargamenti della sezione trasversale alla base della spalla, misurata lungo la direzione
```
longitudinale del ponte. Questi parametri possono assumere valore nullo;
```
o b2 = larghezza della sezione trasversale in testa della spalla, misurata nella direzione longitu-
```
dinale rispetto allo sviluppo del ponte;
```
o Base, B = larghezza della sezione trasversale alla base della spalla, misurata lungo la direzione
longitudinale del ponte. Questo parametro non è editabile, ma assume il valore ottenuto dalla
```
somma di b1, b2 e b3;
```
o Alignment = indica l'allineamento in direzione trasversale della sezione trasversale della cam-
pata del ponte, rispetto alla sezione di testa della spalla. L'allineamento può essere centrale, in
```
alto o in basso ( Center, Top, Bottom);
```
```
o Abutment Material = indica il materiale di cui è costituita la spalla del ponte;
```
```
o Add lateral restraint (Left/Right) = se selezionato, aggiunge un vincolo laterale offerto dalla
```
```
presenza di terreno a monte (o a valle) della spalla;
```
```
o Height, Hsp = altezza del terreno spingente lato monte Hsp1 o lato valle Hsp2 (questa deve es-
```
sere maggiore di zero e non maggiore dell’altezza totale del ponte – data dalla somma della
```
altezza della spalla più la altezza del ponte);
```
o Geotechnical material = indica il materiale geotecnico che caratterizza il terreno spingente. Può
essere diverso a monte e a valle della spalla.
Figura 6.17 - Rappresentazione grafica della sezione trasversale del ponte e caratterizzazione della altezza spinta
terreno a monte e a valle
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
54
□ Foundation parameters:
```
o Height, Hf = altezza della fondazione della spalla;
```
o b1f, b3f = allargamenti della fondazione, rispetto alla sezione trasversale di base della spalla,
```
misurati nella direzione longitudinale di sviluppo del ponte;
```
o w1f, w3f = allargamenti della fondazione, rispetto alla sezione trasversale di base della spalla,
```
misurati nella direzione trasversale di sviluppo del ponte;
```
```
o Foundation material = indica il materiale di cui è costituita la fondazione della spalla;
```
```
Figura 6.18 - Left / Right abutment - input delle proprietà geometriche della Spalla (Abutment parameters)
```
```
Figura 6.19 - Left / Right abutment - input delle proprietà geometriche della fondazione della Spalla (Foundation
```
```
parameters)
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
55
```
6.1.3 Definizione geometria campate (Span N)
```
```
Nella scheda Span 1 , 2, … N (S1, S2, … SN) vengono assegnate tutte le caratteristiche geometriche della
```
campata selezionata, secondo quanto riportato in Figura 6.20:
```
Figura 6.20 - Scheda Span ‘N’ - input delle proprietà geometriche della campata n-esima del ponte (Vault parame-
```
```
ters).
```
□ Vault parameters:
```
o Span lenght, L = luce della campata (ovvero della volta), pari alla distanza tra il paramento in-
```
```
terno della pila a sinistra (o spalla sinistra) e quello della pila a destra (o spalla destra), misurata
```
```
in corrispondenza della sezione di imposta della volta;
```
o Width, W = larghezza della volta. Questo parametro coincide con la larghezza del ponte in dire-
```
zione trasversale e non è editabile (questo parametro dipende dalla geometria della sezione
```
```
trasversale precedentemente definita);
```
```
o f = freccia dell’arco, sezione retta della volta;
```
```
o Thickness Tt = spessore della sezione retta della volta sul piano d’imposta;
```
```
o Thickness Tb = spessore della sezione retta della volta sulla sezione di chiave;
```
o Thickness Law = legge di variazione dello spessore della sezione retta della volta, Costante o
Lineare. Se Costante, viene richiesto un unico parametro Tt = Tb, mentre se Lineare, vengono
```
richiesti i due valori Tt e Tb;
```
o Angle, = angolo di inclinazione della sezione di imposta della volta, rispetto alla sezione di
```
testa della spalla (o della pila); se positivo determinerà la generazione dell’elemento ‘pulvino’;
```
o s1 = distanza tra l’intradosso della volta sulla sezione d’imposta di sinistra e il paramento in-
```
terno della spalla (o pila) alla sua sinistra;
```
o s2 = distanza tra l’intradosso della volta sulla sezione d’imposta di destra e il paramento interno
```
della spalla (o pila) alla sua destra;
```
```
o Span Material = indica il materiale della campata del ponte;
```
o Piercap Material = indica il materiale del pulvino della pila o della spalla.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
56
L'andamento della volta è di tipo ellittico, con centro posto nella mezzeria della campata, ed eventualmente
ribassato rispetto alla quota di imposta di una quantità. I raggi orizzontale e verticale dell'ellisse, rispettiva-
```
mente Rx e Ry rispettano le seguenti condizioni (v. Figura 6.21):
```
2x
y
LR
R f

  
Figura 6.21 - Schema geometrico della sezione della volta.
6.1.4 Caratteristiche geometriche della pila
Nella scheda Pile N. è possibile assegnare tutte le caratteristiche geometriche della pila n-esima del
ponte. Detta scheda viene aggiunta automaticamente nel momento in cui si decide di aggiungere una
nuova campata al ponte
In particolare viene richiesto, secondo quanto riportato in Figura 6.23:
□ Abutment parameters:
```
o Height, H = altezza della pila, misurata dall'estradosso della fondazione;
```
o w1, w3 = allargamenti della sezione trasversale alla base della pila, misurata lungo la direzione
```
trasversale del ponte. Questi parametri possono assumere valore nullo;
```
o w2 = larghezza della sezione trasversale in testa della pila, misurata nella direzione trasversale
```
rispetto allo sviluppo del ponte;
```
o Width, W = larghezza della sezione trasversale alla base della pila, misurata lungo la direzione
trasversale del ponte. Questo parametro non è editabile, ma assume il valore ottenuto dalla
```
somma di w1, w2 e w3;
```
o b1, b3 = allargamenti della sezione trasversale alla base della pila, misurata lungo la direzione
```
longitudinale del ponte. Questi parametri possono assumere valore nullo;
```
o b2 = larghezza della sezione trasversale in testa della pila, misurata nella direzione longitudi-
```
nale rispetto allo sviluppo del ponte;
```
o Base, B = larghezza della sezione trasversale alla base della pila, misurata lungo la direzione
longitudinale del ponte. Questo parametro non è editabile, ma assume il valore ottenuto dalla
```
somma di b1, b2 e b3;
```
o Alignment = indica l'allineamento in direzione trasversale della sezione trasversale delle cam-
```
pate del ponte, che insistono sulla pila, rispetto alla sezione in testa alla pila stessa (L'allinea-
```
```
mento può essere centrale, in alto o in basso);
```
Rx
Ry
f

L
C

Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
57
```
o Pier Material = indica il materiale della pila del ponte;
```
```
o Add lateral restraint (Left/Right) = se selezionato, aggiunge un vincolo laterale offerto dalla
```
```
presenza di terreno a monte (o a valle) della spalla;
```
o Height, Hsp1, Hsp2 = altezza del terreno spingente lato monte e valle della pila.
o Geotechnical material = indica il materiale geotecnico che caratterizza il terreno spingente. Può
essere diverso a monte e a valle della pila.
□ Foundation parameters:
```
o Height, Hf = altezza della fondazione della pila;
```
o b1f, b3f = allargamenti della fondazione, rispetto alla sezione trasversale di base della pila, mi-
```
surati nella direzione longitudinale di sviluppo del ponte;
```
o w1f = allargamento della fondazione, rispetto alla sezione trasversale di base della pila, misurati
```
nella direzione trasversale di sviluppo del ponte;
```
```
o Foundation Material = selezionare e assegnare il materiale della fondazione della pila;
```
```
o Type of restraint - Rigid / Elastic = definisce il tipo di vincolo alla base (rigido o elastico);
```
o kz Winkler = costante di winkler del terreno
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
58
Figura 6.22 - Pile N - input delle proprietà geometriche della pila.
Figura 6.23 - Pile N - input delle proprietà geometriche della fondazione della pila e vista trasversale del ponte.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
59
6.1.5 Backfill
Nella scheda Backfill è possibile definire le caratteristiche del profilo stratigrafico del riempimento gra-
vante sulle volte. E’ possibile ad esempio caratterizzare gli strati di rinfianchi, riempimento, ballast e
definire un profilo stratigrafico con andamento costante o variabile, lungo lo sviluppo longitudinale del
manufatto.
Se il profilo stratigrafico è costante, lungo tutto lo sviluppo longitudinale del ponte, dovranno essere
assegnate nella riga corrispondente alla Xposition 0 le corrispondenti altezze dei vari strati H1, H2, H3.
Assegnare altezza nulla per annullare lo strato.
L’opzione "Variable Stratigraphy" se selezionata consente di definire un profilo stratigrafico variabile.
```
Le altezze H1, H2, H3 di ciascuno strato devono essere assegnate per ogni posizione (X Position) o ordi-
```
nata.
```
Le ordinate (X position) automaticamente individuate coincidono con le sezioni significative del ponte,
```
ovvero con la sezione in corrispondenza dell’estremità del ponte, ovvero delle spalle, ed in corrispon-
```
denza del centro di ciascuna campata e del centro di ciascuna pila. Assegnare una altezza (ad esempio
```
```
H1, H2, H3) dei vari strati di riempimento (Backfill Layer 1, 2, 3).
```
Un’altezza variabile lungo lo sviluppo longitudinale del ponte consente anche di definire una livelletta
del piano superiore del manufatto.
Figura 6.24 - Scheda Backfill - input delle proprietà del profilo stratigrafico di rinfianchi e riempimento.
Nelle schede corrispondenti ai Backfill Layer occorre definire e caratterizzare il materiale di riempi-
```
mento, si riferiscono rispettivamente agli strati di altezza H1, H2 ed H3 sopra definiti (v. Figura 6.25).
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
60
```
Figura 6.25- Scheda Backfill – seleziona materiale riempimento rinfianchi (Backfill).
```
Se la voce “Generate computational elements” è attiva, il riempimento viene modellato mediante ele-
```
menti computazionali (quad) e non trattato come carico esplicito.
```
6.2 DEFINIZIONE DEI MATERIALI
La sezione Material consente di accedere alla finestra di definizione dei Materiali. Dal menu a tendina
sulla sinistra è possibile selezionare il tipo di materiale. Sono disponibili le seguenti tipologie:
```
□ Masonry materials: avvia la finestra dei materiali di tipo muratura;
```
```
□ Elastic Materials: avvia la finestra del materiale elastico;
```
```
□ Steel materials: avvia la finestra dei materiali di tipo acciaio;
```
```
Fiber Materials: avvia la finestra dei materiali di tipo fibre;
```
□ Geotecnical Materials: avvia la finestra delle proprietà meccaniche del terreno. Quest’ultimo presente
solo in HISTRA BRIDGES.
Figura 6.26 – Menu selezione Tipologia Materiali
6.2.1 Material > Masonry materials
La finestra di definizione del materiale si compone di due sezioni, in cui vengono riportati: a sinistra la
lista dei materiali definiti e a destra le proprietà di ciascun materiale selezionato dalla lista.
I parametri di definizione del materiale sono:
```
□ Name: definisce il nome associato al materiale;
```
```
□ Description: consente di associare una descrizione al materiale selezionato;
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
61
□ Specific weigth W: consente di specificare il peso specifico della muratura, secondo le unità di misura
selezionate nell’apposito menu a tendina.
```
Figura 6.27 – Schermata per la definizione di un materiale muratura (modalità semplificata).
```
E’ possibile definire le caratteristiche meccaniche della muratura secondo due modalità:
```
□ Simple mode: modalità semplificata;
```
```
□ Advanced mode: modalità avanzata;
```
Tipologia materiale
Lista dei materiali definiti
Modifica delle caratteristiche
meccaniche elemento selezio-
nato in modalità semplificata
```
(simple mode)
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
62
6.2.1.1 Caratterizzazione del materiale muratura in modalità semplificata
In modalità semplificata vengono richiesti i seguenti dati:
```
□ Masonry typology: l’utente può scegliere il tipo di muratura (muratura in pietrame disordinata, etc…),
```
selezionando la relativa voce dal menu a tendina. Tale scelta consentirà all’utente di attribuire rapida-
```
mente i valori minimi delle caratteristiche meccaniche (modulo di elasticità normale o di Young E, mo-
```
```
dulo di elasticità tangenziale G, etc…), consigliate dalla normativa vigente (cfr tab. C8.5.I Circolare n.7 del
```
```
21/01/2019, se si seleziona NTC2018, e tab. C8.A.2.1 Circolare n.617, 09/02/2019 se si seleziona NTC2008).
```
La scelta della tipologia muraria risulta decisiva ai fini della possibilità di applicare i coefficienti corret-
tivi previsti dalla normativa in presenza di particolari caratteristiche della muratura, o di eventuali in-
terventi di miglioramento delle caratteristiche su di essa applicati.
□ Description: sintetica descrizione della tipologia materiale muratura.
```
□ Elastic properties (E, G) e Strength properties: selezionare una delle tre voci: Min / Average / Max Va-
```
```
lues. Cliccando sul bottone corrispondente (minimo, medio, massimo) viene modificato/aggiornato il
```
```
valore caratteristico (minimo, medio, massimo) delle proprietà meccaniche del materiale, rispettiva-
```
```
mente di rigidezza e di resistenza (tab. C8.5.I Circolare n.7 del 21/01/2019 per NTC2018 e tab. C8A.2.1 Cir-
```
```
colare 2 febbraio 2009 n. 617 per NTC2008).
```
```
□ Knoulege level (livello di conoscenza) LC: LC1, LC2, LC3. Rappresenta il grado di conoscenza della strut-
```
tura portante dell’edificio, ed è una proprietà comune a tutte le normative. La scelta del livello di cono-
scenza implica l’adozione del corrispondente fattore di confidenza FC : il minore livello di conoscenza
dell’edificio determina una riduzione della resistenza a compressione e della resistenza a taglio secondo
```
la seguente espressione: fm = fm,k / FC (Circolare n.7 del 21/01/2019).
```
Figura 6.28 – Materiale muratura: descrizione, livello di conoscenza e selezione valore caratteristico delle proprietà
meccaniche
```
□ Corrective coefficients of mechanical properties (Circolare n.7 del 21/01/2019): Il valore di base, o ca-
```
ratteristico, precedentemente determinato deve essere corretto, ai sensi della normativa adottata, ap-
plicando opportuni coefficienti correttivi. Questi ultimi dipendono dalle caratteristiche della muratura
```
(malta di buona qualità, giunti sottili, ricorsi o listature connessione trasversale, nucleo scadente e/o
```
```
ampio, iniezioni di miscele leganti, intonaco armato, diatoni artificiali). In assenza di particolari specifi-
```
che i valori delle proprietà meccaniche della muratura si attestano sui valori minimi previsti dalla tabelle
specifiche per la normativa adottata sulla base della tipologia muraria selezionata. È possibile editare
tali informazioni nel caso in cui si disponga di dati più precisi.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
63
Figura 6.29 – Materiale muratura: selezione coefficienti correttivi delle proprietà meccaniche.
□ Caratteristiche meccaniche del materiale muratura: In questa tabella sono visualizzate le caratteristi-
```
che meccaniche di calcolo principali (modulo di elasticità normale o di Young E, modulo di elasticità
```
```
tangenziale G, resistenza a compressione fm, resistenza a taglio0, peso specifico w). Di default questi
```
valori sono ottenuti a partire dai valori medi consigliati dalla normativa adottata per la tipologia di mu-
ratura selezionata, penalizzati per il corrispondente fattore di confidenza.
Figura 6.30 – Materiale muratura: caratteristiche meccaniche del materiale Valore di calcolo.
6.2.1.2 Caratterizzazione del materiale muratura in modalità avanzata
Il materiale muratura possiede delle peculiarità che distinguono il suo comportamento rispetto a tutti gli
```
altri materiali (calcestruzzo, acciaio etc…). Essa è infatti caratterizzata da comportamenti diversi, a se-
```
```
conda delle azioni che coinvolgono il pannello murario (cfr. manuale teorico). HISTRA è un codice di cal-
```
colo che simula in maniera precisa il comportamento non lineare di questo materiale e dispone di un
input specifico che consente di definire in maniera precisa il legame caratteristico del materiale mura-
tura per ciascun meccanismo considerato.
```
 Meccanismo di rottura flessionale (rocking mechanism)
```
Si definiscono le caratteristiche meccaniche di calcolo a trazione e a compressione, del materiale
muratura, con riferimento al meccanismo di rottura a flessione.
```
□ Behavior: tipo di comportamento Isotropic o Orthotropic (isotropo o ortotropo). Se Ortotropo, vengono
```
```
richieste le caratteristiche meccaniche per le due direzioni (Local direction1 e Local direction2)
```
□ Young’s modulus E: il modulo di elasticità E= caratterizzante il tratto elastico lineare iniziale del le-
game costitutivo del materiale.
□ Tensile costitutive Law e Compression costitutive Law: selezionare il tipo di legame costitutivo del
materiale lineare o non lineare rispettivamente a trazione e compressione:
```
 Elastic, legame costitutivo elastico lineare;
```
 Linear hardening, legame costitutivo di tipo elasto-plastico con incrudimento cine-
```
matico lineare e duttilità fissata;
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
64
 Linear softening, legame costitutivo di tipo elastico con softening lineare calibrato in
```
funzione dell’energia di frattura;
```
 Exponential softening, legame costitutivo di tipo elastico con softening non lineare
```
calibrato in funzione dell’energia di frattura (solo per legame costitutivo a trazione);
```
 Parabolic, legame costitutivo di tipo non lineare con legge parabolica, calibrato in fun-
```
zione dell’energia di frattura (solo per legame costitutivo a compressione).
```
Con riferimento al legame Linear hardening è possibile definire i seguenti parametri meccanici:
□ Tensile/Compressive strength σyt / σyc: massima tensione di calcolo a trazione/compressione sopporta-
bile dalla muratura.
□ Traction ratio, t / Compressive ratio, c : = E2 / E = rapporto tra il modulo di elasticità post-elastico E2 e
```
quello iniziale E a trazione o a compressione (parametro richiesto nel caso di legame costitutivo di tipo
```
```
elasto plastico con incrudimento cinematico lineare e duttilità fissata)
```
□ Tensile ductility ut / Compressive ductility uc: la duttilità a trazione o a compressione può essere
```
infinita (se non viene espresso un valore spuntando il check) o limitata. Se selezionato, è possibile inse-
```
rire il valore della duttilità in compressione e a trazione. Il valore indicato è espresso come rapporto tra
```
la deformazione ultima (a trazione o compressione) e la corrispettiva al limite elastico uy.
```
□ Unload tensile/compressive behavior: definisce il tipo di scarico nel legame isteretico con degrado. E’
```
possibile scegliere tra tre tipi di scarico: “Initial” se lo scarico è con rigidezza iniziale (=0 ), “Origin” se lo
```
```
scarico è orientato all’origine (=1), oppure “Mixed” (0<<1).
```
□ Unload tensile parameter,t / Unload compression parameterc : valore editabile solo se il compor-
tamento isteretico è di tipo mixed. Il valore deve essere compreso tra 0 e 1:=0 se lo scarico avviene con
rigidezza iniziale,=1 se lo scarico è orientato all’origine.
Nel caso di Legame costitutivo Elastico Lineare, viene richiesto solo il Young’s modulus E, il modulo di
elasticità E=
Con riferimento ai legami Linear softening, Exponential softening e Parabolic è possibile definire oltre
quelli sopra indicati i seguenti parametri meccanici:
```
□ Tensile/ Compressive strength σyt, σyc : massima tensione di calcolo a trazione (e a compressione) sop-
```
```
portabile dalla muratura;
```
□ Tensile / Compressive fracture energy, Gt, Gc: Energia di frattura a trazione o a compressione pari
```
all’area sottesa dalla curva scheletro (backbone curve) espressa in termini di tensione e ampiezza della
```
fessura.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
65
```
Figura 6.31 – a) Meccanismo di rottura a flessione di un pannello murario; a’) Attivazione del meccanismo di rocking sul ma-
```
cro-elemento a quattro nodi di HISTRA
```
A) Elastic – legame costitutivo elastico lineare
```
```
B1) Linear hardening - legame costitutivo a trazione di tipo
```
elasto-plastico con incrudimento cinematico lineare e dutti-
lità fissata
```
B2) Linear hardening - legame costitutivo a compressione di
```
tipo elasto-plastico con incrudimento cinematico lineare e
duttilità fissata
q
F
```
(a)
```
’
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
66
```
C) Linear softening - Legame costitutivo elastico con softe-
```
ning lineare calibrato in funzione dell’energia di frattura
```
D) Exponential softening - legame costitutivo elastico con sof-
```
tening non lineare calibrato in funzione dell’energia di frattura
```
E) Parabolic: legame costitutivo di tipo non lineare con legge
```
parabolica, calibrato in funzione dell’energia di frattura
```
Figura 6.32 - Meccanismo di rottura a flessione (Rocking mechanism) – Costitutive law
```
```
E : modulo di elasticità nor-
```
```
male;
```
σyt , σyc : resistenza a trazione e com-
```
pressione;
```
ut : deformazione ultima a tra-
```
zione;
```
uc : deformazione ultima a com-
```
pressione;
```
yt : deformazione al limite ela-
```
stico a trazione;
```
yc : deformazione al limite ela-
stico a compressione.
```
Eut = E -t (E- E0,t)
```
```
Euc = E -c (E- E0,c)
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
67
Figura 6.33 – Legame costitutivo elasto-plastico con incru-
dimento cinematico lineare e duttilità fissata
Figura 6.34 – Individuazione della energia di frattura nel caso di legame costitutivo elastico con softening lineare
```
 Meccanismo di rottura per fessurazione diagonale (shear mechanism)
```
Vengono specificate le caratteristiche meccaniche di calcolo del materiale muratura:
□ Constitutive law: è possibile definisce il tipo di legame costitutivo selezionando:
```
 Elastic: elastico lineare;
```
 Elasto-Plastic: elastico infinitamente plastico
```
 Elasto-Plastic and ductility-fixed: elastico-plastico con duttilità fissata;
```
```
 Elasto-Plastic and linear-softening: elasto-plastico con softening lineare;
```
```
□ Yelding domain (Mohr-Coulomb, Turnsek Cacovic ): i due criteri Mohr-Coulomb e Turnsek Cacovic sono
```
identici, eccezion fatta per la superficie di snervamento.
Si rimanda al manuale teorico per maggiori approfondimenti.
□ Shear modulus G: il modulo di elasticità G = caratterizzante il tratto elastico lineare del legame costitu-
tivo a taglio del materiale.
```
□ Shear strength 𝝉૙: valore della tensione tangenziale media che, in assenza di carichi verticali (ߪ௡ = 0), attiva
```
il meccanismo di rottura per fessurazione del puntone diagonale.
dove in tal caso non è necessario immettere tale parametro μ.
Con riferimento al dominio di snervamento alla Mohr Coulomb è necessario definire inoltre i seguenti parametri
```
meccanici:
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
68
□ Friction ratio ࣐ܖ܉ܜ = ࣆ : valore del coefficiente d’attrito utilizzato nel dominio di resistenza alla Mohr-Cou-
```
lomb ():
```
߬ ௨ ߬= 0 ߪߤ +௡
□ Stifness shear/Sliding ratio, α: percentuale di rigidezza a taglio attribuita al pannello murario compreso tra
```
0 e 1 (α = 0 pannello rigido a taglio e deformabile a scorrimento; α = 1 pannello deformabile a taglio e rigido a
```
```
scorrimento).
```
□ Reload stiffness ratio rs = Greload / G: rapporto tra il modulo di elasticità tangenziale nella fase di ricarico
dalla fase di slip Greload ed il modulo di elasticità tangenziale iniziale G. La fase di slip si manifesta quando la
tensione normale  è maggiore della tensione limite: 0 / 
□ Max tensile ratio: t,max / 0 rapporto tra la tensione massima a trazione ammissibile e la tensione limite
```
0 = 0 / (valore significativo solo se )
```
□ Ultimate shear strain, γp: selezionando il legame costitutivo a duttilità fissata o con linear softening è ne-
cessario definire il valore ultimo della deformazione a taglio, oltre il quale si determina la perdita di resi-
```
stenza del legame (=0).
```
```
Figura 6.35 – b) Meccanismo di rottura per fessurazione diagonale; b’) Attivazione del meccanismo sul macro-ele-
```
mento a quattro nodi di HISTRA
Legame costitutivo secondo Mohr-Coulomb Legame costitutivo secondo Turnsek-Cacovic
```
τu : resistenza a taglio;
```
```
τ0 : resistenza a taglio in assenza di sforzo normale (coesione);
```
qF
```
(b)
```
tan
n
u
0



 



u
0
n
’
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
69
```
μ=tanφ: coefficiente di attrito del materiale;
```
σn : tensione normale.
Figura 6.36 – Legami costitutivi per meccanismo di rottura a taglio per fessurazione diagonale
Nel caso di dominio di snervamento alla Turnsek-Cacovic, si adotta la seguente espressione per la de-
finizione del criterio di resistenza:
߬ ௨ ߬= 0 ∙ √1 + ߪ௡1.5 ∙߬ 0
Figura 6.37 - Finestra per la modifica dei parametri che regolano il meccanismo di rottura a taglio per fessurazione
diagonale
```
 Meccanismo di rottura per scorrimento (sliding mechanism)
```
In questa schermata devono essere specificate le caratteristiche meccaniche di calcolo, quali:
□ Constitutive law: è possibile definisce il tipo di legame costitutivo selezionando:
```
 Elastic: elastico lineare;
```
 Elasto-Plastic: elastico infinitamente plastico
```
 Linear-softening: elasto-plastico con softening lineare;
```
```
□ (Mohr-Coulomb, Turnsek Cacovic ): i due criteri Mohr-Coulomb e Turnsek Cacovic sono identici, eccezion
```
fatta per la superficie di snervamento.
```
□ Cohesion c: valore della tensione tangenziale che, in assenza di carichi verticali (ߪ௡ = 0), attiva il meccani-
```
smo di rottura per scorrimento in coerenza al legame costitutivo alla Mohr-Coulomb.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
70
□ Friction ratio ࣐ܖ܉ܜ = ࣆ : valore del coefficiente d’attrito secondo il legame costitutivo alla Mohr-Coulomb
```
(߬ ௨ ߬= 0 ߪߤ +௡).
```
□ Plastic stiffness ratio, : è il rapporto tra la rigidezza post-elastica Gp e quella elastica iniziale G. = Gp/G.
□ Fracture energy: se attivata, viene assegnata l’energia di frattura.
□ Check contact area during analysis: se non selezionato considera come area di contatto su cui calcolare il
contributo coesivo della resistenza quella totale dell'interfaccia, altrimenti aggiorna l'area di contatto con-
siderando solo l'area corrispondente a link trasversali che non hanno superato il limite elastico a trazione.
```
Figura 6.38 - c) Meccanismo di rottura a taglio per scorrimento; c’) Attivazione del meccanismo sul macro-elemento a
```
quattro nodi di HISTRA
```
τu : resistenza a taglio;
```
τ0 : resistenza a taglio in assenza
```
di sforzo normale (coesione);
```
μ=tanφ: coefficiente di attrito
```
del materiale;
```
σn : tensione normale.
Figura 6.39 – Legame costitutivo per meccanismo di rottura a taglio per scorrimento all’interfaccia
qF
```
(c)
```
tan
n
u
0



’
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
71
Figura 6.40 - Finestra per la modifica dei parametri che regolano il meccanismo di rottura a taglio per scorrimento
6.2.2 Material > Steel materials
```
E' possibile definire materiali di tipo acciaio (ad esempio per caratterizzare le catene). Nella schermata
```
di definizione dei materiali devono essere specificate le caratteristiche meccaniche di calcolo, quali:
□ Costitutive law: definisce il tipo di legame costitutivo selezionando:
```
 Elastic: elastico lineare;
```
 Hysteretic:
 Steel01: acciaio 1
```
 Steel02: acciaio 2;
```
Se materiale è elastico lineare:
```
□ Specific weight W: peso specifico del materiale;
```
```
□ Young's modulus E: valore del modulo di elasticità normale;
```
Se il legame costitutivo è isteretico, è possibile inoltre definire i seguenti parametri:
□ Is symmetric: se spuntato considera un comportamento simmetrico a trazione e compressione, altrimenti
```
sdoppia il pannello sottostante per differenziare le proprietà nei due casi;
```
```
□ Yielding strength σy: tensione di snervamento;
```
```
□ Strain-hardening factor, μ: fattore di incrudimento;
```
□ Ultimate strain u: deformazione ultima.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
72
Figura 6.41 - Legame costitutivo acciaio
Figura 6.42 - Finestra per la definizione dei materiali di tipo acciaio
6.2.3 Material > Fiber materials
E' possibile introdurre materiali di tipo fibre, da applicare ai rinforzi. In questa schermata devono essere
specificate le caratteristiche meccaniche di calcolo. Esse sono suddivise in:
```
Fiber Parameters (Parametri delle Fibre):
```
```
□ Specific weight W: peso specifico del materiale;
```
```
□ Young's modulus E: valore del modulo di elasticità normale;
```
□ Tensile strength σyt: massima tensione di calcolo a trazione sopportabile dalla fibra
□ Ductility, η: rapporto tra la deformazione ultima e quella al limite elastico
□
```
Flexural Parameters (Parametri di resistenza a flessione):
```
□ Normal stiffness, Kn : rigidezza normale
□ Tensile strength σt: massima tensione di calcolo a trazione sopportabile dall'interfaccia fibra-supporto
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
73
□ Tensile fracture energy, Gt: energia di frattura a trazione
□ Compressive strength σc: massima tensione di calcolo a compressione sopportabile dall'interfaccia fibra-
supporto
□ Compressive fracture energy, Gc: energia di frattura a compressione
```
Bond Slip Law (comportamento a delaminazione):
```
□ Sliding stiffness, Kf : rigidezza a scorrimento dell'interfaccia fibra-supporto
□ Cohesion, coesione dell'interfaccia fibra-supporto
□ Friction coefficient, μ: coefficiente di attrito
□ Sliding fracture energy, Gf: energia di frattura che governa il meccanismo di delaminazione
Figura 6.43 - Legame costitutivo materiale FRP
Figura 6.44 - Finestra per la definizione dei materiali di tipo FRP
6.2.4 Material > Geothecnical materials
```
E' possibile introdurre materiale geotecnico (terreno). In questa schermata devono essere specificate le
```
caratteristiche meccaniche di calcolo, quali:
```
□ Specific weight W: peso specifico del terreno;
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
74
```
□ Friction angle, ϕ: angolo attrito del terreno;
```
□ Coesion, C: Coesione
□ Horizontal Stiffness of the soil, K0 , K1: coefficienti che consentono di caratterizzare la rigidezza orizzon-
tale del terreno. Detta rigidezza è caratterizzata mediante la seguente equazione di rigidezza Kh = K0 +
```
K1*HK, in cui H è la altezza del terreno interagente col manufatto;
```
```
□ Exsponent in stiffness equation, k: esponente nella equazione di rigidezza;
```
```
□ Over consolidation ratio, OCR: rapporto di sovraconsolidazione;
```
□ Over consolidation ratio coefficient, m: coefficiente di sovraconsolidazione.
```
Figura 6.45 - Finestra per la definizione dei materiali di tipo geotecnico (caratteristiche geotecniche del terreno)
```
6.3 DEFINIZIONE DEI CARICHI
Proseguendo con la procedura guidata di wizard, si passa alla definizione dei carichi. HISTRA BRIDGES
dispone di librerie avanzate per la gestione dei carichi e, come vedremo più avanti, anche delle combi-
```
nazioni (schemi di carico), adeguate alle normative vigenti (NTC 2018 e UIC code 700), per ponti stradali
```
e ferroviari, che consentono di definire i carichi secondo diverse modalità:
```
 Carichi di linea equivalenti (Line load). Nel caso di ponti ferroviari sono applicati in asse a ciascun bi-
```
```
nario. (schemi di carico secondo le UIC code 700).
```
```
 Carichi concentrati (Vehicle load) mediante l’inserimento di una distinta voce di carico elementare, su
```
```
ciascuna ruota, associata ad una condizione di carico (schemi di carico secondo le NTC2018). Nel caso di
```
ponti ferroviari sono applicati su ciascuna rotaia, in corrispondenza degli assi dei vagoni.
Selezionare la tipologia, dal menu a tendina a sinistra:
```
 Vehicles (6.3.2)
```
```
 Area loads (6.3.3)
```
```
 Line loads (6.3.4)
```
```
 Point loads (6.3.5)
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
75
Eventuali altre azioni, neve, vento, etc. potrenno essere definite dall’utente conformemente alle
NTC2018.
La definizione dei carichi, indipendentemente dalla tipologia selezionata, avviene attraverso una fine-
```
stra dallo schema ricorrente (v. Figura 6.46).
```
La finestra è divisa in due parti. Nella parte destra viene visualizzata la tabella di definizione dei carichi.
Nella parte sinistra è invece presente un pannello di controllo generale, dove viene visualizzata la "lista
degli elementi" definiti e la barra dei menu per introdurre o eliminare gli elementi in lista. Selezionare un
elemento e definire le voci di carico a destra.
Con riferimento alla "lista degli elementi" è possibile eseguire le seguenti operazioni:
```
□ definire un nuovo elemento col tasto ;
```
```
□ cancellare un elemento definito cliccando ;
```
```
□ copiare un elemento definito col tasto ;
```
```
□ modificare il nome di un elemento della lista (selezionando l'elemento ed editando il nome);
```
```
□ accedere alla scheda delle proprietà dell'elemento (selezionandolo in elenco);
```
```
□ impostare automaticamente o personalizzando i colori per ciascun elemento definito (selezionando dal
```
```
menu a tendina ).
```
Nella sezione di destra, in cui viene visualizzata e gestita la definizione delle singole voci di carico, è
presente una tabella. Ogni riga corrisponde ad una voce di carico. In alto, sopra la tabella vengono ripor-
```
tati il nome dell'elemento (o carico) che si sta definendo (Name), una sintetica descrizione dello stesso
```
```
(Description), ed i tasti Add, Copy e Delete, che consentono rispettivamente di aggiungere, copiare ed
```
```
eliminare una riga in tabella (corrispondente a una voce elementare di carico).
```
Qualunque sia la tipologia di carico selezionata, è possibile definire:
□ Dynamic Coefficient: coefficiente di amplificazione dinamico, che consente di amplificare i valori caratte-
ristici dei carichi, a seguito di effetti dinamici.
Figura 6.46 – Finestra di definizione dei Carichi
Lista dei carichi definiti
Definizione delle voci di carico
elementari
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
76
6.3.1.1 Definizione dei carichi per ponti ferroviari
Con particolare riferimento ai ponti ferroviari, il software HISTRA BRIDGES consente di definire i modelli
di carico previsti dalle cogenti normative. Secondo le indicazioni del Manuale RFI e delle NTC2018, oc-
corre distinguere il caso di nuove strutture da quello di strutture esistenti, ed in particolare:
```
 Carichi di Progetto (per la progettazione di nuove strutture nuove);
```
```
 Carichi realmente circolanti (per la verifica di strutture esistenti).
```
Lo stesso manuale RFI fa riferimento alle NTC 2018, per quanto riguarda la definizione dei modelli di
carico teorici da adottare per la progettazione di nuove strutture, e mantiene la definizione dei modello
di carico introdotta nella circolare del 2 giugno 95, definendo carichi LM71 per traffico normale e SW0 e
```
SW2 per traffico pesante (v.Figura 6.47)Figura 6.47 – Modelli di carico teorici, adottati in fase di proget-
```
```
tazione di nuove strutture (LM71, per il traffico normale e SW0 e SW2 per il traffico pesante). Sempre dal
```
```
manuale RFI, vengono definiti carichi individuati dalle categorie delle linee (facendo riferimento alle FI-
```
```
CHE UIC code 700), i carichi dovuti a Mezzi di trazione circolanti (locomotori ed automotrici, elettrici e
```
```
diesel e gli elettrotreni) ed i Carichi/Trasporti eccezionali.
```
I suddetti modelli sono integrati in maniera automatica nelle librerie di HISTRA BRIDGES. Possono anche
essere definiti modelli di carico personalizzati.
```
Figura 6.47 – Modelli di carico teorici, adottati in fase di progettazione di nuove strutture (LM71, per il traffico nor-
```
```
male e SW0 e SW2 per il traffico pesante).
```
```
Figura 6.48 – Modelli di carico realmente circolanti (UIC-code 700). Schema geometrico di un carro.
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
77
```
Figura 6.49 - Modellazione mediante carichi lineari equivalenti (Line Load).
```
```
Figura 6.50 - Modellazione mediante carichi concentrati (Vehicle Load)
```
6.3.1.2 Definizione dei carichi per ponti stradali
Con particolare riferimento ai ponti stradali, il software HISTRA BRIDGES consente di definire i modelli di
carico previsti dalle NTC2018.
I carichi su ponti stradali possono essere definiti come:
 Vehicle Load, che consente di simulare carichi veicolari concentrati su due assi in tandem, applicati se-
```
condo le disposizioni di normativa (v. Figura 6.14).
```
 Area Load, che consente di simulare i carichi distribuiti su superfici di carico, così come indicato dalle
norme tecniche in figura 5.1.2 e qui riportato in Figura 6.14.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
78
Figura 6.51 – Definizione dei carichi veicolari, modellati come carichi concentrati su due assi in tandem
```
(Vehicle load).
```
```
Figura 6.52 – Definizione dei carichi di area (Area load)
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
79
Figura 6.53 – Visualizzazione del modello 3d del ponte e dei carichi veicolari - schema 1
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
80
Figura 6.54 – Esempio carichi veicolari schema di carico 1 NTC2018 – figura 5.1.2 – Schema di carico1.
6.3.2 Loads > Vehicles loads
Le azioni da traffico stradale o ferroviario possono essere rappresentate mediante un set di
carichi concentrati applicati in corrispondenza degli assali del veicolo secondo i modelli di carico da
```
traffico suggeriti dalle norme (vedi Figura 6.55, Figura 6.56). Tali azioni sono definite come Vehicle Loads;
```
i punti di applicazione delle forze concentrate sul piano stradale o ferroviario saranno individuati attra-
```
verso la definizione degli schemi di carico (vedi par. 6.4).
```
La finestra dei carichi Vehicles, si suddivide in tre parti:
 superiormente è possibile definire il coefficiente di amplificazione dinamico dei carichi e le dimensioni
aggiuntive di ingombro del veicolo oltre la sagoma, di forma rettangolare, che inscrive i carichi concen-
trati. Tali distanze sono utili per la corretta applicazione dei carichi concentrati sul piano estradossale
```
del ponte;
```
 al centro è presente una tabella attraverso cui è possibile definire le azioni concentrate trasmesse dal
```
veicolo al piano stradale (v. Figura 6.46).
```
 inferiormente è rappresentata un’anteprima delle azioni concentrate definite nonché la sagoma del vei-
```
colo di forma rettangolare;
```
Le distanze d1, d2, d3, d4 rappresentano rispettivamente le distanze della sagoma del veicolo, dal ret-
tangolo che circoscrive le aree di carico.
Le colonne della tabella consentono di specificare, per area di carico elementare, le coordinate della
```
ruota, le dimensioni dell'area di impronta (larghezza e lunghezza) e l’intensità del carico, oltre ai coeffi-
```
cienti di combinazione secondo la normativa adottata. In particolare si fa riferimento alle NTC 2018 e agli
```
Schemi di carico specificati al par. 5.1.3.3.3 e riportati in figura 5.1.2 (v. Figura 6.55 ) delle stesse NTC 2018.
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
81
```
□ Name: il nome della voce di carico elementare (Ruota N.).
```
□ Load Condition: è necessario indicare la condizione di carico corrispondente alla voce di carico che si
sta definendo, ad esempio permanente, variabile, veicolare, carico laterale, serpeggio, etc….
□ X e Y: coordinate locali che individuano la posizione del baricentro delle ruote del veicolo, rispetto al
centro del veicolo stesso.
□ Lenght: lunghezza dell'area di impronta della ruota. Nel caso di carichi ferroviari, questo valore va posto
pari a zero.
□ Width: larghezza dell'area di impronta della ruota. Nel caso di carichi ferroviari, questo valore va posto
pari a zero.
□ Load Value: è il valore dell’intensità del carico espresso nell’unità di misura selezionate dall’apposito
menu a tendina. Se il carico è di tipo “variabile” di default viene inserita l’intensità secondo la normativa
italiana in base alla destinazione d’uso della struttura. È possibile modificare tale valore, secondo le
scelte del progettista .
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
```
normativa italiana NTC 2008 (per i carichi veicolari stradali si fa riferimento alla tabella 5.1.VI, mentre
```
```
per i carichi veicolari ferroviari, si fa riferimento alle UIC700). Cliccando sui valori è possibile editare tali
```
coefficienti.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
82
Figura 6.55 - Schemi di carico veicolari secondo le NTC 2018
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
83
Figura 6.56 - Schemi di carico ferroviario secondo le UIC 700.
6.3.3 Loads > Area loads
La schermata dei carichi di area, è costituita da una tabella ove ciascuna riga consente l’inserimento di
```
una distinta voce di carico elementare (peso proprio, variabile, etc…) associata ad una condizione di ca-
```
rico. Le colonne della tabella consentono di specificare, per ogni voce di carico elementare, l’intensità
del carico, direzione, tipo ed i coefficienti di combinazione per carichi variabili, secondo la normativa
```
adottata:
```
```
□ Name: il nome della voce di carico elementare (Ballast, Marciapiedi, etc…).
```
```
□ Load Condition: è necessario indicare la condizione di carico elementare tra quelle predefinite (“perma-
```
```
nente”, “variabile”, etc.).
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
84
□ Use Destination: nel solo caso in cui sia stato selezionato “variabile” nella colonna Load condition, è
necessario indicare la destinazione d’uso della struttura modellata. Ciò consente l’attribuzione automa-
tica dei coefficienti di combinazione, secondo la normativa italiana, che l’utente può comunque modifi-
care, cliccando nell’apposita casella o selezionando la voce “User”.
□ Type Load: tipo di carico.
□ Direction: consente di selezionare la direzione di applicazione del carico.
□ Is Projected: se attivo, considera l’area di carico agente pari alla proiezione dell’area di carico sul piano
orizzontale di riferimento globale xy. Questo comando è efficace nei casi in cui la superficie dell’ele-
```
mento computazionale (quad) su cui viene applicato il carico di area è inclinata rispetto al piano oriz-
```
zontale.
□ Load Value: è il valore dell’intensità del carico espresso nell’unità di misura selezionate dall’apposito
menu a tendina. Se il carico è di tipo “variabile” di default viene inserita l’intensità secondo la normativa
italiana in base alla destinazione d’uso della struttura. È possibile modificare tale valore, secondo le
```
scelte del progettista. La forza di frenamento (Braking action) su ponti stradali va valutata dall’utente
```
secondo le indicazioni di normativa di cui al par. 5.1.3.5 delle NTC2018, equazione [5.1.4] e ridistribuita
sulla corrispondente superficie.
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
normativa italiana. Cliccando sui valori è possibile editare tali coefficienti.
Figura 6.57 - Definizione dei Carichi di Area - Area Loads – Esempio carico di area per ponti ferroviari.
Figura 6.58 - Definizione dei Carichi di Area - Area Loads – Esempio carico veicolare e azione frenante su
ponti stradali.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
85
6.3.4 Loads > Line loads
Analogamente a quanto esposto superiormente per i carichi di area, è possibile definire i carichi di linea
da assegnare alle linee passanti tra due nodi del modello, inserendo: nome e descrizione facoltativa del
carico, condizione di carico ed eventuale destinazione d’uso, se si sta definendo un carico variabile, di-
rezione, intensità del carico, oltre ai coefficienti di combinazione.
Figura 6.59 - Definizione dei Carichi di Linea - Line Loads
```
□ Name: il nome della voce di carico elementare (LineLoadN, Deragliamento, TrenoScarico, etc…).
```
```
□ Load Condition: è necessario indicare la condizione di carico elementare tra quelle predefinite (“perma-
```
```
nente”, “variabile”, etc.).
```
□ Use Destination: nel solo caso in cui sia stato selezionato “variabile” nella colonna Load condition, è
necessario indicare la destinazione d’uso della struttura modellata. Ciò consente l’attribuzione automa-
tica dei coefficienti di combinazione, secondo la normativa italiana, che l’utente può comunque modifi-
care, cliccando nell’apposita casella o selezionando la voce “User”.
□ Type Load: tipo di carico
□ Direction: consente di selezionare la direzione di applicazione del carico.
□ Load Value: è il valore dell’intensità del carico espresso nell’unità di misura selezionate dall’apposito
menu a tendina. Se il carico è di tipo “variabile” di default viene inserita l’intensità secondo la normativa
italiana in base alla destinazione d’uso della struttura. È possibile modificare tale valore, secondo le
scelte del progettista.
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
normativa italiana. Cliccando sui valori è possibile editare tali coefficienti.
6.3.5 Loads > Point loads
E’ possibile definire i carichi di punto, da assegnare in corrispondenza di un nodo del modello, inserendo:
nome e descrizione facoltativa del carico, condizione di carico ed eventuale destinazione d’uso, se si sta
definendo un carico variabile, direzione, intensità del carico, oltre ai coefficienti di combinazione.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
86
Figura 6.60 - Definizione dei Carichi di Punto - Point Loads
□ Name: il nome della voce di carico elementare.
```
□ Load Condition: è necessario indicare la condizione di carico elementare tra quelle predefinite (ad
```
```
esempio il serpeggio, nei casi di carichi ferroviari).
```
□ Use Destination: nel solo caso in cui sia stato selezionato “variabile” nella colonna Load condition, è
necessario indicare la destinazione d’uso della struttura modellata. Ciò consente l’attribuzione automa-
tica dei coefficienti di combinazione, secondo la normativa italiana, che l’utente può comunque modifi-
care, cliccando nell’apposita casella o selezionando la voce “User”.
□ Type Load: tipo di carico
□ Direction: consente di selezionare la direzione di applicazione del carico.
□ Load Value: è il valore dell’intensità del carico espresso nell’unità di misura selezionate dall’apposito
menu a tendina. Se il carico è di tipo “variabile” di default viene inserita l’intensità secondo la normativa
italiana in base alla destinazione d’uso della struttura. È possibile modificare tale valore, secondo le
scelte del progettista.
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
normativa italiana. Cliccando sui valori è possibile editare tali coefficienti.
La definizione dei carichi viene eseguita specificando: nome e descrizione facoltativa del carico, condi-
zione di carico ed eventuale destinazione d’uso se si definisce un carico variabile, direzione, intensità
```
attraverso il peso specifico (la geometria del carico, che è l'altro parametro per determinare l'intensità
```
```
finale del carico, dipenderà dalla specifica assegnazione) e coefficienti di combinazione. Tuttavia in que-
```
sto caso è possibile definire una sola voce di carico e non cumularle.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
87
6.4 DEFINIZIONE DEGLI SCHEMI DI CARICO
```
Seguendo ancora la procedura guidata di input (Wizard) si passa alla definizione degli Schemi di Carico.
```
Cliccando sul tasto Next, in basso a destra, infatti, si accederà al corrispondente ambiente di input, all'in-
```
terno della scheda Schema (v. Figura 6.61).
```
Figura 6.61 - Definizione degli Schemi di Carico per ponte ferroviario e stradale
```
Gli schemi di carico individuano le condizioni di carico più gravose, in funzione delle disposizioni (o pos-
```
```
sibili posizioni) dei carichi, definiti precedentemente.
```
Come già visto per la definizione dei carichi, anche la finestra di definizione degli Schemi di carico pre-
```
senta una struttura ricorrente e familiare in ambiente HISTRA (v. Figura 6.61). In particolare l'area è divisa
```
in due parti.
```
Nella parte a destra viene visualizzata la tabella (o le tabelle) di definizione, specifica per la tipologia di
```
```
elemento considerata (selezionata sulla griglia posta a sinistra).
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
88
Nella parte sinistra, invece, è presente un pannello di controllo generale, con l'elenco degli schemi di
carico definiti e dei comandi di gestione degli stessi.
Con riferimento alla parte a destra della finestra, per ciascuno schema di carico, occorre definire, nella
```
tabella in alto il carico presente su ciascuna parte del ponte (Banchina, corsia, margine, etc.), siano essi
```
```
carichi mobili veicolari (Vehicle) o fissi (Area Load o Line Load).
```
Figura 6.62 – Schema di carico denominato “Schema-D4” dalle UIC700, per ponti ferroviari.
In azzurro evidenziati carichi di area, in giallo carichi di linea.
Figura 6.63 – Schema di carico denominato “Schema 1” tabella 5.1.IV NTC2018 – per ponti stradali.
In azzurro evidenziati carichi di area, in giallo carichi di linea.
```
Il nome dei “Lane” è predefinito in base alla definizione della Geometria della campata del ponte (v. la
```
```
scheda Geometry cfr. par. 6.1). Il numero di righe viene quindi ereditato dalla configurazione geometrica
```
del ponte.
```
Nella colonna “Vehicle” viene indicata la presenza di carico veicolare (Vehicle load). In assenza selezio-
```
nare “none”.
“NumVehicle” è il numero di veicoli viaggianti sulla stessa linea. Assegnare un numero maggiore o
```
uguale ad 1 equivale ad assegnare un numero finito di vagoni (tanti quanto è il numero assegnato), men-
```
tre assegnare -1 significa definire un convoglio infinito di vagoni.
L’opzione “Opposite” se selezionata consente di definire carichi viaggianti in direzioni opposta. Se que-
sta opzione è attiva viene invertito l’ordine delle posizioni dei carichi veicolari.
Nelle colonne “Area Load” e “Line Load” viene indicata la eventuale presenza rispettivamente di carichi
di area e di linea.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
89
Selezionando il check nella colonna “Exclude”, il carico di area e di linea viene escluso in corrispondenza
dell’ingombro del veicolo. Pertanto non viene sovrapposto all’impronta di quest’ultimo.
L1 ed L2 rappresentano rispettivamente la lunghezza del carico di linea o di area che precede e/o che
```
segue il carico viaggiante (se presente).
```
```
Indicare L1 o L2 pari a “+infinito” significa assegnare un carico di linea o di area che si sviluppa (prima e
```
```
dopo il carico veicolare) per tutta la lunghezza del ponte. Per assegnare “infinito”, digitare “i” da tastiera.
```
Queste lunghezze possono anche essere finite.
Viceversa, porre L1 ed L2 pari a zero equivale a non considerare alcun carico aggiuntivo di linea e/o di
area che preceda e/o segua il carico viaggiante o in generale che non è presente carico di linea o di area
su quella porzione della sezione trasversale del ponte.
```
Nella tabella in basso, vengono definite le posizioni dei carichi viaggianti (Vehicle position), siano essi
```
```
veicolari (per ponti stradali) o ferroviari (per ponti ferroviari), riferite a tutto lo sviluppo longitudinale
```
del ponte.
Figura 6.64 – Posizioni dei carichi viaggianti
Figura 6.65 – Posizioni dei carichi viaggianti. Esempio ponte stradale.
E’ possibile individuare le posizioni del carico viaggiante, seguendo due possibili modalità:
□ Equally spaced: individua le posizioni del carico veicolare suddividendo la lunghezza globale longitu-
dinale del ponte in segmenti ugualmente spaziati. Il numero di posizioni è pari al numero indicato nella
cella Number of position.
□ Worth sections and additional positions: le posizioni del carico veicolare vengono individuate in cor-
```
rispondenza delle sezioni significative (worth sections) del ponte, lungo il suo sviluppo longitudinale. Si
```
```
Posizione dei carichi veicolari (Position)
```
```
Sezioni significative (Worth sections)
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
90
```
considerano di default le sezioni significative in corrispondenza degli appoggi (spalle e pile) e della mez-
```
zeria delle campate. In tal caso il numero di posizioni indicato nella cella Number of positions individua
il numero di posizioni aggiuntive, che verranno inserite all’interno di ciascun segmento, individuato da
due successive sezioni significative. Il numero di posizioni aggiuntive proposte di default è pari a zero
```
(v. campo Additional number of position).
```
Nella tabella “Vehicle Position” vengono create tante righe quante sono le possibili posizioni del carico viag-
giante, e per ciascun carico vengono riportate le corrispondenti ascisse, lungo l'asse longitudinale del ponte,
espresse in cm.
Infine, nella sezione Combination coefficients GC vengono riportati i coefficienti di combinazione dei
Gruppi di Carico, inerenti la simultaneità delle azioni da traffico combinate in gruppi di carico, così come
definiti dalle NTC 2018 in Tabella 5.1.VI, per quanto riguarda i ponti stradali, e dalle Tabella 5.2.III delle
NTC2018 e Norme UIC700, per quanto riguarda i ponti ferroviari.
Figura 6.66 – Coefficienti relativi ai carichi variabili per ponti stradali e pedonali, secondo D.M.17/01/2018.
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
91
Figura 6.67 – Coefficienti relativi ai carichi mobili in funzione di binari presenti sul ponte ferroviario, secondo
D.M.17/01/2018
Figura 6.68 – Coefficienti relativi alla simultaneità delle azioni da traffico combinate in gruppi di carico secondo
```
D.M.17/01/2018 (Ponti ferroviari).
```
Figura 6.69 – Coefficienti relativi alla simultaneità delle azioni da traffico combinate in gruppi di carico secondo
```
UIC700 (Ponti ferroviari)
```
Manuale Utente HISTRA HISTRA BRIDGES: PROCEDURA GUIDATA DI INPUT
92
6.5 DEFINIZIONE E ASSEGNAZIONE DELLE COMBINAZIONE DI CARICO ANALISI
```
Nella finestra Analysis (v. Figura 6.70), accessibile proseguendo con la procedura guidata (Wizard), è
```
```
possibile definire le Analisi, assegnando a ciascuna combinazione (Paragrafo 1318.4.4) (Statica e Sismica),
```
selezionata dal menu a tendina, il corrispondente Schema di Carico. Lo schema di carico viene assegnato,
selezionandoli mediante il menu a tendina tra quelli precedentemente definiti. In HISTRA BRIDGES le
analisi vengono definite automaticamente, per ponti ferroviari e stradali. In HISTRA Arches and Vaults
```
la combinazione di carico può essere assegnata all’analisi mediante il menù Define  Analysis (vd. par.
```
```
8.4.5)
```
Figura 6.70 - Definizione delle combinaizioni di carico nelle Analisi – HISTRA BRIDGES
Figura 6.71 - Definizione delle combinaizioni di carico nelle Analisi – HISTRA Arches and Vaults
Manuale Utente HISTRA AREA DI LAVORO
7 AREA DI LAVORO
L’interfaccia utente è semplice ed intuitiva e consente un’agevole visualizzazione ed analisi dei modelli
strutturali anche più complessi ed articolati. Pertanto i manuali messi a disposizione costituiscono un
utile, indispensabile supporto, per l’utilizzo del software. Con questa interfaccia HISTRA si propone agli
utenti per effettuare analisi immediate e con una reportistica ricca di contenuti, utili per poter formulare
motivate valutazioni sull’effettivo comportamento strutturale dei ponti in muratura.
```
L’area di lavoro principale (v. Figura 7.1) , che è la finestra di apertura del programma, è quella nell’am-
```
bito della quale possono essere gestite la visualizzazione e le opzioni del modello. Si suddivide nelle
seguenti parti:
```
□ Menu principale (cfr. § 7.2 ), posto superiormente alla finestra centrale;
```
```
□ Menu comandi rapidi (cfr. § 7.3), posto in alto sulla sinistra della schermata principale;
```
```
□ Finestra centrale, per la vista del modello 3D;
```
```
□ Barra delle informazioni (cfr. § 7.4), posta in basso alla finestra centrale;
```
```
□ Finestra delle proprietà del modello (cfr. § 7.5), posta sulla destra della schermata principale.
```
Figura 7.1 - Interfaccia utente - Schermata principale del programma
Al fine di lavorare con maggiore efficacia è utile conoscere le principali modalità di lavoro nell'area di
lavoro principale. In particolare:
□ Tasto sinistro del mouse: serve per selezionare elementi quando non si è attivato nessun comando, o
```
per eseguire le operazioni di un comando se si è fatto accesso ad un comando;
```
□ Selezione a finestra, in maniera analoga con quando avviene nei software CAD se la finestra va da si-
nistra a destra vengono selezionati tutti gli elementi completamente compresi nella finestra, altrimenti
```
vengono selezionati tutti gli elementi che anche parzialmente ricadono nella finestra;
```
□ Tasto destro, se non si ha niente in selezione ripete l'ultimo comando altrimenti accede al menu conte-
```
stuale dell'elemento in selezione (cfr. § 7.1);
```
```
□ Tasto destro con pressione prolungata, accede al comando orbita che consente di ruotale il modello;
```
Barra delle informazioni
Finestra centrale
Finestra delle
proprietà del
modello
Menù comandi
rapidi
Menù principale
Manuale Utente HISTRA AREA DI LAVORO
94
□ Tasto shift, la pressione prolungata di questo tasto consente di accedere alla possibilità di selezionare
più elementi cliccando col tasto sinistro sui diversi elementi che si vogliono aggiungere alla selezione.
□ Combinazione di tasti Alt+c, consente di passare dalla vista del modello computazionale a quella del
```
modello geometrico e viceversa (cfr. § 8.3.2)
```
□ Tasto Canc, cancella gli elementi in selezione
□ Tasto Esc, consente di uscire dalla modalità del comando corrente
7.1 MENU CONTESTUALE
Il menu contestuale consente di accedere ad alcune funzionalità utili per operare direttamente sugli ele-
menti in selezione. Per accedere al menu contestuale basta cliccare col tasto destro nella finestra prin-
cipale, sugli elementi in selezione. La lista dei comandi cui si può accedere è funzione dell'elemento/i in
selezione.
Il menu dei comandi comprende una parte comune a tutte le tipologie di elementi e una parte specifica.
Se in selezione sono presenti elementi appartenenti a diverse tipologie, quando si opera con i comandi
```
generali, questi saranno applicati a tutti gli elementi in selezione; se si accede al sottomenu specifico di
```
una certa tipologia quei comandi saranno validi solo per gli elementi di tale tipologia.
I comandi generali, indipendenti dalla tipologia di elemento, sono:
□ Set this element as view target: imposta l’elemento corrente come punto di vista target
□ Show all / only selected elements: consente di visualizzare tutto il modello o solo l’elemento selezio-
```
nato (cfr. § 8.3.3);
```
```
□ Invert visibility: nasconde gli elementi visibili e mostra quelli nascosti nella vista corrente (cfr. § 8.3.8);
```
```
□ Save as image: salva come immagine la vista corrente;
```
```
□ Show / Hide selected elements: mostra / nasconde gli elementi in selezione (cfr. § 8.3.4 e § 8.3.6);
```
```
□ Deselect: consente di deselezionare gli elementi ed è equivalente a premere il tasto Esc;
```
```
□ Add selected elements to group: aggiunge l’elemento selezionato a un gruppo;
```
```
□ Copy selected objects: consente di copiare tutti gli oggetti in selezione;
```
□ Delete all selected objects: consente di eliminare tutti gli oggetti in selezione ed è equivalente a pre-
mere il tasto Canc.
Figura 7.2 – Menu contestuale – comandi generali
Alcuni dei comandi sono disponibili solo a calcolo eseguito e servono per accedere ai dati di output.
Inoltre, in base all'elemento selezionato sono disponibili dei comandi più specifici, quali ad esempio:
□ Apply area/line/point load: consente di applicare un carico di area, di linea o di punto all'elemento
```
selezionato (cfr. § 8.4.2);
```
Manuale Utente HISTRA AREA DI LAVORO
95
```
□ Apply material: consente di applicare un materiale tra quelli già definiti (per la definizione cfr. §6.3);
```
□ Internal Costraint: consente di applicare o rimuovere vincoli all’elemento computazionale selezionato.
Figura 7.3 – Menu contestuale – Quad
Figura 7.4 – Menu contestuale – Internal Costraint – Applica o rimuovi
7.2 MENU PRINCIPALE
Il menu principale, posto in alto, è il menu di controllo e di comando del programma. È costituito dai
seguenti menu a tendina:
```
□ File (cfr. § 8.1);
```
```
□ Model (cfr. § 8.2);
```
```
□ View (cfr. § 8.3);
```
```
□ Define (cfr. § 8.4);
```
□ Edit
```
□ Run (cfr. § 8.7)
```
```
□ Response (cfr. § 8.8);
```
```
□ Report (cfr. § 8.9);
```
```
□ ? - Help (cfr. § 8.11)
```
Dai singoli menu è possibile accedere alle singole funzioni e finestre di comando, descritte specificata-
mente nel successivo capitolo.
Figura 7.5 – Voci del Menu principale
Manuale Utente HISTRA AREA DI LAVORO
96
7.3 MENU COMANDI RAPIDI
Questo menu contiene i comandi che l’utente si troverà ad utilizzare con maggiore frequenza. E’ possibile
infatti accedere agli strumenti di disegno, ai comandi per l’assegnazione e modifica delle proprietà e al
menu di output della risposta. La maggior parte di questi comandi ha un corrispondente disponibile nel
menu principale.
Il menu dei comandi rapidi è composto dai seguenti gruppi. Per espandere e vedere i contenuti cliccare
sul corrispondente comando
□ Find elements
□ Coordinate
□ Draw
□ Define
□ Loads
□ Legend
COMANDO DESCRIZIONE
Barra comandi rapidi
```
Nuovo: Apre un file nuovo su cui mo-
```
```
dellare nuovi elementi strutturali (cfr.
```
```
§8.1.1)
```
```
Apri: Apre un file esistente precedente-
```
```
mente salvato (cfr. §8.1.2)
```
```
Save: Aggiorna il modello con le modifi-
```
```
che apportate e salva i dati su file (cfr. §
```
```
8.1.4)
```
Manuale Utente HISTRA AREA DI LAVORO
97
Find elements
Digitando nell’apposito campo è possi-
bile trovare elementi computazionali
nel modello.
Coordinate
Absolute cartesian / polar coordinate:
consente di indicare le coordinate nel
```
sistema di riferimento globale (carte-
```
```
siane o polari), di un punto che si vuole
```
inserire.
Relative cartesian/polar coordinate:
consente di indicare le coordinate rela-
```
tive (cartesiane o polari), di un punto
```
che si vuole inserire.
Draw
Draw Truss: permette di modellare ele-
menti catena
Draw opening: permette di modellare
una finestra all’interno di un pannello in
muratura
Draw ground beam: permette di model-
lare una trave di fondazione
Manuale Utente HISTRA AREA DI LAVORO
98
Edit Bridge: consente di accedere alla
procedura guidata di input per modifi-
care le caratteristiche geometriche del
```
ponte (disponibile per HISTRA BRIDGES)
```
Define
Masonry Material: permette di accedere
alla schermata di definizione dei mate-
```
riali muratura (cfr. §6.2.1)
```
Steel Material: permette di accedere alla
schermata di definizione dei materiali
```
acciaio (cfr. §6.2.2)
```
Area Loads: consente di accedere alla
schermata di definizione dei carichi di
```
area (cfr. §6.3.3)
```
Line Loads: consente di accedere alla
```
schermata carichi di linea (cfr. §6.3.4)
```
Point Loads: consente di accedere alla
```
schermata carichi di punto (cfr. §6.3.5)
```
Geotechnical Materials: consente di de-
```
finire materiale geotecnico (terreno)
```
```
(cfr. §6.2.4)
```
Vehicle Loads: consente di definire i ca-
richi veicolari, per ponti stradali e ferro-
```
viari. (cfr. §6.3.2).
```
Loads
Manuale Utente HISTRA AREA DI LAVORO
99
Load Condition: Consente di filtrare la
visualizzazione delle condizioni di ca-
rico e lo schema, oltre le vari posizioni
nel caso di carico viaggiante. E’ possi-
bile amplificarne il fattore di scala nella
rappresentazione grafica, che viene vi-
sualizzata nell’ambiente principale.
Legend
Di volta in volta, a seconda delle op-
zioni di visualizzazione selezionate,
compariranno le opportune indicazioni
con i colori.
Response
Si tratta di una serie di comandi utili per
la navigazione della risposta tra le ana-
lisi e tra i diversi step. In particolare si
può:
 vedere l'animazione della risposta in
termini di deformata
 selezionare un'analisi tra quelle ese-
guite
 selezionare un passo generico tra quelli
dell'analisi selezionata attraverso un
cursore di avanzamento
 selezionare un passo generico tra quelli
dell'analisi selezionata digitando il nu-
mero del passo desiderato
 amplificare il fattore di scala della de-
formata
 visualizzare un'anteprima della curva di
capacità
 accedere a tutte le funzioni dei grafici
```
(ad es. esportazione)
```
 selezionare un passo generico tra quelli
dell'analisi selezionata cliccando sullo
step corrispondente nella curva di ca-
pacità
Manuale Utente HISTRA AREA DI LAVORO
100
7.4 BARRA DELLE INFORMAZIONI
Nella barra delle informazioni, posta in basso a sinistra della finestra principale, sono indicate alcune
informazioni di carattere molto generale che è bene aver sempre presente. Da sinistra verso destra le
informazioni riportate sono:
Figura 7.6 - Barra delle informazioni
```
□ Il tipo di vista 3D del modello (cfr. § 8.3.2):
```
```
o Geometric Model;
```
```
o Computational Model;
```
```
□ Un menu a tendina delle unità di misura con cui si sta operando nella creazione del modello geometrico;
```
□ Un pulsante che consente di passare da vista geometrica a computazionale
□ Un pulsante che consente di passare da vista estrusa a computazionale
```
□ Le frecce up/down per cambiare quota nella griglia di riferimento;
```
```
□ Il menu vista per scegliere il tipo di vista piana o tridimensionale del modello;
```
□ Il menu a tendina per selezionare il tipo di osnap che serve ad attaccarsi col puntatore agli spigoli
```
dell’elemento disegnato o alla griglia di riferimento creata;
```
□ Il pulsante griglia di riferimento che serve a creare le linee di costruzione per disegnare un modello
```
geometrico di un elemento strutturale;
```
□ La quota corrente e le coordinate del puntatore:
```
□ Il pulsante rapido Run per eseguire le analisi ;
```
```
□ Il pulsante di blocco/sblocco del modello;
```
```
□ Il pulsante per il set color ;
```
□ Il pulsante che consente di visualizzare le proprietà del modello.
Sulla parte sinistra della barra delle informazioni si trovano invece suggerimenti. Ad esempio se si è
fatto accesso ad un comando viene indicato il comando e il tipo di operazione attesa. Questa funziona-
lità risulta molto utile quando il comando prevedere operazioni in sequenza: in questo caso via via che
vengono svolte le operazioni, viene suggerita l'operazione corrente da eseguire.
Inoltre, quando si esegue doppio click sulla barra delle informazioni è possibile visualizzare la lista degli
```
ultimi comandi eseguiti. Tale funzionalità risulta particolarmente utile (soprattutto quando si sono ese-
```
```
guite una o più misure di distanza) poichè è possibile selezionare uno o più comandi, copiarli è incollarli
```
in un file di testo.
Manuale Utente HISTRA AREA DI LAVORO
101
7.5 FINESTRA DELLE PROPRIETA' DEL MODELLO
Si tratta di una barra dinamica che si aggiorna in base agli elementi in selezione. E' molto utile per almeno
```
tre funzionalità: visualizzazione delle proprietà (dati geometrici e assegnazioni), visualizzazione nume-
```
```
rica della risposta degli elementi (spostamenti e sollecitazioni) e infine per la possibilità di editare nu-
```
```
merose proprietà in fase di input (spostare coordinate, cambiare assegnazioni, ecc...).
```
Manuale Utente HISTRA MENU PRINCIPALE
8 MENU PRINCIPALE
In questo capitolo vengono descritti nel dettaglio tutti i comandi eseguibili sul modello dal menu prin-
cipale dell’area di lavoro. In ciascuno dei paragrafi seguenti viene descritta dettagliatamente ciascuna
delle voci del menu principale, di seguito elencate:
```
□ File (cfr. §8.1)
```
```
□ Model (cfr.§8.2)
```
```
□ View (cfr. §8.3)
```
```
□ Define (cfr. §8.4)
```
```
□ Draw (cfr. §8.5)
```
```
□ Edit (cfr. § 8.6)
```
```
□ Run (cfr. §8.7)
```
```
□ Response (cfr. §8.8)
```
```
□ Report (cfr. §8.9)
```
```
□ ? - Help (cfr. §8.11)
```
8.1 FILE
Questo menu consente l’accesso e la gestione dei file dei modelli. I comandi di questo menu coinvolgono
tutte le istruzioni applicabili in misura generale a tutta la finestra.
I comandi disponibili sono:
```
□ New (cfr. § 8.1.1)
```
```
□ Save (cfr. § 8.1.4)
```
```
□ Save as (cfr. § 8.1.5)
```
```
□ Open (cfr. § 8.1.2)
```
```
□ Recent files (cfr. § 8.1.3)
```
```
□ Close (cfr. § 8.1.6)
```
```
□ Open log file (cfr. § 8.1.7)
```
```
□ Import dxf (cfr. § 8.1.8)
```
```
□ Export dxf (cfr.§ 8.1.9)
```
8.1.1 New
Questo comando elimina tutti i dati pre-esistenti e avvia un nuovo lavoro.
8.1.2 Open
Questo comando apre un lavoro memorizzato su hard-disk o su qualunque tipo di supporto di memoria
```
(file con estensione .hrs).
```
8.1.3 Recent files
Questo comando attiva un menu a tendina da cui è possibile aprire gli ultimi lavori utilizzati sul PC.
8.1.4 Save
Questo comando salva il lavoro corrente sovrascrivendo il file esistente.
Manuale Utente HISTRA MENU PRINCIPALE
104
8.1.5 Save as
Questo comando salva il lavoro corrente specificando un nuovo nome e\o percorso.
8.1.6 Close
È il commando che chiude il programma in esecuzione.
8.1.7 Open log file
Apre il file di log che riepiloga le operazioni eseguite dal programma.
8.1.8 Import dxf
Apre la finestra per l'importazione della geometria del modello da file DXF.
Comando disponibile solo per chi possiede il modulo “Import”.
Per importare da file DXF, occorre selezionare il file DXF cliccando sull’apposito comando, quindi perso-
nalizzare le proprietà dei layer individuati nel modello.
Si può scegliere se abilitare o meno il layer del modello che si sta importando, mediante il check di spunta
```
su ciascuna riga. E’ possibile assegnare un materiale e uno spessore del quad (o sezione del truss) diverso
```
per ciascun layer.
Infine bisogna indicare a quanto corrisponde una unità CAD.
Figura 8.1 – Finestra DXF Import – importazione modello da file DXF
Manuale Utente HISTRA MENU PRINCIPALE
105
Figura 8.2 – Opzioni avanzate per importazione di modello da file dxf
Cliccando su Advanced Options, si apre un pannello aggiuntivo in cui è possibile personalizzare le op-
zioni avanzate di importazione del dxf.
□ Line: consente di selezionare il tipo di elemento corrispondente agli elementi di tipo linea in ambiente
```
CAD, scegliendo tra Linee di Riferimento (Line Reference), elementi computazionali di tipo Truss, ele-
```
```
menti asta (Frame elements);
```
□ Polygon/3DFace: consente di associare agli elementi di tipo Poligono o 3DFace, importati da CAD, ele-
```
menti computazionali di tipo Quad o Vertex;
```
```
□ Polyface Mesh: consente di associare alla mesh elementi di tipo Quad/Vertex, o di tipo Solid;
```
```
□ Normals Quad/Vertex: consente di selezionare come direzione normale al Quad (o Vertex) la direzione
```
```
della bisettrice (Bisector direction) o quella Ortogonale (Orthogonal direction).
```
8.1.9 Export dxf
Apre la finestra per l'importazione della geometria del modello da file dxf.
Comando disponibile solo per chi possiede il modulo “Export”.
Nella suddetta finestra occorre selezionare il tipo di elemento CAD a cui far corrispondere gli elementi
computazionali Quad/Vertex, salvandoli come 3DFace o come PolyfaceMesh.
Indicare la misura corrispondente ad una unità CAD e cliccare sul tasto Export Now.
Figura 8.3 – Finestra DXF Export – Esportazione del modello in formato DXF
Manuale Utente HISTRA MENU PRINCIPALE
106
8.2 MODEL
L’accesso al menu Model consente l’impostazione di alcuni settaggi generali, quali la gestione della ope-
razione di selezione di oggetti mediante gruppi o materiali o carichi, la creazione di una griglia di dise-
gno, le opzioni di mesh per la generazione del modello computazionale, l’accesso all’ambiente di crea-
```
zione del modello geometrico del ponte (procedura di wizard spiegata nel precedente capitolo).
```
In particolare vengono distinte le seguenti voci, che vengono di seguito esaminate in dettaglio:
□ Info
□ Advanced options
□ Update computational model
□ Select
8.2.1 Info
La finestra Info consente di gestire tutte le informazioni generali del modello. È costituita da una strut-
tura multi-schede. Sono disponibil le seguenti schede
```
□ Building (par. 8.2.1.1)
```
□ Seismic Response Spectrum
□ User
8.2.1.1 Building
Consente di gestire le informazioni generali relative alla struttura che si sta analizzando, e le norme tec-
niche alle quali si fa riferimento.
In particolare è possibile definire:
```
 Building Name > Nome dell’edficio;
```
```
 Building owner’s > Proprietario dell’edificio (committente);
```
```
 Country > Paese in cui sorge l’edficio;
```
```
 Region/State > Stato in cui sorge l’edificio;
```
```
 Province > Provincia in cui sorge l’edificio;
```
```
 City > Città in cui sorge l’edificio;
```
 Address > Indirizzo
 CAP / ZIP
 Latitude > Latitudine
 Intitude > Longitudine
```
 Notes > Eventuali note informative;
```
```
Per quanto rigurda le coordinate spaziali (latitudine e longitudine) è possibile mostrarle mediante geo-
```
```
localizzazione in google Maps, tramite il pulsante;
```
Manuale Utente HISTRA MENU PRINCIPALE
107
8.2.1.2 Seismic Response Spectrum
Mediante tale schede è possibili definire e visulaizzare gli spettri di risposta ai diversi stati limite così
come definiti dalle Norme Tecniche per le costruzioni. In particolare è necessario inserire i relativi para-
metri strutturali e di sito secondo i quali verrano calcolati gli spettri di risposta.
Figura 8.4 – Finestra Seismic Response Spectrum
Structure parameters
 New/Exsisting structure > selezionare il tipo di struttura scegliendo da menu a tendina tra Existing struc-
ture o New Structure
 Structure Tipology > Tipologia di struttura. Selezionare da menu a tendina il tipo di struttura: Struttura
```
in Muratura (masonry structure) , struttura in c.a. (reinforced concrete structure) , struttura in acciaio
```
```
(Steel Structure), struttura mista (mixed structure)
```
```
 Knouledge level > indicare il livello di conoscenza LC1 (livello di conoscenza elevato) LC2, LC3
```
8.2.1.3 User Info
La finestra User Info consente di definire le informazioni generali dell’utente. In particolare sarà possibile
```
inserire:
```
 Name
 Society
 Country
 Region / State
 Province
 City
 Address
 CAP / ZIP
Manuale Utente HISTRA MENU PRINCIPALE
108
 Email
 Telephone
8.2.2 Advanced options
La finestra Advanced options consente di gestire tutte le opzioni generali del modello. In particolare è
costituita da una struttura multi-schede. In questo manuale vengono riportate le sole schede di perti-
nenza, tralasciando quelle relative alla modellazione di Arches and Vaults, per cui si rimanda al Manuale
Utente di HISTRA Arches and Vaults.
Sono disponibili, tra le altre, le seguenti schede:
```
□ Interface (cfr. § 8.2.2.1)
```
```
□ Solver (cfr. § 8.2.2.2)
```
```
□ General ( cfr. § 8.2.2.3)
```
```
□ Mass Matrix (cfr. § 8.2.2.4)
```
8.2.2.1 Interface
All'interno della scheda Interface sono disponibili le opzioni di discretizzazione delle molle di interfaccia.
```
 Max links distance > massima distanza tra le molle presenti sulle superfici di interfaccia;
```
 Number of links rows > numero di righe lungo cui vengono disposte le molle di interfaccia.
Figura 8.5 – Finestra Advanced Options - Interface - per l’impostazione delle opzioni avanzate di modellazione
delle interfacce.
8.2.2.2 Solver
La scheda Solver contiene tutte le impostazioni secondo le quali opera il solutore. La finestra è suddivisa
in due gruppi di comandi:
Other Options:
Manuale Utente HISTRA MENU PRINCIPALE
109
```
 Save all links status > se selezionato, salva tutti gli stati delle molle;
```
 Show graph error > riporta in fase di analisi un grafico che ad ogni passo indica l'andamento dello squi-
```
librio globale;
```
 Show graph error Dof > riporta in fase di analisi un grafico che ad ogni passo indica l'andamento dello
```
squilibrio corrispondente a ciascun grado di libertà;
```
 Number of records saved for each step > numero di passi entro cui vengono salvate le informazioni sulle
```
analisi;
```
```
 Max number of thread for save > massimo numero di processi di salvataggio eseguibili parallelamente;
```
Figura 8.6 – Finestra Advanced Options - Solver, per l’impostazione delle opzioni di gestione del solutore.
8.2.2.3 General
All'interno della scheda General sono disponibili le opzioni di gestione delle tolleranze, per la gestione
e la creazione del modello computazionale.
Figura 8.7 – Finestra Advanced Options - General, per l’impostazione delle opzioni generali di modellazione.
Manuale Utente HISTRA MENU PRINCIPALE
110
8.2.2.4 Mass Matrix
E' possibile selezionare l'opzione Lumped mass matrix, che consiste nel concentrare la massa di ciascun
elemento nel suo baricentro, o in alternativa l'opzione Consistent mass matrix, che impiega la matrice di
massa coerente.
Figura 8.8 – Finestra Advanced Options - Mass Matrix
8.2.3 Update computational model
Consente di aggiornare il modello computazione al seguito di modifche al modello geometrico.
8.2.4 Select
Apre la finestra che consente di selezionare gli elementi in base a gruppi ci oggetti, materiali assegnati
o carichi applicati:
□ Select by Group: consente di selezionare un insieme di elementi, in base al gruppo di oggetti di appar-
```
tenenza. Il gruppo di oggetti viene definito mediante il comando Define > Group object ;
```
```
□ Select by Materials: consente di selezionare un gruppo di elementi, in base al materiale assegnato;
```
□ Select by Loads: consente di selezionare un gruppo di elementi in base ai carichi assegnati.
Figura 8.9 – Finestra di selezione elementi in base al Group Object di appartenenza
Manuale Utente HISTRA MENU PRINCIPALE
111
Figura 8.10 – Finestra di selezione elementi in base al Materiale assegnato
Figura 8.11 – Finestra di selezione elementi in base al Carico applicato
8.3 VIEW
Questo menu consente di modificare il modo di visualizzazione del modello. Inoltre comprende tutti i
comandi utili per migliorare la lettura grafica del modello nell'ambiente principale del programma, per
colorare gli elementi secondo i criteri desiderati, e per visualizzare, nel modo più efficace possibili, le
informazioni sugli oggetti del modello.
I comandi disponibili sono:
```
□ Number of views (cfr. § 8.3.1)
```
```
□ Geometric/Computational (cfr. § 8.3.2)
```
Manuale Utente HISTRA MENU PRINCIPALE
112
```
□ Show all (cfr. § 8.3.3)
```
```
□ Show only selected elements (cfr. § 8.3.4
```
```
□ Show only elements in group (cfr. § 8.3.5)
```
```
□ Hide selected elements (cfr. § 8.3.6)
```
```
□ Invert visibility (cfr. § 8.3.8)
```
```
□ View options (cfr. § 8.3.9 )
```
```
□ Color according to (cfr. § 8.3.10)
```
```
□ View direction (cfr. § 8.3.11)
```
8.3.1 Number of views
```
Questo comando consente di visualizzare contemporaneamente una o più viste (da una, a quattro viste)
```
del modello tridimensionale, nell’ambiente principale del programma.
Figura 8.12 – Number of views – visualizzazione a multi finestra.
8.3.2 Geometric/Computational
```
Questo comando consente di visualizzare alternativamente il modello (cfr. Figura 8.13) geometrico o
```
```
computazionale (cfr. Figura 8.14). E precisamente, viene visualizzato:
```
```
 il modello geometrico, se nella vista corrente è visualizzato il modello computazionale;
```
```
 il modello computazionale (tasti rapidi Alt+C), se nella vista corrente è visualizzato il modello geometrico.
```
Manuale Utente HISTRA MENU PRINCIPALE
113
Figura 8.13 – Vista del modello geometrico
Figura 8.14 – Vista del modello computazionale
8.3.3 Show all
Questo comando consente di visualizzare tutti gli elementi del modello, quindi gli elementi la cui visibi-
lità è stata nascosta.
8.3.4 Show only selected elements
Questo comando consente di visualizzare gli elementi del modello in selezione, e di nascondere tutti gli
altri.
8.3.5 Show only elements in groups
Questo comando consente di visualizzare solo gli elementi appartenenti a un gruppo.
Manuale Utente HISTRA MENU PRINCIPALE
114
8.3.6 Hide selected elements
Questo comando consente di aggiungere gli elementi del modello in selezione a quelli attualmente già
nascosti.
8.3.7 Show only elements in group
Questo comando consente di aggiungere gli elementi del modello in selezione a quelli attualmente già
nascosti.
8.3.8 Invert visibility
Questo comando consente di rendere invisibili gli elementi visualizzati nella finestra centrale e vice-
versa rendere visibili gli elementi di cui la visualizzazione è stata nascosta.
8.3.9 View options
Questo comando consente di modificare le opzioni di vista degli elementi costituenti il modello geome-
trico, il modello computazionale ed altri elementi del programma, quali assi locali/globali e linee di rife-
rimento. E' possibile accedere a questo comando anche attraverso l'opzione presente nella barra delle
informazioni.
Figura 8.15 – Schermata View options - opzioni di visualizzazione
Manuale Utente HISTRA MENU PRINCIPALE
115
Nella parte in basso a sinistra della finestra sono disponibili dei comandi che consentono di espan-
```
dere/comprimere (Expand/Collapses all groups) tutti i gruppi di opzioni di visualizzazione.
```
Per confermare le impostazioni delle opzioni di visualizzazione cliccare sul bottone Accept and close. Se
non si vogliono confermare le modifiche di visualizzazione apportate, cliccare sul comando Abort and
close, che consente di uscire senza salvare.
```
Per tutti gli elementi geometrici (Geometric Elements), nodi, aste pannelli, ponti, archi, volte. Vincoli
```
```
(line/point restraint o surface restaraint), etc., sono disponibili le seguenti opzioni, visibili espandendo
```
ciascun gruppo.
```
□ Visible: consente di nascondere o rendere visibile la tipologia di elemento considerata;
```
```
□ Color: consente di modificare il colore associato a quella tipologia di elemento;
```
□ Transparency: consente di regolare la trasparenza degli elementi associati a quella determinata tipolo-
gia.
Figura 8.16 - View options – Geometric Elements
```
Per gli elementi computazionali (Quad, Vertex, Truss, etc…) le opzioni disponibili sono le seguenti:
```
```
□ Visible: consente di nascondere o rendere visibile la tipologia di elemento considerata;
```
```
□ Extruded: consente di abilitare la vista estrusa (tridimensionale) o piatta degli elementi;
```
□ Shrink: consente di attivare o disattivare una modalità di vista in cui gli elementi sono leggermente
ritirati rispetto alle loro reali dimensioni, utile in alcuni casi per rendere la connessione tra elementi più
```
chiara;
```
```
□ Local axes: consente di rendere visibile o no la terna di assi locale per quella tipologia di elementi;
```
```
□ Color: consente di modificare il colore associato a quella tipologia di elemento;
```
□ Color according to: consente di colorare gli elementi di quella tipologia in base al colore selezionato per
```
la stessa tipologia o in base al materiale associato a ciascun elemento;
```
□ Transparency: consente di regolare la trasparenza degli elementi associati a quella determinata tipolo-
gia.
Manuale Utente HISTRA MENU PRINCIPALE
116
Figura 8.17 – View options – Computational Elements
```
L’ultima colonna Other (altri elementi) contiene le opzioni di visualizzazione dei carichi (Point Load, Line
```
```
Load e Area Load), quelle delle Linee di riferimento (Line reference), e altre opzioni generali (ambiente
```
```
principale di lavoro).
```
Le opzioni di visualizzazione per i carichi sono:
```
□ Visible: consente di nascondere o rendere visibile la tipologia di carico considerata;
```
```
□ Color: consente di modificare il colore associato a quella tipologia di carico;
```
```
□ Transparency: consente di regolare la trasparenza dei carichi associati a quella determinata tipologia;
```
□ Scale factor, consente di regolare l'amplificazione del fattore di scala dei carichi associati a quella tipo-
logia.
```
Figura 8.18 – – View options - Carichi (Area, Point, Line Load)
```
8.3.10 Color according to
Questo menu consente di gestire la visualizzazione degli elementi, secondo criteri diversi, che permet-
tono una verifica efficace della bontà delle assegnazioni effettuate durante la modellazione. Consente
di visualizzare i colori degli elementi costituenti il modello secondo le seguenti proprietà assegnate per:
```
□ Object > gli elementi vengono colorati proprietà degli oggetti;
```
```
□ Material > gli elementi che costituiscono il modello vengono colorati secondo i materiali assegnati;
```
```
□ AreaLoad > gli elementi che costituiscono il modello vengono colorati secondo i carichi di area assegnati;
```
□ LineLoad. > gli elementi che costituiscono il modello vengono colorati secondo i carichi di linea assegnati.
Manuale Utente HISTRA MENU PRINCIPALE
117
Figura 8.19 – Visualizzazione del modello e degli elementi, colorati in funzione dei materiali assegnati
8.3.11 View direction
Questo comando consente di selezionare il tipo di vista del modello nella finestra centrale, secondo le
preferenze dell’utente, tra le seguenti:
□ 3D
□ 3D-XY
□ 3D-YZ
□ 3D-XZ
□ Plane-XY
□ Plane-YZ
□ Plane-XZ
8.4 DEFINE
Dal menu Define si accede alla definizione delle principali proprietà degli elementi del modello
□ Material: definizione dei materiali. Vengono distinti i materiali per le murature, acciaio e calcestruzzo,
```
oltre il materiale elastico lineare (cfr. 8.4.1).
```
```
□ Load condition (cfr. § 8.4.2.1): avvia la finestra dei tipi di carico che si possono assegnare nel modello;
```
□ Load definition: avvia la finestra per la definizione dei seguenti carichi:
```
 Vehicle load (cfr. § 8.4.2.2);
```
```
 Area load (cfr. § 8.4.2.3);
```
```
 Line load (cfr. § 8.4.2.4);
```
```
□ Schema: avvia la finestra di definizione degli schemi di carico (cfr. § 8.4.3);
```
```
□ Load combination (cfr. § 8.4.3): avvia la finestra sulle combinazioni di carico;
```
□ Schema-Load combination definition: consente di associare ad ogni combinazione dei carichi, uno
```
schema di carico;
```
```
□ Analyses (cfr. § 8.4.5 ): avvia la finestra per la definizione delle analisi da eseguire.
```
```
□ Group Object: (cfr.0): consente di definire un gruppo di oggetti.
```
Manuale Utente HISTRA MENU PRINCIPALE
118
La definizione dei materiali avviene mediante finestre dallo schema ricorrente. In particolare l'area è
divisa in due parti. Nella parte destra verrà visualizzata la parte di definizione specifica per la tipologia
di elemento considerata. Nella parte sinistra è invece presente un pannello di controllo generale.
In particolare, in alto è presente un menu a tendina che consente di accedere a uno dei sottogruppi della
```
tipologia considerata (ad esempio carichi->carichi di linea/area/veicolari).
```
Subito sotto viene visualizzata la "lista degli elementi" definiti e la barra dei menu per introdurre o eli-
minare gli elementi in lista. Quando si seleziona uno degli elementi in lista la parte destra della finestra
verrà riempita con i dati corrispondenti.
Attraverso la "lista degli elementi" è possibile eseguire le seguenti operazioni:
```
□ definire un nuovo elemento col tasto ;
```
```
□ cancellare un elemento definito cliccando ;
```
```
□ copiare un elemento definito col tasto ;
```
```
□ modificare il nome di un elemento della lista (selezionando l'elemento ed editando il nome);
```
```
□ accedere alla scheda delle proprietà dell'elemento (selezionandolo in elenco);
```
```
□ impostare automaticamente o personalizzando i colori per ciascun elemento definito (selezionando dal
```
```
menu a tendina ).
```
8.4.1 Materiali
Da questo menu è possibile accedere alla definizione della tipologia di materiali. Per le singole finestre,
ciascuna delle quali fa riferimento a una specifica tipologia si rimanda a quanto già specificato nel ca-
```
pitolo dedicato alla procedura di modellazione tramite Wizard (v. § 6.2).
```
8.4.2 Definizione dei carichi
La definizione dei carichi comprende diverse sezioni, che consentono di definire i carichi che verranno
applicati sugli elementi strutturali del modello. È possibile accedere alla definizione delle “condizioni di
carico”, la cui definizione verrà ampiamente descritta nell’apposito paragrafo, ed è possibile accedere
```
alla finestra di definizione vera e propria dei carichi (Veicolari, di area, o di linea).
```
I carichi agenti sulla struttura possono essere definiti attraverso i seguenti comandi:
Manuale Utente HISTRA MENU PRINCIPALE
119
1. Condizioni di carico (cfr. § 8.4.2.1): insieme delle condizioni di carico elementari;
2. Carico veicolare (cfr. § 8.4.2.2): carico viaggianti lungo l'asse del ponte;
3. Carico di area (cfr. § 8.4.2.3): carico agente in modo uniforme su una superficie;
4. Carico di linea (cfr. § 8.4.2.4): carico agente in modo uniforme su un elemento linea;
5. Carico di punto (cfr. § 8.4.2.5): carico agente su un punto;
6. Carico di volta: carico agente sull’estradosso di una volta (non di specifica pertinenza di HISTRA BRID-
```
GES – disponibile solo per HISTRA Arches and Vaults).
```
Selezionando uno dei carichi dal menu Define, nella corrispondente finestra è presente sulla sinistra la
lista dei carichi definiti, che li elenca per tipologia, dal relativo menu a tendina.
8.4.2.1 Load condition
La finestra definisci condizioni di carico consente di definire le condizioni di carico elementari, utili per
poter assegnare rapidamente i coefficienti di combinazione dei carichi nell’ambito della definizione dei
carichi sugli elementi strutturali. Le condizioni di carico di default non possono essere rinominate, né eli-
minate e sono di seguito elencate:
□ Gravity: pesi propri degli elementi strutturali calcolate automaticamente da HISTRA.
□ Structural Dead: carichi permanenti derivanti da pesi strutturali, quali ad esempio, elementi secondari
non inseriti esplicitamente nel modello.
□ Not structural dead: carichi permanenti derivanti da elementi non strutturali.
□ Not structural dead CD: carichi permanenti derivanti da elementi non strutturali, dei quali si conosce
l'esatta intensità e l'esatta collocazione.
□ Variable: carichi variabili di tipo “antropico”, derivanti da una specifica destinazione d’uso della strut-
tura o di parti di essa.
□ Vehicle: azioni dovute ai veicoli, ovvero i carichi viaggianti.
Figura 8.20 – Finestra definisci condizioni di carico
Oltre a quelle sopra riportate possono essere aggiunte ulteriori condizioni di carico, personalizzate se-
condo le esigenze dell’utente. Tale necessità si può manifestare nel caso in cui si debbano introdurre
Manuale Utente HISTRA MENU PRINCIPALE
120
carichi di tipo diverso, rispetto a quelli elencati superiormente, quali ad esempio i carichi variabili da
neve, dove i coefficienti di combinazione sono comunque diversi rispetto a quelli definiti per i carichi
variabili di tipo “antropico” dalla normativa adottata.
I comandi disponibili per gestire le condizioni di carico aggiuntive sono:
```
□ Add: aggiunge una nuova condizione di carico;
```
```
□ Delete: elimina la condizione di carico selezionata;
```
```
□ Cancel: annulla le modifiche e chiude la schermata delle condizioni di carico;
```
□ Ok: chiude la finestra e salva le modifiche apportate.
Ciascuna condizione di carico aggiuntiva può essere personalizzata dall’utente, selezionando il tipo di
azione a cui appartiene tra quelle presenti nel menu Action:
8.4.2.2 Load definition > Vehicle Load
La schermata dei carichi veicolari, avviene tramite una tabella ove ciascuna riga consente l’inserimento
```
di una distinta voce di carico elementare, sulla singola ruota, associata ad una condizione di carico (v.
```
```
Figura 6.46).
```
Per la definizione dei carichi veicolari si rimanda al par. 6.3.2 della procedura guidata di input su HISTRA
BRIDGES.
Figura 8.21 – Esempio definizione carichi veicolari per ponte stradale.
Manuale Utente HISTRA MENU PRINCIPALE
121
8.4.2.3 Load definition > Area Load
La finestra riporta l’archivio dei carichi di area applicabili agli elementi Quad e Vertex. I parametri sono
contenuti in una tabella ove ciascuna riga consente l’inserimento di una distinta voce di carico elemen-
```
tare (peso proprio, variabile, etc…) associata ad una condizione di carico (8.4.2.1). Le colonne della tabella
```
consentono di specificare, per ogni voce di carico elementare, l’intensità del carico ed i coefficienti di
combinazione secondo la normativa adottata:
```
□ Name: il nome della voce di carico elementare (peso proprio, peso pavimento, peso tramezzi, carico ac-
```
```
cidentale, etc…).
```
□ Load Condition: è necessario indicare se la voce di carico elementare è di tipo “permanente” ovvero
“variabile” o selezionare una delle condizioni di carico definite dall’utente tra quelle descritte sopra.
□ Use Destination: nel caso in cui sia stato selezionato “variabile” nella colonna Load condition, è neces-
sario indicare la destinazione d’uso della struttura modellata. Ciò consente l’attribuzione dei coefficienti
di combinazione secondo la normativa italiana, che l’utente può sempre modificare cliccando nell’ap-
posita casella.
□ Direction: consente di selezionare la direzione di applicazione del carico.
□ Is Projected: se attivo, il carico di area viene proiettato sul piano medio orizzontale del quad, moltipli-
cando l’intensità del carico per il coseno dell’angolo compreso tra la direzione di carico e quella della
```
normale al piano medio del macro-elemento (Quad o Vertex).
```
□ Load Value: è il valore dell’intensità del carico espresso secondo le unità di misura selezionate dall’ap-
posito menu a tendina. Se il carico è “variabile” di default viene inserita l’intensità secondo la normativa
italiana in base alla destinazione d’uso della struttura. È possibile variare tale valore secondo le scelte
del progettista.
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
normativa italiana. Cliccando sui valori è possibile modificare tali coefficienti.
Figura 8.22 - Definizione dei Carichi di Area - Area Load
```
In generale, per assegnare un carico di area al piano medio degli elementi computazionali (Quad, Ver-
```
```
tex), bisogna selezionare l’elemento computazionale:
```
```
 Premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi;
```
Manuale Utente HISTRA MENU PRINCIPALE
122
 Selezionare il comando: Quad > Apply area load > LoadArea.
Il carico di area è assegnato al piano medio degli elementi computazionali.
Nota bene:
```
nel caso di strutture modellate con macro-elementi il cui piano medio risulta verticale (per cui la normale a tale
```
```
piano medio risulta orizzontale), e selezionando l'opzione “IsProjected” nella definizione dei carichi di area ed
```
```
assumendo il carico agente nella direzione gravitazionale (“Gravity” direction), ne consegue che l’applicazione
```
```
del carico di area a detti macro-elementi comporterà che l’intensità del carico risultante sarà pari a zero (indi-
```
```
pendentemente dal valore assegnato in archivio), in quanto il prodotto scalare tra la normale al piano medio
```
```
(orizzontale) e la direzione di carico (verticale) è pari a zero.
```
Figura 8.23 – Esempio Modello computazionale e piano medio elementi Quad.
Nel caso di modelli generati con il wizard per archi, al fine di rendere orizzontale il piano medio dei quad, sele-
zionare il modello geometrico e dal pannello delle proprietà dell’elemento “Arch”, deselezionare l’opzione
“IsQuadPlaneVertical”. In tal modo il modello sarà generato orientando i macroelementi in modo dal
Figura 8.24 – Modifica direzione del piano medio degli elementi Quad.
Manuale Utente HISTRA MENU PRINCIPALE
123
Figura 8.25 – Piano medio elementi Quad orizzontale.
```
a) b)
```
```
Figura 8.26 – a) Assegnazione di un carico di area ad una volta a botte;
```
```
b) Visualizzazione del carico di area assegnato (visualizzazione dei carichi appartenenti alla condizione di carico
```
```
selezionata)
```
Per rimuovere un carico di area occorre selezionare l’elemento caricato:
```
 Premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi;
```
 Cliccare Quad > Apply area load > Unload elements.
HISTRA BRIDGES
In HISTRA BRIDGES è possibile applicare i carichi di area sulla faccia del macro-elemento corrispondente
alla superficie carrabile selezionando le voci in archivio all’interno della tabella di definizione degli
schemi di carico come riportato nel paragrafo 8.4.3.
Manuale Utente HISTRA MENU PRINCIPALE
124
Figura 8.27 - Assegnazione dei carichi di area, nell'ambito della definizione degli Schemi di Carico
8.4.2.4 Load definition > Line Load
Analogamente a quanto esposto superiormente per i carichi di area, è possibile definire i carichi di linea
da assegnare alle linee passanti tra due nodi del modello, inserendo: nome e descrizione facoltativa del
carico, condizione di carico ed eventuale destinazione d’uso se si definisce un carico variabile, direzione,
intensità e coefficienti di combinazione.
Figura 8.28 - Definizione dei Carichi di Linea - Line Load
□ Name: il nome della voce di carico.
□ Load Condition: riporta la condizione di carico, tra quelle precedentemente definite. Va indicato se la
voce di carico è di tipo “permanente” ovvero “variabile”, etc.
□ Use Destination: nel caso in cui sia stato selezionato “variabile” nella colonna Load condition, è neces-
sario indicare la destinazione d’uso. Ciò consente l’attribuzione dei coefficienti di combinazione secondo
```
la normativa utilizzata (NTC2018). E’ possibile modificare i coefficienti di combinazione e personalizzarli,
```
cliccando sulla apposita casella.
Manuale Utente HISTRA MENU PRINCIPALE
125
□ Direction: consente di selezionare la direzione di applicazione del carico. Gravity rappresenta la dire-
```
zione della forza di gravità (lungo l’asse Z del sistema di riferimento globale).
```
□ Specific weight: è il peso specifico del materiale di riempimento che caratterizza il carico di volta.
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
normativa italiana. Cliccando sui valori è possibile modificare tali coefficienti.
Per assegnare un carico di linea bisogna selezionare l’elemento:
```
 selezionare l’elemento computazionale (quad)
```
 premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi
di linea
```
 cliccare Apply line load > LoadLine;
```
 selezionare i due nodi del quad che identificano i punti di estremità della linea lungo cui si distribuisce
il carico.
Per rimuovere un carico di linea occorre selezionare l’elemento:
```
 premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi;
```
 cliccare Apply line load > Unload elements.

```
 a)
```
```
b)
```
```
Figura 8.29 – a) Menu contestuale per l’assegnazione di un carico di linea; b) Applicazione e visualizzazione del un carico
```
di linea assegnato sulla volta
Manuale Utente HISTRA MENU PRINCIPALE
126
Figura 8.30 – Assegnazione di un carico di linea.
8.4.2.5 Load definition > Point Load
E’ possibile definire i carichi di punto, da assegnare in corrispondenza di un nodo del modello, inserendo:
nome e descrizione facoltativa del carico, condizione di carico ed eventuale destinazione d’uso, se si sta
definendo un carico variabile, direzione, intensità del carico, oltre ai coefficienti di combinazione.
Figura 8.31 - Definizione dei Carichi di Punto - Point Loads
□ Name: il nome della voce di carico elementare.
```
□ Load Condition: è necessario indicare la condizione di carico elementare tra quelle predefinite (ad
```
```
esempio il serpeggio, nei casi di carichi ferroviari).
```
□ Use Destination: nel solo caso in cui sia stato selezionato “variabile” nella colonna Load condition, è
necessario indicare la destinazione d’uso della struttura modellata. Ciò consente l’attribuzione automa-
tica dei coefficienti di combinazione, secondo la normativa italiana, che l’utente può comunque modifi-
care, cliccando nell’apposita casella o selezionando la voce “User”.
□ Type Load: tipo di carico
□ Direction: consente di selezionare la direzione di applicazione del carico.
Manuale Utente HISTRA MENU PRINCIPALE
127
□ Load Value: è il valore dell’intensità del carico espresso nell’unità di misura selezionate dall’apposito
menu a tendina. Se il carico è di tipo “variabile” di default viene inserita l’intensità secondo la normativa
italiana in base alla destinazione d’uso della struttura. È possibile modificare tale valore, secondo le
scelte del progettista.
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
normativa italiana. Cliccando sui valori è possibile editare tali coefficienti.
Per assegnare un carico concentrato bisogna selezionare l’elemento:
 premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi
```
di punto;
```
```
 cliccare Apply point load > LoadPoint;
```
 selezionare il punto da caricare.
```
Per rimuovere un carico concentrato occorre selezionare l’elemento caricato (cfr. Errore. L'origine ri-
```
```
ferimento non è stata trovata.):
```
```
 premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi;
```
 cliccare Apply point load > Unload elements.
Figura 8.32 – Visualizzazione di un arco caricato da una forza concentrata in sommità sulla sezione di chiave
8.4.2.6 Load definition > Voult Load
La definizione dei carichi viene eseguita specificando: nome e descrizione facoltativa del carico, condi-
zione di carico ed eventuale destinazione d’uso se si definisce un carico variabile, direzione, intensità
```
attraverso il peso specifico (la geometria del carico, che è l'altro parametro per determinare l'intensità
```
```
finale del carico, dipenderà dalla specifica assegnazione) e coefficienti di combinazione. Tuttavia in que-
```
sto caso è possibile definire una sola voce di carico e non cumularle.
Manuale Utente HISTRA MENU PRINCIPALE
128
Figura 8.33 – Schermata di definizione dei carichi di volta
□ Name: il nome della voce di carico. Nel caso di carichi di volta è possibile definire una sola voce di carico
elementare.
□ Load Condition: riporta la condizione di carico, tra quelle precedentemente definite. Va indicato se la
voce di carico è di tipo “permanente” ovvero “variabile”, etc.
□ Use Destination: nel caso in cui sia stato selezionato “variabile” nella colonna Load condition, è neces-
sario indicare la destinazione d’uso. Ciò consente l’attribuzione dei coefficienti di combinazione secondo
```
la normativa utilizzata (NTC2018). E’ possibile modificare i coefficienti di combinazione e personalizzarli,
```
cliccando sulla apposita casella.
□ Direction: consente di selezionare la direzione di applicazione del carico. Gravity rappresenta la dire-
```
zione della forza di gravità (lungo l’asse Z del sistema di riferimento globale).
```
□ Specific weight: è il peso specifico del materiale di riempimento che caratterizza il carico di volta.
□ Coefficienti di combinazione ψ0, ψ1, ψ2: visualizza i coefficienti di combinazione del carico secondo la
normativa italiana. Cliccando sui valori è possibile modificare tali coefficienti.
Per assegnare un carico da volta bisogna selezionare l’elemento:
```
 premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi;
```
```
 cliccare Apply vault load > LoadVault;
```
specificare l’altezza H del materiale da riempimento,
```
 settando l’opzione (Figura 69°):
```
```
o Relative e impostando H a partire dal piano d’imposta della struttura voltata;
```
o Absolute e impostando H a partire dalla quota zero del sistema di riferimento globale.
```
Per rimuovere un carico da volta occorre selezionare l’elemento caricato (cfr. Errore. L'origine riferi-
```
```
mento non è stata trovata.):
```
```
 premere il tasto destro del mouse per accedere al relativo menu contestuale di applicazione dei carichi;
```
 cliccare Apply vault load > Unload elements.
Per I carichi di volta è possibile
definire una sola voce di carico
Manuale Utente HISTRA MENU PRINCIPALE
129
```
a) b)
```
```
Figura 8.34 – a) Menu contestuale per l’assegnazione dell’altezza di riempimento di un carico da volta;
```
```
b) Visualizzazione del carico da volta assegnato ad una volta a botte e modifica del carico dal pannello delle pro-
```
prietà
Manuale Utente HISTRA MENU PRINCIPALE
130
8.4.3 Schema
Con questo comando si accede alla schermata di definizione degli Schemi di carico, in cui è possibile
gestire gli schemi di carico, riferiti ai carichi di tipo veicolare. Detti schemi individuano le condizioni di
```
carico più gravose, in funzione delle disposizioni (posizioni) dei carichi mobili, precedentemente definiti.
```
Come già visto per la definizione dei carichi, anche la finestra di definizione degli Schemi di carico pre-
senta una struttura ricorrente e familiare in ambiente HISTRA. In particolare l'area è divisa in due parti.
```
Nella parte a destra viene visualizzata la tabella (o le tabelle) di definizione, specifica per la tipologia di
```
```
elemento considerata (selezionata sulla griglia posta a sinistra).
```
Nella parte sinistra, invece, è presente un pannello di controllo generale, con l'elenco degli schemi di
carico definiti e dei comandi di gestione degli stessi.
Con riferimento alla parte a destra della finestra. per ciascuno schema di carico, occorre definire, nella
```
tabella in alto il carico presente su ciascuna parte del ponte (Banchina, corsia, etc.), siano essi carichi
```
```
mobili (Vehicle) o fissi (Area Load o Line Load). In corrispondenza di Banchine e Spazi non è consentito
```
assegnare carichi veicolari mobili. Nella tabella in basso, invece, vengono definite le posizioni dei carichi
viaggianti, per tutto lo sviluppo longitudinale del ponte.
Il Numero delle posizioni viene indicato nell'apposito campo "Number of position". Di default il pro-
gramma propone un numero di posizioni pari al numero delle sezioni significative del ponte stesso, ov-
```
vero in corrispondenza degli appoggi (spalle e pile) e della mezzeria delle campate.
```
Nella sottostante tabella vengono create tante righe quante sono il numero delle posizioni e per ciascun
carico veicolare assegnate le corrispondenti posizioni lungo l'asse longitudinale del ponte, espresse in
cm.
Figura 8.35 - Definizione degli Schemi di Carico - Schema
Manuale Utente HISTRA MENU PRINCIPALE
131
8.4.4 Load combination
Con questo comando si accede alla schermata delle combinazioni di carico, in cui è possibile gestire i
coefficienti amplificativi di carico associati ad ogni tipo di combinazione. Vengono distinte le combina-
zioni di carico sismiche e quelle non sismiche.
Le combinazioni di carico non sismiche sono quelle in cui la struttura è soggetta ad azioni statiche,
diverse da quella sismica, dovute cioè all’azione dei carichi gravitazionali, strutturali e non strutturali,
variabili e veicolari.
Tali analisi sono condotte per la verifica agli stati limite, ovvero per la valutazione dello stato di solle-
citazione della struttura, da tenere in conto come configurazione iniziale del modello in sede di analisi
sismica, in conformità a quanto prescritto dalla normativa adottata.
Le combinazioni di carico sismiche sono quelle in cui la struttura è soggetta ad una distribuzione di
```
forze orizzontali (proporzionali alla massa o al modo fondamentale di vibrazione dell’edificio nella di-
```
```
rezione di carico considerata), che hanno lo scopo di simulare, in maniera approssimata, l'azione del si-
```
sma. Tali forze, almeno nelle opzioni predefinite, sono determinate in proporzione ai carichi dell'analisi
di partenza che definisce la configurazione iniziale del modello.
Le combinazioni di carico previste dalle attuali normative ed impostate di default sono le seguenti:
□ SLU, di tipo:
o STR
o GEO
□ SLE, di tipo:
o Rara
o Frequente
o Quasi permanente
□ SISMICA
Queste combinazioni sono tuttavia personalizzabili, modificandone i coefficienti amplificativi delle
azioni, secondo le preferenze dell’utente e la normativa di riferimento.
Inoltre, nell'ambito delle SLU, tanto di tipo STR, che GEO, vengono generate più combinazioni, tante
```
quante sono le possibili permutazioni degli schemi di carico (creati per la definizione dei carichi veico-
```
```
lari), e delle rispettive posizioni che i carichi veicolari possono assumere, viaggiando lungo l'asse del
```
ponte.
Ad esempio, se sono stati definiti 2 schemi di carico e per ciascuno di essi 4 posizioni dei carichi viag-
gianti, si genereranno in totale 8 combinazioni di tipo SLU_STR, ed altrettante per SLU_GEO.
Inoltre, viene creata anche una combinazione denominata SLU_Base, sia di tipo STR che di tipo GEO,
nella quale non vengono considerati i carichi veicolari, ma solo quelli fissi, di tipo gravity, e variabili.
Manuale Utente HISTRA MENU PRINCIPALE
132
Figura 8.36 –Combinazioni di carico - Evidenziata la generazione di tutte le possibili comb. SLU.STR, legata a Schemi e
Posizione dei carichi veicolari
8.4.5 Analyses
La finestra di definizione delle analisi è composta da due parti:
```
 La tabella di riepilogo delle analisi, posta nella parte superiore;
```
 Le schede di definizione dei parametri delle analisi, posta nella parte centrale, permettono di caratteriz-
zare l’analisi selezionata nella tabella di riepilogo relativamente alla metodologia di analisi, ai parametri
```
di controllo, alle strategie di iterazione, ai criteri di convergenza e alle modalità di applicazione del carico;
```
 Toolbar dei comandi, posta nella barra inferiore.
Figura 8.37 – Finestra definizione analisi
Le analisi previste nel codice di calcolo di HISTRA si possono distinguere in:
Manuale Utente HISTRA MENU PRINCIPALE
133
```
 Analisi statiche non lineari, distinte in analisi a controllo di forza e analisi a controllo di spostamento;
```
 Analisi modale per il calcolo dei modi e frequenze di vibrare della struttura.
Le analisi statiche non lineari a controllo di forza sono basate sull’algoritmo di Newton-Raphson
```
ed assumono come criterio principale il raggiungimento di un fissato moltiplicatore dei carichi (rate of
```
```
load to be applied), valutato rispetto alla combinazione di carico prescelta. L’agoritmo di Newton-Raph-
```
son risolve iterativamente il seguente problema:
```
i id d  R K u1i id d u K R (1)
```
```
essendo:
```
int
i i
extd  R F F : vettore squilibrio calcolato nell’i-esima iterazione
```
extF : vettore di carico delle forze esterne applicate nel passo dell’analisi
```
```
int :
```
iF vettore delle forze interne reattive mobilitate nell’i-esima iterazione, calcolato mediante
l’applicazione del Principio dei Lavori Virtualiinti tV dv F B σ in funzione della risposta non li-
```
neare dei legami costitutivi( )σ ε quest’ultima valutata attraverso la predizione elastica dell’incre-
```
```
mento delle deformazioni locali( ) eld p d ε B u essendo eld d u C u l’incremento degli sposta-
```
menti locali dell’elemento computazionale,B la matrice di trasformazione contenente gli operatori dif-
ferenziali per il calcolo delle deformazioni valutato secondo l’approccio agli spostamenti, C la matrice
```
di congruenza edu il vettore degli incrementi degli spostamenti globali calcolato in (1); nota la predi-
```
```
zione elastica( )d pε si valuta l’incremento di tensione ed E d σ ε verificando la condizione di am-
```
```
missibilità plastica( ) 0eσ , essendo e ed σ σ σ ; nel caso di violazione della condizione di am-
```
```
missibilità plastica( ) 0eσ il solutore calcola la conseguente correzione plastica( )d f dσ ε e
```
la tensione plasticamente ammissibile d σ σ σ , viceversa eσ σ .
Le analisi statiche non lineari a controllo di spostamento sono basate sull’algoritmo di Arc
Length ed assumono come criterio principale il raggiungimento di un livello di spostamento in corri-
spondenza di un punto di controllo della struttura secondo la direzione individuata dall’analisi. . L’ago-
ritmo di Arc Length risolve iterativamente il seguente problema:
2
i i i
i i
d d
d d dr
   

 
R K u
u u
```
(2)
```
```
essendo:
```
int
i i
extd  R F F : vettore squilibrio calcolato nell’i-esima iterazione
```
extF : vettore di carico delle forze esterne applicate nel passo dell’analisi
```
```
int :
```
iF vettore delle forze interne reattive mobilitate nell’i-esima iterazione, calcolato come de-
scritto superiormente.
Manuale Utente HISTRA MENU PRINCIPALE
134
Le analisi a controllo di spostamento permettono la valutazione della massima capacità portante della
struttura poiché la stessa viene spinta fino al raggiungimento dello spostamento target in corrispon-
denza del punto di controllo, problema tipico delle analisi pushdown per la valutazione del moltiplica-
tore dei carichi di collasso come quelle per la valutazione della capacità portante di un ponte soggetto
all’azione da traffico.
Le analisi a controllo di spostamento possono essere utilizzate per la valutazione della vulnerabilità
sismica poiché permettono di calcolare la capacità di spostamento atteso ed il massimo valore del mol-
tiplicatore dei carichi che la struttura può sostenere rispetto ad una distribuzione di carico individuata
dalla combinazione prescelta ovvero rispetto ad una distribuzione di forze proporzionali ad un modo o
una combinazione di modi di tipo CQC.
Altri tipi di applicazioni sono le simulazioni numeriche di azioni cicliche imposte alla struttura me-
diante la definizione delle LoadFunctions che permettono di applicare un campo di spostamento ciclico.
Le analisi statiche non lineari possono essere automaticamente interrotte se la curva di carico subi-
sce una diminuzione in termini di forza in corrispondenza di una percentuale fissata attivando l’opzione
“Stop analysis if occours a load reduction”.
Le schede di definizione dei parametri permettono di caratterizzare l’analisi selezionata nella tabella
di riepilogo relativamente alla metodologia di analisi, ai parametri di controllo, alle strategie di itera-
zione, ai criteri di convergenza e alle modalità di applicazione del carico.
Di default nel software HISTRA Arches And Vaults sono previste le seguenti analisi:
□ Vert: analisi statica non lineare a controllo di forza del ponte soggetto ai carichi gravitazionali secondo
la combinazione sismica.
□ SLU_STR: analisi statica non lineare a controllo di forza della struttura soggetta ai carichi gravitazionali
ed a quelli dovuti all’azione di spinta delle terre, combinati secondo la combinazione SLU.STR.
□ SLU_GEO: analisi statica non lineare a controllo di forza della struttura soggetta ai carichi gravitazionali
ed a quelli dovuti all’azione di spinta delle terre, combinati secondo la combinazione SLU.GEO. Non sono
inclusi i carichi mobili. E' l'analisi di partenza per tutte le analisi di tipo SLU_GEO.
□ SLE_Rare: analisi statica non lineare a controllo di forza della struttura soggetta ai carichi gravitazionali,
```
adottando la combinazione rara (o caratteristica), impiegata generalmente per le verifiche agli Stati Li-
```
```
mite di Esercizio (SLE) irreversibili.
```
□ SLE_Frequent: analisi statica non lineare a controllo di forza della struttura soggetta ai carichi gravita-
zionali, adottando la combinazione frequente, impiegata generalmente per le verifiche agli Stati Limite
```
di Esercizio reversibili (SLE).
```
□ SLE_Quasi_Permanent: analisi statica non lineare a controllo di forza della struttura soggetta ai carichi
gravitazionali, adottando la combinazione quasi permanente, impiegata generalmente per le verifiche
```
agli Stati Limite di Esercizio, per gli effetti a lungo termine (SLE).
```
□ Pushover+X Mass: analisi statica non lineare a controllo di spostamento di tipo pushover della struttura
soggetta ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle X posi-
tive. Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
□ Pushover-X Mass: analisi statica non lineare a controllo di spostamento di tipo pushover della struttura
soggetta ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle X nega-
tive. Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
Manuale Utente HISTRA MENU PRINCIPALE
135
□ Pushover+Y Mass: analisi statica non lineare a controllo di spostamento di tipo pushover della struttura
soggetta ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle Y posi-
tive. Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
□ Pushover-Y Mass: analisi statica non lineare a controllo di spostamento di tipo pushover della struttura
soggetta ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle Y nega-
tive. Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
□ Pushover+X Modal: analisi statica non lineare a controllo di spostamento di tipo pushover della strut-
tura soggetta ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione
di modi di vibrare della struttura, secondo la direzione delle X positive. Richiede l’esecuzione preliminare
dell’analisi Vert da cui riparte e dell’analisi Modal.
□ Pushover-X Modal: analisi statica non lineare a controllo di spostamento di tipo pushover della strut-
tura soggetta ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione
di modi di vibrare della struttura, secondo la direzione delle X negative. Richiede l’esecuzione prelimi-
nare dell’analisi Vert da cui riparte e dell’analisi Modal.
□ Pushover+Y Modal: analisi statica non lineare a controllo di spostamento di tipo pushover della strut-
tura soggetta ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione
di modi di vibrare della struttura, secondo la direzione delle Y positive. Richiede l’esecuzione preliminare
dell’analisi Vert da cui riparte e dell’analisi Modal.
□ Pushover-Y Modal: analisi statica non lineare a controllo di spostamento di tipo pushover della strut-
tura soggetta ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione
di modi di vibrare della struttura, secondo la direzione delle Y negative. Richiede l’esecuzione prelimi-
nare dell’analisi Vert da cui riparte e dell’analisi Modal.
□ Modal: analisi dei modi e frequenze di vibrare della struttura.
Le analisi di default previste nel software HISTRA BRIDGES sono:
□ Vert: analisi statica non lineare a controllo di forza del ponte soggetto ai carichi gravitazionali secondo
la combinazione sismica.
□ SLU_STR_Base: analisi statica non lineare a controllo di forza del ponte soggetto ai carichi gravitazionali
ed a quelli dovuti all’azione di spinta delle terre, combinati secondo la combinazione SLU.STR. Non sono
inclusi i carichi mobili. E' l'analisi di partenza per tutte le analisi di tipo SLU_STR e SLU_STR_COLLAPSE.
□ SLU_STR: analisi statiche non lineari a controllo di forza del ponte soggetto ai carichi mobili, applicati
```
secondo la combinazione agli Stati Limite Ultimi di tipo strutturale (SLU.STR). In particolare verranno
```
eseguite tante analisi quante sono le possibili distribuzioni di carico individuate dagli schemi di carico
```
ed al numero di posizioni assunte dai carichi mobili (8.4.3). Richiede l’esecuzione preliminare dell’analisi
```
SLU_STR_BASE da cui riparte.
□ SLU_STR_COLLAPSE: analisi statiche non lineari a controllo di spostamento del ponte soggetto ai carichi
```
mobili, applicati secondo la combinazione agli Stati Limite Ultimi di tipo strutturale (SLU.STR) al fine di
```
determinare il moltiplicatore di carico che determina il collasso della struttura. In particolare verranno
eseguite tante analisi quante sono le possibili distribuzioni di carico individuate dagli schemi di carico
```
ed al numero di posizioni assunte dai carichi mobili (8.4.3). Richiede l’esecuzione preliminare dell’analisi
```
SLU_STR_BASE da cui riparte.
□ SLU_GEO_Base: analisi statica non lineare a controllo di forza del ponte soggetto ai carichi gravitazio-
nali ed a quelli dovuti all’azione di spinta delle terre, combinati secondo la combinazione SLU.GEO. Non
sono inclusi i carichi mobili. E' l'analisi di partenza per tutte le analisi di tipo SLU_GEO.
□ SLU_GEO: analisi statiche non lineari a controllo di forza del ponte soggetto ai carichi mobili, applicati
```
secondo la combinazione agli Stati Limite Ultimi di tipo geotecnico (SLU.GEO). In particolare verranno
```
eseguite tante analisi quante sono le possibili distribuzioni di carico individuate dagli schemi di carico
Manuale Utente HISTRA MENU PRINCIPALE
136
```
ed al numero di posizioni assunte dai carichi mobili (8.4.3). Richiede l’esecuzione preliminare dell’analisi
```
SLU_GEO_BASE da cui riparte.
□ SLE_Rare_Base: analisi statica non lineare a controllo di forza del ponte soggetto ai carichi gravitazio-
```
nali, adottando la combinazione rara (o caratteristica), impiegata generalmente per le verifiche agli Stati
```
```
Limite di Esercizio (SLE) irreversibili.
```
□ SLE_Rare: analisi statiche non lineari a controllo di forza del ponte soggetto ai carichi mobili, adottando
```
la combinazione rara (o caratteristica), impiegata generalmente per le verifiche agli Stati Limite di Eser-
```
```
cizio (SLE) irreversibili. In particolare verranno eseguite tante analisi quante sono le possibili distribu-
```
zioni di carico individuate dagli schemi di carico ed al numero di posizioni assunte dai carichi mobili
```
(8.4.3). Richiede l’esecuzione preliminare dell’analisi SLE_Rare_Base da cui riparte.
```
□ SLE_Frequent_Base: analisi statica non lineare a controllo di forza del ponte soggetto ai carichi gravi-
tazionali, adottando la combinazione frequente, impiegata generalmente per le verifiche agli Stati Li-
```
mite di Esercizio reversibili (SLE).
```
□ SLE_Frequent: analisi statiche non lineari a controllo di forza del ponte soggetto ai carichi mobili, adot-
tando la combinazione frequente, impiegata generalmente per le verifiche agli Stati Limite di Esercizio
```
reversibili (SLE). In particolare verranno eseguite tante analisi quante sono le possibili distribuzioni di
```
```
carico individuate dagli schemi di carico ed al numero di posizioni assunte dai carichi mobili (8.4.3). Ri-
```
chiede l’esecuzione preliminare dell’analisi SLE_Frequent_Base da cui riparte.
□ SLE_Quasi_Permanent_Base: analisi statica non lineare a controllo di forza del ponte soggetto ai carichi
gravitazionali, adottando la combinazione quasi permanente, impiegata generalmente per le verifiche
```
agli Stati Limite di Esercizio, per gli effetti a lungo termine (SLE).
```
□ SLE_Quasi_Permanent: analisi statiche non lineari a controllo di forza del ponte soggetto ai carichi mo-
bili, adottando la combinazione quasi permanente, impiegata generalmente per le verifiche agli Stati
```
Limite di Esercizio, per gli effetti a lungo termine (SLE). In particolare verranno eseguite tante analisi
```
quante sono le possibili distribuzioni di carico individuate dagli schemi di carico ed al numero di posi-
```
zioni assunte dai carichi mobili (8.4.3). Richiede l’esecuzione preliminare dell’analisi SLE_Quasi_Perma-
```
nent_Base da cui riparte.
□ Pushover+X Mass: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte sog-
getto ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle X positive.
Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
□ Pushover-X Mass: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte sog-
getto ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle X negative.
Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
□ Pushover+Y Mass: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte sog-
getto ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle Y positive.
Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
□ Pushover-Y Mass: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte sog-
getto ad una distribuzione di forze orizzontali proporzionali alla massa nella direzione delle Y negative.
Richiede l’esecuzione preliminare dell’analisi Vert da cui riparte.
□ Pushover+X Modal: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte
soggetto ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione di
modi di vibrare della struttura, secondo la direzione delle X positive. Richiede l’esecuzione preliminare
dell’analisi Vert da cui riparte e dell’analisi Modal.
□ Pushover-X Modal: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte
soggetto ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione di
modi di vibrare della struttura, secondo la direzione delle X negative. Richiede l’esecuzione preliminare
dell’analisi Vert da cui riparte e dell’analisi Modal.
Manuale Utente HISTRA MENU PRINCIPALE
137
□ Pushover+Y Modal: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte
soggetto ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione di
modi di vibrare della struttura, secondo la direzione delle Y positive. Richiede l’esecuzione preliminare
dell’analisi Vert da cui riparte e dell’analisi Modal.
□ Pushover-Y Modal: analisi statica non lineare a controllo di spostamento di tipo pushover del ponte
soggetto ad una distribuzione di forze orizzontali proporzionali ad un modo o ad una combinazione di
modi di vibrare della struttura, secondo la direzione delle Y negative. Richiede l’esecuzione preliminare
dell’analisi Vert da cui riparte e dell’analisi Modal.
□ Modal: analisi dei modi e frequenze di vibrare della struttura.
Per aggiungere / cancellare o copiare una analisi nella tabella, utilizzare rispettivamente i bottoni Add
/ Del e Copy posti nella Toolbar dei comandi, in basso a sinistra.
La tabella di riepilogo delle analisi riporta per ciascuna analisi i seguenti parametri editabili:
□ Name: nome per l’analisi sismica oppure non sismica.
□ Type analysis: tipo di analisi, se statica non lineare
□ Start from: Indica se l’analisi deve partire dall’ultimo step di un’altra analisi eseguita precedentemente.
Cliccando sulla casella appare un menu a tendina da cui è possibile selezionare l’analisi di restart, a par-
tire dalla quale si intende eseguire quella corrente. Selezionando Zero l’analisi parte dalla configura-
zione indeformata.
□ Load combo: combinazione di carico in archivio, definita nella finestra load combination.
□ Description: sintetica descrizione dell’analisi.
Per personalizzare i parametri dell’analisi è necessario selezionare una analisi in tabella e modificare i
valori dei parametri nelle schede subito in basso.
Nota bene: con particolare riferimento alle analisi sismiche, l’opzione Start From consente di avviare
l’analisi da uno stato di deformazione e di sollecitazione calcolato da un’alta analisi e consente di con-
```
siderare l’effetto della sollecitazione di compressione verticale agente sugli elementi murari (dovuta ai
```
```
carichi gravitazionali), ai fini della corretta valutazione della capacità portante della struttura durante
```
le analisi sismiche. Infatti, secondo il criterio di resistenza di Mohr-Coulomb, la tensione tangenziale
```
limite߬  ௨ cresce proporzionalmente con la tensione normale ߪ௡ (߬ ௨ ߪ + ܿ= ௡ ߮݊ܽݐ ). Pertanto è indispen-
```
sabile valutare tale incremento di resistenza ai fini di una corretta valutazione del meccanismo di col-
lasso e della capacità portante della struttura: per questo motivo le analisi di tipo sismico iniziano sem-
pre dall’ultimo step dell’analisi “Vert”.
8.4.5.1 Control parameters
La scheda “Control parameters” consente di definire i seguenti parametri relativi sia alla fase a controllo
di forza, che a quella a controllo di spostamento:
Manuale Utente HISTRA MENU PRINCIPALE
138
Figura 8.38 – Definizione analisi - Control para-
meters
□ Load control: rate of load to be applied: analisi a controllo di forza. Consente di impostare il valore
target, ossia la percentuale di carico da raggiungere nella analisi a controllo di forza.
□ Displacement control: target displacement: analisi a controllo di spostamento. Consente di impostare
```
lo spostamento ultimo (detto anche spostamento target), da raggiungere nella analisi a controllo di spo-
```
stamento.
□ Start also if previous analysis is not completed: se selezionato, consente di iniziare l’analisi anche se
la precedente non è stata completata.
□ Stop analysis if occours a load reduction to: indica la percentuale di riduzione della reazione vincolare.
```
(esempio: 0,8 = riduzione della reazione vincolare dell’80%).
```
□ Control point: consente di impostare il punto di controllo per monitorare lo spostamento raggiunto dalla
struttura durante l’analisi a controllo di spostamento. Il punto di controllo viene selezionato tra tutti i
```
Model points definiti (v. la scheda Model points)
```
```
o Id(1): Node (…): se selezionato imposta il punto di controllo su uno dei model point definiti. Il
```
```
nodo viene identificato dal proprio id; il punto di controllo di default coincide con il primo della
```
```
lista dei punti di controllo riportati nella omonima scheda (model points)
```
o Max displacement: se selezionato il solutore sceglierà automaticamente il punto di controllo
ossia il grado di libertà da monitorare in ciascun passo dell’analisi. Questa strategia viene
usualmente suggerita nel caso di analisi per carichi viaggianti e per analisi sismiche pushover.
□ Direction: indica il verso e la direzione dell’analisi. Sono disponibili tre modalità di definizione della
```
direzione:
```
```
o Simple: indicare solo la direzione, coerente con gli assi del sistema di riferimento globale;
```
```
o Cart.: caratterizzare la direzione, mediante le coordinate cartesiane;
```
o Polar: caratterizzare la direzione, mediante coordinate polari.
8.4.5.2 Iterative strategy
La scheda “Iterative Strategy” contiene le seguenti opzioni, relative al metodo numerico da utilizzare:
Manuale Utente HISTRA MENU PRINCIPALE
139
Figura 8.39 – Definizione analisi. - Iterative Strategy,
□ Integration method: metodo di integrazione numerica da utilizzare. Load control se il metodo di analisi
scelto è a controllo di forza, oppure Arc Length se il metodo di analisi è a controllo di spostamento.
□ Numerical method: scegliere il metodo di analisi al passo che deve eseguire il solutore tra i seguenti:
o Standard Newton Raphson: la matrice di rigidezza della struttura si aggiorna ad ogni iterazione
```
nel passo dell’analisi non lineare; questo metodo consente di ottenere maggiori velocità di con-
```
vergenza. Tuttavia non è incondizionatamente stabile poiché la matrice di rigidezza può diven-
tare singolare a causa delle non linearità raggiunte nel passo, impedendo la possibilità di risol-
```
vere il sistema lineare;
```
o Modified Newton Raphson: la matrice di rigidezza della struttura viene valutata in corrispon-
denza della configurazione indeformata e non si aggiorna nelle iterazioni. Questo metodo è
incondizionatamente stabile poiché la matrice di rigidezza non viene aggiornata, tuttavia de-
termina un aumento del numero di iterazioni necessarie al fine di ottenere la condizione di con-
vergenza richiesta, in tal caso è opportuno eseguire le analisi con il metodo di Line search, at-
tivando la seguente opzione di calcolo, al fine di ridurre il numero di iterazioni richieste.
```
□ Line search: attivando l’opzione è possibile scegliere dal menu a tendina le seguenti opzioni (vedi note
```
```
seguenti)
```
o Secant line search
o Regula-falsi line search
o Bisection line search
o Initial interpolated line search
□ Max number of iterations: consente di stabilire il massimo numero di iterazioni nel passo dell’analisi.
```
□ Switch to modified strategy when stiffness is lower than (percent) of is initial value: se attivata l’op-
```
zione consente di indicare la percentuale della rigidezza iniziale, al di sotto della quale il solutore modi-
fica il metodo numerico da Standard a Modified Newton-Raphson.
Nota sui metodi di Line Search
I metodi di Line Search consentono di aumentare la velocità di convergenza della soluzione fornita
dal metodo di Newton-Raphson. Solitamente l’incremento di spostamento dU fornito dal metodo di
Newton-Raphson individua una direzione ottimale al fine di ottenere la convergenza ma l’ampiezza del
vettore du potrebbe non conseguire tale risultato essendo troppo grande o troppo poco rispetto alla
condizione di convergenza definita. In tal caso è più economico calcolare il residuo per diversi valori di
du piuttosto che risolvere un nuovo sistema lineare al fine di ottenere un nuovo vettore dU. La proce-
dura di Line search consiste nel calcolare il valore ottimale dell’incremento di spostamento al fine di
Manuale Utente HISTRA MENU PRINCIPALE
140
minimizzare l’energia potenziale totale che risulta funzione dello spostamento totale cumulatou .
L’incremento di spostamento sarà pari a
1n n d   u u u
essendo la lunghezza adimensionalizzata dello step della procedura di Line Search che può essere
calcolato imponendo la condizione di stazionarietà dell’energia potenziale totale :
```
( ) 0td d 
```

   

u R
```
Si definisce la funzione( )  come
```
0 0 0
```
( ) ( )t
```
t
d d
d d
 


  

 
u R
u R
```
essendo:
```
1
0 0d d
 u K R : vettore incremento di spostamento calcolato nella prima iterazione di Line
search
0 int,0extd  R F F : vettore squilibrio calcolato all’inizio della prima iterazione di Line search
```
extF : vettore di carico delle forze esterne applicate nel passo dell’analisi
```
int,0 :F vettore delle forze interne reattive mobilitate all’inizio della prima iterazione di Line search,
I diversi algoritmi di Line search utilizzano diversi metodi di ricerca del valore della lunghezza dello step
```
 calcolato come radice dell’equazione ( ) 0  . Di seguito si riportano le procedure di calcolo.
```
Secant line search:
 00 1
0 1
/ nn n
n
while toll and Iterations MaxIterations  
 
 
   
 
Regula-falsi line search:
Manuale Utente HISTRA MENU PRINCIPALE
141
 

0
1
1 1 1
1 1 1
```
0; 1; ( ); ( )
```
/
```
( )
```
```
( 0) ,
```
```
( 0) ,
```
U L U U L L
n
U L Un U
L U
n L U n U n
n U L n L n
while toll and Iterations MaxIterations
if
if
       
 
   
 
    
    

  
  
   
 
  

    
    
Bisection line search:
 

0
1
1 1 1
1 1 1
```
0; 1; ( ); ( )
```
/
2
```
( 0) ,
```
```
( 0) ,
```
U L U U L L
n
L Un
n L U n U n
n U L n L n
while toll and Iterations MaxIterations
if
if
       
 
 
    
    

  
  
   
 

    
    
Secant line search:
 10 1
1
```
( )/ n n n
```
n n n
n n
while toll and Iterations MaxIterations    
 


  
    
 
Reference
M.A. Crisfield, "Nonlinear Finite Element Analysis of Solids and Structures, Volume 1:Essentials", Wiley,
1991.
La scheda Iterative Strategy, riporta nella parte destra i seguenti parametri
Nel caso in cui l’analisi è a controllo di forza
Manuale Utente HISTRA MENU PRINCIPALE
142
Figura 8.40 – Load control method – parametri specifici
□ Automatic load step: se attivato nel caso in cui non trova convergenza per eccessive iterazioni, riduce
```
il moltiplicatore dei carichi dividendolo per il fattore di riduzione fino a che non si trovi convergenza;
```
```
□ Max number of load reduction: numero massimo di riduzioni del moltiplicatore dei carichi;
```
□ Load factor reduction: fattore di riduzione del moltiplicatore dei carichi
```
Nel caso in cui l’analisi è a controllo di spostamento (Arc length)
```
Figura 8.41 – Arc length method – parametri specifici
□ Arch length ray, dr: ampiezza del raggio del metodo Arc length
□ Compute d as function of: menu a tendina da cui è possibile specificare i gradi di libertà da monitorare
nell’analisi di Arc length
```
o Control point selected (Displacement Control): l’analisi sarà eseguita incrementando il mol-
```
tiplicatore di carico in funzione dello spostamento del grado di libertà traslazionale del punto
```
di controllo selezionato, secondo la direzione specificata nella scheda “Control parameters”;
```
```
o Model points selected (Reduced Arch Length Method): l’analisi sarà eseguita incrementando
```
il moltiplicatore di carico in funzione dello spostamento risultante ottenuto come radice qua-
```
drata della somma dei quadrati (SRSS) degli spostamenti dei gradi di libertà traslazionali rela-
```
tivi i punti di controllo selezionati, secondo la direzione specificata nella scheda “Control pa-
```
rameters”;
```
```
o All degrees of freedom (Arch Length Method): l’analisi sarà eseguita incrementando il molti-
```
plicatore di carico in funzione dello spostamento risultante ottenuto come radice quadrata
```
della somma dei quadrati (SRSS) degli spostamenti dei gradi di libertà traslazionali di tutti i
```
nodi del modello, secondo la direzione specificata nella scheda “Control parameters”.
E’ inoltre possibile chiedere al solutore di modificare in maniera adattiva la lunghezza del raggio
```
dell’arch length dr (Arc lenght ray), durante l’analisi adottando le seguenti strategie.
```
Manuale Utente HISTRA MENU PRINCIPALE
143
□ Max load increment, dλ: selezionando questa opzione si chiede al solutore di modificare il valore del
raggio di arch length in modo tale da ottenere incrementi del moltiplicatore del carico dλ inferiori ri-
spetto al valore massimo fissato dλmax. Se si adotta una distribuzione di forze modali, è opportuno de-
selezionare questa opzione perché la risultante delle forze applicate risulta essere una frazione delle
masse applicate e l’uso di questa opzione determinerebbe una eccessiva riduzione del valore del raggio
di arc length.
□ Number of iterations desired: selezionando questa opzione si chiede al solutore di modificare il raggio
dell’arch length in modo tale da ottenere un numero di iterazioni inferiore al valore fissato.
8.4.5.1 Convergence Criteria
In questa scheda è possibile specificare il criterio di convergenza e la tolleranza da adottare nelle analisi
statiche non lineari. E’ bene precisare che la scelta del criterio di convergenza è un aspetto cruciale nel
risultato numerico. Una tolleranza troppo ampia può determinare il non soddisfacimento della condi-
zione di equilibrio rigorosamente soddisfatta adottando il criterio di convergenza nelle forze.
□ Tolerance: valore massimo dell’errore al di sotto del quale l’analisi trova la sua convergenza.
□ Force: selezionando questo criterio di convergenza l’analisi trova la sua convergenza quando la norma
del vettore residuo è inferiore alla tolleranza fissata
int
i i
extd tol  R F F
□ Displacement: selezionando questo criterio di convergenza l’analisi trova la sua convergenza quando
la norma del vettore incremento di spostamento è inferiore alla tolleranza fissata
i d tolu
□ Work: selezionando questo criterio di convergenza l’analisi trova la sua convergenza quando il lavoro
calcolato come prodotto del vettore residuo per il vettore incremento di spostamento è inferiore alla
tolleranza fissata
i id d tol R u
□ Max displacement: valore massimo dello spostamento in un grado di libertà traslazionale del modello
al di sopra del quale l’analisi viene interrotta per eccessivi spostamenti.
Nelle relazionii dR è il vettore residuoi du è il vettore incremento di spostamento calcolato nella ite-
razione i-esima
Manuale Utente HISTRA MENU PRINCIPALE
144
Figura 8.42 – Definizione analisi - Convergence Criteria
8.4.5.1 Model points
La scheda “Model points” riepiloga i punti di controllo del modello per l'analisi selezionata. La tabella
riporta la lista dei punti di controllo definiti. Nel caso in cui sia stata scelta l’opzione Model points selec-
```
ted (Reduced Arch Length Method) dal menu a tendina Compute d as function of (vedi sopra), è possi-
```
bile attivarli o disattivarli singolarmente per l’analisi selezionata attraverso il relativo checkbox situato
nella colonna ‘Active’.
Figura 8.43 – Scheda Model points
Per aggiungere punti di controllo a questa lista occorre definirli dall’ambiente principale, selezionando
l’elemento computazionale e dichiarando il nodo come punto di controllo nel pannello property. E’ anche
possibile definire come punto di controlo il baricentro o un nodo di un marco-elemento Quad o Vertex
```
(v. Figura 8.44 e Figura 8.45).
```
Manuale Utente HISTRA MENU PRINCIPALE
145
Figura 8.44 – Definizione di punti modello personalizzati.
Figura 8.45 – Model points – in evidenza il punto di controllo definito dall’utente.
8.4.5.1 Loads applied
La scheda “Loads applied” consente di visualizzare i valori dei coefficienti di combinazione relativi alla
combinazione di carico assegnata all’analisi. E’ opportuno segnalare che la combinazione di carico sele-
zionata in generale individua un gruppo di sotto-combinazioni.
Figura 8.46 – Scheda Loads applied
Manuale Utente HISTRA MENU PRINCIPALE
146
8.4.5.1 Load function
E’ possibile definire funzioni di carico, utili soprattutto per poter eseguire analisi monotone o di tipo
ciclico.
```
La funzione di carico è definita attraverso una serie di coppie di valori (pseudo-tempo e moltiplicatore
```
```
del carico) i cui valori sono introdotti mediante in input tabellare.
```
```
L’incremento di carico viene applicato alla serie di dati definiti in tabella rispetto al tempo (pseudo-time)
```
ovvero rispetto al moltiplicatore di carico secondo le opzioni di calcolo di seguito elencate.
□ Discretizzation by pseudo-time: scegliendo questa opzione la funzione di carico prevede incrementi
del moltiplicatore di carico funzione del valore del passo di discretizzazione nel tempo di analisi
```
(pseudo-time) definito tra gli istanti di tempo dichiarati nella tabella a fianco.
```
□ Discretizzation by load multiplier: scegliendo questa opzione la funzione di carico prevede incrementi
del moltiplicatore di carico costanti pari al valore imputatato nel parametro Max discretization.
□ Max discretization: valore del passo di discretizzazione nel tempo ovvero nel moltiplicatore di carico
□ Delete selected row: cancella la riga selezionata in tabella.
Nella parte destra della finestra è rappresentata graficamente la funzione di carico.
Figura 8.47 – Scheda Load function
Group Objects
Questo comando apre la finestra di definizione dei gruppi di oggetti. In ciascun gruppo possono essere
```
aggiunti oggetti aventi caratteristiche comuni, di cui si vuole (ad esempio) leggere la risposta (in termini
```
```
di spostamento o di forze, etc.) in fase di output.
```
Dopo aver creato il gruppo nell’elenco di sinistra, portarsi nella finestra a destra e aggiungere gli ele-
menti mediante il tasto Add Element.
E’ possibile creare i gruppi di oggetti e/o aggiungere gli oggetti selezionati attraverso la finestra di vi-
sualizzazione principale. In tal caso è necessario selezionare gli oggetti visualizzati nella vista corrente,
cliccare con il tasto destro del mouse e richiamare il comando “Add selected elements to Group” presente
nel menu contestuale. Cliccando sul comando “Add to new group” è possibile definire un nuovo gruppo
a cui assegnare gli oggetti selezionati.
Manuale Utente HISTRA MENU PRINCIPALE
147
```
Figura 8.48 – Finestra di definizione dei Gruppi di Oggetti (Group Objects).
```
Figura 8.49 – Comando per aggiungere oggetti ai ‘GroupObjects’.
```
Figura 8.50 – Comando per creare nuovi Gruppi di Oggetti (Group Objects).
```
8.5 DRAW
Dal menu Draw è possibile disegnare i seguenti elementi:
□ Line Reference: disegna linee di riferimento. Per disegnare una linea di riferimento, cliccare sul punto e
individuare la direzione utilizzando il mouse, quindi indicare la lunghezza espressa in cm. E’ possibile
```
anche indicare la direzione digitando Lunghezza < Angolo (es: 100<30) e cliccando su invio, indicando
```
lunghezza della linea in cm e l’angolo formato tra l’asse x del sistema di riferimento globale e la direzione
Manuale Utente HISTRA MENU PRINCIPALE
148
```
della linea che si vuole tracciare. Digitando invece la stringa: @Lunghezza<Angolo (es: @100<30) è pos-
```
sibile considerare il sistema di riferimento relativo all'ultimo punto cliccato.
□ Restraint: consente di definire i vincoli di punto, di linea e di superficie. Per disegnare un vincolo di punto
basta selezionare un nodo. Per disegnare un vincolo di linea, selezionare primo e secondo nodo, che
individuano una linea. Per definire un vincolo di superficie, selezionare in successione tutti i nodi che
racchiudono la superficie che si vuole vincolare.
□ Computational elements: consente di disegnare elementi computazionali quali
o Quad: macro-elementi a quattro nodi deformabili a taglio
o Vertex: macro-elementi a tre nodi non deformabili a taglio
o Solid: macro-elementi a 8 nodi non deformabili a taglio
```
o Truss: elementi finiti tipo truss (pendolo) unidirezionali, con resistenza a compressione even-
```
tualmente limitata.
Figura 8.51 – Menu DRAW.
Figura 8.52 – DRAW.> Computational Elements.
8.6 EDIT
Dal menu Edit è possibile disegnare i seguenti elementi:
□ Distance: misura distanza lineare tra due punti. Selezionare due punti nell’ambiente principale del pro-
gramma. Il valore sara’ riportato nella barra delle informazioni in basso a sinistra.
□ Area: selezionare i punti di una maglia e cliccare col tasto destro del mouse. Selezionare il tasto Fet area
measurement dal menu contestuale. Il valore numerico dell’area selezionata verrà riportato nella barra
delle informazioni in basso a sinistra.
Figura 8.53– Menu EDIT
Manuale Utente HISTRA MENU PRINCIPALE
149
Figura 8.54– Edit > Distance
Figura 8.55– Edit > Area measurement.
Manuale Utente HISTRA MENU PRINCIPALE
150
8.7 RUN
Attraverso il comando Run posto sulla barra del menu principale, si accede alla finestra per l’avvio del
solutore e la selezione delle analisi da eseguire. Essa è composta da:
```
□ toolbar di comando (cfr. 8.7.1);
```
```
□ tabella di selezione delle analisi da eseguire (cfr. 8.7.2);
```
```
□ log di output delle analisi (cfr. 8.7.3);
```
```
□ anteprima della curva di carico (cfr. 8.7.4);
```
```
□ grafici dell’errore;
```
Figura 8.56 – Schermata di selezione delle analisi da eseguire
```
Durante l'esecuzione delle analisi vengono mostrate le curve di carico, il grafico dell’errore (Error value
```
```
at each iteration), il grafico delle forze esterne e interne rappresentato per ogni grado di libertà del mo-
```
```
dello (Error at each DOF); durante l’esecuzione delle analisi è possibile visualizzare la configurazione
```
deformata del modello e le mappe di colore del campo nella finestra principale. Il grafico dell’errore rap-
presentato in basso a destra consente la valutazione del grado di convergenza dell’analisi: l'analisi con-
```
verge quando l’errore è inferiore alla tolleranza fissata (v. Finestra di definizione delle analisi). Pertanto
```
```
se l’analisi converge allora il grarfico dell’errore diviene monotono e tendente a zero (v. Figura 8.57).
```
Eventuali oscillazioni del grafico dell’errore possono essere causate dalla non linearità del modello in
particolare quando si determinano eventi di rottura associati alla perdita di resistenza. Viceversa se il
grafico dell’errore diventa divergente vuol dire che non è possibile determinare una configurazione che
soddisfa il criterio di convergenza adottato.
Toolbar di comando
Tabella di selezione delle
analisi Anteprima della curva
di carico
Log di output delle analisi
Grafico dell’errore
Selettore rapido
delle analisi
Manuale Utente HISTRA MENU PRINCIPALE
151
Figura 8.57 – Finestra di esecuzione delle analisi e visualizzazione del modello tridimensionale.
Al termine dell'esecuzione delle analisi, la barra in basso assume il colore arancione e riporta l’esito delle
```
analisi eseguite (v. Figura 8.57).
```
8.7.1 Toolbar dei comandi
Il menu di avvio delle analisi, posto nella parte alta a sinistra della finestra, permette all’utente l’avvio
l’arresto del solutore. Sono presenti i seguenti comandi
```
□ Run: avvia il solutore ed esegue le analisi selezionate;
```
□ Stop: arresta il solutore ed interrompre l’esecuzione delle analisi salvando anche i risultati calcolati
```
nell’analisi in corso;
```
□ Continue: interrompre l’esecuzione dell’analisi corrente salvando i risultati calcolati nell’analisi in corso
```
ed avvia l’analisi successiva da eseguire tra quelle selezionate;
```
```
□ Maximize: allarga la finestra e rende visibile il log di output delle analisi;
```
```
□ Minimize: riduce la finestra e nasconde il log di output delle analisi;
```
```
□ Over: imposta la finestra in primo piano;
```
```
□ Below: imposta la finestra in secondo piano;
```
□ Quick selector: selettore rapido delle analisi da eseguire.
8.7.2 Tabella di selezione delle analisi
In tale riquadro è possibile scegliere le analisi che si intendono eseguire. La selezione delle analisi da
eseguire può essere effettuata mediante i tasti di scelta “rapida” presenti nel menu di avvio analisi, op-
pure alternativamente l’utente può selezionare singolarmente ciascuna analisi in modo distinto ed
esclusivo.
Manuale Utente HISTRA MENU PRINCIPALE
152
Le colonne del riquadro ambiente di selezione, riportano a partire da sinistra verso destra:
```
□ Execute, comando per selezionare quelle analisi da eseguire;
```
```
□ Analysis, riporta il nome delle analisi da eseguire;
```
```
□ Type: riporta il tipo di analisi ed il metodo numerico;
```
```
□ Start from, riporta il nome dell'analisi da cui riparte l'analisi da eseguire; assume valore "Zero" qualora
```
```
l'analisi debba avviarsi dalla configurazione indeformata iniziale;
```
```
□ State, indica lo stato di esecuzione delle analisi;
```
□ Details, descrizione dell'analisi.
8.7.3 Log di output delle analisi
Nel riquadro di output vengono riportati tutti i messaggi riguardanti lo stato di esecuzione dell’analisi
corrente. Questo riquadro riporta inoltre utili informazioni sul progresso dell’analisi e sull’eventuale rag-
giungimento della convergenza ovvero le informazioni sul tipo di criterio che ha comportato l’interru-
```
zione dell’analisi (labilità, eccessivo numero di iterazioni in un passo, eccessivi spostamenti).
```
8.7.4 Anteprima della curva di carico
Nel riquadro di anteprima della curva di carico vengono visualizzate le curve di carico della struttura in
termini di risultante delle forze applicate e spostamento del punto di controllo secondo la direzione
dell’analisi.
8.8 RESPONSE
Il menu Response consente di visualizzare la risposta del modello. I comandi disponibili sono:
□ Deformed shape: Visualizza la struttura in configurazione deformata.
```
□ Displacement in global direction: Visualizza gli spostamenti in termini assoluti (ovvero la risultante
```
```
delle componenti di spostamento), o relativi (in ciascuna delle tre direzioni del sistema di riferimento
```
```
gobale).
```
```
□ Stress/Strain: restituisce la risposta in termini di tensioni e deformazioni per elementi quad (cfr. § 8.8.1);
```
```
□ Interface: (cfr. § 8.8.2);
```
```
□ Truss (cfr. § 8.8.3);
```
□ Arch element response
```
□ Plot pushover-curve F-U: restituisce la curva push-over in termini di Forza / Spostamento (cfr. § 8.8.4);
```
□ Plot push-over curve λ-U: restituisce la la curva push-over in termini di moltiplicatore dei carichi / Spo-
```
stamento (cfr. § 8.8.4);
```
```
□ Plot response curve (cfr. § 8.8.5);
```
□ Influence line
□ Advanced options
La legenda, presente nel pannello a sinistra della finestra principale, riporta i valori degli spostamenti in
base alla scala colorimetrica.
Manuale Utente HISTRA MENU PRINCIPALE
153
Per poter visualizzare la risposta occorre, prima di tutto, selezionare l'analisi desiderata, mediante la combo-
```
box disponibile sulla sinistra, all'interno del riquadro "Responce", presente nel Menu dei comandi rapidi (v.
```
```
Figura 8.58).
```
Figura 8.58 – Selezione dell'analisi e visualizzazione della risposta a video
Selezione analisi
Visualizzazione della
curva di carico
Manuale Utente HISTRA MENU PRINCIPALE
154
Figura 8.59 – Menu Response
Figura 8.60 – Response – Visualizzazione della risposta in termini di spostamenti
8.8.1 Stress / Strain
Response > Stress / Strain
I comandi presenti in questo menu sono:
□ Diagonal link phase: consente di visualizzare la fase delle molle diagonali degli elementi quad.
```
□ Show pressure curve in arch elements;
```
□ Quad spring diagonal.
□ Color map of diagonal link phase > riporta in scala colorimetrica, sul modello la fase delle molle diagonali
```
(elastica, plastica, etc.)
```
□ Color map of stress in dir. 1, 2 > per ciascuna direzione del sistema di riferimento locale dei quad che
costituiscono il modello computazionale, viene rappresentata la mappa colorimetrica delle tensioni su-
```
gli elementi quad (v. Figura 8.61).
```
□ Color map of strain in dir. 1, 2 > per ciascuna direzione del sistema di riferimento locale dei quad che
costituiscono il modello computazionale, viene rappresentata la mappa colorimetrica, delle deforma-
zioni degli elementi quad.
Legenda e scala colorimetrica
Visualizzazione della risposta in termini di
spostamenti
Manuale Utente HISTRA MENU PRINCIPALE
155
□ Color map of plastic strain > per ciascuna direzione del sistema di riferimento locale dei quad che costi-
tuiscono il modello computazionale, o in termini assoluti, viene rappresentata la mappa colorimetrica
delle deformazioni plastiche sugli elementi quad.
□ Color map of ratio plastic strain > per ciascuna direzione del sistema di riferimento locale, dei quad che
costituiscono il modello computazionale, o in termini assoluti, viene rappresentata, la mappa colorime-
trica del rapporto up/ur.
Figura 8.61 – Visualizzazione della risposta in termini tensioni sugli elementi quad
8.8.2 Interface
Response > Interface
I comandi presenti in questo menu sono:
□ Transversal stress: permette di visualizzare la risposta delle molle flessionali delle interfacce in termini
di tensioni mediante apposita mappa dei colori. Il riquadro Legend, posto a sinistra nella toolbar dei
comandi rapidi, riepiloga i valori di tensione associati alla mappa dei colori
□ Sliding stress: consente di visualizzare la risposta delle molle a scorrimento "Sliding" delle interfacce,
disposte lungo il lato degli elementi connessi, in termini di tensioni mediante apposita mappa dei colori.
Il riquadro Legend, posto a sinistra nella toolbar dei comandi rapidi, riepiloga i valori di tensione asso-
```
ciati alla mappa dei colori;
```
□ Out of plane sliding stress: consente di visualizzare la risposta delle molle a scorrimento "Out of plane
sliding" delle interfacce, disposte perpendi-colarmente al lato degli elementi connessi, in termini di ten-
sioni mediante apposita mappa dei colori. Il riquadro Le-gend, posto a sinistra nella toolbar dei comandi
rapidi, riepiloga i valori di tensione associati alla mappa dei colori.
```
□ Transversal | Out of plane sliding | Slid out of plane phase: (cfr. § 8.8.2.1).
```
8.8.2.1 Transversal Phase, Sliding Phase, Out Of Plane Sliding Phase
Response > Interface > Transversal Phase | Sliding Phase | Out Of Plane Sliding Phase
Questi comandi consentono di visualizzare la fase delle molle delle interfacce mediante apposita mappa
dei colori. Le molle di interfaccia possono trovarsi nelle seguenti fasi:
```
 fase elastica;
```
Manuale Utente HISTRA MENU PRINCIPALE
156
```
 fase plastica a trazione/compressione;
```
```
 fase di scarico a trazione/compressione;
```
```
 fase di ricarico a trazione/compressione;
```
 fase di rottura a trazione/compressione.
Il riquadro Legend, posto a sinistra nella toolbar dei comandi rapidi, riepiloga le colorazioni assunte dalle
interfacce in funzione delle fasi delle molle.
In particolare:
```
□ Transversal Phase: colora le interfacce in funzione della fase delle molle flessionali;
```
□ Sliding Phase: colora le interfacce secondo la fase delle molle a scorrimento disposte lungo il lato degli
```
elementi connessi;
```
□ Out Of Plane Sliding Phase: colora le interfacce secondo la fase delle molle a scorrimento disposte per-
pendicolarmente al lato degli elementi connessi.
8.8.2.2 Risposta delle molle di interfaccia
Menu contestuale > Interface >Transversal links response | Sliding links response | Out of plane sliding links response
Per visualizzare la finestra della risposta delle molle di interfaccia, selezionare un’interfaccia e, cliccando
sul tasto destro del mouse, selezionare il comando Interface > Transversal links response.
La finestra di visualizzazione della risposta delle molle di interfaccia, riporta i seguenti riquadri:
 a sinistra è presente il riquadro di visualizzazione della mesh in cui è discretizzata l’interfaccia, da cui è
```
possibile selezionare e leggere il valore di tensione di ciascuna molla di interfaccia;
```
 a destra è presente il riquadro di visualizzazione della risposta della molla di interfaccia selezionata, da
cui è possibile:
```
o selezionare l'analisi e lo step di carico rispetto a cui viene restituita la risposta visualizzata;
```
```
o le informazioni del tipo di molla selezionata;
```
o la curva di carico della molla selezionata in termini di forza-spostamento e, per le molle a scor-
rimento con legame alla Coulomb e con legame alla Turnsek & Cacovic, in termini di forza F e
```
sforzo normale N;
```
o Show backbone curve, cliccando su questo bottone è possibile visualizzare la curva scheletro
in termini di forza-spostamento che caratterizza il legame il legame costitutivo assegnato alla
molla e, per le molle a scorrimento con legame alla Coulomb e con legame alla Turnsek & Ca-
```
covic, il dominio di resistenza in termini di forza F e sforzo normale N;
```
o Show table, cliccando su questo bottone è possibile visualizzare la tabella che riepiloga la ri-
```
sposta della molla per tutti gli step di analisi;
```
Manuale Utente HISTRA MENU PRINCIPALE
157
Figura 8.62 - Finestra di visualizzazione della risposta delle molle di interfaccia: curva di carico
Figura 8.63 - Finestra di visualizzazione della risposta delle molle di interfaccia: tabella della risposta
Ciascun grafico dispone dei seguenti comandi:
```
 Zoom all;
```
```
 Axis limits, cliccando su questo bottone è possibile regolare i limiti del grafico;
```
 Export data to excel, consente di esportare in excel i valori delle coordinate delle curve visualizzate.
8.8.3 Truss
Response > Truss
Questo menu consente di verificare la risposta di un elemento truss in termini di:
Manuale Utente HISTRA MENU PRINCIPALE
158
□ Stress: consente di visualizzare la risposta dei truss in termini di tensioni mediante apposita mappa dei
colori. Il riquadro Legend, posto a sinistra nella toolbar dei comandi rapidi, riepiloga i valori di tensione
associati alla mappa dei colori.
□ Strain: consente di visualizzare la risposta dei truss in termini di deformazione mediante apposita
mappa dei colori.
□ Force: consente di visualizzare la risposta dei truss in termini di sforzo normale mediante apposita
mappa dei colori.
□ Displacement: consente di visualizzare la risposta dei truss in termini di allungamento mediante appo-
sita mappa dei colori.
8.8.4 Plot push-over curve F-U / λ-U
Response > Plot push-over curve F-U | Plot push-over curve λ-U
Questo comando consente di visualizzare le curve di carico. La schermata si suddivide in due riquadri
```
principali: nel riquadro di sinistra viene mostrata la curva in termini di forza-spostamento; nel riquadro
```
di destra sono riportate in una tabella le coordinate della curva di carico, per il tipo di analisi selezionata
dal menu a tendina il alto a destra.
```
Ricordiamo che nel caso dei ponti, a ciascuna analisi non sismiche di tipo SLU (STR e GEO) corrisponde
```
una specifica combinazione dei carichi veicolari, in funzione dello schema di carico e della posizione
degli stessi, come prescritto dalle norme vigenti.
La curva di capacità è visualizzabile in termini di moltiplicatore dei carichi λ attraverso il tasto Show
λ/Disp curve, in cui si riporta nelle ordinate la forza adimensionalizzata al peso proprio della struttura.
Figura 8.64 – Curva di push-over F-U
Manuale Utente HISTRA MENU PRINCIPALE
159
Figura 8.65 – Curva di push-over in termini di moltiplicatore dei carichi -spostamento λ-U
Cliccando sul bottone Show λ/Disp curve, è possibile visualizzare la curva di capacità in termini di mol-
tiplicatore dei carichi - spostamento. Si può ritornare alla curva di push-over in termini di forza cliccando
il tasto Show Force/Disp curve.
I grafici di cui sopra dispongono dei seguenti comandi:
```
 Zoom all;
```
```
 Axis limits, cliccando su questo bottone è possibile regolare i limiti del grafico;
```
```
 Export data to excel, consente di esportare in excel i valori delle coordinate delle curve visualizzate;
```
```
 Visualizza la curva rappresentando i valori delle coordinate X in valore assoluto;
```
 Visualizza la curva rappresentando i valori delle coordinate Y in valore assoluto.
8.8.5 Plot response curve
Response > Plot push-over curve F-U | Plot response curve
Questo comando consente di visualizzare curve di risposta personalizzate attraverso grafici in cui è pos-
sibile riportare negli assi cartesiani lo spostamento di un punto di controllo, la reazione vincolare in ter-
mini di risultante di tutti i vincoli definiti nel modello ovvero lo spostamento di un nodo o di un macro-
elemento, la reazione vincolare di un gruppo di vincoli. In questi ultimi casi è necessario definire un
```
gruppo di oggetti (Group Objects) al fine di visualizzare la risposta della porzione di struttura che si in-
```
```
tende osservare (vedi 0).
```
. La schermata si suddivide in due riquadri principali: nel riquadro di sinistra viene mostrata la curva in
```
termini di forza-spostamento; nel riquadro di destra è possibile scegliere i parametri da visualizzare
```
sull’asse delle ascisse e delle ordinate. La scelta dei parametri avviene mediante due tabelle che con-
tengono i seguenti comandi.
Manuale Utente HISTRA MENU PRINCIPALE
160
```
 Parameter: parametro da rappresentare (Time, Step, Displacement, Force, λ, Total energy, Plastic energy,
```
```
Elastic energy, Inertial enery, Damping energy);
```
```
 Group: permette la selezione del gruppo di elementi computazionali (vedi §4.4.5 Group Object) rispetto
```
```
a cui si intende visualizzare la risposta (valore di default Model);
```
 Element: tipo di elemento contenuto nel gruppo selezionato, rispetto a cui si intende visualizzare la ri-
```
sposta;
```
 Direction: componente del parametro rispetto al sistema di riferimento globale. Selezionando “Total” si
```
intende ottenere la radice quadrata della somma dei quadrati (SRSS) delle componenti relative al para-
```
```
metro di risposta selezionato;
```
 ModelPoint: punto di controllo rispetto a cui si intende visualizzare la risposta del parametro selezio-
nato.
Figura 8.66 – Finestra “Plot Response Curve”
Manuale Utente HISTRA MENU PRINCIPALE
161
8.8.6 Plot Influence Line
Response > Plot push-over curve F-U | Plot response curve
```
Questo comando (disponibile solo su HISTRA BRIDGES) apre la finestra di visualizzazione della risposta
```
in termini di linee di influenza. Le linee di influenza rappresentano il valore del moltiplicatore dei carichi
di collasso al variare della posizione del carico mobile, ovvero lo spostamento di un nodo o di un macro-
elemento o la reazione vincolare di un gruppo di vincoli. In questi ultimi casi è necessario definire un
```
gruppo di oggetti (Group Objects) al fine di visualizzare la risposta della porzione di struttura che si in-
```
```
tende osservare (vedi 0).
```
Figura 8.67 – Finestra “Influence Lines” per la visualizzazione delle linee di influenza
Manuale Utente HISTRA MENU PRINCIPALE
162
8.9 CHECKS
Tramite il comando Tables, disponibile dal menu Report, è possibile visualizzare ed esportare in excel i tabulati
di calcolo, relativi alle analisi eseguite. Queste ultime sono selezionabili nel riquadro a sinistra. I tabulati da espor-
tare vanno invece selezionati nel riquadro a destra.
E' possibile aggiungere analisi o step di analisi alla lista riportata a sinistra, selezionando l'analisi e il passo desi-
derato e cliccando sul tasto "Add".
8.10 REPORT
Dal menu Report sono disponibili due voci:
- Word Reports disponibile per Histra A&V e per Histra Bridges solo limitatamente ai ponti ferroviari
```
che consente di selezionare ed esportare su file (in formato editabile compatibile con Microsoft
```
```
Word®) le relazioni di calcolo e I tabulati di input e di output generati dal software Histra®.
```
- Excel Tables, che consente di visualizzare ed esportare in excel i tabulati di calcolo, relativi alle
analisi eseguite.
Figura 8.68 – Menu Report
8.10.1 Word Reports
Report > Word Reports
```
Questo comando (disponibile per HISTRA BRIDGES solo limitatamente ai ponti ferroviari) apre la finestra
```
di selezione e generazione degli elaborati che è possibile ottenere in output. Ed esattamente:
```
 General Report - Relazione Generale (o di calcolo)
```
 Input Tables - Tabulati di input
 Output Tables - Tabulati di output
Manuale Utente HISTRA MENU PRINCIPALE
163
Figura 8.69 – Finestra principale per gestire Reports - tabulati e relazione di calcolo.
La finestra è così composta:
 Menu principale in alto
 Group box di selezione delle Analisi e Stati limite da inserire nelle relazioni e nei tabulati
in alto a sinistra
 Group box di visualizzazione dell’elenco delle analisi e stati limite aggiunti in basso a sin-
istra
 Schede dei tabulati e delle Relazioni a destra
Vengono a presso descritti i contenuti dei gruppi di elaborati ottenuti in output:
```
□ General Report: La relazione generale (o di calcolo) rappresenta il docu-
```
mento di sintesi in cui viene descritta la struttura oggetto di studio, i parti-
colari di modellazione, le analisi eseguite ed i risultati ottenuti in termini di
curve di capacità di stima di vulnerabilità sismica e di indici di vulnerabilità
sismica, nonché le relative deformate con gli indicatori di danno.
□ Input Tables: contengono tutti i dati caratteristici del modello quali la geo-
metria, i materiali, i carichi, gli schemi di cario e le analisi da eseguire, ecc.
```
□ Output Tables: contengono tutti i dati e le tabelle di output (spostamenti,
```
```
sollecitazioni, scarichi ai vincoli, ecc…), relativi a ciascun passo e analisi se-
```
lezionati. A differenza dei dati di input e della relazione, i gruppi di tabulati
Manuale Utente HISTRA MENU PRINCIPALE
164
```
di output possono essere molteplici. Il programma (se si seleziona dal grpup
```
box di selezione di analisi e passo, la voce Tutte le analisi e Tutti gli Stati
```
limite) ne genera in automatico uno per ciascuno stato limite e per ciascuna
```
```
analisi; tuttavia l’utente può personalizzarli.
```
```
In ciascuna scheda viene riportato l’elenco (o indice) dei reports generati. Ciascun documento (Relazione
```
```
generale di Calcolo, Tabulati di Input, Tabulati di Output) è suddiviso in più capitoli.
```
Ogni capitolo comprende più paragrafi. Capitoli, paragrafi o sottoparagrafi possono essere inclusi o ri-
mossi dalla stampa del documento, spuntando la corrispondente voce.
Cliccando sulla voce del documento sull’indice, si può comprimere o espandere l’elenco dei capitoli pre-
senti nel documento stesso.
8.10.1.1 Barra principale dei menu
Dal menu esporta è possibile eseguire i seguenti comandi:
La barra principale dei menù è composta da due menu a tendina:
 Menu Export
 Menu Opzioni
Figura 8.70 - Barra dei Menù
8.10.1.1.1 Menu export
Dal menu esporta è possibile eseguire i seguenti comandi:
```
Figura 8.71 - Comandi del Menu Esporta (Export)
```
```
□ General Report: esporta il file doxc della relazione generale (o di calcolo);
```
```
□ Input Tables: esporta il file docx dei tabulati di input selezionati;
```
□ Output Tables: esporta il file docx dei tabulati di output selezionati. E’ pos-
sibile effettuare una di queste operazioni:
Manuale Utente HISTRA MENU PRINCIPALE
165
o Create just one file: crea un unico docx tutti i tabulati di output
```
generati e selezionati nell’elenco sottostante;
```
o Create a Different file for each analysis and: crea un file docx per
ogni analisi e passo di analisi generata e selezionata nell’elenco
sottostante.
Figura 8.72 - Opzioni sulla esportazione dei tabulate di output
8.10.1.1.2 Menu Opzioni
Dal menu Opzioni è possibile eseguire i seguenti comandi:
Figura 8.73 - . Menu Opzions di generazione dei report.
□ Always capture images before exporting the Report: opzione sempre at-
tiva. Questa opzione consente di esportare le immagini ogni volta che si ge-
nera la relazione di calcolo generale. Può essere disattivata, se non si vo-
gliono inserire le immagini in relazione o se si è appena prima generata la
```
relazione e si vogliono ridurre i tempi di generazione;
```
□ Views to use for esporting modal forms: opzione che consente di includere
le viste per esportare le forme modali. Consente di scegliere secondo quale
vista 3D si vuole catturare le forme modali.
8.10.1.1.3 Menu Groups
Dal menu Groups è possibile selezionare la voce Nodes. Così facendo, se sono stati definiti dei gruppi di
nodi precedentemente, i tabulati di output dei nodi saranno esportati solo con riferimento a quei gruppi.
Figura 8.74 - . Menu Groups
Manuale Utente HISTRA MENU PRINCIPALE
166
8.10.1.2 Generazione della relazione generale di calcolo
Dal menu esporta è possibile eseguire i seguenti comandi:
Per generare ed esportare la “relazione di calcolo generale” eseguire i seguenti passi.
□ Scheda General Report: selezionare i Capitoli della relazione che si vo-
gliono esportare.
□ Groupbox Analisi e passo da inserire in relazione e nei tabulati: selezio-
nare le analisi e i passi delle analisi in corrispondenza dei quali riportare i
risultati nella relazione generale. I passi possono essere quelli corrispon-
```
denti gli stati limite oppure passi personalizzati (da selezionare nella cella
```
```
Passo). Cliccare sul bottone Aggiungi per aggiungere analisi e passi nel sot-
```
tostante elenco.
□ Eliminare Analisi o Stati limite di cui riportare i risultati in relazione di cal-
colo selezionando le voci o singole sotto-voci e cliccando sul bottone Eli-
mina.
Figura 8.75 - Generazione della General Report.
Dopo aver selezionato i capitoli della relazione generale di calcolo e generato le Analisi e clicare sul
bottone ADD, esportare la relazione mediante il comando disponibile dal menu Export> Genreal Report.
La relazione viene salvata in formato docx. Selezionare la cartella dove si vuole salvare il documento e
cliccare sul bottone Salva.
Selezionare capitoli Relazione
Generale
Selezionare Analisi e passo analisi
Elenco voci e sotto-voci
Analisi e Passi generati
Manuale Utente HISTRA MENU PRINCIPALE
167
Figura 8.76 - Esporta Relazione Generale di Calcolo in un unico file docx.
8.10.1.3 Generazione dei tabulati
Per generare ed esportare i tabulati sia di output che di input eseguire i seguenti passi.
□ Scheda Input Tables/ Output: Tables: selezionare i Capitoli dei tabulati che
si vogliono esportare.
□ Groupbox Analisi e passo da inserire in relazione e nei tabulati: selezio-
nare le analisi e i passi delle analisi in corrispondenza dei quali riportare i
risultati nei tabulati di output. I passi possono essere quelli corrispondenti
```
gli stati limite oppure passi personalizzati (da selezionare nella cella Step).
```
Cliccare sul bottone Add per aggiungere analisi e passi nel sottostante
elenco.
Manuale Utente HISTRA MENU PRINCIPALE
168
Figura 8.77 - Gestione Tabulati
Per quanto riguarda i Tabulati di input, dopo aver selezionato i capitoli è possibile esportarli mediante
il comando dal menu Export > Input Tables / Output Tables. I tabulati vengono salvati in formato docx
in un unico file. Selezionare la cartella dove si vuole salvare il documento e cliccare sul bottone Salva.
Figura 8.78 - Esporta Tabulati di Input
Manuale Utente HISTRA MENU PRINCIPALE
169
Figura 8.79 - Esporta Tabulati di Output
Per quanto riguarda i Tabulati di Output, selezionato i capitoli e generato Analisi e passi o stati limite,
nonché eventuali inviluppi, cliccare sul commando Export > Output Tables. Da qui si apre un ulteriore
menu, che consente di esportare i tabulati con diverse modalità:
o Crea un unico file: i tabulati di output vengono salvati in formato
docx in un unico file.
o Crea un file DIVERSO per ogni analisi e passo: i tabulati di output
vengono salvati in un file diverso per ciascuna analisi e passo di
```
analisi (o stato limite).
```
Dopo la selezione del comando, selezionare la cartella dove si vuole salvare il documento e cliccare sul
bottone Salva.
Manuale Utente HISTRA MENU PRINCIPALE
170
8.10.2 Excel Tables
Report > Excel tables
Questo comando consente di visualizzare ed esportare in excel i tabulati di calcolo, relativi alle analisi
eseguite. Queste ultime sono selezionabili nel riquadro a sinistra. I tabulati da esportare vanno invece
selezionati nel riquadro a destra.
E' possibile aggiungere analisi o step di analisi alla lista riportata a sinistra, selezionando l'analisi e il
passo desiderato e cliccando sul tasto "Add".
Figura 8.80 – Report - Tabulati di calcolo
8.11 HELP
Il menu Help contiene i comandi utili per la visualizzazione del Manuale d'uso del programma. Inoltre da questo
menu è possibile reperire informazioni utili sulla versione del programma, avviare l'aggiornamento della stessa
```
(disponendo di una connessione internet attiva) ed accedere al sito di riferimento del programma.
```