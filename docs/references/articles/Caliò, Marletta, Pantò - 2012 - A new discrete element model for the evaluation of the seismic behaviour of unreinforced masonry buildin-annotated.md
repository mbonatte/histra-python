

A new discrete element model for the evaluation of the seismic behaviour
of unreinforced masonry buildings
## Ivo Caliò
## ⇑
## , Massimo Marletta, Bartolomeo Pantò
Department of Civil and Environmental Engineering, University of Catania, Italy
article  info
Article history:
## Received 27 May 2011
## Revised 20 October 2011
## Accepted 5 February 2012
Available online 31 March 2012
## Keywords:
Masonry building
Unreinforced Masonry structures
In-plane masonry response
Macro-element approach
Discrete element model
Seismic vulnerability
Nonlinear masonry analysis
abstract
The evaluation of the nonlinear seismic response of masonry buildings represents a subject of consider-
able importance whose resolution is nowadays a main research topic in earthquake engineering. Refined
nonlinear finite element models require a huge computational cost that makes these methods unsuitable
for practical application. In this paper an innovative discrete-element model, conceived for the simulation
of the in-plane behaviour of masonry buildings, is presented. The basic idea of the proposed approach is
to approximate the in-plane nonlinear response of masonry walls by an equivalent discrete element. This
element is able to reproduce the typical in-plane collapse behaviour of a masonry wall subjected to earth-
quake loading. The reliability of the proposed approach has been evaluated by means of nonlinear incre-
mental static analyses performed on masonry structures, for which theoretical and/or experimental
results are available in the literature. The proposed computational strategy provides a relatively simple
and practical tool which could be of significant value for the design and the vulnerability assessment
of unreinforced masonry structures in seismic areas.
Ó2012 Elsevier Ltd. All rights reserved.
## 1. Introduction
The assessment of the nonlinear seismic behaviour of UnRein-
forced Masonry buildings (URM) represents a subject of great
importance, however it is rather difficult to solve. In order to esti-
mate the seismic vulnerability of an existing building and to ascer-
tain if the structure requires a seismic upgrade, a structural
engineer needs simple and efficient numerical tools whose com-
plexity and computational demand must be appropriate for the
practical engineering purposes. However, the simulation of the
nonlinear dynamic behaviour of a masonry building represents a
challenging problem which rigorously requires the use of compu-
tationally expensive nonlinear finite element models and, above
all, expert judgment. For this reason, the seismic assessment and
subsequent rehabilitation of URM constitutes a contemporary is-
sue in most seismic regions in which the historical masonry build-
ings represents a significant number of the existing structures.
Even in the USA, the need of introducing practical approaches for
the evaluation of the seismic behaviour of URM has been recently
highlighted[1–3].
The different behaviour of masonry structures, compared to or-
dinary concrete and steel buildings, requiresad hocalgorithms
capable of reproducing the nonlinear behaviour of masonry media
and providing reliable numerical simulations. Refined finite ele-
ment numerical models, such as the smeared cracked and discrete
crack finite element models[4,5], able to predict the complex non-
linear dynamic mechanical behaviour and the degradation of the
masonry media, require sophisticated constitutive laws and a huge
computational cost. As a consequence these methods are nowa-
days not suitable for practical application and extremely difficult
to apply to large structures. An alternative approach to the nonlin-
ear FEM is represented by the rigid-body spring models (RBSM),
specifically formulated with the aim of approximating the macro-
scopic behaviour of masonry walls with reduced degrees of free-
dom. Some valuable application of this approach are relative to
historical masonry buildings[6,7]. However, the difficulties in
the model implementation make the RBSM rarely used in the engi-
neering practice. A comprehensive review in the current develop-
ment on numerical issues on masonry mechanics is reported in
[8]. In the latter work it is also highlighted that a complex analysis
tool does not necessarily provide better results than a simple tool.
In the last three decades, many authors have developed simpli-
fied or alternative methodologies that, with a reduced computa-
tional effort, should be able to predict the nonlinear seismic
behaviour of masonry buildings and to provide reliable numerical
results for engineering practice purposes. The most commonly
used practical approach for the analysis of URM is the so called
‘equivalent frame model’, in which the masonry building is repre-
sented by an equivalent nonlinear frame structure constituted by
0141-0296/$ - see front matterÓ2012 Elsevier Ltd. All rights reserved.
http://dx.doi.org/10.1016/j.engstruct.2012.02.039
## ⇑
Corresponding author. Address: Department of Civil and Environmental Engi-
neering, University of Catania, Viale Andrea Doria 6, 95125 Catania, Italy. Tel.: +39
(0)95 738 2255; fax: +39 (0)95 738 2249.
E-mail address:icalio@dica.unict.it(I. Caliò).
## Engineering Structures 40 (2012) 327–338
Contents lists available atSciVerse ScienceDirect
## Engineering Structures
journal homepage: www.elsevier.com/locate/engstruct

