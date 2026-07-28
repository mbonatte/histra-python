

See discussions, stats, and author profiles for this publication at: https://www.researchgate.net/publication/346053192
## UN NUOVO MACROMODELLO PER LA VALUTAZIONE DELLA RESISTENZA
## SISMICA DI EDIFICI IN MURATURA
## Thesis · January 2003
## DOI: 10.13140/RG.2.2.11611.59688
## CITATION
## 1
## READS
## 398
2 authors:
## Bartolomeo Pantò
## Durham University
## 117 PUBLICATIONS   1,694 CITATIONS
## SEE PROFILE
## Ivo Caliò
University of Catania
## 171 PUBLICATIONS   2,857 CITATIONS
## SEE PROFILE
All content following this page was uploaded by Bartolomeo Pantò on 21 November 2020.
The user has requested enhancement of the downloaded file.



## UNIONE EUROPEA
## Fondo Sociale Europeo




## UNIVERSITÀ DEGLI STUDI DI CATANIA

Facoltà di Ingegneria
Dipartimento di ingegneria Civile ed Ambientale
## SEZIONE DI INGEGNERIA STRUTTURALE



## Bartolomeo Pantò




## UN NUOVO MACROMODELLO PER LA
## VALUTAZIONE DELLA RESISTENZA SISMICA
## DI EDIFICI IN MURATURA


## TESI DI LAUREA



## Relatore
## Ing. Ivo Caliò

## Correlatori
Ing. Massimo Marletta (Università di Catania)
Ing. Salvatore Miano (S.T.S. – Catania )
Ing. Salvatore Furnari (S.T.S. – Catania )



## Anno Accademico  2003 - 2004




















## 2

## Indice


Capitolo 1: Aspetti generali sulle murature
e inquadramento normativo     1

1.1                  Aspetti costruttivi delle strutture in muratura  1
1.2  Comportamento dei pannelli murari soggetti a
forze orizzontali   2
1.3                  Normativa nazionale in materia di murature  11

## Bibliografia 19


Capitolo 2: Modelli non lineari per l’analisi
di edifici in muratura         21

2.1                  Metodo POR         23
2.2                  Modelli a macro-elementi    24
2.3                  Modelli agli elementi finiti   25
2.4                  Analisi limite  40

Bibliografia                                                                                                                          49


Capitolo 3: La modellazione delle murature
Mediante l’utilizzo di macromodelli       51

3.1                  Macromodello a geometria variabile   52
3.2                  Macromodello di Brencich e Lagomarsino    57

Bibliografia                                                                                                                           66







## 3
Capitolo 4: Il macromodello proposto 67


4.1 Descrizione del modello meccanico
equivalente          67
4.2                  Equazioni del moto del sistema   77
4.3    Struttura ricorrente nelle equazioni
del         moto          90
4.4                  Legami costitutivi  96

## Bibliografia  105


Capitolo 5: Sviluppo di un programma di calcolo non
lineare che utilizza il macromodello proposto                    107

5.1                  Definizione del modello   107
5.2    Organizzazione    generale del programma  112


Capitolo 6: Analisi statiche  123

6.1                  Prove su  pannelli  123
6.2    Prove su pareti piane  132
6.3    Modellazione di muratura blocchi    165

## Bibliografia  169


Conclusioni e sviluppi futuri  171



























## 4




## Introduzione
L’importanza che rivestono le strutture in muratura, soprattutto nel nostro paese,
può essere giustificata sotto molteplici punti di vista. Innanzitutto gran parte del
nostro  patrimonio  edilizio  esistente  è  rappresentato  da  strutture  in  muratura.
Inoltre  bisogna  considerare  la  valenza  assunta  da  queste  dal  punto  di  vista
storico–culturale.  E’  superfluo  ricordare  infatti  che  praticamente  tutto  il  nostro
patrimonio  monumentale  che  oltre  a  costituire  motivo  di  orgoglio,  si  traduce  in
un grosso vantaggio economico,  è costituito da strutture in muratura.
Per i motivi sopra esposti, tali strutture dovrebbero essere oggetto di un interesse
che nella realtà, spesso, non viene riscontrato. L’interesse a cui si fa riferimento
in  quest’ambito  è  naturalmente  di  natura  tecnica  e  in  particolare  riguarda  la
valutazione della vulnerabilità sismica di queste opere a salvaguardia delle stesse
e soprattutto delle vite umane.

Il problema della valutazione della resistenza sismica degli edifici e del costruito
in  generale  sta  divenendo  sempre  più  di  attualità.  Purtroppo  gli  eventi  stessi
spesso impongono un accrescimento repentino d’interesse.
Tale  problema  tuttavia,  anche  quando  c’è  la  volontà  di  affrontarlo,  è  tutt’altro
che  semplice.  In  particolare,  la  valutazione  della  vulnerabilità  sismica  delle
strutture in muratura impone di eseguire analisi in ambito non lineare che, per un
materiale  caratterizzato  da  disomogeneità,  anisotropia,  e  forte  dipendenza  da
possibili difetti costruttivi o fenomeni di degrado localizzato, pongono non poche
difficoltà.
In  questi  ultimi  anni  molti  autori  hanno  condotto  studi  per  mettere  a  punto
metodi  per  la  modellazione  di  edifici  in  muratura.  In  particolare,  si  è  cercato  di
affiancare ai modelli più sofisticati, dei modelli semplificati, più facili da gestire
ma che allo stesso tempo fossero in grado di cogliere gli aspetti qualitativamente
più rilevanti del comportamento delle murature sottoposte a carichi da sisma.

Un’ultima  osservazione  che  pare  importante  fare  è  che  non  è  affatto  detto  che
una  struttura  in  muratura,  in  campo  sismico,  abbia  meno  risorse  rispetto  a  una
struttura  in  cemento  armato  o  altro.  E’  si  vero  che  tante  costruzioni  di  questo
genere  sono  sorte  in  periodi  in  cui  non  erano  ancora  maturate  le  conoscenze
tipiche  dell’analisi  strutturale,  ma  è  pur  vero  che  si  metteva  in  atto  una  regola
d’arte  che  spesso  sintetizzava  una  esperienza  pratica,  accumulata  nell’arco  di
parecchie generazioni.




## 5
Nel presente lavoro viene introdotto un nuovo macro-elemento a quattro gradi di
libertà, atto a descrivere sia il comportamento non-lineare di un singolo pannello
murario che di un blocco lapideo.
Ogni  singolo  macro-elemento  interagisce  con  gli  altri  adiacenti  mediante  un
letto discreto di molle che possono essere unilatere o non lineari. Inoltre ciascun
elemento  risulta  essere  deformabile  a  taglio  e  tale  deformazione  è  controllata
attraverso una coppia di molle inelastiche.
Le  proprietà  di  massa  del  modello  sono  state  considerate  mediante  una
discretizzazione per masse concentrate in corrispondenza del centro di massa di
ogni elemento.
L’estrema  semplificazione  utilizzata  nella  definizione  del  singolo  macro-
elemento consente anche la schematizzazione di un pannello mediante una mesh
di  macro-elementi  e  si  presta  particolarmente  bene  nella  schematizzazione  di
strutture costituite dall’assemblaggio di blocchi lapidei con presenza o assenza di
malta.
La  validità  del  modello  proposto  verrà  valutata  mediante  analisi  push-over,
condotte su pannelli e pareti murarie che sono state oggetto di ricerca teorica e/o
sperimentale.  In  particolare  verranno  effettuati  alcuni  confronti  con  i  risultati
ottenuti  da  altri  autori  utilizzando  macro-modelli  già  proposti  in  letteratura  con
riferimento   ad   alcune   pareti   la   cui   risposta   è   stata   ampiamente   indagata
nell’ambito del progetto Catania [1]. Infine, per valutare le principale limitazioni
del  modello  proposto,  verrà  effettuato  un  confronto  con  i  risultati  che  si
ottengono utilizzando una modellazione agli elementi finiti in ambiente ADINA
## [2].



































## 6
## Bibliografia

[1] D.  Liberatore  (A  cura  di),  Progetto  Catania:  indagine  sulla  risposta
sismica di due edifici in muratura, CNR-Gruppo Nazionale per la
Difesa dai Terremoti - Roma, 2000, 275 pp. + CD-ROM allegato.
## [2]
## ©
ADINA  ,R&D  Inc.    Report  ARD  01-7,    ADINA  teory  and  modeling
guide.



































## 7




1 Aspetti  generali  sulle  murature  ed  inquadramento
normativo
1.1 Aspetti costruttivi delle strutture in muratura
Nello studio di strutture in muratura, più di qualsiasi altra tipologia costruttiva, è
fondamentale  un  attento  esame  delle  caratteristiche  meccaniche  e  costruttive  di
ciascun elemento che compone la costruzione.
Le parti fondamentali cui si può immaginare suddiviso un edificio sono :
- Pareti verticali
## - Orizzontamenti
- Fasce di piano
Per quanto riguarda le pareti murarie, gli elementi essenziali che determinano la
buona  fattura  o  no  di  una  muratura,  sono  le  dimensioni  e  la  organizzazione  dei
conci e la presenza di elementi disposti  ortogonalmente al piano della parete in
modo da attraversare la muratura per tutto il suo spessore (diatoni).
Una  buona  muratura  deve  essere  costituita  da  conci  di  grandi  dimensioni  e
organizzati  in  maniera  da  realizzare  ricorsi  orizzontali  senza  l’interposizione  di
spessori rilevanti di malta. Una muratura siffatta presenterà una scarsa attinenza
a fenomeni di disgregazione.
Nell’esaminare le strutture verticali, è di fondamentale importanza assicurarsi se
sono stati previsti efficaci ammorsamenti tra le pareti ortogonali.

Gli   orizzontamenti   costituiscono   un   elemento   essenziale   perché   sono   il
principale elemento che influenza il comportamento globale della struttura.
La presenza di un orizzontamento sufficientemente rigido fa si che la struttura si
comporti  in  maniere  “scatolare”  vale  a  dire  che  la  struttura  sopporta  i  carichi
orizzontali sollecitando le pareti nel proprio piano.
Chiaramente è inteso che un solaio anche se rigido, per assolvere a tale funzione,
deve essere efficacemente ammorsato alle pareti. Ecco che la presenza di cordoli
di  piano  per  una  struttura  in  muratura  diviene  un  elemento  di  importanza
primaria.
Nelle  tipologie  costruttive  meno  recenti  è  frequente  l’uso  di  solai  in  legno  o  di
orizzontamenti  realizzati  mediante  volte.  La  prima  tipologia  si  presta  bene  a
ripartire  i  carichi  orizzontali  e  quindi  a  garantire  la  scatolarità  della  struttura,
purché i travetti siano efficacemente ancorati alle pareti, condizione che peraltro














## 8
non  è  difficile  da  garantire  anche  se  con  opportuni  interventi  di  miglioramento
(vedi riferimento 3). La seconda tipologia invece è quella che deve suscitare più
preoccupazioni  poiché  difficilmente  può  essere  in  grado  di  effettuare  una
efficace distribuzione delle forze orizzontali, inoltre esercita una spinta contro le
pareti, sollecitando queste a ribaltamento fuori piano, anche in assenza di sisma.
In   presenza   di   orizzontamenti   a   volta   si   dovrà   senz’altro   intervenire   per
migliorarne    il    comportamento    d’insieme    dell’edificio.    L’intervento    più
immediato a cui si può pensare è senz’altro l’inserimento di tiranti.
Uno studio, infine, dei particolari costruttivi consentirà di individuare le possibili
cause  di  innesco  di  meccanismi  locali  di  danno.  Esempi  di  questo  tipo  possono
essere  costituiti  da  architravi  insufficienti  o  scarsamente  ammorsati,  cambio  di
sezioni nelle pareti, ecc.

La  risposta  di  un  edificio  è  fortemente  condizionata  dalle  fasce  di  piano.  La
rigidezza  e  la  resistenza  di  queste  infatti  determina  le  condizioni  di  vincolo  cui
sono soggetti i maschi murari.
In  presenza  di  fasce  rigide,  i  maschi  murari  si  possono  assumere  con  buona
approssimazione nella condizione di vincolo incastro-incastro che gli conferisce
una maggiore resistenza all’azione di carichi orizzontali.
Un’altra  caratteristica  delle  fasce  che  svolge  un  ruolo  importante  ai  fini  del
comportamento sismico degli edifici è la duttilità.
Entrambe le caratteristiche menzionate, dipendono oltre che dalla larghezza delle
fasce   stesse,   dalla   presenza   o   meno   dei   cordoli   di   piano   e   di   architravi
sufficientemente ancorati alla muratura.


1.2 Comportamento dei pannelli murari soggetti a forze
orizzontali
Nell’esaminare il comportamento delle pareti murarie è importante distinguere il
caso  di  pareti  sollecitate  nel  proprio  piano  e  il  caso  di  pareti  sollecitate  fuori
piano.  Nel  seguito  verrà  brevemente  descritto  il  differente  comportamento  della
muratura in relazione della direzione della sollecitazione.

1.2.1 Pannelli murari sollecitati fuori dal proprio piano
Un   pannello   murario   soggetto   a   forze   fuori   dal   proprio   piano   presenta
meccanismi  di  collasso  di    tipo  ribaltante.  Si  ha  cioè  una  perdita  di  capacità
portante  a  causa  dell’apertura  di  fessure  dovute  al  carattere  monolatero  della
muratura.  Le  deformazioni  plastiche  che  accompagnano  tali  meccanismi  sono
molto contenute pertanto l’energia dissipata da una parete sollecitata fuori piano
risulta alquanto modesta.
Si distinguono tre tipi di collasso (meccanismi di Rondelet) [3] . Il primo tipo è
facilmente  riscontrabile  in  pareti  isolate  o  comunque  scarsamente  vincolate  ad
altre  pareti  ortogonali.  Questo  consiste  in  un  ribaltamento  fuori  piano  intorno  a



## 9
una  cerniera  cilindrica  orizzontale  che  si  forma  alla  base  del  pannello  murario
(figura  1,a).  Se  è  presente  un  vincolo  in  sommità,  ad  esempio  un  tirante  o  delle
travi di copertura, il meccanismo si modifica come rappresentato nella figura 1,b
e prevede la formazione di tre cerniere.

## (a)        (b)

figura 1:  Primo meccanismo di Rondelet: (a) assenza del vincolo in sommità;
(b) presenza del vincolo in sommità.

Gli altri due meccanismi di Rondelet si attivano in pareti che sono efficacemente
ammorsate  ad  altre  pareti  ortogonali.  In  particolare  il  secondo  meccanismo  è
relativo ad una parete libera da un lato e ben vincolata dall’altro; in questo caso
la  cerniera  si  forma  lungo  la  diagonale  della  parete  (figura  2,a).  Il  terzo
meccanismo  si  verifica  quando  si  ha  la  contemporanea  presenza  di  due  pareti
ortogonali che vincolano da entrambi i lati la parete in esame; in questo caso si
ha  il  collasso  di  una  porzione  triangolare  (o  trapezoidale)  del  pannello  murario,
come indicato nella figura 2,b.


## (a)(b)

figura2 : (a) Secondo meccanismo di Rondelet; (b) terzo meccanismo di
## Rondelet.
















## 10
Una  volta  individuato  il  meccanismo  di  collasso,  è  possibile  determinare  il
valore  del  carico  ultimo  impostando  un  problema  di  analisi  limite,  come  sarà
ampiamente descritto nel capitolo 2.
Il   carico   ultimo   così   ottenuto   costituisce   una   stima   attendibile   del   reale
moltiplicatore  dei  carichi  a  collasso  solo  se  la  qualità  della  muratura  è  tale  da
garantire  il  comportamento  monolitico  della  parete.  Se  tale  condizione  non  è
verificata  (ad  esempio  nel  caso  di  una  parete  di  mattoni  a  più  teste  senza
l’interposizione  di  un  adeguato  numero  di  diatoni  oppure  nel  caso  di  una
muratura di pietrame composta da materiale di pezzatura modesta con parecchia
malta  di  collegamento)  il  carico  ultimo  deve  essere  adeguatamente  ridotto  per
tenere  in  conto  di  altri  meccanismi  di  danno  localizzati  che  possono  anticipare
l’attivarsi dei meccanismi di collasso descritti.

1.2.2 Pannelli murari sollecitati nel proprio piano
Nello  studio  di  pannelli  murari  soggetti  a  forze  orizzontali  vengono,  in  genere,
presi in considerazione due condizioni di vincolo della sezione di testa: il caso di
estremo  superiore  libero  e  il  caso  di  estremo  superiore  impedito  di  ruotare[1].
Questi  rappresentano  due  casi  limite  della  reale  condizione  di  vincolo  dei
pannelli inseriti in uno schema strutturale complesso.
Si distinguono tre principali meccanismi di collasso :
- rottura per schiacciamento/ribaltamento
- rottura a taglio per fessurazione diagonale
- rottura per scorrimento
Nel  seguito  si  esporranno  alcuni  criteri  di  rottura  presenti  in  letteratura  che
consentono di valutare la resistenza di pannelli murari isolati .
Nel caso che il pannello si trovi inserito in un edificio, oltre all’uso di tali criteri
di rottura, diviene di fondamentale importanza valutare in maniera corretta il tipo
di vincolo che il resto della struttura offre al pannello in esame.

1.2.2.1 Deformabilità e duttilità
Pannelli  murari  caratterizzati  da  bassi  valori  del  rapporto  B/H  (pareti  snelle)  e
soggetti  a  piccoli  carichi  assiali  presentano  una  risposta  di  tipo  prevalentemente
flessionale [4]. Nel collasso di tali pareti il fenomeno della parzializzazione della
sezione  ha  un  ruolo  primario  e  si  perviene  a  un  meccanismo  di  rottura  per
schiacciamento o ribaltamento.
Nel caso di pareti tozze o soggette ad elevati carichi assiali (per esempio i maschi
murari  dei  piani  bassi  di  un  edificio)  il  comportamento  è  fondamentalmente  di
tipo  tagliante.  In  questo  caso  la  parzializzazione  della  sezione  è  fortemente
limitata  dalla  precompressione  dovuta  al  carico  assiale  e  viene  evidenziata  la
deformabilità a taglio.
La  risposta  di  una  parete  che  presenta  un  comportamento  di  tipo  flessionale  è
caratterizzata  da  cicli  di  isteresi  molto  stretti.  Al  limite,  se  il  pannello  murario
viene  schematizzato  come  un  corpo  rigido  e  il  suolo  come  un  vincolo  rigido
unilatero,  si  ottiene  un  comportamento  elastico  non-lineare,  caratterizzato  da  un
ciclo di isteresi nullo.



## 11

figura 3 : Comportamento di una parete snella

E’  inoltre  possibile  osservare  come  all’aumentare  del  numero  di  cicli  non  si  ha
un sensibile degrado di rigidezza o di resistenza.

In  una  parete  in  cui  nella  risposta  complessiva  la  componente  a  taglio  risulta
prevalente  rispetto  a  quella  flessionale,  si  riscontrano  cicli  di  isteresi  piuttosto
contenuti  fino  al  raggiungimento  di  un  valore  di  picco  della  forza  (V
max
),  in
corrispondenza del quale, come verrà meglio descritto nel paragrafo successivo,
avviene  la  formazione  di  fessure  diagonali.  Oltre  tale  valore  si  osserva  un
significativo  degrado  sia  della  rigidezza  che  della  resistenza  e  cicli  di  isteresi
molto ampi. Nella figura 4 è rappresentato un esempio di tale comportamento.

figura 4 : Comportamento di una parete tozza

Nella pratica la reale curva può essere schematizzata con una bilatera. Nel lavoro
di Magenes e Calvi [4] si consiglia di assumere per il ramo elastico, la rigidezza
pari  alla  rigidezza  secante  in  corrispondenza  di un valore dello sforzo di  taglio
pari   al   75%   di   V
max
.   Il   taglio   ultimo   si   determina   in   genere   imponendo
l’equivalenza  delle  aree  sottese  dalla  curva  reale  e  della  bilatera  (fig.  5).  A  tal
proposito studi di Tomazevic [5] hanno evidenziato che per pareti che mostrano
un comportamento di tipo tagliante è possibile assumere V
u
## =0.9 V
max
## .















## 12
## Vu
δ
elasticoδultimo
## V
δ


figura 5 : Equivalenza tra la curva reale e la bilatera equivalente.

Nel  già  citato  lavoro  di  Magenes  e  Calvi  [4]  viene  messo  in  luce  che  lo
spostamento (
δ
ultimo
) ultimo può essere espresso in termini di scorrimento ultimo
che,  per  pareti  caratterizzate  da  un  comportamento  a  taglio,  risulta  essere  un
parametro stabile, gli autori, a seguito di prove sperimentali, propongono:

## %./50≅=H
ultimoultimo
δγ                                       (1)
Dove  con  δ
ultimo
si  indica  lo  spostamento  orizzontale  ultimo  della  sezione  di
sommità della parete(fig.5), con H l’altezza della parete.

1.2.2.2 Descrizione dei meccanismi di rottura e criteri di resistenza
Come già accennato, i meccanismi di rottura di una parete muraria, caricata nel
proprio piano, possono essere classificati come segue :
- meccanismo di schiacciamento/ribaltamento;
- meccanismo di rottura per scorrimento;
- meccanismo di rottura per taglio per fessurazione diagonale.


Meccanismo di schiacciamento/ribaltamento
Le  forze  orizzontali  agenti  sul  pannello  murario inducono un momento flettente
che  varia  linearmente  lungo  l’altezza  della  parete.  Questo  produce  tensioni
normali  di  compressione  e  di  trazione.  Tali  sollecitazioni  risultano  massime  in
corrispondenza delle sezioni di estremità della parete.
Se  le  tensioni  di  compressione  superano  la  resistenza  a  compressione  della
muratura si verifica uno schiacciamento in corrispondenza della parte compressa
della  sezione  trasversale  della  parete.  Pur  non  pervenendo  allo  schiacciamento
della muratura, può verificarsi il ribaltamento del pannello, o di una porzione di
esso,  a  causa  della  progressiva  parzializzazione  della  sezione  che  porta  l’asse
neutro  in  prossimità  del  bordo  compresso  con  un  progressivo  degrado  della
rigidezza fino all’incapacità di sostenere ulteriori incrementi di carico.



## 13
Per  quanto  riguarda  il  meccanismo  di  schiacciamento,  la  formulazione  di  un
criterio  di  rottura  risulta  abbastanza  semplice.  A  tale  scopo  si  consideri  un
pannello  caricato  da  uno  sforzo  assiale  costante  P  eccentrico  rispetto  all’asse
geometrico e da una forza di taglio V (fig. 6).
## P
## H
## V
## H0
## B
esup
einf
ησc

figura 6 : Pannello caricato da sforzo normale eccentrico e forza orizzontale

Si immagini di modellare la muratura come un materiale elastico lineare fino alla
rottura  a  compressione  e  non  reagente  a  trazione.  Ammettendo  tali  ipotesi  la
condizione  di  rottura  coincide  con  il  raggiungimento  della  tensione  massima
ammissibile a compressione (σ
c
) in corrispondenza dello spigolo del pannello.
La  distribuzione  di  tensioni  lineare,  per  semplicità,  viene  qui  sostituita  con  una
distribuzione uniforme di intensità ridotta, come riportato in figura 6.
Imponendo  l’equilibrio  alla  rotazione  attorno  al  punto  medio  della  sezione  di
base, si ha:

## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## −⋅
## ⋅
## =⋅=⋅
c
u
pBP
ePHV
ησ3
## 1
## 2
## 0inf,max
## (2)
essendo:
σ
c
la resistenza a compressione della muratura;
## H
## 0
l’altezza del punto di nullo del diagramma del momento flettente;
P il carico normale agente sul pannello;
B,H e t rispettivamente larghezza, altezza e spessore della parete.
P la tensione media di compressione p=P/Bt
e
inf,u
l’eccentricità  del  risultante  dei  carichi  nella  sezione  di  base  del  pannello
nella condizione limite di schiacciamento.















## 14
Dall’espressione    (2)    è    possibile    ricavare    il    taglio    che    determina    lo
schiacciamento:

## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## −⋅=
cv
pP
## V
ησα3
## 1
## 2
max
## (3)
Nella  quale  è  stato  posto
α
v
## = H
## 0
/B.  Tale  parametro  prende  il  nome  di
coefficiente  di  taglio  e  costituisce  una  misura  del  grado  di  vincolo  opposto  dal
resto della struttura nei confronti del pannello.

Tuttavia  è  possibile  prevedere  modelli  costitutivi  più  complessi,  come  ad
esempio   un   legame   di   tipo   parabola-rettangolo   a   compressione   e   limitata
resistenza a trazione.

## Il
meccanismo  di  ribaltamento  di  un  pannello  può  avvenire  secondo  modalità
differenti a seconda della qualità della malta. Nel caso di una muratura realizzata
con malta di buone caratteristiche il pannello si comporta come un blocco rigido
che  ruota  intorno  a  uno  spigolo  di  base  (figura  7,a).  In  presenza  di  malta  di
qualità  scadente  o  in  totale  assenza  di  questa  e  nel  caso  di  pannelli  tozzi,  come
mostrato  da  studi  sperimentali  [3]  su  murature  di  blocchi  squadrati,  il  collasso
avviene attraverso il distacco e la rotazione di una porzione di parete delimitata
da  una  direzione  inclinata.  Gli  studi  condotti  hanno  mostrato  come  l’angolo  di
inclinazione
α  di  tale  direzione  dipende  dalla  geometria  della  parete  e  dalla
tessitura  dei  mattoni  (figura  7,b  e  figura  7,c).  Ovviamente  il  verificarsi  di  tali
meccanismi parziali riduce il taglio ultimo del pannello murario.
α
## (a)(b)(c)

figura 7: Meccanismi di ribaltamento nel piano: (a) globale da blocco rigido; (b)
e (c) parziali.

Il  valore  del  taglio  ultimo  per  ribaltamento  si  può  calcolare  risolvendo  un
problema   di   analisi   limite.   Considerando   meccanismi   parziali   come   quelli
indicati nelle figure 7,b e 7,c è possibile calcolare il moltiplicatore a collasso al
variare  dell’angolo  α.  Il  minimo  di  tali  moltiplicatori  costituisce  l’effettivo
moltiplicatore a collasso.
In aggiunta alla rotazione rigida, è possibile tener conto in maniera semplificata
di  un  parziale  schiacciamento  della  muratura  considerando  come  centro  di
rotazione, rientrato 5 – 10 cm rispetto allo spigolo [3].



## 15
Ulteriori   dettagli   sull’approccio   tramite   l’analisi   limite   ai   problemi   di
modellazione di strutture in muratura saranno discussi nel capitolo seguente.


Meccanismo di rottura a taglio per fessurazione diagonale
Il meccanismo di rottura a taglio per fessurazione diagonale si realizza quando le
sollecitazioni di taglio provocano la formazione di fessure diagonali che partono
dalla zona centrale del pannello per poi estendersi. La formazione di tali fessure
si  determina  in  corrispondenza  delle  direzioni  principali  cui  corrispondono  le
massime  tensioni  di  compressione,  in  quando  alla  direzione  ortogonale  sono
associate le trazioni massime.
Uno  dei  criteri  presenti  in  letteratura  per  valutare  la  capacità  ultima  a  taglio  di
una  parete  è  dovuto  a  Turnsek  e  Cacovic  [7].  Scaturito  dall’osservazione  dei
risultati  di  diverse  prove  sperimentali  [5,6],  tale  criterio  si  basa  sull’assunzione
che  la  rottura  avviene  quando  la  tensione  principale  di  trazione,  nella  zona
centrale del pannello, eguaglia la resistenza a trazione della muratura.
La  formula  che  esprime  tale  criterio  si  ricava  facilmente,  ammettendo  una
distribuzione parabolica delle tensioni tangenziali lungo la sezione del pannello,
con valore massimo pari a  1.5*V/A in corrispondenza dell’asse baricentrico, da
semplici considerazioni sullo stato tensionale, si ricava infatti l’espressione della
tensione  principale  di  trazione  in  corrispondenza  proprio  dell’asse  del  pannello,
di seguito riportata:
## 22
## 22
## 51
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## +
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## =+=
## A
## V
## A
## P
p
t
## .τσ

Essendo: σ
t
la  tensione  principale  di  trazione,  P  lo  sforzo  normale  agente  sul
pannello,
p la pressione media, V il taglio agente, B e t la base e lo spessore del
pannello, A=B*t la sezione trasversale.

A  questo  punto  eguagliando  tale  espressione  con  la
resistenza  convenzionale  a
trazione, l’espressione del taglio ultimo assume la forma [6,8]:

tu
tu
d
p
## Bt
## V
σ
σ
## +⋅=1
## 51.
## (4.a)
Il termine σ
tu
rappresenta la resistenza a trazione della muratura, tale parametro
in  linea  teorica  è  una  grandezza  locale,  in  quest’ambito  tuttavia  deve  essere
interpretato  come  un  parametro  di  tipo  globale,  dato  che  è  riferito  all’intero
pannello.  Non  è  detto  inoltre  che  debba  coincidere  con  la  resistenza  a  trazione
che   si   ricaverebbe   da   una   prova   a   trazione   sulla   muratura,   va   piuttosto
determinato  eseguendo  una  prova  di  taglio  che  permette  di  ricavare  il  taglio
ultimo e invertendo la (4.a). Per marcare il carattere
macroscopico  e  non  locale
del parametro σ
tu
, questo spesso viene indicato come resistenza convenzionale a
trazione.














## 16

La  (4.a)  viene  spesso  riportata  in  funzione  di  τ
k
che  rappresenta  la  tensione
tangenziale  media  in  condizioni  ultime  (V
d
/A)  in  assenza  di  sforzo  normale,  e
non  in  termini  di  σ
tu
.  E’  facile  notare  che  tali  parametri  sono  legati  dalla
relazione τ
k
## =σ
tu
/1.5; la formula precedente diviene quindi :

k
kd
p
BtV
τ
τ
## ⋅
## +⋅=
## 51
## 1
## .
## (4.b)
Il  parametro  τ
k
presenta  il  vantaggio  di  avere  un  riscontro  fisico  più  immediato
rispetto  alla  tensione  convenzionale  a  trazione.  Se  ad  esempio  si  esegue  una
prova di taglio su un campione di muratura (in assenza di sforzo normale), basta
dividere  il  valore  del  taglio  ultimo  che  si  registra  per  la  sezione  trasversale  del
pannello esaminato e si determina τ
k
## .

Successivamente  fu  proposto  da  Turnsek  e  Sheppard  di  sostituire  al  fattore  1.5
presente  nelle  (4)  un  parametro
b  dipendente  dal  rapporto  geometrico  B/H  del
pannello [8].
In sostituzione della (4) e (5) si ha:

tu
tu
d
p
b
## Bt
## V
σ
σ
## +⋅=1
## (5.a)

k
kd
b
p
BtV
τ
τ
## ⋅
## +⋅=1
## (5.b)
Tra tutti i criteri presenti in letteratura per la determinazione del parametro
b, qui
si cita quello dovuto a Benedetti e Tomazevic [9]:
b = 1 per   H/B
## ≤ 1
b = H/B per       1
## <H/B<1.5
b = 1.5 per           H/B
## ≥1.5
## ++


