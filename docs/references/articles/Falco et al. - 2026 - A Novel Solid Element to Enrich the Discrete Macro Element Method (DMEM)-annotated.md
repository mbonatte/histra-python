

A  Novel  Solid  Element  to  Enrich  the  Discrete
Macro  Element  Method  (DMEM)
## Marcello  Falco
## (
## B
## )
## ,  Ivo  Caliò,  Davide  Rapicavoli,  Francesco  Cannizzaro,
and  Salvatore  Caddemi
Department  of  Civil  Engineering  and  Architecture,  University  of  Catania,  Via  Santa  Sofia  64,
## 95123  Catania,  Italy
falcoprof@gmail.com, {ivo.calio,francesco.cannizzaro,
salvatore.caddemi}@unict.it
Abstract.  In this paper a novel solid macro-element, conceived within the DMEM
is  introduced.  The  solid  macro-element  has  the  shape  of  an  irregular  hexahedron
characterized  by  a  shear  deformability,  defined  according  to  a  generalized  strain
tensor,  while  the  other  deformation  parameters  are  lumped  in  zero-thickness  non-
linear  continuous  interfaces.  For  the  mechanical  characterizations  of  the  continu-
ous  interfaces  a  fiber  calibration  strategy  is  adopted,  whose  integration  can  follow
any  Gauss  integration  quadrature.  The  Poisson  effect,  not  considered  in  the  pre-
viously  introduced  discrete  macro-elements,  can  now  be  considered  according
to  a  further  generalized  strain  field  associated  to  three  additional  degrees  free-
dom.  Some  validation  examples,  limited  to  simple  benchmark  curved-geometry
prototypes,  are  presented  and  discussed.
Keywords:  Discrete  Macro-Element  Method · Masonry · Nonlinear  analyses
## 1   Introduction
The  DMEM  has  been  initially  introduced  [
## 1
]  by  proposing  a  simplified  modelling  strat-
egy  for  the  simulation  of  the  global  nonlinear  behavior  of  unreinforced  masonry  (URM)
buildings.  The  approach  is  based  on  the  concept  of  macro-element  discretization  with
the  aim  of  capturing  the  nonlinear  behavior  of  an  entire  structure  through  an  assemblage
of  discrete  macro-elements  interacting  along  zero  thickness  nonlinear  interfaces.  This
novel  approach  has  been  adopted  and  validated  by  many  authors  [
2–4]  and  successfully
applied  also  for  mixed  reinforced  concrete-masonry  structures  and  for  confined  masonry
buildings  [
5].  The  basic  plane-element,  conceived  for  the  simulation  of  the  nonlinear
response  of  masonry  walls  in  their  own  plane,  has  been  upgraded  by  introducing  a  third
dimension  and  the  relevant  additional  degrees-of-freedom  [
## 6
],  leading  to  the  first  dis-
crete  macro-element  for  unreinforced  masonry  buildings,  including  both  the  in-plane
and  the  out-of-plane  behavior.  A  further  enrichment  of  the  proposed  three-dimensional
macro-element  towards  a  more  general  spatial-element  able  to  model  curved  geometry
has  been  also  proposed  [
7].  The  DMEM  has  been  implemented  in  the  software  codes
3DMacro  and  HiStrA  (Historical  Structures  Analysis),  which  simplifies  the  modeling
©  The  Author(s),  under  exclusive  license  to  Springer  Nature  Switzerland  AG  2026
M.  Fraldi  et  al.  (Eds.):  AIMETA  2024,  LNME,  pp.  46–53,  2026.
https://doi.org/10.1007/978-3-032-17231-0_6

