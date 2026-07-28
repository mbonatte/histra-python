A macro-element modelling approach of Infilled Frame Structures
Ivo Caliò ⇑, Bartolomeo Pantò
Dipartimento Ingegneria Civile e Architettura, University of Catania, Italy
a r t i c l e i n f o
Article history:
Received 23 October 2013
Accepted 9 July 2014
Available online 12 August 2014
```
Keywords:
```
```
Infilled Frame Structures (IFS)
```
Masonry Infilled Reinforced Concrete frame
```
(MIRC)
```
Macro-element approach
Discrete element approach
Seismic vulnerability
Micro-models
a b s t r a c t
```
In this paper a macro-modelling approach for the seismic assessment of Infilled Frame Structures (IFS) is
```
presented. The interaction between frame and infill is simulated through an original approach in which
the frame members are modelled by means of lumped plasticity beam–column elements while the infills
are described by plane macro-elements. The reliability of the approach is evaluated by means of nonlin-
ear analyses, performed on infilled masonry reinforced concrete structures, for which experimental
results are available in literature. The proposed computational strategy is intended to provide a
numerical tool suitable for the design and the vulnerability assessment of IFS.
Ó 2014 Elsevier Ltd. All rights reserved.
1. Introduction
```
Infilled Frame Structures (IFS) represent a high percentage of
```
existing and new buildings in many seismically prone areas around
the world. These mixed structural systems are governed by the
interaction between frame and infill wall. The frame can be built
with different materials: reinforced-concrete, steel or wood, while
the infill wall can be of unreinforced masonry or concrete. Masonry
```
Infilled Reinforced Concrete frames (MIRC) are, at present, widely
```
adopted for the construction of new buildings as well as structural
retrofitting strategy of medium and low-rise buildings. Existing
masonry infilled frame buildings are often difficult to be classified
since, in many cases they are the result of low-engineered struc-
tures built before the emanation of seismic codes and conceived
to resist only gravity loads [1]. Currently, new infilled frame build-
ings are mainly concentrated in several regions around the world
which are often characterised by a high-density population, since
this structural typology represents a rapid and low cost building
strategy [2]. A large number of buildings are built with masonry
infill walls for non-structural reasons, since the role of infill is
associated with architectural needs. In these cases the structural
contribution of masonry infill panels is generally neglected in the
structural analyses, leading to a significant inaccuracy of the
prediction of lateral stiffness, strength and ductility capabilities
of the structure. As highlighted by many authors [1,3,4], ignoring
the role of frame-infill panel interaction is not always safe, result-
ing in a possible change of the seismic demand due to the modifi-
cation of the fundamental period of the mixed structural system.
Furthermore, the presence of infill walls can modify the stiffness
and ductility distribution along the structure causing local col-
lapses, during seismic events, ignored at the structural design
phase.
The ability to assess the seismic behaviour of IFS is of crucial
importance and several contributions have been provided in the
last five decades by many researchers by means of both numerical
and experimental investigations. The highly nonlinear masonry-
infill response and the ever-changing contact condition along the
frame-infill interfaces make the simulation of the nonlinear behav-
iour of an entire infilled frame building a challenging problem. A
detailed simulation of the complex nonlinear behaviour of infilled
frames requires the rigours use of expensive computationally non-
linear finite element models, capable to reproduce the nonlinear
degrading behaviour of the infill masonry and the complex interac-
tion between the frame and the embraced infill. Refined finite ele-
ment numerical models [2,5,6], such as the smeared cracked and
discrete crack finite element models, able to predict the complex
non-linear dynamic mechanical behaviour and the degradation of
the masonry media, require sophisticated constitutive laws and
huge computational resources. As a consequence these numerical
approaches are, at present, unsuitable for practical application
and extremely difficult to apply to large structures. On the other
hand, in order to estimate the seismic vulnerability of an existing
building and to assess whether the structure requires a seismic
```
http://dx.doi.org/10.1016/j.compstruc.2014.07.008
```
0045-7949/Ó 2014 Elsevier Ltd. All rights reserved.
⇑ Corresponding author. Address: Dipartimento Ingegneria civile e Architettura –
DICAR, University of Catania, Viale Andrea Doria, 6, 95125 Catania, Italy.
```
Tel.: +39 (0)95 738 2255; fax: +39 (0)95 738 2249.
```
```
E-mail address: icalio@dica.unict.it (I. Caliò).
```
```
Computers and Structures 143 (2014) 91–107
```
Contents lists available at ScienceDirect
Computers and Structures
j o u r n a l h o m e p a g e : w w w . e l s e v i e r . c o m / l o c a t e / c o m p s t r u c
upgrade, a structural engineer needs simple and efficient numeri-
cal tools, whose complexity and computational demand must be
appropriate for practical engineering purposes. For these reasons,
in the last six decades, many authors have developed simplified
or alternative methodologies for predicting the nonlinear seismic
behaviour of IFS. According to the classification proposed by Aster-
is et al., in a recent comprehensive review of existing mathematical
macro-models of infilled frames [7], the current numerical
approaches can be classified in two main categories, macro- and
micro-models. The macro-models try to grasp the global behaviour
of the Infilled Frame Structures without claiming to obtain a
detailed nonlinear response and to describe all the possible modes
of local failure. On the contrary, the micro-models are conceived
for a detailed behaviour simulation of the infilled frame trying to
encompass all the possible modes of collapse due to different
damage scenarios in the masonry infill and the surrounding frame.
Refined micro-models can also be useful for validating and
calibrating simplified approaches in those cases in which experi-
mental results are unavailable. The most commonly used macro-
model practical approach is the so called ‘diagonal strut model’,
according to this approach the infilled masonry is represented by
a diagonal bar under compression. The first who suggested the
possibility of considering the effect of the infill as an equivalent
diagonal bracing was Polyakov [8]. This suggestion was taken up
by Holmes [9], who modelled the infill by an equivalent pin-
jointed diagonal strut made of the same material with the same
thickness as the infill panel and a width equal to one-third of the
infill diagonal length. This so called ‘one-third’ rule was suggested
as being applicable irrespective of the relative rigidities of the
frame and the infill. Many authors [10–20] suggested alternative
proposals, for the evaluation of the equivalent strut width. Some
of these studies provide analytical expressions, which encompass
the presence of openings in the infill or analyse special layouts
such as the case in which infill and frame are not bonded together
[17].
In the last two decades some authors highlighted the limit of
using a single strut-element for modelling the complex nonlinear
behaviour of IFS and proposed more complex macro-element with
the aim to obtain a better description of the effect of infill on the
surrounding frame. Thiruvengadam [21], with the aim to evaluate
frequencies and modes of vibrations of IFS, proposed a ‘multiple
strut model’, wherein the infills are represented by a set of equiv-
alent multiple struts. The model is able to account for the frame-
infill separation and infill openings and was also included in
FEMA-356 [22]. Subsequently, a number of researchers proposed
the multi-strut approach for modelling both the linear and nonlin-
ear behaviour of IFS [23–30]. The main advantage of the multiple-
strut models, despite the increase in complexity, is the ability to
```
represent the actions in the frame more accurately; a comprehen-
```
sive description of the multiple strut models is reported in the
review paper [7].
In this paper an alternative innovative approach for the simula-
tion of the seismic behaviour of Infilled Frame Structures, suitable
both for research and current engineering practice applications, is
presented. In this approach, the infilled wall is modelled by means
of a discrete element, originally conceived for the simulation of the
nonlinear response of masonry building [31,32], while the rein-
forced concrete frame is modelled by means of inelastic beam–col-
umn elements, in which the plastic hinges can originate in
different positions along the beam-span. The computational cost
of the proposed numerical approach is greatly reduced in compar-
ison to that involved in nonlinear finite element simulations,
which require finite element modelling of both the frame and
the infill. The basic macro-element, adopted for the simulation of
the infilled masonry, consists of an articulated quadrilateral,
with rigid edges, in which two diagonal springs govern the
shear-diagonal behaviour. The flexural and shear-sliding behaviour
is governed by discrete distributions of springs on the sides of the
quadrilateral that govern the interaction with the adjacent
elements. The calibration of the model requires few parameters
to define the masonry material based on results from current
experimental tests. The equivalence between the masonry portion
and the macro-element is based on very simple physical consider-
ations [32] and the interpretation of the numerical results is
straightforward and unambiguous. This novel approach has been
recently successfully applied to mixed reinforced concrete-
masonry structures in the academic context [33–38,52] thus
confirming that it can be considered as a low cost computational
tool suitable for the investigation of the nonlinear structural
behaviour where the seismic capacity results from the interaction
between masonry and reinforced concrete.
In Section 2 a detailed description of the proposed macro-model
approach is provided and the required fiber calibration procedures
are described in detail. The capability of the model to simulate the
complex interaction between the infill and the surrounding frame
is outlined in Section 3, where the typical failure mechanism of
infilled frames and its macro-element modelling are considered.
```
In the numerical applications (Section 4), the proposed
```
approach is adopted for the simulation of the nonlinear response
of masonry infilled frame for which experimental results are avail-
able from previous studies listed in the literature. In the same sec-
tion the influence of the model discretization and the ability of the
model of taking into account the presence of openings through a
simple a macro-element discretization is highlighted.
2. The infilled frame model
In the present study, the complex nonlinear behaviour of
Infilled Frame Structures is analysed according to a hybrid
approach in which the surrounding frame is modelled using con-
centrated plasticity beam–column elements while the nonlinear
response of the infill is simulated by means of a plane discrete ele-
ment recently proposed by the authors [32] which has been imple-
mented in a software used both for research and engineering
practice [39]. In the following it is clarified how the beam–column
element and the discrete-element contribute to provide a reliable
simulation of the nonlinear behaviour of Infilled Frame Structures.
2.1. The discrete-element for modelling masonry infill
Masonry infill is modelled by means of a macro-element,
recently introduced by Caliò et al. [32], conceived for the simula-
tion of the nonlinear in-plane behaviour of unreinforced masonry
walls. This element is characterised by a simple mechanical
scheme, Fig. 1, constituted by an articulated quadrilateral with
rigid edges connected by four hinges and two diagonal nonlinear
springs. Each side of the quadrilateral can interact with other ele-
ments or supports by means of a discrete distribution of nonlinear
springs, denoted as interface. Each interface is constituted by n
nonlinear orthogonal springs, perpendicular to the panel side, and
an additional longitudinal spring, parallel to the panel edge. In spite
of its simplicity, such a basic mechanical scheme is able to simulate
the main in-plane failures of a masonry wall portion subjected to
in-plane horizontal and vertical loads.
These well-known collapse mechanisms, namely the flexural
failure, the diagonal shear failure and sliding shear failure, are
roughly represented in Fig. 2 where the typical crack patterns,
together with the qualitative kinematics of the masonry portion,
are also sketched.
Fig. 3 shows how the proposed plane macro-element allows a
simple and realistic mechanical simulation of the corresponding
```
92 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
failure mechanisms. The flexural failure mode, sketched in Fig. 2a.,
is associated with the rocking of the masonry panel in its own
```
plane; the activation of this collapse mode is governed by the inter-
```
face orthogonal springs, Fig. 3a. The diagonal-shear failure mode,
shown in Fig. 2b, is related to the loss of bearing capacity of the
masonry panel due to excessive shear and to the consequent for-
mation of diagonal cracks along the directions of the principal
```
compression stresses; this mechanism is controlled by the diago-
```
nal nonlinear links, Fig. 3b.
The shear-sliding failure mode is characterised by the sliding of
the masonry panel in its own plane. In this case the loss of bearing
capacity is associated to the formation of cracks parallel to the bed-
```
joints, Fig. 2c; this mechanism is governed by the sliding spring of
```
the interface, Fig. 3c.
According to the proposed discrete element approach, a
masonry macro-element is modelled by an equivalent mechanical
scheme in which the physical role of each component is simple and
unambiguous [32].
Each discrete element exhibits three degrees-of-freedom, asso-
ciated with the in-plane rigid-body motion, plus a further degree-
of-freedom, needed for the description of the shear deformability.
The deformations of the interfaces are associated to the relative
```
(a) (b)
```
```
Fig. 1. The basic macro-element for the masonry infill: (a) undeformed configuration; and (b) deformed configuration.
```
q
q qF F F
```
(a) (c)(b)
```
```
Fig. 2. Main in-plane failure mechanisms of a masonry portion. (a) flexural failure; (b) shear-diagonal failure; and (c) shear-sliding failure.
```
q q
qFF F
```
(a) (c)(b)
```
```
Fig. 3. Simulation of the main in-plane failure mechanisms of a masonry portion by means of the macro-element. (a) flexural failure; (b) shear-diagonal failure; and (c) shear-
```
sliding failure.
I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 93
motion between corresponding panels, therefore no further
Lagrangian parameters have to be introduced in order to describe
their kinematics.
In Fig. 4 a typical discretization of an infilled frame with and
```
without a central door opening is shown. Namely Fig. 4(a, d) refer
```
```
to the geometrical layouts of the infilled frames, Fig. 4(b, e) report
```
the corresponding discretization according to the basic needed
```
mesh while the representations of Fig. 4(c, f) are relative to a more
```
refined mesh. The use of a more refined mesh is not mandatory
however, in some cases, can provide more accurate results and a
better description of the collapse mechanism. This aspect is partic-
ularly important in the modelling of infilled frames since it allows
a better description of the infilled masonry also in the presence of
window or door openings and in some cases can lead to more accu-
rate modelling of the infilled frame, as described in the subsequent
paragraphs.
It is worth to notice that each macro-element inherits the plane
geometrical properties of the corresponding modelled masonry
portion avoiding any effective dimension definition of the element,
as required by the simplified models based on equivalent strut ele-
ment approach.
The efficacy of the masonry infill model relies on a suitable
choice of the mechanical parameters of the macro-element
inferred by an equivalence between the masonry media and a ref-
erence continuous model characterised by simple but reliable con-
stitutive laws. This equivalence is based on a straightforward
calibration procedure that exploits the main mechanical parame-
ters of the masonry only, according to an orthotropic homogeneous
medium, as highlighted in the following.
2.1.1. Calibration of the interface orthogonal springs
Since the masonry is considered as a homogeneous medium its
global behaviour should be ascribed to the flexural and shearing
characteristics of a finite portion of an orthotropic inelastic con-
tinua. As mentioned before, the flexural behaviour is governed by
the interface orthogonal springs connecting the panel to adjacent
elements. Each spring is calibrated by adopting a specific constitu-
tive law for the masonry media, according to a fiber modelling
approach. The orthotropic nature of the masonry is simply consid-
ered by calibrating separately the horizontal and vertical interfaces
according to the mechanical properties of the corresponding
directions.
In reference [32] a detailed description of the calibration of the
model for unreinforced masonry structures is reported, here the
calibration procedure is specialised for a typical masonry-frame
layouts, as reported in Figs. 4 and 5. The deformability of the infill
along the horizontal and vertical directions are concentrated in the
nonlinear links of the vertical and horizontal interfaces. Consis-
tently with a fiber calibration approach, the stiffness calibration
of the panel is simply obtained by assigning to each link the axial
rigidity of the corresponding masonry strip. Each masonry strip is
identified by its influence area and the half dimension of the panel
in the direction perpendicular to the interface, Fig. 5.
With reference to a single orthotropic panel, the initial stiffness,
the compression and tensile yielding strengths and the corre-
sponding ultimate displacements are derived by the mechanical
material properties of the masonry in horizontal and vertical direc-
tions as reported in the Table 1, with reference to a simple elasto-
plastic behaviour with limited deformability.
In Table 1, Eh and Ev are the Young’s modulus in horizontal and
```
vertical direction of the homogenised orthotropic masonry media;
```
rhc, rvc and rht, rvt are the corresponding compressive and tensile
yielding stresses, ehcu, evcu and ehtu, evtu are the ultimate compres-
```
sive and tensile strains; s is the thickness of the masonry infill
```
and kh and kv are the distance between two nonlinear links in
the vertical and horizontal interfaces.
Also in presence of openings the calibration of the macro-ele-
ments is simple and straightforward. In Fig. 4d–f it is shown how
a central opening can be represented through two different mesh
discretizations. It is worth noticing that only the link associated
to interfaces between elements have to be calibrated. As an exam-
ple, in Fig. 5d–f a simple case of a partially infilled frame, in which
the opening is adjacent both to a column and to a portion of the
beam, is represented. In this case the expressions reported in
Table 1 have to be referred to the actual size of the masonry
macro-element, furthermore in the horizontal direction only the
nonlinear links of the column-panel interface have to be consid-
ered and calibrated.
The collapse behaviour of the panel is dealt with by different
criteria in compression and in tension. Precisely, once the compres-
sive ultimate displacement is reached, the spring is removed from
the model and the relevant reaction is applied as an external force
loading the corresponding elements. On the other hand, when the
tensile limit displacement is attained, although the reaction is
```
(a) (b) (c)
```
```
(d) (e) (f)
```
```
Fig. 4. Modelling of infilled frame with and without a central door opening. (a, d) the geometrical layout; (b, e) model corresponding to the basic mesh; (c, f) model
```
corresponding to a more refined mesh resolution.
```
94 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
again re-distributed to the corresponding elements, the link is not
removed from the model, since it will be able to bear further com-
pressive loads once the contact with the corresponding panel will
be restored.
2.1.2. Calibration of the sliding springs of the interface
The longitudinal spring governs the sliding-shear failure by
considering the potential sliding between two adjacent elements.
The characteristics of this spring depend on the effective contact
surface between the adjacent elements. When the contact zone
between the elements is zero the sliding spring is no longer active.
The sliding springs have been modelled by means of a rigid-plastic
constitutive behaviour which is governed by a Mohr–Coulomb
yielding surface, sliding occurs in particular when the force in
the nonlinear link reaches its limit value, Flim, which is given by
the expression:
Flim ¼ ðc þ l rmÞA o ð1Þ
```
in which c is a cohesion parameter and l is the friction coefficient;
```
rm is the current average value of the compressive stresses acting
on the interface and Ao is the effective contact area of the two adja-
cent elements. The sliding behaviour that can occur between the
infill and the adjacent frame has to be characterised by specific val-
ues of the cohesion and the friction coefficient which, in general, are
not coincident with the values associated to the masonry media, in
which the brick texture plays an important role.
2.1.3. Calibration of the diagonal springs
Shear failure is the most common type of masonry collapse
when the infilled frame is subjected to action in its own plane, this
is aided by the kinematic constraint exerted by the surrounding
frame. In the macro-element model the shear failure collapse is
controlled by the diagonal springs [32] according to a suitable
yielding criteria. As highlighted in reference [40], two fundamen-
tally different hypotheses, which lead to similar results, have been
developed in order to model the shear failure mechanism. In the
```
first case, which has been accepted by Eurocode 6 (Design of
```
```
masonry structures) [41], the shear strength is defined according
```
to a Mohr Coulomb law
Fm ¼ fmo þ lc rn ð2Þ
where fmo is the shear strength associated to a zero value of com-
pression strength, lc is a friction coefficient, defining the contribu-
tion of compressive stresses, rn is the value of the average
compressive stress. Values for fmo and lc should be determined by
experimental test [42–44]. It is worth highlighting that this crite-
rion is the same suggested for the description of the sliding-shear
failure, although characterised by appropriate values of fmo and lc
that in general do not coincide with the corresponding values that
govern the sliding-shear failure.
Alternative theories associate the diagonal shear failure to the
principle tensile stresses that develop in the wall when subjected
to vertical loads and increasing horizontal forces. The most
adopted criterion based on this assumption is the well known
Turnsek and Cacovic criterion [42] in its modified form [44] that
H
L
λhL/2
v
λh
λv
H/2
```
(a) (b) (c)
```
H
L'
λh
λv
λh
λv
H/2
L'/2
'
'
```
(d) (e) (f)
```
Fig. 5. Fiber calibration of the orthogonal springs of masonry-frame interfaces.
Table 1
calibration of the orthogonal spring of masonry-frame interfaces.
Initial elastic stiffness Compression yielding force Tensile yielding force Compression ultimate displacement Tensile ultimate displacement
```
Orthogonal springs in the vertical interfaces (Fig. 5b)
```
K hp ¼ 2 E h kh sL F hcy ¼ skh rhc F hty ¼ skh rht uhcu ¼ L2 ehcu uhtu ¼ L2 ehtu
```
Orthogonal springs in the horizontal interfaces (Fig. 5a)
```
Kvp ¼ 2 Ev kv sH Fvcy ¼ skv rvc Fvty ¼ skv rvt uvcu ¼ H2 evcu uvtu ¼ H2 evtu
I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 95
takes into account the influence of the geometry of the wall and
the distribution of action at maximum resistance. The latter crite-
rion can be expressed as
fv ¼ f tb
ffiffiffiffiffiffiffiffiffiffiffiffiffiffi
1 þ rnf t
r
ð3Þ
where fv is the average shear stress in the wall attained at the max-
imum resistance, ft is the tensile strength of masonry, b is the shear
```
stress distribution factor (depending on the geometry of the wall
```
and on the value of the ratio between the vertical N and horizontal
```
H load), rn is the average compression stress due to vertical load N.
```
In the initial linear elastic range, the calibration of the diagonal
springs is simply obtained by enforcing an elastic equivalence
between the panel and the corresponding masonry wall, which is
considered as a pure shear deformable homogeneous plate, as
reported in reference [32]. The ultimate shear load and the corre-
sponding displacement of each diagonal spring are therefore
derived by the knowledge of the mechanical material properties
of the masonry by means of the adopted shear resistance criteria
[32]. Since the macro-element must incorporate the mechanical
property of the finite portion of the modelled masonry wall, the
ultimate shear displacement of the element is directly associated
to the ultimate shear generalized deformability of the homoge-
nised masonry media. The latter value can be evaluated experi-
mentally or can be obtained from technical codes. The ultimate
displacement of the wall can be associated with a specific value
of the ultimate angular deformation which is dependent on the
particular masonry media.
The post-yielding behaviour of each nonlinear link can be char-
acterised according to different constitutive models, as shown in
the numerical applications reported in Section 4.
2.2. The interacting beam column element
For mixed masonry-reinforced concrete structures, beam–col-
umn lumped plasticity elements are included in the model. The
interaction between the frame elements, along the entire length,
with the adjacent masonry is modelled by means of the interfaces
of the macro-elements.
The frame element interacts with the masonry panels by means
of nonlinear-links distribution along the macro-element interfaces.
Each interface, as those between masonry panels, is constituted by
n orthogonal and a single longitudinal nonlinear links. In Fig. 6 the
degrees of freedom which govern the interaction between a panel
```
and an adjacent beam element are indicated; u pk (k = 1. . .4) are the
```
four degrees of freedom that describe the kinematic of the macro-
element, u1, v1, /1, u2, v2, /2 are the degrees of freedom of the beam
```
ends, while voj, /oj (j = 1. . .n) and um are the degrees of freedom
```
associated to the nonlinear links of the interface. For the evaluation
of the nonlinear behaviour of the frame element it has been
assumed that plastic hinges can occur in each sub-beam element
between two nonlinear links. This latter assumption provides a
reliable frame element model since it is able to embed the occur-
rence of plastic hinges at different positions and it is consistent
with the adopted level of infill discretization. The inelastic behav-
iour of the frame element, concentrated at plastic hinges is gov-
erned by the interaction of the axial force and two flexural
moments consistent with the yield surfaces of the concrete cross
sections. In the application developed in this work the yield
surfaces have been evaluated according to a standard approach,
modelling the inelastic behaviour of beam cross sections consistent
with an inelastic-perfectly plastic behaviour [45]. Once the consti-
tutive laws have been defined, both force and displacement con-
trolled load processes can be performed according to procedures
currently used in finite element analysis [45,46].
3. The typical failure mechanism of infilled frames and its
macro-element modelling
Infilled frames exhibit a highly nonlinear inelastic behaviour as
a result of the interaction between the masonry infill panel and the
surrounding frame. The most important factors contributing to the
nonlinear behaviour are: cracking and crushing of the masonry,
cracking of the concrete, yielding of the reinforcing bar, local bond
slip, degradation of the bond friction mechanism at the panel-
frame interface associated to a variation along the contact length.
Macro-models, due to their simplicity, cannot accurately represent
all the various failure mechanisms of infilled frame.
Numerous experimental and numerical studies have identified
many complicated failure mechanisms due to the frame–panel
interaction [3,7]. According to the classification reported in the
recent state of art review by Asteris et al. [7], these different failure
mechanisms can be classified as an out-of plane buckling mode or
one of four distinct in-plane modes.
```
The Diagonal Compression Buckling mode (DCB) is associated
```
with the crushing of the infill within its central region due to
out-of-plane buckling of the infill. This failure mode mainly hap-
pens in slender infills and cannot be directly controlled through
the in-plane response of the proposed macro-element approach.
Several analytical models have been introduced to represent the
out-of-plane behaviour of infill panels during seismic events. The
majority of experimental data suggest that after the initial cracking
of the URM infill wall, the out-of-plane strength depends upon the
compressive strength of the masonry, not upon its tensile strength,
due to the arching action of the infill wall. Recently Kadyiewski and
Mosalam [47] proposed an alternative model that considers both
the in-plane and out-of-plane behaviour consisting of two beam
column elements with a node at mid-span used to account for
out-of-plane inertial forces.
The in-plane modes are qualitatively represented in Fig. 7
together with their equivalent macro-element representations,
according to two different levels of discretization. The Corner
```
Crushing mode (CC), Fig. 7a1 is associated with the crushing of
```
the infill in at least one of its loaded corners. This failure mecha-
nism generally occurs in presence of weak masonry infill panel sur-
rounded by a frame with weak joints and strong members [7,29].
In Fig. 7a2 and a3 simplified representations of the kinematic
u 1
v 1
u p3
φ1
u 2
φ2
v 2
u p2
rigid edge
u m
k s
v onv o1
φo1 φon
k 1 k nk n-1
v o2
φo2
k 2
u p4
u p1
beam/column internal degrees of freedom
beam/column external degrees of freedom
Fig. 6. Qualitative representation of an interface between a beam column and the
adjacent macro-elements and the corresponding degrees of freedom.
```
96 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
associated to the proposed formulation, corresponding to the two
different mesh resolutions, are reported. The same figure high-
lights how the Corner Crushing of the infill can be controlled by
the deformation of the nonlinear links of frame-panel interfaces.
```
The Diagonal cracKing mode (DK) corresponds to a shear diag-
```
onal collapse and manifests by cracking along the compressed
diagonal of the infill, Fig. 7b1. The activation of this failure mode
is governed by the diagonal nonlinear links of the macro-elements
as qualitative reported in Fig. 7b2 and b3. This is a common mech-
anism that is often associated with damage within the frame.
```
The Sliding Shear (SS) mode is associated to the sliding shear
```
failure through bed joints, this mechanism generally happens in
the case of infill with weak mortar joints surrounded by a strong
frame, Fig. 7c1. If the infill is modelled by only one element, this
behaviour can also be captured by an appropriate calibration of
the diagonal links of the macro-element which aims to control
both the DK and SS failure modes at the macro-scale as qualita-
tively reported in Fig. 7c2. When the infill is modelled as a mesh
of macro-elements, this mechanism is mainly controlled by the
nonlinear links, along the horizontal interfaces between adjacent
masonry elements [32]. In Fig. 7c3 a simplified qualitative repre-
sentation of the kinematic associated to this failure mechanism is
reported.
```
The Frame Failure mode (FF) is seen in the form of a distribution
```
of plastic hinges producing a mechanism in the frame, as in
```
Fig. 7d1; this mode occurs in weak frame and strong infill. Fig. 7d 2
```
and d3 report a qualitative representation of the collapse mecha-
nism associated to the two considered mesh discretizations, it
can be observed as a refined mesh can allow a better representa-
tion of the collapse mechanism. Further details on the capability
of the present approach to provide a satisfactory simulation of
the collapse behaviour of infilled frames are reported in Section 4.
It is worth noting that all the considered basic mechanisms can
occur under different combinations and can involve low or heavy
damage in the surrounding frame. The proposed approach is able
to identify combined mechanisms and the simultaneous presence
of damage corresponding to different failure modes.
4. Numerical applications
In this section the proposed model is employed to simulate the
nonlinear response of masonry infilled frame for which experimen-
tal results are available from previous studies reported in the liter-
ature. In particular, the results of the following two different
experimental programs have been taken into account:
– A research program, performed by the Construction Engineering
```
Research Laboratory (Champaign USA), aimed to investigate the
```
seismic vulnerability of masonry-infilled non-ductile reinforced
```
concrete frames (designed to resist gravity loads) [48].
```
– An experimental campaign, carried out at the University of Col-
orado, devoted to the seismic assessment of reinforced concrete
frames designed in accordance with the Uniform Building Code
[3,49,50].
4.1. Simulation of experimental results of non-ductile RC infilled
frames
The first experimental program, under consideration, was per-
formed at the Construction Engineering Research Laboratory, at
```
Champaign (Illinois) to determine the seismic vulnerability of
```
existing dormitory-type buildings, constructed during the 1950s
and 1960s in the USA. The research investigated the structural
```
(d1)(c1)(b1)(a1)
```
```
(d2)(c2)(b2)(a2)
```
```
(d3)(c3)(b3)(a3)
```
```
Fig. 7. Qualitative representation of the in-plane collapse mode and its equivalent macro-element discretization. (a) Corner Crushing (CC) mode, (b) Diagonal cracKing (DK)
```
```
mode, (c) Sliding Shear (SS) mode, and (d) Frame Failure (FF) mode.
```
I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 97
behaviour of non-ductile RC frames fully infilled with masonry
panels. The term non-ductile, as used in the reference paper [48],
refers to the RC bare frames based on reinforcement details typical
of structures designed to resist gravity loads without taking into
account seismic actions. In the experimental campaign, five half-
scale models were tested, all subjected to lateral, in-plane mono-
tonic loading. The five models were all single-storey RC frames of
single-, double- or triple-bay construction. In the following, the
results of a single-bay infilled frame are considered, the detailed
model configurations and the material properties of the considered
specimen are reported in the reference paper [48].
Fig. 8 shows the layout corresponding to the geometrical char-
acteristics and the reinforcement of the infilled frame. The input
data, assumed in the numerical simulations, refer to a homoge-
nised representation of the infill. The stress/strain relationship
for concrete in compression is assumed to be of parabolic type
up to the strain eco and of rectangular type up to the ultimate strain
ecu. The stress/strain relationship for steel has been taken as that of
elastic-perfectly plastic.
The properties of the nonlinear links that govern the behaviour
of the macro-element discretization of the masonry infill have
been evaluated according to the straightforward calibration proce-
dure reported in Section 2.
The proposed model has been implemented in the software
3DMacro [39], and used for the numerical simulations presented
in this section. The reliability of the latter implementation, for
```
the seismic assessment of Unreinforced Masonry Building (URM),
```
has been recently investigated, also by other authors [51] where
different structural component models for URM have been com-
pared. Further validations both for unreinforced and confined
masonry structures are reported in [32–38,52].
The input parameters required for calibrating the reinforced
concrete frame and the discrete element are reported in Tables 2
and 3 respectively, according to the failure criteria considered in
Section 2.
The first numerical application analyses the behaviour of the
basic single-bay frame without considering masonry infill contri-
bution. Fig. 9 reports the comparison between the experimental
and numerical results relative to the bare RC frame. A good agree-
ment can be observed between experiment and simulation both in
terms of the capacity curve and the collapse mechanism, the latter
is associated to the activation of plastic hinges in column ends.
The results relative to the single-bay RC infilled frame are
reported in Fig. 9b, where the base shear versus the top horizontal
displacement is reported. The continuous line is relative to the
experimental results while the dashed lines refer to the numerical
```
simulation; the latter has been performed by considering a 3  3
```
macro-elements discretization. The agreement between experi-
mental and numerical results, at least in terms of maximum base
shear force and top displacements, can be considered satisfactory.
A further investigation of the role of the frame and the infill dur-
ing the interaction is conducted in Fig. 10. In Fig. 10a the contribu-
tions of the infill and the interacting frame to the base shear are
reported together with the total base shear, already displayed in
Fig. 9b. Furthermore, in Fig. 10b a comparison of the monotonic
nonlinear response of the frame in bare and interacting conditions
is reported. It is interesting to observe how the contribution of the
frame increases when it interacts with the infill.
The shear sliding properties, reported in Table 3, have been cho-
sen by assuming typical values of brick masonry media. However,
with the aim to investigate the role of the cohesion and the friction
angle, which control the shear sliding properties, in Fig. 11 the base
shear versus the top displacement has been evaluated for different
value of the cohesion c and friction angle l, it can be observed a
very small sensitivity to the friction angle and a low dependence
on the cohesion.
In Fig. 12b the damage scenario predicted by the model corre-
sponding to the ultimate value of drift of 2.86%, is compared to
the corresponding damage crack patterns obtained experimentally
[48], as shown in Fig. 12a. It is worth to notice that, due to their
simplicity, macro-elements provide a simplified representation of
failure mechanisms for infilled frame. With reference to the com-
parison reported in Fig. 12a and b it has to be considered that at
the base of the column there is the overlapping of steel reinforce-
ment, as detailed in [48]. This overstrength can partly justify the
difference between numerical and experimental collapse simula-
tions, since the experiment does not show any hinge at the base
of the left column, provided by the numerical simulation, which
is instead collocated in the middle.
The used representation in the interface allows the distinction
of the reactive compressive zone from the cracked one due to ten-
```
sile forces; diagonal bars inside a panel indicate the yielding of the
```
diagonal springs. It is worth noting how the proposed approach is
able to grasp the distribution of damage on both the infill and the
surrounding frame.
In Fig. 12c and d the flexural moment distribution in the frame,
corresponding to the values of drift 0.55% and 2.86%, are reported.
These further representations show how the proposed approach
provides a simulation of the complex interaction between frame
and infill, characterised by continuous variation of the contact zone
with redistributions of internal forces both in the infill and the sur-
rounding frame.
4.2. Simulation of experimental results of RC infilled frames designed in
accordance with the UBC
To investigate the performance of masonry-infilled RC frames
subjected to in-plane lateral loads, a comprehensive study was
carried out at the University of Colorado. The results and major
conclusions of this study, obtained from the experimental
6101829 203203
S4S2
S8S5
457
S6
457
S776
381381
L
197
127
203
5 #3127
S3S1
1327
76 203
381
6 ga./12.7mm
6 ga./12.7mm4 #3
H
```
Fig. 8. Layout corresponding to (a) the geometrical characteristics and (b) the typical geometrical reinforcing, from reference [48].
```
```
98 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
investigation conducted on twelve one-half-scale frame speci-
mens, are summarised in the paper by Mehrabi et al. [50] and
reported in more details in [49]. The study focused on RC frames
designed in accordance with code provisions, with and without
the consideration of strong earthquake loadings. A six-storey,
three-bay, reinforced concrete moment-resisting frame was
selected as a prototype structure. The design loads complied with
```
the specifications of the Uniform Building Code (UBC) (1991).
```
```
Two types of frames were considered: (i) a ‘‘weak’’ frame, repre-
```
sentative of existing reinforced concrete structures not designed
```
to resist to earthquake loadings; (ii) a ‘‘strong’’ frame, designed
```
for Seismic Zone 4 according to the UBC. In the present study the
results of a loaded specimen designed for Seismic Zone 4 are
considered. All the details of the considered specimen, identified
in the reference works by the number 7, are reported in the studies
[3,49,50]. Here, for the sake of comprehensiveness, the layout of
the frame, together with IFS geometrical and reinforcing character-
istics, are displayed in Fig. 13.
The considered specimen is characterised by a strong frame
with a strong solid type masonry infill and possesses an aspect
ratio, h/L, equal to 2/3, where h is the height and L is the width
of the infill. The ultimate resistance and failure were dominated
by the Corner Crushing of the infill at a displacement of approxi-
mately 130 mm, and internal crushing at around 180 mm. In spite
of the presence of a strong panel, no shear failure was observed in
the columns. The aim of simulating the nonlinear cyclic experi-
mental behaviour, by means of the adoption of simple constitutive
laws, has been pursued by means of the following assumptions for
the reinforced concrete frame and the infilled masonry. The nonlin-
ear cyclic behaviour of the reinforced concrete has been modelled
according to a bilinear-envelope Takeda scheme [53] as reported in
Table 4.
For the simulation of the cyclic degrading hysteretic behaviour
of the masonry infill, subjected to a combination of vertical loads
and to a sequence of lateral load reversals, the use of an idealised
bi-or tri-linear resistance envelope is recommended [40]. Here,
the shear-diagonal behaviour of the masonry infill has been mod-
elled by means of an idealised bi-linear envelope, consistent with
the approach reported in [32] for unreinforced masonry, whose rel-
evant parameters are summarised in Table 5, these have been cho-
sen by considering the experimental data reported in [3], which
also contain the results of shear sliding experimental tests. The
parameter K o represents the initial slope of the idealised envelope,
```
in the post-yielding behaviour, the kinematic hardening (or soften-
```
```
ing) is governed by the parameter a, that is given by
```
a ¼ H d max  Hmaxdmax  dH maxð4Þ
where Hmax is the resistance at the elastic limit, Hdmax is the resis-
tance at the ultimate displacement and dHmax and dmax are the cor-
responding displacements of the envelope curve.
The unloading stiffness has been expressed according to the fol-
lowing simple expression
Table 2
Case study 1. Mechanical characteristics of concrete and steel.
Concrete Steel
```
E (MPa) rc (MPa) rt (MPa) ec0 (%) ecu (%) w (kN/m 3) E (GPa) fy (MPa) eu (%)
```
29,992 38.50 1.50 0.20 0.35 25 200 377 10
Table 3
Case study 1. Mechanical characteristics of masonry infill.
Flexural
w
```
(kN/m 3)
```
E
```
(MPa)
```
rc
```
(MPa)
```
rt
```
(MPa)
```
```
k (cm)
```
18 2500 5.00 0.15 10
Shear diagonal
```
G (MPa) fv0 (MPa) lc
```
1000 0.30 0.15
Shear sliding
```
(horizontal) (vertical)
```
```
c (MPa) l c (MPa) l
```
0.30 0.4 0.7 0.5
base shear [KN]
0
10
20
30
40
0 10 20 30 40
top displacement [mm]
base shear [KN]
0
25
50
75
100
0 10 20 30 40
top displacement [mm]
```
(b)(a)
```
```
Fig. 9. Numerical simulation of experimental tests on the (a) bare frame and (b) infill frame.
```
I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 99
0
20
40
60
80
100
0 10 20 30 40
base shear [KN]
top displacement [mm]
0
20
40
60
0 10 20 30 40
base shear [KN]
top displacement [mm]
```
(a) (b)
```
Fig. 10. Masonry and frame contribution to base shear.
0
20
40
60
80
0 2 4 6 8 10
base shear [KN]
top displacement [mm]
μ
μ
μ
0
20
40
60
80
0 2 4 6 8 10
base shear [KN]
top displacement [mm]
μ
μ
μ
Fig. 11. Base shear versus top displacement for different values of the shear sliding paramenters.
```
(b)(a)
```
```
(d)(c)
```
```
Fig. 12. Collapse behaviour. Damage scenario: (a) experimental test, (b) numerical model; Flexural moment distribution in the frame for different values of drift: (c) 7.5 mm,
```
```
and (d) 40 mm.
```
```
100 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
K u ¼ K oK IK o
 b
ð5Þ
where K o is the initial stiffness, KI is the value of the stiffness that is
obtained by connecting the point corresponding to the current
plastic deformation with the origin of the axes and b is a real num-
ber that can assume a value in the range 0–1. The re-loading stiff-
ness Kr, in the cyclic behaviour, has been set by returning to the
point which corresponds to the maximum reached plastic
deformation.
The flexural behaviour is governed by the orthogonal interface
springs. These have been calibrated according to an elastic-per-
fectly-plastic constitutive law, with different tensile and compres-
sive limits, as specified in Table 5, and an unloading stiffness
```
expressed according to Eq. (5) with b = 0.8. Furthermore, the duc-
```
tility of the orthogonal springs has been considered infinite in com-
pression and equal to 1.5 under tensile actions.
Fig. 14 reports the comparisons between the experimental and
numerical results in terms of base shear versus the top displacement.
In Fig. 15 a comparison between the experimental observed failure
mechanism and the simplified numerical prediction, is reported.
Fig. 16 reports, separately, the contributions of the interacting
frame and of the infill obtained by the numerical simulation. It
can be observed how the infill is characterised by a strong degrad-
ing behaviour, that has been controlled simply by setting the
parameters of the assumed constitutive law, consistent with a bi-
linear degrading envelope.
The low contribution of the infill, after several cyclic loads, and
its brittle behaviour is consistent with the actual failure mecha-
nism, reported in the Fig. 15a, in which the masonry infill appears
severely damaged.
Keeping in mind that both the reinforced concrete and the
masonry infill have been calibrated according to very simple con-
stitutive laws, by observing the maximum reached forces and the
exhibited hysteretic behaviour, the agreement between the exper-
imental and numerical results can be considered satisfactory.
254
203
420
F2 F1 F1 F2
8 #5
229
2 #5
92
92
254
203
280280 430
152
4 #6
203
203
420
Lateral force
1422
230
360
254178178254 2133
6 #54 #4
```
Fig. 13. Layout corresponding to (a) the geometrical characteristics and (b) the typical geometrical reinforcing, from reference [3].
```
Table 4
Case study 2. Mechanical characteristics of concrete and steel.
```
E (MPa) rc (MPa) rt (MPa) ec0 (%) ecu (%) w (KN/m3) Cyclic behaviour
```
Concrete
18,670 25.46 1.00 0.20 0.35 25
```
E (GPa) f y (MPa) eu (%)
```
Steel
200 420 10
Table 5
Case study 2. Mechanical characteristics of masonry infill.
```
Flexural w (kN/
```
```
m3)
```
E
```
(MPa)
```
rc
```
(MPa)
```
rt
```
(MPa)
```
k
```
(cm)
```
18 2100 5.00 0.15 10
Shear diagonal G
```
(MPa)
```
f v0
```
(MPa)
```
lc a
```
(%)
```
b
750 0.70 0.40 7.5 0.8
Shear sliding
```
(horizontal) (vertical)
```
```
c (MPa) l c (MPa) l
```
0.2 0.8 0.4 0.8
I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 101
The choice of a simple constitutive law is justified by the goal
of proposing a method suitable for practical applications and
based on a limited number of parameters, however the proposed
model is able to account for more complex constitutive
behaviours.
4.3. Influence of the model discretization: from macro- to micro-
modeling
In the considered approach each macro-element inherits the
geometry of the masonry portion that represents, this aspect con-
stitutes a great advantage that is not common to all the simplified
approaches based on a macro-element discretization.
Furthermore the consistent geometry of the element allows an
easy implementation of openings in the infills and permits the
implementation of models characterised by different level of dis-
cretization according to different mesh resolutions and to the
fine-tuning of nonlinear links of the interfaces, this latter associ-
ated to the distance between the NLinks k.
In Fig. 18 the results of push-over-analyses, performed on the
non-ductile model considered in Section 4.2, associated to different
mesh resolutions are reported. Further four different mesh resolu-
tions have been considered whose increasing computational cost is
summarised in Table 6.
Mesh A corresponds to the basic mesh size in which the infill is
modelled by a single macro-element. Mesh B and D represent more
base shear [KN]
displacement [mm]
base shear [KN]
displacement [mm]
```
(b)(a)
```
```
Fig. 14. Base-shear versus top displacement: (a) experimental results; and (b) numerical simulations.
```
```
Fig. 15. Collapse behaviour. Damage scenario: (a) experimental test, and (b) numerical model.
```
base shear [KN]
top displacement [mm]
base shear [KN]
top displacement [mm]
```
(a) (b)
```
```
Fig. 16. Contribution of interacting frame (a) and infill masonry panel (b).
```
```
102 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
refined mesh resolutions in which the infill is represented by 2  2
and 4  4 macro-elements respectively while the 3  3 mesh, con-
sidered in the simulation reported in Section 4.1, has been identi-
fied as C.
Mesh M is relative to a detailed model in which each discrete-
element corresponds to a single brick and is assigned to represent
both the brick and the mortar joints properties according to the
correspondence reported in Fig. 17a and b. In Fig. 17c–f a shrink
representation of the macro-element is reported, although the ele-
ment-interfaces have zero thickness, with the aim to show the
nonlinear links of the interfaces. In the same figures it is high-
lighted how the nonlinear links are delegated to represent the
mortar joints and the deformability of bricks by indicating the cor-
responding influence area.
The parameters used in the micro-model refined simulation are
summarized in Table 7.
This micro-element application shows the capability of the dis-
crete element to be used on a different scale, versus a micro-model
representation.
From Fig. 18 it can be observed a small sensitivity to the mesh
size and very good agreement between the micro and macro-
model numerical simulations. It is worth highlighting that, to the
author knowledge, this is the first simplified approach that can
be used both at macro- and micro-scale.
Furthermore the micro-model approach can also be used for
validating and better calibrating the macro-model parameters,
which is a great advantage.
In Fig. 19 simplified representations of the damage scenarios
corresponding to the mesh A, B, D, M are reported. All the simula-
tions show collapse mechanisms which produce a shear-diagonal
Table 6
Computational resources associated to the considered discretizations.
Mesh Number of elements Number of degrees of freedom
Panels Frames Panels Frames Total
A 1 3 4 6 10
B 4 6 16 15 31
C 9 9 36 24 60
D 16 12 64 33 97
M 143 40 572 117 689
Micro Model discretizationMasonry portion Mechanical scheme
Longitudinal Springs Orthogonal SpringsDiagonal Springs
```
(a) (b) (c)
```
```
(d) (e) (f)
```
```
Fig. 17. The micro-model discretazation. (a) The geometrical layout; (b) the discretization; (c) the mechanical representation; (d) the influence area of the diagonal springs;
```
```
(e) the influence areas of the longitudinal springs, and (f) the influence area of orthogonal springs.
```
Table 7
Mechanical characteristics of micro model.
```
Flexural w (kN/m3) E (MPa) rc (MPa) rt (MPa)
```
18 2500 5.00 0.15
```
Shear diagonal G (MPa) f v0 (MPa) lc
```
1500 Linear elastic Linear elastic
```
Shear sliding (horizontal) (vertical)
```
```
c (MPa) l c (MPa) l
```
0.30 0.4 0.7 0.5
0
25
50
75
100
0 10 20 30 40
base shear [KN]
top displacement [mm]
```
Fig. 18. Influence of the mesh discretization of single-bay RC infilled frame; base
```
shear as a function of the top horizontal displacement.
I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 103
```
Fig. 19. Influence of the mesh discretization of single-bay RC infilled frame; Simplified representations of the damage scenario predicted numerically.
```
0
20
40
60
80
0 10 20 30 40
base shear [KN]
top displacement [mm]
0
20
40
60
80
0 10 20 30 40
base shear [KN]
top displacement [mm]
```
(1)
```
```
(2)
```
d1 d2 d3
```
(3)
```
w1 w2 w3
```
Fig. 20. Influence of openings in the macro-model numerical simulation of single-bay RC infilled frame; (1) base shear as a function of top displacement; (2) damage scenario
```
```
in the presence of door openings; and (3) damage scenario in the presence of windows openings.
```
```
104 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
failure with damage on the frame. In particular, the micro-model
simulation provides results in better agreement with the experi-
mental damage scenario reported in Fig. 12a.
4.4. Modelling of openings in the masonry infills
As highlighted in the previous paragraph, since each discrete-
element is assigned to represent the nonlinear behaviour of the
corresponding macro-portion, as in a finite element simulation,
this approach allows a simple modelling in the presence of
openings.
Although this important feature should require an extensive
investigation and a possible validation with experimental results,
in this context, for the sake of conciseness, it is shown how the pro-
posed approach leads to a straightforward and reliable modelling
of openings in the Infilled Frame Structures.
With reference to the RC masonry infilled frame analysed in
Section 4.1, the influence of a central door and window openings
in the masonry infill are examined.
The first investigation, reported in Fig. 20, analyses the reduc-
tion of the base shear due to the presence of central door or win-
dow openings, of various dimensions, characterised by a width bo
and a height h o. Each geometrical layout is identified by the ratio
```
ao = bo/bi, between the width bo of the opening and the width bi
```
of the infill, and the aspect ratio ko = ho/bo, as reported in Table 8.
The results are expressed in terms of base shears as function of
the top displacements and are compared with the corresponding
values of the bare frame and of the infilled frame without
openings.
Table 8
Geometrical characteristics of the openings.
d1 d2 d3 w1 w2 w3
```
ao = bo/b i 1/3 1/2 3/5 1/3 1/2 3/5
```
```
ko = ho/b o 2 1.5 1 1 2/3 1/2
```
0
20
40
60
80
0 10 20 30 40
base shear [KN]
top displacement [mm]
0
20
40
60
80
0 10 20 30 40
base shear [KN]
top displacement [mm]
```
(a) (b)
```
```
Fig. 21. Comparison between micro- and macro-model simulations in terms of base shear versus top displacement; (a) door openings; and (b) windows openings.
```
```
Fig. 22. Comparison between micro- and macro-model simulations in terms of collapse mechanisms; (a) door openings; and (b) windows openings.
```
I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 105
With the aim to obtain a numerical validation of the obtained
results, Fig. 21 reports a comparison, in terms of base shear as a
```
function of top displacement, between the macro- and the micro-
```
model simulations with reference to the cases identified as d2
and w2. Furthermore, Fig. 22 reports a simplified representation
of the corresponding collapse mechanisms. A strong correlation
between the basic macro-model and the refined micro-model pre-
dictions can be observed.
5. Conclusions
Infilled Frame Structures represent a high percentage of existing
and new buildings in many seismically prone areas around the
world. These composite structural systems are governed by the
interaction between frame and infill walls. The high nonlinear
response of the masonry infill and the ever-changing contact con-
ditions along the frame-infill interfaces make the simulation of the
nonlinear behaviour of an infilled frame building a challenging
problem currently involving many research groups worldwide.
In this context, an alternative innovative approach for the simu-
lation of the seismic behaviour of Infilled Frame Structures, suitable
both for research and current engineering practice applications, is
presented in this paper. In this approach, the infilled wall is mod-
elled by means of an innovative discrete element, originally con-
ceived for the simulation of the nonlinear response of
Unreinforced Masonry Building [32], while the reinforced concrete
frame is modelled by means of inelastic beam–column elements in
which the plastic hinges can form at different positions along the
beam-span. The computational cost of the proposed numerical
approach is significantly lower in comparison to the nonlinear finite
element modelling, which requires both discretization of the frame
and the infill. Furthermore, the adopted strategy, based on a combi-
nation of finite element and macro-element discretization, offers
many advantages with respect to the existing simplified methods
in which the contribution of the infill is represented by one or more
diagonal struts. The equivalence between the masonry portion and
the macro-element is based on very simple physical considerations
founded on a fiber element calibration [32] and the interpretation
of the numerical results is simple, straightforward and unambigu-
ous. Since each discrete-element is assigned to represent the non-
linear behaviour of the corresponding macro-portion, as in a finite
element simulation, this approach allows a simple modelling
including the presence of openings and can be used on different
scales, from macro- to micro-modelling, although its use has been
conceived in the context of macro-elements. The effectiveness of
the proposed modelling strategy has been evaluated by means of
nonlinear monotonic and cyclic static analyses performed on RC
masonry infilled frame which have been the object of theoretical
and experimental research. The results seem to indicate that the
proposed approach can be adequate for seismic assessments and
the design of Infilled Frame Structures since it requires very low
computational resources, allows easy interpretation of results and
provides satisfactory accuracy.
Acknowledgement
This research has been supported by the Italian Network of
```
Seismic Engineering University Laboratories (ReLUIS).
```
References
```
[1] Buonopane SG, White RN. Pseudodynamic testing of masonry infilledreinforced concrete frame. J Struct Eng 1999;125(6):578–89.
```
```
[2] D’Ayala D, Worthb J, Riddle O. Realistic shear capacity assessment of infillframes: comparison of two numerical procedures. Eng Struct 2009;31:
```
1745–61.
```
[3] Mehrabi A, Benson Shing P, Schuller M, Noland J. Experimental evaluation ofmasonry-infilled RC frames. J Struct Eng 1996;122(3):228–37.
```
```
[4] Madan A, Reinhorn AM, Mander JB, Valles RE. Modeling of masonry infillpanels for structural analysis. J Struct Eng 1997;123(10):1295–302.
```
```
[5] Singh H, Paul DK, Sastry VV. Inelastic dynamic response of reinforced concreteinfilled frame. Comput Struct 1998;69:685–93.
```
```
[6] Asteris PG. Finite element micro-modeling of infilled frames. Electron J StructEng 2008;8:1–11.
```
```
[7] Asteris PG, Antoniou ST, Sophianopoulos D, Chrysostomou CZ. Mathematicalmacromodeling of infilled frames: state of the art. J Struct Eng (ASCE)
```
```
2011;137(12):1508–17.[8] Polyakov SV. On the interaction between masonry filler walls and enclosing
```
```
frame when loading in the plane of the wall. In: Translation in earthquakeengineering. San Francisco: Earthquake Engineering Research Institute; 1960.
```
p. 36–42.[9] Holmes M. Steel frame with brickwork and concrete infilling. Reader in civil
```
engineering. Inst Technol, Bradford 1961;19(4):473–8.[10] Smith BS. Behavior of square infilled frames. J Struct Div 1966;92(1):381–403.
```
```
[11] Smith BS, Carter C. A method of analysis for infilled frames. ICE Proc, Inst CivilEng 1969;44(1):31–48.
```
[12] Mainstone RJ, Weeks GA. The influence of bounding frame on the rackingstiffness and strength of brick walls. In: Proceedings of 2nd Int. brick masonry
```
conf., building research establishment, Watford, England; 1970. p. 165–71.[13] Mainstone RJ. On the stiffnesses and strengths of infilled frames. ICE Proc, Inst
```
```
Civil Eng 1971;4:57–90.[14] Abdul-Kadir MR. The structural behaviour of masonry infill panels in framed
```
```
structures. PhD thesis. Edinburgh: University of Edinburgh UK; 1974.[15] Bazan E, Meli R. Seismic analysis of structures with masonry walls. In:
```
```
Proceedings of 7th World Conference on Earthquake Engineering, vol. 5.International Association of Earthquake Engineering (IAEE), Tokyo; 1980. p.
```
```
633–40.[16] Tassios TP. Masonry infill and RC walls (an invited state-of the-art report). In:
```
```
Proceedings of 3rd international symposium on wall structures, centre forbuilding systems, research and development, Warsaw, Poland; 1984.
```
```
[17] Liauw TC, Kwan KH. Nonlinear behaviour of nonintegral infilled frames.Comput Struct 1984;18:551–60.
```
[18] Decanini LD, Fantin GE. Modelos simplificados de la mampostería incluida enporticos. Características de rigidez y resistencia lateral en astado límite.
```
Jornadas Argentinas de Ingeniería Estructural III, Asociacion de IngenierosEstructurales, Buenos Aires, Argentina 1987; 2:817–836 (in Spanish).
```
```
[19] Paulay T, Pristley MJN. Seismic design of reinforced concrete and masonrybuildings. New York: Wiley; 1992. pp. 744.
```
[20] Durrani AJ, Luo YH. Seismic retrofit of flat-slab buildings with masonry infills.In: Proceedings of NCEER workshop on seismic response of masonry infills,
```
National Center for Earthquake Engineering Research (NCEER), Buffalo, NY;1994.
```
```
[21] Thiruvengadam V. On the natural frequencies of infilled frames. EarthquakeEng Struct Dyn 1985;13(3):401–19.
```
```
[22] FEMA. Prestandard and commentary for the Seismic Rehabilitation ofBuildings. FEMA-356, Washington, DC; 2000.
```
[23] Syrmakezis CA, Vratsanou VY. Influence of infill walls to RC frames Response.In: Proceedings of 8th European conference on earthquake engineering,
```
European Association for Earthquake Engineering (EAEE), Istanbul, Turkey;1986. p. 47–53.
```
[24] Chrysostomou CZ. Effects of degrading infill walls on the nonlinear seismicresponse of two-dimensional steel frames. PhD thesis. Ithaca: Cornell
```
University, NY; 1991.[25] Saneinejad A, Hobbs B. Inelastic design of infilled frames. J Struct Eng
```
```
1995;121(4):634–50.[26] Chrysostomou CZ, Gergely P, Abel JF. A six-strut model for nonlinear
```
```
dynamic analysis of steel infilled frames. Int J Struct Stab Dyn 2002;2(3):335–53.
```
[27] El-Dakhakhni WW. Non-linear finite element modeling of concrete masonry-infilled steel frame. MS thesis. Philadelphia: Drexel University, Civil and
```
Architectural Engineering Dept; 2002.[28] El-Dakhakhni WW, Elgaaly M, Hamid AA. Finite element modeling of concrete
```
```
masonry infilled steel frame. In: Proceedings of 9th Canadian masonrysymposium, National Research Council (NRC), Ottawa, Canada; 2001.
```
[29] El-Dakhakhni WW. Experimental and analytical seismic evaluation of concretemasonry-infilled steel frames retrofitted using GFRP laminates. PhD thesis.
```
Philadelphia: Drexel Univ; 2002.[30] Crisafulli FJ, Carr AJ. Proposed macro-model for the analysis of infilled frame
```
```
structures. Bull New Zealand Soc Earthquake Eng 2007;40(2):69–77.[31] Caliò I, Marletta M, Pantò B. A simplified model for the evaluation of the
```
seismic behaviour of masonry buildings. In: Proceedings of the 10thinternational conference on civil, structural and environmental engineering
computing. Stirlingshire, UK: Civil-Comp Press 2005, Paper 195.[32] Caliò I, Marletta M, Pantò B. A new discrete element model for the evaluation
```
of the seismic behaviour of unreinforced masonry buildings. Eng Struct2012;40:327–38.
```
[33] Caliò I, Cannizzaro F, D’Amore E, Marletta M, Pantò B. A new discrete-elementapproach for the assessment of the seismic resistance of composite reinforced
```
concrete-masonry buildings. In: Proceedings of AIP (American Institute ofPhysics); 2008. p. 832–839.
```
[34] Nucera F, Santini A, Tripodi E, Cannizzaro F, Pantò B. Influence of geometricaland mechanical parameters on the seismic vulnerability assessment of
```
106 I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107
```
confined masonry buildings by macro-element modeling. In: Proceedings of15th World Conference on Earthquake Engineering 24–28 September 2012.
[35] Nucera F, Tripodi E, Santini A, Caliò I. Seismic vulnerability assessment ofconfined masonry buildings by macro-element modeling: a case study. In:
Proceedings of 15th world conference on earthquake engineering 24–28September 2012.
[36] Marques R, Lourenco PB. Pushover seismic analysis of quasi-static testedconfined masonry buildings through simplified model. In: Proceedings of the
```
15th international brick and block masonry conference, Florianopolis; 2012.[37] Marques R, Lourenco PB. A model for pushover analysis of confined masonry
```
```
structures: implementation and validation. Bull Earthquake Eng2013;11:2133–50.
```
```
[38] Marques R. New methodologies for seismic design of unreinforced andconfined masonry structures. PhD thesis. Guimarães: University of Minho;
```
2012. <http://www.civil.uminho.pt/masonry>.[39] 3DMacro. Il software per le murature (3D computer program for the seismic
```
assessment of masonry buildings). Gruppo Sismica s.r.l., Catania, Italy. Release3.0, March 2014. <http://www.3dmacro.it>.
```
[40] Tomazevic M. Earthquake-Resistant Design of Masonry Building. Series onInnovation in Structures and Construction – Vol. 1. Series Editor: A.S. Elnashai
```
& P.J. Dowling. London: Imperial College Press; 2006.[41] Eurocode 6: Design of masonry structures, Part 1–1: General rules for
```
```
buildings. Rules for reinforced and unreinforced masonry. ENV 1996-1-1:1995 (CEN, Brussels, 1995).
```
[42] Turnsek V, Cacovic F. Some experimental result on the strength of brickmasonry walls. In: Proceedings of the 2nd international brick masonry
```
conference. Stoke-on-Trent; 1971. p. 149–56.
```
```
[43] Corradi M, Borri A, Vignoli A. Experimental study on the determination ofstrength of masonry walls. Constr Build Mater 2003;17:325–37.
```
[44] Turnsek V, Sheppard P. The shear and flexural resistance of masonry walls. In:Proceedings of international research conference on earthquake engineering,
```
IZIIS, Skopje; 1981. p. 517–73.[45] Jirasek M, Bazant Z. Inelastic analysis of structures. Wiley; 2001.
```
```
[46] Zienkiewicz OC, Taylor RL. The finite element method vol. 2 Solid Mechanics(fifth edition), Butterworth Heinemann; 2000.
```
[47] Kadysiewski S, Mosalam KM. Modeling of Unreinforced Masonry Infill WallsConsidering In-Plane and Out-of-Plane Interaction. PEER Report 2008/102,
```
Berkeley; 2009. pp. 144.[48] Al-Chaar G, Issa M, Sweeney S. Behavior of masonry-infilled nonductile
```
```
reinforced concrete frames. J Struct Eng 2002;128(8):1055–63.[49] Mehrabi AB, Shing PB, Schuller MP, Noland JL. Performance of masonry-infilled
```
```
R/C frames under in-plane lateral loads. Struct Eng and Struct Mech res series,Report CD/SR-94/6; 1994. pp. 237.
```
```
[50] Mehrabi AB, Shing PB. Finite element modeling of masonry-infilled RC frames.J Struct Eng 1997;123(5):604–13.
```
[51] Marques R, Lourenço PB. Possibilities and comparison of structural componentmodels for the seismic assessment of modern unreinforced masonry buildings.
```
Comput Struct 2011;89:2079–91.[52] Marques R, Lourenço PB. Unreinforced and confined masonry buildings in
```
```
seismic regions: validation of macro-element models and cost analysis. EngStruct 2014;64:52–67.
```
```
[53] Takeda T, Sozen MA, Nielsen NN. Reinforced concrete response to simulatedearthquakes. J Struct Div 1970;96(12):2557–73.
```
##### I. Caliò, B. Pantò / Computers and Structures 143 (2014) 91–107 107