Più  recentemente,  un  criterio  di  rottura  alternativo  per  murature  di  blocchi
squadrati  è  stato  proposto  da  Magenes  e  Calvi  [4].  In  tale  formulazione  viene
distinto il caso di fessurazione diagonale dovuta al cedimento dei giunti di malta
(taglio  ultimo
## V
## 1
)  e  il  caso  di  fessurazione  diagonale  per  rottura  dei  mattoni
(taglio ultimo
## V
## 2
## ) :


## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## +
## +
## ⋅⋅=
v
c
tBV
α
σμ
## 1
## 1
## (6,a)



## 17

btv
bt
f
f
tBV
σ
αβ
## +⋅
## +
## ⋅⋅=1
## 1
## 2
## )(
## (6,b)


Nelle quali:
f
bt
indica la resistenza a trazione dei mattoni;
B,t la base e lo spessore della parete;
c,μ  coesione e coefficiente di attrito della malta;
α
v
## = H
## 0
/B; con H
## 0
il punto di nullo del diagramma dei momenti;
β

= è un coefficiente che può essere assunto da 2 a 3.
Si  noti  come  l’espressione  di
## V
## 2
,  relativa  al  caso  di  rottura  dei  mattoni,  sia
l’equivalente  dell’espressione  di  Cacovic  (4,5)  nella  quale  è  stato  introdotto  il
coefficiente  di  taglio
α
v
che  dipende  dalla  condizione  di  vincolo  del  pannello.
Inoltre  nell’espressione  (6,b)  la  resistenza  a  taglio  è  legata  esclusivamente  alla
resistenza  dei  mattoni  proprio  perché  si  suppone  che  siano  questi  a  giungere  a
rottura.
Nel caso di muratura in pietrame è comunque preferibile continuare ad utilizzare
le (4) nelle quali è possibile introdurre un parametro convenzionale di resistenza.


Meccanismo di rottura per scorrimento
Il  meccanismo  di  rottura  a  scorrimento  si  realizza  in  seguito  alla  formazione  di
piani di scorrimento lungo i letti di malta nelle sezioni di estremità della parete.
Il  criterio  di  rottura  tradizionalmente  utilizzato  è  quello  di  Mohr-Coulomb.
Secondo tale criterio, la tensione tangenziale ultima viene espressa come somma
di un termine costante
c (coesione) e di un termine proporzionale alla tensione di
compressione media nella sezione
σ
## :


## ()
σμτ+=c
u
## (7)

Il coefficiente di proporzionalità
μ prende il nome di coefficiente di attrito.
Al  fine  di  determinare  il  taglio  ultimo  corrispondente,  è  possibile  supporre  una
distribuzione  uniforme  e  integrare  la  (6)  su  tutta  la  zona  di  contatto(B’*t).  Si
ottiene l’espressione:


## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ⋅
## +⋅⋅=
tB
## P
ctBVd
## '
## '
μ
## (8)

















## 18







1.3 Normativa nazionale in materia di murature
Si presenta una panoramica delle normative nazionali che trattano le strutture in
muratura,  anticipando  fin  da  adesso  che    molte  di  queste  non  sono  state  redatte
con  l’obiettivo  di  inquadrare  in  maniera  organica  il  problema  ma  sono  state
piuttosto dettate da esigenze particolari e urgenti come le ricostruzioni che hanno
seguito i più importanti eventi sismici degli ultimi decenni. Norme insomma che
dettavano   prescrizioni   di   dettaglio   nell’ambito   di   un   settore   per   il   quale
mancavano principi e direttive generali.
Nel redigere il quadro normativo che verrà presentato, oltre che dai testi originali
delle norme, si è fatto riferimento a quanto riportato nel lavoro prodotto a cura di
Magenes [1] nell’ambito del progetto Catania.
1.3.1 D.M. 3 Marzo 1975
E’  il  primo  decreto  che  introduce  in  Italia  norme  per  costruzioni  in  zone
sismiche,  le  murature  vengono  trattate  solo  fornendo  alcune  indicazioni  su
possibili  interventi  di  riparazione  di  strutture  in  muratura,  trattandosi  solo  di
vaghi  cenni,  tale  decreto  non  può  assolutamente  considerarsi  un  punto  di
riferimento per la progettazione e verifica di strutture in muratura.
1.3.2 Legge regionale 20 Giugno 1977 . n°30
Fu   emanata   a   seguito   del   terremoto   in   Friuli,   vengono   introdotti   alcuni
importanti  concetti  che  possono  far  comprendere  il  comportamento  di  una
struttura  muraria,  come  il  comportamento  scatolare  o  globale  di  un  edificio,
l’importanza di una corretta distribuzione delle rigidezze, ecc.
Inoltre  si  trattano  alcune  possibili  tecniche  di  intervento,  in  particolare  vengono
trattate l’inserimento di lastre in calcestruzzo armato per il rinforzo delle pareti e
le iniezioni di malta cementizia.
Vengono  altresì  fornite  indicazioni  sulla  determinazione  delle  caratteristiche
meccaniche  dei  materiali  e  sui  metodi  di  dimensionamento  degli  interventi  di
riparazione.
1.3.3 D.M.LL.PP. 2 Luglio 1981
Emanata per regolare gli interventi di risanamento degli edifici colpiti dal sisma
nelle  regioni  Basilicata,  Campania  e  Puglia,  al  suo  interno  vengono  distinti  gli
interventi di riparazione dagli interventi di adeguamento sismico.
Tratta  i  possibili  interventi  tecnici  per  adeguare  sismicamente  una  struttura,
distinguendoli  in  interventi  mirati  ad  aumentare  la  resistenza  della  struttura  e
interventi mirati alla diminuzione delle masse.



## 19
Al  punto  3.4  in  particolare  tratta  le  strutture  in  muratura  e  i  possibili  interventi
per i diversi componenti strutturali, in particolare individua e descrive i seguenti
interventi per il risanamento delle pareti:
## -
risarciture localizzate
## -
iniezioni di miscele leganti
## -
applicazione di lastre in cemento armato
## -
inserimento di pilastri in breccia alla muratura
## -
tirantature orizzontali e verticali
Va  ricordato  che  nella  circolare  di  attuazione  (Circolare  M.LL.PP.  30/7/1981
n°21754)  viene  riportato  come  esempio  la  verifica  sismica  di  un  edificio  che
viene  effettuata  utilizzando  il  metodo  POR  e  valutando  il  taglio  ultimo  dei
maschi con la formula di Turnsek e Cacovic (4).
1.3.4 D.M.LL.PP. 7 Novembre 1987
“Norme  tecniche  per  la  progettazione,  esecuzione  e  collaudo  degli  edifici  in
muratura e per il loro consolidamento” [10]
E’  stata  la  prima  norma  che  ha  trattato  le  murature  in  maniera  organica  ed  ha
costituito  per  anni  il  principale  riferimento  per  la  progettazione  di  strutture  in
muratura.
Fornisce innanzitutto indicazioni generali sulla concezione strutturale, ribadendo
che bisogna garantire un comportamento scatolare della struttura muraria e a tal
fine prevede:
## -
efficaci ammorsamenti lungo le intersezioni verticali tra i muri.
## -
legature tra i muri paralleli realizzate da incatenamenti a livello di solaio e
dal  solaio  stesso  nella  direzione  di  orditura,  purché  sia  garantito  un
efficace collegamento tra i travetti del solaio e le pareti
## -
inserimento  di  cordoli  di  piano  di  cui  fissa  le  caratteristiche  minime  di
area trasversale e armatura.
Contiene  indicazioni  sulla  determinazione  dei  valori  caratteristici  di  resistenza
della  muratura  che  possono  essere  determinati  partendo  dalle  caratteristiche  dei
mattoni  e  della  malta,  se  questi  rispettano  certi  limiti  imposti,  oppure  tramite
prove sperimentali di cui riporta le modalità di esecuzione.
In  particolare  la  resistenza  a  compressione  (f
k
)  viene  fornita  mediante  una
tabella, in funzione della resistenza a compressione dei mattoni e il tipo di malta.
La resistenza a taglio (f
vk
) è espressa secondo un criterio alla Coulomb:

mvkvk
ffσ40
## 0
## .+=                                             (9)
Il  termine  f
vk0
rappresenta  la  resistenza  a  taglio  in  assenza  di  sforzo  normale  e
viene fornito in maniera analoga alla resistenza a compressione.
Per  quanto  riguarda  la  verifiche  di  resistenza,  prevede  innanzitutto  una  verifica
semplificata se sono rispettate certe prescrizioni, questa consiste nel verificare:


k
fAN≤=*)./(650σ
## (10)
Dove :  N è lo scarico totale di piano.














## 20
A è la sezione totale di muratura dello stesso piano.
f
k
è la resistenza caratteristica a compressione

Se tali prescrizioni non sono rispettate, impone una verifica per carichi verticali
che in pratica è una verifica a pressoflessione fuori piano poiché si considerano
delle  eccentricità  cui  può  essere  affetto  lo  sforzo  normale,  e    delle  verifiche  a
pressoflessione  (nel  piano  della  parete)  e  a  taglio  per  pareti  soggette  a  forze
orizzontali.
C’è  da  dire  a  tal  proposito  che  questa  norma  non  si  riferisce  alla  costruzione  in
zona sismica e i carichi orizzontali previsti sono quelli da vento.
I carichi verticali possono essere ripartiti ragionando per aree di influenza, per la
distribuzione  dei  carichi  orizzontali  si  può  adoperare  uno  schema  che  prevede  i
solai sufficientemente resistenti e rigidi a trasmettere tali carichi a tutte le pareti
secondo le rigidezze di ognuna.
La  normativa  prevede  sia  la  possibilità  di  seguire  il  metodo  di  verifica  delle
tensioni ammissibili che il metodo semiprobabilistico degli stati limite ultimi.
Al contrario di quanto annunciato dal titolo, la presente norma si limita a pochi
cenni  sul  consolidamento  delle  strutture  murarie  riportando  concetti  generali,
peraltro  già  espressi  dalle  precedenti  normative.  Non  viene  fornita  nessuna
indicazione  pratica  per  la  progettazione  ed  esecuzione  di  un  intervento  di
consolidamento.
1.3.5 D.M.LL.PP. 16 Gennaio 1996 : “Norme tecniche per le costruzioni
in zona sismica”
[11]  In  riferimento  alle  murature  detta  delle  prescrizioni  generali  che  tutte  le
costruzioni  in  muratura  devono  rispettare,  prevede  poi  ulteriori  prescrizioni,
rispettate le quali è possibile omettere la verifica sismica.
Nel caso in cui si debba effettuare la verifica sismica la normativa, analogamente
a  quanto  imposto  per  le  altre  tipologie  di  edifici,  prescrive  una  analisi  statica  e
assegna  la  distribuzione  di  forze.  Per  le  verifiche  delle  sezioni  dei  muri  rimane
valido quanto contenuto nel decreto del 1987.

Le norme appena descritte hanno costituito per parecchi anni il quadro normativo
nazionale. Prima di passare a dare qualche cenno sulla nuova normativa sismica,
recentemente  emanata  si  vuole  citare  uno  studio  condotto  da      Braga  et  al  [2]
mirato  a  stabilire  se  le  prescrizioni  riportate  nel  decreto  del  1996,  in  particolar
modo quelle che permettono di non eseguire la verifica sismica, siano in grado di
garantire un coefficiente di sicurezza rispetto al collasso sufficiente.
Gli  autori  hanno  considerato  una  serie  di  pareti  che  rispettavano  la  norma,  per
tutti  i  parametri  non  espressamente  citati  dalla  normativa  gli  autori  hanno
proceduto  a  un’analisi  parametrica.  Per  ogni  parete  hanno  calcolato  il  carico
ultimo  con  il  metodo  POR  e  con  un  macromodello  sviluppato  dagli  autori  e
descritto nel seguito di questo lavoro (macromodello a ventaglio), il rapporto tra
il  carico  ultimo  della  struttura  ottenuto  tramite  detti  modelli  e  il  carico  previsto
dalla stessa normativa costituisce il coefficiente di sicurezza.



## 21
Dal  risultato  delle  analisi  si  è  riscontrata  una  distribuzione  del  coefficiente  di
sicurezza al variare dei diversi parametri tutt’altro che uniforme e situazioni con
coefficienti di sicurezza minori dell’unità.
Una di queste è rappresentata dagli edifici con numero di piani pari al massimo
consentito dalla normativa (3 e 4 rispettivamente per gradi di sismicità 9 e 12), si
è visto altresì che in questo caso non porta alcun miglioramento aumentare l’area
di muratura, questo perché il carico ultimo risulta influenzato solo dalla snellezza
globale  della  parete,  che  potrebbe  essere  oggetto  di  ulteriori  prescrizioni  di
normativa.
Come  nel  caso  appena  citato,  gli  autori  hanno  individuato  altri  parametri  che
sebbene non contemplati dalla norma possono giocare un ruolo fondamentale per
la sicurezza di una struttura.
Quanto  detto  non  deve  apparire  come  una  critica  alla  normativa,  che  è  normale
abbia  dei  limiti;  si  è  solo  voluto  mettere  in  luce  come  sia  importante  prendere
coscienza  dei  problemi  e  approfondire  di  volta  in  volta  quelli  che  si  ritiene  più
opportuno a seconda del problema trattato.

1.3.6 Nuova normativa sismica : “Norme tecniche per il progetto, la
valutazione e l’adeguamento sismico degli edifici”
[12] La norma considera solo l’approccio semiprobabilistico agli stati limite.
Per   le   nuove   costruzioni   impone   che   le   forze   sismiche   debbano   essere
fronteggiate con un comportamento globale della struttura. Gli orizzontamenti a
tal  proposito  devono  essere  sufficientemente  rigidi  da  garantire  la  distribuzione
degli sforzi alle pareti parallele alle sollecitazioni sismiche.
Viene  mantenuto  il  concetto  di  “regolarità”,  rispettata  la  quale  si  possono
considerare alcune semplificazioni nelle analisi e nelle verifiche.

Caratterizzazione delle forze sismiche
L’azione  sismica  viene  caratterizzata  tramite  la  definizione  di  uno  spettro  di
progetto   elastico   la   cui   forma   è   indipendente   dall’intensità   sismica,   e
normalizzato  rispetto  a  g.  Tale  spettro  viene  amplificato  dalla  accelerazione
massima  al  suolo  definita  in  base  alla  zona  sismica  di  appartenenza  (ne  sono
previste  quattro)  e  a  un  coefficiente  dipendente  dal  tipo  di  suolo  (sono  previsti
cinque tipi di suolo).

Spettro di risposta elastico :

## ()
## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## −⋅⋅+⋅⋅=1521.)(
η
## B
ge
## T
## T
SaTS
## 0<T<T
## B


52.)(⋅⋅⋅=ηSaTS
ge
## T
## B
## <T<T
## C














## 22

## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ⋅⋅⋅=
## T
## T
SaTS
c
ge
## 52.)(η T
## D
## <T<T
## D


## 2
## 52
## T
## TT
SaTS
## DC
ge
## ⋅
## ⋅⋅⋅=.)( T
## D
## <T
## S, T
## B
## , T
## C
## , T
## D
dipendono dal tipo di suolo; a
g
dipende dalla zona sismica, secondo
quanto riportato nella tabella seguente:

Zona                                       a
g

## 1                                        0.35g
## 2                                        0.25g
## 3                                        0.15g
## 4                                        0.05g


Lo  spettro  inelastico,  utilizzato  nella  determinazione  delle  forze  sismiche  agli
SLU  viene  ottenuto  da  quello  elastico  riducendo  le  ordinate  in  funzione  del
coefficiente di struttura q.
Per strutture in muratura ordinaria (non armata) si considera :  q=1.5

Spettro di progetto inelastico :

## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## −⋅+⋅⋅=1
## 5.2
## 1)(
qT
## T
SaTS
## B
gd
## 0<T<T
## B


q
SaTS
gd
## 5.2
## )(⋅⋅=
## T
## B
## <T<T
## C


## T
## T
q
SaTS
## C
gd
## ⋅⋅⋅=
## 5.2
## )( T
## C
## <T<T
## D


## 2
## 5.2
## )(
## T
## TT
q
SaTS
## DC
gd
## ⋅
## ⋅⋅⋅=
## T>T
## D

Lo  spettro  da  utilizzare  agli  stati  limite  di  esercizio  (o  di  danno)  viene  ottenuto
da quello elastico riducendo le ordinate di un fattore pari a 2.5.







## 23









Schemi strutturali
Le strutture tridimensionali possono essere considerate come un insieme spaziale
di sottostrutture piane, nel caso della muratura la sottostruttura è costituita dalla
generica parete piana.
Soltanto  se  la  struttura  è  “regolare”  lo  studio  si  può  ricondurre  a  quello  di  due
schemi piani relativi alle direzioni principali della struttura.


Modellazione e analisi
E’ prevista la possibilità di eseguire :

## -
Analisi lineari
## -
Analisi statica lineare
## -
Analisi modale

## -
Analisi non lineari
## -
Analisi statica non lineare
## -
Analisi dinamica non lineare

Verifiche mediante analisi lineari
Nell’ambito delle analisi lineari, il metodo principale viene considerato
l’analisi  modale;  solo  se  si  è  in  presenza  di  strutture  con  determinate
caratteristiche  da  renderle  “regolari”,  si  può  applicare  l’analisi  statica
lineare. Questa consiste nell’applicare una distribuzione di forze, la cui
intensità  viene  ricavata  tramite  lo    spettro  elastico  per  la  verifica  agli
SLD,  oppure  tramite  lo  spettro  inelastico,  precedentemente  riportato,
per  le  verifiche  agli  SLU.  Tale  distribuzione  è  lineare  con  l’altezza,  in
maniera analoga a quanto prescritto dal D.M. del ’96.
Per  le  rigidezze  elastiche  degli  elementi  murari  la  norma  prescrive  di
considerare  gli  elementi  deformabili  flessionalmente  e  a  taglio  e  di
considerare  la  rigidezza  relativa  agli  elementi  fessurati.  Tale  rigidezza,
in  mancanza  di  dati  attendibili,  può  porsi  pari  alla  metà  della  rigidezza
relativa a elementi non fessurati.
Sia  che  si  utilizza  l’analisi  modale  che  l’analisi  statica,  si  giunge  a
calcolare  il  valore  di  calcolo  delle  sollecitazioni  dovute  al  sisma  che
vengono combinati con le sollecitazioni derivanti dagli altri carichi. La
verifica  agli  stati  limite,  in  questo  caso,  consiste  nel  verificare  che  in














## 24
ogni sezione muraria il valore di calcolo della resistenza superi il valore
di calcolo delle sollecitazioni.

In   particolare   ogni   elemento   deve   essere   sottoposto   alle   seguenti
verifiche :




## -
Verifica a pressoflessione nel piano

## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## ⋅
## −⋅
## ⋅
## ⋅⋅⋅
## =
d
f
f
p
## H
ptD
## V
## 850
## 1
## 2
## 0
## 2
## .
## (11)
## Dove    V
f
rappresenta    il    valore    del    taglio    che    porta    allo
schiacciamento    della    muratura    compressa,    D    e    t    sono
rispettivamente  larghezza  e  spessore  della  parete,  H
## 0
è  la  distanza
dalla  sezione  considerata  al  punto  di  nullo  del  diagramma  dei
momenti, p è la compressione media sulla sezione in esame.
f
d
## =f
k
## /γ
m
è la resistenza di calcolo a compressione della muratura.

- Verifica a taglio

m
vk
f
ftD
## V
γ
## ⋅⋅
## =
## '
## (12)
Dove  D’  è  la  larghezza  della  parte  di  sezione  compressa,  fvk  è  la
resistenza caratteristica a taglio calcolata in base alla compressione
media della sezione e secondo quanto prescritto dal decreto dell’87.

- Verifica a pressoflessione fuori piano
Il   momento   ultimo   deve   essere   calcolato   considerando   un
diagramma    delle    tensioni    di    compressione    rettangolare,    di
ampiezza  0.85*fd  e  trascurando  la  resistenza  a  trazione  della
muratura.
Per  la  progettazione  di  costruzioni  in  muratura  viene  fissato: γ
m
=2.Per
verifiche di edifici esistenti tale valore viene incrementato a seconda del
grado  di  conoscenza  della  struttura  che  il  professionista  è  in  grado  di
documentare tramite prove e sondaggi.

Verifiche mediante analisi non lineari
In  questo  caso  la  verifica  consiste  nel  controllare  che  la  duttilità
richiesta  dal  sisma  di  progetto  non  superi  le  reali  disponibilità  della
struttura.
I  legami  costitutivi  degli  elementi  murari  possono  essere  considerati
elasto perfettamente plastici, per quanto riguarda la rigidezza elastica si



## 25
fa riferimento a quanto detto per le analisi lineari, il valore ultimo della
resistenza    è    definito    dalle    relazioni    (11)    e    (12),    relative    al
comportamento  flessionale  e  a  taglio,  mentre  gli  spostamenti  ultimi
sono fissati in :

Rottura a flessione      δu = 0.008*h
Rottura a taglio           δu = 0.004*h

Dove con h si indica l’altezza del pannello.
Se  si  intende  utilizzare  una  analisi  dinamica  non  lineare,  le  richieste  di
duttilità vengono ricavate direttamente dall’integrazione delle equazioni
del  moto  della  struttura  soggetta  agli  accelerogrammi  opportunamente
scelti.

Nel  caso  che  si  utilizzi  l’analisi  statica  non  lineare,  alla  struttura  viene
applicata  una  distribuzione  di  forze  proporzionali  alle  masse  e  una
proporzionale   al   primo   modo   di   vibrazione,   l’analisi   verrà   quindi
eseguita  per  entrambe  le  distribuzioni  per  poi  considerare  il  caso  più
sfavorevole.
L’analisi  viene  condotta  incrementando  le  forze  fino  al  collasso  della
struttura  e  ricavando  il  diagramma  che  riporta  in  ordinata  il  taglio  alla
base  e  in  ascissa  lo  spostamento  del  punto  baricentrico  posto  a  2/3
dell’altezza totale dell’edificio.
Da   tale   diagramma   si   ricava   la   disponibilità   di   duttilità   globale
dell’edificio. In particolare vengono definiti :
## -
Capacità    di    spostamento    allo    stato    limite    ultimo:    Lo
spostamento  relativo  alla  perdita  di  capacita  portante  del  20%
rispetto  alla  forza  massima,  dovuta  alla  progressiva  rottura
degli  elementi  murari  che  raggiungono  il  limite  ultimo  di
spostamento.


## -
Capacità   di   spostamento   allo   stato   limite   di   danno:   Lo
spostamento  minimo  tra  quello  relativo  alla  massima  forza  e
quello per il quale si ha la rottura del primo elemento murario.

La  domanda  di  spostamento  relativa  al  sisma  di  progetto,  deve  essere
calcolata attraverso lo spettro elastico :

## ()
## 2
## 2
## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## ⋅=Δ
π
s
sed
## T
## TS


## Dove  T
s
è  il  periodo  del  sistema  a  un  grado  di  libertà  equivalente  alla
struttura  che  deve  essere  definito  tramite  la  procedura  riportata  nella
normativa stessa.














## 26

## Bibliografia

[1] G.  Magenes,  D.  Bolognini,  C.  Braggio  (A  cura  di):  “Metodi  semplificati
per  l'analisi  sismica  non  lineare  di  edifici  in  muratura”,  CNR-Gruppo
Nazionale per la Difesa dai Terremoti - Roma, 2000, 99 pp.

[2] F.  Braga,  D.  Liberatore  &  G.  Spera:  “Esame  critico  delle  prescrizioni  di
norma  per  pareti  in  muratura  soggette  ad  azioni  sismiche”.  Atti  8°
convegno nazionale ANIDIS, Taormina, 21-24 Settembre, 1997.
[3] A. Giuffrè (A cura di:): “Sicurezza e conservazione dei centri storici – Il
caso Ortigia”, Ed. Laterza.
[4] G.  Magenes,  G.  M.  Calvi  :  “In  plane  seismic  response  of  brick  masonry
walls”,  Earthquake  Engineering  and  structural  Dynamics,  Vol.  26,  1091-
## 1112  (1997).
[5] M.   Tomazevic:   “Recent   advances   in   earthquake-resistant   design   of
masonry buildings: European perspective”, Proc. 11th World Conference
on Earthquake Engng., Acapulco, Paper N° 2012, 1996.
[6] M.  Tomazevic:  “Masonry  structures  in  seismic  areas  –  a  state  of  the  art
report”, 9th European Conference on Earthquake Engng., Moscow, 1990,
Vol. A, pp 246-302.

[7] V.  Turnsek,  F.  Cacovic:  “Some  experimental  result  on  the  strength  of
brick  masonry  walls”,  Proc.  Of  the  2nd  Int.  Brick  Masonry  Conference,
Stoke-on-Trent, 1971, pp 149-156.

[8] V.  Turnek,  P.  Sheppard  :  “The  shear  and  flexural  resistence  of  masonry
walls”,  Pro.  Intern.  Research    Conference  on  Earthq.  Engng.,  Skopje,
1980, pp. 517-573.
[9] D.  Benedetti,  M.  Tomazevic:  “  sulla  verifica  sismica  di  costruzioni  in
muratura”, Ingegneria sismica, Vol I, No. 0, 1984, pp.9-16.
[10] Decreto Ministeriale 20 novembre 1987 (D.M. 20-11-1987) (Suppl. Ord.
alla G.U. 5-12-1987, n. 285).
[11] Decreto Ministero Dei Lavori Pubblici 16-01-1996 (G.U. 5-2-1996, n.29).
[12] Ordinanza  n.  3274  della  Presidenza  del  Consiglio  dei  Ministri  (Suppl.
Ord. 72 alla G. U.  8 maggio 2003 n.105).









## 27





2 Modelli  non  lineari  per  l’analisi  di  edifici  in
muratura


## Introduzione

L’analisi  di  strutture  esistenti  in  muratura  non  può  prescindere  da  un  accurato
esame  del  corpo  di  fabbrica.  Tale  esame  deve  essere  mirato  ad  accertare  le
tecniche  costruttive,  i  materiali  utilizzati,  nonché  lo  stato  di  degrado  della
struttura   (presenza   di   dissesti   e   lesioni).   Questo   passo   preliminare   è
fondamentale per comprendere il comportamento qualitativo della struttura e per
individuare  i  parametri  di  resistenza  e  di  deformabilità  che  dovranno  poi  essere
impiegati nelle analisi numeriche.
La scelta del modello da adoperare, essendo subordinata a tali informazioni sulla
struttura  in  esame,  non  può  pertanto  essere  effettuata  a  priori,  come  invece
avviene   usualmente   per   altre   tipologie   strutturali   per   le   quali   le   tecniche
costruttive   e   le   caratteristiche   dei   materiali   sono   standardizzate   (come   ad
esempio strutture in cemento armato o acciaio).
Tuttavia  questa  non  è  la  sola  difficoltà  che  si  incontra  nella  modellazione  delle
strutture  murarie.  Numerosi  aspetti  tipici  delle  strutture  in  muratura,  quali  il
comportamento fortemente inelastico con limitata o nulla resistenza a trazione, la
presenza  di  elementi  strutturali  che  mal  si  prestano  ad  essere  modellati  come
elementi   monodimensionali,   nonché   fenomeni   di   degrado   che   modificano
continuamente il comportamento della struttura, rappresentano aspetti salienti del
manufatto   murario   e   incidono   fortemente   sulla   sua   risposta.   Una   corretta
modellazione non può pertanto prescindere da tali aspetti che però, se venissero
presi   in   considerazione   integralmente,   condurrebbero   a   modelli   di   calcolo
estremamente  complessi,  la  cui  risoluzione  richiederebbe  un  enorme  sforzo
computazionale, spesso tale da rendere inapplicabile un approccio di questo tipo.
Appare quindi evidente come il grado di dettaglio della modellazione deve essere
il  giusto  compromesso  tra  costi  e  benefici  ovvero  tra  oneri  computazionali  e
risultati che ci si propone di ottenere. Il peso che può essere attribuito a ognuno














## 28
dei contrapposti interessi è certamente diverso a seconda se le analisi da condurre
sono  relative  a  scopi  di  ricerca  o  all’ambito  professionale.  Nel  secondo  caso
viene  quasi  sempre  adoperato  un  approccio  semplice  che,  pur  non  cogliendo
appieno   il   comportamento   non-lineare   della   struttura,   presenta   il   notevole
vantaggio  di  essere  compatibile  con  le  conoscenze  della  maggioranza  dei
professionisti   del   settore   e   di   fornire   in   tempi   brevi   risultati   facilmente
interpretabili.
I  metodi  presenti  in  letteratura  per  il  calcolo  in  campo  inelastico  delle  murature
sono svariati. Sembra utile, prima di descrivere nel dettaglio quelli che appaiono
essere i più rappresentativi, riportarne una possibile classificazione [1].
Una  prima  suddivisione  individua  quattro  diversi  approcci,  all’interno  dei  quali
possono pensarsi collocati tutti i metodi di analisi :
## 1.
Calcolo secondo l’analisi limite :  con un approccio del genere si mira
esclusivamente   a   determinare   il   carico   ultimo   della   struttura   e   il
meccanismo   di   collasso,   senza   ricevere   alcuna   informazione   sulla
deformabilità della struttura.

## 2.
Modelli     monodimensionali     : Gli     elementi     murari     vengono
schematizzati  utilizzando  degli  elementi  asta,  le  cui  caratteristiche  di
rigidezza   e   duttilità   devono   essere   opportunamente   tarate.   Tale
categoria  comprende  il  metodo  POR,  le  schematizzazioni  a  telaio,  i
modelli a puntone equivalente.

- Modelli  bidimensionali  :  I  pannelli  murari  vengono  schematizzati
mediante  modelli  continui  bidimensionali.  In  tale  categoria  rientra  la
grande famiglia degli elementi finiti.


## 4. Macromodelli  :
In  cui  i  pannelli  murari  vengono  descritti  mediante
modelli discreti equivalenti.


La  maggiore  peculiarità  della  muratura  è  quella  di  possedere  una  limitata
resistenza  a  trazione.  In  relazione  a  tale  peculiarità  si  può  operare  un’ulteriore
suddivisione in:
## -
Modelli a geometria fissa : Sono tutti quei modelli in cui la geometria
della  struttura  resta  immutata  durante  l’analisi,  coincidente  con  la
configurazione    iniziale,    coerentemente    con    l’ipotesi    di    piccoli
spostamenti.  La  non  resistenza  a  trazione  viene  simulata  o  attraverso
opportune ipotesi sul campo di tensioni (es: macromodello a ventaglio)
o  agendo  sui  vari  legami  costitutivi  degli  elementi  che  compongono  il
modello.


- Modelli  a  geometria  variabile  :  Il  materiale  si  considera  elastico
lineare,la   fessurazione   per   trazione   viene   simulata   modificando   la
geometria  della  struttura  in  modo  da  escludere  le  porzioni  di  struttura
che  vanno  in  trazione.  Le  altre  possibili  modalità  di  rottura  possono
essere modellate tramite opportuni criteri di resistenza.



## 29
2.1 Metodo POR
Secondo  la  classificazione  presentata,  tale  metodo  si  colloca  tra  i  modelli
monodimensionali e a geometria fissa.
Per  la  sua  semplicità  il  metodo  POR    è  attualmente  il  metodo  per  la  verifica  di
strutture  in  muratura  più  diffuso  in  ambito  professionale,  essendo  implementato
nella quasi totalità dei programmi di calcolo commerciali.
Tale  metodo  è  applicabile  esclusivamente  a  edifici  bassi  con  impalcati  di  piano
sufficientemente    rigidi.    Questo    perché    il    metodo    si    basa    sull’ipotesi
fondamentale    di    impalcati    infinitamente    rigidi,    sia    assialmente    che
flessionalmente, perfettamente ammorsati alle pareti. Tale assunzione, comunque
molto   approssimata,   risulta   accettabile   nel   caso   di   edifici   con   solai   in
latero-cemento, i quali, oltre a offrire una maggiore rigidezza flessionale rispetto
a  tutte  le  altre  tipologie  di  orizzontamenti,  risultano  usualmente  ben  ammorsati
alle pareti.
Nel  caso  di  edifici  con  differenti  tipologie  di  impalcato,  come  solai  in  legno  o
volte  portanti,  entrambi  frequentemente  riscontrabili  in  edifici  storici,  le  ipotesi
formulate risultano molto meno accettabili. In questo caso infatti i solai risultano
più  deformabili  e  non  sempre  l’impalcato  è  sufficientemente  ammorsato  alle
pareti verticali. Tale condizione può essere migliorata mediante l’inserimento di
tiranti e progettando opportunamente i collegamenti solaio-parete.
Il  metodo  risulta  invece  del  tutto  inapplicabile  a  edifici  privi  di  impalcati.  Tale
situazione    si    riscontra    in    diverse    tipologie    di    costruzioni    a    carattere
monumentale, come ad esempio le chiese.

Descrizione del metodo
Nell’applicazione del metodo POR, per l’edificio si assume un comportamento a
impalcati  rigidi,  pertanto  le  pareti  di  ogni  piano  si  comportamento  come  un
sistema di molle in parallelo che collegano due impalcati contigui. La rigidezza
assiale  dei  setti  viene  trascurata,  pertanto  il  sistema  presenta  complessivamente
tre gradi di libertà per ogni impalcato. Spesso viene trascurata anche la rigidezza
fuori  piano  delle  pareti  in  quanto  risulta  notevolmente  inferiore  rispetto  alla
rigidezza  nel  piano.  I  setti  costituiscono  delle  molle  alla  traslazione  nella
direzione  della  parete  stessa,  il  legame  costitutivo  considerato  è  elastico  -
perfettamente plastico con una resistenza limitata in termini di spostamenti.
Le  analisi  in  campo  inelastico  vengono  condotte  applicando  le  forze  orizzontali
nel centro di massa di ogni impalcato. Tali forze si distribuiranno inizialmente a
seconda delle rigidezze elastiche delle molle. Durante l’analisi quando una parete
giunge al proprio limite di snervamento inizia a deformarsi senza incrementare il
proprio  carico,  fino  al  raggiungimento  del  valore  ultimo  dello  spostamento.  A
questo punto tale parete viene eliminata dallo schema di calcolo in quanto non è
più  in  grado  di  portare  carico.  L’analisi  procede  finché  è  possibile  garantire
l’equilibrio.
Il  modello  in  genere  fornisce  valori  di  carico  ultimo  e  rigidezza  iniziale  della
struttura sovrastimati.














## 30
Originariamente  il  metodo  POR  prevedeva  esclusivamente  la  rottura  a  taglio
diagonale  che  portava  a  valutare  il  taglio  ultimo  con  la  già  citata  espressione  di
Cacovic  (1.4).  In  successive  versioni  del  metodo  si  è  cercato  di  tenere  conto
anche  della  eventualità  di  rottura  per  presso-flessione  del  maschio  murario,
considerando quindi un criterio di rottura a presso-flessione (POR-flex).
Come  già  accennato,  il  carico  ultimo  della  struttura  determinato  attraverso  il
metodo  POR  risulta  essere  una  stima  per  eccesso  di  quello  reale.  Ciò  è
conseguenza  dell’ipotesi  di  impalcati  rigidi,  che  si  traduce  in  un  vincolo  alla
rotazione in testa dei pannelli murari. Un pannello facente parte di una struttura
si  trova  in  realtà  in  una  condizione  di  vincolo  intermedia  tra  quella  di  parete
libera in testa e quella di parete impedita di ruotare in testa. L’effettivo grado di
vincolo dipende dalla rigidezza delle fasce di piano e dalla presenza o meno del
cordolo  di  piano.  Non  è  detto  tra  l’altro  che  tale  condizione  di  vincolo  resti
immutata durante tutta l’analisi, ma è piuttosto probabile che cambi a seguito di
eventuali rotture o plasticizzazioni che interessano le fasce di piano.




2.2 – Modelli a macro-elementi

Un  macroelemento  costituisce  un  modello  discreto  equivalente  ad  una  intera
porzione  di  muratura,  in  genere  un  macroelemento  è  studiato  per  modellare  un
intero  pannello  murario.  L’intera  struttura  viene  ottenuta  per  assemblaggio  dei
vari pannelli. Il principale vantaggio che offre tale approccio è quello di ridurre
considerevolmente l’onere computazionale dell’analisi rispetto alla modellazione
agli elementi finiti, in quanto viene ridotto di molto il numero dei gradi di libertà
ed  inoltre  il  comportamento  non  lineare  dell’elemento  che  si  intende  modellare
viene descritto mediante legami mono-dimensionali.
Tutti i parametri che caratterizzano un macro-elemento sono da intendersi come
grandezze  medie  e
globali,  in  quanto  viene  persa  ogni  informazione  di  ciò  che
avviene
localmente all’interno della porzione di struttura rappresentata.
Le  maggiori  difficoltà  che  si  riscontrano  nello  sviluppo  di  un  modello  a  macro-
elementi   (
macromodello)   risiedono   nella   taratura   dei   parametri   che   lo
caratterizzano, specialmente se questi non hanno un significato fisico immediato
o se risentono dell’influenza di diversi fattori.
Nell’ambito  dello  studio  del  comportamento  sismico  di  edifici  in  muratura,  allo
stato  attuale,  questo  approccio  sembra  quello  ottimale,  in  quanto  consente  di
ottenere  modelli  più  raffinati  rispetto  alla  schematizzazione  di  tipo  POR,  e  nel
contempo  evita  di  ricorrere  all’utilizzo  eccessivamente  laborioso  degli  elementi
finiti e quindi alla definizione di un legame costitutivo puntuale per la muratura,
operazione  questa  che  risulta  essere  molto  onerosa  a  causa  del  comportamento
non-lineare e alla presenza di stati tensionali pluriassiali.



## 31
Diversi   autori   hanno   sviluppato   macro-modelli,   sia   a   geometria   fissa   che
variabile,  capaci  di  rappresentare  un  intero  pannello  murario.  Alcuni  di  questi
saranno  oggetto  di  più  ampie  discussioni  nel  capitolo  successivo,  interamente
dedicato allo studio dei macromodelli presenti in letteratura.




2.3  - Modelli agli elementi finiti
L’approccio agli elementi finiti (FEM), consiste nel modellare la muratura come
un  continuo  generalmente  omogeneo  caratterizzato  da  un  opportuno  legame
costitutivo  non-lineare.  E’  pertanto  necessario  definire  tale  legame  costitutivo
non-lineare,  le  sue  superfici  di  plasticizzazione  e  le  relative  leggi  evolutive  per
regimi tensionali pluriassiali. L’onere computazionale connesso a tale approccio
è molto elevato.
I  parametri  che  caratterizzano  il  legame  costitutivo  possono  essere  ricavati,
partendo  dalle  caratteristiche  dei  componenti,  mediante  opportune  tecniche  di
omogenizzazione di non immediata definizione.
La modellazione agli elementi finiti si propone come quella più specialistica ed
evoluta, anche se a livello pratico probabilmente non è la via migliore da seguire
per la modellazione di edifici in muratura, soprattutto in ambito dinamico. Essa
infatti  presenta  notevoli  inconvenienti  che  spesso  la  rendono  inapplicabile.
Inoltre  risulta  sempre  estremamente  difficile  condurre  analisi  inelastiche  fino  a
rottura, in quanto possono presentarsi problemi di convergenza della soluzione.
Per  tale  motivo  spesso  l’analisi  viene  terminata  molto  prima  rispetto  al  reale
collasso,  corrispondente  al  raggiungimento  delle  tensioni  e  delle  deformazioni
limite.
Infine, i risultati che si ottengono risultano spesso eccessivamente dipendenti da
alcuni dei parametri costitutivi del modello e dalla
mesh adottata.
Nonostante  le  difficoltà  di  applicazione,  il  metodo  ha  comunque  una  notevole
rilevanza soprattutto nell’ambito della ricerca.
Nel  seguito  si  richiamano  brevemente  alcuni  modelli  correntemente  utilizzati
per   la   modellazione   di   materiali   di   tipo   fessurante.   In   particolare   verrà
considerata   la   modellazione   implementata   nell’ADINA   [2]   ed   inoltre   si
descriverà brevemente un modello sviluppato da Gambarotta e Lagomarsino [3]
per le murature.
2.3.1 Alcuni elementi finiti implementati in programmi commerciali
Alcuni  tra  i  codici  di  calcolo  più  evoluti  presenti  attualmente  sul  mercato
dispongono di elementi finiti non-lineari che consentono di modellare materiali
di tipo fessurante.
Nel  codice  di  calcolo  ABAQUS  è  disponibile  l’elemento
concrete,  il  quale
consente  di  modellare  materiali  con  comportamento  di  tipo  fragile  quali  il
calcestruzzo,  semplice  o  armato  con  piccole  pressioni  di  confinamento,  e  la
muratura.  Inizialmente  il  materiale  è  isotropo,  ma  a  seguito  della  formazione














## 32
delle  fessure  si  introduce  un’anisotropia.  Tali  fessure  provocano  un  graduale
degrado  della  rigidezza.  Non  vengono  prese  in  considerazione  le  deformazioni
plastiche associate alla chiusura delle fessure che si assume totale al momento in
cui lo sforzo normale di trazione ridiviene di compressione. Il criterio di rottura
utilizzato è quello di Coulomb.
Al fine di caratterizzare il comportamento del materiale, viene assunta l’energia
spesa  per  la  formazione  di  una  frattura  di  area  unitaria  come  una  proprietà  del
materiale;  ciò  è  riscontrabile  in  molti  altri  modelli  di  materiale  fessurante
disponibili in letteratura [4].
Al programma è necessario fornire il legame
σ-ε monoassiale e il coefficiente ν
di  Poisson.  Il  legame  a  trazione  è  di  tipo  lineare  fino  alla  fessurazione  con  un
successivo
softening.   I   risultati   che   si   ottengono   risultano   fortemente
condizionati dal valore della resistenza a trazione.
LUSAS    -  In  questo  codice  è  stato  implementato  un  elemento  finito  ‘concrete’
più semplice rispetto a quello già visto. Si tratta di una modellazione certamente
meno raffinata ma che può essere di più facile utilizzo.

## -
L’elemento concrete nel codice di calcolo ADINA
Nel codice di calcolo ADINA è implementato un elemento denominato
concrete
in quanto pensato soprattutto per descrivere il comportamento del calcestruzzo.
In  tale  modello  viene  considerato  un  legame  costitutivo  ortotropo  rispetto  agli
assi principali di tensione.

I  moduli  di  elasticità  normale  lungo  le  direzioni  principali  sono  determinati
considerando  un  legame  tensioni-deformazioni  riferito  a  uno  stato  tensionale
monoassiale (fig. 1), che deve essere fornito dall’utente.
σc
σcu
σtr
σt
εcu
εcy
εtyεtu

figura  1:  legame  costitutivo  della  muratura,  riferito  a  uno  stato  di  tensione
monoassiale.

Tale  legame,  durante  l’analisi,  viene  aggiornato  in  modo  da  tener  conto  della
natura  pluriassiale  dello  stato  tensionale.  Utilizzando  il  dominio  di  rottura  a



## 33
compressione, in seguito descritto, in ogni passo dell’analisi si può determinare
la  tensione  di  compressione  (σ
## 3
)  che  porta  a  schiacciamento  il  materiale.  Tale
valore,  che  può  esprimersi  come  σc’=γ
## 1
## *σ
c
,  sostituisce  il  valore  della  tensione
di  compressione  assegnato  inizialmente.  Partendo  da  questa  correzione  tutti  gli
altri   parametri   vengono   aggiornati,   il   legame   riferito   a   stati   tensionali
monoassiali viene così adattato agli stati tensionali pluriassiali.
Il materiale si fessura non appena una tensione principale raggiunge il valore di
resistenza limite a trazione riferita a uno stato tensionale monoassiale. La rottura
a   compressione   è   regolata   dal   dominio   riferito   alle   tensioni   principali
σ1>σ2>σ3, riportato in figura.

figura 2: Dominio di rottura
Per i dettagli si rimanda al manuale del programma [2].
Un  esempio  di  applicazione  del  codice  ADINA  e  ABAQUS  nella  simulazione
numerica  di  una  parete  in  muratura  di  pietrame  è  riportato  negli  atti  del
convegno nazionale sulle murature del 1996 [5], in questo studio i parametri del
modello sono stati calibrati attraverso il confronto tra i dati sperimentali ottenuti
da  prove  di  compressione  semplice  e  compressione  diagonale  e  i  risultati
ottenuti dalla modellazione numerica delle stesse.

2.3.2 Legame costitutivo a piani di danneggiamento di Gambarotta e
## Lagomarsino
Il  modello  è  stato  sviluppato  da  Gambarotta  e  Lagomarsino[3]  esplicitamente
per la modellazione della muratura.
Si considera un continuo omogeneo e ortotropo con degrado delle caratteristiche
meccaniche  che  può  avvenire  lungo  dei  piani  di  danneggiamento  individuati
dalla direzione dei giunti di malta orizzontali.
Tale degrado, come verrà meglio descritto in seguito, può essere di due diverse
nature:   il   danno   causato   dal   progressivo   distacco   dei   giunti   di   malta   o
schiacciamento  dei  mattoni  e  il  danno  legato  agli  scorrimenti  lungo  gli  stessi
giunti.
Il grado di danneggiamento viene caratterizzato da una variabile scalare (α) che
evolve durante l’analisi dal valore iniziale zero (materiale integro) fino al valore
uno che caratterizza le condizioni di rottura del materiale.














## 34



piani di
danneggiamento
volume di controllo
muratura
modello continuo
n
t
## (E
b,Gb,νb)
(Em,Gm,νm)
(En,Et,G,ν)
b
s

figura 3: Muratura reale e continuo equivalente, elastico ortotropo

Le caratteristiche elastiche del modello continuo vengono definite, partendo dalle
caratteristiche  elastiche  dei  mattoni  e  della  malta,  utilizzando  una  tecnica  di
omogeneizzazione.
Indicando  con  E
b
## ,G
b
## ,ν
b
i  moduli  elastici  dei  mattoni,  con  E
m
## ,G
m
## ,ν
m
i  moduli
elastici  della  malta,  con  b  ed  s  le  dimensioni  geometriche  rispettivamente  dei
mattoni  e  dei  giunti  di  malta,  le  caratteristiche  dell’insieme  omogeneo  risultano
date da:

## 1
## 1
## 2
## −
## −
## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## +=
## ⋅+⋅=
## ⎥
## ⎥
## ⎦
## ⎤
## ⎢
## ⎢
## ⎣
## ⎡
## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## −⋅
## ⋅⋅⋅
## −+=
## ⋅+⋅=
m
m
b
b
bbmm
m
m
b
b
m
bmbm
m
m
b
b
t
bbmmn
## GG
## G
## EEE
## EE
## EE
## E
## EEE
ηη
νηνην
ννηηηη
ηη