A Novel Solid Element to Enrich the Discrete Macro Element Method (DMEM)47
of  structures  and  masonry  bridges  by  means  of  several  wizard  generation  tools,  suitable
to  manage  complex  curved  geometries.
The  main  advantage  of  the  proposed  DMEM  is  related  to  the  very  low  computational
cost, compared to the traditional nonlinear finite element modeling. Another benefit relies
on  the  adopted  mechanical  calibration  strategy  that,  being  based  on  straightforward  fiber
discretization,  allows  the  use  of  simple  uniaxial  constitutive  laws  and  leads  to  a  very  easy
interpretation  of  the  numerical  results.  Based  on  the  above  issues,  the  DMEM  can  be
considered  not  only  a  reliable  numerical  tool  for  academic  research  but  also  an  efficient
practice-oriented  numerical  approach.
In  this  work  a  new  solid  macro-element  endowed  with  shear  deformability  and
including  the  Poisson  effect  is  introduced.  The  main  novelties  of  this  solid  element  are
related  to  definition  of  the  element  deformability,  related  to  a  strain  tensor  applied  to  all
volume  of  the  element  and  the  introduction  of  further  degrees  of  freedom  accounting  for
the  Poisson  effect.  In  the  paper  after  a  brief  theoretical  introduction  and  some  validation
examples  are  presented  and  discussed.
2   The  Novel  Solid  Macro-Element
The  novel  solid  element  here  proposed  is  more  general  than  the  previously  introduced
macro-elements.  The  solid  element  is  characterized  by  a  generalized  shear  deforma-
tion  attributed  to  the  volume  occupied  by  the  element,  in  its  initial  configuration,
according  to  an  infinitesimal  strain  field.  Differently  from  the  previous  spatial  discrete
macro-elements,  the  zero-thickness  two-dimensional  cohesive  interfaces,  inheriting  the
mechanical  properties  of  the  material,  are  continuously  distributed.  In  the  following  a
basic  description  of  the  theoretical  formulation  of  the  proposed  solid  macro-element  is
reported.
## 2.1   The  Geometry
The  element  is  represented  by  an  irregular  hexahedron  whose  volume  is  assumed  to  be
consistent  with  the  corresponding  macro-portion  of  the  structure  in  its  initial  configu-
ration.  Following  the  same  strategy  adopted  for  the  already  proposed  macro-elements,
this  solid  macro-element  will  allow  to  describe  the  linear  and  nonlinear  behavior  of  a
structure  by  considering  a  mesh  of  solid  macro-elements.
## 2.2   The  Kinematic  Model
Due  to  the  irregular  geometry  that  the  element  can  assume,  many  different  strategies  can
be  used  to  define  a  generalized  shear  strain  to  be  associated  to  the  element  volume.  In
the  approach  here  presented  the  shear  strain  field  is  defined  with  reference  to  the  regular
counterpart  of  the  element  in  its  intrinsic  coordinate  reference  system.  The  corresponding
shear  deformation  in  the  actual  three-dimensional  space  will  be  therefore  characterized
by  a  slightly  inhomogeneity  that,  however,  do  not  significantly  influence  the  accuracy
of  the  results.  The  axial-flexural,  the  torsional  and  shear  sliding  behavior  are  instead
encompassed  in  the  interfaces.

