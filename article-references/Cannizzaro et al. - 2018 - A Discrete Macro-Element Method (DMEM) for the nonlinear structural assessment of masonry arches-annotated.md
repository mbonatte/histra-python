

Contents lists available atScienceDirect
## Engineering Structures
journal homepage:www.elsevier.com/locate/engstruct
A Discrete Macro-Element Method (DMEM) for the nonlinear structural
assessment of masonry arches
## F. Cannizzaro, B. Pantò, S. Caddemi, I. Caliò
## ⁎
Department of Civil Engineering and Architecture, University of Catania, Italy
## ARTICLE INFO
## Keywords:
Macro-element modelling
## Discrete Element Method
Discrete Macro-Element Method (DMEM)
Masonry arch
Historical structures analysis
Nonlinear analysis
HiStrA software
## ABSTRACT
The structural response of masonry arches is strongly dominated by the arch geometry, the stone block di-
mensions and the interaction with backfill material or surrounding walls. Due to their intrinsic discontinuous
nature, the nonlinear structural response of these key historical structures can be efficiently modelled in the
context of discrete element approaches. Smeared crackfinite elements models, based on the assumption of
homogenised media and spread plasticity, fail to rigorously predict the actual collapse behaviour of such
structures, that are generally governed by rocking and sliding mechanisms along mortar joints between stone
blocks. In this paper a new Discrete Macro-Element Method (DMEM) for predicting the nonlinear structural
behaviour of masonry arches is proposed. The method is based on a macro-element discretization in which each
plane element interacts with the adjacent elements through zero-thickness interfaces and whose internal de-
formability is related to a single degree of freedom only. Both experimental and numerical validations show the
capability of the proposed approach to be applied for the prediction of the non-linear response of masonry arch
structures under different loading conditions.
## 1. Introduction
Although arches, vaults and domes have been adopted since ancient
ages [1] for engineering works, their complete structural assessment is
not an easy task even today. Masonry arches transmit the self-weight
and the applied loads through load-paths that mainly involve com-
pressive stresses by taking advantage of gravity loads through their own
shape. The high nonlinearity, due to low-tensile resistance of masonry
or to the presence of dry stone-interfaces, does not allow the assump-
tion of linear elastic behaviour and leads to load dependent equilibrium
solutions strongly related to the arch geometry and its supports con-
ditions. A further very complex numerical issue is related to the pre-
sence of the backfill whose actual structural contribution is very diffi-
cult to model due to the non cohesive nature of the material generally
adopted[2]. For this reason in many cases it is generally preferred to
model the backfill structural role simply considering its stabilising ef-
fect related to its own weight and neglecting its mechanical contribu-
tion.
In the past, graphical based design approaches have been developed
and widely used for the structural design and the construction of
monumental structures[3]. However, these traditional methods, based
on the concept of the line of thrust, are difficult to apply in presence of
material nonlinearities and cyclic loads related to dynamic actions such
as earthquakes. On the other hand, the potential availability of efficient
and easy to apply numerical approaches could allow performing non-
linear structural analyses under different loading conditions, such as
dynamic excitations or moving loads, these latter typical of masonry
arch bridges.
The most important contributions to the understanding of the
structural behaviour of stone and masonry arches were provided by
Jacques Heyman in his famous treatises[3–7]. More recently, several
numerical strategies have been proposed based on linear[8–11] or
nonlinear Finite Element Models (FEM)[12,13], or Discrete Element
Method (DEM)[14,15].
Sarhosis et al.[16]presented a three dimensional computational
model, based on the DEM, which was used to investigate the effect of
the angle of skew on the load carrying capacity of twenty-eight single
span stone masonry arches with different geometric layouts.
Rizzi et al.[17]presented an analytical and numerical analysis of
the classical Couplet–Heyman problem in the statics of circular ma-
sonry arches.
Dimitri and Tornabene[18] developed an analytical model based on
limit analysis for describing the stability of pointed and basket-handle
arches and portals with respect to circular ones, for varying geometry
parameters. They compared the predictions of the analytical model
with results of numerical modelling by the classical DEM and obtained
https://doi.org/10.1016/j.engstruct.2018.04.006
Received 31 October 2017; Received in revised form 26 January 2018; Accepted 3 April 2018
## ⁎
Corresponding author.
E-mail address:icalio@dica.unict.it(I. Caliò).
## Engineering Structures 168 (2018) 243–256
Available online 27 April 2018
0141-0296/ © 2018 Elsevier Ltd. All rights reserved.
## T

a satisfactory agreement showing the potentiality of the discrete ele-
ment framework as a method of evaluating the quasi-static behaviour of
unreinforced masonry structures. In the context of the DEM strategies,
Dimitri et al.[19]and De Lorenzis et al.[20,21]investigated the im-
portant role of buttresses, in the dynamicfield, considering several
shapes of the buttress, typical of ancient constructions.
Gago et al. in[2], using modern structural analysis, explained the
favourable effect of the extrados infill in the stability of arched struc-
tures also highlighting the high collapse risk related to the backfill re-
moval.
Very recently Zhang et al.[22]investigated the nonlinear response
of brick-masonry arches, up to collapse, by using an accurate 3D meso-
scale description utilising solid elements for representing brick units
and 2D nonlinear interface elements for describing mortar joints and
brick–mortar interfaces. The masonry meso-scale strategy has been also
combined with an original domain partitioning approach that, allowing
for parallel computation, leads to powerful high accurate computa-
tional tool applicable for large structures.
In this paper an innovative Discrete Macro-Element Method
(DMEM), alternative to previously proposed approaches, for the simu-
lation of the nonlinear behaviour of masonry arches is presented. The
proposed approach takes advantage of the Discrete Element Method
(DEM) strategies at a‘macro-scale’.Differently from the classical DEM
approach, in which each element is considered as a rigid body, in the
proposed DMEM strategy each macro-element possesses a shear de-
formability allowing to identify shear diagonal local failure. This shear
deformability is related to a single degree of freedom for each macro-
element. The mechanical interaction among adjacent macro-elements is
concentrated in zero-thickness interfaces distributed along the entire
length of the contact edges. The computational cost of the proposed
numerical approach is greatly reduced in comparison to that involved
in detailed nonlinearfinite element simulations or DEM strategies based
on meso-scale discretizations.
The basic macro-element, which is adopted for the simulation of an
arch macro-portion, is described in Section2. It consists of an articu-
lated irregular quadrilateral whose internal deformability is dependent
on a single degree of freedom. Three further Lagrangian parameters
identify the rigid motion of the element needed to complete its plane
kinematics description. Theflexural and shear-sliding behaviours are
governed by along-edge zero-thickness interfaces, lying on the sides of
the quadrilateral and governing the interaction with the adjacent
macro-elements. Three specific non-linear one-dimensional constitutive
laws are considered in the model for simulating separately theflexural,
shear-diagonal and shear-sliding behaviour of the masonry medium,
assumed as an orthotropic homogenised continuous material. The ca-
libration of the model requires few parameters in order to define the
basic masonry mechanical properties. Such properties of the material
can be easily obtained from current experimental tests and/or sug-
gested by technical codes. The equivalence between the masonry arch
portion, that is represented at the macro-scale, and the macro-element
is here based on a very simplefibre calibration approach making the
interpretation of the numerical results straightforward and un-
ambiguous.
In Section2 a detailed description of the kinematics of the proposed
macro-element is provided. Furthermore, a qualitative classification of
the typical failure mechanism of masonry arches is presented and it is
shown how the proposed approach is capable to provide a satisfactory
prediction of all the possible collapse mechanisms of a masonry arch.
## In Section
3 the
mechanical calibration of the element in terms of its
shear behaviour and its contouring interfaces, which govern the
membrane deformability of the element, are described. In the numer-
ical applications (Section4), the model is applied for the simulation of
the nonlinear response of masonry arches for which experimental and
numerical results are available from previous research-studies reported
in the literature.
The obtained results show the capability of the proposed‘parsimo-
nious’(i.e. low cost) approach to be used for the structural assessment
of masonry arch structures both for researches and practical applica-
tions.
- The DMEM formulation for masonry arches
The proposed nonlinear discrete macro-element for plane masonry
curved structural elements, such as arches, is defined according to an
original approach that enriches the classical discrete element strategy
generally based on rigid elements interacting by means of nonlinear
links.
The basic element here proposed can be described through a me-
chanical representation obtained as a nontrivial upgrade of a regular
macro-element, based on the use of rectangular elements, proposed for
the simulation of unreinforced and confined masonry structures
[23–26]. In this new formulation the element is conceived as a plane
irregular articulated quadrilateral, formed by four rigid sides connected
by internal hinges, hence, differently from the classical DEM, the ele-
ment is endowed with an internal shear deformability that is related to
a single degree of freedom. Furthermore, the interaction between ad-
jacent elements is modelled by along-sides nonlinear zero-thickness
continuous interfaces,Fig. 1. The latter, connecting two rigid sides of
different quadrilaterals, are responsible for the axial andflexural be-
haviour as well as the shear sliding between adjacent elements.
The kinematics of the proposed plane macro-element, although
described by four degrees of freedom only, allows a simple but accurate
description of theflexural, shear diagonal and shear sliding collapse
behaviour of masonry arches. Thanks to the capability of capturing the
main collapse mechanisms, the above introduced macro-element
modelling leads to an efficient simulation of arch structures loaded in
their own plane.
Some typical arch collapse scenarios, in which the relevant damage
patterns are highlighted, are reported inFig. 2. Namely,Fig. 2a reports
an  arch  collapse  mechanism  dominated  by  aflexural  failure
Fig. 1.The discrete macro-element: (a) discretization pattern of a masonry arch; (b) the interface for the case of a linearly variable width.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 244