## Dove
η
m
e η
b
sono due rapporti geometrici e valgono :

mb
m
sb
s
ηη
η
## −=
## +
## =
## 1




Con riferimento agli assi n e t indicati in figura, la matrice di flessibilità assume
la forma :




## 35
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎦
## ⎤
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎣
## ⎡
## −
## −
## =
## −
## G
## EE
## EE
## K
tn
nn
el
## 1
## 00
## 0
## 1
## 0
## 1
## 1
ν
ν


σt
σn
τ
τ

figura 4: Componenti tensionali riferite al sistema di riferimento n,t

Il legame elasto-plastico che governa il modello è :

## ()
pl
el
## Kεεσ−⋅=


## Dove
σ = [σ
t
## ,σ
n
## ,τ]
t
è il vettore delle tensioni , i vettori  ε = [ε
t
## ,ε
n
## ,γ]
t
## ,
ε
pl
=  [0, ε∗,γ∗]
t
sono  rispettivamente  il  vettore  delle  deformazioni  totali  e  il
vettore delle deformazioni plastiche. Si noti come vengano trascurate il formarsi
di deformazioni plastiche in direzione t.
Il  vettore  delle  deformazioni  plastiche  si  ottiene  dalla  somma  del  contributo
dovuto ai mattoni (
ε
b
pl
) e di quello della malta (ε
m
pl
## ).
pl
bb
pl
mm
pl
εηεηε⋅+⋅=

Riferendosi  per  adesso  alla  sola  malta,  viene  assunto  che  le  componenti  di
deformazione plastica possano esprimersi nella forma:

## )()(
## )()(
fky
## Hh
m
pl
m
nnm
pl
m
## −⋅=
## ⋅⋅=
τα
σσαε
## (1)
α
m
è la variabile che indica lo stato di danneggiamento della malta, f è la forza di
attrito  che  si  instaura  nei  giunti  di  malta  allorché  la  tensione  normale  al  giunto
stesso è di compressione, H è definita come segue :














## 36

H(x)=1 ;         se x>0
H(x)=0 ;         se x<0

Serve  a  tenere  conto  del  carattere  monolatero  del  vincolo  offerto  dalla  malta,
questa infatti si suppone che esplichi la sua funzione e quindi possa danneggiarsi
solo  andando  in  trazione  mentre  quando  la  tensione  normale  al  piano  di
danneggiamento è di compressione a reagire è il contatto tra i mattoni adiacenti.
h  e  k  sono  due  funzioni  di
α
m
, sono  positive  e  si  azzerano  per α=0. Nel  lavoro
citato,  gli  autori,  per  non  appesantire  la  formulazione  del  modello  definiscono
tali funzioni in maniera estremamente semplice come :

mmt
mmn
ck
ch
α
α
## ⋅=
## ⋅=
## (2)
La  forza  di  attrito  f,  in  generale,  non  coincide  con  la  tensione  τ  anzi  è  proprio
l’eccedenza di
τ rispetto a f a generare gli scorrimenti plastici.
L’evoluzione  del  sistema,  vale  a  dire  dell’insieme  delle  variabili  di  stato
α  ,  f  e
delle  deformazioni  plastiche
ε
pl
e  γ
pl
è  governato  da  due  distinte  superfici  di
plasticizzazione e dai relativi legami associati.
La   prima   condizione   di   ammissibilità   plastica   determina   l’attivarsi   degli
scorrimenti  angolari  ed  è  da  prendere  in  considerazione  solo  se  la
σ
n
è  di
compressione:

## ⎪
## ⎪
## ⎩
## ⎪
## ⎪
## ⎨
## ⎧
## =⋅=⋅≥
## ⋅=
## ≤⋅+=
## 00
## 0
ss
pl
ns
fsign
f
φλφλλ
λγ
σμφ
## &&&
## &
## &
## ,
## )(
## (3)
La seconda determina l’attivarsi di incrementi di danno (incrementi di
α) :

## ⎪
## ⎩
## ⎪
## ⎨
## ⎧
## =⋅=⋅
## ≥
## ≤−=
## 0
## 0
## 0
dmmdmm
m
mmdm
## RY
φαφα
α
φ
## &
## &
## &
## (4)
Il  termine  Y
m
rappresenta  l’energia  disponibile  per  compiere  il  processo  di
danneggiamento,  mentre  R
m
rappresenta  l’energia  richiesta  perché  si  possa
estendere il danno, ed è una proprietà del materiale. Si possono avere incrementi
di danno solo quando l’energia disponibile eguaglia l’energia richiesta.
La  funzione  di  tenacità  viene  supposta  dipendente  solo  da  α
m
(fig.5)  mentre
l’energia disponibile (Y
m
) si può esprimere nella forma :

## ()()()()
## 2222
## 2
## 1
## 2
## 1
## 2
## 1
## 2
## 1
fcHcf
k
## H
h
## Y
mtnnmnnnm
## −⋅⋅+⋅⋅⋅=−⋅
## ∂
## ∂
## ⋅+⋅⋅
## ∂
## ∂
## ⋅=
τσστ
α
σσ
α




## 37
Rm,Ym
## Rmc
α
## 1
## Rm
## Ym

figura 5: funzione di tenacità

Allorché   si   raggiunge   il   massimo   di   R
m
(convenzionalmente   per   α=1)   il
materiale  giunge  a  rottura,  segue  quindi  una  fase  di  softening  nella  quale
l’energia   richiesta   per   successivi   incrementi   di   danno   decresce,   tendendo
asintoticamente a zero per α che tende a infinito.
Dalla condizione φ
dm
(α=1) = 0 si ricava il dominio di rottura, rappresentato nella
figura  6,  assieme  al  dominio  di  primo  snervamento  che  racchiude  tutti  gli  stati
tensionali caratterizzati da valore nullo del danno.

σn
σmr
## |τ |+μσn=τmr
## |τ |+μσn=0
τ
mr
## |τ |
Dominio elastico
Superficie di rottura

figura 6: Dominio elastico e di rottura

Dove i termini σ
mr
e τ
mr
possono essere considerati come i valori della resistenza
a trazione e a taglio della malta, essi risultano :


mtmnmrmr
mnmcmr
cc
cR
## /*
## /
στ
σ
## =
## ⋅=2
## (5)














## 38
La figura seguente riporta i risultati di una simulazione numerica che riproduce
una prova di trazione monoassiale sulla muratura. Si nota il successivo degrado
delle  caratteristiche  meccaniche  dovute  ovviamente  al  danneggiamento  per  la
progressiva fessurazione dei giunti di malta.
La  rottura  avviene,  coerentemente  con  il  dominio  di  rottura  precedentemente
illustrato, per il valore σ
mr
della tensione. Per scarichi che partono dal materiale
già  fessurato,  il  comportamento  è  lineare  con  rigidezza  orientata  all’origine,  si
ha  cosi  la  chiusura  completa  delle  fessure  se  il  carico  viene  completamente
rimosso.

## 1
## 0
σ
n/σmr
εn/εmr
## 12340

figura 7: simulazione numerica di una prova a trazione sulla malta

La  figura  seguente  illustra  invece  una  simulazione  di  una  prova  a  scorrimento
con σ
n
mantenuta  costante.  L’ordinata  del  grafico  riporta  le  tensioni  tangenziali
normalizzate rispetto a τ
r
- = τ
mr
- μσ
n
## .
Superato  il  valore  di  picco  della  resistenza  si  ha  una  fase  di  softening  con
tensione tangenziale che tende asintoticamente a  μσ
n
## .
La  figura  mostra  anche  il  complesso  comportamento  isteretico,  si  nota  subito
come  la  rigidezza  elastica  di  scarico  si  degradi  man  mano  che  aumenta  lo
scorrimento  da  cui  si  parte  a  scaricare,  e  allo  stesso  tempo  aumenta  l’area  del
ciclo di isteresi.
Scaricando  completamente  il  carico,  non  si  ha  il  recupero  completo  delle
deformazioni ma si ha uno scorrimento residuo.



## 39
## 1
γ/γr*
## 1
τ/τr*
## 234
μσn/τr*

figura 8: simulazione numerica di una prova a scorrimento sulla malta


Il  modello  plastico  dei  mattoni  è  del  tutto  analogo  alla  malta,  in  particolare  le
deformazioni plastiche si possono scrivere nella forma :

τ
σσε
## ⋅⋅=
## ⋅−⋅⋅=
bbt
pl
b
nnbbn
pl
bb
acy
## Hac
## )(
## (6)
Si fa notare che, mentre la malta poteva danneggiarsi solo a seguito di sforzi di
trazione,  il  danneggiamento  dei  mattoni  è  previsto  solo  se  si  è  in  presenza  di
sforzi di compressione.
In  pratica  si  sta  concentrando  tutto  il  danneggiamento  per  trazione  della
muratura  in  corrispondenza  della  malta,  mentre  tutto  il  danneggiamento  per
compressione in corrispondenza dei mattoni.

Per  i  mattoni  si  ha  la  sola  condizione  limite  che  regola  l’attivarsi  di  incrementi
di  danno  (manca  una  condizione  limite  di  scorrimento  analoga  alla  malta),  tale
condizione  è  definita  in  maniera  analoga  al  caso  della  malta,  vale  a  dire  come
differenza   tra   l’energia   disponibile   per   la   propagazione   del   danno(Y
b
)   e
l’energia richiesta(R
b
) e si aggiungerà alle due della malta per la risoluzione del
problema incrementale :

## ⎪
## ⎩
## ⎪
## ⎨
## ⎧
## =⋅=⋅
## ≥
## ≤−=
## 0
## 0
## 0
dbbdbb
b
bbdb
## RY
φαφα
α
φ
## &
## &
## &
## (7)















## 40
L’energia disponibile si può scrivere come :
## ()
## 2
## 2
## 2
## 1
## 2
## 1
τσσ⋅⋅+⋅−⋅⋅=
btnnbnb
cHcY

Mettendo assieme quanto detto fin ora, la soluzione del problema incrementale
si ottiene risolvendo il seguente problema complementare :

Caso di giunti in compressione (σ
n
## <0)

## ⎪
## ⎪
## ⎪
## ⎪
## ⎪
## ⎪
## ⎩
## ⎪
## ⎪
## ⎪
## ⎪
## ⎪
## ⎪
## ⎨
## ⎧
## =⋅=⋅
## =⋅=⋅
## =⋅=⋅
## ≥≥≥
## ⋅=
## ≤−=
## ≤−=
## ≤⋅+=
## 0
## 0
## 0
## 000
## 0
## 0
## 0
dbbdbb
dmmdmm
ss
bm
pl
m
bbdb
mmdm
ns
fsign
## RY
## RY
f
φαφα
φαφα
φλφλ
ααλ
λγ
φ
φ
σμφ
## &
## &
## &
## &
## &&
## &&
## &
## &
## &
## ,,
## )(
## (8)
Caso di giunti in trazione (σ
n
## >0)

## ⎪
## ⎪
## ⎪
## ⎩
## ⎪
## ⎪
## ⎪
## ⎨
## ⎧
## =⋅=⋅
## =⋅=⋅
## ≥≥
## ≤−=
## ≤−=
## 0
## 0
## 0,0
## 0
## 0
dbbdbb
dmmdmm
bm
bbdb
mmdm
## RY
## RY
φαφα
φαφα
αα
φ
φ
## &
## &
## &
## &
## &&
## (9)
Il  dominio  completo  si  ottiene  considerando  il  precedente  e  aggiungendo  la
condizione di rottura per i mattoni che si esprime come φ
db
## (α
b
## =1) = 0, (fig.9).
Ai  simboli  gia  incontrati  si  aggiungono  le  resistenze  a  compressione  e  a  taglio
dei mattoni che risultano :

bnbcbr
cR/⋅=2σ
btbnbrmr
cc/⋅=στ

Per quanto riguarda le funzioni di tenacità R, gli autori propongono la seguente
definizione :
R(α)=R
c
∗α          se 0<α <1
R(α)=R
c
## ∗α
## −β
se α >1



## 41
σn
σmr
## |τ |+μσn=τmr
## |τ |+μσn=0
τmr
## |τ |
Dominio elastico
Superficie di rottura malta
Superficie di rottura
mattoni
Superficie di rottura
globale
τbr
σbr

figura 9: dominio elastico e di rottura globale

Si  conclude  la  descrizione  di  questo  modello  con  delle  considerazioni  sui
parametri che lo caratterizzano e la loro determinazione. In precedenza si è fatto
notare che il danneggiamento globale della muratura è stato attribuito per intero
alla malta nel caso in cui le  tensioni normali ai piani di danneggiamento fossero
di  trazione,  e  interamente  ai  mattoni  nel  caso  di  compressione.  Ne  deriva  che  i
parametri di resistenza e deformabilità che caratterizzano le condizioni di rottura
a  trazione  della  malta,  devono  essere  visti  come  parametri  di  resistenza  e
deformabilità  a  trazione  della  muratura.  Allo  stesso  modo  i  parametri  che
caratterizzano  il  comportamento  a  compressione  dei  mattoni,  rappresentano  la
resistenza a compressione dell’intera muratura.

I parametri necessari a caratterizzare il modello si ottengono attraverso semplici
prove   effettuate   sui   singoli   componenti   e   su   campioni   di   muratura,   in
particolare:
## -
prove sui mattoni :
si determinano i parametri elastici dei mattoni  E
b
## ,G
b
## ,ν
b
, e la resistenza
ultima a taglio dei mattoni τ
br
## .

- prove sulla malta :
si determinano i parametri elastici della malta  E
m
## ,G
m
## ,ν
m
## .

## -
prova di compressione monoassiale su campione di muratura :
misurando  lo  sforzo  e  la  deformazione  a  rottura  si  ricavano  σ
br
e  c
bn
## .
Seguendo il ramo di softening si determina β
b
## .

## -
prova di scorrimento su un campione di giunto di malta :
si  tratta  di  una  prova  su  tripletta  con  tensione  normale  costante,
misurando la resistenza e la deformazione a rottura si determina τ
mr
e

c
mt
Eseguendo  più  prove  variando  σn,  si  ottiene  il  coefficiente  di  attrito
μ. Infine seguendo il ramo di softening si ottiene β
m
## .














## 42
2.4 - Modellazione a telaio
Nell’  ambito  dei  modelli  monodimensionali,  occorre  citare  la  modellazione  a
telaio.  Essa  si  applica  a  strutture  murarie  con  distribuzione  regolare  di  aperture,
in  cui  sono  facilmente  riconoscibili  i  maschi  murari  collegati  a  fasce  di  piano
tramite una porzione di muratura compresa tra i due, tale zona risulta sottoposta a
una grande azione di confinamento.
Sia  i  maschi  murari  che  le  fasce  di  piano  vengono  modellati  con  elementi
monodimensionali, alle estremità di ogni elemento si prevedono delle zone rigide
che modellano la muratura di collegamento.
L’estensione  dei  tratti  rigidi  di  ogni  asta  non  coincide  con  le  reali  dimensioni
geometriche della muratura di  collegamento  ma va opportunamente valutata.
Per  gli  elementi  trave  si  considera  sia  la  deformabilità  flessionale  che  quella  a
taglio.

zone rigide
elemento monodimensionale
deformabile flessionalmente e a taglio

figura 10: Schema a telaio equivalente alla muratura : si distinguono gli elementi
asta  deformabili  che  modellano  i  setti  e  le  fasce,  e  gli  estremi  rigidi
che modellano la muratura di collegamento.

Il  modello  a  telaio  equivalente  viene  comunemente  usato  per  strutture  in
calcestruzzo  debolmente  armato  con  presenza  di  setti  e  murature  confinate.  La
limitazione  maggiore  di  tale  modellazione  è  di  non  considerare  le  escursioni
dell’asse  neutro  all’interno  della  parete  che  portano  a  una  valutazione  errata
soprattutto  dei  tagli  degli  elementi  che  collegano  i  setti.  L’estensione  al  caso



## 43
delle  murature  richiede  comunque  maggiore  accortezza,  la  non  resistenza  a
trazione infatti caratterizza in maniera predominante la risposta della struttura e,
se non presa correttamente in conto, accentua i limiti di una schematizzazione a
telaio.
A  questo  proposito  sono  due  le  strade  comunemente  adottate,  una  è  quella  di
considerare  elementi  con  sezione  costante  e  rigidezza  ricavata  da  opportuni
legami costitutivi non lineari [6], l’altro approccio utilizzato è di considerare gli
elementi monodimensionali lineari di sezione limitata alla sola parte compressa
in un processo step by step.
Se  si  segue  quest’ultimo  approccio,  il  modello  chiaramente  può  considerarsi  a
geometria variabile.
## P
## P
Trave a sezione
variabile
## A = A
cost
Trave a sezione
variabile
## L/2
e
## 2
u
u
## L/2
e
## 1
Modello monodimensionale

Figura   11:   Generico   elemento   asta   in   un   passo   dell’analisi:   si   possono
distinguere le tre porzioni in cui risulta divisa la trave, la porzione
centrale a sezione costante e le porzioni laterali a sezione variabile.

2.4.1 Metodo SAM
Un  approccio  che  può  considerarsi  una  via  di  mezzo  tra  un  modello  a  telaio
equivalente  e  un  metodo  POR  è  proposto  da  Magenes  e  Calvi  [7].  La  generica
parete  viene  anche  qui  ricondotta  a  un  telaio  composto  da  elementi  trave  che,
modellano  sia  i  maschi  murari  che  le  fasce  di  piano  e  vengono  previste  delle
zone rigide alle estremità di ogni asta.
Ad   ogni   maschio   murario   viene   associata   una   legge   taglio-spostamento
orizzontale  di  tipo  elasto-plastico  (fig.11),  il  valore  del  taglio  ultimo  è  dato  dal
minore tra i valori corrispondenti ai diversi meccanismi di rottura considerati nel
capitolo  precedente  (rottura  per  flessione,  rottura  per  scorrimento,  rottura  per
fessurazione  diagonale).  Lo  spostamento  limite  viene  fissato  in  termini  di
distorsione ultima (vedi capitolo 1).














## 44

## (a)                                                (b)

Figura 12:   Legami costitutivi; a) comportamento flessionale dei maschi e della
fasce  e  comportamento  a  taglio  dei  maschi,  b)  comportamento  a
taglio delle fasce

Il  legame  costitutivo  degli  elementi  che  modellano  le  fasce  è  lineare  fino  al
valore  del  taglio  massimo,  raggiunto  il  quale  si  ha  una  rottura  fragile.  Per  la
valutazione del taglio ultimo, per tali elementi, si considerano solo i meccanismi
di   rottura   a   scorrimento   e   per   fessurazione   diagonale,   mentre   non   viene
considerata la possibilità che una fascia possa rompersi per flessione.
Parlando  della  modellazione  delle  fasce,  va  puntualizzato  che,  al  contrario  dei
maschi, non si dispone di sufficienti studi sperimentali [1], quindi ogni tentativo
di  modellazione  teorica  è  destinata  a  portare  in  sé  un  certo  margine  di
incertezza.
L’analisi con il metodo SAM viene condotta per incrementi fissati del carico. Il
primo  passo  consiste  nel  determinare  la  distribuzione  dei  tagli  nei  maschi  che
equilibra  il  carico,  secondo  la  rigidezza  di  ognuno,  imponendo  l’eguaglianza
degli spostamenti orizzontali di tutti i punti afferenti a un impalcato.
Noti  i  tagli,  si  determinano  i  momenti  alle  estremità  dei  maschi,  considerando
come punto di nullo del diagramma del momento quello di inizio passo. A inizio
analisi si devono fissare le posizioni iniziali dei punti di nullo per tutti i maschi e
questo verrà fatto in base alla condizione di vincolo di ciascuno.
## Mps
## Mfs
## Mfd
## Mpi
Mfs = (Mps + Mpi)  (Ks/(Ks + Kd))
Mfd = (Mps + Mpi)  (Kd/(Ks + Kd))
maschio inferiore
maschio superiore
fascia


figura 13: particolare del nodo trave colonna dello schema a telaio.




## 45
Si  procede  quindi  a  imporre  l’equilibrio  alla  rotazione  di  ogni  nodo  (fig.  13),
ricavando così i momenti alle estremità delle fasce, e quindi i tagli agenti in ogni
fascia.
Lo  sforzo  normale  agente  nelle  fasce  è  direttamente  valutabile  dai  tagli  di
estremità  dei  maschi,  quindi  è  possibile  verificare  se  a  fine  passo  i  tagli  agenti
nelle fasce superano il valore corrente del taglio ultimo.
Se in qualche fascia si è superato il taglio limite, si riporta il valore del taglio al
valore  massimo,  l’eccedenza  di  momento  che  ne  scaturisce  viene  ridistribuita
agli  elementi  dei  nodi  che  afferiscono  a  tale  fascia  secondo  le  rigidezze  di
ognuno.
Tutti  gli  elementi  interessati  dalla  ridistribuzione  subiscono  una  variazione  del
diagramma  del  momento  mentre  viene  mantenuto  costante  il  taglio  agente.  I
punti di nullo dei momenti nei maschi subisce quindi delle variazioni, in questo
modo  si  sta  tenendo  conto  delle  mutate  condizioni  di  vincolo  dei  maschi
interessati dalla rottura di una fascia.

Dopo   aver   effettuato   tutte   le   ridistribuzioni   relative   alle   fasce   rotte,   si
determinano  gli  sforzi  normali  agenti  nei  maschi,  imponendo  l’equilibrio  alla
traslazione verticale dei nodi, partendo da quelli del piano più alto.
A  questo  punto,  per  ogni  maschio,  si  dispone  sia  dei  tagli  che  degli  sforzi
normali  di  fine  passo  e  si  può  effettuare  una  verifica  sull’ammissibilità  del
valore  dei  tagli  rispetto  ai  criteri  di  snervamento  prescelti.  Se  si  riscontrano
valori  di  taglio  maggiori  del  taglio  massimo  corrente,  si  procede  a  ridistribuire
l’eccedenza di taglio a tutti i tagli ancora elastici e la rigidezza del maschio che
è giunto a snervamento, nel passo successivo, verrà considerata nulla.

Il  metodo  nella  sua  semplicità  ha  il  pregio  di  tenere  in  considerazione  molti
aspetti essenziali della risposta di una parete muraria:

## -
Coglie  la  variazione  di  sforzo  normale  nei  maschi  durante  l’analisi,
elemento  essenziale  poiché  influenza  la  resistenza  a  taglio  dei  maschi
stessi.
## -
Prevede  tutti  i  meccanismi  di  rottura  cui  può  essere  soggetto  un
pannello murario.
## -
Prevede  la  variazione  delle  condizioni  di  vincolo  cui  è  soggetto  un
maschio murario a seguito della rottura di una fascia.

Il  metodo  SAM  è  stato  applicato  a  diverse  pareti,  che  in  precedenza  erano  state
oggetto  di  studi  sperimentali  e  teorici,  di  cui  si  conosceva  con  sufficiente
approssimazione  la  risposta  a  carichi  orizzontali,  sia  in  termini  di  taglio  ultimo
che di meccanismo di collasso[1].
Ciò  ha  permesso  di  valutare  l’attendibilità  dei  risultati  ottenuti  con  il  metodo
SAM  che  si  è  mostrato  capace  di  prevedere  con  sufficiente  approssimazione  la
risposta globale di una parete muraria regolare.














## 46
2.5 – Analisi limite
Con un approccio di questo tipo si è in grado di determinare il carico ultimo della
struttura e il meccanismo di collasso, è quindi ben lontano da tutti gli altri metodi
di  analisi  che  restituiscono  l’intera  risposta  della  struttura.  Per  la  sua  semplicità
tuttavia    può  essere  applicato  contestualmente  ad  altri  metodi  più  raffinati,  in
modo  da  offrire  uno  strumento  di  verifica  dei  risultati  ottenuti  ed  evitare  così
errori  grossolani.  In  determinate  circostanze  e  per  certe  tipologie  costruttive,  di
cui   si   discuterà   in   seguito,   tale   approccio   diviene   forse   l’unico   metodo
applicabile   e   senz’altro   il   più   semplice   per   eseguire   delle   valutazioni   di
vulnerabilità sismica.

La  muratura  viene  modellata  come  un  insieme  di  corpi  rigidi,  liberi  di  ruotare
attorno  a  delle  cerniere  cilindriche  che  si  possono  formare  all’interno  della
muratura.  L’insieme  dei  centri  di  rotazione    assoluti  e  relativi  definiscono  il
meccanismo di collasso.
A  questo  punto  si  imposta  un  problema  di  analisi  limite  per  determinare  il
moltiplicatore  dei  carichi  che  attiva  il  meccanismo  di  collasso  ipotizzato.  Il
moltiplicatore  del  carico  così  trovato  è  un  moltiplicatore  cinematico,  quindi
costituisce  un  estremo  superiore  del  reale  moltiplicatore  a  collasso.  Se  si
potessero considerare tutti i possibili meccanismi di collasso, il moltiplicatore dei
carichi  sarebbe  il  più  piccolo  dei  moltiplicatori  cinematici  trovati;  nei  casi  reali
non  è  chiaramente  possibile  contemplare  tutti  i  meccanismi  di  collasso,  si
dovranno scegliere un certo numero di meccanismi, che sembrano più probabili e
individuare il moltiplicatore dei carichi che attiva ognuno di questi.
Il  rischio  cui  si  va  incontro  è  che  se  non  si  contempla  il  reale  meccanismo  di
collasso si sovrastima il carico ultimo della struttura.
A questo inconveniente può ovviarsi determinando una distribuzione di tensioni
staticamente    equilibrata    e    plasticamente    ammissibile    che    porti    alla
determinazione  di  un  moltiplicatore  statico  relativamente  vicino  al  più  piccolo
dei  cinematici  calcolati  e  che  assieme  a  questo  individui  un  intervallo  in  cui  è
compreso il reale moltiplicatore a collasso della struttura.

Da   quanto   detto   fin’ora   che   la   fase   più   delicata   è   l’individuazione   dei
meccanismi  di  collasso  dell’intera  struttura,  questi  sono  ottenuti  combinando  i
meccanismi  di  collasso  elementari  dei  singoli  pannelli  murari,  descritti  nel
capitolo 1 (ribaltamento fuori piano, ribaltamento/scorrimento nel piano).
Per  una  corretta  valutazione,  è  di  fondamentale  importanza  uno  studio  della
tipologia  edilizia,  delle  carenze  costruttive  e  del  quadro  fessurativo.  Se  la
struttura  in  esame,  ad  esempio,  ha  degli  orizzontamenti  rigidi  ben  ammorsati  ai
muri  e  le  pareti  ben  collegate  tra  loro,  si  prevederanno  dei  meccanismi  di
collasso globali con le singole pareti caratterizzate da collassi di secondo modo.
Se   invece   la   struttura   presenta   pareti   scarsamente   collegate   alla   restante
muratura,  si  andranno  a  prevedere  meccanismi  di  ribaltamento  della  singola
parete.




## 47
In riferimento ai meccanismi di collasso di intere strutture quindi, analogamente
a  singoli  pannelli,  si  può  distinguere  un  collasso  di  secondo  modo  nel  quale  le
pareti,  sollecitate  nel  proprio  piano,  perdono  la  possibilità  di  portare  carico;
questo  di  solito  avviene  dopo  che  la  parete  ha  subito  dei  grandi  spostamenti
oppure  dopo  un  grande  numero  di  cicli  di  carico,  e  un  meccanismo  di  primo
modo che vede, in genere,  il ribaltamento delle pareti esterne dell’edificio [8].



figura 14: Schematizzazione di un collasso strutturale di primo e di secondo
modo


## (a)

















## 48
## (b)

figura15: Esempi di collassi incipienti: (a) di primo modo;
(b) di secondo modo

I  meccanismi  di  secondo  modo  più  immediati  che  possono  prevedersi  per  una
parete piana sono :

## -
Meccanismo  a  mensole  indipendenti  :  le  fasce  di  piano  giungono  a
rottura  e  i  maschi  murari  allineati  verticalmente  si  comportano  come  un’unica
mensola.  L’accoppiamento  delle  mensole  è  garantito  dalla  capacità  di  trasferire
sforzo normale da parte delle fasce (fig. 16).
Un meccanismo del genere approssima bene il comportamento ultimo di pareti in
cui le fasce raggiungono la rottura per taglio prima dei maschi.
λF2
λF1
## G1G2G3
## Tr
## Tr
## Tr
## Tr

figura 16: meccanismo di collasso per ribaltamento delle mensole murarie



## 49
Supponendo  che  le  fasce  anche  se  rotte  riescono  a  trasmettere  un  taglio  residuo
## T
r
e imponendo l’equilibrio limite, si ha:
## ∑
## ⋅
## =
## =
## ∑
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ∑
## ⋅+⋅
## ∑
## =⋅⋅
## =
## ===
np
n
nn
ntestabilizza
ntestabilizza
nm
i
np
n
n
rii
i
i
np
n
nn
hF
## M
MTb
b
GhF
## 1
## 111
## 2
λ
λ

Dove si è indicato con F
n
e h
n
la forza e la quota dell’ n-esimo impalcato, con n
p

il  numero  di  impalcati,  con  G
i
e  b
i
rispettivamente  il  peso  e  la  larghezza  dell’i-
esima  mensola,  con  n
m
il  numero  di  mensole,  con  T
n
ri
il  taglio  trasmesso  alla  i-
esima mensola dalla fascia del piano n-esimo.



## -
Ribaltamento  dei  maschi  murari  di  un  piano  :  Tutti  i  maschi  murari  di
un  piano  ribaltano  rigidamente.  Se  i  maschi  hanno  tutti  le  stesse  dimensioni,  si
può   ammettere   che   le   fasce   si   mantengono   integre,   altrimenti   si   deve
contemplare  una  rottura  a  taglio  delle  stesse  per  garantire  la  congruenza  degli
spostamenti   verticali,   visto   che   tutti   i   maschi   devono   subire   lo   stesso
spostamento orizzontale (fig. 17).
Tale  meccanismo  può  essere  considerato  attendibile  in  circostanze  opposte  a
quelle del meccanismo precedente.

λF1
λF2
## G1
## G2G3

figura 17: meccanismo di collasso per ribaltamento di tutti i maschi murari
appartenenti a un piano
















## 50
## ∑
## Δ⋅
## =
## =
## ∑
## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## ⋅+⋅
## ∑
## =Δ⋅⋅
## =
## ==
np
nn
nn
ntestabilizza
ntestabilizza
nm
i
ii
i
i
np
nn
nn
hF
## M
MbN
b
GhF
λ
λ
## 1
## 2
## *

Dove  si  è  indicato  con  n*  il  piano  in  cui  si  sta  verificando  il  meccanismo,  con
## Δh
n
la quota relativa al piano n* del piano n-esimo, con n
p
il numero di piani, con
n
i
il numero di maschi nel piano n*, con G
i
, b
i
peso e larghezza dei maschi, con
## N
i
lo scarico verticale sull’i-esimo maschio.



-    Rottura diagonale e ribaltamento dei maschi murari di un piano: Come
descritto  nel  capitolo  1,  quando  un  pannello  murario  diventa  più  tozzo,  nel
ribaltare  è  probabile  che  il  pannello  stesso  si  fessura  secondo  una  diagonale  (la
cui inclinazione non è a priori ipotizzabile) e solo una porzione di esso subisce il
ribaltamento (fig. 18).
Nella rappresentazione sotto riportata si è voluto mostrare, a differenza del caso
precedente, il caso di maschi con differente larghezza.
## G1
λF1
λF2
## G3
## G2
## N1N2N3

figura 18: meccanismo di collasso per ribaltamento delle mensole murarie

L’espressione  del  moltiplicatore  a  collasso  dei  carichi  è  del  tutto  analoga  al
caso precedente, l’unica differenza riguarda i termini Gi che stavolta indicano il
peso delle porzioni di maschi che ruotano e non il peso totale





## 51
## ∑
## Δ⋅
## =
## =
## ∑
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ⋅+⋅
## ∑
## =Δ⋅⋅
## =
## =
## =
np
nn
nn
ntestabilizza
ntestabilizza
nm
i
ii
i
i
np
nn
nn
hF
## M
MbN
b
GhF
λ
λ
## 1
## 3

Nell’esempio  proposto,  si  è  supposto  che  i  maschi  si  fessurano  lungo  la
diagonale, come accennato prima, non c’è alcun motivo per scegliere a priori una
direzione  rispetto  a  un'altra.  Il  modo  corretto  di  procedere  per  determinare  il
moltiplicatore  relativo  a  tale  meccanismo  è  quello  di  mantenere  l’inclinazione
(α) della fessura generica e calcolare λ=λ(α). Il moltiplicatore e la direzione da
considerare saranno quelli per cui tale funzione ha un minimo.
Nel far variare α da 0° a 90°, fin tanto che la fessura interseca il lato verticale del
maschio,  la  formula  riportata  sopra  va  modificata  soltanto  relativamente  ai
termini  G
i
e  ai  relativi  bracci.  Solo  quando  la  fessura  interseca  la  sezione
superiore del maschio, cambia il contributo relativo agli scarichi N
i
## .





Come già accennato prima, lo studio del quadro fessurativo assume un ruolo
di  fondamentale  importanza  per  l’analisi  di  strutture,  soprattutto  se  di  carattere
storico,   questo   è   infatti   l’unico   strumento   capace   di   mostrare   il   reale
funzionamento della struttura, rivela inoltre tutti i meccanismi attivati in seguito
a eventi sismici precedenti che con ogni probabilità verranno riattivati a seguito
di un nuovo sisma.
Le  figure  seguenti  mostrano  come  si  può  giungere  all’individuazione  dei  più
probabili meccanismi di collasso, partendo dallo studio del quadro fessurativo, in
un esempio di intervento di restauro e adeguamento sismico [8].
















## 52

figura 19: Rilievo di un quadro fessurativo.




## 53



figura 20: Individuazione dei meccanismi di collasso




















## 54
Nell’ambito  di  strutture  che  presentano  un  comportamento  “scatolare”,  in  cui
cioè i meccanismi di primo modo sono impediti dalle connessioni tra le pareti e
tra  pareti  e  impalcati  e  ogni  singola  parete  viene  sollecitata  nel  proprio  piano,
sono  applicabili  tutti  i  metodi  fino  a  qui  esposti.  Ecco  che  l’importanza  di  un
approccio  basato  sull’analisi  limite  può  essere  considerata  marginale  e  il  suo
utilizzo limitato alla verifica di risultati ottenuti per altre vie e con altri modelli.

Per  strutture  nelle  quali  sono  predominanti  i  moti  di  ribaltamento  della  pareti,
risulta  difficile  applicare  metodi  di  calcolo  diversi  da  quelli  dell’analisi  limite.
Del  resto  tali  strutture  hanno  certamente  un  comportamento  fragile,  si  può
ipotizzare   quindi   che   si   mantengano   in   ambito   lineare   fino   al   collasso
(ribaltamento  della  prima  parete),  quindi  l’unica  grandezza  significativa  diventa
il carico ultimo.
L’approccio  tramite  l’analisi  limite  diventa  ancora  più  indicato  in  tutti  i  casi  in
cui  non  si  riesce  a  giungere,  con  sufficiente  approssimazione,  a  una  stima  dei
parametri meccanici della muratura. Si pensi ad esempio al caso di costruzioni di
carattere storico, caratterizzate da una notevole disomogeneità in cui i valori dei
parametri  meccanici  subiscono  notevoli  variazioni  tra  un  punto  e  l’altro  della
stessa  costruzione.  In  casi  del  genere  i  risultati  di  modellazioni  sofisticate
perdono  di  valore  visto  il  carattere  aleatorio  dei  dati  di  partenza.  Per  il  calcolo
tramite  l’analisi  limite  non  viene  utilizzato  nessun  parametro  di  resistenza  o  di
deformazione ma solo il peso della muratura.


























## 55


## Bibliografia

[1] G.  Magenes,  D.  Bolognini,  C.  Braggio  (A  cura  di):  “Metodi  semplificati
per  l'analisi  sismica  non  lineare  di  edifici  in  muratura”,  CNR-Gruppo
Nazionale per la Difesa dai Terremoti - Roma, 2000, 99 pp.
[2] ©ADINA  ,R&D  Inc.    Report  ARD  01-7,    ADINA  teory  and  modeling
guide.
[3] L.  Gambarotta  e  S.  Lagomarsino  :  “Damage  models  for  the  seismic
response of brick masonry shear walls. Part I: The mortar joint model and
its  applications.  Part  II:  The  continuum  model  and  its  application”.
Earthquake Engineering and Structural Dynamic, 26 424-462.
[4] Hilleborg,  M.  Mooder  &  P.E.  Peterson:  “Analysis  of  crack  formulation
and  crack  growth  in  concrete  by  means  of  fracture  mechanics  and  finite
element”,Cement and concrete research, Vol. 6, pp. 773 – 782, 1976.
[5] G. C. Beolchini, F. Grillo & G. Valente:  “La  modellazione  numerica  del
comportamento  di  una  muratura  in  pietrame”,  Convegno  nazionale  “La
meccanica delle murature tra teoria e progetto” Messina, 18-20 Settembre
## 1996.
[6] F.  Braga,  M.  Dolce:  “Un  metodo  per  l’analisi  di  edifici  multipiano  in
muratura  antisismici”,  Proceeding  of  the  6th  I.B.M.a.C.,  Roma,  1982,
ANDIL, pp.1088-1099.
[7] G.  Magenes,  G.M.  Calvi:  “Prospettive  per  la  calibrazione  di  metodi
semplificati    per    l’analisi    sismica    di    pareti    murarie”,    Convegno
nazionale”La  meccanica  delle  murature  tra  teoria  e  progetto”,  Messina,
## 18-20 Settembre, 1996.
[8] Giuffrè (A cura di:): “Sicurezza e conservazione dei centri storici – Il caso
## Ortigia”, Ed. Laterza.
























## 56




## 3 A MODELLAZIONE DELLE MURATURE
## MEDIANTE L’UTILIZZO DI MACROMODELLI


## Premessa

Le difficoltà  connesse con l’utilizzo degli elementi finiti per la modellazione di
edifici   in   muratura   hanno   determinato   l’esigenza   di   ricercare   soluzioni
alternative per lo studio degli edifici in muratura, soprattutto in ambito sismico.
Per questo motivo diversi autori hanno introdotto dei modelli discreti equivalenti
a  porzioni  di  pareti  murarie,  in  grado  di  descrivere  macroscopicamente  il
comportamento  d’insieme  dell’elemento  rappresentato.  Tali  elementi  sono  noti
come
macro-elementi   e   consentono   una   descrizione   del   comportamento
d’insieme  di  un  intero  edificio  con  un  costo  computazionale  ridotto  rispetto  ad
una modellazione agli elementi finiti.
Escludendo i modelli a puntone equivalente, di cui si cita soltanto il modello di
## Calderoni
et al. [3,4], nei quali la muratura viene modellata tramite la definizione
di   un   puntone   equivalente   la   cui   sezione   e   inclinazione   devono   essere
opportunamente  valutate  (fig.  2),  sulla  base  della  ricerca  da  noi  condotta,  il
primo  tentativo  di  modellare  la  muratura  tramite  un  macroelemento  è  dovuto  a
Braga   e   Liberatore   (1990)   [1,2],   con   l’introduzione   di   un   macroelemento
bidimensionale denominato
a ventaglio multiplo poiché è composto da una serie
di conci elementari di forma triangolare (fig.1) compressi.

figura 1: Macromodello a ventaglio multiplo



## 57


## (a)                                                                  (b)

figura 2: Modello a puntone equivalente; a) individuazione della sezione e della
inclinazione  del  puntone  equivalente  al  pannello,  b)  intera  parete
modellata con i puntoni equivalenti

Il  modello  si  basa  su  delle  ipotesi  formulate  sullo  stato  tensionale  che  mirano  a
simulare la resistenza nulla a trazione della muratura. I parametri cinematici che
governano  il  modello  sono  sei,  assunti  coincidenti  con  le  due  traslazioni  e
rotazione dei punti medi delle sezioni di estremità del pannello.

Le applicazioni eseguite utilizzando tale modello (alcune delle quali riportate nel
seguito), mostrano una sovrastima eccessiva del carico limite della struttura. Tale
circostanza  come  evidenziato  anche  da  Magenes  [5]  è  dovuta  al  fatto  che  tale
modello  non  prende  in  considerazione  in  alcun  modo  i  meccanismi  di  rottura  a
taglio e a scorrimenti che possono verificarsi in un pannello murario.

3.1 - Macromodello a geometria variabile
Il  modello  è  stato  Proposto  da  D’  Asdia  e  Viskovic,  nell’ambito  del  sesto  e
settimo convegno nazionale A.N.I.D.I.S. [6], per lo studio di pareti piane caricate
da  forze  orizzontali  nel  proprio  piano.  Successivamente  è  stato  aggiornato  per
essere applicato allo studio di strutture tridimensionali [7].
Il modello si presta bene a modellare strutture regolari, nelle quali si distinguono
nettamente  da  una  parte  gli  elementi  “maschio”  e  “fascia  di  piano”  e  dall’altra
l’elemento “nodo di collegamento”, atto a modellare la muratura compresa tra i
maschi e le fasce.
Il  modello  è  basato  sulla  introduzione  di  macroelementi  costituiti  da  un  numero
limitato di elementi finiti elastico-lineari di forma triangolare. Tali elementi finiti
sono a deformazione costante, caratterizzati cioè da un campo di spostamenti che
dipendono linearmente dagli spostamenti dei vertici.
Le dimensioni dei singoli elementi finiti sono paragonabili a quelle del pannello,
questa scelta è giustificata dalla considerazione che il materiale è elastico lineare
a  compressione  e  dal  mantenere  l’ipotesi  di  sezioni  piane.  In  tali  circostanze
infatti   lo   stato   deformativo   e   tensionale   di   un   corpo   è   completamente














## 58
determinabile  tramite  gli  spostamenti  dei  vertici,  per  cui  si  possono  utilizzare
elementi finiti di dimensioni paragonabili al pannello stesso .

Vengono definiti due macroelementi distinti, rappresentati nella figura seguente,
il primo è pensato per modellare i pannelli murari costituiti dai maschi murari e
dalle  fasce  di  piano  di  un  edificio,  il  secondo  invece  serve  a  modellare  la
porzione di muratura che funge da collegamento proprio tra i maschi e le fasce.
Il  principio  di  base  del  modello  è  di  modificare  la  geometria  dell’elemento
pannello al fine di escludere la porzione di muratura in cui le tensioni di trazione
superano  il  valore  di  resistenza  della  muratura.  In  modo  da  riprodurre  la
parzializzazione    progressiva    della    sezione    trasversale    del    pannello    con
conseguente degrado di rigidezza globale del sistema.
F1yF2y
F1xF2x
F3xF4x
F4yF3y
## (a)(b)


figura  3:  a)  Rappresentazione  del  macromodello  per  la  modellazione  di  un
pannello  murario  con  indicate  le  forze  nodali  che  caratterizzano,  in
termini    di    risultanti,    lo    stato    tensionale    nel    pannello.    b)
Rappresentazione   del   macroelemento   per   la   modellazione   della
muratura di collegamento tra maschi e fasce di piano.