48M. Falco et al.
2.3   The  Generalized  Shear  Deformation  and  the  Corresponding  Degrees
of  Freedom
The  shear  deformation,  in  the  intrinsic  coordinate  reference  system  with  axes
ξ,  η and  ζ,
is  defined  according  to  following  homogenous  displacement  field
## U =
## 1
## 2
γ
ξη
η +  γ
ξζ
ζ e
ξ
## +
## 1
## 2
γ
ξη
ξ +  γ
ηζ
ζ e
η
## +
## 1
## 2
γ
ξζ
ξ + γ
ηζ
ηe
ζ
## (1)
in  which
γ
ξη
,  γ
ξζ
,  γ
ηζ
correspond  to  Lagrangian  parameters  governing  the  shear  defor-
mation  of  the  solid  macro-element,  Fig.
-  The  corresponding  displacement  field  in  the
actual  geometrical  space  is  given  by
u =
## 1
## 2
γ
ξη
η +  γ
ξζ
ζ
∂ x
∂ ξ
## +
## 1
## 2
γ
ξη
ξ +  γ
ηζ
ζ
∂ x
∂ η
## +
## 1
## 2
γ
ξζ
ξ+ γ
ηζ
η
∂ x
∂ ζ
## (2)
being  x  the  position  vector  in  the  actual  space  expressed  as  a  function  of  the  intrinsic
coordinates.
Fig.  1.  Shear  deformation  degrees  of  freedom  in  the  intrinsic  coordinate  space.
2.4   The  Degrees  of  Freedom  Related  to  the  Poisson  Effect
In  the  previously  proposed  discrete  macro-elements  the  Poisson  effect  has  been  ignored.
To  overcome  this  weakness,  that  in  some  structural  problems  could  play  an  impor-
tant  role,  in  this  new  solid  macro-element  three  further  degrees  of  freedom  have  been
introduced  to  accounting  for  the  Poisson  effect  at  the  macro-scale.  In  view  of  the  macro-
element  irregularity  a  similar  approach  to  that  proposed  for  the  generalized  shear  defor-
mation  is  adopted.  Namely,  the  dilatation  effect  is  kinematically  defined  in  the  regular
intrinsic  coordinate  space  and  then  transformed  in  the  actual  irregular  geometry.
In  the  intrinsic  coordinate  space,  the  dilatations  are  related  to  the  following
expressions:
U =  ξε
ξ
e
ξ
+  ηε
η
e
η
+  ζε
ζ
e
ζ
## (3)
in  which
ε
ξ
, ε
η
## ,ε
ζ
correspond  to  the  degrees  of  freedom  that  will  be  adopted  only  for
modeling  the  Poisson  effect  since  the  membrane  behavior  of  the  element  is  associated

A Novel Solid Element to Enrich the Discrete Macro Element Method (DMEM)49
to  the  interface  deformations.  The  corresponding  displacement  field  in  the  actual  space
is  given  by:
u =  ε
ξ
ξ
∂ x
∂ ξ
+  ε
η
η
∂ x
∂ η
+ ε
ζ
ζ
∂ x
∂ ζ
## (4)
## 2.5   The  Complete  Kinematics
The  complete  kinematics  of  the  solid  macro-element  is  therefore  related  to  the  following
Lagrangian  parameters:
q
## T
## =
u
## T
## G
|  φ
## T
|  γ
## T
|  ε
## T
## (5)
where:
u
## T
## =
u
## Gx
u
## Gy
u
## Gz
φ
## T
## =
φ
x
φ
y
φ
z
γ
## T
## =
γ
ξη
γ
ξζ
γ
ηζ
ε
## T
## =
ε
ξ
ε
η
ε
ζ
## (6)
corresponding  to  rigid  motion  (
u and φ),  shear  deformability  (γ)  and  Poisson  effect  (ε).
2.6   The  Relative  Motion  of  the  Interfaces
A  peculiarity  of  the  DMEM  is  that  the  mechanical  behavior  of  the  element  is  partly
defined  in  the  element  deformability  and  in  part  lumped  in  the  zero-thickness  interfaces.
This  choice  is  particularly  effective  for  the  simulation  of  the  nonlinear  response  leading
to  a  fiber  nonlinear  model  similarly  to  what  has  been  already  proposed  for  distributed
plasticity  beam  models  [
## 8
## ,
## 9
].  Non-conforming  discretization  is  also  allowed  since  two
macro-elements  can  share  an  interface  that  only  partially  comprises  the  faces  of  the
corresponding  adjacent  elements,  Fig.
## 2a.
## 2.7   The  Interface  Relative  Displacement
A  pair  of  corresponding  points  of  an  interface  belonging  to  different  surfaces  (cor-
responding  to  the  macro-elements  i  and  j)  are  initially  identified  by  the  same  vector
coordinate  x.  The  relative  displacement  is  therefore  defined  as  the  relative  displacement
of  the  points  of  each  surface  as  represented  in  Fig.
2b,  where  the  initial  reference  and
current  configurations  are  reported.
u
## (
x
## )
=  u
j
## (
x
## )
−  u
i
## (
x
## )
## (7)