nonlinear beam elements and rigid offsets[9,10]. According to the
equivalent frame model approach, each wall of the building is sub-
divided into macro-elements representing piers, spandrels and ri-
gid zones. The nonlinear behaviour of piers and spandrels are
simulated by nonlinear frame element, while the rigid zones, in
which the damage cannot occur, are substituted by rigid offsets.
The substitution of a masonry portion with a frame element has
some restrictions due to the inaccurate simulation of the interac-
tion between macro-elements, to the difficulties that arise for com-
plex geometry and to the weak modelling of the cracked condition
of panels. For these reasons some authors proposed the use of two-
dimensional macro-elements, D’Asdia and Viskovic[11]model the
masonry by linear elastic macro-finite elements. Namely, the non-
linearity is simulated by updating the geometry of the element
excluding the volumes undergoing tensile stresses, or cracked, or
generally no more co-operating. A similar approach has been pro-
posed by Braga et al.[12]that introduced the so-called ‘multi-fan
panel element’ in which the stress field of the panel is assumed
to follow a multi-fan pattern, the material behaviour is assumed
linear elastic in compression and non reacting in tension. More re-
cently Vanin and Foraboschi[13]proposed a new approach based
on modelling masonry panels by means a strut and tie model.
Comparative evaluations of commonly used techniques for practi-
cal analysis of realistic URM structures subjected to seismic load-
ings are reported in the studies of Lourenço[8], Seible and
Kingsley[5], Magenes and La Fontana[9]and Kappos et al.[10].
An overview on recent code developments and state-of-the-art
methods of earthquake resistant design of masonry buildings is
reported in[14]where the experimental results are also used in
order to justify the analysed numerical approaches.
In this paper a new modelling approach for the simulation of the
seismic behaviour of masonry buildings, suitable for current engi-
neering practice applications, is presented. The proposed approach
is based on the concept ofmacro-element discretization[8]and has
been conceived with the aim of capturing the nonlinear behaviour
of an entire masonry wall and of the entire building, as an assem-
blage of several walls. The model is based on a plane nonlinear dis-
crete element, able to simulate the behaviour of masonry wall in its
own plane. The basic macro-element consists of an articulated
quadrilateral with rigid edges in which two diagonal springs govern
the shear behaviour. The flexural and sliding shear behaviour is
governed by discrete distributions of springs in the sides of the
quadrilateral that preside over the interaction with the adjacent
macro-elements. The calibration of the model require only a few
parameters to define the masonry material based on results from
current experimental tests. The computational cost of the proposed
numerical approach is greatly reduced, compared to a traditional
nonlinear finite element modelling. Since the equivalence between
the masonry portion and the macro-element is based on very
simple physical considerations, the interpretation of the numerical
results is simple and straightforward. This novelty approach is in-
tended as a tool, which requires low computational resources, for
investigating the nonlinear behaviour of URM buildings.
In the paper the efficiency of the computational tool is shown by
means of nonlinear static analyses, carried out on case studies of
masonry walls and structures that have been object of theoretical
and experimental researches. The influence of the discretization
of the model associated to the size of the mesh of macro-element
and the fine-tuning of the nonlinear links have been also
investigated.
- The basic discrete-element
The basic element of the proposed approach has a simple
mechanical scheme,Fig. 1. It is represented by an articulated
## (a)(b)
Fig. 1.The basic macro-element: (a) undeformed configuration; and (b) deformed configuration.
## (a)
## (b)(c)
## F
q
## F
q
## F
q
Fig. 2.Main in-plane failure mechanisms of a masonry portion: (a) flexural failure; (b) shear-diagonal failure; and (c) shear-sliding failure.
328I. Caliò et al./Engineering Structures 40 (2012) 327–338

quadrilateral constituted by four rigid edges connected by four
hinges and two diagonal nonlinear springs. Each side of the panel
can interact with other panels or elements or supports by means
of a discrete distribution of nonlinear springs, denoted asinterface.
Each interface is constituted bynnonlinear springs, orthogonal to
the panel side, and an additionallongitudinal springwhich controls
the relative motion in the direction of the panel edge. In spite of its
great simplicity, such a basic mechanical scheme is able to simu-
late the main in-plane failures of a portion of masonry wall sub-
jected  to  horizontal  and  vertical  loads.  These  well-known
collapse mechanisms, namely theflexural failure, thediagonal shear
failureandsliding shear failure, are approximately represented in
Fig. 2where the typical crack patterns together with the qualita-
tive kinematics of masonry portion are also sketched.Fig. 3shows
how the proposed macro-element allows a simple and realistic
mechanical simulation of the corresponding failure mechanisms.
Theflexural failuremode, sketched inFig. 2a, is associated to the
rocking of the masonry portion in its own plane. The loss of the
bearing capacity is related to the progressive rupture of the panel
in the tensile zone and/or to the crushing of the panel in the com-
pressive zone. The latter mechanism is reproduced by the consid-
ered macro-element as shown inFig. 3a. The axial and flexural
deformability of the masonry panel is concentrated in the orthog-
onal nonlinear links according to a simple fiber model discretiza-
tion, as is usually adopted for reinforced concrete structures.
Thediagonal-shear failuremode, drafted inFig. 2b, is associated
to the loss of the bearing capacity of the masonry panel due to
excessive shear and to the consequent formation of diagonal cracks
along the directions of the principal compression stresses. Through
the proposed discrete-element this collapse mechanism can be
governed by means of the two diagonal nonlinear springs which
have the role to simulate and predict the nonlinear shear response
of the modelled masonry portion,Fig. 3b.
Thesliding-shear failure modeis associated to the sliding of the
masonry panel in its own plane. In this case the loss of the bearing
capacity is associated to the formation of cracks parallel to the bed-
joints (Fig. 2c). This failure mode, which generally occurs for low
levels of vertical loads and low values of friction coefficients, can
be controlled by the longitudinal nonlinear springs of the inter-
faces,Fig. 3c.
In the following paragraphs, the kinematics and the mechanical
characteristics of the basic element are outlined. Consequently, a
simple procedure, based on a fiber modelling approach, for the
calibration of the mechanical parameters of the nonlinear links of
the discrete element, is presented.
2.1. The kinematics
According to the proposed discrete element approach, a ma-
sonry macro-portion is assimilated to an equivalent mechanical
scheme in which the physical role of each component is simple
and unambiguous. This feature is not common to all the simplified
models proposed in the literature and is noteworthy since it makes
the direct implementation of the model in many general-purpose
finite element platforms possible. As mentioned in the sequel,
the model can be also improved by using a refined mesh of ele-
ments in order to obtain a more detailed description of the kine-
matics of the structure and the collapse mechanism.
The degrees-of-freedom of the structural scheme are those
associated to the in-plane motion of the basic elements. Each ele-
ment exhibits three degrees-of-freedom, associated to the in-plane
rigid-body motion, plus a further degree-of-freedom needed for
the description of the shear deformability. InFig. 4the chosen
Lagrangian parameters for the panel and the corresponding
deformed configurations are reported. The deformations of the
interfaces are associated to the relative motion between corre-
sponding panels, therefore no further Lagrangian parameters must
be introduced in order to describe their kinematics. Each interface
can be identified by twonodes
,iandj. Each node actually corre-
sponds to thejointsof the model belonging to the panels which
are connected by the interface.
Since the proposed modelling approach is suitable for describ-
ing the behaviour of a plane wall loaded in its own plane, a
three-dimensional masonry building can be modelled as an assem-
blage of plane walls. Therefore, in this simplified approach the
behaviour of the wall in the out-of-plane direction is not consid-
ered. The latter limitation is common to all the proposed simplified
approaches. The inclusion of the out-of-plane behaviour of the ma-
sonry wall in the proposed model constitutes a further develop-
ment which, at present time, is a work in progress.
InFig. 5it is shown how a simple masonry wall can be modelled
by means of the proposed modelling approach. Namely,Fig. 5a
refers to a basic scheme composed by 12 panels and is character-
ised by 48 degrees of freedom, while inFig. 5b the same wall is
## (a)
## (b)(c)
## F
## FF
q
qq
Fig. 3.Simulation of the main in-plane failure mechanisms of a masonry portion by means of the macro-element: (a) flexural failure; (b) shear-diagonal failure; and (c) shear-
sliding failure.
u
## 3
u
## 1
## 2
uu
## 4
## 1
uu
## 3
u
## 2
u
## 4
## (a)(b)
Fig. 4.(a) Chosen Lagrangian parameters for the quadrilater; and (b) deformed
configurations corresponding to the activation of each degree-of-freedom.
I. Caliò et al./Engineering Structures 40 (2012) 327–338
## 329