## 59
## *
## **
Armature verticali
Armature orizzontali o
cordoli
## **
## *

figura 4: Assemblaggio di una parete piana.

Gli  elementi  finiti,  nel  pannello,  sono  disposti  in  maniera  tale  che,  variando  la
forma  dei  singoli  triangoli,  la  geometria  del  pannello  possa  essere  variata,
durante l’analisi, in funzione dello stato tensionale agente sul pannello stesso, in
modo da escludere la porzione di sezione in cui la trazione ha superato il limite
ammissibile.
Nella  figura  seguente  si  mostra  come  varia  la  geometria  del  pannello  per
simulare la parzializzazione della sezione. Si è indicato lo stato tensionale nelle
sezioni di estremità in termini di sforzo normale (N), taglio (T) e momento (M).
Inoltre  si  considera  che  la  muratura  possa  offrire  una  piccola  resistenza  a
trazione.














## 60
## N
## T
## M
## T
## M
## N


figura 5: Pannello con geometria variata

I triangoli esterni dell’elemento di collegamento sono quelli che possono variare
la loro forma per seguire le variazioni di geometria dei maschi o delle fasce che
collegano.  I  nodi  e  i  triangoli  interni,  invece,  sono  a  geometria  fissata.  Nel
rappresentare l’elemento di collegamento, si sono indicati con un cerchio vuoto i
nodi  a  geometria  fissa  e  con  un  cerchio  pieno  i  nodi  la  cui  posizione  viene
aggiornata durante l’analisi.
Nella figura seguente è schematizzato l’assemblaggio tra due pannelli (maschio e
fascia)  tramite  un  elemento  di  collegamento,  in  configurazione  variata,  nella
quale   cioè   la   geometria   dei   pannelli   è   stata   aggiornata   a   causa   della
parzializzazione  della  sezione.  Si  può  notare  altresì  la  variazione  di  forma  che
devono  subire  i  triangoli  esterni  dell’elemento  di  collegamento  per  continuare  a
garantire la congruenza.




## 61
Area del pannello in trazione
Maschio murario
Fascia di piano

figura   6:   Assemblaggio   di   un   maschio   murario   e   una   fascia,   mediante
l’interposizione  di  un  elemento  di  collegamento,  in  configurazione
variata.


L’analisi viene condotta per passi successivi di carico, alla fine di ogni passo si
determinano  le  forze  nodali  e  quindi  la  risultante  in  termini  di  sforzo  assiale,
taglio e momento agente nel pannello.
In  base  a  tale  risultante,  si  determina  la  distribuzione  degli  sforzi  lungo  la
sezione (fig. 5),  viene quindi variata la posizione dei nodi esterni in maniera da
escludere la zona fessurata. La geometria così ottenuta sarà quella di partenza per
il passo successivo.
E’ interessante notare come, man mano che la parzializzazione della sezione
aumenta,  la  forma  e  il  comportamento  del  pannello  si  avvicinano  sempre  più  a
quelli  di  un  puntone,  cogliendo  in  pieno  la  reale  tendenza  della  muratura  di
resistere  ai  carichi  assumendo  configurazioni  di  equilibrio  con  sviluppo  di  sole
tensioni di compressione.















## 62
## TT
zona fessurata
Puntone interno
alla muratura
muratura realemodello teorico


figura 7: Comportamento a puntone della muratura reale e del modello teorico


La   procedura   non   è   iterativa   nel   passo,   quindi   perché   i   risultati   siano
sufficientemente accurati, bisogna che i passi di carico siano piccoli.

Come  evidenziato  dalla  figura  7,  il  modello  si  presta  bene  all’inserimento  di
elementi   “truss”   che   vengono   fissati   in   corrispondenza   dei   nodi   fissi
dell’elemento   di   collegamento,   con   tali   elementi   si   riesce   facilmente   a
schematizzare  barre  di  armatura  (lente  o  pretese)  orizzontali  e  verticali  e  il
comportamento  assiale  di  cordoli  di  piano.  Non  vi  è  tuttavia  la  possibilità  di
modellare l’interazione flessionale tra i cordoli di piano e la muratura.

3.2 - Macromodello di Brencich e Lagomarsino
Tale  macromodello  è  stato  introdotto  nel  1997  da  Brencich  e  Lagomarsino  [9],
esso è idealmente suddiviso in tre moduli. Uno centrale (
pannello), deformabile
solo a taglio, e due moduli periferici (
interfacce) in corrispondenza delle sezioni
di  base  e  di  testa,  che  possono  subire  solo  deformazioni  di  tipo  flessionale.  Le
due  interfacce  hanno  dimensioni  nulle;  si  osservi  tuttavia  che  nella  figura  8,
esclusivamente  per  comodità  di  rappresentazione,  queste  presentano  dimensioni
finite.
Considerando il vincolo di rigidità a taglio dei due moduli periferici e il vincolo
di   rigidità   flessionale   del   modulo   centrale,   il   macro-elemento   presenta
complessivamente  otto  gradi  di  libertà.  Come  parametri  lagrangiani  vengono
scelte  le  traslazioni  e  le  rotazioni  dei  punti  medi  delle  sezioni  di  base  e  di  testa
u
est
## =  [u
## 1
,  v
## 1
, φ
## 1
,  u
## 2
,  v
## 2
, φ
## 2
],  nonché  la  traslazione  e  la  rotazione  del  baricentro
della zona centrale u
pan
= [δ, φ
c
## ].



## 63
## Nj
## Tj
## Mj
## Ni
## Ti
## Mi
## Mc
## Nc
interfacce deformabili
assialmente
Pannello centrale
deformabile a taglio
## (a)

vi
ui
φi
φj
φc
δc
## (b)
vj
uj


figura 8: Schematizzazione del macro-elemento: (a) forze nodali,
(b) spostamenti nodali.

Viene mantenuta l’ipotesi di conservazione delle sezioni piane, quindi il vettore
u
est
caratterizza  completamente  la  deformata  esterna  del  macro-elemento.  Per
l’assemblaggio   dei   vari   elementi   che   costituiscono   l’intera   struttura   sono
necessari esclusivamente i gradi di libertà u
est
## .
Il  vettore  u
pan
è  necessario  per  caratterizzare  la  cinematica  del  modulo  centrale,
necessaria  per  poter  determinare  gli  spostamenti  relativi  tra  le  interfacce  di
estremità  e  il  modulo  centrale  stesso.  Da  questi  derivano  le  deformazioni
flessionali delle interfacce e la deformazione a taglio del pannello centrale.


ui , Vi , φi
δc , ui , φc
δc , uj , φc
δc , ui , φc
δc , uj , φc
uj , Vj , φj
uj
ui = vi = φi = 0
δc
φc
γ=uj-ui-φc*h


figura 9: Cinematica dei vari moduli del macromodello.

















## 64
Si osservi che tale modello permette di imporre la congruenza in corrispondenza
di una sola coppia di lati paralleli (interfacce), pertanto ogni macro-elemento può
essere  affiancato  ad  altri  solo  lungo  tali  due  lati,  mentre  gli  altri  due  devono
rimanere liberi.
Tale  circostanza  non  comporta  alcuna  limitazione  nella  modellazione  di
maschi   murari   e   fasce   di   piano;   elementi   per   i   quali   il   modello   è   stato
specificatamente  sviluppato.  Risulta  invece  essere  un  limite  nella  modellazione
della porzione di muratura che collega i maschi con le fasce, che difatti gli autori
del    macromodello    considerano    rigida.    Tale    ipotesi    è    avvalorata    dalla
considerazione  che  l’azione  di  confinamento  che  questa  zona  riceve  dai  maschi
murari,  dalle  fasce  di  piano  e  da  eventuali  cordoli  o  pareti  sovrastanti  gli
conferisce  una  elevata  rigidezza  e  che  eventuali  fessurazioni,  probabilmente,  si
localizzeranno in corrispondenza dell’attacco con i pannelli. Peraltro, considerare
la zona di collegamento rigida oppure elastica non è una ipotesi inusuale: viene
utilizzata,  ad  esempio,  nella  schematizzazione  a  telaio  e  trova  giustificazione
nelle  osservazioni  di  edifici  colpiti  da  eventi  sismici,  nei  quali  raramente  si
riscontrano danneggiamenti in tali zone di collegamento.

zone rigide
nodi del modello
maschi murari
fasce di piano

figura 10: Parete piana ottenuta tramite assemblaggio di macroelementi
e zone rigide.

Tuttavia, in molti casi, il modello considerato può risultare parecchio limitativo a
causa della impossibilità di affiancare lateralmente due macro-elementi.
Innanzitutto  non  è  possibile  modellare  un  pannello  murario  attraverso  più
macroelementi  allo  scopo  di  ottenere  una  risposta  più  dettagliata.  Analoghe
difficoltà si riscontrano nel caso di strutture con geometria complessa o con una
disposizione irregolare delle aperture.
Pur considerando geometrie semplici (come quella raffigurata in figura 10), può
risultare  estremamente  difficile  l’inserimento  nel  modello  di  elementi  strutturali



## 65
che  interagiscono  con  la  muratura,  come  ad  esempio  un  cordolo  di  piano.  In
questo  caso  la  fascia  di  piano,  oltre  ad  essere  collegata  alla  restante  muratura,
deve interagire lungo un lato con il cordolo (fig. 11).


Interazione cordolo-fascia
MaschioMaschio
## Fascia


figura 11: Esempio di interazione tra cordolo e fascia di piano.

Le  interfacce  sono  costituite  da  un  insieme  continuo  di  molle  non  reagenti  a
trazione  e  a  comportamento  elastico-lineare  in  compressione.  Tali  molle  sono
caratterizzate dalla rigidezza per unità di superficie
k.

Il  comportamento  a  taglio  del  pannello  centrale  è  caratterizzato  da  una  fase
iniziale elastica con successivo sviluppo di deformazioni plastiche e di degrado,
secondo    una    formulazione    analoga    al    legame    costitutivo    a    piani    di
danneggiamento,   sviluppato   dagli   stessi   autori,   e   descritto   nel   precedente
capitolo [9].
La   rigidezza   iniziale   a   taglio   del   pannello   centrale,   considerando   una
distribuzione uniforme delle tensioni tangenziali in tutte le sezioni, risulta :

h
## AG
## K
## T
## ⋅
## =                                                  (1)
essendo
G il modulo di elasticità tangenziale iniziale della muratura, h l’altezza e
A l’area trasversale del pannello.
Se,  in  una  prima  fase,  si  considera  un  comportamento  elastico-lineare  sia  per  le
interfacce che per il pannello centrale, limitandosi al ramo elastico del legame a
taglio  e  trascurando  la  resistenza  nulla  a  trazione  delle  interfacce,  è  possibile
ottenere la matrice di rigidezza elastica:















## 66
## K
el
## =
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎦
## ⎤
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎣
## ⎡
## +−−−
## −−
## −
## −
## −
## −
## −
## −−
## 222
## 22
## 22
## 6
## 1
## 0
## 12
## 1
## 0
## 12
## 1
## 0
## 020000
## 12
## 1
## 0
## 12
## 1
## 00000
## 000000
## 00000
## 12
## 1
## 0000
## 12
## 1
## 00
## 000000
## 00000
kAbGAhkAbGAkAbGA
kAkAkA
kAbkAb
kAkA
## GA
h
## GA
hGA
kAbkAb
kAkA
GAhGAHGA
## /
## //


riferita ai gradi di libertà

u

## =
## []
cc
jvjujiviuiφδφφ

e alle corrispondenti forze (e momenti) nodali

## F

## =
## []
00MjNjTjMiNiTi

La  non  linearità  dovuta  al  contatto  monolatero  nelle  interfacce  e  al  legame  a
taglio del pannello centrale sono tenute in conto non attraverso l’aggiornamento
della   matrice   di   rigidezza,   che   viene   mantenuta   costante,   ma   attraverso
l’introduzione di un vettore di pseudo forze, che contiene i contributi, in termini
di forze nodali, delle non linearità.
## F* = [N
i
## *
,Ti
## *
,Μi
## *
,Nj
## *
,Tj
## *
,Μj
## *
,Nc
## *
,Mc
## *
## ]
Tale  vettore,  in  generale,  può  essere  definito  attraverso  semplici  considerazioni
sulla formulazione del legame elasto-plastico. Si può infatti scrivere la seguente
relazione tra le forze nodali e gli spostamenti elastici:
elel
uKF⋅=
esplicitando la parte plastica degli spostamenti, si ottiene:
## )(
plel
uuKF−⋅=

Introducendo appunto il vettore delle pseudo forze esterne (
F*) come segue :

plel
uKF⋅−=*                                                (2)
Il  legame  si  può  scrivere  in  funzione  della  rigidezza  elastica,  dato  che  i  termini
relativi alle non linearità sono racchiusi nel vettore appena definito; si ha:
uKFF
el
## ⋅=−*



## 67
L’analisi  deve  essere  condotta,  naturalmente,  in  termini  incrementali  e  ad  ogni
passo, partendo dalla deformata corrente si può determinare il vettore
F* (u) , il
procedimento  deve  prevedere  una  iterazione  nel  passo,  visto  che
F*  dipende  da
u; l’iterazione di ogni passo si arresta quando si annulla il vettore delle pseudo-
forze.

Nel caso in esame, le componenti del vettore
F* possono essere semplicemente
determinate, distinguendo tra i termini relativi alle interfacce e i termini relativi
al legame costitutivo a taglio.
Le  componenti  del  vettore
F*  relative  al  comportamento  assiale-flessionale
[Mi*,Ni*,
φi,Mj*,Nj*,φj*],  sono  dovuti  esclusivamente  ai  distacchi,  dato  che  in
compressione  il  legame  è  lineare  e  possono  essere  facilmente  calcolate  (vedi
figura   12)   come   il   risultante   delle   tensioni   di   trazione   relative   a   un
comportamento  elastico  lineare  sia  a  compressione  che  a  trazione,  che  in  realtà
non   possono   avere   luogo   a   causa   del   legame   costitutivo   assiale   di   tipo
monolatero attribuito al modello.

## −
## +
## −
σ legame elastico
σ legame monolatero
Deformata corrente
squilibrio
## R
## N* = R
## M* = R*d
d

figura 12: Diagrammi delle tensioni normali relative  al legame elastico e al
legame monolatero e lo squilibrio.
















## 68
## []
## ()
## ()
## ()[]
## []()
## 62
## 24
## 62
## 8
## 2
## 2
## /)(
## )(
## /)(
## *
## *
beHvb
vb
b
## Ak
## M
beHvb
## Ak
## N
nnccn
nccn
cncn
n
nnccn
cn
n
## −⋅−⋅+⋅−⋅
## ⋅−−⋅−⋅
## −⋅−⋅⋅
## ⋅
## =
## −⋅−⋅+⋅−⋅
## −⋅
## ⋅
## =
δφφ
δφφ
φφφφ
δφφ
φφ
## (3)

Con n = i , j viene individuato il nodo cui si riferisce il grado di libertà (fig. 9) ;
b  indica  la  larghezza  del  pannello,  A=b*s  l’area  trasversale,  H  la  funzione  a
gradino di Heaviside che fa in modo di azzerare i termini delle pseudoforza se la
sezione non è parzializzata.

Rimane  da  esplicitare  il  termine  relativo  alle  deformazioni  plastiche  di  taglio
Con  riferimento  a  quanto  detto  prima  sul  vettore
F*,  e  alla  figura  13,  si  può
scrivere :

pl
h
## AG
## T
δ⋅
## ⋅
## −=*                                              (4)
## Dove
δ
pl
è la componente plastica della deformazione totale a taglio δ, subita
dal pannello centrale.
## T,T*
δ=δel+δpl
## T,T*
## T*(δ)
δ
δ
elδpl
## Τ
δ
## (a)(b)


figura 13: (a) versi positivi della sollecitazione di taglio e dello squilibrio,
(b) rappresentazione dello squilibrio.


Ome  già  accennato  prima,  il  legame  costitutivo  a  taglio  è  analogo  a  quello
definito  nel  modello  continuo  a  piani  di  danneggiamento,  che  in  questo  caso  si
potrà   formulare   in   termini   di   variabili   globali,   grazie   all’ipotesi   di   stato
tensionale e deformativo uniforme all’interno del pannello centrale.




## 69
Si  consideri  la  relazione  del  tutto  analoga  a  quella  incontrata  nel  capitolo
precedente  che  esprimere  lo  scorrimento  plastico  in  funzione  delle  due  variabili
di stato
α e f :
## )(fc
pl
−⋅⋅=ταγ                                                                        (5)
Si  ricorda  che  a  è  una  variabile  scalare  di  danno  e  f  la  tensione  tangenziale
dovuta all’attrito.

Attraverso passaggi elementari si esplicita l’espressione precedente in
γ
pl
## :
## ()
## []
## ()
## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## −⋅
## ⋅⋅+
## ⋅
## ⋅=
## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## −⋅⋅⋅=⋅⋅+
## −−⋅⋅=
## G
f
cG
c
## G
## G
f
cGcG
fGc
pl
pl
plpl
γ
α
α
γ
γααγ
γγαγ
## 1
## 1

Poiché  si  hanno  tensioni  e  deformazioni  uniformi,  si  possono  introdurre  le
grandezze  globali  al  posto  delle  locali.  Si  considererà,  quindi  la  forza  totale  di
attrito F al posto di
f e lo scorrimento totale a taglio (δ) anziché γ:
h
## A
## F
f
## ⋅=
## =
γδ
## (6)
sostituendo tali espressioni si ha :
## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## ⋅
## ⋅
## −⋅
## ⋅⋅+
## ⋅
## ⋅=F
## AG
h
cG
c
## G
pl
δ
α
α
δ
## 1

Lo   scorrimento   globale   del   pannello   si   può   esprimere   in   funzione   degli
spostamenti nodali :
huu
cij
## ⋅−−=φδ

Infine si ottiene :
## ()
## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## ⋅
## ⋅
## −⋅−−⋅
## ⋅⋅+
## ⋅
## ⋅=F
## AG
h
huu
cG
c
## G
cijpl
φ
α
α
δ
## 1
## (7)














## 70
Il resto delle relazioni, che unitamente all’espressione appena trovata, governano
il   comportamento   a   taglio   del   pannello   centrale,   sono   analoghe   a   quelle
presentate nel capitolo precedente, riferite però a variabili globali.

Le condizioni limite sono :
## ⎪
## ⎩
## ⎪
## ⎨
## ⎧
## ≤−=
## ≤⋅+=
## 0
## 0
## )(
αφ
μφ
## RY
## NF
d
is
## (8)
R è definita analogamente al capitolo precedente ed è caratterizzata dai parametri
c e Rc=R(
α=1).
## ()
## 2
## 2
## 1
FTcY
m
## −⋅⋅=
## (9)
Il dominio di rottura a taglio dato da :
c
## R
TNiT
c
r
## =≤⋅−μ
## (10)

Tornando al calcolo dello squilibrio, si ottiene :
## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## ⋅+⋅+−⋅
## ⋅⋅+
## ⋅⋅
## ⋅
## ⋅
## =⋅
## ⋅
## −=F
## G
h
huu
cG
cG
h
## AG
h
## AG
## T
## Mjipl
## )(*φ
α
α
δ
## 1
## (11)
Le componenti di
F*, risultano :
## **
## **
## TT
## TT
j
i
## −=
## =
## (12)
I  parametri  che  caratterizzano,  in  definitiva,  il  modello  sono  E  e  k  per  quanto
riguarda    il    comportamento    assiale-flessionale.    Per    quanto    riguarda    il
comportamento a taglio, si ha il modulo G della muratura, la resistenza limite a
taglio  in  assenza  di  sforzo  normale  (Tr)  ,  il  coefficiente  di  attrito  (
μ),  e  i
parametri c,
β per che regolano la duttilità e la fase di softening a taglio.
Sono  tutti  facilmente  deteminabili  attraverso  prove  di  compressione  semplice  e
di taglio su campioni di muratura. E’ importante sottolineare che sarebbe inutile
condurre   prove   sui   singoli   elementi   visto   che   si   intende   riprodurre   il
comportamento macroscopico dell’elemento strutturale.









## 71

## Bibliografia

[1] F. Braga, D. Liberatore: “A finite element for the analysis of the response
of   masonty   buildings”,   Proc.   Of   the   5
th
## North   American   Masonry
Conference, Urbana, 1990, pp.201-212.
[2] F.Braga, D. Liberatore & G. Spera: “A computer program for the seismic
analysis  of  complex  masonry  duildings”.  In  G.N.  Pande,  J.  Middleton  &
B.Kralj (eds.), Computer Methods in Strustural Masonry – 4; Proc. Inter.
Symp., Firenze, 3-5 Settembre, 1997:309-316. London: E& FN spons.
[3] B. Calderoni, P. Marone, M. Pagano: “Modelli per la verifica statica degli
edifici  in  muratura  in  zona  sismica”.
Ingegneria  sismica,  n.  3,  1987,
pp.19-27.
[4] B.  Calderoni,  P.  Lenza,  M.  Pagano:  “Attuali  prospettive  per  l’analisi
sismica   non   lineare   di   edifici   in   muratura”.   Atti   del   4°   Convegno
Nazionale ANIDIS, Milano, 1989.
[5] G.  Magenes,  D.  Bolognini,  C.  Braggio  (A  cura  di):  “Metodi  semplificati
per  l'analisi  sismica  non  lineare  di  edifici  in  muratura”,  CNR-Gruppo
Nazionale per la Difesa dai Terremoti - Roma, 2000, 99 pp.
[6] P. D’Asdia e A. Viskovic: “Un modello di calcolo della resistenza ultima
delle  pareti  in  muratura”.  Atti  6°  convegno  nazionale  ANIDIS,  Perugia,
## 13-15 Ottobre, 1993.
[7] P.  D’Asdia  e  A.  Viskovic:  “Analisi  tridimensionale  della  resistenza  di
edifici in muratura, storici o recenti, soggetti ad azioni orizzontali di tipo
sismico”.  Convegno  nazionale  “La  meccanica  delle  murature  tra  teoria  e
progetto”, Messina, 1996.
[8] A. Brencich e S. Lagomarsino: “Un modello a macroelementi per l’analisi
ciclica di pareti murarie”. Atti 8° convegno nazionale ANIDIS, Taormina,
## 21-24 Settembre,1997.
[9] L.  Gambarotta  e  S.  Lagomarsino  :  “Damage  models  for  the  seismic
response of brick masonry shear walls. Part I: The mortar joint model and
its  applications.  Part  II:  The  continuum  model  and  its  application”.
Earthquake Engineering and Structural Dynamic, 26 424-462.





















## 72




4 Il macromodello proposto


## Premessa

Nel   seguito   viene   introdotto   un   nuovo   modello   meccanico   equivalente   o
macromodello in grado di descrivere sia il comportamento di un singolo pannello
murario  che  di  una  porzione  di  esso.  Un  tale  macromodello  può  pertanto
rappresentare  un  intero  maschio  murario,  caricato  nel  proprio  piano,  attraverso
un   singolo   elemento   o   mediante   una
mesh di   elementi.   E’   evidente   che
all’aumentare  del  numero  di  elementi  la  descrizione  del  comportamento  del
pannello   murario   risulterà   più   accurata   a   fronte   di   un   maggior   costo
computazionale.  Tuttavia  il  macromodello  proposto  è  concepito  con  l’obiettivo
di  rappresentare  un  intero  maschio  murario  senza  la  necessità  di  utilizzare  una
mesh  di  elementi.  Per  raggiungere  un  tale  obiettivo  esso  deve  essere  capace  di
descrivere  il  comportamento  meccanico  della  porzione  di  elemento  murario  che
si vuole rappresentare considerandone la limitata resistenza a trazione e a taglio e
descrivendone i principali meccanismi di rottura.

4.1 Descrizione del modello meccanico equivalente
Come ampiamente descritto nel capitolo 1, i principali meccanismi di collasso di
una porzione di elemento murario caricato nel proprio piano e soggetto ad azioni
orizzontali    possono    essere    così    riassunti:    rottura    per    schiacciamento
/ribaltamento,  rottura  a  taglio.  La  rottura  a  taglio  può  avvenire  secondo  due
differenti meccanismi corrispondenti rispettivamente alla rottura per fessurazione
diagonale  e  alla  rottura  per  scorrimento.  A  ciascuno  dei  meccanismi  di  rottura
risulterà possibile associare criteri di resistenza differenti.








## 73
## (a)
## (b)(c)

figura 1: Meccanismi di rottura di un pannello murario o di una porzione
di  muratura;  (a)  rottura  per  schiacciamento/ribaltamento;  (b)  rottura  a
taglio per fessurazione diagonale; (c) rottura a taglio per scorrimento.

Il  modello  proposto  è  in  grado  di  simulare  i  principali  meccanismi  di  rottura  di
un  pannello  murario  o  di  una  sua  porzione.  Esso  è  costituito  da  un  quadrilatero
articolato,  i  cui  lati  sono  infinitamente  rigidi  e  i  cui  vertici  incernierati  sono
collegati  da  molle  diagonali  (figura  2),  e  da  un  insieme  discreto  di  molle
distribuite   lungo   il   perimetro   del   quadrilatero   (figura   3);   queste   ultime
stabiliscono  il  legame  non-lineare  con  i  quadrilateri  eventualmente  adiacenti  o
con  i  supporti.  Il  letto  di  molle  ortogonali  ai  lati  del  quadrilatero  oltre  a
concentrare  la  deformabilità  assiale  e  flessionale  della  porzione  di  muratura  che
rappresentano, serve a simulare i meccanismi di rottura per schiacciamento e per
ribaltamento (figure 4 a). Il legame costitutivo delle molle diagonali deve essere
tale  da  descrivere  la  deformabilità  a  taglio  della  porzione  di  muratura  che  si
vuole  discretizzare  e  il  corrispondente  meccanismo  di  rottura  per  fessurazione
diagonale  (figura  4b).  Il  meccanismo  di  rottura  a  taglio  per  scorrimento  risulta
invece descritto dalle molle non lineari che risultano poste nella stessa direzione
dei lati rigidi che connettono (figura 4 c).
molle diagonali
inelastiche
## K2
## K1
aste rigide

Figura 2: Il macromodello proposto; in configurazione iniziale e in
configurazione deformata.















## 74


figura  3:  Il  macromodello  proposto;  modellazione  di  una  porzione  di  muratura
mediante  il  macroelemento,  con  evidenziato  il  letto  discreto  di  molle
interposto tra i vari quadrilateri.



fessurazione (b)
schiacciamento
della muratura (a)
## F
## Fmolla
## Δmolla
a
b

figura 4,a: Simulazione  del  meccanismo  di  schiacciamento/ribaltamento
tramite il macromodello proposto




## 75
## F
rottura del puntone
compresso
## Fmolla
## Δmolla

figura    4,b:    Simulazione    del    meccanismo    di    rottura    a    taglio    per
fessurazione diagonale tramite il macromodello proposto

## F
Attivazione di
scorrimenti plastici
## F
## Ν

figura 4,c: Simulazione del meccanismo di rottura a scorrimento tramite il
macromodello proposto


Per  comodità  di  trattazione  l’insieme  discreto  delle  molle  distribuite  lungo  un
generico  lato  nel  seguito  verrà  denominato
interfaccia,  mentre  il  quadrilatero
articolato con le due molle diagonali verrà denominato
pannello.
L’interfaccia, che per scelta nella presente trattazione non è rappresentato da un
elemento continuo ma piuttosto da un numero finito ma arbitrario di molle, oltre
a  costituire  la  connessione  tra  pannello  e  pannello,  può  rappresentare  anche
l’elemento di connessione tra un pannello e l’esterno (figura 5).















## 76
Muratura reale
## Modello
pannello
pannellopannello
interfacce
pannello-pannello
interfaccia
pannello-vincolo

figura 5: Rappresentazione schematica della modellazione di una parete
muraria.

In  alternativa  ai  quadrilateri  articolati  (pannelli),  il  modello  proposto  prevede
anche la possibilità di inserire elementi poligonali rigidi, denominati nel seguito
elementi  rigidi.  Tali  elementi  possono  essere  collegati  mediante  interfacce  ad
altri elementi rigidi o ai pannelli e possono risultare utili per la rappresentazione
di geometrie complesse.

## 4.1.1 Pannello
Come  già  detto,  il  pannello  è  costituito  da  un  quadrilatero  articolato  piano  nel
quale  i  vertici  opposti  sono  collegati  tramite  molle  non-lineari,
## K
## 1
e  K
## 2
,  che
simulano  la  resistenza  e  la  deformabilità  a  taglio  del  pannello.  E’  evidente  che
per simulare tale legame sarebbe stata sufficiente un’unica molla posta lungo una
delle    due    diagonali,    tuttavia    per    comodità    sia    di    trattazione    che    di
rappresentazione  si  è  preferito  considerare  due  molle  diagonali  ciascuna  delle
quali possiede una limitata o nulla resistenza a trazione ed un legame non lineare
a compressione.
Considerando anche i moti rigidi il pannello possiede nel piano quattro gradi di
libertà.  Nella  presente  trattazione  si  considera  una  cinematica  limitata  ai  piccoli
spostamenti  tuttavia  si  tiene  conto  degli  effetti  p-
δ.  Come  parametri  lagrangiani
sono  stati  considerati  le  quattro  traslazioni  di  ciascuno  dei  lati  rigidi  lungo  la
propria  direzione  (figura  6a).  A  tali  parametri  lagrangiani  si  associano  le  forze
duali  (figura  6b).  Scelto  il  vertice  1,  gli  altri  vertici  del  pannello  sono  numerati
progressivamente  in  senso  antiorario  a  partire  da  questo.  All’elemento  viene
associato un sistema di riferimento locale avente origine nel vertice 1 e assi
x, y
orientati  rispettivamente  verso  i  vertici  2  e  3  (figura  6c).  I  versi  positivi  dei
parametri lagrangiani vengono assunti concordi con il sistema locale fissato.




## 77
u3
u1
u2u4
## F1
## F3
## F4F2
x
v1
y
v1
v4v3
## (a)(b)(c)


figura  6:  Scelta  dei  parametri  lagrangiani  relativi  al  pannello:  (b)  spostamenti
nodali,  (c)  forze  nodali,  (a)  sistema  di  riferimento  locale  e  numerazione
dei vertici.

4.1.2 Elemento rigido
Come  già  detto,  oltre  agli  elementi  pannello,  nel  modello  proposto  vengono
introdotti  degli
elementi  rigidi.  Questi  possono  essere  utilizzati  in  luogo  dei
pannelli nei casi in cui la rigidezza a taglio è estremamente elevata (per esempio
strutture  murarie  a  blocchi)  oppure  possono  risultare  utili  per  la  definizione  di
elementi  dalla  geometria  irregolare.  Come  i  pannelli,  anche  gli  elementi  rigidi
sono  connessi,  tra  loro  o  al  resto  della  struttura,  tramite  elementi  interfaccia.  A
differenza  dei  pannelli,  gli  elementi  rigidi  possono  avere  un  numero
n  qualsiasi
di  vertici,  che  verranno  indicati  con
## V
## 1
## , V
## 2
## , V
## 3
## ,  ...,  V
n
,  e  ovviamente  altrettanti
lati, che verranno indicati con
## L
## 1
## , L
## 2
## , L
## 3
## , ..., L
n
, essendo:
## - L
i
, con 0<i<n, il lato che congiunge i vertici V
i
e V
i+1
## ;
## -
## L
n
il lato che congiunge il vertice V
n
con il vertice V
## 1
## .
Le  coordinate  cartesiane  del  vertice
## V
i
nel  sistema  di  riferimento  assoluto
verranno  indicate  con  (
x
i
, y
i
);  mentre  il  baricentro  geometrico  dell’elemento
rigido ha, nello stesso sistema di riferimento, coordinate (
x
## G
, y
## G
## ).
Ogni  elemento  rigido  piano  ha  ovviamente  tre  gradi  di  libertà,  che  vengono
caratterizzati mediante le due componenti nelle direzioni degli assi del sistema di
riferimento  assoluto  dello  spostamento  del  baricentro  geometrico  (
## U
## GX
## , U
## GY
## )
dell’elemento, nonché attraverso la sua rotazione rigida
θ
## G
, positiva se in senso
antiorario (figura 7).















## 78
uGX
## G
uGY
θG
## X
## Y
## Vi
## Vi+1
t
n
Sistema associato al
lato
Sistema assoluto
lato i
i
## 1
i3
i2

Figura 7. Elemento rigido: gradi di libertà e convenzioni sugli spostamenti.

Al  fine  di  assemblare  le  matrici  globali,  è  utile  determinare  per  ogni  lato  la
componente di spostamento nella direzione del lato stesso e gli spostamenti degli
estremi nella direzione ortogonale in funzione dei parametri lagrangiani. Tali tre
componenti  di  spostamento  del  lato  sono  indicate  con
i
## 1
, i
## 2
e  i
## 3
nella  figura  7.
Queste  sono  considerate  positive  se  concordi  al  sistema  di  riferimento  locale
fissato  per  ogni  lato,  costituito  da  un  versore
n  diretto  secondo  la  normale
uscente dal lato e da un versore
t diretto lungo il lato nel verso che va dal vertice
## V
i
al vertice V
i+1
## .
Nel sistema di riferimento globale
## ()
## Oxy

il vettore spostamento del vertice
i si
può scrivere:

## ()
iGXiGGGYiGG
PVUy    yx    Ux    xyθθ
## ⎡⎤⎡⎤
## =−− ⋅ ⋅+  +−⋅ ⋅
## ⎣⎦⎣⎦


I  versori  del  sistema  di  riferimento  associato  al  lato
i-esimo  possono  essere
ottenuti in funzione delle coordinate dei vertici:


## 11
## 2222
## 1111
## 11
## 2222
## 1111
iii i
i
ii    i iii    i i
iiii
i
ii    i iii    i i
xxyy
txy
xx  yyxx  yy
yyxx
nxy
xx  yyxx  yy
## ++
## ++++
## ++
## ++++
## −−
## =⋅+⋅
## −+ −−+ −
## −−
## =⋅−⋅
## −+ −−+ −



Le  componenti  di  spostamenti
i
## 1
, i
## 2
, i
## 3
possono  essere  calcolate  proiettando  gli
spostamenti dei vertici lungo le direzioni
t e n:




## 79
## ()
## 1
## 1
## 22
ii
iiGX   i GG
yy
iPVn Uyy
xy
θ
## +
## −−
## ⎡⎤
## =⋅=−−⋅⋅+
## ⎣⎦
## Δ+Δ
r


## 1
## 22
ii
GYiGG
xx
## Uxx
xy
θ
## +
## −
## ⎡⎤
## ++−⋅⋅
## ⎣⎦
## Δ+Δ

## ()
## 1
## 211
## 22
ii
ii GXi GG
yy
iPV n U    y  y
xy
θ
## +
## ++
## −−
## ⎡⎤
## =⋅=−−⋅⋅    +
## ⎣⎦
## Δ+Δ
r


## 1
## 1
## 22
ii
GYiGG
xx
## Uxx
xy
θ
## +
## +
## −
## ⎡⎤
## ++−⋅⋅
## ⎣⎦
## Δ+Δ

## ()( )
## 1
## 311
## 22
ii
iiiiGXiG G
xx
iPVtPV t U    y  y
xy
θ
## +
## ++
## −
## ⎡⎤
## =⋅= ⋅=−−⋅⋅+
## ⎣⎦
## Δ+Δ
rr


## 1
## 1
## 22
ii
GYiGG
yy
## Uxx
xy
θ
## +
## +
## −
## ⎡⎤
## ++−⋅⋅
## ⎣⎦
## Δ+Δ



## 4.1.3 Interfaccia
Se  si  considera  la  muratura  come  un  corpo  omogeneo,  in  cui  cioè  non  si
distingue   tra   elementi   lapidei   e   malta   di   collegamento,   il   comportamento
complessivo  si  può  pensare  dovuto  in  parte  al  suo  comportamento  flessionale  e
in  parte  al  suo  comportamento  a  taglio.  Il  comportamento  flessionale  viene
simulato  dall’insieme  discreto  di  molle  verticali  poste  nei  lati  del  pannello.  In
corrispondenza di tali interfacce si considerano concentrate tutte le caratteristiche
flessionali della porzione di muratura che si vuole rappresentare. Come già detto,
la  deformazione  tagliante  e  i  corrispondenti  meccanismi  di  rottura  vengono
invece  simulati  dalle  molle  diagonali  e  dalle  molle  poste  nelle  direzioni  dei  lati
del pannello atte a simulare eventuali scorrimenti.
L’accostamento  di  elementi  pannello  e/o  elementi  rigidi  mediante  interfacce
consente  inoltre  di  modellare  agevolmente  strutture  come  ad  esempio  i  templi
greci  che  possono  essere  assimilati  ad  un  assemblaggio  di  blocchi  ad  elevata
rigidezza.  In  questo  caso  ogni  singolo  concio  sarà  schematizzato  mediante  un
elemento pannello deformabile a taglio o un elemento rigido, a seconda dei casi,
mentre  le  interfacce  modelleranno  la  malta,  se  presente,  o  semplicemente  il
contatto monolatero tra i conci.
Nella figura 8 è schematicamente rappresentata un’interfaccia, solo per comodità
di  rappresentazione  l’interfaccia  è  rappresentata  con  uno  spessore  finito  in














## 80
quanto  nella  formulazione  matematica  è  considerata  priva  di  spessore.  Nella
figura  l’interfaccia  collega  due  pannelli  (
interfaccia  pannello-pannello);  più  in
generale  un’interfaccia  può  connettere  tra  loro  due  elementi  del  modello,  siano
essi pannelli o elementi rigidi, o un elemento a un vincolo esterno. Pertanto, oltre
al   caso   di   interfaccia   pannello-pannello,   un’interfaccia   può   connettere:   un
pannello a un vincolo esterno (
interfaccia pannello-vincolo), due elementi rigidi
tra  loro  (
interfaccia  rigido-rigido),  un  elemento  rigido  a  un  vincolo  esterno
## (
interfaccia  rigido-vincolo)  e  un  pannello  a  un  elemento  rigido  (interfaccia
pannello-rigido
).  Inoltre,  per  indicare  genericamente  un’interfaccia  che  collega
due  elementi  tra  loro  nel  seguito  di  parlerà  di
interfaccia  elemento-elemento,
mentre  per  indicare  una  interfaccia  che  collega  un  elemento  a  un  vincolo  si
utilizzerà la denominazione
interfaccia elemento-vincolo.
Per  ogni  interfaccia  è  conveniente  individuare  due  punti  estremi  (o  nodi),  che
verranno indicati con
i e j (figura 8a). Nel caso di interfaccia elemento-elemento,
a   ognuno   di   tali   estremi   corrispondono   in   realtà   due   nodi   del   modello,
appartenenti ciascuno a uno dei due elementi collegati dall’interfaccia. Tali nodi,
pur   avendo   nella   configurazione   iniziale   le   medesime   coordinate,   sono
fisicamente  distinti  e  subiranno  spostamenti  differenti.  I  quattro  nodi  (due  per
ogni   elemento   di      connessione)   che   corrispondono   ai   due   estremi
i   e   j
dell’interfaccia  vengono  denominati
vertici dell’interfaccia.  Ognuna  delle  due
linee  che  congiungono  i  vertici  che  appartengono  ad  uno  stesso  elemento  (o  al
vincolo) rappresentano convenzionalmente i
lati dell’interfaccia.
Nel  caso  di  interfaccia  elemento-vincolo,  i
vertici dell’interfaccia  sono  i  due
vertici dell’elemento a contatto con l’interfaccia stessa.
Il  sistema  di  riferimento  locale  ha  origine  nell’estremo
i,  asse  ξ  diretto  verso
l’estremo
j  e  asse  η  ruotato  di  90°  in  senso  antiorario  rispetto  a  ξ.  Le  molle
vengono numerate da 1 a
n a partire dal nodo j, come rappresentato in figura. Nel
caso   di   interfaccia   elemento-elemento,   i   due   pannelli   che   sono   collegati
dall’interfaccia  vengono  indicati  rispettivamente  con
elemento  1,  quello  che  ha
normale  uscente  opposta  a
η,  e  con  elemento  2  quello  che  ha  normale  uscente
concorde con
η  (figura 8a).
L’interfaccia è costituita da un letto discreto di molle trasversali e da una singola
molla longitudinale che simulano rispettivamente il comportamento flessionale, e
lo  scorrimento  (figura  8b).  Se  si  indica  con
n  il  numero  di  molle  e  con  L  la
lunghezza dell’interfaccia, l’interasse
λ tra le molle, risulta pari a

## 1
## L
n
λ=
## −


Come  si  vedrà  nel  seguito,  la  molla  longitudinale  ha  il  compito  di  simulare  lo
scorrimento dei due elementi corrispondenti, per questo motivo tale molla viene
considerata attiva solo se vi sono molle trasversali in compressione ed inoltre la
rigidezza  di  tale  molla  dipende  dal  numero  di  molle  trasversali  attive  ovvero
dalla lunghezza di contatto della zona di interfaccia.




## 81
## Pannello 1
## Pannello 2
ξ
η
nodo inodo j


## (a)

## . . .
kn-1kn
kh
Molla longitudinale
kn/2kn/2+1k2
k1
## Δ
Molle trasversali

## (b)
figura  8:  Interfaccia  tra  due  pannelli:  (a)  Sistema  di  riferimento  locale  e
individuazione  dei  nodi  e  dei  pannelli;  (b)  molle  longitudinali  e  molla
trasversale.


Lo stato di una generica interfaccia dipende da sei gradi di libertà corrispondenti
agli  elementi  cui  risulta  associata,  essi  sono  rappresentati  dalle  componenti  di
spostamento   dei   quattro   vertici   dell’interfaccia   nella   direzione   ortogonale
all’interfaccia stessa, nonché dagli scorrimenti della faccia superiore e inferiore.
Nel  caso  l’interfaccia  risulti  collegata  ad  un  supporto  elastico  (che  può  ad
esempio  rappresentare  il  terreno)  lo  stato  dell’interfaccia  potrà  ancora  essere
rappresentato da 6 parametri lagrangiani di cui tre appartengono al pannello e tre
al   supporto   elastico,   questi   ultimi   vengono   caratterizzati   mediante   le   due
componenti di spostamento (ortogonale e parallela all’interfaccia) e la rotazione
del vincolo elastico, fig.9. E’ evidente che se l’interfaccia risulta collegata ad un
vincolo fisso saranno necessari soltanto tre gradi di libertà per definirne lo stato e














## 82
vi possono essere casi intermedi in cui il supporto risulta cedevole elasticamente
soltanto in corrispondenza di determinati gradi di libertà.
Nella   descrizione   del   comportamento   dell’interfaccia,   tutti   i   parametri
lagrangiani  si  considerano  positivi  se  concordi  con  gli  assi  del  sistema  di
riferimento locale dell’interfaccia. I gradi di libertà sono illustrati con i loro versi
positivi nella figura seguente sia nel caso di interfacce elemento-elemento che di
interfacce elemento-vincolo.
ji
u2
u3
u1
u6
u4
u5
u1
u4
i
u5
u6
u3
j
u2
## (a)
## (b)
ξ
η

figura 9: Gradi di libertà interfaccia; (a) interfaccia elemento-elemento;
(b) interfaccia elemento-vincolo.

4.2 Equazioni del moto del sistema
Nel  seguito  vengono  ricavate  le  equazioni  del  moto  relative  ad  una  porzione  di
muratura  schematizzata  mediante  l’uso  della  macromodellazione  proposta.  La
derivazione di tali equazioni e quindi delle matrici di massa e di rigidezza, valide
ovviamente nel passo d’integrazione, verrà effettuata mediante l’applicazione del
noto  principio  di  Hamilton  [1]  nell’ipotesi  di  comportamento  elastico  lineare.
L’applicazione  del  principio  di  Hamilton  richiede  la  definizione  dell’energia
potenziale,   dell’energia   cinetica   e   del   lavoro   compiuto   dalle   forze   non
conservative.   Per   comodità   di   trattazione   nel   seguito   verranno   valutati
separatamente  i  contributi  energetici  associati  ai  pannelli  (sia  deformabili  che
rigidi) e alle interfacce.




## 83
4.2.1 Contributi energetici dovuti ai pannelli

- Energia potenziale elastica associata alle molle diagonali

Con  riferimento  ad  un  pannello  di  base  B  ed  altezza  H,  indicando  con  Δ
l’allungamento di ciascuna delle molle diagonali, supposte contemporaneamente
attive  ed  elastiche  nel  passo  d’integrazione,  l’energia  potenziale  elastica  risulta
espressa della relazione

## ()
## 2
## 12
## 1
## 2
## UKK=⋅+⋅Δ
## (1)
considerando la cinematica, riportata in figura 10, si ha:
## H
## B
u3-u1
α
## Δ
u2-u4
## H
α
## Δ
## B

figura 10: deformazioni nelle molle diagonali del pannello

## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## =
## B
## H
arctg
α

## ()()
ααsenuuuu
## 4213
cos−+−=Δ

Sostituendo tali espressioni nell’energia potenziale, si ha:

## ()()  ()
## 2
## 2
## 22
## 12    3124
## 1
## 2
UKKuuuusen
αα
## ⎡
## =⋅ + ⋅  −+ −+
## ⎣


## ()()
## 31   2 4
## 2sensenuuuuαα
## ⎤
## +⋅   ⋅   ⋅  −  ⋅  −
## ⎦


## ()
## ()()
## 222222
## 12    31  1324  24
## 1
## 22
## 2
UKK uuuuuuuusen
αα
## ⎡
## =⋅ + ⋅  + −+ + −+
## ⎣


## ()
## 12143234
2sensen   uuuuuuuuαα
## ⎤
## +⋅   ⋅   ⋅−  +   +   −
## ⎦















## 84

- Energia potenziale gravitazionale

Con riferimento ad un pannello ruotato di un angolo
θ rispetto all’orizzontale e
indicando  con  Oxy  il  sistema  di  riferimento  locale  e  con  OXY    il  sistema  di
riferimento  globale  (che  individua  il  livello  zero  dell’energia  gravitazionale),
figura 11, l’energia potenziale gravitazionale associata allo spostamento verticale
del centro di massa del pannello è data da

## G
UmgY=⋅⋅                                                 (2)
## X
## Y
y
x
θ
## G
y
## G
xG
## (a)
## G0
## G
δy
## G
yG0
yG
## Y
## X
## (b)

Figura 11. a) sistema di riferimento globale e locale del pannello, b)
variazione della quota del centro di massa