50M. Falco et al.
Fig.  2.  (a)  Interface  identification  between  adjacent  elements  and  (b)  relative  displacements  of
corresponding  pairs  of  points  of  an  interface.
It  is  worth  noticing  that  there  is  no  need  to  introduce  further  degrees  of  freedom  since
## Eq.  (
7)  can  be  expressed  as  a  function  of  the  degrees  of  freedom  of  macro-elements  i
and  j  as  follows:
u
## (
x
## )
## =  V
j
## (
x
## )
·  q
j
## −  V
i
## (
x
## )
· q
i
## (8)
where  matrices
## 12×3 V
i
## (
x
## )
and V
j
## (
x
## )
are  the  kinematic  matrices  of  the  macro-elements
i  and  j.  Their  expressions,  in  addition  to  the  infinitesimal  rigid  motion  of  the  macro-
element,  are  derived  from  relations  (
2)  and  (3).
3   Macro-Element  Versus  FEM
The  proposed  macro-element  approach  has  been  implemented  in  new  version  of  the
software  3DMacro  and  HiStrA  that  is  based  on  the  use  of  solid  elements  also  for  beams,
columns,  masonry  walls  as  well  as  beam-to-column  joints.  In  this  paper  the  capability  of
the  solid  macro-element  is  investigated  considering  typical  spatial  curved  unreinforced
masonry  structures,  such  as  vaults  and  domes.  The  applications  reported  in  the  following
aim  at  providing  a  first  validation  of  the  model  in  the  linear  and  nonlinear  field  through  a
comparison  with  numerical  and  experimental  results,  already  published  in  the  literature.
In  the  proposed  DMEM  application  a  curved  geometry  structure  is  discretized  by
means  of  an  assemblage  of  several  solid  hexahedron  elements.  In  order  to  investigate  the
accuracy  of  the  solution  the  results  are  compared  to  those  obtained  by  FEM  analyses.
The  considered  example  is  relative  to  a  brick  masonry  spherical  dome  with  a  circular
hole  in  the  key  zone  that  has  been  investigated  by  Foraboschi  [
10]  in  2006.  Besides
the  experimental  tests,  some  numerical  simulations  obtained  by  some  authors  through
different  modeling  approaches  have  been  used  for  comparison  [
11, 12].  The  geometrical
scheme  of  the  dome  presents  a  0,20  m  circular  hole  in  the  key  zone,  the  inner  radius  is
2.2  m,  while  the  thickness  is  12  cm.  The  vertical  load  is  applied  in  an  annulus  around
the  hole,  Fig.
## 4.