mechanism, in whichfive hinges are activated.Fig. 2b shows the cap-
ability of the element to grasp shear local crisis of afinite portion of
masonry element.Fig. 2c highlights a shear failure scenario related to
shear sliding mechanism between stone blocks or concentrated in
mortar joints.
It is worth to notice that the overall elastic shear deformation of a
masonry arch, discretized by several macro-elements, can be partly
related to the diagonal deformations of the irregular quadrilateral and
partly attributed to concentrated sliding displacements along the in-
terfaces. In the proposed formulation, the shear-sliding mechanism is
aimed to govern the deformations between macro-elements related to
the occurrence of sliding along the interfaces (Fig. 2c). On the other
hand, the shear-type deformability enriches the element kinematics
and, differently from the classical DEM approach, allows the simulation
of possible diagonal shear cracking damage distribution or failure re-
lated to the shear collapse of a masonry element (Fig. 2b). Mixed failure
mechanisms can also be considered being each mechanism governed by
specific constitutive laws.
The versatile geometry of the element allows a consistent simulation
of masonry arch structures also in presence of complex geometrical
layouts or for those cases in which the texture, related to the orientation
of the mortar joints, could strongly affect the structural behaviour. In
these latter cases, the proposed model can be employed considering the
actual geometry and the real arrangement of the units through a con-
sistent mesh of irregular quadrilateral elements. One peculiarity of the
proposed approach is that the axial andflexural deformations of the
homogenised masonry arch portion, represented by the macro-element,
are both lumped in the zero-thickness interfaces.
## 2.1. Kinematics
The DME kinematics is presented in this section to describe both the
relative displacements at the interface between elements and the shear
deformation mechanism of the single macro-element.
The macro-element is constituted by an irregular plane quadrilateral
whose edges, connected by four rotational hinges, are assumed to be
rigid. Each side of the quadrilateral is characterised by its length
l
k
## ,
## =...k1, ,4
, and the internal angles between the adjacent edges
α
k
## ,
## =...k1, ,4
, as indicated inFig. 3(anti-clockwise numbering is adopted).
The in-plane kinematics of each element is governed by 4 degrees of
freedoms, three associated to the rigid body motion and the other re-
lated to the quadrilateral in-plane articulation. The chosen Lagrangian
parameters, indicated inFig. 3, are the translational displacements
## U
## ,
## V
and the rotation
## Φ
of the centre of mass of the element‘G’(Fig. 3a) and
the parameter
## Γ
, that identifies the variation of the angle
α
## 1
between the
edges departing from the origin of the local element reference system
## (
ee,
xy
), as depicted inFig. 3b. All the Lagrangian parameters of the
macro-element are collected in the vector
## =
## UV
d[
## ΦΓ
## ]
## T
## .
In order to describe the mechanical behaviour related to the inter-
action with adjacent elements, the definition of the in-plane kinematics
of each side of the quadrilateral, as a function of the chosen Lagrangian
parameters, is introduced in the following subparagraph.
2.1.1. Interface displacements
Let us consider two adjacent elementspandqsharing thei-th in-
terface, where thep-th element is located on the left of the interface
whereas theq-th element is located at its right,Fig. 4. Denoting by
ξ
the
Fig. 2.Typical in-plane collapse mechanisms of a masonry arch: (a) Flexural
failure scenario related to the formation of several hinges; (b) shear failure
scenario due to the failure of a stone element or afinite portion of a masonry
arch; (c) shear failure scenario due to the localised sliding along a mortar joint.
Fig. 3.The element’s kinematics and the chosen Lagrangian parameters: (a) the rigid body motion and (b) the generalized shear distortion.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 245

normalised abscissa, variable between 0 and 1, referred to a local re-
ference system (
ee,
ξη
) of thei-th interface, the corresponding local
longitudinal and orthogonal displacements of the two opposite element
edges
uξ(),
p
vξ()
p
and
uξ(),
q
vξ()
q
can be expressed as function of cor-
responding auxiliary local degrees of freedom
uvv,,
p01
pp
and
uvv,,
q01
qq
(Fig. 4) given by the displacements of the hinges at
## =ξ0,1
, as follows:
## ⎡
## ⎣
## ⎢
## ⎤
## ⎦
## ⎥
## =
## ⎡
## ⎣
## −
## ⎤
## ⎦
## ⎡
## ⎣
## ⎢
## ⎢
## ⎤
## ⎦
## ⎥
## ⎥
## ⎡
## ⎣
## ⎢
## ⎤
## ⎦
## ⎥
## =
## ⎡
## ⎣
## −
## ⎤
## ⎦
## ⎡
## ⎣
## ⎢
## ⎢
## ⎤
## ⎦
## ⎥
## ⎥
uξ
vξ
ξξ
u
v
v
uξ
vξ
ξξ
u
v
v
## ()
## ()
## 100
## 01
## ;
## ()
## ()
## 100
## 01
p
p
p
q
q
q
## 0
## 1
## 0
## 1
p
p
q
q
## (1)
By collecting the local longitudinal and transversal displacement
functions    in    the    vectors
## =ξ
uξ vξ
u() [
## ()  ()
## ]
p
## T
pp
and
## =ξ
uξ vξ
u() [
## ()  ()
## ]
q
## T
qq
, and the auxiliary local degrees of freedom of
each edge in the vectors
## =
uv v
u[]
p
## T
p01
p
p
and
## =
uv v
u[]
q
## T
q01
q
q
## , Eq.
(1) can be rewritten in compact notation as follows:
==ξξ    ξξuNu  u   Nu()   () ;()   ()
ppqq
## (2)
where
## =
## ⎡
## ⎣
## −
## ⎤
## ⎦
ξ
ξξ
## N()
## 100
## 01
## (3)
The auxiliary local degrees of freedom of each edge of the two ad-
jacent elementsp,qat thei-th interface can be related to the relevant
Lagrangian parameters as follows:
==uAd  u  Ad
pppqqq
## (4)
where
## AA,
pq
are compatibility matrices, whose components are simply
related to the element geometry. The compatibility matrices, relative to
the example reported inFig. 4, are given as follows:
## =
## ⎡
## ⎣
## ⎢
## ⎢
## ⎢
## ⎢
## −−   + −
## −−   + −
## −−   + −−
## ⎤
## ⎦
## ⎥
## ⎥
## ⎥
## ⎥
## =
## ⎡
## ⎣
## ⎢
## ⎢
## ⎢
## −−   + −
## −−   + −
## −−   + −
## ⎤
## ⎦
## ⎥
## ⎥
## ⎥
yyxx
yyxx
yyxxlp
yyxx
yyxx
yyxxl
## A
ee eeee e
ee eeee e
ee eeee e
## A
ee eeee e
ee eeee e
ee eeee e
## ··[()( )]· 0
## ··[()( )]· 0
## ··[()( )]·
## ··[( )( )]·0
## ··[( )( )]·0
## ··[()( )]·
p
ξpx ξpy
pGp
pxp   Gp  py   ξ
ηpx ηpy
pGp
pxp   Gp  py   η
ηpx ηpy
pGp
pxp   Gp  py   η
α
α
q
ξqx ξqy
qGq
qxq   Gq  qy   ξ
ηqx ηqy
qGq
pxq   Gq  qy   η
ηqx ηqy
qGq
qxq   Gq  qy   η  q
## 2
## 2
## 2
## 2
## 3
## 3
## 4
sin
sin
## 1
## 1
## 1
## 1
## 4
## 44
p
p
## 4
## 3
## (5)
where
xy(,)
## Gp
## Gp
and
xy(,)
## Gq
## Gq
represent the coordinates of the centre of
mass of thep-th andq-th elements, respectively. In view of Eq.(4),
providing the displacements of the elements edges, Eq.(2), can be
expressed as a function of the corresponding element degrees of free-
doms as follows:
==ξξξξuNAdu   NAd()   ();()   ()
pppqqq
## (6)
therefore, the relative displacement function
## ̂
## =−ξξξ
uuu()   ()  ()
qp
of the
i-th interface can be expressed as follows:
## ̂
=−ξξ   ξ
uNAdNAd()   ()()
qqpp
## (7)
2.1.2. The kinematics associated to the shear distortionΓ
Besides the kinematic characterisation of the interfaces between
macro-elements, aiming at modelling the axial, bending and sliding
behaviour of curved structures, the shear behaviour is intended to be
described by the kinematics of the macro-element itself that implies
angle variation of adjacent edges. The macro-element internal de-
formability, related to the Langrangian parameter
## Γ
, implies displace-
ments in correspondence of the 3-rd and 4-th vertexes of the element
given by
## =−
## =−
## =−
## =
u
u
ulα
ulα
## Γ;
## Γ;
sin  Γ;
cos  Γ
x
lαα
α
y
lαα
α
x
y
## 3
sin  sin
sin
## 3
cos  sin
sin
## 441
## 441
## 424
## 3
## 424
## 3
## (8)
- The mechanical behaviour
The formulation here proposed follows a phenomenological de-
scription of the mechanical behaviour of an arch portion in which the
zero-thickness interfaces rule the axial-flexural response and the shear
sliding behaviour of adjacent elements, while the in-plane shear ele-
ment deformability is related to the angular distortion of the articulated
quadrilateral. The mechanical characterisation of the zero-thickness
interfaces is here performed through a straightforwardfibre calibration
procedure while the shear element deformability is calibrated through a
mechanical equivalence with a reference geometric-consistent con-
tinuous plane model.
Each macro-element is intended to represent an equivalent homo-
genised masonry portion, whose mechanical properties can be inferred
according to suitable homogenization techniques[27–29] here con-
veniently extended.
3.1. The interface stiffness matrix
A peculiar aspect of the proposed numerical method is that the
mechanical properties in the zero-thickness interfaces include both the
stone and the mortar joints mechanical behaviour of the adjacent ele-
ments, leading to a simple homogenization strategy. As a consequence,
the apparent interpenetration of the rigid edges of adjacent panels,
along the zero-thickness interfaces, does not point out a compatibility
violation but simply identifies states corresponding to compressive
strains.
The zero-thickness continuous interfaces are characterised by a
nonlinear behaviour described by the incremental relationship between
the increments of the internal force distributions along the longitudinal
and orthogonal directions of the interface,
dfξdfξ(),  ()
uv
, collected in the
vector
## =dξ
df ξ  df ξ
f() [
## ()  ()
## ]
## T
uv
int
and the relative displacement incre-
ment
## ̂
dξu()
of the vector
## ̂
ξ
u()
, introduced in Eq.(7), as follows:
## ̂
## =
dξξdξfku()   () ()
## Tint
## (9)
where
ξk()
## T
represents a
## ×22
tangent stiffness distribution of thei-th
interface at the abscissa
ξ
that can be defined as follows:
## =
## ⎡
## ⎣
## ⎢
## ⎤
## ⎦
## ⎥
ξ
kξ k ξ
kξkξ
k()
## ()    ()
## ()   ()
## T
## TT
## TT
uuv
vuv
## (10)
Fig. 4.Local relative displacements in the interface between two adjacent
macro-elements.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 246

where the subscripts
u
and
v
identify the longitudinal and orthogonal
directions of the generici-th interface.
In view of Eq.(7), the force increment of thei-th interface
dξf()
int
## ,
given by Eq.(9), can be also expressed as function of the degrees of
freedom increments of the corresponding adjacent elements, denoted as
dddd,
pq
, as follows:
=−dξξξdξdfkNAdNAd()    ()[ ()()    ]
## Tqqppint
## (11)
Considering Eq.(11) and by applying the principle of virtual work
an
## ×88
tangent stiffness matrix related to the contribution of thei-th
interface, with respect to the global degrees of freedom of the two
adjacent elementsp,q, is obtained as follows:
## ∫
## =
## ∼∼
ξξξdξKANkNA() () ()
## T
## T
## T
## T
## 0
## 1
## (12)
being
## =
## ⎡
## ⎣
## ⎢
## ⎤
## ⎦
## ⎥
## =
## −
## ∼
ξ
ξξ
## A
## A0
## 0A
## N
## NN
## ;()[
## ()   ()
## ]
q
p
## (13)
The tangent stiffness matrix
## K
## T
rules the nonlinear behaviour of the
i-th interface and its current value is related to the tangent interface
stiffness distribution
ξk()
## T
## .
The integration of Eq.(12)has been performed according to a
uniformfibre discretation of the adjacent elements, as depicted in
Fig. 5, where the masonry macro-elementspandq, have been dis-
cretised according to
n
f
cells of the homogenised masonry arch, and for
simplicity, a constant width of the arch elements is considered.
Precisely, the contribution
ξk()
## T
j
to the stiffness matrix of thej-th
fibre at abscissa
ξ
j
## ,
## =...jn1, ,
f
, is obtained by following a detailed ca-
libration procedure based on the main mechanical and geometrical
parameters of the masonry. According to the presented procedure, for
the interface stiffness matrix definition, the generic interface is re-
presentative of the elastic/inelastic axial,flexural and sliding beha-
viours of adjacentfinite portions of masonry considered as an equiva-
lent homogeneous medium.
The shear sliding behaviour of adjacent elements, along the inter-
faces, being associated to a single degree of freedom, has been char-
acterised according to a uniaxial nonlinear behaviour, as clarified in the
next section.
It is worth to notice that, the choice to concentrate the mechanical
properties of the connected elements in zero-thickness interfaces is
common to other discrete numerical approaches such for example the
applied element method[30–34] and the rigid body spring model
[35–38], however these latter strategies do not operate at the macro-
scale.
Different levels of discretisation can be adopted in accordance to the
chosen number offibres along the masonry arch section. Furthermore,
the presented procedure, for the evaluation of the interface stiffness
matrix, can accommodate any nonlinear model chosen to represent the
masonry constitutive law characterising the constitutive behaviour of
each masonryfibre.
3.1.1. The stiffness component orthogonal to the interface edge
The evaluation of the contribution of thej-thfibre,
## =...jn1, ,
f
, to the
tangent stiffness component
kξ()
## T
v
in the direction orthogonal to the
interface of thei-th interface, is obtained as the combination in series of
two contributions inherited by elementspandq. For arches with linear
non-uniform geometry and constant width of the element, the area of
thej-thfibre varies linearly from
## A
p0
j
to
## A
p1
j
over the length
l
p
j
on thep-
th element and from
## A
q0
j
to
## A
q1
j
over the length
l
q
j
on theq-th element,
as indicated inFig. 5.
According to thefibre geometry the contributions
kk,
pq
jj
to the
tangent stiffness component of thej-thfibre relative to thep-th andq-th
element are as follows:
## =
## =
## ∫
## ∫
## +−
## +−
k
k
## ;
p
## E
q
## E
j
## Tp
j
l
p
j
dz
## A
p
j
z
l
p
j
## A
p
j
## A
p
j
j
## Tq
j
l
q
j
dz
## A
q
j
z
l
q
j
## A
q
j
## A
q
j
## 0
## 0
## (
## 1
## 0
## )
## 0
## 0
## (
## 1
## 0
## )
## (14)
being
## EE,
## Tp   Tq
jj
the tangent modulus of the nonlinear constitutive be-
haviour ofj-fibre relative to thep-th andq-th element, respectively. The
integral appearing at the denominator of Eq.(14), extended over the
length of thefibre, by using a local coordinatezalong thefibre axis, can
be evaluated leading to the following expressions:
## =≠=≡
## =≠=≡
## −
## ⎛
## ⎝
## ⎜
## ⎞
## ⎠
## ⎟
## −
## ⎛
## ⎝
## ⎜
## ⎞
## ⎠
## ⎟
kifAAkifAA
kifAAkifAA
## ;
## ;
p
## EA A
l
ppp
## EA
l
pp
q
## EA A
l
qqq
## EA
l
qq
## ()
## ·ln
## 1010
## ()
## ·ln
## 1010
j
## Tp
j
p
j
p
j
p
j
## A
p
j
## A
p
j
jj
j
## Tp
j
p
j
p
j
jj
j
## Tq
j
q
j
q
j
q
j
## A
q
j
## A
q
j
jj
j
## Tq
j
q
j
q
j
jj
## 10
## 1
## 0
## 0
## 10
## 1
## 0
## 0
## (15)
Fig. 5.Fibre discretisation of thei-th interface and the adjacent macro-elements representation.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 247

In order to consider the actual orientation of thei-th interface,
identified by the unit vector
e
η
, with respect to thej-fibre relative to the
p-th andq-th element, the two contributions to the tangent stiffness
component, evaluated as in Eq.(15), are modified as follows:
## ==kkkkeeee|·|;|·|
p
i
ppη
q
i
qqη
j
j
j
j
j
j
## (16)
being
ee,
pq
jj
the unit vectors identifying thej-thfibre orientation along
thep-th andq-th element, as inFig. 5.
3.1.2. The stiffness component along the interface edge
In view of the kinematics of the macro-element, described in the
previous section, the sliding mechanism of the two elementsp,qad-
jacent to thei-th interface is governed by a single relative displacement
component
## ̂
u
, and the contribution of thej-thfibre,
## =...jn1, ,
f
, to the
tangent stiffness component
kξ()
## T
j
u
along thei-th interface edge is here
considered independent of thefibre position. Accordingly, the non-
linear behaviour of the interface ruling the sliding mechanism between
the two edges of the interface is here calibrated by adopting an overall
suitable nonlinear constitutive law of the cohesive-friction type.
Without loss of generality, only as a matter of example, for nu-
merical application purposes a Mohr-Coulomb approach is followed by
adopting a yielding dominium related to the actual contact area
## A
c
of
thei-th interface, accounting for the presence of cracks, as follows:
## ̂
=++FcAμNgu··(
## )
yc
p
## (17)
where the mechanical parameters are the cohesioncand the friction
coefficientμ, while
## =
## ∑
## =
## Nfξ()
j
n
v
j
## 1
f
is the resultant of the orthogonal
forces
f
v
at thei-th interface and
## ̂
gu()
p
represents an hardening func-
tion. For the case of rigid-plastic behaviour the tangent stiffness com-
ponent
kξ()
## T
j
u
along thei-th interface is as follows:
## ̂
## ̂
## ∑
## ∑
## =∞  ∀ = ...<
## =∀=...=
## =
## =
kξj   nfξ F
kξj   nfξ F
()1,,  for()
()1,,  for()
## T
j
f
j
n
u
j
y
## T
j
n
dg u
du
f
j
n
u
j
y
## 1
## 1
## ()
## 1
u
f
u
f
p
p
f
## (18)
where
## ∑
## =
fξ()
j
n
u
j
## 1
f
is the resultant of the forces
f
u
along thei-th interface
direction.
It has to be noted that the adoption of the yielding dominium as in
Eq. (17)somehow accounts for the influence of the internal forces
normal to thei-th interface on the sliding mechanism. On the other
hand, the influence of the sliding mechanism on the stiffness along the
direction orthogonal to the interface is neglected. For the latter two
reasons the out-of-diagonal terms of the tangent stiffness matrix in Eq.
(10) are considered null. However, it has to be reminded that the me-
chanical model of the interfacefibre discretization of the proposed
macro-element can accommodate any bi-axial constitutive law able to
account for the longitudinal-orthogonal mutual influence.
3.2. The macro-element in-plane shear diagonal stiffness
The in-plane shear deformability of the proposed macro-element is
controlled by a single Lagrangian parameter related to the angular
distortion
## Γ
of the articulated quadrilateral, as introduced in Section2.1
describing the element kinematics. The mechanical characterisation of
the shear element deformability is calibrated through a mechanical
equivalence, introduced in this section, with reference to a geome-
trically consistent continuous plane model.
The calibration of the macro-element shear stiffness
## K
## Γ
is performed
by enforcing an equivalence with a homogeneous continuum model, i.e.
an isotropic plate of the same geometry and subjected to a displacement
field consistent to the kinematics of the articulated quadrilateral as in
## Fig. 3b.
In order to enforce the equivalence between the discrete and the
continuous model, the displacementfield of the plate isfirst provided as
function of the variation of angle
## Γ
, ruling the deformation mode. It is
worth to notice that the presented approach implies that the strainfield
consistent with a pure shear behaviour is recovered in the case of
regular quadrangular element.
The displacementfield
## =xy
uxy uxy
u(,) [
## (,)  (,)
## ]
## T
xy
of a generic point
of the corresponding irregular plate is defined by its components along
the
x
and
y
directions
uxy u xy(,),  (,)
xy
respectively, that can be ex-
pressed according to the intrinsic coordinates
ς
and
λ
,defined in the
range
## −[1,1]
, as follows:
## ∑∑
## ==
## ==
uςλu m ςλ  u ςλu m ςλ(,)(,);   (,)(,)
x
i
ix  iy
i
iy  i
## 1
## 4
## 1
## 4
## (19)
## Being
uu,,
ix   iy
## =...i1,4
, the translational displacements of the nodes
of the quadrilateral,Fig. 3, and
mςλ(,)
i
the classical bilinear polynomial
functions given by:
## ==
## ==
## −−+−
## ++−+
mςλmςλ
mςλmςλ
## (,);   (,);
## (,);   (,)
ςλςλ
ςλςλ
## 1
## (1   )(1   )
## 4
## 2
## (1   )(1   )
## 4
## 3
## (1   )(1   )
## 4
## 4
## (1   )(1   )
## 4
## (20)
Since the macro-element deformation does not depend on the rigid
body motion it is sufficient to consider a kinematics in which one side of
the quadrilateral is rigidly constrained. Without loss of generality, by
constraining thefirst edge (between the nodes1and2), the displace-
ment of vertices3and4only are considered, as a consequence the
summations in Eq.(20) can be limited to the last two terms. The cor-
responding deformationfield is given by
## =
## =
## =+
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
εςλ
εςλ
γςλ
## (,);
## (,);
## (,)
x
uςλ
x
y
uςλ
y
xy
uςλ
x
uςλ
y
## (,)
## (,)
## (,)
## (,)
x
y
y
x
## (21)
In view of Eqs.(20) and (21)the deformationfield can be written as
follows:
=ςλςλεBu(,)   (,)
r
## (22)
where
## =
## ⎡
## ⎣
## ⎢
## ⎢
## ⎢
## ⎤
## ⎦
## ⎥
## ⎥
## ⎥
## =
## ⎡
## ⎣
## ⎢
## ⎢
## ⎢
## ⎤
## ⎦
## ⎥
## ⎥
## ⎥
## =
## ⎡
## ⎣
## ⎢
## ⎢
## ⎢
## ⎢
## ∂
## ⎤
## ⎦
## ⎥
## ⎥
## ⎥
## ⎥
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
ςλ
εςλ
εςλ
γςλ
u
u
u
u
ςλ
mςλ
εu
## B
## (,)
## (,)
## (,)
## (,)
## ,
## (,)
## 00
## 00(,)
x
y
xy
r
x
y
x
y
mςλ
x
mςλ
x
mςλ
y
mςλ
y
mςλ
x
mςλ
y
mςv
x
## 3
## 3
## 4
## 4
## (,)(,)
## (,)
## 4
## (,)(,)(,)(,)
## 34
## 3
## 334 4
## (23)
According to the macro-element kinematics, described in Section2,
the nodal displacement vector
u
r
can be expressed in terms of the
variation of angle
## Γ
as follows:
=uCΓ
rr
## (24)
where the vector
## C
r
, in view of Eq.(8), is given as:
## =
## ⎡
## ⎣
## ⎢
## ⎢
## ⎢
## ⎢
## ⎢
## −
## −
## −
## ⎤
## ⎦
## ⎥
## ⎥
## ⎥
## ⎥
## ⎥
lα
lα
## C
sin
cos
r
lαα
α
lαα
α
sin  sin
sin
sin  cos
sin
## 41
## 41
## 442
## 3
## 442
## 3
## (25)
Accounting for Eqs.(24) and (25)the deformationfield vector given
by Eq.(22) can now be expressed as follows:
=ςλςλεBC(,)   (,)Γ
r
## (26)
Furthermore, by assuming a plane stress condition, the stressfield
## =ςλ
σςλ σςλ τ ςλ
σ(,)  [
## (,)  (,)  (,)
## ]
## T
xyxy
, collecting normal
σσ,
xy
and shear
τ
xy
stress components in the
xy,
plane, related to a linear elastic isotropic
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 248

constitutive law, is given by:
=ςλςλσDε(,)(,)
## (27)
where
## =
## −
## ⎡
## ⎣
## ⎢
## ⎢
## −
## −
## +
## ⎤
## ⎦
## ⎥
## ⎥
## E
ν
ν
ν
ν
## D
## 1
## 10
## 10
## 002(1 )
## 2
## (28)
Once the strain and stressfield have been obtained, the internal
virtual work
δL
int
can be written as follows:
## ∫∫
## =
## −−
δLςλ δ ςλ J ςλ tdςdλσε(,) (,) (,)
## T
int
## 1
## 1
## 1
## 1
## (29)
where the Jacobian function
## =−
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## ∂
## Jςλ(,)
x
ς
y
λ
x
λ
y
ς
has been introduced
and
δ(·)
indicates any virtual variation of the indicated quantity.
Substitution of Eqs.(26) and (27)in Eq.(31) leads to:
## ∫∫
## =
## −−
δLςλ    ςλ   tJ ςλ dςdλδCB   DB   CΓ(,)  (,)   (,)Γ
i
r
r
## T
## T
## 1
## 1
## 1
## 1
## (30)
being
t
the constant width of the element. The double integral in Eq.
(30) represents the scalar stiffness
## K
## Γ
of a generic four-node plate with a
constant width associated to the Lagrangian parameter
## Γ
. The stiffness
## K
## Γ
can be approximated by means of a Gaussian integration scheme in
the space of the intrinsic coordinates
ς
and
λ
of the plate leading to the
following expression:
## ∑∑
## =
## ==
Kwwtςλ    ςλ   JςλCBDB   C[   (,)  (,) ] (,)
k
## N
l
## N
kl
r
k
l
k
lr
k
l
## T
## T
## Γ
## 11
## GG
## (31)
where the coefficients
ww,
kl
represent the Gaussian weights and
## ×NN
## GG
is the number of Gaussian points adopted for the integration.
Once the elastic shear stiffness
## K
## Γ
of the macro-element has been
defined, based on the equivalent isotropic plate, its uniaxial nonlinear
evolution is defined by suitable choices for the yielding domain able to
account for the confinement action of adjacent elements. In particular,
two possible yielding domains, suitable for masonry media, can be
considered, namely the Mohr-Coulomb or the Turnsek and Cacovic[39]
criteria. Further cyclic constitutive laws incorporating stiffness de-
gradation can also be adopted, as reported in[23,25], with reference to
the rectangular macro-element.
- Numerical applications
The proposed macro-element approach has been implemented in
the software HiStrA[40], specifically devoted to nonlinear analyses of
Historical Masonry Structures. The applications reported in the fol-
lowing aim at validating the proposed DMEM, both in the linear and
nonlinearfield, through a comparison with analytical, numerical and
experimental results already available in the specific literature. In
particular, the results of two different experimental campaigns have
been taken into account.
Thefirst application is relative to an experimental campaign, led by
Ramos et al. on a masonry circular arch[41], for which both static and
dynamic tests have been performed.
The second considered benchmark is relative to another circular
masonry arch, extensively studied in the literature[42], by means of
limit analysis and nonlinearfinite element approaches.
The choice of the circular arches occurred to obtain a validation of
the model with experimental and numerical data already available in
the literature. However, the proposed approach is not limited to cir-
cular arches only. Each element has a generic quadrangular shape that
can be adapted to different geometrical layouts according to an as-
sumed mesh, similar to a FEM modelling.
Without loss of generality, the constitutive laws described in the
previous sections are conveniently particularized as better described in
the following.
The axial behaviour of each masonryfibre is characterised by an
elastic–plastic behaviour with linear post peak softening branches
whose ductility is governed by fracture energy values in tension,
## G
t
, and
compression,
## G
m
, as qualitatively reported inFig. 6.
The tensile
## F
t
and compressive
## F
m
strengths of eachfibre are as-
sumed to be related to the minimum cross area
## A
p
j
min
of thefibre along
its span as a function of
f
t
p
and
f
m
p
, respectively the tensile and com-
pressive yielding strengths of the homogenised masonry medium of the
p-th element. The compressive and tensile behaviour is also char-
acterised by a linear softening associated to the corresponding fracture
energies identified inTable 1by the capital letterG. Consequently, the
ultimate displacements
uξu ξ(),  ()
t
j
m
j
uu
can be conveniently expressed as
reported inTable 1.
With regard to the sliding behaviour a post-elastic linear softening is
here employed, associated to a sliding fracture energyG
s
. In particular,
with reference to Eq.(18), the function
## ̂
gu()
p
is given by
## ̂̂
## =gu
cA
## G
u()
## ()
## 2
p
s
p
## 2
## (32)
Finally, for the diagonal shear mechanism, an elastic-perfectly
plastic behaviour is considered.
4.1. Simulation of an experimental campaign on a circular masonry arch
subjected to static loads and dynamic characterisation
This experimental campaign has been conducted at the laboratory
of the Civil Engineering Department of the University of Minho with the
aim of identifying damage in masonry arches. To this purpose, a cir-
cular arch, built with clay bricks (100 × 50 × 25 mm
## 3
) bounded with
mortar with poor mechanical properties[43], is considered. The geo-
metrical layout of the investigated arch is reported inFig. 7, con-
sidering a width of the arch equal to 450 mm, however a detailed de-
scription of the specimen and the performed experiment can be found
in [41]. In the experimental campaign modes and frequencies of vi-
brations have been identified in the undamaged configuration atfirst;
then, in order to induce a damage in the arch, to be successively
identified, several cycles of loading and unloading were performed by
applying a concentrated vertical force located at the quarter of the span,
as reported inFig. 7.
Fig. 6.Constitutive law adopted for the axial behaviour of thefibres.
## Table 1
The mechanical characteristics of the nonlinearfibre equivalent to two adjacent
fibres.
Elastic stiffnessCompressive and tensile yielding
fibre forces
Compressive and
tensilefibre ultimate
displacements
## =
## +
kξ()
## T
v
j
k
p
j
i
k
q
j
i
k
p
j
i
k
q
j
i
=FξA   f A   f() min(,)
t
j
p
j
t
p
q
j
t
q
minmin
## =
## +
uξ()
t
u
j
## G
t
p
## G
t
q
## F
t
ξ
j
## ()
=FξA  f A  f() min(,)
m
j
p
j
m
p
q
j
m
q
minmin
## =
## +
uξ()
m
u
j
## G
m
p
## G
m
q
## F
m
ξ
j
## ()
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 249

Thefirst numerical simulations here performed aim at providing a
model validation in the linear domain through a comparison in terms of
eigen-properties. Aiming at performing both an experimental and nu-
merical validation, the eigen-properties obtained by the proposed
model have been compared with the experimental values as well as the
results obtained through a plane linear FEM simulation performed by
using the software environment SAP2000[44].
All the mechanical properties of the homogenised material, adopted
in the numerical simulations according to the experimental data, are
reported inTable 2. In particularf
m
andf
t
are the strengths in com-
pression and tension,G
m
andG
t
are the compressive and tensile frac-
tural energy values.
Finally the cohesionc, the friction coefficientμand the fractural
shear energyG
s
govern the Mohr-Coulomb yielding criterion and its
ductility. The elastic properties, governed by the modulusEandG, have
been determined as suggested in[45].
The comparison in terms of thefirst four mode shapes is reported in
Fig. 8, where the corresponding natural frequencies are shown as well.
It can be observed how the considered model is able to provide the
same vibration modes obtained by the two-dimensional FEM analysis.
A more detailed comparison among the frequencies is reported in
Table 3in which thefirst four eigenvalues have been considered. The
differences in terms of frequencies with respect to the experimental and
the FEM results are within the limits of 7.90% and 2.32% respectively;
it is worth to note that only thefirst three eigen-values have been ex-
perimentally evaluated.
With the aim to evaluate the influence of the shear deformability of
the macro-element in the linear range, a circular arch characterised by
different aspect ratiost/R= 0.1, 0.15, 0.20, 0.25 has been analysed
considering the same radius and material properties of the previous
example but different thicknesses. The eigen-values of the investigated
arches have been than evaluated by accounting and/or ignoring the
shear deformability. As reported inTable 4, frequency differences
ranging from 1.56% to 9.17% are observed, highlighting the influence
of the shear deformability, particularly for squat arches.
To validate the proposed approach in the nonlinearfield, a non-
linear static analysis was performed on the arch. In order to simulate its
actual behaviour,first the self weight was applied and then the con-
centrated load, according to the layout reported inFig. 7. The con-
sidered monitored displacement is the vertical component of the loaded
point.
In Fig. 9the comparison in terms of load-displacement curves is
reported, showing how the considered model provides a good predic-
tion of the nonlinear behaviour of the experimental test, in terms of
envelope curve. The peak load achieved during the cyclic experimental
test is 1.45 kN, while in the monotonic numerical simulation performed
with the proposed approach the peak load is 1.36 kN. The residual force
at the end of the softening branch is about 1.05 kN against a value of
about 1.01 kN in the experiment. In the same picture, the curves ob-
tained by Ramos through a nonlinear FEM simulation[45], are re-
ported. The FEM numerical simulations considered two different values
of the tensile strength (inFig. 9the cases off
t
= 0.2 MPa and
f
t
= 0.4 MPa are reported) and assumed a tensile fracture energy equal
to 1/10 of the tensile strength (expressed in N/mm).
The nonlinear response of thefirst example is associated to the
activation of fourflexural hinges. According to the obtained numerical
results all the hinges reach the limit tensile strength but do not attain to
the ultimate compressive strength. As a result, the structure maintains a
residual capacity that is related to the residual reaction of the plastic
hinges. It is worth to notice that when the progressive reduction of the
compressive area leads to the ultimate compressive strength, the re-
sidual capacity of the arch will necessary drop to zero.
In Fig. 10the numerical predictions are shown at different load
levels corresponding to the sequential initial opening of theflexural
hinge. A magnification factor of the deformed shapes equal to 100 is
adopted. In the sameFig. 10the inelastic stored strain in the direction
orthogonal to the interfaces, defined in[46], is reported in greyscale.
Aiming at investigating the influence of the main parameters gov-
erning the nonlinear static behaviour of the arch, a sensitivity analysis
with respect to the tensile strength and the tensile fracture energy has
been reported in the following.Fig. 11a reports the capacity curves
obtained by considering four further values of the tensile strengths
## (f
t
= 0.1, 0.2, 0.3, 0.4 N/mm) together with the already performed
analysis relative tof
t
= 0.25 MPa, and a tensile fracture energy
## G
t
= 0.02 N/mm. It can be observed how the tensile strength highly
influences the ultimate load and the post-peak behaviour.
The influence of different values of the fracture energy (G
t
## = 0.01,
0.02, 0.03, 0.04 N/mm) for afixed value of the peak tensile strength,
f
t
= 0.25 MPa, is investigated inFig. 11b, it can be observed how both
the peak load and the global ductility are strongly influenced by the
assumed fracture energy.
4.2. Comparison with other numerical results on a benchmark circular
masonry arch
In this section a numerical validation of the proposed model is re-
ported considering a set of elementary applications in order to compare
the results of the proposed discrete model with the results of refined
nonlinear FEM and limit analysis methods already published in litera-
ture. Namely, a stone circular arch bridge, which has been extensively
studied in the past[42,47,48]is considered.
The main plane geometrical parameters, thickness, inner span and
inner rise, are summarizedFig. 12and the width of the arch is equal to
## 1m.
Thefinite element analysis model[42]consists of quadrilateral,
four-node, bilinear, plane strain elements with two translational de-
grees of freedom per node. A typical value for the length of eachfinite
element is 0.05 m. A total number of 3036 elements was used. In the
FEM model unilateral interfaces are included between the parts of the
structure and for the parametric investigation the number of uniformly
distributed interfaces has been gradually increased. Large displacement
effects are neglected and the arch is considered to befixed to the
ground.
Fig. 7.Geometric layout of the experimental test and described in[41].
## Table 2
Mechanical properties adopted for the numerical model of the arch tested in[41].
E[MPa]f
t
[MPa]G
t
[N/mm]f
m
[MPa]G
m
[N/mm]G[MPa]c[MPa]μG
s
[N/mm]w[kN/m
## 3
## ]
## 37900.250.027.89015160.30.47.015
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 250

SAP2000Proposed model
## Mode 1
## 38.26 Hz37.37 Hz
## Mode 2
## 79.56 Hz77.81 Hz
## Mode 3
## 145.69 Hz142.92 Hz
## Mode 4
## 212.02 Hz208.95 Hz
Fig. 8.Comparisons of thefirst four modes of vibration obtained by the DMEM (HISTRA) and continuous FEM (SAP2000).
## Table 3
Comparison in terms of frequencies.
ModesExperimentalContinuous model (SAP2000)Proposed discrete model (HISTRA)
T[s]f[Hz]T[s]f[Hz]T[s]f[Hz]Err
exp
[%]Err
## SAP
## [%]
## 10.028135.590.026138.260.026837.375.002.32
## 20.013972.110.012679.560.012977.817.902.20
## 30.0071140.080.0068145.690.0070142.922.031.90
## 4__0.0047212.020.0048208.95_1.45
## Table 4
The influence of the shear-diagonal deformability in the frequencies.
Modest/R =0.10t/R =0.15t/R =0.20t/R =0.25
G=1516 MPaG→∞Diff[%]G=1516 MPaG→∞Diff[%]G=1516 MPaG→∞Diff[%]G=1516 MPaG→∞Diff[%]
## 156.9457.831.5683.5386.423.46108.08114.61    6.04130.25142.20    9.17
2116.31119.28    2.55163.14171.32    5.01197.67210.77    6.63220.36235.00    6.64
3213.63221.76    3.81299.82308.30    2.83328.44339.40    3.34356.44384.68    7.92
4274.78279.62    1.76304.41322.46    5.93362.20394.42    8.90399.47426.74    6.82
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 251

The macro-element numerical model was implemented by con-
sidering a stone by stone discretization with 39 elements corresponding
to 156 in-plane degrees of freedom. The mechanical properties of the
stone blocks have been chosen according to those adopted in the FEM
model reported in[42]and summarized inTable 5. The elastic de-
formation of the blocks is described by the Young modulus (E) and
Poisson coefficient (ν), the simplified hypotheses of zero tensile
strength (f
t
) and cohesion (c), and unlimited compressive strength (f
m
## ),
have been adopted for the bed joints. Furthermore unlimited ductility is
considered for the sliding behaviour.
The numerical simulations have been performed applying the self-
weight of the arch atfirst, and then a concentrated vertical load with
increasing amplitude. Two different load scenarios have been con-
sidered according to the position of the vertical load: in one case the
load is applied at the mid-span (case 1), while in the second case at the
quarter span (case 2). The results of the two analyses, in terms of col-
lapse mechanisms, are reported inFig. 13. In both cases the behaviour
is characterised by the occurrence offlexural hinges without the acti-
vation of sliding mechanisms along the stone interfaces. In the case of
the mid-span applied loadfive plastic hinges occur (because of the
symmetry of the geometry of the arch and of the load), while four
plastic hinges occur in the other case. The collapse mechanisms are
consistent with those obtained in the simulations already reported in
the literature[42].
The force-displacement results are reported inFig. 14in terms of
total vertical base reaction (F) vs the vertical displacement of the ap-
plication point of the external force.
A good agreement with the limit and FEM analyses in terms of ul-
timate load can be recognised, however the spread plasticity FEM ap-
proach shows a different trend of the pushover curves with respect to
the proposed DMEM.
The collapse mechanism of the arch can be dominated by theflex-
ural or the shear behaviour according to the value of the friction
## H1
## H2
## H3
## H4
Fig. 9.Capacity curves: comparison between the proposed model and the ex-
perimental results.
Fig. 10.Damage scenarios for different levels of the monitored displacement andfinal collapse mechanism.
## (a)
## (b)
## 0
## 0.2
## 0.4
## 0.6
## 0.8
## 1
## 1.2
## 1.4
## 1.6
## 1.8
## 2
## 00.20.40.60.8
Vertical load [kN]
## Displacement [mm]
## Experimental
HiStrA (reference model)
HiStrA (other tensile strengths)
## 0
## 0.2
## 0.4
## 0.6
## 0.8
## 1
## 1.2
## 1.4
## 1.6
## 1.8
## 2
## 00.20.40.60.8
Vertical load [kN]
## Displacement [mm]
## Experimental
HiStrA (reference model)
HiStrA (other fracture energies)
Fig. 11.Capacity curves: comparison between the proposed model and the
experimental results for different levels of (a) tensile strength and (b) tensile
fracture energy.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 252

coefficient attributed to the interfaces (and keeping the other me-
chanical properties according toTable 5). In order to identify the in-
fluence of the value of the friction coefficient on the limit load, as well
as on the corresponding failure scenarios, several numerical analyses
have been performed gradually reducing its value for both the load
scenarios.
In Fig. 15the collapse value of the applied load is shown as a
function of the friction coefficient. The collapse value of the applied
load has been conventionally referred to the load that produces a
Fig. 12.Geometric layout of the experimental test studied in[42].
## Table 5
Mechanical properties adopted for the numerical model of the arch studied in
## [42].
Flexural behaviour(transversal N-Links)Sliding behaviour(longitudinal N-
## Links)
E[MPa]νw[kN/
m
## 3
## ]
f
t
[MPa]f
m
[MPa]c[MPa]μ
## 50000.3  220∞00.6
Fig. 13.Collapse mechanisms of the arch: (a) mid-span load and (b) quarter of
span load.
## 0
## 50
## 100
## 150
## 200
## 0510152025
F [kN]
## Displacement [mm]
## Case 1 - Limit  Analysis
## Case 2 - Limit  Analysis
Case 1 - FEM
Case 2 - FEM
Case 1 - Proposed  approach
Case 2 - Proposed  approach
Fig. 14.Pushover curves of the arch and comparisons of the proposed model (continuous lines) with limit analysis (dashed lines) and FEM approach (dash dot lines):
mid-span load (thick lines) and quarter of span load (thin lines).
Fig. 15.Ultimate load vs friction coefficient: mid-span load (continuous line)
and quarter of span load (dashed line).
Fig. 16.Collapse mechanisms of the arch with the occurring of sliding: quarter
of span load andμ= 0.3.
Fig. 17.Ultimate load vs load position for two different values of the friction
coefficients:μ= 0.6 (continuous line) andμ= 0.3 (dashed line).
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 253

vertical displacement of 10 mm in the section where the load is applied.
It can be observed that for values of the friction coefficient greater than
aboutμ
c
= 0.4, the load is constant and equal to 150 kN, in this range
onlyflexural hinges occur, being the friction coefficient sufficient to
prevent shear-sliding along the interfaces. When the friction coefficient
is lower thanμ
c
the collapse mechanism involves a shear sliding close to
the section in which the load is applied and the value of the load pro-
gressively reduces, following a roughly linear trend, until the value of
0.1 corresponding to a case in which neither the self-weight loading
condition can be accomplished. The bifurcation value of friction coef-
ficientμ
c
is in the range 0.38–0.4 for the case of applied eccentric load
and 0.4–0.42 for the case of mid-span load.
In Fig. 16, a typical collapse mechanism of the arch associated to the
occurring of sliding is reported. This is characterised by two plastic
hinges involving the shear and theflexural behaviours located in cor-
respondence of the applied load and at the right base; in addition a
spreadflexural damage can be observed at the extrados symmetrically
with respect to the applied concentrated load.
A further parameter which strongly influences the ultimate carrying
capacity of the structure is the load position (x), particularly in the case
of masonry arch bridges. In the application reported in the following
the role of the position of the vertical load in the ultimate capacity of
the arch is investigated. Two values of the friction coefficient have been
considered, namelyμ= 0.6 andμ= 0.3.
The obtained results are summarized inFig. 17, where the ultimate
load (related to an ultimate conventional displacement equal to 25 mm)
is reported as a function of the normalised abscissa of the load position
considering one half of the arch. The obtained results show that the
minimum ultimate load is related to positions of the concentrated
vertical load close to the value of the normalised abscissa 0.3 for both
the investigated cases.
The collapse mechanisms associated to some significant positions of
the load are reported inTable 6, with the indication of the
## Table 6
Influence of the load position: collapse mechanisms.
x/Lμ= 0.3μ= 0.6
## 0.1
## F
u
= 98.42 kNF
u
= 219.99 kN
## 0.25
## F
u
= 56.90 kNF
u
= 83.46 kN
## 0.4
## F
u
= 59.82 kNF
u
= 82.58 kN
## 0.5
## F
u
= 69.47 kNF
u
= 150.52 kN
## (a)
## (
b)
Fig. 18.Influence of the tensile fracture energy: (a) mid-span load and (b)
quarter of span load.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 254

corresponding limit value. The cases corresponding to the higher fric-
tion coefficient show collapse mechanisms characterised by the occur-
rence of fourflexural hinges (with the exception of the case of central
load characterised byfive hinges). The cases corresponding to the lower
friction coefficient are all characterised byflexural or shear hinges
depending on the position of the load.
The arch behaviour has been also investigated considering different
values of tensile strength and fracture energy. Thefirst parametric in-
vestigation considers afixed value of tensile strength,
=f0.02MPa
t
## ,
and different fracture energy values between the limit cases of
## →G0
t
(brittle behaviour) and
## →∞G
t
(infinite ductility), for the mid-span
(Fig. 18a) and one-quarter span positions (Fig. 18b) of the load. The
influence of the tensile fracture energy has been assessed by considering
four different values (
=∞G0.01,0.05,0.1,  N/mm
t
). It can be observed
how the fracture energy affects the ultimate load of the arch although
maintaining a good ductility behaviour also for a low value of fracture
energy, in this latter case the ultimate load is close to the lower bound
provided by the limit analysis,Fig. 14.
The influence of the tensile strength has been investigated by con-
sidering the load scenarios for the values of the tensile strength
=f0,0.01,0.02,0.04MPa
t
and perfectly ductile behaviour
## →∞G
t
, the
results are reported inFig. 19. It can be observed how the tensile
strength strongly influences the ultimate load capacity of the arch in
both the load configurations.
## 5. Conclusions
In this paper a Discrete Macro-Element (DME) approach for the
assessment of the nonlinear behaviour of masonry arches is presented.
The method can be regarded as a discrete method in which each ele-
ment possesses an internal deformability and represents the corre-
sponding masonry element, at the macro-scale, according to a simpli-
fied kinematics. A single degree of freedom accounts for the internal
shear deformability, three further degrees of freedom describe the rigid
motion of each macro-element. Namely, each macro-element can be
assimilated to a hinged quadrilateral with an internal deformability and
contouring interfaces which govern the interaction with the adjacent
elements. The calibration of the model requires few parameters in order
to define the basic masonry mechanical properties. The equivalence
between the macro-masonry arch portion and the macro-element is
based on a very simplefibre calibration strategy that makes the inter-
pretation of the numerical results straightforward and unambiguous.
In spite of its simplicity and ability to limit the needed computa-
tional effort to perform numerical simulations, this approach appears to
be able to simulate the main in-plane failure mechanisms of masonry
arch structures, also in presence of irregular geometry layouts.
Several comparisons with experimental and benchmark numerical
results demonstrate the reliability and suitability of the model in the
evaluation of the bearing capacity of arched masonry structures.
The proposed methodology is also suitable to model retrofitting
techniques based on Fiber Reinforced Polymer strategies, as proposed
in [49]. It is worth to mention that geometric nonlinearity could sig-
nificantly affect the results, particularly with reference to the post-peak
behaviour in the nonlinear range. The adopted linear kinematics re-
presents a limit of the current formulation, the extension to a general
macro-element strategy, accounting for material and geometrical non-
linearities in curved geometry masonry structures, is currently a work
in progress.
## Acknowledgement
This research has been supported by the Italian Network of Seismic
Engineering University Laboratories (ReLUIS). This work is part of the
National Research Project“Advanced mechanical modelling of new
materials and structures for the solution of 2020 Horizon challenges”
(2017–2020), supported by MIUR, Grant No. 2015JW9NJT, Scientific
coordinator, prof. M. Di Paola, prot. n. 2015JW9NJT_017.
Appendix A. Supplementary material
Supplementary data associated with this article can be found, in the
online version, athttp://dx.doi.org/10.1016/j.engstruct.2018.04.006.
## References
[1] Huerta S. Galileo was wrong: the geometrical design of masonry arches. Nexus Netw
## J 2006;8(2):25–6.
[2] Gago AS, Alfaiate J, Lamas A. The effect of the infill in arched structures: Analytical
and numerical modelling. Eng Struct 2011;33(5):1450–8.
[3] Heyman J. The stone skeleton: structural engineering of masonry architecture.
## Cambridge University Press; 1995.
[4] Heyman J. On the rubber vaults of the middle ages, and other matters. Gaz Beaux-
## Arts 1968;71:177–88.
[5] Heyman J. The safety of masonry arches. Int J Mech Sci 1969;11(4):363–82. IN3-
## IN4,383-385.
[6] Heyman J. The estimation of the strength of masonry arches. Proc Inst Civ Eng
## 1980;69:921.
[7] Heyman J. The masonry arch. Chichester: Ellis Horwood; 1982.
[8] Caliò I, Greco A, Urso DD'. Free vibrations of spatial Timoshenko arches. J Sound
## Vib 2014;333(19):4543–61.
[9] Caliò I, Greco A, D’Urso D. Structural models for the evaluation of eigen-properties
in damaged spatial arches: a critical appraisal. Arch Appl Mech 2016;86:1853.
[10]Cannizzaro F, Greco A, Caddemi S, Caliò I. Closed form solutions of a multi-cracked
circular arch under static loads. Int J Solids Struct 2017;121:191–200.
[11]Caliò I, D'Urso D, Greco A. The influence of damage on the eigen-properties of
Timoshenko spatial arches. Comput Struct 2017;190:13–24.
[12]Cavicchi A, Gambarotta L. Collapse analysis of masonry bridges taking into account
arch-fill interaction. Eng Struct 2005;27(4):605–15.
[13]Thavalingam A, Bicanic N, Robinson JI, Ponniah DA. Computational framework for
discontinuous modelling of masonry arch bridges. Comput Struct
## 2001;79(19):1821–30.
[14]Lemos JV. Discrete element modelling of the seismic behaviour of stone masonry
arches. In: Pande GN, Middleton J, Kralj B, editors. Computer methods in structural
masonry—4. London: E & FN Spon; 1998. p. 220–7.
[15]Tóth AR, Orbán Z, Bagi K. Discrete element analysis of a stone masonry arch. Mech
## Res Commun 2009;36(4):469–80.
## (a)
## (b)
Fig. 19.Influence of the tensile strength: (a) mid-span load and (b) quarter of
span load.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 255

[16]Sarhosis V, Oliveira DV, Lemos JV, Lourenco PB. The effect of skew angle on the
mechanical behaviour of masonry arches. Mech Res Commun 2014;61:53–9.
[17]Rizzi E, Rusconi F, Cocchetti G. Analytical and numerical DDA analysis on the
collapse mode of circular masonry arches. Eng Struct 2014;60:241–57.
[18]Dimitri R, Tornabene F. A parametric investigation of the seismic capacity for
masonry arches and portals of different shapes. Eng Fail Anal 2015:1–34.
[19]Dimitri R, De Lorenzis L, Zavarise G. Numerical study on the dynamic behavior of
masonry columns and arches on buttresses with the discrete element method. Eng
## Struct 2011;33:3172–88.
[20]De Lorenzis L, Dimitri R, Ochsendorf J. Structural study of masonry buttresses: the
stepped form. ICE Proc–Struct Build 2012;165(9):499–521.
[21]De Lorenzis L, Dimitri R, Ochsendorf J. Structural study of masonry buttresses: the
trapezoidal form. ICE Proc–Struct Build 2012;165(9):483–98.
[22] Zhang Y, Macorini L, Izzuddin BA. Mesoscale partitioned analysis of brick-masonry
arches. Eng Struct 2016;124.http://dx.doi.org/10.1016/j.engstruct.2016.05.046.
## ISSN 0141-0296.
[23]Caliò I, Marletta M, Pantò B. A new discrete element model for the evaluation of the
seismic behaviour of unreinforced masonry buildings. Eng Struct 2012;40:327–38.
[24] Caddemi S, Caliò I, Cannizzaro F, Pantò B. A new computational strategy for the
seismic assessment of infilled frame structures. In: Proceedings of the 14th inter-
national conference on civil, structural and environmental engineering computing,
CC 2013, civil-comp proceedings; 2013.
[25]Caliò I, Pantò B. A macro-element modelling approach of Infilled Frame Structures.
## Comput Struct 2014;143:91–107.
[26]Pantò B, Cannizzaro F, Caddemi S, Caliò I. 3D macro-element modelling approach
for seismic assessment of historical masonry churches. Adv Eng Softw
## 2016;97:40–59.
[27]Zucchini A, Lourenço PB. A micro-mechanical model for the homogenisation of
masonry. Int J Solids Struct 2002;39(12):3233–55.
[28]Wu C, Hao H. Derivation of 3D masonry properties using numerical homogenization
technique. Int J Numer Meth Eng 2006;66(11):1717–37.
[29]Bacigalupo A, Gambarotta L. Computational two-scale homogenization of periodic
masonry: Characteristic lengths and dispersive waves. Comput Methods Appl Mech
## Eng 2012;213–216:16–28.
[30]Meguro K, Tagel-Din H. Applied element method for structural analysis: Theory and
application for linear materials. Struct Eng/Earthquake Eng 2000;17(1):21
## –35.
[31]Meguro
K, Tagel-Din H. Applied element method for simulation of nonlinear ma-
terials: theory and application for RC structures. Struct Eng/Earthquake Eng
## 2000;17(2):137–48.
[32]Meguro K, Tagel-Din H. Applied element simulation of RC structures under cyclic
loading. J Struct Eng 2001;127(11):1295–305.
[33]Mayorka P, Meguro K. Modeling Masonry Structures using the Applied Element
Method, Seisan Kenkyu. 55. Japan: Institute of Industrial Science, The University of
Tokyo; 2003. p. 123–6. 6, ISSN 1881-2058.
[34]Furukawa A, Kiyono J, Toki K. Proposal of a numerical simulation method for
elastic, failure and collapse behaviors of structures and its application to seismic
response analysis of masonry walls. J Disaster Res 2011;6(1):51–69.
[35] Nagashima F, Fumihito I.Application of RBSM to slipping problem of friction-type
joints. Memoirs of Faculty of Technology, Tokyo Metropolitan University, vol. 33;
- p. 3317–27.
[36]Casolo S. Modelling the out-of-plane seismic behaviour of masonry walls by rigid
elements. Earthquake Eng Struct Dyn 2000;29(12):1797–813.
[37]Casolo S. Modelling in-plane micro-structure of masonry walls by rigid elements. Int
## J Solids Struct 2004;41(13):3625–41.
[38]Dolatshahi KM, Aref AJ. Two-dimensional computational framework of meso-scale
rigid and line interface elements for masonry structures. Eng Struct
## 2011;33(12):3657–67.
[39] Turnsek V, Cacovic F. Some experimental result on the strength of brick masonry
walls. In: Proceedings of the 2nd international brick masonry conference; stoke-on-
trent; 1971. p. 149–56.
[40] HiStrA (Historical Structure Analysis) software. HISTRA s.r.l, Catania, Italy. Release
## 17.2.3, April 2015.http://www.grupposismica.it.
[41]Ramos LF, De Roeck G, Lourenço PB, Campos-Costac A. Damage identification on
arched masonry structures using ambient and random impact vibrations. Eng Struct
## 2010;32:146–62.
[42]Drosopoulos GA, Stavroulakis GE, Massalas CV. Limit analysis of a single span
masonry bridge with unilateral frictional contact interfaces. Eng Struct
## 2006;28:1864–73.
[43] Basilio I. Strengthening of arched masonry structures with composite materials. Ph.
D. Thesis. Portugal: University of Minho. Available from:www.civil.uminho.pt/
masonry; 2007.
[44] CSI analysis reference manual for SAP2000, Computers and Structures Inc.; 2007.
[45] Ramos LF. Damage identification on masonry structures based on vibration sig-
natures. Ph.D. Thesis. Portugal: University of Minho. Available from:www.civil.
uminho.pt/masonry; 2007.
[46]Pantò B, Cannizzaro F, Lourenço PB, Caliò I. Numerical and experimental validation
of a 3D macro-model for the in-plane and out-of-plane behavior of unreinforced
masonry walls. Int J Architectural Heritage 2017;11(7):946–64.
[47] Betti M, Drosopoulos GA, Stavroulakis GE. On the collapse analysis of single span
masonry/stone arch bridges withfillinteraction. In: Proceedings of the 5th inter-
national conference on arch bridges ARCH’07; 2007. p. 617–24.
[48] Cavicchi A, Gambarotta L. Load carrying capacity of masonry bridges: numerical
evaluation of the influence offill and spandrels. In: Proceedings of the 5th inter-
national conference on arch bridges ARCH’07; 2007. p. 609–16.
[49]Pantò B, Cannizzaro F, Caddemi S, Caliò I, Chácara C, Lourenço PB. Nonlinear
modelling of curved masonry structures after seismic retrofit through FRP re-
inforcing. Buildings 2017;7(3). art. no. 79.
F. Cannizzaro et al.
## Engineering Structures 168 (2018) 243–256
## 256