E’ importante notare che con tale approccio, nella configurazione corrente, si
considera la posizione del centro di massa con riferimento al pannello deformato.

Come  si  evince  dalla  figura  11,b  Y
## G
rappresenta  l’ordinata  del  baricentro  nella
configurazione  corrente  nel  sistema  di  riferimento  globale;  questa  può  essere
scritta  in  funzione  delle  coordinate  del  baricentro  nel  sistema  di  riferimento
locale del pannello (figura 11,a):



## 85

## GGG
## Yyxsenθθ=⋅  +⋅                                      (3)
L’espressione  (2) in funzione dei parametri lagrangiani del pannello diviene:

## 13
## 24
## 22
uu
uu
## Umgsen
θθ
## ⎛⎞
## +
## +
## =⋅⋅⋅   +    ⋅
## ⎜⎟
## ⎜⎟
## ⎝⎠
## (4)
E’  importante  osservare  che  l’eventuale  contributo  di  massa  associato  ai  carichi
esterni deve essere aggiunto alle masse derivanti dal peso proprio.

- Lavoro compiuto dalle forze non conservative

Le forze statiche esterne compiono lavoro non conservativo che con riferimento
ad un singolo pannello può esprimersi nella forma
## 44332211
uFuFuFuFW
nc
## +++=

## Essendo
## 1
## F
## ,
## 2
## F
## ,
## 3
F ed
## 4
## F
le forze nodali equivalenti all’effettiva distribuzione
di carico.

## -
## Energia Cinetica

Il problema dinamico viene trattato operando una concentrazione della massa del
modello,  che  in  realtà  è  diffusa  in  tutto  il  pannello.  Tale  discretizzazione  può
naturalmente essere operata in diversi modi.
Si sceglie di operare coerentemente con l’ipotesi di concentrare la forza peso in
corrispondenza  del  centro  di  massa,  quindi  la  massa  del  pannello  (m)  verrà
considerata   concentrata   in   corrispondenza   di   tale   punto,   priva   di   inerzia
rotazionale.
u1, F1
sistema di
riferimento locale
## X
sistema di riferimento globale
sistema di riferimento fisso
orientato come il sistema locale
## Y
m
x
y
y
x
u4, F4
u2, F2
## P=mg
## G
## K2
## K1
u3, F3

figura 12: Modello con massa concentrata in corrispondenza del centro di
massa














## 86
L’energia cinetica è esprimibile come:

## 2
## 1
## 2
## G
TmV=
r
## (5)

Esprimendo  il  vettore  velocità  V
## G
secondo  un  sistema  di  riferimento  fisso  e
orientato come il pannello, e riferendosi ai gradi di libertà del pannello, si ha :
## ⎥
## ⎥
## ⎦
## ⎤
## ⎢
## ⎢
## ⎣
## ⎡
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## +
## +
## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## +
## ⋅=
## 2
## 42
## 2
## 31
## 222
## 1
uu
uu
mT
## &&
## &&


## 2222
## 13   1324   24
## 1
## 22
## 8
T  muu  uuuu  uu
## ⎡⎤
## = ⋅ ++  +++
## ⎣⎦
## && &&&& &&
## (6)

E’  ovviamente  possibile  un  approccio  alternativo  in  cui  le  masse  vengono
concentrate  in  corrispondenza  dei  gradi  di  libertà,  come  indicato  nella  figura
seguente, in tal caso si giungerebbe a una matrice di massa diagonale.

u4, F4
m/4
m/4
u2, F2
m/4
m/4
u1, F1
u3, F3
## P=mg
## G
## K1
## K2
x
y
## X
## Y
x
y
sistema di
riferimento locale
sistema di riferimento fisso
orientato come il sistema
locale
## (a)
sistema di riferimento
globale

figura 13: Massa concentrata in corrispondenza dei gradi di libertà

4.2.2 Contributi energetici dell’elemento rigido
L’elemento  rigido  si  considera  soggetto  alla  propria  forza  peso  P  applicata  nel
baricentro  geometrico  G.  I  parametri  lagrangiani  che  caratterizzano  i  gradi  di
libertà e le corrispondenti forze duali sono riportati nella figura 14.



## 87
## G
## X
## Y
Sistema assoluto
## P
uGX , FX
uGY , FY
θG , Μ
m

figura 14: Elemento rigido

- Energia potenziale gravitazionale

Considerando  l’asse  Y  del  sistema  di  riferimento  assoluto  orientato  secondo  la
direzione verticale, l’energia potenziale della forza peso P=mg risulta:

## PGY
UmgU=⋅                                                (7)


## -
Lavoro compiuto dalle forze non conservative

Con  riferimento  alle  componenti  del  vettore  degli  spostamenti  nodali  e  del
vettore  delle  forze  nodali  dell’elemento  rigido  (vedi  figura),  si  può  facilmente
scrive:

ncGXGYG
WFxU FYU Mθ=⋅ +⋅ +⋅                               (8)
## - Energia Cinetica

La massa si può considerare uniformemente ripartita, l’energia cinetica si ricava
facilmente  dalla  teoria  dei  corpi  rigidi.  In  particolare,  utilizzando  il  teorema  di
Konig, si ottiene:

## 222
## 0
## 111
## 222
## GGG
TmVT  mVθ=⋅+=⋅+Ι
## &
## (9)


















## 88
essendo:
m la massa totale dell’elemento rigido;
## V
## G
il modulo della velocità del baricentro;
## I
o
il  momento  d’inerzia  rispetto  a  un  asse  baricentrico  ortogonale  al  piano
dell’elemento;
θ
## &
la velocità di rotazione nel piano dell’elemento rigido

Riscrivendo   l’espressione   precedente   esplicitando   i   parametri   lagrangiani
dell’elemento rigido, si ottiene:

## 222
## 0
## 111
## 222
## GXGYG
TmU   mUθ=⋅+⋅+Ι
## &
## &&
## (10)


4.2.3 Contributi energetici delle interfacce

- Energia potenziale elastica associata ad una singola interfaccia

Le  interfacce  vengono  considerate  prive  di  massa.  L’applicazione  del  principio
di Hamilton richiede quindi la definizione dell’energia potenziale delle molle che
costituiscono l’interfaccia e del lavoro compiuto dalle forze non conservative che
il resto del modello esercita sull’interfaccia.

## Δ1
## (i)
estremo iestremo j
## (i+1)
di
λ
## Δi
## Δ2


figura 15: Cinematica dell’interfaccia in assenza di scorrimento
longitudinale.

Con riferimento al generico istante di integrazione, si ha:

scorr
na
i
ii
KsKU⋅Δ⋅+
## ∑
## Δ⋅=
## =
## 2
## 1
## 2
## 2
## 1
## 2
## 1
## (11)






## 89
essendo:
## K
i
= la rigidezza elastica tangente dell’ i-esima molla flessionale;
n
a
= numero di molle flessionale attive dell’interfaccia;
## K
scorr
= rigidezza della i-esima molla longitudinale;

Indicando inoltre con:
L   la lunghezza della interfaccia;
d
i
la distanza della i-esima molla dall’estremo j;
## Δ
i
l’allungamento della i-esima molla trasversale;
## Δ
s
lo scorrimento tra le estremità dell’interfaccia.

Gli spostamenti lungo l’interfaccia variano linearmente, quindi si può esprimere
l’allungamento della i-esima molla come combinazione lineare degli spostamenti
dei punti estremi:
## L
d
i
i
## ⋅Δ−Δ+Δ=Δ)(
## 121

con:
λ⋅−=
## −=Δ
## −=Δ
## )1(
## 142
## 231
id
uu
uu
i


Lo scorrimento longitudinale è invece dato da:
## 656
uu−=Δ

Sostituendo tali espressioni nella (11), si ha:

## []
scorr
na
i
i
i
## Kuu
## L
d
uuuuuuKU⋅−⋅+
## ∑
## ⎥
## ⎦
## ⎤
## ⎢
## ⎣
## ⎡
## ⋅−−−+−⋅=
## =
## 2
## 65
## 2
## 1
## 231423
## 2
## 1
## 2
## 1
## )()()()(
## (12)
che, con semplici considerazioni algebriche può essere così trasformata:

## ()[]
scorr
na
i
iii
KuudLuuduuK
## L
## U⋅−⋅+
## ∑
## −⋅−+⋅−⋅=
## =
## 2
## 65
## 2
## 1
## 2314
## 2
## 2
## 1
## 2
## 1
## )()()(

## () ()[]
scorr
na
i
iiiii
## Kuu
uuuudLddLuuduuK
## L
## U
## ⋅−⋅+
## +
## ∑
## −−⋅−+−⋅−+⋅−⋅=
## =
## 2
## 65
## 1
## 2314
## 2
## 2
## 23
## 22
## 14
## 2
## 2
## 1
## 2
## 2
## 1
## )(
## ))(()()(















## 90
## [
## ()
## ]
scorrii
iii
na
i
i
KuuuuuuuuuuuudLd
LddLuuuuduuuuK
## L
## U
## ⋅−+⋅++−−⋅−+
## +−+⋅−++⋅−+
## ∑
## ⋅=
## =
## )()()(
## )()(
## 65
## 2
## 6
## 2
## 521312434
## 22
## 23
## 2
## 2
## 2
## 3
## 2
## 14
## 2
## 1
## 2
## 4
## 1
## 2
## 2
## 2
## 1
## 2
## 222
## 2
## 1


pertanto, l’energia potenziale delle molle di interfaccia si scrive nella forma:
## ()
## 2
## 121314234324
## 2
## 1
## 2222222
## 123432   3243122413
## 22222
## 32   2356   56
## 1
## 222222
## 2
## 22
## 1
## 22
## 2
na
i
i
i
ii
scorr
UKd uuuuuuuuuuuu
## L
d   uuuuLd    uuuuuuuuuuuu
Lu   uuuu   uuu   K
## =
## ⎡
## =   ⋅−+−−−+ +
## ⎣
## +   +++ +  −−+  + + − −  +
## ⎤
## ++−  +⋅+− ⋅
## ⎦
## ∑


- Lavoro compiuto dalle forze non conservative

Indicando  con  F
i
e u
i
rispettivamente  le  forze  e  gli  spostamenti  nodali,  con
i=1,..,6, si ha:
## 6
## 1
NCi    i
i
WFu
## =
## =
## ∑



























## 91
4.2.4 Applicazione del principio di Hamilton

Per  ricavare  le  equazioni  del  moto  di  un  sistema  composto  da  più  elementi
pannello,  assemblati  tra  loro  mediante  le  interfacce,  si  applica  il  principio  di
## Hamilton.
Nel seguito si farà riferimento alla seguente simbologia:

Np :  numero di elementi pannello presenti nel sistema
Nr  :  numero di elementi rigidi presenti nel sistema
## N
## I
:  numero di interfacce del sistema
na
## I
:  numero di molle attive dell’interfaccia i
## U
k  :
potenziali delle molle (interfacce o pannelli)
## U
g
:  potenziali gravitazionali (pannelli o elementi rigidi)
u
p
i
:  grado di libertà locale i del pannello p con i=1,..,4
u
## I
i
:  grado di libertà locale i della interfaccia I con i=1,..,6
## F
p
i
: forza nodale i del pannello p             con i=1,..,4
## F
## I
i
:  forza nodale i della interfaccia I          con i=1,..,6
## K
## I
m
:  rigidezza tangente della molla m dell’interfaccia I
## K
p
## 1,
## K
p
## 2
:  rigidezza tangenti delle molle diagonali del pannello p
## K
## I
scorr
:  rigidezza a scorrimento dell’interfaccia I
## L
## I
:  lunghezza  dell’interfaccia  I
ρ
p
:   angolo   di   rotazione   del   sistema   relativo   del   pannello   p
rispetto XYO assoluto (positivo se antiorario).
u
r
## Gx
, u
r
## Gy
## ,
r
## G
θ :  gradi di libertà locali dell’elemento rigido r
## F
r
## Gx
## , F
r
## Gy
## , M
r

:  forze nodali dell’elemento rigido r
m
p
:  massa totale del  pannello p
m
r
:  massa totale dell’elemento rigido r
α
p
:  arcotangente di H/B del pannello p
d
## I,m
:  distanza tra la molla m e l’estremo j dell’interfaccia I



L’espressione generale del principio è :
## ()[]
## 0
## 1
## =
## ∫
## ⋅+−−
t
to
ncgK
dtWUUTδ

## 10
tt,∀
Evidenziando i vari contributi degli elementi, peraltro già calcolati nei paragrafi
precedenti:

## 0
## 111
## 1111
## 1
## 0
## 11
## =⋅
## ⎥
## ⎦
## ⎤
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ∑
## +
## ∑
## +
## ∑
## +
## +
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ∑
## +
## ∑
## −
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ∑
## +
## ∑
## −
## ∫
## ⎢
## ⎣
## ⎡
## ⎟
## ⎠
## ⎞
## ⎜
## ⎝
## ⎛
## ∑
## +
## ∑
## ===
## ======
dtWWW
## UUUUTT
## Ni
i
i
## Nr
r
r
## Np
p
p
## Ni
i
i
## K
## Np
p
p
## K
## Nr
r
r
g
## Np
p
p
g
t
t
## Nr
r
r
## Np
p
p
δδδ
δδδδδδ
## (13)















## 92
Sostituendo nella precedente espressione di termini energetici relativi ai pannelli,
interfacce  e  corpi  rigidi,  ricavati  in  precedenza,  e  utilizzando  le  notazioni  sopra
riportate, la formulazione del principio di Hamilton può essere scritta in funzione
del gradi di libertà locali di tutti gli elementi, come segue:

## ()()
## ()
## 1
## 1223344133124
## 1
## 1
## 0
## 2
## 421233 11  13  31
## 1
## 2
## 22    44   24   423
## 4
t
## Np
p
p
ppppppppppppp
p
t
## Np
p  ppppp    pp   pp   pp
p
p
pp    pp   pp   ppp
p
m
u u  uu  uu  uu  uu  uu  uu
uuK   Kuu  uu  uu  uu
uu  uu  uu  uusenu
δδδδδδδ
δδδδδα
δδδδ α
## =
## =
## ⎧
## ⎪
## ⎡
## +++++++
## ⎨
## ⎣
## ⎪
## ⎩
## ⎡
## ⎤
## +−+⋅ +−−+
## ⎦
## ⎣
## ++−−+
## ∑
## ∫
## ∑
## && && && && && && &&
## &&
## ()
## ()
## () ()
## 223
## 34   43   12   21   1 4   41
## 4
## 2413
## 111
## 2
## 11441 4
## 2
## 11
## 2
## 1
## 222
## 2
ppp
pp
pp   pp   pp   pp    pp    pp
pp
NpNp
p
pp
ppii
ppi
## Nina
## IIIII
mIm
## Im
i
uuusen
uu  uu  uu  uu  uu  uusen
mg
uuuuFu
Kd    uuuuuu
## L
δδαα
δδδδδδαα
δδ   ρδδρδ
δδδ
## ===
## ==
## ++
## ⎤
## +−−−−+++
## ⎦
## ⎡⎤
## −+⋅++⋅++
## ⎣⎦
## ⎡
## −+−
## ⎢
## ⎢
## ⎣
## ∑∑∑
## ∑∑
## (
## )
## 413 32 2
## 2
## 233 2433424421 3
## 311 22133223223
## 43    34   1 2    2
## 222
## 22 2 2 2 2 2
## 222  22222
## IIIIIII
IiI IIIIIIIIIII
## Im
## IIIIIIIIIIIIII
IIm
## II    II    II    I
uuuuuu
d   uuuuuuuuuuuuuu
uuuuuuLduuuuuuuu
uu  uu  uu  u
δδδ
δδ δδδδδ
δδδδδδδ
δδδ
## −+++
## +−− −−++++
## +− − + −− + + +
## ++ + +
## 124421331
## 2
## 33222332
## 6
## 55    66   5665
## 11
## 0
## 1
## 2222
## 1
## 222
## 2
## IIIIIIIII
## IIIIIIII
## I
## Ni
## II    II   III I III
scorrjj
ij
## Nr
rrrrrr
r    GxGxr    GyGyrGG
r
uuuuuuuuu
## Luuuuuuuu
uu  uu  uu  u uKFu
muumuuI
δδδδδ
δδδδ
δδδ δδ
δδθδθ
## ==
## =
## −−−− +
## ++−−+
## ⎤
## −+−−++
## ⎦
## ⎡⎤
## +++
## ⎣⎦
## ∑∑
## ∑
## &&
## &&  &&
## 11
## 0
NrNr
rrirrrrr
GyGxGxGyGyG
rr
r
mg uF   uF   uMdtδδδδθ
## ==
## +
## ⎫
## ⎡⎤
## −+ ++⋅=
## ⎬
## ⎣⎦
## ⎭
## ∑∑













## 93
Integrando  per  parti  i  termini  in  cui  figurano  le  variazioni  delle  derivate
temporali dei gradi di libertà, si ha:

## ()()
## ()
## 1
## 1  1    22   33    44   1 3    31    24
## 1
## 0
## 2
## 421233 11  13  31
## 1
## 2
## 22    44   24   42
## 4
t
## Np
p
p  p    pp    pp    pp    pp    pp    pp
p
t
## Np
p  ppppp    pp   pp   pp
p
p
pp    pp   pp   pp
p
m
u u  uu  uu  uu  uu  uu  uu
uuK   Kuu  uu  uu  uu
uu  uu  uu  uusenu
δδδδδδδ
δδδδδα
δδδδ α
## =
## =
## ⎧
## ⎪
## ⎡
## −+++++++
## ⎨
## ⎣
## ⎪
## ⎩
## ⎡
## ⎤
## +−+⋅ +−−+
## ⎦
## ⎣
## ++−−+
## ∑
## ∫
## ∑
## &&   &&   &&   &&   &&   &&   &&
## && &
## ()
## ()
## () ()
## 32   23
## 34   43   12   21   1 4   41
## 4
## 2413
## 111
## 2
## 11223
## 2
## 11
## 2
## 1
## 222
## 2
pp    pp
pp
pp   pp   pp   pp    pp    pp
pp
NpNp
p
pp
ppii
ppi
## Nina
## IIIIII
mIm
im
i
uuusen
uu  uu  uu  uu  uu  uusen
mg
uuuuFu
Kd    uuuuu
## L
δδαα
δδδδδδαα
δδ   ρδδρδ
δδ
## ===
## ==
## ++
## ⎤
## +−−−−+++
## ⎦
## ⎡⎤
## −+⋅++⋅++
## ⎣⎦
## ⎡
## −++
## ⎢
## ⎢
## ⎣
## ∑∑∑
## ∑∑
## (
## )
## 3441441
## 2
## 233 2433424421 3
## 311 22133223223
## 43    34   1 2    2
## 222
## 22 2 2 2 2 2
## 222  22222
## IIIIIII
IiI IIIIIIIIIII
m
## IIIIIIIIIIIIII
IIm
## II    II    II
uuuuuuu
d uuuuuuuuuuuuuu
uuuuuuLduuuuuuuu
uu  uu  uu  u
δδδδ
δδ δδδδδ
δδδδδδδ
δδδ
## +−−+
## +−− −−++++
## +− − + −− + + +
## ++ + +
## 124421331
## 2
## 33222332
## 6
## 55    66   5665
## 11
## 0
## 1
## 2222
## 1
## 222
## 2
## II   II   II   II   II
## IIIIIIII
## I
## Ni
## II    II   III I III
scorrjj
ij
## Nr
rrrrrr
rGx    GxrGy    GyrG    G
r
uuuuuuuuu
## Luuuuuuuu
uu  uu  uu  u uKFu
muumuuI
δδδδδ
δδδδ
δδδ δδ
δδθδθ
## ==
## =
## −−−− +
## ++−−+
## ⎤
## −+−−++
## ⎦
## ⎡⎤
## −++
## ⎣⎦
## ∑∑
## &&
## &&&&
## 11
## 0
NrNr
rrirrrrr
GyGxGxGyGyG
rr
r
mg uF   uF   uMdtδδδδθ
## ==
## +
## ⎫
## ⎡⎤
## −+ ++⋅=
## ⎬
## ⎣⎦
## ⎭
## ∑
## ∑∑


nella  quale  sono  non  sono  stati  considerati  i  termini  a  contorno  derivanti
dall’integrazione per parti.
























## 94
Raccogliendo i termini a fattor comune rispetto alle variazioni δ
u
i
, si ha:

## ()( )()  ()
## ()( )() ()
## 1
## 2
## 131  2  1342
## 1
## 0
## 11
## 2
## 241  2  2431
## 1
## 2
## 4
## 2
## 4
## 2
t
## Np
p
ppp  p  pppp
ppp
p
t
p
pp
p
## Np
p
ppp  p  pppp
ppp
p
p
p
m
uu   K K  uuuusen
mg
senFu
m
uu   K K  uusenuusen
mg
## F
ααα
ρδ
ααα
ρ
## =
## =
## ⎧
## ⎧
## ⎡
## ⎪⎪
## ⎡⎤
## −+−+  −    +−+
## ⎢
## ⎨⎨
## ⎣⎦
## ⎢
## ⎪⎪
## ⎣
## ⎩
## ⎩
## ⎫
## ⎤
## ⎪
## −++
## ⎥
## ⎬
## ⎥
## ⎪
## ⎦
## ⎭
## ⎧
## ⎡
## ⎪
## ⎡⎤
## + −   +− +−+−+
## ⎢
## ⎨
## ⎣⎦
## ⎢
## ⎪
## ⎣
## ⎩
## −+
## ∑
## ∫
## ∑
## &&  &&
## &&  &&
## ()( )()  ()
## ()( )()  ()
## 2
## 2
## 131  2  3124
## 1
## 33
## 2
## 241  2  4213
## 1
## 4
## 2
## 4
## 2
pp
## Np
p
ppp  p  pppp
ppp
p
p
pp
p
## Np
p
ppp  p  pppp
ppp
p
p
u
m
uu   K K  uuuusen
mg
senFu
m
uu   K K  uuuusen
mg
δ
ααα
ρδ
ααα
## =
## =
## ⎫
## ⎤
## ⎪
## +
## ⎥
## ⎬
## ⎥
## ⎪
## ⎦
## ⎭
## ⎧
## ⎡
## ⎪
## ⎡⎤
## + −   +− +−+−+
## ⎢
## ⎨
## ⎣⎦
## ⎢
## ⎪
## ⎣
## ⎩
## ⎫
## ⎤
## ⎪
## −++
## ⎥
## ⎬
## ⎥
## ⎪
## ⎦
## ⎭
## ⎧
## ⎡
## ⎪
## ⎡⎤
## + −   +− +−+−+
## ⎢
## ⎨
## ⎣⎦
## ⎢
## ⎪
## ⎣
## ⎩
## −
## ∑
## ∑
## &&  &&
## &&  &&
## 44
pp
p
## Fuρδ
## ⎫
## ⎤
## ⎪
## ++
## ⎥
## ⎬
## ⎥
## ⎪
## ⎦
## ⎭

## ()()
## ()()
## ()
## }
## 2
## 143232  11
## 2
## 11
## 2
## 23 413412
## 2
## 11
## 2
## 23   22
## 1
## 2222  2
## 2
## 1
## 2222  2
## 2
## 22
## Nina
## IIIIIIIII
mImI Im
## Im
## I
## Nina
## IIIIIIIII
mImI Im
## Im
## I
## II    II
## I
Kd  uuuu  Ld uu  Fu
## L
Kd  uuuu  Ld uuuu
## L
Lu  uF u
δ
δ
## ==
## ==
## ⎧⎫
## ⎪⎪
## ⎡⎤
## +−−+ − +    −+ +   +
## ⎨⎬
## ⎣⎦
## ⎪⎪
## ⎩⎭
## ⎧
## ⎪
## ⎡
## +−−+ − +    +−+−+
## ⎨
## ⎣
## ⎪
## ⎩
## ⎤
## +−+
## ⎦
## ∑∑
## ∑∑
## ()()
## ()
## }
## 2
## 321 44321
## 2
## 11
## 2
## 32   33
## 1
## 2222  2
## 2
## 22
## Nina
## IIIIIIIII
mImI Im
## Im
## I
## II    II
## I
Kd  uuuu  Ld uuuu
## L
Lu  uF u
δ
## ==
## ⎧
## ⎪
## ⎡
## +−−+ − +    +−+−+
## ⎨
## ⎣
## ⎪
## ⎩
## ⎤
## +−+
## ⎦
## ∑∑




## 95
## ()()
## ()
## {}
## ()
## {}
## {}{}
## 2
## 41 2 323   44
## 2
## 11
## 56   5565   66
## 11
## 11
## 1
## 2222  2
## 2
## Nina
## IIIIIII    II
mImI Im
## Im
## I
NiNi
## III IIIII II
scorrscorr
## II
NrNr
rrrrrr
rGxGxGxrGxrGyGy
rr
KduuuuLduuFu
## L
KuuFuKuuFu
muFumumg   Fu
δ
δδ
δδ
## ==
## ==
## ==
## ⎧
## ⎫
## ⎪
## ⎡⎤
## +−−+ − +    −+ +
## ⎨⎬
## ⎣⎦
## ⎪
## ⎭
## ⎩
## −−+− −++
## +− +    ++− − +    +
## +
## ∑∑
## ∑∑
## ∑∑
## &&&&
## {}
## 0
## 1
## 0
## Nr
rrrr
rGGG
r
IMdtθδθδθ
## =
## ⎫
## −+=
## ⎬
## ⎭
## ∑
## &&
##  

Tenendo  conto  che  tale  espressione  deve  annullarsi  qualsiasi  t
## 0
e  t
## 1
,  devono
annullarsi  tutte  le  espressioni  che  moltiplicano  i  termini  delle  variazioni  dei
parametri lagrangiani. In tal modo si giunge alle equazioni del moto del sistema.
Vista  la  complessità  del  sistema  di  equazioni,  nel  seguito,  per  semplicità  di
esposizione,   si   riportano   le   equazioni   del   moto   di   un   pannello   generico
circondato da altri pannelli

4.3 Struttura ricorrente nelle equazioni del moto
L’espressione  appena  ottenuta  tramite  l’applicazione  del  principio  di  Hamilton,
viene  applicata  a  un  modulo  ricorrente  nella  modellazione  di  una  porzione  di
muratura, che è quello di un pannello confinato in ogni lato da altri pannelli.
p
p
## 4
## I1
## I4I2
## I3
## (a)
## U41
## U42
## U43
## U44U24
## U22
## U21
p2
## U23
## U12
## U14
## U11
p1
## U13
## U34
## U31
p3
## U32
## U33
## U7
## (b)
p1
## U5
u4
## U15
## U14
p4
## I4
## U6
## I1
u1
p
u
## 2
## I2
## U10
## U8
p2
## U13
## U16
u3
## I3
## U11
p3
## U12
## U9
## U2
## U1
## U4
## U3

figura  16:  modulo  tipo  di  pannello  affiancato  confinato  da  altri  pannelli;  (a)
numerazione  locale  dei  gradi  di  libertà,  (b)  numerazione  dei  gradi  di  libertà
globali.