modelled through a more refined mesh composed by 48 quadrilat-
erals which require 192 degrees of freedoms. The use of a more re-
fined mesh is not mandatory however in some cases can provide
more accurate results and a better description of the collapse
mechanism.
2.2. Calibration of the nonlinear springs
It has been shown that the kinematics of the proposed model is
able to simulate the main failure mechanisms of a masonry ele-
ment. However the effectiveness of the simulation of the nonlinear
behaviour relies on a suitable choice of the mechanical parameters
of the model inferred by an equivalence between the masonry wall
and a reference continuous model characterised by simple but reli-
able constitutive laws. This equivalence relies on a straightforward
fiber calibration procedure, and is based only on the main mechan-
ical parameters which characterise the masonry according to an
orthotropic homogeneous medium.
2.2.1. Calibration of the interface orthogonal springs
Since the masonry is considered as a homogeneous medium its
global behaviour should be ascribed to the flexural and shearing
characteristics of a finite portion of an orthotropic inelastic con-
tinua. As mentioned before, the flexural behaviour is simulated
by the interface orthogonal springs connecting the panel to adja-
cent elements. Each spring is here calibrated by adopting a specific
constitutive law for the masonry media, according to a simplified
fiber model approach. In the description of the calibration proce-
dure an elasto-plastic behaviour with limited deformability is as-
sumed. The orthotropic nature of the masonry can be simply
considered by calibrating separately the horizontal and vertical
interfaces according to the mechanical properties of the corre-
sponding directions.
The case regarding a horizontal interface connecting two gener-
ic panels,kandl, characterised by different mechanical and
geometrical properties, is represented inFig. 6. The vertical orthog-
onal springs have the role of simulating the deformability of the
two panels in the vertical direction. The stiffness calibration of
void
void
void
void
## (a)(b)
Fig. 5.Masonry wall and corresponding macro-element discretizations with different mesh resolutions.
## F
u
u
spring 1
Panel k
Panel l
Panel k
Panel l
spring 2
single spring
equivalent to springs
1 and 2 in series
## L
## 1
## L  /2
## 1
## L  /2
## 2
## L
## 2
ty1
ty1tu1
## F
cy1
cy1
u
cy1
u
u
cy2
cy2
## F
ty2
## F
cy2
ty2tu2
u
u
u
## F
u
## F
u
influence area
λ
zero
thickness
influence area
Fig. 6.Calibration of the interface springs.
330I. Caliò et al./Engineering Structures 40 (2012) 327–338

each panel is simply obtained by assigning to each link the axial
rigidity of the corresponding masonry strip. The masonry strip is
identified by the influence area of the spring and the half-dimen-
sion of the panel in the direction perpendicular to the interface.
This procedure provides couples of springs in series. Each couple
of springs is then replaced by a single resulting nonlinear elasto-
plastic spring as described in what follows.
With reference to a single panel, according to the above-de-
scribed procedure, the initial stiffnessK
p
, the compression and ten-
sile yielding strengthsF
cy
## ,F
ty
and the corresponding ultimate
displacementsu
cu
## ,u
tu
are derived by the knowledge of the
mechanical material properties of the masonry as follows:
## K
p
## ¼2
## Eks
## L
ð1Þ
## F
cy
## ¼skr
c
## ;F
ty
## ¼skr
t
ð2a;bÞ
u
cu
## ¼
## L
## 2
e
cu
## ;u
tu
## ¼
## L
## 2
e
tu
ð3a;bÞ
whereEis the Young’s modulus in the direction orthogonal to the
interface;
r
c
andr
t
are the compressive and tensile yielding stres-
ses,
e
cu
ande
tu
are the ultimate compressive and tensile strains;sis
the thickness of the represented masonry andkis the distance be-
tween two nonlinear link.
Each couple of elasto-plastic springs in series, once the mechan-
ical properties have been defined, can be replaced by a single
resulting nonlinear spring,Fig. 6, defined by appropriate stiffness,
yielding strengths and ultimate displacements. The substitution
of two nonlinear springs in series with a nonlinear single spring
leads to a reduction of the computational cost.
In the initial elastic range the resulting stiffness of the two
springs in series, of stiffnessK
p1
andK
p2
is as follows:
## K¼
## K
p1
## K
p2
## K
p1
þK
p2
;ð4Þ
while the yielding strengths of the resultant spring are given by the
minima between the yielding strengths of the two springs in series.
Considering two springs corresponding to panels of lengthL
## 1
andL
## 2
and characterised by ultimate deformatione
cu1
## <e
cu2
in compres-
sion ande
tu1
## <e
tu2
in tension, the ultimate displacements of the
combined resultant spring is simply obtained by adding the ulti-
mate displacement of the yielded spring to the displacement of
the other spring that behaves elastically. These displacements in
compression and in tension can therefore be expressed as:
## U
cu
## ¼
## L
## 1
## 2
## 
e
cu1
þ
## F
cy1
## K
c2
## U
tu
## ¼
## L
## 1
## 2
## 
e
tu1
þ
## F
ty1
## K
t2
## ;
ð5Þ
whereF
cy1
andF
ty1
are the compressive and tensile yielding forces
of the yielded spring andK
c2
andK
t2
are the corresponding stiffness-
es of the elastic spring.
The rupture behaviour of the panel is dealt with by different cri-
teria in compression and in tension. Precisely, once the compres-
sive ultimate displacement is reached, the spring is removed
from the model and the relevant reaction is applied as an external
force loading the corresponding panel. On the other hand, when
the tensile limit displacement is attained, although the reaction
is again re-applied to the panel, the link is not removed from the
model, since it will be able to bear further compressive loads once
the contact with the corresponding panel will be restored.
The post-yielding behaviour of each orthogonal spring can be
characterised according to different constitutive plastic models
according to the experimental results obtained at the macro-scale,
as shown in the numerical applications.
2.2.2. Calibration of the sliding springs of the interface
The longitudinal spring governs the sliding-shear failure by
considering the potential sliding between two adjacent elements.
The characteristics of this spring depend on the effective contact
surface between the adjacent elements. When the contact zone be-
tween the elements reduces to zero the sliding spring is no more
active. The sliding springs have been modelled by means of a ri-
gid-plastic constitutive behaviour governed by a Mohr–Coulomb
yielding surface, in particular sliding occurs when the force in
the nonlinear link reaches its limit value,F
lim
, that is given by
the expression:
## F
lim
## ¼ðcþlr
m
## ÞA
o
ð6Þ
in whichcis a cohesion parameter andlis the friction coefficient
that can be attributed to the masonry, in the considered direction,
in order to control the sliding-shear failure mechanism;
r
m
is the
current average value of the compressive stresses acting on the
interface andA
o
is the effective contact area of the two adjacent
panels.
2.2.3. Calibration of the diagonal springs of the panel
In view of typical mechanical properties of masonry material
and the geometry of structural walls, shear failure is the most com-
mon type of failure of masonry wall subjected to seismic action in
its own plane. The diagonal springs have the fundamental role to
preside over the diagonal shear failure collapse. This is associated
to the loss of the bearing capacity of masonry panel due to exces-
sive shear and the consequent formation of diagonal cracks along
the direction of the principal compressive stresses. Although the
use of two springs it is not compulsory, it allows a better interpre-
tation of the physical response providing an improved model for
the shear-diagonal failure, since a different state of damage can
be associated to each spring depending on the direction and versus
of the shear force. The shear failure of URM piers associated with
diagonal cracking is difficult to describe with a simple expression
[15]. Many different yielding criteria can be adopted[16,17]all
accounting for a shear resistance strongly dependent on vertical
compression stresses in the wall. As highlighted in reference
[14], two basically different hypotheses, which lead virtually to
the same results, have been developed in order to model the shear
failure mechanism. In the first case, which has been accepted by
Eurocode 6 (Design of masonry structures)[18]the shear strength
is defined according to a Mohr Coulomb law:
f
v
## ¼f
vo
þl
c
r
n
ð7Þ
wheref
vo
is the shear strength under zero compression strength,l
c
is a friction coefficient defining the contribution of compressive
stresses,
r
n
is the value of the compressive stress. Values off
vo
andl
c
should be determined by experimental test[16,19]. This cri-
terion is the same suggested for the description of the sliding-shear
failure, although characterised by appropriate values off
vo
andl
c
that in general do not coincide with the corresponding values that
govern the sliding-shear failure. In the proposed macro-modelling
approach the two mechanisms are controlled separately.
Alternative theories associate the diagonal shear failure to the
principle tensile stresses which develop in the wall when subjected
to vertical loads and increasing horizontal forces. The most
adopted criterion based on this assumption is the well known
Turnsek and Cacovic criterion[16]in its modified form[17]that
takes into account the influence of the geometry of the wall and
the distribution of action at maximum resistance. The latter crite-
rion can be expressed as
f
v
## ¼
f
t
b
ffiffiffiffiffiffiffiffiffiffiffiffiffiffi
r
o
f
t
þ1
r
ð8Þ
I. Caliò et al./Engineering Structures 40 (2012) 327–338
## 331