A Novel Solid Element to Enrich the Discrete Macro Element Method (DMEM)51
Table  1.   Geometric  and  mechanical  properties  of  the  dome
E  [MPa]
νγ [kN/m
## 3
## ]σ
t
[MPa]σ
c
[MPa]C [MPa]μ
## 850
## 0.25200.071.90.120.37
3.1   Validation  of  the  Model  in  the  Linear  Elastic  Field
The  dome  is  considered  clamped  at  its  base  and  subject  to  its  self-weight  only.  The
adopted  geometrical  and  mechanical  properties  of  the  dome  are  reported  in  Table
## 1.
The  linear  elastic  validation  has  been  performed  by  comparing  the  eigen-properties
with  those  obtained  using  the  software  SAP2000  using  8-nodes  solid  elements.  In  the
under  validation  discrete  element  approach,  the  distribution  of  mass  is  modelled  accord-
ing  to  a  kinematics  consistent  mass  matrix  while  in  the  FEM  approaches  the  mass  con-
tribution  is  lamped  in  the  element-nodes.  In  Fig.
3 the  first  six  vibration  frequencies  and
the  corresponding  modes  have  been  compared  with  those  obtained  in  the  FEM  model.
In  the  FEM  approaches  the  mass  contribution  is  concentrated  in  the  element-nodes.
## In  Fig.
3 the  first  six  vibration  frequencies  and  the  corresponding  modes  have  been
compared  to  those  obtained  in  the  FEM  model.  An  optimum  agreement  in  terms  of
frequencies and mode shapes can be observed. The introduction of the degrees of freedom
associated  to  the  Poisson  effect  slightly  influences  the  values  of  frequencies.
Fig.  3.  First  six  vibration  frequencies  and  the  corresponding  modes.  Comparison  DMEM  versus
## FEM.
3.2   Validation  of  the  Model  in  the  Nonlinear  Field
In  this  section  a  numerical  and  experimental  validation  of  the  proposed  model  in  the
nonlinear  field  is  provided.  In  Fig.
4,  the  results  of  the  nonlinear  static  analyses  have
been  compared  with  other  results  already  available  in  the  literature  [
## 13
].  In  the  picture  the
vertical  top  displacement  U  as  a  function  of  the  vertical  load  F  is  reported.  The  ultimate
vertical  load  applied  is  about  50  kN,  which  is  consistent  to  the  results  of  the  experimental
test  as  well  as  the  other  numerical  models.  The  proposed  model  very  well  predicts  the
initial  stiffness  and  the  ultimate  load  of  the  structure,  and  it  is  in  very  good  agreement
with  the  available  numerical  results  obtained  by  FEM  and  limit  analysis  approaches.

52M. Falco et al.
Fig.  4.  Experimental  validation  of  the  proposed  model  in  the  nonlinear  field
## 4   Conclusions
In  this  paper  a  novel  solid  element  within  the  context  of  the  discrete  macro-element
approach  is  introduced.  The  element  is  characterized  by  a  new  kinematics  model,  that
allows  small  shear  deformations,  within  the  element  volume,  while  the  membrane  behav-
ior  is  lumped  in  continuous  zero  thickness  interfaces.  Differently  from  the  previously
proposed  discrete  macro-element,  the  Poisson  effect  is  considered  at  the  macro-scale
according  to  a  generalized  dilatation  effect  spread  in  the  element  volume.  The  asso-
ciate  computational  cost  of  the  proposed  general  solid  element  can  be  tailored  being  the
element  characterized  by  a  number  of  degrees  of  freedom  ranging  from  6  to  12  accord-
ing  to  the  assumed  kinematics  model.  The  new  solid  macro-element  enriches  a  larger
computational  framework,  based  on  discrete  macro-element  approach  devoted  to  the
nonlinear  assessment  of  any  construction  (buildings,  bridges,  dams,  soil  etc.).  The  vali-
dation  example  reported  in  the  paper  shows  the  high  accuracy  of  the  proposed  DMEM
in  conjunction  with  the  use  of  the  novel  solid  element.
Acknowledgements.  This  research  was  partially  funded  by  the  Italian  Ministry  of  University
and  Research  (MUR)  with  the  project  PRIN2022PNRR  P20229YAYL  “Safer  Architectural  Her-
itage  Assets  through  Risk  Assessment - SAHARA  project”,  Principal  Investigator  Prof.  Ivo  Caliò
and  partially  by  the  ReLUIS-DPC  2022–2024  research  program,  funded  by  the  Presidenza  del
Consiglio  dei  Ministri-Dipartimento  della  Protezione  Civile  (DPC)  work  package  WP10.
## .
## References
- Caliò,  I.,  Marletta,  M.,  Pantò,  B.:  A  simplified  model  for  the  evaluation  of  the  seis-
mic  behaviour  of  masonry  buildings.  In:  Topping,  B.H.V.  (ed.)  Proceedings  of  the  Tenth
International  Conference  on  Civil,  Structural  and  Environmental  Engineering  Computing,
Civil-Comp  Press,  Stirlingshire,  UK,  Paper  195  (2005).
https://doi.org/10.4203/ccp.81.195
- Marques,  R.,  Lourenco,  P.B.:  Possibilities  and  comparison  of  structural  component  models
for  the  seismic  assessment  of  modern  unreinforced  masonry  buildings.  Comput.  Struct.  89,
## 2079–2091  (2011)

A Novel Solid Element to Enrich the Discrete Macro Element Method (DMEM)53
- Haji  Sadeghi,  N.,  Azizi-Bondarabadi,  H.,  Correia,  M.:  Preventive  conservation  of  vernacular
adobe  architecture  at  seismic  risk:  the  case  study  of  a  world  heritage  historical  city.  Buildings
15(1),  art.  no.  134  (2025)
- Cristian-Scupin  A.,  Vacareanu  R.:  Performance  criteria  expressed  by  means  of  relative  dis-
placements  for  a  retrofitted  masonry  school  building.  Eng.  Failure  Anal.  153,  art.  no.  107531
## (2023)
- Caliò, I., Pantò, B.: A macro-element modelling approach of infilled frame structures. Comput.
## Struct.  143,  91–107  (2014)
- Pantò,  B.,  Cannizzaro,  F.,  Caliò,  I.,  Lourenço,  P.B.:  Numerical  and  experimental  validation  of
a  3D  macro-model  for  the  in-plane  and  out-of-plane  behavior  of  unreinforced  masonry  walls.
## Int.  J.  Archit.  Herit.  11(7),  946–964  (2017)
- Calió,  I.,  Cannizzaro,  F.,  Marletta,  M.:  A  discrete  element  for  modeling  masonry  vaults.  Adv.
## Mat.  Res.  133–134,  447–452  (2010)
- Spacone,  E.,  Filippou,  F.C.,  Taucer,  F.F.:  Fibre  beam-column  model  for  non-linear  analysis
of  R/C  frames:  part  I.  formulation.  Earthq.  Eng.  Struct.  Dyn.  25,  711–725  (1996)
- Pantò,  B.,  Rapicavoli,  D.,  Caddemi,  S.,  Caliò,  I.:  A  Fibre  Smart  Displacement  Based  (FSDB)
beam  element  for  the  nonlinear  analysis  of  reinforced  concrete  members.  Int.  J.  Non-Linear
## Mech.  117  (2019)
- Foraboschi,  P.:  Masonry  structures  externally  reinforced  with  FRP  strips:  tests  at  the  collapse.
In:  Proceedings  of  I  Convegno  Nazionale  “Sperimentazioni  su  Materiali  e  Strutture”,  Venice
## (2006)
- Milani,  G.,  Tralli,  A.:  A  simple  meso-macro  model  based  on  SQP  for  the  non-linear  analysis
of  masonry  double  curvature  structures.  Int.  J.  Solids  Struct.  46,  808–834  (2012)
- Milani,  E.,  Milani,  G.,  Tralli,  A.:  Limit  analysis  of  masonry  vaults  by  means  of  curved  shell
finite  elements  and  homogenization.  Int.  J.  Solids  Struct.  45,  5258–5288  (2008)
- Caddemi,  S.,  Caliò,  I.,  Cannizzaro,  F.,  Occhipinti,  G.,  Pantò,  B.:  A  parsimonious  discrete
model  for  the  seismic  assessment  of  monumental  structures.  In:  Kruis,  J.,  Tsompanakis,
Y.,  Topping,  B.H.V.  (eds.)  Proceedings  of  the  Fifteenth  International  Conference  on  Civil,
Structural  and  Environmental  Engineering  Computing,  Civil-Comp  Press,  Stirlingshire,  UK,
## Paper  82  (2015)