I pannelli e le interfacce sono numerate come in figura, con m
i
si indica la massa
totale del pannello i, con m si indica la massa totale del pannello centrale.














## 96
Utilizzando  l’espressione  finale  ottenuta  in  precedenza  dall’applicazione  del
principio  di  Hamilton  per  il  sistema  in  esame  (N
p
## =4,  N
## I
## =4,  N
r
=0),  è  possibile
ottenere le equazioni del moto in funzione dei gdl locali (fig. 16,a). Sostituendo
infine questi con i gradi di libertà e forze globali (u1,...u16 e F1,..F16 indicati in
figura   16,b)   si   ottengono   le   espressioni   delle   espressioni   definitive   delle
equazioni del moto che in forma matriciale come segue:
## MUKU F+=
## &&

Dove con
U si indica il vettore dei gradi di libertà globali :  U = [u
## 1
, ....., u
## 16
## ]
t
## ,
con
F il vettore delle forze esterne, duali ai gradi di libertà :  F = [F
## 1
## , ....., F
## 16
## ]
t
## .
## Con
K  e  M (di  seguito  riportate)  si  sono  indicate  le  matrici  di  massa  e  di
rigidezza dell’intero sistema.

- Matrice di massa (M)

## 11
## 1
## 11
## 22
## 22
## 2
## 00000000000000
## 44
## 00000000000000
## 44
## 00000000000000
## 44
## 00000000000000
## 44
## 00000000000000
## 44
## 000000000000000
## 4
## 00000000000000
## 44
## 0000 0 0 00  0 0  0  0  0  0
## 44
## 0000 0 0 00  0 0  0  0  0  0
## 44
## 0000 0 0 0 0  00 0  0  0  0  0
## 4
## 00
mm
mm
mm
mm
mm
m
mm
mm
mm
m
## ))
## )
## ))
## ))
## ))
## )
## 3
## 33
## 33
## 44
## 4
## 44
## 000000 0 00 0 0 0 0
## 4
## 00000000000000
## 44
## 00000000000000
## 44
## 0000 0 0 0 0  0  0  0 0  00
## 24
## 0000 0 0 0 0  0  0  0 0  0  00
## 2
## 0000 0 0 0 0  0  0  0 0  00
## 42
m
mm
mm
mm
m
mm
## ⎡⎤
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## ⎣⎦
## )
## ))
## ))
## ))
## )
## ))
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥




## 97
- Matrice di rigidezza (K)



























































## 98

Il pedice j, variabile da 1 a 4, inserito nei termini che compaiono nella matrice di
rigidezza,  indica  il  numero  d’ordine  del  pannello  o  dell’interfaccia  da  cui
proviene.
I termini senza indice sono quelli che si riferiscono al pannello centrale.

Per  una  lettura  più  agevole  sono  stati  associati  dei  colori  ad  ogni  pannello  e  ad
ogni interfaccia dello schema considerato.

Legenda colori:           Pannello centrale
Pannello o interfaccia 1
Pannello o interfaccia 2
Pannello o interfaccia 3
Pannello o interfaccia 4

Valgono inoltre le seguenti posizioni:

- Termini relativi alle matrici di rigidezza dei pannelli:
jjj
jjj
senKKS
## KKC
senKKS
## KKC
α
α
α
α
## )
## )
## )
## )
## ⋅+=
## ⋅+=
## ⋅+=
## ⋅+=
## )(
cos)(
## )(
cos)(
## 21
## 21
## 21
## 21


- Termini relativi alle matrici di rigidezza delle interfacce:
## ()
## 2
## 1
## 2
## 2
## 11
## 22
## 2
## 11
## 22
## 1
## 2
na
mm
m
j
j
j
nana
mmmm
mm
jj
j
jj
nana
mmmm
na
mm
jm
m
jj
j
jscorr
j
## Kd
a
## L
KdKd
b
## LL
KdKd
cK
## LL
eK
## =
## ==
## ==
## =
## ⎛⎞
## ⋅
## ⎜⎟
## ⎝⎠
## =
## ⎛⎞⎛⎞
## ⋅⋅
## ⎜⎟⎜⎟
## ⎝⎠⎝⎠
## =−
## ⋅⋅
## ⎛⎞
## =−⋅+
## ⎜⎟
## ⎝⎠
## =
## ∑
## ∑∑
## ∑∑
## ∑









## 99
Osservando  la  matrice  di  massa,  si  nota  che  è  fortemente  bandata  (larghezza  di
banda pari a tre), tale circostanza è legata al fatto che la matrice di massa globale
ha  la  stessa  larghezza  di  banda  della  matrice  di  massa  elementare  del  singolo
pannello.


## -
Matrici dei pannelli e delle interfacce

Come caso particolare, della formulazione appena presentata, si possono ricavare
le matrici di massa e di rigidezza relative ai contributi del pannello singolo o di
una singola interfaccia.

## -
## Pannello

Matrice di massa

## 00
## 44
## 00
## 44
## 00
## 44
## 00
## 44
mm
mm
mm
mm
## ⎡⎤
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎣⎦


Matrice di rigidezza

## ()
## 22
## 22
## 22
## 22
## 12
sensen
sensensensen
## KK
sensen
sensensensen
αααα   αα
αα    α    ααα
αααα    αα
ααα    αα    α
## ⎡⎤
## −−
## ⎢⎥
## −−
## ⎢⎥
## +
## ⎢⎥
## −−
## ⎢⎥
## ⎢⎥
## −−
## ⎣⎦


Dove si è indicato con m la massa totale del pannello, con K1 e K2 le rigidezze
tangenti delle molle diagonali, e
α=arctg(H/B).

























## 100

## -
Matrice di rigidezza Interfaccia

## 2222
## 111111
## 2222
## 2222
## 11111111
## 2222
## 11
## 00
## 00
nanannanna
iiiiiiiiiiii
iiiiii
nananananananana
iiiiiiiiiiiiiiii
nn
iiiiiiii
ii
ii
kdkdkdkdkdkd
## LL
## LLLL
kdkdkdkdkdkdkdkd
kk
## LLLL
## LLLL
## ======
## ========
## ==
## −++−−
## −+−+−+−−
## +
## ∑∑∑∑∑∑
## ∑∑∑∑    ∑∑   ∑∑
## ∑∑
## 2222
## 11  111111
## 2222
## 11
## 2222
## 111111
## 2222
## 00
## 00
nananananananana
iiiiiiiiiiiiiiii
nn
ii  iiiiii
ii
ii
nananananana
iiiiiiiiiiii
iiiiii
kdkdkdkdkdkdkdkd
kk
## LLLL
## LLLL
kdkdkdkdkdkd
## LL
## LLLL
## == ======
## ==
## ======
## −−+−−+−+
## −−−+
## ∑∑ ∑∑   ∑∑    ∑∑
## ∑∑
## ∑∑∑∑∑∑
## 0000
## 0000
scorrscorr
scorrscorr
kk
kk
## ⎡⎤
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## ⎢⎥
## −
## ⎢⎥
## −
## ⎢⎥
## ⎣⎦



Dove  si  è  indicato  con  K
i
la  rigidezza  tangente  della  i-esima  molla,  con  d
i
la
distanza della i-esima molla dal primo estremo (vedi 4.1.3), con L la lunghezza
dell’interfaccia,  con  K
scorr
la  rigidezza  allo  scorrimento  e  con  na  il  numero  di
molle flessionali attive.




























## 101

4.4 Legami costitutivi
4.4.1 Elemento interfaccia
L’interfaccia deve simulare sia il comportamento assiale-flessionale dei pannelli
che collega, sia lo scorrimento che può avvenire tra due elementi contigui.

4.4.1.1 Comportamento assiale
L’interfaccia  simula  la  rigidezza  assiale  e  flessionale  dei  pannellli  che  collega,
tramite un numero discreto di molle poste in direzione ortogonale alla direzione
dell’interfaccia stessa, vedi figura 8b.
Il  legame  costitutivo  delle  molle  trasversali  è  elasto-plastico  con  limite  negli
spostamenti sia a compressione che a trazione.
## EE
## (a)(b)
utuuty
utyutuutyutu
## Fty
## Fcy
## Fty
## Fcy
## F
u
## F
u


figura 17: legame costitutivo molle trasversali interfaccia; (a) molla integra a
trazione, (b) molla rotta a trazione.

Non appena si raggiunge il limite di rottura a compressione si verifica la rottura
della  molla  con  azzeramento  del  carico,  che  viene  ridistribuito  al  resto  della
struttura  e  tale  molla  non  interverrà  più  nell’analisi,  in  modo  da  simulare  lo
schiacciamento del calcestruzzo.
Se  viene  raggiunto  lo  spostamento  ultimo  a  trazione,  la  molla  non  sarà  più  in
grado   di   sopportare   sforzi   di   trazione   può   invece   sopportare   sforzi   di
compressione se si determina il ricarico a compressione, in tal modo si modella
la condizione di materiale fessurato.
Allo  scopo  di  considerare  un  possibile  degrado  delle  proprietà  elastiche  della
struttura,  si  prevedono  due  possibili  comportamenti  isteretici  a  compressione,
con scarico iniziale e con scarico orientato all’origine. A trazione si prevede solo
lo scarico orientato all’origine.















## 102
## 12
## 3
## 5
## 6
## 0
## 4
## 7
## (a)
## 1
## 3
## 0
## 4
## 5
## 3=7
## 2=8
## (b)

figura 18: comportamenti isteretici previsti; (a) scarico elastico,
(b) scarico orientato all’origine


Dato   che   nelle   molle   trasversali   è   concentrata   la   deformabilità   assiale   e
flessionale  dei  pannelli,  le  proprietà  meccaniche  di  queste  dovranno  essere
ricavate  a  partire  dalle  caratteristiche  di  entrambi  i  pannelli  a  contatto  con
l’interfaccia.
Il comportamento assiale della muratura si considera caratterizzato da un legame
costitutivo  ortotropo,  in  ognuna  delle  direzioni  principali  si  prevede  un  legame
elastoplastico governato dai seguenti parametri:
E che rappresenta il modulo di deformabilità normale,
σ
c
e σ
t
che rappresentano
le tensioni limite a compressione e a trazione,
ε
cu
e

ε
tu
che rappresentano invece le
deformazioni  ultime  a  compressione  e  a  trazione.  Tali  parametri  si  considerano
noti.

La  procedura  che  si  segue  per  trasferire  le  proprietà  della  muratura  dei  pannelli
alle  molle  di  interfaccia  consiste  nel  concentrare  prima  le  caratteristiche  di
deformabilità di tutto il pannello in corrispondenza delle sezioni di estremità. Si
vengono  a  determinare  due  molle,  ognuna  delle  quali  si  riferisce  a  un  pannello,
disposte  in  serie.  Le  caratteristiche  finali  da  attribuire  alle  interfacce  vengono
quindi determinate attraverso semplici operazioni di equivalenza.



## 103
## M1
## Uty1
## Utu1
## Fty1
## Fcy1
## Utu1
## Fty1
## Uty1
## Fcy1
## M2
E2 , G2 , s2
E1 , G1 , s1

figura 19: procedura di concentrazione delle caratteristiche della muratura
alle molle delle interfacce.

La  prima  fase,  in  cui  le  caratteristiche  di  ogni  pannello  vengono  concentrate  in
delle  molle  di  estremità  (Kp),  avviene  imponendo  l’equivalenza  tra  il  modello
continuo (costituito dalla muratura reale considerata come un solido omogeneo)
e quello discreto (costituito dalle due molle di estremità come indicato in figura)
in presenza di carico normale centrato.
modello
continuo
## F
λ
rigido
## F
## Kp
## Kp

figura 20: equivalenza tra il pannello e le molle Kp














## 104
## -
Rigidezza equivalente

Uguagliando  le  rigidezze  assiali  offerte  dal  modello  continuo  e  quella  invece
relativa alle due molle K
p
disposte in serie, si ottiene immediatamente:

## 2
p
## Es
## K
## L
λ⋅⋅
## =⋅
## (14)
Dove si è indicato con E il modulo della muratura  relativamente alla direzione di
carico  considerata,  con
λ  l’interasse  delle  molle,  con  s  e  L  rispettivamente  lo
spessore e l’altezza del pannello.

## -
Forze di snervamento equivalenti

Considerando  le  tensioni  limite  della  muratura  nella  direzione  considerata,  le
corrispondenti  forze  di  snervamento  delle  molle  si  ottengono  dalla  semplice
considerazione di equivalenza:

t
p
tu
c
p
cu
sF
sF
σλ
σλ
## =
## =
## (15)
Che equivale ad assumere una distribuzione uniforme di tensioni corrispondente
all’area di influenza della molla.

## -
Spostamenti ultimi

Immaginando di concentrare la deformabilità di metà pannello, e assumendo uno
stato deformativo uniforme lungo l’altezza, si ha :

tutu
cucu
## L
## U
## L
## U
ε
ε
## ⋅=
## ⋅=
## 2
## 2
## (16)

Avendo  ricavato  tutti  i  parametri  delle  molle  K
p
dei  pannelli,  i  parametri
definitivi si ricavano considerando le due molle in serie (fig.19), si ha pertanto:

## 12
## 12
pp
pp
## KK
## K
## KK
## ⋅
## =
## +
## (17)
Relativamente  alla  forza  di  snervamento  della  molla  complessiva,  questa  sarà
ovviamente data dalla più piccola delle forze di snervamento relative ai pannelli
connessi.





## 105
Gli spostamenti ultimi a trazione e a compressione, si ottengono sommando allo
spostamento  della  molla  che  si  plasticizza  quello  elastico  dell’altra  molla  in
serie.

## 2
## 2
cy
## F
cucu
## F
ty
## F
tutu
## F
## F
## L
## U
## K
## F
## L
## U
## K
ε
ε
## =⋅   +
## =⋅   +
## (18)
dove:
ε
tu
## Fmin
e ε
cu
## Fmin
sono  le  deformazioni  ultime  a  trazione  e  compressione
relative  al  pannello  che  possiede  Fy  minore  (F
ty
min
## ),  K
## Fmax
è  la  rigidezza  della
molla  di  estremità  relativa  al  pannello  che  possiede  forza  di  snervamento
maggiore.


4.4.1.2 Legge di scorrimento
Superficie di
scorrimento con attrito
## Escorr
τ
γ

figura 21: Comportamento a scorrimento dell’interfaccia

Lo scorrimento è regolato solo dalla porzione di muratura reagente. La tensione
tangenziale limite dell’interfaccia, in accordo con il criterio di scorrimento alla
Mohr-Coulomb, risulta data da:

m
cτφσ=+⋅
## (19)
## Dove
σ
m
si assume pari alla compressione media sull’interfaccia.

La coesione (c) e l’angolo di attrito (φ) sono due proprietà relative alle superfici
di contatto (a prescindere dalla presenza o meno di malta). Proprio il contributo
della  malta  alla  coesione  totale,  viene  azzerato  in  corrispondenza  della  prima
fessurazione.














## 106
σ
τlim
φ
c


figura 22: Dominio di scorrimento alla Coulomb


La forza di taglio limite è determinata, integrando l’espressione precedente nella
porzione di sezione non fessurata, indicando con Ac proprio l’area reagente, con
N lo sforzo di compressione cui è soggetta l’interfaccia e supponendo infine una
distribuzione delle tensioni tangenziali uniforme, si ha :

NAcT
c
## ⋅+⋅=φ
lim
## (20)
Quando una interfaccia si trova sulla superficie di scorrimento e l’incremento di
stato  tensionale  è  tale  che  porterebbe  l’interfaccia  a  violare  tale  dominio,  si
attivano gli scorrimenti plastici. Utilizzando un legame elastoplastico associato e
considerando   che   il   problema   è   regolato   da   due   parametri   di   tensione   e
deformazione  che  sono  la  tensione  tangenziale
τ  (duale  dello  scorrimento
angolare
γ)  e  la  tensione  di  compressione  media  σ
m
(duale  della  deformazione
normale nella direzione ortogonale all’interfaccia
ε
m
), si ha:

λ
σ
ε
μσττστ
dd
csign
pl
mm
## ⋅
## ∂
## Φ∂
## =
## −−⋅=Φ
r
## )(),(

λτλ
τ
γ
λμλ
σ
ε
dsigndd
ddd
pl
m
pl
m
## ⋅=
## ∂
## Φ∂
## =
## −=
## ∂
## Φ∂
## =
## )(


L’ipotesi   di   legame   associato   fa   si   che   si   determina   una   componente   di
deformazione plastica d
ε
pl
, nota come “dilatanza” che tenderebbe ad allontanare i
pannelli  l’uno  rispetto  all’altro,  violando  l’evidenza  fisica.  Per  ovviare  a  tale
problema si è pensato di operare secondo due possibili strategie:



## 107
la  prima  strategia  consiste  nel  considerare  nel  passo  di  integrazione  un  legame
elasto-plastico  con  forza  di  snervamento  corrispondente  al  valore  della  tensione
di  compressione  media  (
σ
m
)  di  inizio  passo;  l’altro  procedimento  adottato  è
quello di ignorare la componente di “dilatanza” (d
ε
pl
) e di valutare comunque lo
scorrimento plastico a partire dalle leggi di flusso del legame associato. Si riporta
il calcolo dello scorrimento plastico relativo alla seconda strategia.

L’ampiezza  degli  incrementi  di  deformazioni  plastiche  si  ricava  imponendo
d
## Φ=0 :

## ()()
## 0=−⋅+−−=
## ∂
## Φ∂
## +
## ∂
## Φ∂
## =Φ
pl
scorr
pl
mmmm
m
ddKsignddKdddγγτεεμτ
τ
σ
σ
## )(

()()0=⋅−⋅+−=ΦλτγτεμdsigndKsigndKd
scorrmm
## )()(


Da cui si ricava:

scorrscorr
mmscorr
## K
dN
dsign
## K
dKdKsign
d−⋅=
## −⋅
## =
γτ
εμγτ
λ)(
## )(


Considerando  che  il  termine  K
m
dε
m
rappresenta  l’incremento  di  sforzo  di
compressione  N  agente  sull’interfaccia,  lo  scorrimento  plastico  si  può  scrivere
come :

scorrscorr
scorr
pl
## K
dNsign
d
## K
dNsigndK
d
## ⋅⋅
## −=
## ⋅⋅−⋅
## =
## )(
## )(
τμ
γ
τμγ
γ
## (21)































## 108
4.4.2 Molle diagonali dei pannelli

Le molle diagonali nei pannelli devono simulare il comportamento a taglio della
muratura,  il  meccanismo  di  rottura  che  devono  riprodurre  è  il  meccanismo  di
rottura per fessurazione diagonale.
Dal  punto  di  vista  del  legame  costitutivo  si  possono  seguire  due  approcci,  il
primo  consiste  nel  considerare  entrambe  le  molle  con  una  limitata  o  nulla
resistenza  a  trazione,  in  modo  da  simulare  i  fenomeni  di  fessurazione.  Tale
approccio  è  senz’altro  indicato  in  ambito  dinamico  poiché  da  la  possibilità  di
associare  a  ogni  molla  un  diverso  stato  di  degrado.  Il  secondo  approccio
senz’altro  più  semplice,  consiste  nel  considerare  le  due  molle  con  lo  stesso
legame   costitutivo   e   con   lo   stesso   comportamento   sia   a   trazione   che   a
compressione.  In  questo  caso  l’uso  delle  due  molle  è  senz’altro  superfluo,
basterebbe  infatti  una  sola  molla  a  taglio  con  rigidezza  e  resistenza  esattamente
doppie rispetto a quelle che andrebbero attribuite a ciascuna delle due molle.
Nel  presente  lavoro,  al  fine  di  semplificare  il  più  possibile  il  problema  (almeno
in  una  prima  fase),  si  seguirà  il  primo  approccio,  attribuendo  un  legame  elasto-
perfettamente plastico ad entrambe le molle (figura 21).Vengono considerati due
possibili   comportamenti   isteretici   (scarico   con   rigidezza   iniziale   e   scarico
orientato all’origine).
## 4
## 5
## 6
## 4
## 5
## 6
## (a)
## (b)

figura 23: legame costitutivo e comportamento isteretico considerato per le molle
diagonali;  a) scarico con rigidezza iniziale, b) scarico orientato
all’origine


Si  indicano  con  F
diag
la  forza  massima  delle  molle  diagonali,  con  K
diag
la
rigidezza e con U
diag
lo spostamento ultimo.

Tali  parametri  devono  essere  messi  in  relazione  alle  caratteristiche  meccaniche
della muratura. Si consideri a tal proposito un pannello soggetto a taglio e sforzo
normale (fig.22). Il comportamento della muratura può essere ben approssimato ,
come è stato detto nel capitolo 1, tramite una bilatera. Si indica con G il modulo
elastico della muratura, con Tu il valore massimo di taglio sopportabile e con
δu
lo  spostamento  orizzontale  ultimo  che  provoca  la  rottura  per  fessurazione
diagonale.



## 109
## T
## T
δ
## T
## T
δ molla
F molla
δ

figura 24: equivalenza a taglio tra il modello continuo e il modello discreto.

La  resistenza  a  taglio  per  fessurazione  diagonale  della  muratura  viene  espressa
mediante  la  definizione  di  una  tensione  tangenziale  media  ultima  (
τ
u
)  che  viene
ricavata utilizzando il già descritto criterio di rottura di Turnsek e Cacovic [2], la
cui   espressione,   ampiamente   commentata   nel   capitolo   1,   viene   di   seguito
riscritta:

## 1
## 15
n
uk
k
σ
ττ
τ
## =+                                           (22)
Tale espressione deve essere tuttavia adattata al caso in esame, poiché questa
è  stata  ottenuta  considerando  un  pannello  compresso  solo  lungo  la  direzione
verticale.  Nel  modello  proposto  invece,  un  pannello  può  essere  affiancato  in
ciascun lato da altri elementi che possono comprimere il pannello in esame sia in
direzione  x  che  in  direzione  y  (dove  x  e  y  sono  le  direzioni  del  sistema  di
riferimento locale del pannello).
Le  ipotesi  alla  base  del  criterio  rimangono  quelle  descritte  nel  capitolo  1,
deve  essere  variata  soltanto  l’espressione  della  tensione  principale  di    trazione,
per tenere conto della contemporanea presenza di
σx e σy.
Omettendo  per  brevità  i  passaggi,  l’espressione  della  tensione  principale  di
trazione risulta:
## 2
## 2
## 22
τ
σσσσ
σ+
## ⎟
## ⎟
## ⎠
## ⎞
## ⎜
## ⎜
## ⎝
## ⎛
## −
## +
## +
## =
yxyx
t

Uguagliando la tensione principale di trazione alla resistenza a trazione (
σ
tu
## ),
si   ottiene   la   nuova   espressione   del   criterio   di   rottura   da   sostituire   alla
formulazione classica del criterio di Turnsek e Cacovic:

## 2
## 51
## 5151
## 1
k
yx
k
y
k
x
ku
τ
σσ
τ
σ
τ
σ
ττ
## .
## ..
## +++=
## (23)














## 110
che naturalmente contiene come caso particolare la (22).
E’  evidente  che  il  criterio  proposto  va  applicato  attribuendo  ai  valori
σ
x
e  σ
y
le
tensioni medie di compressione sulle facce del pannello.
## Noto
τ
u
,  il  taglio  ultimo  relativo  alla  rottura  per  fessurazione  diagonale,  si
esprimerà :

tuu
AT⋅=τ                                                 (24)
Per  quanto  riguarda  lo  spostamento  ultimo  della  parete  (
δ
u
),  coerentemente  con
quanto  proposto  da  Magenes  e  Calvi[3],  si  esprime  in  termini  di  deformazione
angolare ultima (
γ
u
) della muratura:

## %./530==
pultimoultimo
## Hδγ                                  (25)
dove : Hp è l’altezza del pannello.

Noti il taglio e lo spostamento ultimo, le relative grandezze delle molle diagonali
si valutano con considerazioni su semplici equilibri e/o congruenze.
Nel seguito si riportano la forza e lo spostamento ultimi della molla diagonale e
la  rigidezza  iniziale,  nell’ipotesi  che  entrambe  le  molle  abbiano  un  legame
costitutivo simmetrico rispetto all’origine, e indicando con
α l’arctg (H/B).

## 22
ukT
diag
## TA
## F
τ
αα
## ⋅
## ==
## ⋅⋅
## (26,a)

diagup
## Hδγα=⋅ ⋅
## (26,b)

## 2
## 2
diag
## P
## GA
## K
## H
α
## ⋅
## =
## ⋅⋅
## (26,c)










## 111

## Bibliografia

[1] R. W. Clough J. Penzien : “Dinamic of structures”, Mc Graw-Hill.
[2] G.  Magenes,  G.  M.  Calvi  :  “In  plane  seismic  response  of  brick  masonry
walls”,  Earthquake  Engineering  and  structural  Dynamics,  Vol.  26,  1091-
## 1112  (1997).
[3] V.  Turnsek,  F.  Cacovic:  “Some  experimental  result  on  the  strength  of
brick  masonry  walls”,  Proc.  Of  the  2nd  Int.  Brick  Masonry  Conference,
Stoke-on-Trent, 1971, pp 149-156.






















## C
## 2
## +e
## 1
## +
## +c
## 2
## +c
## 4

## -C·S
## C
## 2
## +b
## 2
## +
## +b
## 4

C·S           0           e
## 1
## 0 -c
## 2
## -b
## 2
## 0             0             0             0             -c
## 4
## 0            -b
## 4

## -C·S
## S
## 2
## +c
## 1
## +
## +c
## 2
## +b
## 3

## C·S
## -S
## 2
## +b
## 1
## +
## +b
## 3

## -c
## 1
## 0            -b
## 1
0             0            e
## 2
## 0            -c
## 3
## -b
## 3
## 0             0             0

## C
## 2
## +a
## 2
## +
## +a
## 3
## +a
## 4

-C·S          0             0             0          -b
## 2
## -a
## 2
## 0            -e
## 3
## 0             0            -b
## 4
## 0            -a
## 4


## S
## 2
## +a
## 1
## +
## +a
## 3
## +e
## 4

## -b
## 1
## 0            -a
## 1
## 0             0             0             0             -b
## 3
## -a
## 3
## 0            -e
## 4
## 0
## S
## 1
## 2
## +c
## 1
## C
## 1
## ·S
## 1
## -S
## 1
## 2
## +b
## 1
0             0             0             0             0             0             0             0             0
## C
## 1
## 2
## +e
## 1
## -C
## 1
## ·S
## 1
0             0             0             0             0             0             0             0             0
## S
## 1
## 2
## +a
## 1
0             0             0             0             0             0             0             0             0
## C
## 2
## 2
## +c
## 2
## -C
## 2
## 2
## +b
## 2
## C
## 2
## ·S
## 2
## 0             0             0             0             0             0
## C
## 2
## 2
## +a
## 2
## -C
## 2
## ·S
## 2
## 0             0             0             0             0             0
sim       S
## 2
## 2
## +e
## 2
## 0             0             0             0             0             0
## C
## 3
## 2
## +e
## 3
## -C
## 3
## ·S
## 3
## C
## 3
## ·S
## 3
## 0             0             0
## S
## 3
## 2
## +c
## 3
## -S
## 3
## 2
## +b
## 3
## 0             0             0
## S
## 3
## 2
## +a
## 3
## 0             0             0
## C
## 4
## 2
## +c
## 4
## -C
## 4
## ·S
## 4
## -C
## 4
## 2
## +b
## 4
## S
## 4
## 2
## +e
## 4
## C
## 4
## ·S
## 4

## C
## 4
## 2
## +a
## 4

































## 113



5 Sviluppo di un programma di calcolo non lineare
che utilizza il macromodello proposto

## Premessa
Una  procedura  di  calcolo  non  lineare  che  consente  di  eseguire  analisi  strutturali
utilizzando  il  macromodello  proposto  nell’ambito  di  questo  lavoro  è  stata
implementata in un programma di calcolo realizzato in
## Visual Basic
## ®
## .
In questo capitolo verranno descritte le principali caratteristiche del programma,
e  le  procedure  generali  mediante  le  quali  viene  eseguita  l’analisi.  Verrà  inoltre
presentato  un  quadro  sulle  potenzialità  attuali  del  software  sviluppato  e  sulle
estensioni previste nell’ambito della presente ricerca.
In  questa  fase  della  ricerca  si  è  stabilito  un  proficuo  rapporto  di  collaborazione
con l’azienda
S.T.S. - Software Tecnico Scientifico s.r.l. di Catania. Il rapporto di
collaborazione  con  la
S.T.S.  si  è  rilevato  particolarmente  utile  nella  definizione
delle  interfacce  di  input-output  e  nella  individuazione  di  tutti  quei  problemi  di
carattere  pratico-professionale  che  troppo  spesso  sfuggono  negli  ambienti  di
ricerca. Tale sinergia ha consentito di creare un software scientifico avanzato che
molto presto potrà essere reso disponibile anche in ambiente professionale.

5.1 Definizione del modello
5.1.1 Immissione dei dati

I dati di input del modello possono essere forniti sia tramite un file di testo (
file
dati
) che tramite interfaccia grafica.
Il  file  dati  è  organizzato  in  blocchi  omogenei  di  dati,  ognuno  identificato  da
una  specifica  parola  chiave  racchiusa  tra  parentesi  quadre.  Il  blocco  viene  poi
chiuso  dalla  parola  chiave
End.  All’interno  di  ogni  blocco  i  dati  vengono
assegnati  indicando  prima  il  nome  che  identifica  la  proprietà  che  si  desidera
impostare,  seguito  dal  segno  di  uguale  e  dal  valore,  numero  o  stringa,  da
assegnare  alla  proprietà.  In  questo  modo  l’ordine  con  cui  le  diverse  proprietà
devono   essere   assegnate   non   è   imposto   e   l’utente   ha   la   massima   libertà
nell’organizzare ogni blocco di dati. Ad esempio la seguente riga assegna i valori
1 e 2 rispettivamente alle proprietà
A e B:
















## 114

## A=1 B=2

La  possibilità  di  immettere  i  dati  del  modello  in  forma  grafica  è  fornita
mediante  l’integrazione  tra  il  programma  di  calcolo  e  il  software  commerciale
CDS realizzato dalla S.T.S. Al momento tale integrazione consiste nel fatto che,
una  volta  immesso  un  modello  in  CDS,  il  programma  può  generare  per  tale
modello  un  file  dati  leggibile  dal  programma
Parete.  Nel  prossimo  futuro  si
prevede di realizzare una integrazione più diretta tra i due programmi.
5.1.2 Output dei risultati
L’output  fornito  dal  programma  consiste  sia  in  files  di  testo,  nei  quali  vengono
salvate tutte le quantità che vengono richieste tramite la specifica sezione del file
dati (o tramite l’interfaccia grafica), sia in grafici che visualizzano su schermo la
deformata e le distribuzione delle tensioni ai vari passi di ogni analisi eseguita.

## 5.1.3 Geometria
Allo stato attuale è possibile considerare soltanto schemi piani. Il primo passo
nella  definizione  dello  schema  geometrico  consiste  nell’assegnazione  dei  punti
che  costituiscono  il  modello  (
nodi),  assegnandone  le  coordinate  rispetto  un
sistema di riferimento assoluto. Tali nodi vengono numerati automaticamente in
ordine sequenziale.
Successivamente   è   possibile   inserire   gli   elementi   di   tipo
pannello
deformabile a taglio,
aventi forma di quadrilatero regolare e gli elementi di tipo
pannello  rigido,  di  forma  poligonale  con  un  arbitrario  numero  di  lati.  Tali  due
tipi  di  elemento,  descritti  nel  capitolo  6,  permettono  la  modellazione  della
muratura. Per ognuno di tali elementi è necessario specificare i numeri dei nodi
che  costituiscono  i  vertici  (proprietà
joints),  lo  spessore  (proprietà  Th)  e  il
nome  del  materiale,  che  deve  essere  precedentemente  definito  (propretà
## Mat),
come verrà meglio chiarito nel successivo paragrafo 5.1.4.
In  aggiunta  ai  due  elementi  sopra  descritti,  il  programma  permette  anche
l’inserimento  di
cordoli  di  piano.  Tali  elementi  consistono  in  una  serie  di
elementi  rigidi  (
bracci  rigidi)  interconnessi,  tra  loro  e  agli  altri  elementi  del
modello, mediante interfacce. Le proprietà di deformabilità del cordolo vengono
concentrate  in  corrispondenza  delle  interfacce  che  si  vengono  a  formare  tra  due
bracci  rigidi  contigui.  I  cordoli  di  piano  possono  essere  definiti  semplicemente
specificando, nell’apposita sezione del file dati o mediante l’interfaccia grafica, i
nodi che formano l’allineamento che determina l’asse del cordolo.
Nel  breve  file  dati  di  esempio  che  segue  vengono  definiti  alcuni  nodi  e  un
pannello:


















## 115
## .
## .
## .
## [COORDS]
x=0 y=70
x=70 y=70
x=110 y=70
x=0 y=70
x=70 y=70
x=110 y=70
## End

## [PANELS]
joints=2,3,5,4
mat=masonry1
th=0.50
## End
## .
## .
## .

figura 1: Esempio di file dati per la definizione di nodi e di elementi pannello
e rappresentazione grafica ottenuta.

Per  brevità  non  si  riporta  nel  dettaglio  la  sintassi  del  file  dati  relativa
all’inserimento di cordoli di piano.
5.1.4 Caratteristiche meccaniche
Le   proprietà   meccaniche   della   muratura   possono   essere   caratterizzate   dai
parametri descritti nel capitolo 4. In particolare, ai fini della completa definizione
del  comportamento  meccanico  di  tale  materiale,  è  necessario  definire  tutti  i
parametri atti a descrivere le non-linearità che il modello consente di trattare.
A  Ciascun  pannello,  sia  esso  deformabile  a  taglio  o  rigido,  è  attribuito  un
materiale. Inoltre, al fine di determinare le caratteristiche meccaniche di una data
interfaccia, verranno prese in considerazione le proprietà dei materiali relativi ai
due  elementi  pannello  che  sono  connessi  dall’interfaccia  considerata  con  le
modalità descritte nel capitolo 4.
All’interno del file dati è prevista una sezione
[Materials] nella quale è
possibile elencare i materiali e le rispettive proprietà; all’interno di tale sezione a
ogni  materiale  è  attribuito  un  nome,  al  quale  deve  essere  fatto  riferimento  nella
definizione dei pannelli (proprietà
Mat nella sezione [Panels]).
In aggiunta a tale procedura standard, viene lasciata all’utente la possibilità di
specificare  direttamente  le  proprietà  meccanica  di  una  particolare  interfaccia.
Tale  possibilità  risulta  utile  nei  casi  in  cui  mediante  l’interfaccia  si  vuole
modellare  ad  esempio  il  comportamento  della  malta  tra  elementi  rigidi.  Per
brevità si omette la descrizione della sintassi relativa a tale funzionalità.
5.1.5 Vincoli esterni
Ogni lato di qualsiasi elemento che non si trova a contatto con altri elementi ha
in  generale  tre  gradi  di  libertà:  traslazione  nella  direzione  del  lato,  traslazione
nella  direzione  ortogonale  al  lato,  rotazione.  Al  fine  di  limitare  o  impedire  tali
gradi  di  libertà  è  possibile,  per  ognuno  di  essi,  definire  un  vincolo,  che  può
















## 116
essere  fisso  o  cedevole  elasticamente.  Ciò  è  conforme  all’impostazione  teorica
riportata nel capitolo 6.


v1
v2
v3


figura 2: Esempio di elemento con un lato vincolato:
v
## 1
= vincolo elastico
alla  traslazione  nella  direzione  del  lato  stesso,
v
## 2
=  vincolo  elastico  alla
traslazione  ortogonale  alla  direzione  del  lato,
v
## 3
=  vincolo  elastico  alla
rotazione del lato.


I  vincoli  esterni  possono  essere  definiti  all’interno  della  sezione  denominata
[Restraints] del file dati. Per ogni lato vincolato devono essere specificati i
numeri  dei  due  nodi  che  individuano  il  lato  (proprietà
joints)  e  i  codici  di
vincolo per ognuno  dei  tre  gradi  di  libertà  sopra descritti (proprietà
X, Y e R). I
codici di vincolo ammessi sono:
0 vincolo non presente;
-1     vincolo     fisso;
k>0  vincolo cedevole elasticamente con rigidezza k.

5.1.6 Definizione dei carichi e delle analisi statiche
Una volta definito il modello, è necessario assegnare i carichi agenti. E’ possibile
applicare  dei  carichi  concentrati  in  corrispondenza  di  ogni  elemento  pannello  o
elemento  rigido,  tali  forze  possono  essere  concentrate  sia  in  corrispondenza  di
uno  dei  vertici  dell’elemento  stesso  oppure  in  corrispondenza  del  baricentro.  Si
possono  inoltre  applicare  forze  o  momenti  concentrati  in  corrispondenza  di
ognuno dei punti utilizzati nella definizione di un cordolo.
Ogni forza costituisce un
carico elementare. Nella definizione del modello è
possibile  definire  delle
distribuzioni  di  carico  (nella  sezione  [LOADS]  se  si
immette  l’input  tramite  file  dati).  Ciascuna  distribuzione  è  composta  da  un
identificativo e da un insieme di carichi elementari.















## 117
Nell’esempio  seguente  viene  definita  una  distribuzione  di  carico  chiamata
prova composta  da  tre  forze  applicate  ai  nodi  3  e  4  del  pannello  1  e  nel  suo
baricentro. Le proprietà utilizzate sono:
## -
name = identificativo della combinazione di carico;
## -
elem = tipo di elemento (p.es. P=pannello deformabile a taglio);
## -
id = identificativo dell’elemento;
## -
joint = numero del nodo locale a cui è applicato il carico oppure 0 per
indicare il baricentro;
## -
Fx = componente x della forza;
## -
Fy = componente y della forza.


## .
## .
## .
## [LOADS]
name=prova
elem=P id=1
joint=0
## Fx=0 Fy=-500000

elem=P id=1
joint=3
## Fx=0 Fy=-500000

elem=P id=1
joint=4
## Fx=0 Fy=-500000

## End
## .
## .
## .

figura 3: Esempio di file dati per la definizione dei carichi.

Il  programma  attualmente  è  in  grado  di  eseguire  analisi  statiche  non  lineari  a
controllo di spostamento. Nel file dati è possibile definire un numero arbitrario di
analisi  statiche  all’interno  della  sezione
[STATICS];  l’utente  dopo  avere
mandato  in  esecuzione  il  programma,  può  decidere  quali  analisi  mandare  in
esecuzione.
I  carichi  che  verranno  applicati  durante  una  analisi  statica  sono  assegnati  come
combinazione lineare delle combinazioni di carico precedentemente definite nel
blocco
[LOADS]. Per ciascuna combinazione di carico deve essere specificato il
nome e il coefficiente della combinazione lineare. Il carico risultante costituisce
il carico di riferimento per l’analisi.
All’interno  della  sezione
[STATICS]  del  file  dati  l’utente  può  specificare
una  uno  stato  iniziale  e  una  lista  di  moltiplicatori.  Lo  stato  iniziale  può  essere
scarico oppure lo stato finale di una analisi precedente. L’analisi verrà condotta
scalando il carico di riferimento da zero al primo dei moltiplicatori indicati, poi
















## 118
da questo al secondo, poi dal secondo al terzo e così via. Ciò consente di definire
analisi cicliche.
La seguente porzione di file dati definisce due analisi statiche:
## -
La  prima,  di  nome  analisi1,    parte  da  condizioni  iniziali  nulle  e  ha
come   moltiplicatori   del   carico   di   riferimento   1,-1,1,-1,1,-1   (carico
ciclico); il carico di riferimento è costituito dalla distribuzione
carico1
moltiplicata per 1, più la distribuzione
carico2 moltiplicata per -2, più
la    distribuzione
carico3    moltiplicata    per    2;    ovviamente    tali
distribuzioni   devono   essere   state   definite   in   un   precedente   blocco
## [LOADS].
## -
La seconda, di nome analisi2, parte dallo stato finale di analisi1.

## [STATICS]
name=analisi1 from=0 mult=1,-1,1,-1,1,-1
load=carico1 mult=1
load=carico2 mult=-2
load=carico3 mult=2

name=analisi2 from=analisi1 mult=1,-1,1,-1
load=carico1 mult=1
load=carico2 mult=3
## End

5.2 Organizzazione generale del programma
Il  programma  sviluppato  permette  di  eseguire  analisi  statiche  non  lineari  su
pareti  schematizzate  mediante  un  assemblaggio  di  macro  elementi  costituiti  da
pannelli   rettangolari   deformabili   a   taglio   e/o   da   pannelli   poligonali   rigidi
connessi mediante interfacce. Ogni singola analisi statica può essere composta da
un  numero  arbitrario  di  cicli  di  carico  monotono  nei  quali  si  fa  variare  il
moltiplicatore della distribuzione di carichi definita dall’utente.
Il   programma   è   stato   realizzato   in   Visual   Basic
## ®
.   Tale   linguaggio   di
programmazione   è   stato   scelto   in   quanto   consente   la   costruzione   di   una
interfaccia utente grafica (GUI, Graphic User Interface) in maniera estremamente
semplice e perché è basato sulla
Programmazione Orientata agli Oggetti (OOP,
Object Oriented Programming). Inoltre il programma CDS è anch’esso realizzato
in  Visual  Basic
## ®
e  pertanto  la  scelta  di  implementare  il  macromodello  proposto
utilizzando  lo  stesso  linguaggio  consentirà  una  più  semplice  integrazione  tra  i
due programmi.
Rispetto ad altri linguaggi di programmazione orientati agli oggetti il Visual
## Basic
## ®
presenta però alcuni svantaggi. Il più significativo è una minore velocità
di calcolo del codice eseguibile. Per ovviare a tale inconveniente, le porzioni di
programma  relative  alle  operazioni  di  puro  calcolo  sono  state  implementate  nel
linguaggio C++ e rese disponibili al programma principale sotto forma di
librerie
a collegamento dinamico
(DLL, Dynamic Linked Libraries). Ciò ha permesso di
coniugare i vantaggi del Visual Basic
## ®
con una maggiore rapidità di calcolo.















## 119
Al fine di meglio illustrare il modo di operare del programma è conveniente
descrivere separatamente l’organizzazione della struttura dati del programma, le
fasi  preliminari  di  costruzione  del  modello  (
pre-processing)  e  la  vera  e  propria
fase  di  calcolo  (
processing).  Riguardo  la  rappresentazione  grafica  dei  risultati
delle  analisi  (
post-processing)  si  rimanda  al  successivo  capitolo  relativo  alle
applicazioni numeriche.
5.2.1 Struttura dati orientata agli oggetti
Come  già  detto,  Il  programma  è  stato  realizzato  secondo  la  filosofia  della
Programmazione  Orientata  agli  Oggetti  (OOP,  Object  Oriented  Programming).
Ciò  consente  di  stabilire  delle  connessioni  logiche  tra  le  strutture  dati  del
programma che riflettono le connessioni fisiche tra gli elementi del modello.
## Gli
oggetti (o classi) sono strutture dati avanzate che, oltre a contenere i dati
del modello fisico (
variabili membro o proprietà della classe) possono contenere
le funzioni che operano su tali dati (
funzioni membro o metodi della classe).
Per una trattazione approfondita dell’argomento si rimanda a manuali tecnici
di  OOP.  In  questa  sede  si  vuole  solo  dare  una  sommaria  descrizione  dei
principali oggetti definiti nel programma di calcolo.
La  classe  principale  dell’intera  struttura  dati  è  la  classe
## Modello.  Tale
classe  è  quella  in  posizione  gerarchica  più  elevata  e  da  essa  dipendono  tutte  le
classi  relative  agli  elementi  fisici  che  costituiscono  il  modello.  La  classe
Modello infatti contiene dei puntatori a liste concatenate di oggetti dei seguenti
tipi:
## -
## Classe Nodo
## -
## Classe Pannello
## -
## Classe Rigido
## -
## Classe Interfaccia
## -
## Classe Materiale
## -
## Classe Carico
## -
## Classe Statica

Ogni   oggetto   Nodo, Pannello, Rigido   e   Interfaccia   rappresenta
rispettivamente  un  nodo,  un  pannello  deformabile  a  taglio,  un  pannello  rigido  e
un’interfaccia  del  modello  fisico.  Ognuno  di  tali  oggetti  contiene  le  variabili
membro che servono a caratterizzare l’elemento stesso e le funzioni membro che
operato su di esso.
A   titolo   esemplificativo,   alcune   delle   variabili   membro   della   classe
Pannello sono:
## -
Nodi (array dei nodi che delimitano il pannello)
## -
Materiale (numero del materiale del pannello)
## -
ecc.

Alcune delle funzioni membro della classe
Pannello, sono:
## -
Disegna (consente di disegnare il pannello)
## -
CalcolaK (calcola la matrice di rigidezza del pannello)
















## 120
## -
ecc.
Un   oggetto
Materiale contiene   tutte   le   proprietà   di   uno   specifico
materiale. Gli oggetti
Panello e Rigido fanno riferimento a uno degli oggetti
Materiale definiti nel modello.
Numerose  altre  classi  fanno  parte  del  programma.  Fra  queste  ad  esempio  la
classe
Carico,  che  contiene  i  dati  e  le  funzioni  relative  a  una  distribuzione  di
forze e la classe
Statica, che contiene i dati e le funzioni relative a una analisi
statica.
## 5.2.2 Il Pre-processing
Nella  fase  di  pre-processing,  il  programma  acquisisce,  dal  file  dati,  tutte  le
informazioni  necessarie  e  le  utilizza  per  costruire  la  struttura  dati  descritta  nel
paragrafo precedente. Nel seguito si riassumano le azioni principali che occorre
definire nella fase di pre-processing:

## 1.
Memorizzazione  di  tutti  i  materiali  relativi  alla  muratura  dichiarati  nel
file dati.
## 2.
Memorizzazione  tutti  i  tipi  di  sezione  per  i  cordoli  di  piano  dichiarate
nel file dati.
## 3.
Individuazione della geometria di tutti i pannelli (deformabili a taglio e
rigidi) e dei cordoli di piano e assegnazione delle proprietà meccaniche
del materiale a essi associato.
## 4.
Individuazione  delle  interfacce  e  determinazione  delle  corrispondenti
caratteristiche  meccaniche  sulla  base  delle  caratteristiche  meccaniche
degli elementi adiacenti.
## 5.
Numerazione  dei  gradi  di  libertà  globali  della  struttura.  Questa  viene
eseguita  partendo  dal  primo  pannello  deformabile  a  taglio  e  seguendo
l’ordine  di  numerazione  locale  dei  gradi  di  libertà  del  pannello  stesso.
Successivamente vengono numerati i gradi di libertà relativi ai pannelli
rigidi e ai cordoli.
## 6.
Individuazione dei vincoli esterni e esclusione dei gradi di libertà a essi
corrispondenti.
## 7.
Costruzione  delle  matrici  di  afferenza  di  ogni  elemento.  Tali  matrici
consentono  di  determinare  il  numero  del  grado  di  libertà  globale  cui
corrisponde ogni grado di libertà locale dell’elemento.
## 8.
Definizione  delle  varie  distribuzioni  di  carico  e  costruzione  del  vettore
dei carichi esterni.
## 9.
Definizione  e  memorizzazione  di  tutte  le  informazioni  sulle  analisi
statiche che sono state specificate nel file di input.
## 10.
Definizione  dei  parametri  utili  per  il  calcolo  (per  esempio  le  varie
tolleranze, il numero massimo di iterazioni, ecc.) e delle opzioni relative
alle informazioni da restituire nel file di output.
5.2.3 La fase di elaborazione (Processing)
Nella  versione  attuale  del  software,  (ver.  1.0),  ogni  analisi  viene  eseguita
secondo  un  processo  statico-incrementale  variando  il  moltiplicatore  dei  carichi















## 121
per  passi  variabili  di  carico  in  accordo  ai  cicli  di  carico  monotono  definiti
dall’utente. Ogni fase di carico viene eseguita per incrementi di carico successivi
e  ha  termine  quando  il  moltiplicatore  dei  carichi  raggiunge  il  valore  assegnato
oppure   quando   la   struttura   diviene   labile   (matrice   di   rigidezza   prossima
dall’essere singolare) ovvero quando si genera un meccanismo di collasso.
Allo scopo di snellire le procedure si è fatta l’ipotesi che in ogni passo di carico
la  struttura  si  possa  ritenere  a  comportamento  lineare  nel  passo,  pertanto  il
sistema  risulta  lineare  a  tratti  è  l’analisi  viene  condotta  per  passi  lineari  che
possono essere comunque grandi fino al verificarsi di un dato
evento (ad esempio
plasticizzazione di un pannello o distacco di un’interfaccia). Ciò significa che il
sistema viene risolto considerando la matrice di rigidezza calcolata a inizio passo
e  imponendo  un  carico  pari  a  quello  necessario  per  completare  la  fase  lineare
corrente. Diversi controlli sono stati implementati per verificare se all’interno del
passo  di  carico  uno  degli  elementi  a  comportamento  non  lineare  ha  violato  la
condizione  di  snervamento,  la  condizione  di  rottura  o,  in  generale,  qualunque
condizione che determini una variazione della rigidezza tangente. Il verificarsi di
una di tali condizioni viene appunto denominato
evento.
Se all’interno del passo di carico non si verifica alcun evento, la fase di carico è
completata;   in   caso   contrario   viene   determinata   la   frazione   di   carico   che
determina il verificarsi dell’evento e i risultati vengono scalati di conseguenza. A
questo   punto   la   matrice   di   rigidezza   viene   ricalcolata   tenendo   conto
dell’elemento nel quale si è verificato l’evento e viene applicato il carico residuo.
Se durante tale nuovo passo si verificano altri eventi vengono trattati allo stesso
modo,  finche  non  si  giunge  all’applicazione  dell’intero  carico  e  quindi  si  passa
alla fase di carico successivo.
Nel seguito la procedura di analisi al passo sopra sintetizzata viene descritta con
maggiore dettaglio.
Si  supponga  di  essere  all’inizio  di  un  generico  passo  dell’analisi  e  di  disporre
della  matrice  di  rigidezza  tangente  della  struttura
K  calcolata  a  inizio  passo.  A
questo  punto  si  tenta  di  applicare  l’intero  carico,
## ΔF
## *
,  che  allo  stato  corrente
rimane da applicare che rappresenta una frazione del carico totale
## ΔF
## *
## =step F.

FstepKU⋅=Δ
## −1*
## (1)
Dove  si  è  indicato  con
## ΔU
## *
il  vettore  degli  incrementi  dei  spostamenti  nodali
della struttura, con
K la matrice tangente.
In generale l’applicazione dell’incremento
## ΔF
## *
fino al raggiungimento del carico
totale
F determina  la  violazione  del  comportamento  lineare  segnalata  dalle
condizioni di controllo sugli eventi.
## Noto
## ΔU
## *
, gli incrementi dei parametri lagrangiani corrispondenti ai gradi di
libertà dell’elemento
i-esimo, Δu
## (i)
, si ricavano attraverso la matrice di afferenza
## C
## (i)
e, mediante la matrice di rigidezza locale dell’elemento K
locale
, si ricavano le
corrispondenti forze
## Δf
## (i)
## :

















## 122

## )()()(
## )()(
iii
ii
uKf
UCu
locale
## Δ⋅=Δ
## Δ⋅=Δ
## (2)
Note tali grandezze, è  possibile controllare se all’interno del passo si è verificato
un evento. Questo  può consistere nel cambio di fase (ossia nella transizione da
un  tratto  lineare  della  legge  costitutiva  al  successivo)  di  una  o  più  molle  delle
interfacce  o  dei  pannelli  deformabili  a  taglio,  dalla  rottura  di  una  o  più  molle,
oppure  dal  raggiungimento  del  contorno  del  dominio  di  scorrimento  da  parte  di
una o più interfacce.
Nel  caso  alcuni  dei  controlli  precedenti  indichino  il  verificarsi  di  uno  o  più
eventi,  il  passo  di  carico  viene  ridotto  al  minore  fra  i  moltiplicatori  dei  carichi
corrispondenti  a  tali  eventi.  Tale  moltiplicatore,  che  determina  il  verificarsi  del
primo evento, viene indicato con il simbolo
λ
evento
. Gli incrementi di spostamento
e  di  forza  in  corrispondenza  del  moltiplicatore
λ
evento
possono  essere  ottenuti
moltiplicando i risultati a fine passo per la quantità

evento
step
evt
λ
## =
## (3)
che  risulterà  maggiore  di  uno  in  quanto,  se  l’evento  si  verifica  all’interno  del
passo di carico, sarà
λ
evento
## <step.
Riducendo  il  passo  di  carico  a
λ
evento
,  gli  incrementi  di  spostamento  e  di  forza,
dati dalle (2), si riducono secondo le relazioni:

## {}
## {}
evtff
evtuu
ii
ii
## ,1max/
## ,1max/
## )()(
## )()(
## Δ=Δ
## Δ=Δ

## (4)
Nel caso in cui non si sia verificato alcun evento all’interno del passo, le (4) sono
ancora valide se si considera che in tal caso sarà
λ
evento
>step e quindi evt<1.

Una  volta  determinati  gli  incrementi  di  spostamento  e  di  forza  nel  passo  di
carico, si aggiorna lo stato di tutti gli elementi:

## )()()(
## )()()(
iii
iii
fff
uuu
## Δ+=
## Δ+=

## (5)
L’algoritmo  che  consente  di  effettuare  un  ciclo  di  carico  monotono  è
contenuto nella funzione
AnalisiStatica, il cui flow chart è riportato nella
figura 4.
















## 123
5.2.3.1 Costruzione e aggiornamento della matrice di rigidezza
All’inizio di ogni ciclo di carico vengono costruite le sottomatrici di rigidezza di
tutti  gli  elementi  e  di  tutte  le  interfacce,  quindi  per  assemblaggio  si  ottiene  la
matrice di rigidezza dell’intera struttura.
Alla fine di ogni passo viene ricostruita soltanto la matrice di rigidezza degli
elementi nei quali si è verificato un evento; la matrice di rigidezza globale viene
aggiornata  (non  ricostruita  totalmente)  sottraendo  il  contributo  di  tali  elementi,
valutato a inizio passo, e aggiungendo il contributo degli stessi elementi, valutato
a fine passo. La matrice di rigidezza globale così ottenuta consente di effettuare
un’ulteriore passo di carico con la tecnica già descritta. Tale procedimento risulta
valido fintanto ché l’evento corrispondente a fine passo non è associato a rotture,
a  scorrimenti  plastici  oppure  a  condizioni  scarico  plastico.  Infatti  in  questi  casi
occorre  iterare  per  valutare  la  matrice  di  rigidezza  tangente  associata  all’inizio
del  passo  successivo  che  può  consistere  in  un  ulteriore  incremento  di  carico
esterno o una ridistribuzione di carico. Tale procedura per brevità verrà omessa.
5.2.3.2 Rottura delle molle
Durante  l’analisi  può  verificarsi  la  rottura  di  molle  appartenenti  a  pannelli
deformabili a taglio o a interfacce.
Entrambe  le  circostanze  determinano  il  verificarsi  di  un  evento  e  quindi  la
riduzione  del  passo  di  carico.  Prima  di  passare  al  passo  di  carico  successivo  è
necessario  eseguire  la
ridistribuzione dei  carichi  che  venivano  portati  dagli
elementi pervenuti a rottura sul  resto della struttura. Nelle analisi push-over, tale
operazione è stata eseguita in modo fittizio aggiungendo alla struttura un carico
uguale  e  opposto  alle  forze  precedentemente  esercitate  dall’elemento  il  cui
contributo è cessato.
La  procedura  di  ridistribuzione  è  del  tutto  analoga  a  un  normale  ciclo  di
carico.  L’unica  differenza  consiste  nel  fatto  che,  man  mano  che  si  applica  il
carico   da   ridistribuire,   possono   verificarsi   ulteriori   rotture   che   modificano
ulteriormente il carico da applicare al resto della struttura.
Nel  programma  l’algoritmo  appena  descritto  è  stato  implementato  nella
funzione
Ridistribuzione che viene schematizzata nel flow chart riportato
nella figura 5.


























## 124
## INIZIO CICLO
## DI CARICO
F=vettore dei carichi
λ=moltiplicatore limite
step=0
step=λ
calcola evt
ΔU=K^-1*(step*F)
Incrementi singoli
elementi
Δu_molle/Δf_molle
aggiorna stato elementi:
u_molle=Δu_molle/evt
f_molle=Δf_molle/evt
Costuisce K per
assemblaggio
det(K)=0
## 0
no_convergenza
aggiorna la fase delle
molle plasticizzate
aggiorna K
## Rotture ?

aggiorna carico
step=step-step/evt
calcola K di inizio
passo (passo di carico)
## Ridistribuzione
si
no
det(K)=0
## 0
no_convergenza
## FINE CICLO
## DI CARICO
no
si
no
si
no
si



Figura 4: Flow chart della funzione
AnalisiStatica.
aggiorna lo stato degli
elementi















## 125
Molle rotte
Interfacce che violano il
doinio a scorrimento
## F_tot=0
## Calcola F_tot
vettore carichi da
ridistribuire
calcola evt
ΔU=K^-1*(step*F)
Incrementi singoli
elementi
Δu_molle/Δf_molle
aggiorna lo stato degli
elementi
## Rotture ?

calcola K di inizio
passo (passo di carico)
## FINE
## RIDISTRIBUZIONE
no
si
no
si
Scarica le molle rotte
e le interfacce
che scorrono
aggiorna carico
step=step-step/evt
aggiorna K
aggiorna la fase delle
molle plasticizzate
aggiorna K
aggiorna carico
step=step-step/evt
det(K)=0
## 0
no_convergenza
si
no
## INIZIO
## RIDISTRIBUZIONE

Figura 5: Flow chart della funzione Ridistribuzione.

















## 126





6 Analisi statiche

## Premessa
In  questo  capitolo  vengono  presentati  i  risultati  di  analisi  statiche  non  lineari,
(analisi push-over) condotte su alcuni pannelli murari e pareti piane che sono già
state  oggetto  di  studi  sperimentali  e  simulazioni  numeriche  da  parte  di  altri
autori.  Ciò  ha  consentito  di  confrontare  i  risultati  con  quelli  ottenuti  da  altri
autori utilizzando altri modelli e di testare quindi l’efficienza del macromodello
proposto e delle operazioni di taratura dei legami costitutivi dei vari elementi.


6.1 Prove su pannelli
Come  primo  esempio  di  studio  si  considerano  due  pannelli  in  muratura  di
mattoni  (5.5x12x25)  sui  quali  sono  state  condotte  prove  sperimentali  di  carico
ciclico da Magenes et al [1]. Le stesse prove sono state simulate numericamente
da  Lagomarsino  [2]  utilizzando  il  modello  continuo  a  piani  di  danneggiamento
già descritto nel capitolo 4.
Il  primo  pannello  considerato  ha  dimensioni  B=100,  H=200  e  costituisce  un
esempio  di  muro  snello  mentre  il  secondo  avente  dimensioni  B=100,  H=135,
rappresenta la tipologia dei muri tozzi. In entrambi i casi lo spessore è 25 cm.
I  pannelli  sono  incastrati  alla  base  e  hanno  sezione  di  sommità  vincolata  alla
rotazione.  I  carichi  consistevano  in  un  carico  assiale  distribuito  il  cui  valore
iniziale è di 0.6 MPa, e in una forza orizzontale agente nel piano del pannello ed
applicata  in  sommità,  la  cui  intensità  viene  incrementata  ciclicamente  fino  alla
rottura del pannello (figura 1).


















## 127
q=0.6 Mpa
## F

figura 1: schema della prova

I  risultati  delle  prove  cicliche    sono  riportati  nella  figura  seguente  in  termini  di
curve   carico   –   spostamento   di   sommità.   Appare   evidente   il   differente
comportamento  isteretico,  caratterizzato  da  cicli  molto  più  ampi  nel  caso  di
pannello  tozzo  che  denotano  l’innesco  di  un  meccanismo  di  collasso  a  taglio    e
cicli di isteresi stretti per il pannello snello.



figura 2: curva di carico (KN)-spostamento di sommità (mm) ottenuta
sperimentalmente; (a) pannello tozzo, (b) pannello snello

Tab 1 – Parametri della muratura attribuiti nella modellazione agli elementi
finiti a piani di danneggiamento

## E
## M1
(MPa) E
## M2
(MPa)
ν
m

## G
## M
(MPa) Moduli elastici
## Muratura
## 1560                 2100                 0.194                  420
σ
trazione
(MPa) τ
r
(MPa)
μ
## Caratteristiche
malta
## 0.1                                0.4                                0.3
σ
bc
(MPa) τ
br
(MPa)
## Caratteristiche
mattoni
## 5 1.2
















## 128


figura 3: Modellazione agli Elementi finiti a piani di danneggiamento;
cicli isteretici; (e) pannello tozzo, (f) pannello snello.

figura 3.a : Modello agli E.F. del pannello tozzo – distribuzione delle tensioni
verticali di compressione, (c) in corrispondenza della rottura , (d) nella fase di
softening

figura  3.b  :  Modello  agli  E.F.  del  pannello  snello  –  distribuzione  delle  tensioni
verticali  di  compressione,  (c)  in  corrispondenza  della  rottura  ,  (d)  nella  fase  di
softening















## 129
Dall’osservazione  dei  risultati  ottenuti  tramite  le  analisi  numeriche  condotte  da
Gambarotta  e  Lagomarsino  [2]  sul  pannello  tozzo  è  possibile  osservare  che  in
corrispondenza  della    rottura  del  pannello  si  ha  una  concentrazione  di  danno
nella zona centrale del pannello stesso, mentre il danneggiamento nelle sezioni di
estremità  si  mantiene  contenuto.  Si  denota  quindi  un  meccanismo  di  rottura  a
taglio  per  fessurazione  diagonale.  Nella  successiva  fase  di  softening  (che  il
modello agli elementi finiti consente di cogliere) il danno già presente nella zona
centrale  si  estende  e  si  assiste  alla  formazione  di  una  ampia  zona  lungo  la
diagonale  in  cui  si  sviluppano  tensioni  di  trazione;  tale  fase  riesce  a  simulare
quindi il comportamento post-rottura del pannello in cui si ha il progredire delle
fessure diagonali già formate in precedenza. Dall’analisi della distribuzione delle
tensioni  normali  in  direzione  verticale  si  nota  che  le  tensioni  di  compressione
sono   ovunque   ampiamente   inferiori   alla   resistenza   a   compressione   della
muratura (fig 3.a).
Nel caso del pannello snello invece il danno appare maggiormente concentrato in
prossimità  delle  sezioni  di  estremità,  ed  è  quindi  riconducibile  alla  fessurazione
del  materiale.  Il  taglio  massimo  viene  raggiunto  senza  danneggiamento  della
zona  centrale  del  pannello,  confermando  quindi  che  la  rottura  avviene  secondo
un meccanismo di natura flessionale. Nella fase  che segue la rottura del pannello
si assiste alla formazione di una danneggiamento dovuto allo scorrimento lungo i
giunti  di  malta  in  corrispondenza  di  una  striscia  verticale  posta  in  prossimità
dell’asse  baricentrico  del  pannello,  che  interessa  tutta  la  lunghezza  della  parete,
tale  fenomeno  di  scorrimento,  riconducibile  con  ogni  probabilità  alla  natura
ciclica  del  carico,  è  responsabile  dell’incremento  repentino  dell’ampiezza  dei
cicli di isteresi riscontrato nella risposta numerica (fig. 3.f). Anche in questo caso
le  tensioni  di  compressione  si  mantengono  sensibilmente  inferiori  al  valore  di
resistenza  della  muratura  (in  particolare  si  nota  che  in  corrispondenza  della
rottura del pannello, la massima tensione di compressione non supera 3.6 Mpa);
pertanto   è   lecito   parlare   di   meccanismo   di   ribaltamento   piuttosto   che   di
schiacciamento (fig 3.b).
Il confronto tra i risultati ottenuti con la modellazione agli elementi finiti a piani
di  danneggiamento  e  le  reali  prove  sperimentali  risulta  soddisfacente  sia  in
termini di spostamenti che di comportamento isteretico. Il modello teorico non è
aderente al caso reale solo per quanto riguarda l’aumento dei cicli di isteresi, che
sono previsti nel caso di pannello snello di cui sì è discusso prima.

Oltre  ai  risultati  disponibili  in  letteratura,  altri  risultati  sono  stati  ottenuti
mediante  modellazioni  numeriche  agli  elementi  finiti  in  ambiente  ADINA  in
campo non lineare utilizzando il materiale ‘concrete’.
Nelle tabelle sottostanti si riportano i parametri utilizzati nella modellazione, per
il significato dei simboli si rimanda al cap. 1.

Tab 2 – Parametri modellazione ADINA
## E
elastico
(MPa)
ν
σ
cy
(MPa)
σcu
(MPa)
εcy
(MPa)
εcu
(MPa)
σt
(MPa)
σt’
(MPa)
2100      0.194        -5         -4.5       -0.02      -0.05       0.1        0.05
















## 130



figura 5: curve pushover ADINA

## (a)   (b)

figura 6: Modello ADINA del pannello tozzo; (a) tensioni principali minime,
(b) fessure.

Le distribuzioni delle tensioni verticali e del danno previste mediante il modello
ADINA  risultano  qualitativamente  concordi  con  i  risultati  ottenuti  attraverso  la
modellazione  agli  elementi  finiti  con  il  modello  a  piani  di  danneggiamento,
tuttavia il modello ADINA a parità di carico applicato prevede delle tensioni di
compressione maggiori di quelle previste dal modello a piani di danneggiamento.















## 131
Il  modello  ADINA  non  sembra  essere  in  grado  di  prevedere  in  maniera
accettabile gli spostamenti e la resistenza.
Eseguendo  le  analisi  si  è  notato  che  il  modello  ADINA  presenta  una  eccessiva
sensibilità nei confronti dei parametri di resistenza a trazione.




## (a)
## (b)

figura 7: modello ADINA del pannello snello: (a) tensioni principali minime,
(b) fessure


Modellazione tramite il macroelemento proposto
In questo paragrafo verranno presentati e commentati i risultati ottenuti mediante
il   nuovo   macroelemento.   Nella   realizzazione   del   modello   è   innanzitutto
necessario  determinare  i  parametri  meccanici  da  assegnare  alla  muratura.  Nel
caso  in  esame  non  si  dispone  dei  dati  sperimentali  relativi  alla  resistenza
convenzionale  a  taglio  (
τ
k
)  e  delle  resistenze  a  compressione  e  trazione  (σc,σ
t
## ),
sono note però i valori delle resistenze dei singoli costituenti, (tabella 1).
Per la determinazione di
τ
k
della muratura si è fatto riferimento al D.M. dell’ 87
[6], considerando la resistenza a compressione dei mattoni.
Per   quanto   riguarda   il   comportamento   flessionale,   la   tensione   limite   a
compressione  della  muratura  viene  fissata  pari  a  quella  dei  singoli  mattoni.  La
resistenza a trazione si considera pari a quella della malta.
Per quanto riguarda la coesione della malta, si è fatto riferimento al valore di
τ
mr

riportato nella tab. 1.




















## 132

Tab 3 – Parametri macroelemento
## Ex
(MPa)
## Ey
(MPa)
G (MPa)
σ
c

(MPa)
ε
cu

(MPa)
σ
t

(MPa)
ε
tu

(MPa)
## 1560         2100          420
## -5.00
## 3*
ε
cy

## 0.1
1.5* ε
ty






figura 8: Macromodello proposto; curve pushover dei due pannelli

Nella   figura   8   sono   state   riportate   le   curve   push-over   dei   due   pannelli,
osservando l’andamento di tali curve si può subito osservare di come il modello
proposto  sia  in  grado  di  simulare  sia  un  comportamento  di  tipo  flessionale
(esaltato  nella  risposta  del  pannello  snello),  sia  un  comportamento  di  tipo
tagliante (che caratterizza la risposta del pannello tozzo).
Nel caso del pannello tozzo il meccanismo di collasso si è formato a causa della
plasticizzazione delle molle diagonali, cogliendo quindi il meccanismo di rottura
a taglio per fessurazione diagonale in accordo con i risultati sperimentali e teorici
ottenuti con il modello agli elementi finiti a piani di danneggiamento.
Nel  caso  del  pannello  snello  al  momento  del  collasso  le  molle  diagonali  sono
ancora in campo elastico.
Dall’osservazione  delle  distribuzioni  di  tensioni  nelle  interfacce,  si  riscontra  un
buon accordo con i risultati ottenuti tramite il modello agli elementi finiti a piani
di danneggiamento (figure 3.a e 3.b).
τ
k

(MPa)
γ
u

c (MPa)
φ
## 0.2         0.53%         0.3            0.3















## 133


figura  9.a:  Modellazione  del  pannello  tozzo  mediante  il  macromodello
proposto.


figura  9.b:  Modellazione  del  pannello  snello  mediante  il    macromodello
proposto.
















## 134

figura 10.a: Curve pushover del pannello corto ottenute con i vari modelli.


figura 10.b: Curve pushover del pannello snello ottenute con i vari modelli.


















## 135
Dal  confronto  delle  curve  push-over  ottenute  con  i  vari  modelli  teorici  presi  in
esame  con  i  dati  sperimentali  (figure  10.a  e  10.b)  si  osserva  che  il  modello
ADINA non lineare, in entrambi i casi esaminati, risulta totalmente inaccettabile.
Il macromodello proposto, per entrambi i casi studiati, fornisce risultati concordi
ai dati sperimentali e ai risultati ottenuti con il modello agli elementi finiti a piani
di danneggiamento, sia in termini di spostamenti che di carico ultimo. Tuttavia si
riscontra  una  leggera  sottostima  della  rigidezza  iniziale,  soprattuto  nel  caso  di
pannello snello.
















































## 136
6.2 Prove su pareti piane

6.2.1 Parete a una elevazione

Il primo esempio di parete piana che si considera è un prototipo, in scala ridotta,
di  parete  in  muratura  di  mattoni  ad  un  solo  piano  che  è  stato  oggetto  di  prove
sperimentali condotte presso l’Università di Catania [3].
Tale   parete   è   fortemente   asimmetrica   a   causa   delle   dimensioni   e   della
disposizione delle due aperture, e presenta l’accoppiamento di maschi murari con
snellezza molto diversa.
In sommità è disposta una trave in cemento armato di sezione 15x25 cm, che può
considerarsi rigida rispetto alla muratura.
## F
trave in cemento
armato

figura 11: schema geometrico della parete

Nella  prova  sperimentale  la  parete  viene  sottoposta  prima  a  un  carico  verticale
q=3.55  kN/m  e  successivamente  a  un  carico  ciclico  orizzontale  F  applicato  in
corrispondenza  della  trave.  Il  carico  viene  applicato  per  passi  a  spostamento
controllato, con cicli di ampiezza crescente fino alla rottura della parete.

Tab 4 – Parametri della muratura

E (MPa)   G (MPa)
σ
c

(MPa)
σ
c
## /mattoni
(MPa)
peso sp.
(Kg/m
## 3
## )
## 1000          300          -6.00            12            1500















## 137
Il  meccanismo  di  collasso  ottenuto  interessa  soltanto  i  maschi  murari  mentre  le
fasce   non   vengono   danneggiate.   Tale   comportamento   è   da   attribuirsi   alla
presenza  della  trave.  In  particolare  si  rivela  il  ribaltamento  del  maschio  snello
d’estremità  e  la  formazione  di  fessure    a  45  gradi  che  prendono  origine  dagli
spigoli della finestra.

figura 12: Curva sperimentale; carico ciclico(kN)-spostamento di
sommità(mm)

Come nel caso precedente, sono state eseguite analisi numeriche non lineari agli
elementi finiti mediante il programma ADINA.

Tab 5 – Parametri modellazione ADINA non-lineare  (N,mm)
## E
elastico

ν
σ
cy σcu εcy εcu σt σt’
2100        0.2          -5         -4.5        -0.02        -0.05        0.15        0.05

figura 13: modellazione ADINA; curva forza -  spostamento in sommità
















## 138
In  questo  caso,  il  modello  ADINA  riesce  a  riprodurre  in  maniera  accettabile  la
curva  carico-spostamento.  Tuttavia  c’è  da  rilevare  ancora  una  volta  l’eccessiva
sensibilità  che  tale  modello  evidenzia  nei  confronti  dei  parametri  meccanici,  in
particolare nei confronti della resistenza a trazione.
Tale  circostanza  rende  i  risultati  ottenuti  poco  attendibili,  poiché  le  incertezze
insite nei parametri meccanici assumono un peso eccessivo nella determinazione
della risposta.


figura 14: modellazione ADINA: tensioni verticali


figura 15:  modellazione ADINA: zone di fessurazione





Modellazione tramite il macromodello proposto
Nella   modellazione   realizzata   con   il   nuovo   macroelemento,   non   avendo
sufficienti  informazioni  per  determinare
τ
r
,  si  è  fatto  riferimento  al  D.M.  del
1987  [4].  Dalla  resistenza  a  compressione  dei  mattoni  (12  MPa)  e  dal  tipo  di
malta M4 si ricava :
τ
r
=0.2 MPa.

















## 139
La resistenza a compressione della muratura viene fissata pari a 5 MPa. Dato che
si è in presenza di maschi snelli, il meccanismo di collasso si formerà senz’altro
in  presenza  di  tensioni  di  compressione  non  eccessive,  pertanto  l’incertezza  sul
valore  di  resistenza  a  compressione,  non  inficerà  in  alcun  modo  i  risultati
dell’analisi. La resistenza a trazione viene fissata pari a 0.15 MPa.


Tab 6 – Parametri macroelemento
## Ex
(MPa)
## Ey
(MPa)
## G
(MPa)
σ
c

(MPa)
ε
cu

(MPa)
σ
t

(MPa)
ε
tu

(MPa)
## 1000         1000          300
## -5.00
## 3*
ε
cy

## 0.15
1.5* ε
ty








figura 16: modellazione macromodello; curva carico spostamento.




τ
k

(MPa)
γ
u

c (MPa)
φ
## 0.2         0.53%         0.15           0.3
















## 140

figura 17: modellazione macromodello : distribuzione delle tensioni nelle
interfacce (N/cm
## 2
) e forze diagonali nei pannelli (N) al passo 215.


figura 18: modellazione macromodello : distribuzione delle tensioni nelle
interfacce (N/cm
## 2
) e forze diagonali nei pannelli (N) a collasso.
















## 141
Di  seguito  si  riporta  il  confronto  tra  la  curva  forza-spostamento  ottenuta  dalle
prove sperimentali e i risultati delle modellazioni mediante ADINA e mediante il
nuovo macroelemento proposto.
Come  si  può  notare,  entrambi  i  modelli  di  calcolo  approssimano  bene  la  curva
reale.  Vi  è  una  sovrastima  della  rigidezza  iniziale,  da  imputare  senz’altro  alle
incertezze  relative  ai  parametri  di  deformabilità  elastica,  attribuiti  ai  modelli
teorici. Tuttavia il comportamento inelastico è colto molto bene, sia dal punto di
vista qualitativo che quantitativo.

figura 19: Confronto curve carico – spostamento tra i modelli teorici a
macroelemento e ADINA e i dati sperimentali.





























## 142
6.2.2 Parete a due elevazioni

Il secondo caso esaminato consiste in una parete realizzata in muratura di blocchi
squadrati.  La  parete  presenta  due  aperture  porta  al  primo  piano  e  due  aperture
finestre  al  secondo  piano,  disposte  in  maniera  simmetrica.  Lo  spessore  è
uniforme e pari a 25 cm.
La  parete  in  esame  fa  parte  di  un  prototipo  di  edificio  a  due  piani  testato
sperimentalmente da Calvi e Magenes [5]. Su tale prototipo sono state condotte
prove  di  carico  ciclico  fino  a  rottura  applicando  due  forze
## F
## 1
e  F
## 2
a  livello  dei
solai, e carichi verticali costante
p
## 1
e  p
## 2
## (figura 20).

p1=14100 N /m
p2=13800 N /m
## F1
## F2
p2
p1

figura 20: Schema geometrico delle parete.


Oltre   ai   risultati   sperimentali,   per   la   parete   in   esame   sono   disponibili   in
letteratura   i   risultati   di   alcune   simulazioni   numeriche   agli   elementi   finiti
realizzate mediante un modello a piani di danneggiamento [6] e nell’ambito del
progetto  Catania  [7]  mediante  il  modello  SAM,  per  il  quale  è  stato  considerato
un carico monotono fino a rottura.

Tab    7    –    Parametri    della    muratura    presi    in    considerazione    nella
modellazione agli E.F.















## 143
## E
## M1
(MPa) E
## M2
(MPa)
ν
m

## G
## M
(MPa) Moduli elastici
## Muratura
## 1910                 1480                  0.26                  360
σ
trazione
(MPa) τ
r
(MPa)
μ
## Caratteristiche
malta
## 0.05                               0.18                               0.577
σ
bc
(MPa) τ
br
(MPa)
## Caratteristiche
mattoni
## 5.9 2




figura  21:  Risposta  ciclica:  taglio  alla  base  –  spostamento  alla  quota  del
secondo  impalcato.  (a)  risultati  sperimentali,  (b)  risultati  teorici  mediante
elementi finiti.




















## 144


figura 22: Modellazione agli elementi finiti a piani di danneggiamento;
(a) distribuzione della variabile di danneggiamento, (b) tensioni verticali.


Come  si  può  notare  dal  confronto  delle  risposte  cicliche,  il  modello  a  piani  di
danneggiamento   è   capace   di   riprodurre   con   ottima   approssimazione   il
comportamento  sperimentale  della  parete,  sia  in  termini  di  spostamento  che  in
termini  di  comportamento  isteretico.  Tale  modello  può  pertanto  considerarsi
come  un  modello  di  riferimento  per  valutare  i  risultati  ottenuti  mediante  il
macromodello proposto.
Osservando la distribuzione del danno e le tensioni verticali ottenute mediante le
analisi  numeriche  agli  elementi  finiti  (figura  22),  si  può  individuare  una  prima
fase in cui si ha una risposta globale della struttura, con un forte impegno a taglio
delle  fasce  e  del  maschio  centrale;  proprio  quest’ultimo  giunge  per  primo  a
rottura. Proseguendo nella fase di carico, si può osservare che il sovraccarico dei
due   maschi   laterali   determina   un   collasso   di   tipo   locale   che   interessa
principalmente  i  maschi  del  primo  livello.  Dalla  distribuzione  della  variabile  di
danno  si  nota,  infatti,  una  concentrazione  del  degrado  alla  base  dei  maschi
inferiori  dovuto  alla  fessurazione  che  si  estende  successivamente  alla  parte
centrale dei pannelli, soprattutto di quello centrale, a causa dello scorrimento tra i
giunti di malta. Anche le fasce inferiori risultano fortemente danneggiate.

Il modello ottenuto utilizzando il metodo SAM fornisce risultati in buon accordo
con  la  modellazione  agli  elementi  finiti,  sia  in  termini  di  curva  carico  –
spostamento sia in termini di distribuzione del danno. Il danno in tale modello è
rappresentato dalla rottura degli elementi, che può avvenire per schiacciamento,
per scorrimento o per fessurazione diagonale.

Il meccanismo di collasso previsto dal modello SAM (fig 23) prevede la rottura
per  flessione  dei  maschi  inferiori,  la  rottura  a  taglio  del  maschio  centrale  e  di
quello  compresso  e  la  rottura  a  taglio  per  scorrimento  delle  fasce  inferiori.  Tali
meccanismi  sono  coerenti  con  la  distribuzione  della  variabile  di  danno  nel
modello agli elementi finiti (figura22).

















## 145


figura 23.a: Modello SAM ; curva push-over,


Rottura per schiacciamento
Rottura per scorrimento
Rottura per fessurazione diagonale
## (b)

figura 23.b: Modello SAM ; meccanismo di collasso




Modellazione tramite il macromodello proposto
La muratura che costituisce il prototipo di edificio considerato è stata oggetto di
prove  sperimentali  su  campioni  di  muratura  e  sui  singoli  componenti;  i  risultati
di tale prove sono reperibili in letteratura [8].
















## 146
In   particolare,   su   campioni   di   muratura   sono   state   condotte   prove   di
compressione  semplice,  compressione  diagonale  e  prove  su  triplette.  Si  dispone
quindi  di  dati  attendibili  sulla  resistenza  a  taglio  per  fessurazione  diagonale  in
assenza di sforzo normale (
τ
k
), sulla base delle prove di compressione diagonale,
e sui valori di coesione e coefficiente di attrito (
c,φ) dei giunti di malta, ricavati
mediante le prove su triplette.
Le prove di compressione semplice su campioni di muratura forniscono i moduli
di  elasticità  normale,  che  risultano  in  buon  accordo  con  i  valori  utilizzati  nella
modellazione    agli    elementi    finiti    ottenuti,    mediante    la    tecnica    di
omogeneizzazione (capitolo 4), a partire dai valori relativi ai singoli componenti
riportati  nella  tabella  1.  Nella  modellazione  con  il  macroelemento  proposto
saranno utilizzati i moduli di elasticità normale riportati nella tabella 7.
La  resistenza  a  compressione  della  muratura  si  considera  pari  a  quella  dei
mattoni,  mentre  la  resistenza  a  trazione  viene  fissata  pari  alla  resistenza  a
trazione  della  malta.  Tutti  i  parametri  necessari  alla  definizione  del  modello  a
macroelementi sono riassunti nella tabella seguente.

Tab 8 – Parametri macroelemento
## Ex
(MPa)
## Ey
(MPa)
## G
(MPa)
σ
c

(MPa)
ε
cu

(MPa)
σ
t

(MPa)
ε
tu

(MPa)
## 1480         1910          360          -5.90
## 3*
ε
cy

## 0.05
1.5* ε
ty







figura 24: Modello a macroelementi: curva carico spostamento.

τ
k

(MPa)
γ
u

c (MPa)
φ
## 0.388       0.53%       0.156        0.577















## 147

figura 25: Modello a macroelementi: deformata a collasso.



## (a)



















## 148

## (b)





## (c)

figura 27: Modello a macroelementi : tensioni normali nelle interfacce e forze di
taglio lungo le diagonali dei pannelli : (a) al passo 65 – basso impegno plastico,
(b) al passo 119 – medio impegno plastico, (c) a collasso.















## 149
Così come agli altri modelli, il macromodello prevede un collasso che interessa
principalmente   i   maschi   del   piano   inferiore   secondo   un   meccanismo   di
ribaltamento.   Infatti   in   detti   maschi   le   tensioni   di   compressione   sono
sensibilmente  inferiori  ai  valori  limite  e  non  si  registra  la  rottura  a  taglio  per
fessurazione diagonale.
Si  osserva  che  la  forza  di  taglio  non  si  distribuisce  tra  i  maschi  del  piano
inferiore in maniera proporzionale alle rigidezze elastiche, ma nella distribuzione
assume una importanza rilevante anche la fessurazione che annulla la capacità di
trasferire  sforzi  tangenziali.  Si  nota  infatti  come  il  maschio  di  estremità  della
parte  tesa  risulti  praticamente  scarico,  mentre  quello  all’estremità  compressa
risulta il più sollecitato.
Al  momento  del  collasso,  la  fascia  più  sollecitata  risulta  la  numero  7  con  un
taglio  diagonale  pari  a  51103  N,  pari  a  meno  della  metà  del  taglio  ultimo
corrente,  pari  a  112002.  Pertanto,  nessuna  delle  fasce  di  piano  perviene  alla
rottura a taglio per fessurazione diagonale.
Ciò nonostante, le fasce del primo e del secondo livello, relative alla porzione di
parete  compressa,  subiscono  vistose  rotazioni,  che  quasi  causano  il  distacco
dell’ultima  mensola  muraria.  Queste  osservazioni  sono  in  parziale  disaccordo
con  i  risultati  delle  prove  sperimentali,  nelle  quali  il  secondo  livello  rimane
praticamente    indeformato.    Tuttavia    va    puntualizzato    che    nella    prova
sperimentale   l’intelaiatura   realizzata   in   corrispondenza   dei   solai   per   il
trasferimento   dei   carichi   realizzava   un’azione   di   contenimento   che   nella
modellazione numerica non è stata messa in conto.


Figura 28: Confronto fra le curve forza-spostamento della prova sperimentale
e dei diversi modelli considerati.
















## 150
Nella   figura   precedente   sono   riportate   le   curve   push-over   relative   alle
simulazione  numeriche  e  quella  ottenuta  dall’inviluppo  dei  cicli  della  prova
sperimentale. Il confronto mostra come tutti i modelli riescono a ben interpretare
il  reale  comportamento  della  parete.  In  particolare  si  osserva  che  la  curva
ottenuta   con   il   macromodello   proposto   è   quella   più   vicina   ai   risultati
sperimentali.


6.2.3 Pareti di due edifici rappresentativi del patrimonio edilizio del
comune di Catania

Nell’ambito del progetto Catania [7] sono stati studiati da diverse unità di ricerca
due  edifici  in  muratura,  considerati  rappresentativi  del  patrimonio  edilizio  della
zona. In particolare, il primo dei due edifici, situato in via Martoglio (figura 29),
è  stato  scelto  come  rappresentativo  delle  costruzioni  in  muratura  di  recente
costruzione, mentre il secondo edificio, ubicato in via Verdi, è tipico degli edifici
storici.
L’edificio di via Martoglio è stato costruito intorno al 1950, ha pareti perimetrali
in   muratura   di   pietra   lavica   e   pareti   interne   in   mattoni   di   laterizio.   Gli
orizzontamenti sono realizzati tramite solai latero-cementizi; l’edificio è pertanto
rappresentativo   di   quegli   edifici   in   muratura   con   comportamento   di   tipo
## “scatolare”.
Nell’ambito  del  progetto  Catania,  le  unità  di  ricerca  coinvolte  hanno  realizzato
analisi  numeriche  relative  alla  struttura  tridimensionale  dell’edificio  e  a  una
singola parete interna (evidenziata nella figura 29). Nel seguito i risultati ottenuti
dalle varie unità di ricerca verranno commentati e confrontati con quelli ottenuti
utilizzando il nuovo macromodello da noi proposto.

figura 29: Edificio di via Martoglio. E’ evidenziata la parete analizzata.
















## 151
Il  secondo  edificio,  situato  in  via  Verdi,  come  già  detto  è  rappresentativo  delle
costruzioni  presenti  nel  centro  storico.  Le  pareti  sono  realizzate  in  muratura
portante di pietra lavica, gli orizzontamenti sono in prevalenza costituiti da volte.
L’edificio   rappresenta   quindi   tutti   quegli   edifici   in   muratura   nei   quali   la
“scatolarità”   deve   essere   garantita   tramite   opportuni   interventi   (es.   tiranti)
necessari  anche  per  eliminare  l’azione  spingente  degli  orizzontamenti.  Tali
strutture in genere necessitano, oltre che di verifiche globali, anche di verifiche al
ribaltamento delle singole pareti. Nell’ambito del progetto Catania le varie unità
di ricerca hanno condotto analisi sull’intero edificio e su singole pareti sottoposte
a  sollecitazioni  nel  piano  e  fuori  dal  piano.  Ai  fini  della  presente  tesi  è  stata
considerata  la  parete  perimetrale  evidenziata  nella  figura  30,  sollecitata  nel
proprio piano.

figura 30: Edificio di via Verdi. E’ evidenziata la parete analizzata.


8.2.4.1 – Parete interna dell’edificio di via Martoglio

La parete presenta cinque elevazioni ed è costituita da muratura di mattoni pieni.
Per  i  primi  quattro  piani  lo  spessore  è  pari  a  30  cm,  mentre  all’ultimo  piano  lo
spessore si riduce a 16 cm.
La  disposizione  delle  aperture  è  regolare  lungo  l’altezza  e  quasi  perfettamente
simmetrica rispetto a un asse verticale. L’apertura dell’androne, di luce molto più
ampia delle altre, determina il formarsi di due maschi più snelli rispetto agli altri,
che  peraltro  si  trovano  in  una  zona  della  struttura  che  per  l’assenza  di  aperture
sovrastanti  è  più  rigida  e  quindi  destinata  ad  assorbire  sforzi  più  elevati.  Sono
presenti cordoli di piano di altezza pari a quella del solaio (24 cm) e spessore di
30 cm.

















## 152
## 174273256203330
## 160
## 440
## 370
## 130
## 2950
## 225
## 163
## 225
## 145
## 225
## 145
## 225
## 145
## 225
## 122
## 1900

figura 31: Schema geometrico della parete

I  parametri  meccanici  attribuiti  alla  muratura  dalle  diverse  unità  di  ricerca  del
progetto Catania sono riportati nella tabella seguente.

Tab 9 – Parametri della muratura

Unità di Ricerca
## E
(MPa)
## G
(MPa)
f
u

(MPa)
τ
k

(MPa)
c
(MPa)
φ
Università di Basilicata
Modello a ventaglio
multiplo
## 1600       300          6          0.16
## 0.15        0.5
Università di Genova
E.F.a piani di
danneggiamento
## 2500       500
σ
mt
=0.1      τ
mr
## =0.15
σ
bc
=3      τ
br
## =1
## 0.5
Università di Genova
“Macroelemento”
## 2500       500          -          0.15       -        0.5
Università di Pavia
“Metodo SAM”
## 1600       300          6          0.15       -        0.5


I  parametri  meccanici  che  compaiono  nella  precedente  tabella,  a  eccezione  di
quelli  relativi  al  modello  a  elementi  finiti  dell’Università  di  Genova,  sono
parametri globali della muratura. In particolare
E e G rappresentano i moduli di
elasticità normale e tangenziale,
f
u
la resistenza a compressione, τ
k
la resistenza a
taglio   per   fessurazione   diagonale   in   assenza   di   sforzo   normale,
c   e   φ
rispettivamente la coesione e il coefficiente di attrito. Soltanto i parametri relativi
al  modello  agli  elementi  finiti  a  piani  di  danneggiamento  dell’Università  di















## 153
Genova  sono  relativi  ai  singolo  elementi  costitutivi  della  muratura  (malta  e
mattoni).
Le  varie  unità  di  ricerca  hanno  condotto  le analisi considerando  prima  la  parete
senza cordoli di piano e poi inserendo tali elementi. Dato che la struttura ha solai
latero-cementizi,   al   fine   di   modellare   correttamente   i   cordoli   di   piano   è
necessario  individuare  la  porzione  di  solaio  che  collabora  con  il  cordolo.  Tale
problema ha portato i vari autori a considerare diverse ipotesi di comportamento
per i cordoli. Nel presente lavoro vengono considerati i casi:
## -
Caso A:  muratura senza cordoli di piano;
## -
Caso  B:  presenza  di  cordoli  di  piano  elastici  con  sezione  30x24  cm
## 2
e
modulo elastico longitudinale
E=20000 MPa.
Al  fine  di  realizzare  un  confronto  tra  i  risultati  ottenuti  con  il  macromodello
proposto  e  quelli  ottenuti  dalle  unità  di  ricerca  del  progetto  Catania,  sono  stati
presi in considerazione i risultati delle seguenti modellazioni:
## -
modello  a  elementi  finiti  a  piani  di  danneggiamento  e  macromodello
(U.R. di Genova);
## -
modelli   di   tipo   POR   ottenuti   considerando   l’altezza   di   setti   pari
all’altezza  delle  aperture  e,  in  alternativa,  considerando  l’altezza  dei
setti pari all’interpiano (U.R. dell’Aquila);
## -
modello SAM  (U.R. Pavia);
## -
macromodello a ventaglio multiplo (U.R. di Basilicata).
Inoltre sono stati presi in considerazione i risultati dell’unità di ricerca di Genova
che ha condotto analisi limite a rottura considerando i meccanismi elementari di
ribaltamento delle mensole murarie e la rottura dei maschi di un piano.
Dal  confronto  dei  diversi  risultati  emerge  innanzitutto  che  i  valori  di  taglio
ultimo ricavati dal calcolo a rottura costituiscono rispetto agli altri valori:
## -
l’estremo  inferiore  nel  caso  di  parete  senza  cordoli  (meccanismo  di
ribaltamento delle mensole); figura 32;
## -
l’estremo superiore nel caso di parete con cordoli di piano (meccanismo
di  rottura  dei  maschi),  con  l’unica  eccezione  del  macromodello  a
ventaglio, che fornisce un valore più elevato; figura 33.

















## 154


figura 32: Parete senza cordoli di piano: confronto tra le unità di ricerca del
progetto Catania.

figura 33: Parete con cordoli elastici: confronto tra le unità di ricerca del
progetto Catania.

















## 155
Per quanto riguarda la parete senza cordoli, vi è una buona corrispondenza tra i
valori di taglio ultimo calcolati con il modello agli EF e con il modello SAM.
Entrambi i modelli prevedono un valore di taglio in corrispondenza del quale si
ha un brusco abbattimento della resistenza, che corrisponde alla rottura repentina
di gran parte delle fasce. Tale valore risulta però sensibilmente diverso per i due
modelli. Questo risulta infatti molto maggiore nel modello agli EF.
Differente è anche il comportamento post rottura: nel modello agli elementi finiti
si  ha  un  progressivo  degrado  di  rigidezza,  mentre  in  base  al  metodo  SAM  il
modello può ancora accettare incrementi di carico.
Le  modellazioni  a  macroelemento  sovrastimano  invece  il  carico  ultimo  della
struttura;  in  particolare  il  macromodello  a  ventaglio  multiplo  sembra  fornire  i
risultati più elevati.
Il meccanismo di collasso evidenziato dalla modellazione agli elementi finiti con
legame  costitutivo  a  piani  di  danneggiamento  è  quello  di  ribaltamento  globale
dei maschi che si instaura dopo che si verifica la rottura delle fasce di piano per
taglio. Le tensioni si mantengono comunque inferiori al limite di compressione.
A risultati praticamente analoghi si giunge mediante il modello SAM, nel quale
successivamente   alla   rottura   delle   fasce   (cui   segue   il   già   citato   brusco
abbassamento  del  taglio  agente)  vengono  sollecitati  a  flessione  i  maschi  del
piano  superiore  e  del  piano  terra.  La  rottura  a  schiacciamento  di  questi  ultimi
determina  il  collasso,  mentre  quasi  tutti  i  maschi  dell’ultimo  piano  giungono
anch’essi a rottura per schiacciamento (figura 34).



## (a)


















## 156
## (b)

figura   34:   Modello   di   parete   senza   cordoli   -   meccanismo   di   collasso:
a) modellazione agli elementi finiti a piani di danneggiamento, b) modello SAM.


Passando al modello di parete con cordoli di piano, i risultati in termini di curve
push-over sono compresi in un ristretto campo di incertezza, fatta eccezione per
il  macromodello  a  ventaglio  che  fornisce  risultati  esageratamente  distaccati.  I
modelli POR (che differiscono tra loro per la lunghezza dei setti) forniscono un
valore di taglio ultimo maggiore del 20% circa rispetto a quello evidenziato dagli
altri modelli. Si riscontra inoltre che il modello SAM e il modello ottenuto con in
macroelemento  a  ventaglio  multiplo  sottostimano  sensibilmente  la  rigidezza
elastica della struttura rispetto agli altri modelli.
Per  quanto  riguarda  il  meccanismo  di  collasso,  il  modello  agli  elementi  finiti  a
piani   di   danneggiamento   prevede   la   formazione   di   un   piano   debole   in
corrispondenza del piano terra. I risultati del modello SAM, che prevede un forte
impegno a taglio delle fasce e dei maschi murari del primo e dell’ultimo piano,
risultano  sostanzialmente  in  accordo  con  tale  conclusione:  il  collasso  avviene
infatti  per  rottura  a  taglio  per  fessurazione  diagonale  di  tutti  i  maschi  del  piano
inferiore,  tuttavia  i  maschi  dell’ultimo  piano  risultano  anch’essi  quasi  tutti  rotti
per scorrimento.















## 157
## (a)
figura 35: Modello agli elementi finiti della parete senza cordoli, distribuzione a
collasso della variabile di danno per scorrimento dei giunti di malta.
## (b)

figura 36: Modello di parete senza cordoli, meccanismo di collasso previsto
dal  modello SAM

Modellazione con il macromodello proposto
Nel  presente  paragrafo  si  riportano  i  risultati  relativi  alla  parete  dell’edificio  di
via Martoglio ottenuti mediante il macromodello proposto. I parametri meccanici
utilizzati nel modello sono riassunti nella tabella 1.
La distribuzione delle forze orizzontali che simulano il sisma, coerentemente con
quanto  fatto  dalle  unità  di  ricerca  intervenute  nel  progetto  Catania,  è  stata
determinata  seguendo  le  indicazioni  del  D.M.  del  1996  [9]  ed  è  riassunta  nella
tabella 2.
















## 158
Tab 10 – Parametri macroelemento

## Ex
(MPa)
## Ey
(MPa)
## G
(MPa)
σ
c

(MPa)
ε
cu

(MPa)
σ
t

(MPa)
ε
tu

(MPa)
## 2500 2500
## 500
## --6.00
## 3*
ε
cy

## 0.1
1.5* ε
ty








Tab 11 – Distribuzione carichi verticali e orizzontali

## Livello 0   Livello 1   Livello 2   Livello 3   Livello 4   Livello 5
## Carico
verticale (KN)
## 569.75      785.60      859.60      859.60      746.05      183.50
## Quota
## (cm)
64            452            822            1192            1562            1910
## Carico
orizzontale
## (KN)
## 16.05       156.30      311.00      439.65      512.90      154.40


I carichi verticali di piano sono stati ripartiti uniformemente; le forze orizzontali
sono state distribuite uniformemente tra i maschi presenti in ogni piano.
Nel  modello  privo  di  cordoli  le  forze  orizzontali  sono  state  distribuite  in  modo
uniforme  tra  i  maschi    e  applicate  a  questi  in  corrispondenza  della  quota  del
solaio. Nel modello con cordoli le forze sono state invece applicate come carico
uniformemente distribuito, direttamente ai cordoli; in modo che questi potessero
assolvere,  così  come  avviene  nella  realtà,  la  funzione  di  ridistribuire  le  forze  in
base alle rigidezze di ogni maschio.



τ
k

(MPa)
γ
u

c (MPa)
φ
## 0.15        0.53%        0.15           0.5















## 159

figura 37: Modello a macroelementi : curva carico – spostamento nel caso di
parete senza cordoli di piano

figura 38: Modello a macroelementi : meccanismo di collasso nel caso di
parete senza cordoli di piano
















## 160

figura 39: Modello a macroelementi : curva carico – spostamento nel caso di
parete con cordoli di piano




figura 40: Modello a macroelementi : meccanismo di collasso nel caso di
parete con cordoli di piano















## 161

figura 41: Parete con cordoli : confronto tra il macromodello proposto e i
modelli agli elementi finiti e SAM.


figura 42: Parete senza cordoli : confronto tra il macroelemento proposto e i
modelli agli elementi finiti e SAM

Taglio alla base (KN)
Taglio alla base (KN)
















## 162
Nel   caso   di   assenza   di   cordoli,   il   macromodello   proposto   prevede   un
meccanismo  di  ribaltamento  delle  mensole  murarie;  a  differenza  di  quanto
ottenuto  con  gli  altri  modelli,  tale  meccanismo  è  di  tipo  locale.  La  struttura  si
divide  infatti  in  due  porzioni  con  differente  comportamento,  una  delle  quali  si
danneggia   molto   meno   rispetto   all’altra   poiché   viene   salvaguardata   dalla
presenza  del  maschio  centrale  molto  rigido.  La  restante  parte  della  struttura
giunge a collasso per ribaltamento delle mensole murarie.
Il  differente  meccanismo  di  collasso  rispetto  al  modello  agli  elementi  finiti  a
piani di danneggiamento è da imputarsi al fatto che tale modello, a differenza del
macromodello  proposto,  non  prevede  il  danneggiamento  per  fessurazione  lungo
direzioni  verticali  e  pertanto  le  fasce  di  piano  realizzano  un  accoppiamento
assiale tra le mensole, facendo sì che il meccanismo di rotazione risulti globale.
Il confronto tra le curve push-over relative al macromodello con quelle ottenute
con gli altri modelli mostra una buona corrispondenza in termini di taglio ultimo
della  struttura.  Ovviamente  con  il  macromodello  proposto  non  è  possibile
ottenere  la  caduta  di  resistenza  che  si  riscontra  negli  altri  modelli,  dato  che  si
procede a controllo di carico. La rottura delle fasce è tuttavia evidenziata da tratti
orizzontali  della  curva  di  carico  (dovuti  alle
ridistribuzioni),  presenti  prima  del
formarsi del meccanismo di collasso.
Nel caso del modello in cui sono stati inseriti i cordoli di piano, la modellazione
tramite  il  macromodello  proposto    prevede  un  meccanismo  di  collasso  parziale
che  consiste  nella  rottura  a  taglio  per  fessurazione  diagonale  di  quasi  tuti  i
maschi  del  piano  terra;  tale  risultato  è  in  sostanziale  accordo  con  i  risultati
ottenuti  con  gli  altri  modelli.  In  particolare  si  riscontra  che  solo  nel  pannello
posto in corrispondenza dell’estremità in cui sono applicate le forza (pannello 15
in  figura  40)  le  molle  diagonali  rimangono  in  campo  elastico,  tutti  gli  altri
pannelli  vedono  snervarsi  le  proprie  molle  diagonali,  inoltre  i  pannelli  20  e  22
superano   il   limite   ultimo   di   deformazione   a   taglio   quindi   si   scaricano
completamente.
































## 163
6.2.3.1 Parete perimetrale dell’edificio di via Verdi

La parete analizzata è realizzata in muratura di pietra lavica. E’ costituita da tre
elevazioni  e  presenta  una  disposizione  regolare  delle  aperture.  Lo  spessore  è  di
86 cm al primo livello e di 57 cm ai piani superiori. Non sono presenti cordoli di
piano.  La  parete  è  caratterizzata  da  una  notevole  snellezza,  sia  in  termini
complessivi che a livello dei singoli maschi murari.

## F1
## F2
## F3

figura 43: Schema geometrico della parete .

I  valori  dei  parametri  meccanici  considerati  dalle  diverse  unità  di  ricerca  del
progetto Catania sono riassunti nella tabella 1.
La  parete  modellata  con  il  modello  a  piani  di  danneggiamento  mostra  un
meccanismo  di  collasso  con  rottura  a  taglio  delle  fasce  e  successiva  rotazione
rigida delle mensole ormai disaccoppiate.
La   modellazione   mediante   il   metodo   SAM   conduce   a   risultati   differenti,
prevedendo  un  meccanismo  di  collasso  parziale  secondo  il  quale  giungono  a
rottura  per  scorrimento  tutti  i  maschi  murari  dell’ultimo  piano,  a  eccezione  del
maschio all’estremità compressa che si rompe per presso-flessione.
In  termini  di  spostamenti,  invece,  si  riscontra  una  buona  corrispondenza  tra  i
risultati ottenuti con i diversi modelli.
















## 164
Tab 12 – Parametri della muratura

Parametri utilizzati
## E
(MPa)
## G
(MPa)
f
u

(MPa)
τ
k

(MPa)
c
(MPa)
φ
Università di Basilicata
Modello a ventaglio
multiplo
## 1500       150        2.4        0.13
## 0.2          0.5
Università di Genova
E.F.a piani di
danneggiamento
## 2500       500
σ
mt
=0.1      τ
mr
## =0.2
σ
bc
=2.4      τ
br
## =0.6
## 0.5
Università di Pavia
“Metodo SAM”
## 1500       150        2.4        0.13       -       0.5

figura 44: Parete dell’edificio di via Verdi: confronto tra le unità di ricerca
del progetto Catania.















## 165

figura 45:  Modello agli elementi finiti della parete, distribuzione a collasso della
variabile di danno  per scorrimento dei giunti di malta


figura 46:  Modello SAM – meccanismo di collasso


















## 166
Modellazione con il macromodello proposto
Nel  presente  paragrafo  si  riportano  i  risultati  ottenuti  con  il  macromodello
proposto.  Le  caratteristiche  meccaniche  della  muratura  utilizzate  nel  modello
sono  riportate  nella  tabella  1,  mentre  i  carichi  orizzontali,  calcolati  secondo
quanto  prescritto  dal  D.M.  del  1996  per  una  zona  sismica  di  prima  categoria,
sono  riassunti  nella  tabella  2.  I  carichi  sono  stati  applicate  alla  struttura  come
mostrato nella figura 43


Tab 13 – Parametri macroelemento

## Ex
(MPa)
## Ey
(MPa)
## G
(MPa)
σ
c

(MPa)
ε
cu

(MPa)
σ
t

(MPa)
ε
tu

(MPa)
## 2500 2500
## 250
## 2.4
## 3*
ε
cy

## 0.1
1.5* ε
ty










## Tab 14 – Carichi

## Livello 1 Livello 2 Livello 3
Carico verticale
## (KN)
## 739.2              603.2              410.8
## Quota
## (m)
## 4.85                9.80                15.86
Carico orizzontale
## (KN)
## 157.0              258.9              285.4
τ
k

(MPa)
γ
u

c (MPa)
φ
## 0.15        0.53%        0.15           0.5















## 167

figura 47: Modello Macroelemento :Curva carico-spostamento.

Il  modello  ottenuto  utilizzando  il  macromodello  proposto  giunge  a  collasso  per
ribaltamento  dei  maschi  murari  dell’ultima  elevazione,  in  accordo  con  quanto
previsto  dal  modello  SAM.  A  tal  proposito  si  fa  notare  come  il  meccanismo  di
ribaltamento globale delle mensole murarie, previsto invece dal modello a piani
di danneggiamento, è probabilmente inibito dalla forte differenza di spessore tra
la prima elevazione e le altre due.
Analogamente  alla  modellazione  agli  elementi  finiti,  il  macromodello  proposto,
prevede un forte impegno delle fasce di piano delle prime due elevazioni, mentre
risultano scariche le fasce dell’ultimo piano.
Il confronto, in termini di curva carico-spostamento, con gli altri modelli appare
soddisfacente.
Taglio alla base (KN)
















## 168


figura 48: Meccanismo Macroelemento : meccanismo di collasso di collasso

figura 49: Confronto tra il macroelemento proposto e i modelli delle unità di
ricerca del progetto Catania


Taglio alla base (KN)















## 169
8.3 – Modellazione di muratura a blocchi

Fino ad ora sono stati riportati esempi di modellazione di strutture nelle quali la
muratura  può  essere  studiata  come  un  corpo  omogeneo.  In  tali  casi  non  viene
presa in esame la reale disposizione dei conci. Per alcune tipologie di strutture è
invece necessario modellare la muratura mediante l’accostamento degli effettivi
conci che la compongono secondo la loro reale disposizione.
Nel  modellare  strutture  di  questo  tipo  è  possibile  sfruttare  la  possibilità  offerta
dal  programma  sviluppato  di  inserire  elementi  rigidi  e  di  assemblarli  mediante
interfacce di contatto di tipo unilatero.
Come  esempio  di  applicazione  del  macromodello  proposto  a  tale  particolare
tipologia si riportano i risultati relativi alla modellazione del prospetto anteriore
del tempio greco in stile dorico
“della concordia”, situato nella valle dei templi
di Agrigento.

L’effettiva  disposizione  dei  conci  che  costituiscono  l’intera  struttura  è  riportato
nella  figura  sottostante.  Lo  schema  statico  è  quello  del  trilite  realizzato  dalle
colonne  e  dall’architrave.  Si  può  facilmente  supporre  che  la  porzione  superiore
della  facciata  si  comporti  come  un  unico  corpo  rigido;  pertanto  tale  elemento
verrà  incluso  nel  modello  solo  ai  fini  della  determinazione  del  carico  verticale
derivante dal peso e delle forze sismiche.


figura 44: Vista del tempio

















## 170
Le analisi pushover sono state condotte considerando i carichi verticali dovuti al
peso  proprio  e  forze  orizzontali  in  corrispondenza  dell’architrave.  I  risultati  di
tali   analisi   vengono   riportati   rappresentando   la   curva   dello   spostamento
dell’architrave in funzione del taglio alla base applicato.
## 110
## D=100
## 108.5
## 504
## 126.5
## 70
## 70
## 70
## 190
## 904
## 1201

figura 45: schema geometrico della facciata anteriore del tempio

La  struttura  è  stata  modellata  utilizzando  pannelli  poligonali  rigidi.  Il  legame
costitutivo  delle  interfacce  viene  assegnato  direttamente  e  non  viene  desunto
dalle  caratteristiche  assegnate  ai  blocchi  (capitolo  5).  Tale  legame  prevede
resistenza  nulla  a  trazione,  al  fine  di  simulare  la  totale  assenza  di  malta,  e
comportamento    elastico    lineare    a    compressione    che    deve    simulare    la
deformabilità  assiale  dei  blocchi.  Viene  assegnato  un  modulo  elastico  E
c
## =
2000 MPa uguale per tutte le interfacce.
Il   comportamento   a   compressione   è   stato   quindi   modellato   in   maniera
semplicistica. Tuttavia si ritiene che ciò non possa inficiare i risultati in quanto la
risposta  della  struttura,  data  l’elevata  snellezza  delle  colonne,  sarà  condiziona
principalmente dal carattere monolatero del contatto tra i blocchi.
Nelle successive figure,  sono riportate le deformate corrispondenti a tre livelli di
carico  mentre  nella  figura  46  è  riportato  l’andamento  dello  spostamento  alla
quota dell’architrave in funzione del taglio alla base.
Il  collasso  si  stabilisce  in  corrispondenza  di  un  coefficiente  di  taglio  alla  base
pari a circa 0.16g.
La   curva   di   capacità   così   ottenuta   può   essere   utilizzata   per   stimare   la
vulnerabilità  sismica  del  tempio  con  i  metodi  descritti  da  Oliveto,  Caliò  &
Marletta  [10].  Tuttavia  con  l’implementazione  in  campo  dinamicodel  macro-
modello  proposto  sarà  possibile  effettuare  analisi  non-lineari  che  consentiranno
una  valutazione  più  accurata  della  resistenza  sismica  anche  di  tali  tipologie
strutturali.















## 171

figura 46: Andamento dello spostamento alla quota dell’architrave in
funzione del taglio alla base


figura 47: deformata a collasso della struttura

















## 172


figura 48: deformata al passo 100: modesto impegno plastico




figura 49: deformata al passo 223: medio impegno plastico

















## 173


## Bibliografia

[1] A. Anthoine, G. Magonette, G. Magenes: “Shear compression testing and
Analysis of brick masonry walls”, in G. Duma (ed.), Proc. 10th European
conf.  On  Earthquake  eng.,  Vol.  3,  Balkema,  Rotterdam,  1995,  pp.  1657-
## 1662.
[2] L.  Gambarotta  e  S.  Lagomarsino  :  “Damage  models  for  the  seismic
response of brick masonry shear walls. Part II: The continuum model and
its application”. Earthquake Engineering and Structural Dynamic, 26 440-
## 462.
[3] L.  Anania,  A.  Badalà,  S.  Costa:  “Retrofitting  of  buildings  constituted  by
calcareous    block    stone:    teoretical    and    sxperimental    analysis”.
Computational  Methods  in  Engineering,  1999,  Eds:  P.  M.  Pimentra;  R.
## M. L. F. Brasil; E. S. Almeida N.
[4] Decreto Ministeriale 20 novembre 1987 (D.M. 20-11-1987) (Suppl. Ord.
alla G.U. 5-12-1987, n. 285).
[5] M.  G.  Calvi,  G.  Magenes:  “Experimental  research  on  response  of  URM
building  system”,  in  D.P.  Abrams  and  G.  M.  Calvi  (eds.).  Proc.  U.S.  –
Italy  workshop  on  guidelines  for  seismic  evaluation  and  rehabilitation  of
unreinforced  masonry  buildings,  State  University  of    New  York  at
Buffalo,NCEER-94-2001, 3-41/57, Pavia, 1994.
[6] L.  Gambarotta  e  S.  Lagomarsino  :  “Damage  models  for  the  seismic
response of brick masonry shear walls. Part II: The continuum model and
its application”. Earthquake Engineering and Structural Dynamic, 26 424-
## 462.
[7] D.  Liberatore  (A  cura  di),  Progetto  Catania:  indagine  sulla  risposta
sismica di due edifici in muratura, CNR-Gruppo Nazionale per la Difesa
dai Terremoti - Roma, 2000, 275 pp. + CD-ROM allegato.
[8] B.  Filardi,  D.  Liberatore,  A.  &  Masi:  “Valutazione  della  resistenza  a
taglio  di  una  tipologia  muraria  tramite  prove  su  pannelli,  carote  e
triplette”,  Atti  del  convegno  nazionale  “La  meccanica  delle  murature  tra
teoria e progetto”, Messina, 18-20 Settembre 1996.
[9] Decreto Ministero Dei Lavori Pubblici 16-01-1996 (G.U. 5-2-1996, n.29).
[10] G.  Oliveto,  I.  Caliò  &  M.  Marletta:  “Seismic  resistance  and
vulnerability of reinforced concrete buildings not designed for earthquake
action”  In  G.  Oliveto  (editor)  “Innovative  Approaches  to  Earthquake
Engineering”, WIT Press, ISBN: 1-85312-885-6, ISSN: 1361-617X,2002.

















## 174



Conclusioni e sviluppi futuri
La  valutazione  della  resistenza  sismica  di  edifici  in  muratura  rappresenta  un
problema   di   estrema   complessità   e   nello   stesso   tempo   di   fondamentale
importanza.   Vista   la   complessità,   tali   problematiche   sono   state   affrontate
soprattutto  negli  ambienti  di  ricerca  e  i  modelli  di  calcolo  che  sono  stati  nel
tempo  sviluppati,  di  fatto  non  sono  stati  recepiti  in  ambito  professionale.  Nella
presente  tesi,  prendendo  spunto  da  un  progetto  di  ricerca  riconosciuto  valido
dalla associazione SinTeSi (Sinergie e Tecnologie in Sicilia), che ha incentivato
la  tesi  con  una  borsa  di  studio,  si  è  cercato  di  unire  Ricerca  e  Mondo
Professionale per lo sviluppo di un prodotto sufficientemente avanzato ma nello
stesso tempo pensato per le esigenze mosse in ambito professionale.
Nel   presente   lavoro   è   stato   introdotto   un   modello   discreto
equivalente  (macro-elemento)  atto  a  descrivere  il  comportamento
non-lineare  degli  edifici  in  muratura.  L’uso  dei  macro-elementi
consente  di  cogliere  il  comportamento  non-lineare  di  un  edificio
con  un  costo  computazionale  estremamente  ridotto  rispetto  ad  una
modellazione   agli   elementi   finiti.   L’estrema   semplificazione
utilizzata  nella  definizione  del  singolo  macro-elemento  consente
anche  la  schematizzazione  di  un  pannello  murario  mediante  una
mesh  di  macro-elementi  e  si  presta  particolarmente  bene  nella
schematizzazione   di   strutture   costituite   dall’assemblaggio   di
blocchi  lapidei  con  presenza  o  assenza  di  malta.  Nella  tesi  la
validità  del  modello  proposto  è  stata  valutata  mediante  analisi
statiche  incrementali  (push-over)  condotte  su  pannelli  e  pareti
murarie  che  sono  state  oggetto  di  ricerca  teorica  e/o  sperimentale.
In  particolare  sono  stati  effettuati  alcuni  confronti  con  i  risultati
ottenuti  da  altri  autori  utilizzando  macro-modelli  già  proposti  in
letteratura  con  riferimento  ad  alcune  pareti  la  cui  risposta  è  stata
ampiamente indagata nell’ambito del progetto Catania.
Il  rapporto  diretto  con  un’azienda  di  rilevanza  nazionale,  la  STS
(Software  Tecnico  Scientifico),  è  stato  e  sarà  di  fondamentale
importanza  per  il  raggiungimento  di  un  prodotto  orientato  alle
applicazioni avanzate in ambito professionale. Il lavoro fino adesso















## 175
sviluppato costituisce un primo significativo passo in cui sono state
considerate solo applicazioni non-lineari in ambito statico. Ulteriori
sviluppi riguarderanno le applicazioni in ambito dinamico di cui la
linea teorica è stata già tracciata nella presente Tesi.










View publication stats