wheref
v
is the average shear stress in the wall attained at the max-
imum resistance,f
t
is the tensile strength of masonry,bis the shear
stress distribution factor (depending on the geometry of the wall
and on the value of the ratio between the verticalNand horizontal
## Hload),
r
o
is the average compression stress due to vertical loadN.
The calibration of the diagonal springs in the initial linear
elastic range is simply obtained by enforcing an elastic equivalence
between the panel and the corresponding masonry wall, consid-
ered as a pure shear deformable homogeneous plate with tangen-
tial modulusG, transversal areaA
t
and heighth,Fig. 7. In the
homogeneous media the relationship between the shear forceV,
and the top horizontal displacementdis given by
d¼
## V
## GA
t
hð9Þ
while in the macro-element the corresponding force–displacement
relationship is:
d¼
## V
## 2cos
## 2
aK
diag
ð10Þ
whereK
diag
represents the initial elastic stiffness of each diagonal
link and
a= arctan (b/h), beingbthe base length. By equating
expressions (9) and (10) the initial elastic stiffness of each diagonal
spring is derived:
## K
diag
## ¼
## GA
t
## 2hcos
## 2
a
ð11Þ
The ultimate shear loadV
u
and the corresponding displacement
u
u
of each diagonal spring are therefore derived by the knowledge
of the mechanical material properties of the masonry by means of
the adopted shear resistance criteria. Since the macro-element
must incorporate the mechanical property of the finite portion of
the masonry wall that represents, the ultimate shear displacement
of the element is directly associated to the ultimate shear general-
ised deformability of the masonry media, whose value can be eval-
uated experimentally or can be suggested by technical codes. If
experimental data are available, a better prediction of experimen-
tal results can be obtained by considering different values of ulti-
mate shear loads and displacements for piers and spandrels.
According to the proposal of Magenes and Calvi[15], the ultimate
displacement of the wall can be associated to a specific value of the
ultimate angular deformation
c
u
## =d
u
/hthat is dependent on the
particular masonry media. The post-yielding behaviour of each
diagonal spring can be characterised according to different consti-
tutive plastic models as shown in the numerical applications
reported in the following section.
It is worth to notice that in the proposed approach each macro-
element inherits the plane geometrical properties of the modelled
masonry portion, as a consequence, contrary to the simplified
models based on equivalent frame element approach, there is no
need to define an effective dimension of the structural element.
Once the constitutive laws have been defined both force and
displacement controlled load processes can be performed accord-
ing to procedures currently used in finite element analyses
[20,21]. In the applications reported in the following displacement
controlled nonlinear static analyses have been performed. Further
details on the numerical procedures are reported in the subsequent
paragraph.
- Simulation of experimental results
In this section the proposed discrete model is employed to sim-
ulate the nonlinear response of real masonry walls and structures
for which numerical and/or experimental results are available from
previous studies. In particular, the results of an extensive experi-
mental and numerical research on the behaviour of unreinforced
brick masonry buildings[22,23]have been considered. The first
applications are relative to numerical simulations of experimental
results of simple masonry panels characterised by various geomet-
rical ratios[24]. Secondly, a case study relative to a large-scale
masonry model built and tested at the University of Pavia, in the
North of Italy, is considered[23].
3.1. Case study 1: masonry panels
The first case study considers the results of cyclic shear tests on
brick masonry walls[24]that have been considered by several
authors aiming at validating different numerical approaches[25–
28]. Namely the experimental behaviour of simple piers under
fixed–fixed end conditions with the aim to reproduce flexural
and diagonal shear cracking behaviours have been analysed. The
dimensions of the squat wall, that collapsed according to a diago-
nal shear behaviour failure mechanism, are 100135 cm
## 2
## . The
dimension of the slender wall, which exhibited a collapse response
dominated by the rocking, are 100200 cm
## 2
. Both the walls are
characterised by a thickness of 25 cm and have been subjected to
an initial mean compressive stress of 0.6 MPa, associated to a
constant vertical load at the top, in addition to their own weights.
Further details on the specimens and test procedures are reported
on the referenced paper[24].
The experimental results of the considered panels are reported
inFig. 8. In particularFig. 8a reports the flexural response charac-
terised by a moderate hysteretic energy dissipation and an almost
nonlinear elastic behaviour with negligible strength degradation.
Fig. 8b reports the shear-diagonal typical force–displacement
curve dominated by shear cracking with high energy dissipation
and a significant strength and stiffness degradation.
For the simulation of the cyclic degrading hysteretic behaviour
of a masonry wall, subjected to a combination of constant vertical
load and to a sequence of lateral load reversals, the use of an idea-
lised bi- or tri-linear resistance envelope is recommended[14].
Here the cyclic shear-diagonal behaviour of the considered walls
has been modelled with the proposed approach by means of a
single macro-element. Furthermore, the shear-diagonal behaviour
has been modelled by means of the idealised bi-linear envelope
reported inFig. 9. The relevant parameters of the bilinear envelope
have been identified according to the following simple rules:
– The initial slope of the idealised envelope is evaluated according
to a secant stiffness, that can be associated to the formation of
the cracks, called effective stiffness of the wallK
e
. The latter
has been obtained by assuming the resistance at the crack limit
as a percentage (60%) of the experimental maximum resistance,
as follows:
## K
e
## ¼
## H
cr
d
cr
ð12Þ
– The maximum resistance of the idealised curve is set equal to
the maximum resistance attained during the testH
max
## ;
Fig. 7.Calibration of the diagonal springs in the linear elastic range.
332I. Caliò et al./Engineering Structures 40 (2012) 327–338

– The idealised ultimate states, determined by the maximum dis-
placement attained during the testd
max
and the corresponding
resistanceH
dmax
are set to be coincident to the experimental
ones.
The ratio between the resistanceH
dmax
at the ultimate displace-
ment and the maximum resistanceH
max
defines a strength
degradation factorC
sd
## [14].
## C
ds
## ¼
## H
dmax
## H
max
ð13Þ
The slope of the envelope curve in the post-yielding behaviour is gi-
ven by the kinematic hardening (or softening) parameter.
a¼
## H
dmax
## H
max
d
max
## d
## Hmax
ð14Þ
In order to calibrate the shear diagonal nonlinear link of the macro-
element, that governs the pure shear behaviour, it is necessary to
observe that a fixed-ended masonry wall exhibits a deformation
that is partly associated to bending and partly to shear. Denoting
the shear and the flexural stiffness asK
## V
andK
## F
, respectively, the
overall stiffness exhibited by the wall during the experiment,K,
can be considered as the result of two springs in series, from which
the shear stiffness can easily be obtained
## K
## V
## ¼
## KK
## F
## K
## F
## K
ð15Þ
where the flexural stiffnessK
## F
is provided, in simplified form, by the
following stiffness of an equivalent beam
## K
## F
## ¼12
## EI
h
## 3
ð16Þ
whereEis the Young modulus,Iis the moment of inertia of the wall
cross-section andhis the height of the wall. The unloading stiffness
has been expressed according to the following simple expression
## K
u
## ¼K
o
## K
## I
## K
o
## 
b
ð17Þ
whereK
o
is the initial stiffness,K
## I
is the value of the stiffness that is
obtained by connecting the point corresponding to the current plas-
tic deformation with the origin of the axes andbis a real number
that can assume value in the range 0–1. In the simulation the value
0.8 has been set. The re-loading stiffnessK
r
, in the cyclic behaviour,
has been set by pointing to the maximum reached plastic
deformation.
The flexural behaviour is governed by the orthogonal interface
springs. These have been calibrated according to an elastic-per-
fectly-plastic constitutive law, with different tensile and compres-
sive limits and an unloading stiffness expressed according to the
Eq.(17)withb=0.8, the ductility of the orthogonal springs has
been set equal to 5. The other parameters, assumed in the simula-
tion according to the above described criteria, are reported in
## Table 1.
The results of the numerical simulation are reported inFig. 10.
Even though the adopted constitutive models are very simple,
there is a satisfactory agreement between the experimental and
the numerical results.
3.2. Case study 2: masonry model (two-storey prototype brick
masonry building)
This case study is relative to a two-storey prototype brick
masonry building tested by Magenes and Calvi[22,23]at the
University of Pavia and considered in[29]for comparing and vali-
dating different simplified numerical approaches. The rectangular
plan of the building is 64.4 m while the total height is equal to
6.4 m. The building consists of four two-wythe solid brick walls
with a total wall thickness of 250 mm. The prototype has been
tested by means of cyclic horizontal forces acting along the longi-
tudinal direction. The building is composed by two masonry walls
with openings, in the longitudinal direction, and two masonry
walls with no openings in the transversal direction. These forces,
of equal value, have been applied directly to the two longitudinal
walls at the floor levels. As a result of the performed cyclic tests,
the cyclic force–displacement relationships for both the longitudi-
nal walls have been obtained. The spatial configuration of the aper-
tures in the walls with openings are different: the main entrance
wall of the building, denoted as ‘door wall’, possesses two windows
and two doors, while the wall opposite to this, denoted as ‘window
wall’, is characterised by six regularly located windows. The door
wall was disconnected from the adjacent transversal walls, while
the other (window wall) was connected to the adjacent walls with
an interlocking brick pattern around the corner. The floor consisted
## -80
## -60
## -40
## -20
## 0
## 20
## 40
## 60
## 80
## -1,5-1,0-0,50,00,51,01,5
force (KN)
displacement (cm)
## -100
## -80
## -60
## -40
## -20
## 0
## 20
## 40
## 60
## 80
## 100
## -1,0-0,50,00,51,0
force (KN)
displacement (cm)
## (a)
## (b)
Fig. 8.Experimental behaviour of simple piers, from Ref.[12]: (a) example of
flexural response and (b) example of behaviour with diagonal shear cracking.
Fig. 9.Idealisation of experimental resistance envelope with bi-linear relationship.
I. Caliò et al./Engineering Structures 40 (2012) 327–338
## 333

of a series of isolated steel beams designed to simulate a very
flexible diaphragm. The constant vertical forces acting on the walls
are due to the self-weight of the masonry and to the gravity and
accidental loads of the floor slabs (248.4 kN for the first storey
and 263.8 kN for the second storey). The seismic forces were sim-
ulated by the application of equal concentrated horizontal forces
directly applied at the longitudinal walls at the floor levels by
means of displacement controlled screw jacks.
The results of the numerical simulations reported in the follow-
ing aim to predict the response of the door wall. InFig. 11the geo-
metric layout of the wall and its basic representation by means of
the proposed macro-element approach is reported.
InTable 2the mechanical masonry characteristic that have
been used for the numerical simulations are summarised. The re-
sults of the numerical simulation are relative to a displacement-
controlled push-over analysis. Since the experimental test has
been performed by applying equal concentrated forces at the floor
levels, the nonlinear numerical analyses have been conducted by
imposing, at each step, different floor displacement values leading
to equal resisting forces. These latter values have been obtained by
means of a Newton–Raphson iterative procedure imposing a global
equilibrium condition.
The diagonal springs of the panels have been modelled by con-
sidering the well known Turnsek Cacovic criterion[16,17]in which
## Table 1
Case study 1. Mechanical characteristics of the masonry.
FlexuralShear-diagonal
E(MPa)
r
c
(MPa)r
t
(MPa)G(MPa)f
t
(MPa)bb
## 21006.200.15000.2751.5    0.8
## -80
## -60
## -40
## -20
## 0
## 20
## 40
## 60
## 80
## -1,5-1,0-0,50,00,51,01,5
force (KN)
displacement (cm)
## -100
## -80
## -60
## -40
## -20
## 0
## 20
## 40
## 60
## 80
## 100
## -1,0-0,50,00,51,0
force (KN)
displacement (cm)
## (a)
## (b)
Fig. 10.Numerical simulation of experimental tests on piers: (a) example flexural
response and (b) example of behaviour with diagonal shear cracking.
voidvoid
voidvoid
## (a)(b)
Fig. 11.The door wall (a) geometric layout; and (b) equivalent mechanical scheme.
## Table 2
Case study 2. Mechanical characteristics of the masonry.
FlexuralShear-diagonalSliding
## E
(MPa)
r
c
(MPa)
r
t
(MPa)
## G
(MPa)
f
t
(MPa)
bf
o
(MPa)
l
## Piers2100   6.20.055000.18    1.5  0.20.5
## Spandrels  2100   6.20.055000.225   1.5  0.20.5
## -150
## -100
## -50
## 0
## 50
## 100
## 150
## -3,0   -2,5   -2,0   -1,5   -1,0   -0,5   0,00,51,01,52,02,53,0
Base Shear (KN)
Top displacement (cm)
## -150
## -100
## -50
## 0
## 50
## 100
## 150
## -3,0   -2,5   -2,0   -1,5   -1,0   -0,5   0,00,51,01,52,02,53,0
Base Shear (KN)
Top displacement (cm)
## (a)
## (b)
Fig. 12.‘‘Door’’ prototype wall. Comparison between (a) experimental and (b)
numerical cyclic tests.
334I. Caliò et al./Engineering Structures 40 (2012) 327–338

the damage has been controlled by a strength degradation param-
eter
a=0.08. The hysteretic behaviour has been defined accord-
ing to the bi-linear idealisation described in the previous
subsection.
InFig. 12a comparison between the experimental and numer-
ical results in terms of base shear versus the absolute value of the
top displacement is reported. By observing the maximum reached
forces and displacements as well as the exhibited hysteretic behav-
iour and keeping in mind that the shear-diagonal behaviour has
been calibrated according to a simple bi-linear representation,
the agreement between the experimental and numerical results
can be considered satisfactory.Fig. 13reports a comparison be-
tween the experimental and numerical results in terms of base
shear of the wall versus the first inter-storey drift; also in this case
the numerical prediction appears to be acceptable.
InFig. 14a simplified representation of the damage scenarios
predicted by the model, corresponding to the value of drift of 3%
and to the ultimate value of 4.3%, are compared with the corre-
sponding crack patterns obtained experimentally. It is worth to no-
tice how the proposed approach is able to grasp the progressive
distribution of damage in the wall. The used representation in
the interface allows to distinguish the reactive compressive zone
from the cracked one due to tensile forces; diagonal bars inside a
panel indicate the yielding of the diagonal springs.
The further representation of the ultimate state, reported in
Fig. 15, clearly shows the composite shear-flexural failure of the
piers and the diagonal shear failures of spandrels as well as the
crack patterns due to the partialisation of the interfaces.
## -150
## -100
## -50
## 0
## 50
## 100
## 150
## -2,5-2,0-1,5-1,0-0,50,00,51,01,52,02,5
Base Shear (KN)
First interstory displacement (cm)
## -150
## -100
## -50
## 0
## 50
## 100
## 150
## -2,5-2,0-1,5-1,0-0,50,00,51,01,52,02,5
Base Shear (KN)
First interstory displacement (cm)
Fig. 13.‘‘Door’’ prototype wall. Comparison between (a) experimental and (b)
numerical cyclic tests.
Fig. 14.Simplified drafts of damage scenarios corresponding to different values of the applied drifts: (a) 0.3% and (b) 0.43% (maximum drift).
I. Caliò et al./Engineering Structures 40 (2012) 327–338
## 335

InFig. 16, the resultants of the compressive and shear forces in
the piers are reported as functions of the top displacement. It is
worth to notice how the proposed approach is able to model the
variation of the coupled normal and shear forces during the nonlin-
ear response of the structure.
3.3. Influence of the model discretization
In the considered approach the macro-element inherits the
geometry of the masonry portion that is modelled, this aspect
constitutes a great advantage that is not common to all the simpli-
fied approaches based on a macro-element discretization. Further-
more the consistent geometry of the element makes possible the
implementation of models with an irregular distribution of the
openings and allows the implementation of models characterised
by different level of discretization associated to the mesh resolu-
tion and to the fine-tuning of nonlinear links in the interfaces. In
Fig. 17the results of push-over analyses, performed on the door
wall of Pavia prototype, associated to different mesh resolutions
are  reported.  Three  different  mesh  resolutions  have  been
Fig. 15.Damage scenarios corresponding to a maximum applied drift 0.43%.
## 0
## 40
## 80
## 120
## 160
## 200
## 0,00,51,01,52,02,5
Panel Compression (KN)
Top displacement (cm)
rigth pier
## -40
## -20
## 0
## 20
## 40
## 0,00,51,01,52,02,5
Shear (KN)
Top displacement (cm)
rigth pier
## 0
## 40
## 80
## 120
## 160
## 200
## 240
## 0,00,51,01,52,02,5
Panel Compression (KN)
Top displacement (cm)
central pier
## -100
## -60
## -20
## 20
## 60
## 100
## 0,00,51,01,52,02,5
Shear (KN)
Top displacement (cm)
central pier
## 0
## 40
## 80
## 120
## 160
## 200
## 0,00,51,01,52,02,5
Panel Compression (KN)
Top displacement (cm)
left pier
## -40
## 0
## 40
## 80
## 0,00,51,01,52,02,5
Shear (KN)
Top displacement (cm)
left pier
## (a)
## (b)
Fig. 16.‘‘Door’’ prototype wall: the resultants of compressive (a) and shear forces (b) in the piers of the door wall as a function of the absolute top displacement.
336I. Caliò et al./Engineering Structures 40 (2012) 327–338

considered whose increasing computational cost is summarised in
Table 3. MeshAcorrespond to the basic mesh size in which piers
and spandrels are modelled by a single macro-element. MeshB
andCrepresent more refined mesh resolutions in which piers
and spandrels are represented by several macro-elements. It is well
known that, in the case of the finite element approach, convention-
ally conducted within the framework of the local continuum
theory[20,21], the numerical solution is sensitive to the mesh size
when strain softening models are used. For this reason with the
aim to investigate the influence of the mesh in the numerical
simulations, inFig. 17, for the Pavia prototype, two different com-
parisons have been considered according to a strain-softening and
a strain hardening shear-behaviour characterised by
a=0.08 and
a= 0.08, respectively. All the other parameters are reported inTa-
ble 2. It can be observed as, in presence of strain softening plastic-
ity (Fig. 17a), the localisation of plastic deformation causes a mesh
dependence in the softening branch of the push-over curve, while
in presence of strain-hardening behaviour (Fig. 17b) there is a good
agreement between the results obtained by different mesh
resolutions.
With reference to the meshAand an elasto-perfectly plastic
behaviour, inFig. 18the influence of the fine-tuning of the Nonlin-
ear Links in investigated. Namely, the results of push-over analyses
associated to different numbers ofNlinksfor unit length are com-
pared. The comparison shows that, in the analysed case, all the con-
sideredNlinksdistributions provide results in very good agreement.
3.4. Influence of the tensile and shear strength
In the following a sensitivity analysis on the tensile strength,
associated to the flexural and shear-diagonal behaviours, has been
performed in terms of monotonic push-over curves on the door
wall of the Pavia prototype. The discretization of the model is con-
sistent with the meshAand an elasto-perfectly plastic behaviour,
according to the parameters reported inTable 2. Namely, in
Fig. 19a the push-over curves for three different value of the tensile
strength
r
t
, that governs the flexural behaviour of the panel, are
represented. InFig. 19b the sensitivity analysis has been conducted
by varying the tensile strengthf
t
associated to the Turnsek and
Cacovic criterion. It is worth to notice, that the present modelling
approach allows to calibrate each fundamental collapse behaviour
(flexural failure, diagonal shear failure and sliding shear failure)
## 0
## 25
## 50
## 75
## 100
## 125
## 150
## 175
## 0.000.501.001.50
Base Shear (KN)
Top displacement (cm)
mesh A
mesh B
mesh C
## 0
## 25
## 50
## 75
## 100
## 125
## 150
## 175
## 0.000.501.001.50
Base Shear (KN)
displacement (cm)
mesh A
mesh B
mesh C
## (a)
## (b)
Fig. 17.‘‘Door’’ prototype wall: Push-over analyses associated to different mesh-
resolutions: (a) strain-softening behaviour; and (b) strain-hardening behaviour.
## Table 3
mesh resolutions.
Label  Number of macro-
elements
Number of degrees of
freedom
MaximumNlink
distance (cm)
## A166410
## B6425610
## C14457610
## 0
## 20
## 40
## 60
## 80
## 100
## 120
## 140
## 160
## 0.000.501.001.502.002.50
Base Shear (KN)
Top displacement (cm)
10 cm
20 cm
40 cm
Fig. 18.‘‘Door’’ prototype wall: Push-over analyses associated to differentNlinks
distributions in the interfaces.
## 0
## 25
## 50
## 75
## 100
## 125
## 150
## 175
## 0.00
## 0.501.001.502.00
Base Shear (KN)
Top displacement (cm)
## 0
## 25
## 50
## 75
## 100
## 125
## 150
## 175
## 0.000.501.001.502.00
Base Shear (KN)
Top displacement (cm)
f
t
= 0 .12   MPa
f
t
= 0 .075 MPa
f
t
= 0 .05   MPa
t
= 0 .05 MPa
σ
t
= 0 .10 MPa
σ
t
= 0 .20 MPa
σ
## (a)
## (b)
Fig. 19.‘‘Door’’ prototype wall: Push-over analyses associated to different values of
tensile strength associated to the flexural (a) and to the shear-diagonal (b)
behaviours.
I. Caliò et al./Engineering Structures 40 (2012) 327–338
## 337

according to ad hoc adopted collapse criteria, this constitutes a
novelty with respect to the other approaches presented in the
literature. The parameters associated to each failure mechanism
are based on results from current experimental tests.
## 4. Conclusions
The problem of the evaluation of the seismic vulnerability of
unreinforced masonry buildings represents a subject of high practi-
cal relevance but, at the same time, a very difficult task. For the
assessment of URM building seismic vulnerability and its possible
seismicretrofitting,thestructuralanalystneedssimpleandefficient
numerical tools whose complexity and computational demand
must be appropriate. In the present work an advanced model, based
on the definition of a plane macro-element, for the simulation of the
seismic behaviour and the evaluation of the seismic vulnerability of
unreinforced masonry buildings has been introduced. The proposed
model has been conceived to provide a simulation method capable
of predicting the seismic behaviour of a masonry structure at a
low computational cost, compared to a nonlinear finite element
simulation. A considerable reduction of the computational cost is
achieved since the nonlinear behaviour of a masonry portion is de-
scribed by very few degrees of freedom and by means of uniaxial
nonlinear springs. A suitable definition of the parameters of the
model that leads to a reasonable equivalence between the masonry
wall and its simplified nonlinear mechanical representation has
been proposed. This method possesses many advantages with re-
spect to other existing simplified approaches. The ability of the
macro-element to model a portion a masonry which inherits the
same plane configuration, and without distinguishing between
piers, spandrels and immune zones, makes the modelling of the glo-
bal in-plane response of masonry façades with irregular opening
pattern possible. The presence of the interfaces between macro-
elementsallowsalsothemodellingoftheinteractionwithnonlinear
frame elements. As a result infilled frame structures could also be
modelled. Furthermore the introduction of ad hoc interface ele-
ments could lead to a simple evaluation of the global behaviour of
three dimensional masonry building in presence of concrete ring
beams at the floor levels. This latter aspects constitute a research
in progress that will be the subject of a paper to come.
Although simple to comprehend, the proposed approach for
wide spread practical application requires the implementation of
ad hoc user interfaces able to simplify the application by third
party or practicing engineers. The effectiveness of the proposed
modelling has been evaluated by means of nonlinear incremental
static analyses performed on masonry walls and structures which
have been the object of theoretical and experimental research in
the past. The numerical results describe fairly well the experimen-
tal results, in terms of the cyclic response, stiffness, strength and
dissipative behaviour, as well as damage distribution.
## Acknowledgement
This research has been supported by the Italian Network of
Seismic Engineering University Laboratories (ReLUIS).
## References
[1] Associated Press. Quake panel urges law on retrofitting buildings. AP breaking
news, May 8 2004.
[2] Chen SY, Moon FL, Yi T. A macroelement for the nonlinear analysis of in-plane
unreinforced masonry piers. Eng Struct 2008;30:2242–52.
[3] Moon FL, Yi T, Leon RT, Kahn LF. Recommendations for the seismic evaluation
and  retrofit  of  low-rise  URM  structures.  ASCE  J  Struct  Eng
## 2006;132(5):663–72.
[4] Penelis Gr G. An efficient approach for pushover analysis of unreinforced
masonry (URM) structures. J Earthq Eng 2006;10(3):359–79.
[5] Seible F, Kingsley GR. Modeling of concrete and masonry structures subjected
to seismic loading. Experimen Numer Meth Earthq Eng; 1991.
[6] Casolo S, Peña F. Rigid element model for in-plane dynamics of masonry walls
considering hysteretic behaviour and damage. Earthq Eng Struct Dynam
## 2007;36(8):1029–48.
[7] Casolo S, Sanjust CA. Seismic analysis and strengthening design of a masonry
monument by a rigid body spring model: The ‘‘Maniace Castle’’ of Syracuse.
## Eng Struct 2009;31(7):1447–59.
[8] Lourenço PB. Computations on historic masonry structures. Progr Struct Eng
## Mater 2002;4(3):301–19.
[9] Magenes G, La Fontana A. Simplified nonlinear seismic analysis of masonry
buildings. In: Proceedings of British masonry society, vol. 8; 1998. p. 190–5.
[10] Kappos AJ, Penelis GG, Drakopoulos CG. Evaluation of simplified models for
lateral load analysis of unreinforced masonry buildings. J Struct Eng
## 2002;128(7):890–7.
[11] D’Asdia P, Viskovic A. Analyses of a masonry wall subjected to horizontal
actions on its plane, employing a non-linear procedure using changing shape
finite elements. Trans Modell Simul 1995;10:519–26 [WIT Press].
[12] Braga F, Liberatore D, Spera G. A computer program for the seismic analysis of
complex masonry buildings. In: Pande GN, Middleton J, Kralj B, editors.
Computer methods in structural masonry, vol. 4. London: E & FN Spon; 1998.
p. 309–16.
[13] Vanin A, Foraboschi P. Modelling of masonry panels by truss analogy – part 1.
## Masonry Int 2009;22(1):1–10.
[14] Tomazevic M. Earthquake-resistant design of masonry building. In: Elnashai
AS, Dowling PJ, editors. Series on innovation in structures and construction,
vol. 1. London: Imperial College Press; 2006.
[15] Magenes G, Calvi GM. In plane seismic response of brick masonry walls. Earthq
## Eng Struct Dynam 1997;26:1091–112.
[16] Turnsek V, Cacovic F. Some experimental result on the strength of brick
masonry walls. In: Proceedings of 2nd international brick masonry conference.
Stoke-on-Trent; 1971. p. 149–56.
[17] Turnsek V, Sheppard P. The shear and flexural resistance of masonry walls. In:
Proceedings of international research conference on earthquake engineering.
IZIIS, Skopje; 1981. p. 517–73.
[18] Eurocode 6: Design of masonry structures, part 1-1: general rules for
buildings. Rules for reinforced and unreinforced masonry. ENV 1996-1-1:
- CEN, Brussels, 1995.
[19] Corradi M, Borri A, Vignoli A. Experimental study on the determination of
strength of masonry walls. Construct Build Mater 2003;17:325–37.
[20] Jirasek M, Bazant Z. Inelastic analysis of structures. Wiley; 2001.
[21] Zienkiewicz OC, Taylor RL. The finite element method. Solid mechanics, fifth
ed., vol. 2. Butterworth Heinemann; 2000.
[22] Calvi GM, Magenes G. Experimental research on response of URM building
systems. In: Proceedings of the US–Italy workshop on guidelines for seismic
evaluation and rehabilitation of unreinforced masonry buildings. Pavia,
Technical  Report  NCEER-94-0021.  National  Centre  for  Earthquake
## Engineering, Buffalo, 20 July 1994.
[23] Magenes G, Calvi GM, Kingsley GR. Seismic testing of a full-scale, two-story
masonry building: test procedure and measured experimental response. In:
Experimental and numerical investigation on a brick masonry building
prototype – numerical prediction of the experiment, Report 3.0 – G.N.D.T.
## Pavia, January 1995.
[24] Anthoine A, Magonette G, Magenes G. Shear compression testing and analysis
of brick masonry walls. In: Proceedings of 10th European conference on
earthquake engineering, vol. 3. Vienna, A. A. Balkema: Rotterdam, 1995. p.
## 1657–62.
[25] Gambarotta L, Lagomarsino S. Damage models for the seismic response of
brick masonry shear walls. Part II: the continuum model and its application.
## Earthq Eng Struct Dynam 1997;26:440–62.
[26] Calvi MG, Kingsley GR, Magenes G. Testing of masonry structures for seismic
assessment. Earthq Spectra 1996;12(1):145–62.
[27] Calderini C, Lagomarsino S. Continuum model for in-plane anisotropic inelastic
behaviour of masonry. J Struct Eng 2008;134(2).
[28] Brenchich G, Gambarotta L, Lagomarsino S. A macroelement approach to the
three-dimensional seismic analysis of masonry buildings. In: Proceedings of
11th European conference on earthquake engineering. Paris, A. A. Balkema:
## Rotterdam 602; 1998.
[29] Marques R, Lourenço PB. Possibilities and comparison of structural component
models for the seismic assessment of modern unreinforced masonry buildings.
## Comput Struct 2011;89:2079–91.
338I. Caliò et al./Engineering Structures 40 (2012) 327–338