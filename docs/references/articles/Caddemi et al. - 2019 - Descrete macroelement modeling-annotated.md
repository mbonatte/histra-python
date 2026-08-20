

## Chapter 14
Descrete macroelement
modeling
## S. Caddemi, I. Calio
## `
## , F. Cannizzaro, B. Panto
## `
and D. Rapicavoli
Department of Civil Engineering and Architecture, University of Catania, Catania, Italy
## 14.1  Introduction
Simulation of the nonlinear behavior of masonry structures subjected to
earthquake excitations or extreme loadings is a complex computational issue
for which many numerical strategies characterized by different levels of
accuracy and efficiency have been proposed. Masonry is one of most ancient
construction materials and today represents a large part of existing and new
structures. However, the word “masonry” has to be intended as a composite
material obtained by the assemblage of individual units and mortars whose
property is different from the property of its components (
## Hilsdorf, 1969).
As a consequence, the word masonry itself refers to a great variability of
masonry materials characterized by different constituents, geometrical lay-
outs, and construction techniques. This huge variability makes it difficult to
define reliable numerical models and general constitutive laws suitable for
all masonry structures (
Lourenc ̧o et al., 1998; Asteris et al., 2014). Masonry
material provides its mechanical contribution also in mixed-masonry struc-
tures, like confined masonry and infilled frame structures; in these latter
cases, reliable numerical simulations also require nonlinear modeling of the
interaction of the different structural members contributing to the global
bearing capacity of the structural system (
Asteris et al., 2011; Calio
## `
and
## Panto
## `
## , 2014
## ).
Many significant examples of applications of the nonlinear FEM to
historical masonry buildings and churches are reported in the literature;
some of these studies consider masonry as a homogenized continuum at the
## 503
Numerical Modeling of Masonry and Historical Structures.
## DOI:
https://doi.org/10.1016/B978-0-08-102439-3.00014-2
Copyright©2019 Elsevier Ltd. All rights reserved.

macroscale (Mele et al., 2003; Betti and Vignoli, 2008, 2011; Araujo et al.,
2012; Lourenc ̧o et al., 2012; Barbieri et al., 2013; Milani and Valente,
## 2015
), other refined FE approaches are based on detailed simulations of units
and mortar as micromodeling (
Lofti and Shing, 1994; Anthoine, 1997;
Gambarotta and Lagomarsino, 1997; Lourenc ̧o and Rots, 1997; Berto et al.,
2002; Macorini and Izzuddin, 2011
). Much effort is made today in the link
between the micro- and macro-modeling approaches using homogenization
techniques that allow the use of continuum based approaches as the nonlin-
ear FEM simulation as well as macromodeling simplified strategies.
Nonlinear FEM approaches require the adoption of sophisticated constitu-
tive laws, huge computational costs as well as advanced skills in the model
implementation and in the interpretation of the numerical results. However,
practitioners need simple and efficient numerical tools, whose complexity
and computational demand are appropriate for practical engineering pur-
poses. For these reasons, in recent decades, many researchers have proposed
new efficient numerical methodologies for predicting the nonlinear seismic
behavior of Un Reinforced Masonry (URM) structures (
Brenchich et al.,
## 1998
;Magenes and Della Fontana, 1998;Kappos et al., 2002;Calio
## `
et al.,
## 2005
;Chen et al., 2008;Marques and Lourenc ̧o, 2011;Lagomarsino et al.,
## 2013
;Raka et al., 2015).Marques and Lourenc ̧o (2011)report a comparison
between different simplified approaches currently used in academic research
and engineering practice. A common limitation of the existing simplified
numerical strategies for URM structures, currently used by many practi-
tioners, is the basic assumption of in-plane behavior of masonry walls, mak-
ing these approaches less suitable for Historical Masonry Structures (HMSs),
in which the out-of-plane behavior strongly influences the seismic response.
An original alternative efficient approach is represented by the “rigid body
spring model”, specifically formulated with the aim of approximating the
macroscopic behavior of masonry walls with reduced degrees of freedom.
Some valuable applications of this approach are related to historical masonry
buildings (
Casolo and Pen
## ̃
a, 2007; Casolo and Sanjust, 2009; Valente and
## Milani, 2016
## ).
Among the simplified methods, the Equivalent Frame Model (EFM)
approach represents the most commonly adopted strategy and was implemen-
ted in several academic as well as commercial software environments.
Several numerical and experimental validations have been already reported
in the literature and different formulations have been proposed in the last
three decades. In the following, a more detailed description of the EFM
approach and its recent evolution is given, highlighting the advantages and
the few drawbacks of this simplified strategy. Subsequently, an alternative
macromodeling strategy for the simulation of the nonlinear behavior of
URM structures is presented. The approach is based on the concept of
504PART | IIModeling of unreinforced masonry

macroelement discretization (Calio
## `
et al., 2012a) and was conceived with the
aim of capturing the nonlinear behavior of an entire structure through an
assemblage of discrete macroelements characterized by different levels of
complexity, according to the role played in the global model. The basic ele-
ment was first developed for the simulation of the in-plane response of
masonry walls (
## Calio
## `
et al., 2005) and has been validated by several numeri-
cal and experimental tests (
Marques and Lourenc ̧o, 2011; Calio
## `
et al., 2012a;
## Panto
## `
et al., 2015
). The basic plane element can be represented through a
simple mechanical scheme comprised by an articulated quadrilateral with
four rigid edges and four hinged vertices connected by two diagonal nonlin-
ear links. The interaction between the macroelements is ruled by nonlinear
zero-thickness interfaces. This novel approach has also been successfully
applied for infilled frame structures (
## Calio
## `
et al., 2008; Caddemi et al., 2013;
## Calio
## `
and Panto
## `
, 2014; Marques and Lourenc ̧o, 2014
). In this latter case, the
infills are modeled by the macroelements, while the reinforced concrete
frames are modeled by concentrated-plasticity beam columns. The basic 2D
macroelement has been solely utilized for the simulation of the nonlinear
response of masonry walls in their own plane. To overcome this significant
restriction—common to several simplified approaches—a third dimension,
together with the relevant needed additional degrees of freedom, were intro-
duced in a 3D macroelement (
## Panto
## `
, 2007; Caddemi et al., 2014; Panto
## `
et al., 2017a
). The kinematics of the enriched 3D macroelement is governed
by seven Lagrangian parameters only and allows an efficient simulation of
both the in-plane and the out-of-plane response of masonry walls.
One of the advantages of the proposed macroelement strategy is related
to the strongly reduced computational cost, if compared to the traditional
nonlinear Finite Element Modeling (FEM). However, another benefit relies
on the adopted mechanical calibration strategy that, being based on a
straightforward fiber discretization, allows the use of simple uniaxial consti-
tutive laws and leads to an easy interpretation of the numerical results.
Based on the above issues, the proposed discrete macroelement method can
be considered not only a reliable numerical tool for academic research but
also an efficient practice-oriented approach for the nonlinear simulation of
masonry buildings.
However, many masonry monumental constructions are characterized by
the presence of structural elements with curved geometry, such as arches,
vaults, and domes, which require an efficient reliable simulation. For this
reason, a further enrichment of the proposed 3D macroelement, with a more
general shell macro element, was subsequently introduced (
## Calio
## ́
et al.,
2010; Cannizzaro, 2010; Caddemi et al., 2015; Cannizzaro et al., 2018
## ). The
latter shell macroelement was conceived as an extension of the spatial ele-
ment and currently represents the first macroelement proposed for curved
Descrete macroelement modelingChapter | 14505

masonry structures. Its nucleus is comprised by anirregulararticulated
quadrilateral, still characterized by four rigid layer edges, whose orientation
and size are now related to the shape of the element and to the thickness of
the modeled masonry portion. This more general macroelement strategy is
mainly used for the numerical simulation of the seismic behavior of HMSs,
masonry arch bridges and has been implemented into the software code
HiStrA (Historical Structures Analysis) (
## Calio
## `
et al., 2015), which simplifies
the modeling of historical structures by means of several wizard generation
tools, capable of managing complex curved geometries through to a powerful
parametric input.
In this chapter, a comprehensive review of the proposed discrete macroe-
lement strategy is discussed. The different proposed macroelements and their
capability to be applied for the structural assessment of masonry structures
are discussed with reference to some relevant cases. Numerical and experi-
mental validations are reported with reference to some benchmarks already
investigated in the literature. The low computational cost and the easiness in
the interpretation of the results make this method particularly suitable for the
engineering community, as well as for academic research on the seismic
assessment of cultural heritage buildings.
14.2  The equivalent frame models
A widely used model for the global analysis of masonry buildings—assum-
ing an in-plane response of masonry walls—is the so-called EFM. This
approach can be regarded as a macroelement strategy based on the assump-
tion that the out-of-plane response of the masonry walls is prevented and the
global behavior of the structure is ruled by the in-plane reactions of the
masonry walls that can horizontally interact through diaphragms. Following
the macroelement approach, each wall is idealized in several macroportion,
or structural components, to be represented by a suitable equivalent mechani-
cal model. In the EFM, it is generally assumed that in-plane damage can
occur on piers and spandrels while the other masonry portions are not sub-
jected to damage. Piers and spandrels are identified as the masonry portions
between horizontally and vertically aligned openings, respectively. In this
macroelement approach, the masonry portions susceptible to damage are
represented by equivalent nonlinear beams whose nonlinear behavior is cali-
brated for describing the nonlinear response of the corresponding masonry
panel. In
Fig. 14.1an example of the subdivision of a typical masonry wall
in piers, spandrels, and joint regions is shown; in the same figure, a geomet-
rical scheme of the corresponding equivalent frame is also represented.
Under this hypothesis the masonry portions connecting piers and spandrels
are considered damage prevented and are regarded as rigid links connecting
506PART | IIModeling of unreinforced masonry

the equivalent beams representating piers and spandrels. This practically ori-
ented approach leads to the definition of an equivalent frame for each plane
masonry wall; the spatial connection of the plane frames by means of rigid
or deformable diaphragms allows to obtain a spatial frame model representa-
tive of the global behavior of the overall building.
The first equivalent beam-based model can be attributed to
## Tomazevic
## (1978)
, which introduced the so-called POR method. In this pioneering ver-
sion of the EFM, each wall was idealized as a shear-type frame in which
only the columns, representing the masonry piers, were assumed as suscep-
tible to damage while both spandrels and connecting regions were assumed
as rigid zones exempt from damage. Initially, only the shear capacity of the
masonry piers had been considered,according to simplified elastic per-
fectly plastic constitutive laws. Thisvery simple EFM strategy, although
too approximate, had the advantage to recognize the need to perform non-
linear analyses for masonry buildings. The POR method was than improved
by considering shear and flexural collapse mechanisms for the masonry
FIGURE 14.1Equivalent frame modeling strategy. (A) Masonry wall geometrical layout; (B)
identification of piers, spandrels and regions assumed as rigid; (C) frame model superimposed to
the wall geometry; (D) equivalent frame model.
Descrete macroelement modelingChapter | 14507

piers, leading to the PORFLEX method (Braga and Dolce, 1982; Dolce,
## 1991
).  After  the  introduction  of  the  POR  method,  some  research
highlighted the need to enrich the model by introducing the possibility of
identifying the presence of damage in other structural components. Taking
inspiration from a seismic damage scenario on URM buildings, some
research groups observed that the in-plane damage in masonry walls is
mainly concentrated on piers and spandrels, while the masonry portion con-
necting these regions is rarely subjected to significant damage. In view of
this consideration, the shear-typemodel has been abandoned and new
EFMs proposed.
Magenes and Calvi (1996)introduced the SAM (simpli-
fied analysis of masonry) method, which was then further modified by
Magenes and Della Fontana (1998). In the SAM method, each plane wall is
represented by an equivalent frame where columns and beams represent
piers and spandrels respectively. Rigid offsets describe the joint panels in
which damage cannot occur. Many equivalent beam-based models (
## Kappos
et al., 2002; Roca et al., 2005; Penelis, 2006; Belmouden and Lestuzzi,
## 2009
) are based on the idealization ofthe structure as an assemblage of
piers as columns and spandrels as beamelements, connected by rigid links.
The main differences between thesemodels rely on rules adopted for the
definition of the equivalent frame and on the constitutive laws adopted for
the description of the nonlinear behavior of piers and spandrels. A widely
used EFM is implemented in the Tremuri software (
Lagomarsino et al.,
## 2013
), which has been validated experimentally and numerically, and
implements an original and versatilealgorithm for the pushover analysis,
suitable for assessing the nonlinear evolution of the lateral response of 3D
masonry buildings—including the deterioration of the base shear for
increasing lateral displacements after the attainment of peak strength.
Recently some equivalent beam-based models proposed the use of distrib-
uted plasticity beam elements (
Addessietal.,2015;Rakaetal.,2015)lead-
ing to a better description of the nonlinear flexural behavior associated
with a fiber discretization of the masonry.
Equivalent frame approaches represent a sleek and fast solution to assess
masonry buildings, whose main advantages are listed here:
1.The needed degrees of freedom to model an entire building is limited,
thus allowing to perform of nonlinear analyses with a reasonable compu-
tational burden when compared with FE approaches.
2.The main in-plane failure mechanisms of a masonry panel can be consid-
ered by means of ad-hoc constitutive laws.
3.A large part of masonry structures respects the hypothesis which this
methodology relies on.
4.The implementation of such approaches in general-purpose software
environments is possible.
508PART | IIModeling of unreinforced masonry

On the other hand, these approaches present some drawbacks that limit
their employability. In particular:
1.The definition of the equivalent frame is not always straightforward,
especially when the distribution of the openings on the masonry walls is
irregular.
2.The geometric inconsistency between a plane masonry portion and the
beam makes it difficult to simulate the interaction between reinforced
concrete or steel frame structures and adjacent masonry walls. This is the
case with confined masonry or infilled frame structures.
3.As in many macroelement approaches, the out-of-plane response is not
considered.
Many works investigated and validated the EFM, highlighting the differ-
ence between the approaches already proposed in the literature as well as the
advantages and limits of applicability, explored in the recent works of
Marques and Lourenc ̧o (2011),Raka et al. (2015),Quagliarini et al. (2017),
Siano et al. (2018).
14.3  A discrete macroelement strategy
Starting from pioneering work in 2004 (Calio
## `
et al., 2004), a research
group at the University of Catania proposed a new macroelement
method defined according to a unique approach within the framework
of a discrete element formulation strategy. Such an approach is based
on the subdivision of the structure under consideration in several macro-
portions; after homogenization of the mechanical properties of the com-
ponents  (mortar  and  units),  each  macroportion  is  regarded  as  an
equivalent continuum whose mechanical properties can be assumed as
isotropic or orthotropic depending on the masonry texture. The follow-
ing step is the discretization by means of a mesh of macroelements cho-
sen according to the macroportion that has to be modeled.
## Fig. 14.2
FIGURE 14.2Subdivision of a dome in macroportion to be represented by macroelements.
Descrete macroelement modelingChapter | 14509

shows a qualitative subdivision of adome by means of several macro-
portions that, according to a macroelement strategy, will be represented
by shell macroelements.
In this approach, each flexible macroelement interacts with the adjacent
elements through nonlinear distributed zero-thickness interfaces. The nonlin-
ear behavior of the structure is captured through an assemblage of macroele-
ments, characterized by different levels of complexity, according to the role
played by the global model. The degrees of freedom needed to describe the
macroelements’ kinematics are those strictly related to the rigid body motion
plus a single degree of freedom governing the element deformability. The
following subsections contain a brief description of the different macroele-
ments introduced so far.
14.4  The basic 2D macroelement
The basic 2D macroelement is a plane quadrangular element endowed by
four degrees of freedom (
Fig. 14.3A).
The 2D macroelement, first proposed in 2004 (
## Calio
## `
et al., 2004), was con-
ceived for the simulation of the nonlinear response of masonry walls in their
own plane (
Fig. 14.3B). The element can be regarded as an articulated quadri-
lateral of rigid beams connected by four hinges, leading to a kinematics gov-
erned by only four degrees of freedom. Zero-thickness interfaces govern the
interaction with the adjacent elements, while the element deformability is con-
veniently ruled by a single, diagonal nonlinear link. The kinematics of the
mechanical scheme, after a proper calibration procedure of the nonlinear links,
is capable of simulating the main in-plane collapse failure modes of a masonry
panel: flexural failure, diagonal shear failure, and sliding shear failure (
## Calio
## `
et al., 2012a
). Despite its simplicity, the assemblage of these elements
allows the simulation of the global nonlinear response of masonry buildings
FIGURE 14.3The 2D macroelement and its mechanical scheme. (A) Initial undeformed con-
figuration; (B) deformed configuration.
510PART | IIModeling of unreinforced masonry

(also in the presence of openings) allowing a geometrically consistent simula-
tion of the masonry walls in their own plane. Each macroelement exhibits
three degrees of freedom associated with the in-plane rigid body motion, plus
the additional degree of freedom, needed for the description of the in-plane
shear deformability. The deformations of the interfaces are related to the rela-
tive motion between corresponding panels; therefore, no further Lagrangian
parameter has to be introduced to describe their kinematics. The adopted
model has the advantage of interacting with the adjacent elements along the
entire perimeter, thus allowing the possibility of using different mesh discreti-
zations, as highlighted in the following paragraphs. The numerical approach
has been validated by several studies (
Marques and Lourenc ̧o, 2011)andit
has been implemented in the software 3DMacro (
## Calio
## `
et al., 2012b) currently
used for research and practical applications. The geometric consistency of the
elements also allows an efficient simulation of infilled frame structures;
Fig. 14.4reports an example of infilled frame model by means of a hybrid
approach in which the beams are modeled as frame elements and the infill is
modeled by means of mesh of plane macroelements.
14.4.1  The 3D macroelement
The 2D macroelement allows the simulation of a masonry wall in its own
plane but ignores the out-of-plane response. To overcome this significant
restriction, a third dimension, and the relevant needed additional degrees of
freedom were introduced in a 3D macroelement (
## Panto
## `
## , 2007; Caddemi
et al., 2014; Panto
## `
et al., 2017a
## ).
Fig. 14.5reports the 3D macroelement (Panto
## `
, 2007; Caddemi et al.,
## 2014; Panto
## `
et al., 2017a
) obtained as the extension to the space of the plane
element described in the previous paragraph. The kinematics of the spatial
macroelement is governed by seven degrees of freedom, able to describe the
in- and out-of-plane rigid body motions of the quadrilateral and the in-plane
shear deformability. The interaction of the spatial macroelement with
FIGURE 14.4Typical macroelement discretization of an infilled frame in presence of a central
door opening.
Descrete macroelement modelingChapter | 14511

the adjacent elements or the external supports is ruled by 3D interfaces.
Each 3D interface possessesmrows ofnorthogonal (i.e., perpendicular to
the planes of the interface) nonlinear links. Consequently, each interface is
discretized, similarly to what is done in classical fiber models, inm3nsub-
areas (
Fig. 14.5B). The 3D interfaces are endowed with additional shear-
sliding links (
Fig. 14.5A), required to control the in-plane and out-of-plane
sliding mechanisms and the torsion around the axis perpendicular to the
plane of the interface. The number of nonlinear links adopted in the 3D
interfaces is selected according to the desired level of accuracy of the nonlin-
ear response. A detailed description of the mechanical calibration of the spa-
tial macroelement and its numerical and experimental validation is reported
in
## Panto
## `
et al. (2017a). This model has also been applied for the simulation
of infilled frame structures, accounting for the in- and out-of-plane behavior
of the infills (
## Panto
## `
et al., 2018).
14.4.2  The shell macroelement for modeling curved geometry
The 3D macroelement (Panto
## `
et al., 2017a) allows the simulation of the in-
plane and out-of-plane behavior of plane masonry walls. However, historical
structures are often characterized by a curved geometry whose role in the
global and local response cannot be ignored. Aiming at modeling curved
geometry, a more general shell macroelement for modeling arches, vaults,
domes, and masonry arch bridges has been introduced. The shell macroele-
ment is characterized by four rigid layer edges whose orientation and dimen-
sion is now associated to the shape of the element and to the thickness of the
portion of structure to be modeled (
Fig. 14.6). The in-plane shear deformabil-
ity is still governed by a single degree of freedom related to a diagonal spring
placed along one of the diagonals of the quadrilateral. The plane interfaces
rule the interaction with adjacent elements or external supports. However, due
to the irregular geometry, these interfaces are in general skewed with respect
FIGURE 14.53D macroelement. (A) Simplified mechanical scheme; (B) a typical fiber discre-
tization of the element.
512PART | IIModeling of unreinforced masonry

to the average plane of the element. Curved surfaces are therefore modeled
under the assumption that the behavior of a continuously curved surfaces can
be adequately represented by flat macroelements. Each quadrilateral is geo-
metrically defined by the coordinates of its vertices, the four normal vectors to
the surface and the thicknesses at these points (
## Fig. 14.7).
The most significant features of the improved shell element are:
1.interfaces no longer orthogonal to the plane of the element, thus allowing
to follow the curved geometry of the structure;
2.thickness can be linearly variable at each interface;
3.shape of the element can be represented by a generic quadrangular
element.
Despite the complications, due to the curved geometry, the model keeps
the original simplicity and computational cost. Its kinematics is still ruled by
seven degrees of freedom (six rigid body motion degrees of freedom and one
associated with the in-plane shear deformability). The irregular geometry
implies that each link corresponds to a prismatic fiber, whose cross-sectional
area varies with a parabolic trend (
## Fig. 14.8).
FIGURE 14.7(A) Curved portion of masonry structures; (B) its flat discrete element
representation.
FIGURE 14.6Shell macroelement. (A) The orthogonal links of the interfaces; (B) the longitu-
dinal and the diagonal links.
Descrete macroelement modelingChapter | 14513

There are three nonlinear sliding links in each interface (Fig. 14.6B): one
along the axis of the interface (in-plane sliding link) and two orthogonal to
the axis and still lying on the plane of the interface (out-of-plane sliding
links). The calibration strategy follows the same philosophy of the spatial
regular model. Since those links have to simulate the occurrence of sliding
along the bed joints, their nonlinear behavior is closely affected by friction
phenomena and the yielding domain accounts for the influence of the normal
force acting on the interface. In the subdivision of an arbitrary shell into flat
elements, both triangular and quadrilateral elements should generally be used
## (see
Fig. 14.2). The triangular elements are assumed to be rigid in their own
plane and are therefore characterized by six degrees of freedom only. A
detailed description of the mechanical characterization of this nontrivial shell
discrete element is outside the purpose of the present chapter.
14.5  Mechanical characterization strategy of the proposed
macroelement approach
According to the proposed strategy, each macroelement must be representa-
tive of the corresponding finite portion of masonry wall, cut out by plane
sections located at the edges of the element. The formulation follows a
phenomenological description of the mechanical behavior of a masonry por-
tion in which the zero-thickness interfaces rule the membrane-flexural
response and the shear-sliding behavior of adjacent elements, while the in-
plane shear element deformability is related to the angular distortion of the
articulated  quadrilateral.  The  mechanical  characterization  of  the  zero-
thickness interfaces here is performed following a straightforward fiber cali-
bration procedure, while the shear element deformability is calibrated
through a mechanical equivalence with the reference geometric-consistent
continuous model. The interface nonlinear links can be distinguished as
orthogonal links and shear-sliding links. In the following paragraphs, the
main steps needed for the calibration procedure are described with reference
to each group of nonlinear links.
FIGURE 14.8Fiber discretization of the shell macroelement.
514PART | IIModeling of unreinforced masonry

14.5.1  Calibration of the nonlinear links orthogonal to the
interfaces
The orthogonal nonlinear links incorporate the mechanical properties of the
represented element assuming masonry as an orthotropic homogeneous
medium. Each orthogonal link encompasses the nonlinear behavior of the
corresponding fiber along a given material direction (
Fig. 14.5B). With a
regular 3D macroelement, each link is calibrated, assuming that the uniform
masonry strip is a homogeneous inelastic material, and can also consider
cyclic behavior governed by fracture energy values for the tensile and com-
pressive response,G
t
andG
c
, respectively, and follows different postelastic
branch laws (
## Ch
## ́
acara et al., 2018).
For clarity, reference is made to a single orthotropic panel under mono-
tonic loadings (
Fig. 14.9). In this case, the flexural behavior of the masonry
panel is characterized by different mechanical properties along the two fun-
damental directions.E
h
andE
v
are the Young’s moduli of the homogenized
orthotropic masonry medium;σ
ch
## ,σ
th
, andσ
cv
## ,σ
tv
are the corresponding
compressive and tensile maximum stresses,G
ch
## ,G
th
, andG
cv
## ,G
tv
are the
fracture energies in compression and tension, as shown in
Fig. 14.9A.
Consistently with the adopted fiber calibration strategy, the flexural stiffness
calibration of the panel is simply obtained by assigning to each link the axial
stiffness of the corresponding masonry strip. Each masonry strip is identified
by its influence area, and the half-dimension of the panel in the direction
perpendicular to the interface (
Fig. 14.5B). The initial stiffnessK, the com-
pressive and tensile yielding strengths,f
c
andf
t
, and the corresponding ulti-
mate displacements,u
c
andu
t
(under the simplified hypothesis of a
## E
v
## G
t
h
## H
## 2
σ
th
## G
cv
## B
## 2
σ
cv
## B
σ
ch
λ
h
## E
h
λ
v
## G
tv
k
h
, f
th
, f
ch
, u
th
## ,u
ch
k
v
, f
tv
, f
cv
, u
tv
, u
cv
## H
σ
tv
## G
ch
u
u
## (A)(B)
FIGURE 14.9Mechanical characterization of an orthotropic masonry panel: (A) constitutive
laws; (B) calibration of the orthogonal links (
## Panto
## `
et al., 2017a).
Descrete macroelement modelingChapter | 14515

rectangular shape of the panel and linear softening) of the links relative to
the horizontal and vertical interfaces are reported in
Table 14.1as a function
of the mechanical and geometrical properties of the masonry panel.
## In
Table 14.1BandHare the length and the height of the panel,λ
h
and
λ
v
are the in-plane distances between the springs along the interfaces
arranged according to the two fundamental directions, andλ
s
is the out-of-
plane distance between the rows of links, as shown in
Fig. 14.9B.
14.5.2  Calibration of the nonlinear links along the interfaces
The nonlinear links, lying along the interface and denoted as shear-sliding
links, govern the torsional and shear-sliding behavior along the interfaces. In
the discretization shown here, one single link is considered for the in-plane
model (
Fig. 14.3) while three nonlinear links are considered for the spatial
models (
Figs. 14.5 and 14.6), this being the minimum required to obtain the
possible masonry failure modes (
## Panto
## `
et al., 2017a). A single in-plane
shear-sliding spring, governing the in-plane sliding of the element along the
interface is calibrated according to a rigid-plastic MohrCoulomb law. The
out-of-plane shear deformability is ruled by two parallel links, which take
care of the out-of-plane sliding behavior and the torsional elastic and inelas-
tic response of connected, adjacent panels. The two out-of-plane shear-
sliding nonlinear links are required to control the out-of-plane sliding
mechanisms as well as the torsion around the axis perpendicular to the plane
of the interface. With the goal of maintaining a simple fiber calibration
approach, the out-of-plane shear deformability of each link connecting two
adjacent panels is calibrated according to their influence volumes. Referring
to two identical adjacent macroelements, with thicknesss, widthBand
heightH, shear modulusG, cohesionc, and friction coefficientμ
s
, the cali-
bration procedure is summarized providing the main parameters that govern
the mechanical behavior of the sliding links (
## Table 14.2).
Once the elastic shear out-of-plane stiffness has been assigned, accord-
ingtotheformulasreportedin
Table 14.2, the relative distancedbetween
TABLE 14.1Mechanical calibration of the orthogonallinksfor a rectangular
panel.
DirectionKf
c
f
t
u
c
u
t
## Horizontal
## K
h
## 52
## E
h
λ
h
λ
s
## B
f
ch
## 5σ
ch
λ
h
λ
s
f
th
## 5σ
th
λ
h
λ
s
u
ch
## 52
## G
ch
σ
ch
u
th
## 52
## G
th
σ
th
## Vertical
## K
v
## 52
## E
v
λ
v
λ
s
## H
f
cv
## 5σ
cv
λ
v
λ
s
f
tv
## 5σ
tv
λ
v
λ
s
u
cv
## 52
## G
cv
σ
cv
u
t2
## 52
## G
tv
σ
tv
516PART | IIModeling of unreinforced masonry

the two out-of-plane sliding links has to be set according to an equivalence
with the corresponding elastic continuum in terms of torsional behavior
## (
## Panto
## `
et al., 2017a). Aiming at obtaining a suitable torsional elastic cali-
bration, although maintaining a simplified calibration strategy, the distance
dbetween the two links is simply obtained considering that the torsional
elastic stiffness of the corresponding geometrical consistent continuous
modelisequivalenttothatassociated to the discrete system. The yielding
strength of each link is associated with the current contact areaAof the
interface and to the current axial forceNassociated to the orthogonal links
of the interface.
14.5.3  Calibration of the diagonal link
The diagonal shear failure (collapse of the panel) is related to a single
degree of freedom; this allows to associate the shear nonlinear response to
a single diagonal nonlinear link. Many different yielding criteria, strongly
dependent on the compressive stresses in the wall, can be adopted to
account for the shear capacity. In the elastic range, the diagonal shear link
is calibrated by imposing an energy equivalence between the articulated
quadrilateral, ruled by the diagonal spring, and a continuous reference
elastic model. The yielding forces areassociated with the limits of tensile
or compressive stresses in the reference continuous model, while the
postelastic  behavior  is  ruled  by  a  suitable  constitutive  law.  The
MohrCoulomb law or the TurnsekCacovic (1970) law can generally be
adopted for the calibration of the diagonal link, although any constitutive
law can also be considered.
14.6  Experimental and numerical validation of the proposed
macroelement strategy
In this section, the capability of the proposed discrete macroelement
approach to simulate the nonlinear response of masonry structures is
TABLE 14.2Mechanical calibration of the shear-sliding links for a
rectangular panel.
## Directionk
s
df
sy
In-planeN
f
sy
## 5c1μ
s
## N
## 
## A
## Out-of-plane
k
s
## 5
## 1
## 2
GBs
## H
d52s
ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi
## 1
## 3
## 20;21
s
## B
## 12
s
## 4
## 12B
## 4
## 
q
f
sy
## 5
## 1
## 2
c1μ
s
## N
## 
## A
Descrete macroelement modelingChapter | 14517

investigated. The method is validatedby comparing the numerical results
with those obtained by other numerical approaches or by experiments
already available in the literature.
14.6.1  The 2D macroelement
The first validation is relative to the case of a single 2D macroelement,
which was investigated by a comparison of the proposed approach (
## Panto
## `
et al., 2015
) and an EFM, combined with a fiber section model recently pro-
posed in
Raka et al. (2015). The panel is restrained at its base and at its top.
Initially the panel is subjected to a force-controlled application of a vertical
load, then a displacement-controlled analysis, with an increasing horizontal
displacement at the top of the panel, is applied. The panel is characterized
by the thicknesst50.6 m, the widthw53 m, and the heighth52 m. The
adopted mechanical properties are reported in
Table 14.3; for this first exam-
ple, the shear failure is considered inhibited.
The results are compared with those obtained by an equivalent frame
approach on a direct fiber section analysis (
Raka et al., 2015).
Several analyses were performed for different levels of the axial load; in
Fig. 14.10Athe ultimate bending moment of the base section is reported ver-
sus the considered axial load. The capability of the model to describe the
axial-flexural response of a masonry wall section is assessed by comparing
theMNdominium of the base section with data obtained following the
closed-form expression reported in the Italian building code (
## NTC, 2008). A
second example of a single panel is reported in
Fig. 14.10B. The ultimate
load obtained with the equivalent frame fiber model, as proposed by
## Raka
et al. (2015)
, and the proposed macroelement are compared when either only
the flexural or only shear mechanisms are considered. The two numerical
models provide very close results in terms of ultimate loads, and they are
consistent with the values suggested by the Italian code (
## NTC, 2008).
The plane macroelement can also be adopted for modeling infilled frame
structures. In the latter case a hybrid approach is applied: the surrounding
frame is modeled using lumped plasticity beamcolumn elements while
the nonlinear response of the infill is modeled by means of the plane
TABLE 14.3Mechanical properties adopted for the masonry.
G(MPa)E(MPa)ρ(kN/m
## 3
## )σ
c
(MPa)σ
t
(MPa)f
v0
(MPa)
## 230870191.00.10.4
518PART | IIModeling of unreinforced masonry

macroelement, already described in the previous section. The frame element
interacts with the masonry panels by means of nonlinear-links distribution
along discrete interfaces. Each interface is constituted byntransversal non-
linear links and a single longitudinal nonlinear link. The flexural interaction
between the panel and an adjacent beam is governed by the four degrees of
freedom of the beam associated to its two ends and by theninternal degrees
of freedom associated to the links of the interface. For a more accurate eval-
uation of the nonlinear behavior of the frame element, it has been assumed
that plastic hinges can occur in each sub-beam element between two nonlin-
ear transversal links. This latter assumption provides a reliable frame element
model as it can embed plastic hinges at different positions and is consistent
with the adopted level of discretization for the infill interface.
An experimental validation of the 2D macroelement, implemented in the
software 3DMacro (
## Calio
## `
et al., 2012b) has been provided byMarques and
## Lourenc ̧o (2014)
with reference to a three-dimensional building prototype.
## 0
## 100
## 200
## 300
## 400
## 500
## 600
## 700
## 800
## 0400800120016002000
## M
(KNm)
## N (KN)
3DMacro model
Fiber approach
## Closed-form
## 0
## 100
## 200
## 300
## 400
## 500
## 600
## 700
## 0100200300400500600700800900
Base shear (kN)
N (kN)
Shear failure fiber model
Flexure failure fiber model
Shear failure 3DMacro model
Flexure failure 3DMacro model
## (A)
## (B)
FIGURE 14.10Interaction diagrams: (A) MN; (B) VN(Panto
## `
et al., 2015).
Descrete macroelement modelingChapter | 14519

The experimental campaign was carried out at Centro peruano japones de
Investigaciones Sismicas y MItigacion de Desastres (CISMID) research cen-
ter in Peru (
Zavala et al., 2004) on a two story building with an irregular
plan,  representative  of  a  typical  existing  residential  houses  in  Peru
## (
Fig. 14.11AC). The tests were performed under quasistatic cyclic loads,
applied through two actuators located at the two slabs, used to induce a con-
stant load pattern to the structure proportional to the building height. In
Fig. 14.11B, the comparison between numerical pushover curve (dotted
curve) and the experimental results is reported, while
Fig. 14.11Cshows the
damage scenario of the “south” wall at the last step of the analysis, a detailed
comparison is reported in
Marques and Lourenc ̧o (2014).
14.6.2  The 3D macroelement
An extensive numerical validation of the model on single walls with and
without openings was recently carried out by
## Panto
## `
et al. (2017a)considering
masonry panels loaded out-of-plane with different geometries and boundary
conditions. Applications of the model at a mesoscale for the out-of-plane
behaviors of masonry prototypes can be found in
Cannizzaro and Lourenc ̧o
## (2017)
. The numerical applications here reported refer to a real scale simula-
tion of a prototype building representative of a structural typology popular in
Portugal between the end of 19th century and the beginning of the 20th cen-
tury. This typology, known as “Gaioleiro” buildings, corresponds to tall
structures, usually with six stories, in which walls are made of rubble
masonry and lime mortar, and the horizontal diaphragms are timber floors
and roofs. A four-story building with a timber roof and blind wall was inves-
tigated in the work conducted by
Mendes and Lourenc ̧o (2009)andMendes
## (2012)
. Such a building was built in 1:3 scale and subsequently tested on a
shaking table at Laboratorio Nacional de Engenharia Civil (LNEC),
## Mendes
FIGURE 14.11Experimental validation of the 2D macroelement for a prototype building
## (
Marques and Lourenc ̧o, 2014): (A) numerical model, (B) comparison in terms of capacity
curve; (C) damage scenario at collapse of the south wall.
520PART | IIModeling of unreinforced masonry

et al. (2014). Details on the geometry can be found inMendes (2012).
The prototype was studied by means of an advanced FE model implemented
in the software DIANA, conducting static and dynamic nonlinear analyses.
The 3D macroelement method has been applied by using the software
HiStrA (
## Calio
## `
et al., 2015) in which the proposed macroelement strategy was
implemented. The mechanical properties here assumed are reported in
Table 14.4and were determined consistently with the data proposed by
## Mendes (2012).
## A
## Turn
## ˇ
sek and
## ˇ
## Ca
## ˇ
covi
## ˇ
c (1970)yielding criterion was assumed for the
diagonal shear behavior characterized by a perfectly postelastic behavior
until a transition driftγ
t
, assumed equal to 0.6%, with a subsequent linear
softening branch till the achievement of a limit driftγ
u
equal to 1.5%. The
numerical model consists of 704 elements (corresponding to an average
mesh size equal to 1.1 m) with a total amount of degrees of freedom equal to
5568 (the FE model is characterized by 75,880 degrees of freedom;
## Mendes,
## 2012
). The structure was initially loaded with the self weight and then sub-
jected to horizontal mass proportional load distributions along the two main
directions of the building, namely parallel and perpendicular to the fac ̧ade.
The target displacements for the two analyses were set according to the ulti-
mate displacements achieved in FE model. The results reported in
## Fig. 14.12
show the two capacity curves obtained from the numerical simulations. In
this figure, the horizontal top displacement at a monitored node versus the
base shear coefficient are reported along the horizontal and vertical axes,
respectively. The monitored node corresponds to the middle point of the top
wall loaded in the out-of-plane direction, whereas the base shear coefficient
was computed as the base shear along the load direction normalized by the
self weight. As expected, the direction parallel to the fac ̧ade is weaker than
the perpendicular one (peak base shear coefficient equal to 0.11 vs 0.40).
Despite this, it presents a much more ductile behavior (ultimate displacement
equal to 200 mm vs 40 mm).
## In
Fig. 14.13, the deformed configurations associated with the peak load
and ultimate displacement are plotted with their corresponding damage pat-
terns for the analysis in the weakest direction parallel to the main fac ̧ade.
Fig. 14.13Aillustrates the damage pattern associated with the peak load
which is mainly characterized by the failure of spandrels in the first two
TABLE 14.4Mechanical properties adopted in the numerical model.
E(MPa)σ
t
(MPa)G
t
(N/mm)σ
c
(MPa)G
c
(N/mm)G(MPa)γ
t
## (%)γ
u
## (%)
## 10000.10.051001.64170.61.5
Descrete macroelement modelingChapter | 14521

FIGURE 14.13Damage pattern at (A) the peak load and (B) at collapse for the analyses along
the direction parallel to the fac ̧ade (
Caddemi et al., 2018).
## –0.02
## 0.00
## 0.02
## 0.04
## 0.06
## 0.08
## 0.10
## 0.12
## (A)
## (B)
## 050100150200
Base shear coefficient
Top displacement  (mm)
## DIANA
HiStrA
## –0.05
## 0.00
## 0.05
## 0.10
## 0.15
## 0.20
## 0.25
## 0.30
## 0.35
## 0.40
## 0.45
## 0.50
Base shear coefficient
Top displacement  (mm)
## DIANA
HiStrA
## 0 1020304050
FIGURE 14.12Numerical validation of the 3D macroelement through a comparison with FE
results for a Gaioleiro prototype buildings (
Caddemi et al., 2018). Capacity curves along the
directions (A) parallel and (B) orthogonal to the fac ̧ade.
522PART | IIModeling of unreinforced masonry

stories. The damage pattern associated with the ultimate displacement is
depicted in
Fig. 14.13B. In this case, it is observed that the spandrels of the
upper stories present significant damage. In addition, this damage pattern
was also characterized by rocking at the base of the piers.
The comparison with the FE model shows good agreement of damage
patterns. In the direction parallel to the fac ̧ade, the damage concentrates pro-
gressively in the spandrels, from the lower to the upper stories, leading to a
final damage pattern in which the overall collapse mechanism involves all
the stories.
14.6.3  The shell macroelement
The proposed macroelement approach was implemented in the HiStrA
software, specifically devoted to historical structure analyses. The soft-
ware is able to model typical masonry monumental structures with the aid
of a graphical user interface that facilitates the input of the geometry and
of the mechanical properties of the materials of the structure through the
processing of a CAD drawing and the help of several generations of wiz-
ard tools. In
## Panto
## `
et al. (2016), with the aim to provide a numerical vali-
dation for a full scale structure. The approach has been applied to an
historical basilica church, characterized by the presence of arches on
masonry walls and masonry columns.A similar application was reported
in
## Panto
## `
et al. (2017b). In this section, the capability of the shell macroele-
ment to simulate the behavior of typical spatial curved masonry element
structures is investigated.
The applications discussed in the following section aim at validating
the model through comparison with experimental and numerical methods.
The case reported is relative to a brick masonry spherical dome with a
central hole tested by
Foraboschi (2006). The dome was subjected to an
incremental vertical load along the edge of the central hole. Details on the
experimental layout and on the mechanical properties can be found in
Foraboschi (2006). The numerical model implemented to simulate the
experimental tests consists of 544 quadrangular elements (17 along meri-
dians and 32 along parallels), which correspond to a total number of
degrees of freedom equal to 3808. Regarding the membrane fiber discreti-
zation, a maximum distance of the orthogonal nonlinear links equal to
5 cm along the parallels and 1.5 cm through the thickness of the dome
were set, respectively. In the performed nonlinear static analysis, the
model was subjected first to its self-weight, then to the external vertical
load applied on the annulus of quadrilateral elements sited around the
hole. The mechanical properties employed in the numerical simulations,
reported in
Table 14.5, were deduced by the simulations already reported
in the literature (
Milani et al., 2008; Milani and Tralli, 2012). The elastic
properties of the masonry are represented by the Young’s modulus (E)and
Descrete macroelement modelingChapter | 14523

the shear Poisson’s coefficient (ν). The sliding shear failure is ruled by the
cohesion (c) and the friction factor (μ). The diagonal shear behavior is
considered elastic.
## In
Fig. 14.14, the results of the nonlinear static analysis, expressed in
terms of deformed shape and damage pattern at collapse, were compared to
those already available in the literature. Namely,
Fig. 14.14Creports the ver-
tical top displacement as a function of the vertical load. The proposed model
correctly predicts the initial stiffness and the ultimate load of the structure,
TABLE 14.5Mechanical properties adopted in the numerical model.
E(MPa)σ
t
(MPa)σ
c
(MPa)c(MPa)μνγ(kN/m
## 3
## )
## 8500.071.90.120.370.2519
## (A)
## (C)
Base reaction (kN)
## 0
## 10
## 20
## 30
## 40
## 50
## 60
## 0
## 1
Top displacement (mm)
## 234
DSM model
QP model
## HISTRA
## 5
## Experiment
DIANA homogeneous
DIANA heterogeneous
Milani (limit analysis)
## (B)
FIGURE 14.14Hemispherical dome (Caddemi et al., 2015): (A) failure mechanism repre-
sented in half dome; (B) damage inelastic distribution expressed in gray scale; (C) load displace-
ment curves.
524PART | IIModeling of unreinforced masonry

and it is in good agreement with the available numerical results throughout
all phases of the experiment.
## In
Fig. 14.14A and B, the failure mechanism and the corresponding dam-
age scenario at the incipient collapse condition, obtained by the numerical
model implemented in HiStrA (
## Calio
## `
et al., 2015), are reported. Additional
details of the comparison can be found in
Caddemi et al. (2015).
14.6.4  Application to masonry arch bridges
A further structural typology to which the proposed approach was applied is
represented by masonry arch bridges. Such structures represent a large part
of the railway and road infrastructures of many countries and embeds very
specific structural features to which the proposed approach was adapted,
such as, the curved geometry and the 3D structural response. In order to
reduce the needed effort for the implementation of the numerical model of a
multiarch masonry bridge, a parametric input tool was developed considering
both the complex geometry (e.g., the presence of backfill layers or the pres-
ence of tapered piers) and the automatic generation of load combinations,
considering the presence of a roving vehicle load (
Caddemi et al., 2019). A
comparison on the results obtained on a five arches railway bridge over
Esino Torrent (Italy) is here briefly summarized. The results obtained with
the proposed approach were validated in the nonlinear field with those
obtained with a classic nonlinear FEM approach (
FEA Ltd., 2018). The
adopted mechanical properties are summarized in
Table 14.6, differentiated
according to the structural components groups, considering the elastic modu-
lusE, the shear modulusG, and the specific weightw. Tensilef
t
and com-
pressivef
c
strengths of the masonry were related to a linear softening
behavior governed by the corresponding fracture energiesG
ft
andG
fc
.The
shear diagonal behavior is associated with a MohrCoulomb domain charac-
terized by a shear strengthτ
## 0
and a friction coefficientμ50.5. The two
numerical models were subjected to a pushdown nonlinear analysis corre-
sponding to a nonsymmetric vehicle load arrangement (see
## Fig. 14.15). The
proposed approach drastically limits the required degrees of freedom (12,080
vs 349,362 in the FE model). Line loads were applied to simulate the
presence of vehicles, and their intensity was magnified until the failure of the
bridge. A comparison of the two models in terms of capacity curves, by moni-
toring the displacement of the top of the second arch, is shown in
Fig. 14.16A.
While the corresponding damage patterns are shown in
Fig. 14.16B,C.A
strong agreement between the two models is encountered considering the dis-
placements of each of the five arches. The observed damage patterns of the
two numerical models are similar as well, with significant vertical cracks on
the first two piers and a spread damage on the arches.
Descrete macroelement modelingChapter | 14525

## TABLE 14.6
Mechanical properties adopted for the masonry bridge.
## Elements
f
m
(MPa)
τ
## 0
(MPa)
## E
(MPa)
## G
(MPa)
f
t
(MPa)
## G
ft
(MPa)
## G
fc
(MPa)
w
(kN/m
## 3
## )
Abutment, pier, spandrel wall    5.8
## 0.4
## 2060
## 860
## 0.12
## 0.02
## 100
## 22
Masonry arches
## 2.6
## 0.3
## 1200
## 500
## 0.12
## 0.02
## 100
## 18
Backing, fill material, ballast
## 1.1
## 0.05
## 700
## 290
## 0.05
## N
## 100
## 19

FIGURE 14.15Railway bridge (Caddemi et al., 2019): (A) layout of the applied loads and
numerical models according to (B) proposed and (C) the FE approaches.
FIGURE 14.16Comparison in terms of (A) capacity curves and damage pattern at collapse
according to (B) proposed and (C) the FE approaches.
Descrete macroelement modelingChapter | 14527

14.7  Summary and conclusions
In this chapter, a numerical strategy focused on simulating the nonlinear
behavior of masonry structures is presented. The proposed numerical model,
which belongs to the framework of the simplified models, is based on a sim-
ple mechanical scheme that consists of a hinged quadrilateral, endowed with
a diagonal link to govern the in-plane diagonal shear behavior, and contour-
ing interfaces that rule the interaction with contiguous elements.
The proposed approach appears to be a fair compromise between over-
simplified models (e.g. EFMs) and accurate models based on cumbersome
strategies, which require an expert interpretation of the results. The basic
model, originally conceived for the simulation of masonry walls loaded in
their own plane, was repeatedly upgraded, progressively increasing the struc-
tural typologies that the proposed strategy is able to model. Within the scope
of the numerical simulation of ordinary buildings with box behavior (the
out-of-plane behavior is considered inhibited), interaction with frames con-
touring a masonry panel was enabled, thus allowing the numerical simulation
of both URM and infilled masonry structures.
With the goal of accurate numerical modeling of HMS, two further
upgrades were considered. First, theout-of-plane degrees of freedom were
enabled to assess the out-of-plane behavior of masonry walls. Then, a fur-
ther improvement allowed simulating masonry structures with a curved
geometry. Finally, by ruling the interaction between structural elements in
correlation with their intersections,full nonlinear simulations of large his-
torical masonry constructions were performed. The progressive improve-
ments were obtained by simply extending the calibration procedure of the
links according to the different peculiarities of the model at the various
stages of complexity. However, the philosophy of the model was kept the
same for all contemplated advances of the model; that is, the calibration is
always straightforward and based on the same concepts. Some simple vali-
dations of the model were presented consistently with each of the described
stage. The results show that the proposed strategy appears to be reliable in
all the considered cases and that it represents an original approach to the
nonlinear assessment of ordinary masonry buildings, historical and monu-
mental structures.
## References
Addessi, D., Liberatore, D., Masiani, R., 2015. Force-based beam finite element (FE) for the
pushover analysis of masonry buildings. Int. J. Architect. Herit. 9 (3), 231243.
Anthoine, A., 1997. Homogenisation of periodic masonry: plane stress, generalised plane strain
or 3D modelling? Commun. Numer. Methods Eng. 13, 319326. Available from:
https://
doi.org/10.1002/(SICI)1099-0887(199705)13:5,319::AID-CNM55.3.3.CO;2-J
## .
528PART | IIModeling of unreinforced masonry

Araujo, A., Lourenc ̧o, P.B., Oliveira, D., Leite, J., 2012. Seismic assessment of St James Church
by means of pushover analysisbefore and after the New Zealand earthquake. Open Civil
Eng. J. 6, 160172. Available from:
https://doi.org/10.2174/1874149501206010160.
Asteris, P.G., Antoniou, S.T., Sophianopoulos, D., Chrysostomou, C.Z., 2011. Mathematical
macromodeling of infilled frames: state of the art. J. Struct. Eng. 137, 15081517.
Available from:
https://doi.org/10.1061/(ASCE)ST.1943-541X.0000384.
Asteris, P.G., Chronopoulos, M.P., Chrysostomou, C.Z., Varum, H., Plevris, V., Kyriakides,
N., et al., 2014. Seismic vulnerability assessment of historical masonry structural sys-
tems.  Eng.  Struct.  62-63,  118134.  Available  from:
https://doi.org/10.1016/j.
engstruct.2014.01.031
## .
Barbieri, G., Biolzi, L., Bocciarelli, M., Fregonese, L., Frigeri, A., 2013. Assessing the seismic
vulnerability of a historical building. Eng. Struct. 57, 523535. Available from:
https://doi.
org/10.1016/j.engstruct.2013.09.045
## .
Belmouden, Y., Lestuzzi, P., 2009. An equivalent frame model for seismic analysis of masonry
and reinforced concrete buildings. Constr. Build. Mater. 23 (1), 4053.
Berto, L., Saetta, A., Scotta, R., Vitaliani, R., 2002. Orthotropic damage model for masonry
structures. Int. J. Numer. Methods Eng. 55, 127157. Available from:
https://doi.org/
## 10.1002/nme.495
## .
Betti, M., Vignoli, A., 2011. Numerical assessment of the static and seismic behaviour of the
basilica of Santa Maria all’Impruneta (Italy). Constr. Build. Mater. 25, 43084324.
Available from:
https://doi.org/10.1016/j.conbuildmat.2010.12.028.
Betti, M., Vignoli, A., 2008. Assessment of seismic resistance of a basilica-type church under
earthquake loading: modelling and analysis. Adv. Eng. Soft. 39, 258283. Available from:
https://doi.org/10.1016/j.advengsoft.2007.01.004.
Braga, F., Dolce, M., 1982. ‘Un metodo per l’analisi di edifici multipiano in muratura antisismi-
ci. In: Proc. of the 6th I.B.MA.CInternational Brick Masonry Conference, Rome.
Brenchich, G., Gambarotta, L., Lagomarsino, S., 1998. A macro-element approach to the three-
dimensional seismic analysis of masonry buildings. In: Proceedings of 11th European
Conference on Earthquake Engineering. A. A. Balkema, Paris, Rotterdam, p. 602.
## Caddemi, S., Calio
## `
## , I., Cannizzaro, F., Panto
## `
, B., 2013. A new computational strategy for the
seismic assessment of infilled frame structures. In: Topping, B.H.V., Iv
## ́
anyi, P. (Eds.),
Proceedings  of  the  Fourteenth  International  Conference  on  Civil,  Structural  and
Environmental Engineering Computing. Civil-Comp Press, Stirlingshire, Paper 77.
## Caddemi, S., Calio
## `
## , I., Cannizzaro, F., Panto
## `
, B., 2014. The seismic assessment of historical
masonry structures. In: Topping, B.H.V., Iv
## ́
anyi, P. (Eds.), Proceedings of the Twelfth
International Conference on Computational Structures Technology. Civil-Comp Press,
## Stirlingshire, Paper 78.
## Caddemi, S., Calio
## `
## , I., Cannizzaro, F., Occhipinti, G., Panto
## `
, B., 2015. A parsimonious discrete
model for the seismic assessment of monumental structures. In: Kruis, J., Tsompanakis, Y.,
Topping, B.H.V. (Eds.), Proceedings of the Fifteenth International Conference on Civil,
Structural and Environmental Engineering Computing, Civil-Comp Press, Stirlingshire,
## Paper 82.
## Caddemi, S., Calio
## `
, I., Cannizzaro, F., Chacara, C., D’Urso, D., Liseni, S., et al., 2018. An origi-
nal discrete macro-element method for the analysis of historical structures. In: Proceedings
of the 16th European Conference on Earthquake Engineering, Thessaloniki, Greece, 1821
## June 2018.
Descrete macroelement modelingChapter | 14529

## Caddemi, S., Calio
## `
, I., Cannizzaro, C., D’Urso, D., Occhipinti, G., Panto
## `
, B., et al., 2019. 3D
discrete macro-modelling approach for masonry arch bridges. In: IABSE Symposium 2019,
## Guimara
## ̃
es (Portugal), 2729 March 2019.
## Calio
## `
,I.,Panto
## `
, B., 2014. A macro-element modelling approach of infilled frame structures.
Comput. Struct. 143, 91107. Available from:
https://doi.org/10.1016/j.compstruc.2014.07.008.
## Calio
## `
## , I., Marletta, M., Panto
## `
, B., 2004. Un semplice macro-elemento per la valutazione della
vulnerabilita
## `
sismica di edifici in muratura. In: atti dell’XI congresso nazionale l’Ingegneria
Sismica in Italia, Genova 2004 (in Italian).
## Calio
## `
## , I., Marletta, M., Panto
## `
, B., 2005. A simplified model for the evaluation of the seismic
behaviour of masonry buildings. In: Topping, B.H.V. (Ed.), Proceedings of the Tenth
International Conference on Civil, Structural and Environmental Engineering Computing,
Civil-Comp Press, Stirlingshire, 195.
## Calio
## `
, I., Cannizzaro, F., D’Amore, E., Marletta, M., Panto
## `
, B., 2008. A new discrete-element
approach for the assessment of the seismic resistance of composite reinforced concrete-
masonry buildings. In: AIP Conference Proceedings, 1020 (PART 1), 2427 June 2008,
Reggio Calabria, pp. 832839.
## Calio
## ́
, I., Cannizzaro, F., Marletta, M., 2010. A discrete element for modeling masonry vaults.
Adv. Mater. Res. 133134, 447452. Available from:
https://doi.org/10.4028/www.scien-
tific.net/AMR.133-134.447
## .
## Calio
## `
## , I., Marletta, M., Panto
## `
, B., 2012a. A new discrete element model for the evaluation of the
seismic behaviour of unreinforced masonry buildings. Eng. Struct. 40, 327338. Available
from:
https://doi.org/10.1016/j.engstruct.2012.02.039.
## Calio
## `
## , I., Cannizzaro, F., Marletta, M., Panto
## `
, B., 2012b. 3DMacro: A 3D Computer Program for
the Seismic Assessment of Masonry Buildings. Gruppo Sismica s.r.l, Catania.
## Calio
## `
## , I., Cannizzaro, F., Panto
## `
, B., Rapicavoli, D., 2015. HiStrA (historical structure analysis).
In: HISTRA s.r.l (Catania, Italy). Release 17.2.3; April 2015. Available from:,
http://www.
grupposismica.it
## ..
Cannizzaro, F., 2010. The Seismic Behaviour of Historical Buildings: A Macro-Element
Approach (Ph.D. thesis). Structural Engineering, University of Catania (in Italian).
Cannizzaro, F., Lourenc ̧o, P.B., 2017. Simulation of shake table tests on out-of-plane masonry
buildings. Part (VI): discrete element approach. Int. J. Architect. Herit. 11, 125142.
## Cannizzaro, F., Panto
## `
## , B., Caddemi, S., Calio
## `
, I., 2018. A Discrete Macro-Element Method
(DMEM) for the nonlinear structural assessment of masonry arches. Eng. Struct. 168,
243256. Available from:
https://doi.org/10.1016/j.engstruct.2018.04.006.
## Casolo, S., Pen
## ̃
a, F., 2007. Rigid element model for in-plane dynamics of masonry walls consid-
ering hysteretic behaviour and damage. Earthq. Eng. Struct. Dyn. 36, 10291048. Available
from:
https://doi.org/10.1002/eqe.670.
Casolo, S., Sanjust, C.A., 2009. Seismic analysis and strengthening design of a masonry monu-
ment by a rigid body spring model: the “Maniace Castle” of Syracuse. Eng. Struct. 31,
14471459. Available from:
https://doi.org/10.1016/j.engstruct.2009.02.030.
## Ch
## ́
acara, C., Cannizzaro, F., Panto
## `
## , B., Calio
## `
, I., Lourenc ̧o, P.B., 2018. Assessment of the
dynamic response of unreinforced masonry structures using a macro-element modeling
approach. Earthq. Eng. Struct. Dyn. 47 (12), 24262446.
Chen, S.Y., Moon, F.L., Yi, T., 2008. A macroelement for the nonlinear analysis of in-plane
unreinforced masonry piers. Eng. Struct. 30 (8), 22422252. Available from:
https://doi.org/
## 10.1016/j.engstruct.2007.12.001
## .
530PART | IIModeling of unreinforced masonry

Dolce, M., 1991. Schematizzazione e modellazione degli edifici in muratura soggetti ad azioni
sismiche. L’Industria delle costruzioni 25 (242), 4457. in Italian.
FEA Ltd., 2018. LUSASTheory Manuals, Lusas Version 16.0. FEA Ltd.
Foraboschi, P., 2006. Masonry structures externally reinforced with FRP strips: tests at the col-
lapse. In: Proceedings of I Convegno Nazionale Sperimentazioni su Materiali e Strutture
(Venice) (in Italian).
Gambarotta, L., Lagomarsino, S., 1997. Damage models for the seismic response of brick masonry
shear walls. Part II: the continuum model and its applications. Earthq. Eng. Struct. Dyn. 26,
441462. Available from:
https://doi.org/10.1002/(SICI)1096-9845(199704)26:4,423::AID-
## EQE650.3.0.CO;2-#
## .
Hilsdorf, H.K., 1969. Investigation into the failure mechanism of brick masonry loaded in axial
compression. Designing, Engineering and Constructing With Masonry Products. Gulf
Publishing Company, pp. 3441.
Kappos, A.J., Penelis, G.G., Drakopoulos, C.G., 2002. Evaluation of simplified models for lat-
eral load analysis of unreinforced masonry buildings. J. Struct. Eng. 128, 890897.
Available from:
https://doi.org/10.1061/(ASCE)0733-9445(2002)128:7(890).
Lagomarsino, S., Penna, A., Galasco, A., Cattari, S., 2013. TREMURI program: an equivalent
frame model for the nonlinear seismic analysis of masonry buildings. Eng. Struct. 56,
17871799. Available from:
https://doi.org/10.1016/j.engstruct.2013.08.002.
Lofti, H.R., Shing, P.B., 1994. Interface model applied to fracture of masonry structures. J. Struct.
Eng. 120, 6380. Available from:
https://doi.org/10.1061/(ASCE)0733-9445(1994)120:1(63).
Lourenc ̧o, P.B., Rots, J.G., 1997. A multi-surface interface model for the analysis of masonry
structures. J. Eng. Mech. 123, 660668. Available from:
https://doi.org/10.1061/(ASCE)
## 0733-9399(1997)123:7(660)
## .
Lourenc ̧o, P.B., Rots, J.G., Blaauwendraad, J., 1998. Continuum model for masonry: parameter
estimation and validation. J. Struct. Eng. 124, 642652. Available from:
https://doi.org/
## 10.1061/(ASCE)0733-9445(1998)124:6(642)
## .
Lourenc ̧o, P.B., Nuno Mendes, A.T., Ramos, L.F., 2012. Seismic performance of the St. George
of the Latins church: lessons learned from studying masonry ruins. Eng. Struct. 40,
501518. Available from:
https://doi.org/10.1016/j.engstruct.2012.03.003.
Macorini, L., Izzuddin, B.A., 2011. A non-linear interface element for 3D mesoscale analysis of
brick-masonry structures. Int. J. Numer. Methods Eng. 85, 15841608. Available from:
https://doi.org/10.1002/nme.3046.
Magenes, G., Calvi, G.M., 1996. Prospettive per la calibrazione di metodi semplificati per
l’analisi sismica di pareti murarie. Atti del Convegno Nazionale La meccanica delle mura-
ture tra teoria e progetto, Ed. Pitagora Bologna, 18-20 September 1996. Messina 503512.
Magenes, G., Della Fontana, A., 1998. Simplified nonlinear seismic analysis of masonry build-
ings. Br. Mason. Soc. Proc. 8, 190195.
Marques, R., Lourenc ̧o, P.B., 2011. Possibilities and comparison of structural component models
for the seismic assessment of modern unreinforced masonry buildings. Comput. Struct. 89,
20792091. Available from:
https://doi.org/10.1016/j.compstruc.2011.05.021.
Marques, R., Lourenc ̧o, P.B., 2014. Unreinforced and confined masonry buildings in seismic
regions: validation of macro-element models and cost analysis. Eng. Struct. 64, 5267.
Available from:
https://doi.org/10.1016/j.engstruct.2014.01.014.
Mele, E., De Luca, A., Giordano, A., 2003. Modelling and analysis of a basilica under earthquake
loading. J. Cult. Herit. 4, 355367. Available from:
https://doi.org/10.1016/j.culher.2003.03.002.
Descrete macroelement modelingChapter | 14531

Mendes, N., 2012. Seismic Assessment of Ancient Masonry Buildings: Shaking Table Tests and
Numerical Analysis (Ph.D. thesis). Civil Engineering, University of Minho.
Mendes, N., Lourenc ̧o, P.B., 2009. Seismic assessment of masonry “Gaioleiro” buildings in
## Lisbon, Portugal. J. Earthq. Eng. 14, 80101.
Mendes, N., Lourenc ̧o, P.B., Campos-Costa, A., 2014. Shaking table testing of an existing
masonry building: assessment and improvement of the seismic performance. Earthq. Eng.
## Struct. Dyn. 43 (2), 247266.
Milani, G., Tralli, A., 2012. A simple meso-macro model based on SQP for the non-linear analy-
sis of masonry double curvature structures. Int. J. Solids Struct. 46, 808834. Available
from:
https://doi.org/10.1016/j.ijsolstr.2011.12.001.
Milani, G., Valente, M., 2015. Failure analysis of seven masonry churches severely damaged
during the 2012 Emilia-Romagna (Italy) earthquake: non-linear dynamic analyses vs con-
ventional static approaches. Eng. Fail. Anal. 54, 1356. Available from:
https://doi.org/
## 10.1016/j.engfailanal.2015.03.016
## .
Milani, E., Milani, G., Tralli, A., 2008. Limit analysis of masonry vaults by means of curved
shell finite elements and homogenization. Int. J. Solids Struct. 45, 52585288. Available
from:
https://doi.org/10.1016/j.ijsolstr.2008.05.019.
NTC, 2008. Decreto Ministeriale. Norme tecniche per le costruzioni. Ministry of Infrastructures
and Transportations. G.U. S.O. n.30 on 4/2/2008; 2008 (in Italian).
## Panto
## `
, B., 2007. The Seismic Modeling of Masonry Structure, an Innovative Macro-Element
Approach (PhD Thesis). Structural Engineering, University of Catania, Catania (in Italian).
## Panto
## `
, B., Raka, E., Cannizzaro, F., Camata, G., Caddemi, S., Spacone, E., et al., 2015. Numerical
macro-modeling of unreinforced masonry structures: a critical appraisal. In: Topping, B.H.V.,
## Iv
## ́
anyi, P. (Eds.), Proceedings of the Fifteenth International Conference on Civil, Structural
and Environmental Engineering Computing. Civil-Comp Press, Stirlingshire.
## Panto
## `
## , B., Cannizzaro, F., Caddemi, S., Calio
## `
, I., 2016. 3D macro-element modelling approach
for seismic assessment of historical masonry churches. Adv. Eng. Soft. 97, 4059.
Available from:
https://doi.org/10.1016/j.advengsoft.2016.02.009.
## Panto
## `
## , B., Cannizzaro, F., Calio
## `
, I., Lourenc ̧o, P.B., 2017a. Numerical and experimental valida-
tion of a 3D macro-model element method for the in-plane and out-of-plane behaviour of
unreinforced masonry walls. Int. J. Architect. Herit. 11 (7), 946964. Available from:
https://doi.org/10.1080/15583058.2017.1325539.
## Panto
## `
## , B., Giresini, L., Sassu, M., Calio
## `
, I., 2017b. Non-linear modeling of masonry churches
through a discrete macro-element approach. Earthq. Struct. 12, 223236. Available from:
https://doi.org/10.12989/eas.2017.12.2.223.
## Panto
## `
## , B., Calio
## `
, I., Lourenc ̧o, P.B., 2018. A 3D discrete macro-element for modelling the out-
of-plane behaviour of infilled frame structures. Eng. Struct. 175, 371385. Available from:
https://doi.org/10.1016/j.engstruct.2018.08.022.
Penelis, G.G., 2006. An efficient approach for pushover analysis of unreinforced masonry
(URM) structures. J. Earthq. Eng. 10 (03), 359379.
Quagliarini, E., Maracchini, G., Clementi, F., 2017. Uses and limits of the Equivalent Frame
Model on existing unreinforced masonry buildings for assessing their seismic risk: a review.
J. Build. Eng. 10, 166182. Available from:
https://doi.org/10.1016/j.jobe.2017.03.004.
Raka, E., Spacone, E., Sepe, V., Camata, G., 2015. Advanced frame element for seismic analysis
of masonry structures: model formulation and validation. Earthq. Eng. Struct. Dyn. 44,
24892506. Available from:
https://doi.org/10.1002/eqe.2594.
532PART | IIModeling of unreinforced masonry

## Roca, P., Molins, C., Mar
## ́
ı, A.R., 2005. Strength capacity of masonry wall structures by the
equivalent frame method. J. Struct. Eng. 131 (10), 16011610.
## Siano, R., Roca, P., Camata, G., Pela
## `
, L., Sepe, V., Spacone, E., et al., 2018. Numerical investi-
gation of non-linear equivalent-frame models for regular masonry walls. Eng. Struct. 173,
## 512529.
Tomazevic, M., 1978. The Computer Program POR: Institute for Testing and Research in
Materials and Structures. ZRMK, Ljubljana.
## Turn
## ˇ
sek, V.,
## ˇ
## Ca
## ˇ
covi
## ˇ
c, F., 1970. Some experimental results on the strength of brick masonry
walls. In: Proceedings of the 2nd International Brick & Block Masonry Conference, Stoke-
on-Trent, pp. 149156.
Valente, M., Milani, G., 2016. Seismic assessment of historical masonry towers by means of
simplified approaches and standard FEM. Constr. Build. Mater. 108, 74104. Available
from:
https://doi.org/10.1016/j.conbuildmat.2016.01.025.
Zavala, C., Honma, C., Gibu, P., Gallardo, J., Huaco, G., 2004. Full scale on line test on two
story masonry building using handmade bricks. In: Proceedings of the 13th World
Conference on Earthquake Engineering, Vancouver, p. 2885.
Further reading
Lourenc ̧o, P.B., 2002. Computations on historic masonry structures. Prog. Struct. Eng. Mater. 4,
301319. Available from:
https://doi.org/10.1002/pse.120.
Descrete macroelement modelingChapter | 14533