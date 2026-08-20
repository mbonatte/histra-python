# R E S E A R C H A R T I C L E
Assessment of the dynamic response of unreinforced
masonry structures using a macroelement modeling
approach
César Chácara1 | Francesco Cannizzaro 2 | Bartolomeo Pantò 2 | Ivo Caliò2 |
Paulo B. Lourenço1
1 Department of Civil Engineering, ISISE,
University of Minho, Guimarães, Portugal
2 Department of Civil Engineering and
Architecture, University of Catania,
Catania, Italy
Correspondence
César Chácara, Department of Civil
Engineering, ISISE, University of Minho,
Azurém, 4800‐058 Guimarães, Portugal.
```
Email: c.chacara@pucp.pe
```
Funding information
Innovate Perú‐Fondo para la Innovación,
Ciencia y Tecnología, Grant/Award Num-
```
bers: PhD grant BECA‐1‐P‐078‐13 and
```
```
BECA‐1‐P‐078‐13; Foundation for Science
```
and Technology, Grant/Award Number:
```
POCI‐01‐0145‐FEDER‐007633; FEDER /
```
```
ERDF: “Fundo Europeu de
```
Desenvolvimento Regional / European
Regional Development Fund”
Summary
The seismic performance of unreinforced masonry structures is strongly associ-
ated with the interaction between in‐plane and out‐of‐plane mechanisms. The
seismic response of these structures has been thoroughly investigated by means
of experimental testing, analytical procedures, and computational approaches.
Within the framework of the numerical simulations, models based on the finite
element method provide a good prediction of the seismic performance of unre-
inforced masonry structures. However, they usually require a high computa-
tional cost and advanced user expertise to define appropriate mechanical
properties and to interpret the numerical results. Because of these limitations,
simplified models for practical applications have been developed during the
last decades. Despite this, a great number of these models focus mostly on
```
the evaluation of the in‐plane response, assuming box (or integral) behavior
```
of the structure. In this paper, a simplified macroelement modeling approach
is used to simulate the seismic response of 2 masonry prototypes taking into
consideration the combined in‐plane and out‐of‐plane action. The numerical
investigations were performed in the static and dynamic fields by using push-
over analyses and nonlinear dynamic analyses respectively. The latter is a
novel implementation of a model previously developed for static analysis.
The results obtained from this study are in good agreement with those pro-
vided by a detailed nonlinear continuum FE approach, demonstrating the
applicability of this macroelement model with a significant reduction of the
computational cost.
KEYWORDS
dynamic nonlinear analysis, finite element model, in‐plane mechanisms, out‐of‐plane mechanisms,
static nonlinear analysis
1 | INTRODUCTION
```
The behavior of existing unreinforced masonry (URM) structures subjected to dynamic loading and the corresponding
```
```
seismic performance are still considered a complex task because of (i) the high nonlinearity of the masonry, as
```
```
Received: 18 July 2017 Revised: 5 June 2018 Accepted: 7 June 2018
```
```
DOI: 10.1002/eqe.3091
```
```
2426 © 2018 John Wiley & Sons, Ltd. Earthquake Engng Struct Dyn. 2018;47:2426–2446.wileyonlinelibrary.com/journal/eqe
```
```
heterogeneous, anisotropic, and quasi‐brittle material; (ii) the complex structural response which involves several non-
```
```
linear interaction mechanisms between vertical and horizontal elements; and (iii) the presence of complex and irregular
```
geometries which often include modifications and alterations difficult to survey.1 The nonlinear dynamic behavior of
this type of structures, characterized by the combination of in‐plane and out‐of‐plane mechanisms, has been widely
investigated in the literature by means of experimental campaigns, analytical formulations, and numerical simula-
tions. 2-4 In addition, several contributions have been provided from different authors aiming at the definition of refined
and simplified numerical strategies for simulating the structural response in the presence of horizontal loads. However,
a general agreement regarding the most appropriate methods for assessing the seismic response and capacity of URM
structures has not yet been achieved. 2
During a seismic event, the out‐of‐plane behavior of URM masonry structures represents the most dangerous col-
lapse mechanism as it has been evidenced by means of postearthquake surveys. Ordinary masonry buildings, for which
a box‐type behavior is guaranteed, can be conventionally and effectively studied by means of simplified models which
neglect the out‐of‐plane mechanisms. On the contrary, the buildings that do not guarantee a box behavior, mainly rep-
```
resented by historical buildings, require sophisticated modeling approaches, namely the finite element method (FEM)
```
```
or the distinct element method (DEM). As an example, in‐depth assessments of the seismic performances of URM struc-
```
tures, such as masonry churches, for which the out‐of‐plane behavior is crucial, are currently object of important aca-
demic studies. 5-7
Advanced tools based on the FEM are the most used approaches for a rigorous assessment of masonry structures. Nev-
ertheless, such approaches do not only require the definition of complex constitutive laws, together with large computa-
tional cost for sophisticated analyses, but a high expertise for an accurate interpretation of the numerical results,
making them less suitable for practical purposes. In this scope, several numerical models, based on simplified mechanical
schemes, have been developed as alternative tools for the seismic assessment of masonry structures subjected to static and
dynamic loading. The most diffused of these approaches are related to equivalent frame models. 8-10 Others, more refined,
are based on bidimensional models 11-13 which are geometrically coherent to the 2D kinematics of masonry panels. How-
ever, both approaches allow an effective assessment of the in‐plane response of masonry walls leading to a box‐type behav-
ior simulation of the masonry structure neglecting the out‐of‐plane response of the masonry walls. An interesting review of
the state of the art on this topic is reported in Marques and Lourenço. 14 In this regard, the assessment of the out‐of‐plane
capacity of the structure can be conducted independently through a simplified evaluation based on limit analysis
approaches, 4,15,16 but the reliability of this process is difficult to assess. On the other hand, there are, available in the liter-
ature, a few number of refined and simplified numerical models capable of simulating both the in‐plane and out‐of‐plane
responses and their interaction. 7,17 These models can be effectively used for assessing the seismic performance of existing
and monumental buildings whose response is governed by the out‐of‐plane behavior of masonry walls.
This paper reports a numerical investigation on the seismic behavior of 2 URM structures which were experimen-
tally tested by means of shaking table tests 18 to investigate their out‐of‐plane capacity against seismic excitations. A pri-
mary numerical prediction of the seismic performance of these structures was conducted and reported by Mendes
et al. 19 The out‐of‐plane response of these structures was further investigated by means of analytical procedures based
on rigid‐body mechanism, 20 and different numerical models based on the FEM, 21,22 DEM,23 combined FEM‐DEM, 24
and macroelement method. 25 A summary of these investigations was presented by de Felice et al. 2 The present work
corresponds to an extension of the investigation conducted by Cannizzaro and Lourenço, 25 in which a preliminary study
of these 2 structures was presented. The latter was limited to static nonlinear analyses carried out by means of the
macroelement modeling approach proposed in Pantò et al26 using simple constitutive laws. The 2 main goals of this
paper consist on the adoption of more reliable and sophisticated constitutive laws for the tensile and compressive behav-
ior of masonry suitable to be used in static pushover analyses and to a nontrivial extension of the numerical investiga-
tions into nonlinear time history analyses. The aim of this study is related to the assessment of the accuracy of the
proposed macroelement modeling approach in reproducing the out‐of‐plane failure mechanisms of full‐scale URM
structures composed by different masonry arrangements.
The results obtained from this investigation were compared in load capacity, hysteretic response, and collapse mech-
```
anism the finite element (FE) models presented by Chácara et al, 21 using the DIANA software 27 and with the observed
```
experimental results. 18 The considered modeling strategy, which has been successfully used to simulate the nonlinear
behavior of URM structures in the nonlinear static context, demonstrates its suitability and reliability also with regard
to the dynamic field. In addition, because of its computational efficiency, it opens a significant perspective toward the
practical adoption of nonlinear dynamic analyses to assess the seismic performance of URM structures, also considering
their out‐of‐plane response.
CHÁCARA ET AL . 2427
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
2 | MACR OELEMENT MODEL
The seismic assessment of the masonry prototypes was conducted by means of the macroelement model introduced by
Caliò et al, 13 and further upgraded by Pantò et al 26 as an extension of the model to a 3‐dimensional kinematics. The
initial concept of this macroelement model aimed at the simulation of the main in‐plane failure mechanisms of
URM structures, namely flexural, shear‐diagonal, and shear‐sliding. It is worth noting that because of the mechanical
scheme, the influence of the out‐of‐plane mechanisms is not taken into consideration. Each panel or macroelement cor-
```
responds to a quadrilateral made of rigid edges connected by hinges and a diagonal nonlinear link (see Figure 1A). An
```
interface element, composed by a discrete distribution of nonlinear links, is used for the connection of adjacent panels,
or the connection of panels to other types of elements such as restraints. The main in‐plane failure mechanisms are sim-
ulated by the nonlinear links at the panels, and at the interface elements. The flexural response is governed by the dis-
crete distribution of nonlinear links which are placed orthogonally to the length of the interface element. The shear‐
sliding is ruled by an additional nonlinear link along the length of the interface element. Finally, the nonlinear diagonal
link at each panel simulates the shear‐diagonal mechanism. Each plane macroelement is characterized by 4 degrees of
```
freedom (DOFs): 3 related to the rigid body motion and 1 corresponding to the in‐plane shear deformability.
```
The upgrade reported by Pantò et al26 consisted in the introduction of additional DOFs and new sets of nonlinear
links at the interface elements to simulate the torsion effects, and the out‐of‐plane mechanisms of URM structures.
The rigid edges are now replaced by rigid plates in a 3‐dimensional macroelement or panel. The interface elements
are composed by a matrix of m × n nonlinear links located perpendicularly to the surface of each connected element.
Two additional links were placed at the interface element along its thickness. The 3‐dimensional representation of
the macroelement is illustrated in Figure 1B. The matrix of nonlinear links, denoted as transversal links, is capable
of simulating the in‐plane and out‐of‐plane flexural response of masonry structures. Analogously to the plane
macroelement, a single nonlinear link along the length of the interface governs the in‐plane shear‐sliding behavior of
2 connected panels. The 2 additional longitudinal links, placed at the interface element along its thickness, rule the
out‐of‐plane shear‐sliding and the torsion of the panels. Finally, the in‐plane shear‐diagonal behavior is still governed
by the single nonlinear link at the macroelement. Based on this implementation, 3 additional DOFs are included in
the kinematics, leading to a total number of 7 DOFs for each element. The first 6 DOFs correspond to the translations
and rotations of the panel as a rigid body, whereas the seventh is related to the additional in‐plane shear deformability
DOF. It is worth to note that because the deformation of the interface elements is associated to a relative motion
between 2 adjacent panels, the introduction of additional DOFs is not required. An additional development was con-
```
ducted aiming at the representation of irregular macroelements (see Figure 1C) for the modeling of curved struc-
```
tures. 28,29 In addition, the proposed approach also allows the modeling of multiwythe masonry walls by means of a
set of panels in thickness whose connection along the width is conducted by means of cohesive interface elements.
```
(A) (B) (C)
```
```
FIGURE 1 Macroelement model: (A) initial plane mechanical scheme, (B) 3‐dimensional scheme with regular geometry, and (C) 3‐
```
dimensional scheme with irregular geometry [Colour figure can be viewed at wileyonlinelibrary.com]
2428 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
The plane macroelement has been implemented in the 3DMacro software 30 focused mainly for the assessment of
masonry buildings with box behavior. On the contrary, the HiStrA software31 was conceived for the seismic assessment
of monumental structures by means of spatial regular and irregular macroelements. Some applications related to the
seismic assessment of masonry structures were reported in Pantò et al7 and Cannizzaro. 25
2.1 | Calibration of transversal links
The transversal nonlinear links of the interface elements simulate the in‐plane and the out‐of‐plane flexural behavior of
the connected panels. Each link represents a strip of masonry corresponding to 2 adjacent elements along a given mate-
rial direction as illustrated in Figure 2A. The calibration of each link is conducted by means of a fiber discretization
approach that provides a couple of nonlinear links in series, which are further replaced by an equivalent one. Details
regarding the calibration procedure of the transversal nonlinear links, considering masonry as a homogeneous elasto‐
plastic material, are reported by Caliò et al13 and by Pantò et al.26 The nonlinear behavior of the transversal links used
in this study was based on a fracture energy approach, in which the tensile and compressive responses were governed by
exponential and parabolic curves respectively, as illustrated in Figure 2B. The yielding forces in tension F yt and com-
pression F yc are related to the corresponding tensile and compressive strengths of the homogeneous material, and
the influence area A s of each nonlinear link. The estimation of the ultimate displacement is based on the fracture energy
defined in tension Gft and compression Gfc. It is worth noting that throughout the calibration procedure, the crack band-
width is considered coincident to the mesh size discretization of the macroelements guaranteeing the independency of
the ductility from the mesh size.
The hysteretic behavior defined for the transversal nonlinear links was adapted from the cyclic constitutive model
introduced by Takeda,32 and implemented in the OpenSees framework. 33 Such hysteretic constitutive model is influ-
enced by an unloading coefficient denoted as β which ranges from 0 to 1. Figure 2C illustrates the cyclic response of
```
the transversal nonlinear links with exponential and parabolic curves for tension and compression (backbone curve).
```
It can be observed that, besides the backbone curve, there are 3 additional curves corresponding to different unloading
```
and reloading responses. The first unloading response (curves 3, 6, 9, and 12) is characterized by an unloading oriented
```
```
to the origin, in which the β coefficient corresponds to 1. The second unloading response (curves 3″, 6″, 9″, and 12″) is
```
```
(A) (C)
```
```
(B)
```
```
FIGURE 2 Transversal nonlinear links: (A) fiber calibration for a single masonry strip, (B) exponential and parabolic curves, and (C) cyclic
```
behavior related to the flexural response [Colour figure can be viewed at wileyonlinelibrary.com]
CHÁCARA ET AL . 2429
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
```
ruled by the initial stiffness, and the β coefficient is equal to 0. In the remaining unloading response (curves 3′, 6′, 9′,
```
```
and 12′), the β coefficient presents an intermediate value between 0 and 1. The unloading cycle finishes once the link
```
```
reaches a zero force, and the loading in the opposite direction begins. The reloading cycles (curves 4, 7, and 10) are ori-
```
ented to the maximum point at the backbone curve from the previous cycle. It is worth noting that tensile and compres-
sive behavior may present a different cyclic response, and therefore, coefficients βt and βc are defined in an independent
manner.
2.2 | Calibration of sliding link
The 3 additional nonlinear links located at the interface elements aim at simulating the shear‐sliding and torsion
responses of URM structures. In addition to the diagonal deformations, the overall in‐plane shear deformation of
URM structures is also constituted by the concentrated deformability along the mortar joints. This deformability is
related to the relative in‐plane sliding motion between 2 adjacent panels, and this behavior is reproduced by the single
nonlinear link along the length of the interface element. Each in‐plane sliding link is characterized by an influence area
```
A s, which corresponds to the total area of the interface element (see Figure 3A). The behavior of the link in the
```
preyielding phase is kept rigid. On the other hand, the out‐of‐plane shear deformability is solely simulated by 2 addi-
tional nonlinear links along the thickness of the interface element. These 2 links also govern the torsion around the axis
perpendicular to the interface plane. In the case of the out‐of‐plane sliding link, the influence area A s corresponds to
```
half of the interface surface (see Figure 3B). The calibration procedure of these links is based on an elasto‐plastic con-
```
stitutive law whose elastic stiffness is computed to simulate the overall out‐of‐plane shear stiffness on the panels. The
```
torsion elastic stiffness is obtained by evaluating the distance (d) between the links, which is determined enforcing
```
an equivalence between a discrete model and a reference elastic continuous beam model. Further details regarding
the calibration of these nonlinear links are presented in Caliò et al13 and Pantò 26
```
(A) (B)
```
```
FIGURE 3 Calibration of the shear‐sliding response: (A) in‐plane and (B) out‐of‐plane nonlinear links [Colour figure can be viewed at
```
wileyonlinelibrary.com]
2430 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
The ultimate strength of the in‐plane and out‐of‐plane links is associated to friction‐sliding phenomena along the
```
mortar joints. The yielding force F y of each link is ruled by the Mohr‐Coulomb criterion expressed in Equation (1),
```
which is related to the influence area As, to the cohesion c of the mortar joints, to friction coefficient μs, and to the
applied normal force N. The normal force N is obtained as the resultant force from the matrix of transversal links within
the influence volume of the considered longitudinal link.
```
F y ¼ c⋅A s þ μs⋅N (1)
```
Figure 4 illustrates the elasto‐plastic hysteretic behavior of the nonlinear sliding link in which the normal forces N
present a constant value. The cyclic behavior of the sliding links is governed by a perfectly elasto‐plastic hysteretic
```
model with unloading (curves 3, 9, 6, 12) and reloading (curves 4, 10, 7, 13) cycles governed by the initial stiffness.
```
The reloading cycle finishes once the nonlinear link reaches the yielding force associated to a current axial force N.
2.3 | Calibration of diagonal link
The diagonal nonlinear link is mainly associated to the in‐plane shear‐diagonal response of masonry panels. The cali-
bration in the initial elastic range of this link is obtained by enforcing an elastic equivalence between a single
macroelement and a finite portion of masonry. This finite portion of masonry is considered as a pure shear deformable
continuum plate defined by a shear modulus G, as illustrated in Figure 5. A more detailed description of the elastic cal-
ibration of the diagonal links is reported in Caliò et al, 13 Cannizzaro, 29 and Pantò.34 The nonlinear behavior of the diag-
onal link can be effectively described by 2 different yielding criteria: Mohr‐Coulomb or Turnsek and Cacovic, 35
```
expressed respectively in Equations (2) and (3) respectively.
```
```
F y ¼ F s0 þ μd⋅N (2)
```
F y ¼ F v0
ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi
N
1:5⋅F v0þ 1
r
```
(3)
```
Here, F y, F s0, and F v0 correspond respectively to the current yielding force and the yielding force under no confine-
ment conditions for Mohr Coulomb and Turnsek and Cacovic criteria respectively. N is related to the current normal
force, and μd is the friction coefficient for the shear‐diagonal mechanism. The definition of the F y0 and μd should be
conducted by means of a proper experimental test. 36,37
The hysteretic constitutive law that governs the cyclic response of the diagonal nonlinear links is also based on the
Takeda model. 32 Similarly to the transversal links, a βd coefficient is defined to characterize the unloading behavior
associated to the shear‐diagonal mechanism. Figure 6 illustrates the hysteretic response of a diagonal link in which
the 3 different responses related to the definition βd are depicted. It is worth noting that because of the adopted yielding
```
criterion, a symmetric hysteretic response (tension and compression) is assumed.
```
FIGURE 4 Cyclic constitutive model
for the in‐plane and out‐of‐plane sliding
nonlinear links [Colour figure can be
viewed at wileyonlinelibrary.com]
CHÁCARA ET AL . 2431
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
2.4 | Mass matrix
The definition of the mass matrix is based on the application of virtual displacements at each of the vertexes of a
macroelement as reported in Chácara et al.38 Two strategies, namely diagonal and consistent approaches, were taken
into consideration for the computation of such mass matrix. A validation of both approaches was conducted by means
of the comparison of the dynamic properties of masonry structures. It was evidenced that there is no significant differ-
ence in natural frequencies when using the 2 approaches. In this sense, the use of a lumped mass matrix is preferable
because it requires a lower computational cost.
3 | BRICK MASONRY PROTOTYPE
The first case study corresponds to a prototype of brick masonry subjected to shaking table tests at National Laboratory
for Civil Engineering in Lisbon, Portugal. 18 During the experimental campaign, the structure was loaded up to collapse
aiming at the assessment of the out‐of‐plane response because of dynamic solicitations. The brick masonry prototype
```
corresponds to a U‐shape structure composed by a main gable wall connected to 2 orthogonal walls (return walls) with
```
a constant thickness of 0.235 m. The main gable wall was characterized by a height of 2.75 m at the top of the tympa-
num and a length of 3.5 m, presenting a central window opening with a length and height of 0.80 m. Both return walls
were characterized by a height of 2.25 m and a length of 2.50 m. However, only 1 of the return presented a window
```
(A) (B)
```
```
FIGURE 5 Calibration of diagonal nonlinear link: (A) finite portion of masonry as a pure shear deformable media and (B) equivalent
```
macroelement [Colour figure can be viewed at wileyonlinelibrary.com]
FIGURE 6 Cyclic constitutive law for
diagonal nonlinear links [Colour figure
can be viewed at wileyonlinelibrary.com]
2432 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
opening in which the length and height corresponded to 0.80 and 1.00 m respectively. The geometric configuration of
the brick masonry prototype is illustrated in Figure 7A.
The prototype was subjected to 1‐directional horizontal component of dynamic excitation, oriented orthogonally to
the main gable wall. The tests were performed by applying a horizontal component of the 2011 Christchurch Earth-
```
quake (New Zealand) accelerogram with increasing intensities.18 The failure mechanism of the prototype was reached
```
when it was subjected to a PGA of 1.27 g, and consisted on the out‐of‐plane collapse of the tympanum at the main gable
```
wall, and the in‐plane collapse of the return wall with opening, mainly because of a rocking response (see Figure 7B, C).
```
A horizontal detachment in the lower part of the openings was also observed. It is worth noting that the return wall
without opening presented no significant damage during the shaking table tests. Further details concerning the exper-
imental campaign are reported in Candeias et al. 18
Aiming at the interpretation of the experimental campaign, numerical investigations regarding the assessment of the
out‐of‐plane response of this structure were carried out in Felice et al.2 Further numerical investigations by means of FE
continuum model, developed through DIANA software, 27 were carried out by Chácara et al.21 In the following sections,
a comparison between the latter and the numerical response obtained by the macroelement model is reported to provide
a numerical validation of this simplified modeling approach. This comparison is performed both in the static field
```
(through pushover analyses) and dynamic field, by means of nonlinear time history analyses.
```
The constitutive laws used in the DIANA 27 FE models correspond to 3 different total strain crack models: a rotating
one and 2 fixed ones. For the latter, a shear retention factor needs to be defined to simulate the behavior of the shear
stiffness, which mainly consists on its reduction once the material is subjected to damage. Constant shear retention fac-
tors of 0.2 and 0.05 were taken into consideration.21 Exponential and parabolic curves were selected for the description
of the tensile and compressive behaviors respectively. These behaviors were characterized by nonlinear parameters such
as strength and fracture energy for tension and compression. The definition of fracture energies was based on recom-
mended values provided by Lourenço. 39 It is worth noting that no additional properties that describe the material non-
linearity were defined because the behavior in tension and shear in the FE models is coupled.
```
In the case of the macroelement model, similar curves were used for the flexural response (tension and compres-
```
```
sion). Because this macroelement model is based on independent failure mechanisms, it was necessary to define addi-
```
tional mechanical properties for shear‐diagonal and shear‐sliding. In the case of the shear‐sliding mechanism, the
cohesion c under no confinement conditions is assumed to be equal to the tensile strength f t considering that the diag-
onal compression tests produced a uniform shear stress. 40,41 To simulate the degradation of the shear‐sliding strength, a
fracture energy G fs is assumed as 1.5 times the fracture energy in tension Gft. Finally, a value of 0.7 is assumed for the
shear‐sliding friction coefficient μs. The shear‐diagonal mechanisms described by the Mohr‐Coulomb criterion pre-
sented an assumed friction coefficient μd of 0.6. For the definition of the capacity associated with the shear‐diagonal
mechanism, a typical ratio of 1.5 between tensile strength f t and shear strength in absence of axial load f s0 was also
taken into consideration. Although such ratio has not general validity, it has been obtained by comparing the FEM
and the macroelement model for typical masonry walls subjected to horizontal increasing loads and exhibiting shear
diagonal failure response. The mechanical properties for the FE and macroelement models are summarized in
Table 1. It is worth noting that this structure was previously studied based on the same modeling approach by
Cannizzaro and Lourenço. 25 In such study, the flexural response was ruled by linear softening postpeak branches for
tensile and compressive behavior. In the current investigation, different approaches, regarding not only the flexural
but also the shear‐sliding responses, were considered for this investigation. These differences corresponded to the adop-
tion of exponential and parabolic laws for the nonlinear behavior in tension and compression respectively. On the other
```
(A) (B) (C)
```
```
FIGURE 7 Brick masonry prototype (A) and collapse mechanism from shaking table tests: (B) main gable wall and (C) return wall with
```
window opening18 [Colour figure can be viewed at wileyonlinelibrary.com]
CHÁCARA ET AL . 2433
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
hand, this investigation also considered the introduction of fracture energy in the shear‐sliding response leading to a
more pronounced softening behavior.
The FE model was based on a solid discretization adopting a refined mesh. On the contrary, a large mesh
discretization is used for the macromodel, according to its simplified numerical strategy and to the aim of reducing
the computational effort. The numerical models corresponding to the FE and macroelement model are illustrated in
Figure 8. It is worth noting that there is a significant reduction in the number of DOFs corresponding to macroelement
models, which leads to a decrease of the computational cost. The FE models presented 108 954 DOFs, whereas the
macroelement model presented 616 DOFs only, corresponding to 88 shear deformable panels.
3.1 | Static nonlinear analysis
This section reports a comparison of the results obtained by the macroelement and the FE models subjected to a mass
distributed lateral force in the directions perpendicular to the main gable wall to evaluate the out‐of‐plane responses.
The results from the pushover analyses, when pushing inside the main gable wall, are presented in Figure 9 in capacity
```
curves of the load factor (ratio between total horizontal base shear and self‐weight of the structure) vs horizontal dis-
```
placements at the top of the tympanum, as well as collapse mechanisms and principal strains. The response of the
FE model based on a fixed crack model with a shear retention factor of 0.2 is characterized by a ductile behavior with
a hardening of the load capacity after yielding. When using a shear retention factor of 0.05, the response of the FE
model is also characterized by a ductile behavior with no major increase of the maximum load capacity. On the other
hand, the last considered FE model, governed by a rotating crack constitutive law, is characterized by almost the same
limit load of the previous model but followed by a softening behavior. It could be observed that the macroelement
model resembles well the response of the FE rotating model, because it is also characterized by a softening postpeak
TABLE 1 Mechanical properties of the brick masonry prototype finite element and macroelement models
FE Model Macroelement Model
Linear parameters Young's modulus E GPa 5.17 5.17
Poisson's ratio ν ‐ 0.2 ‐
Shear modulus G GPa 2.15 2.15
Specific weight γ kN/m3 18.9 18.9
Tensile parameters Tensile strength f t MPa 0.10 0.10
Fracture energy Gft N/mm 0.012 0.012
Compressive parameters Compressive strength f c MPa 2.48 2.48
Fracture energy Gfc N/mm 3.97 3.97
Shear‐diagonal parameters Shear strength f s0 MPa ‐ 0.067
Friction coefficient μd ‐ ‐ 0.60
Shear‐sliding parameters Cohesion c MPa ‐ 0.10
Friction coefficient μs ‐ ‐ 0.70
Fracture energy Gfs N/mm ‐ 0.018
```
(A) (B)
```
```
FIGURE 8 Numerical models for the seismic assessment of the brick masonry prototype: (A) finite element model and (B) macroelement
```
model [Colour figure can be viewed at wileyonlinelibrary.com]
2434 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
behavior. The collapse mechanism corresponding to the FE models consists mainly in a diagonal and vertical cracking
at the return wall and concentrated inelastic strains at the connections and at the center of the tympanum. The
macroelement model does not experience any significant damage related to the in‐plane response of the return wall
with window opening. This mechanism consists mainly on the out‐of‐plane collapse of the tympanum at the main gable
wall and concentration of damage in the corners and at the upper part of the tympanum in which a vertical cracking is
```
observed. The damage scenario of the macro model is also characterized by the torsional rotation of the panels (red
```
```
lines) located at the right and left to the gable opening which produces out‐of‐plane‐sliding motion at the vertical
```
and horizontal interfaces.
Pushover analyses were also conducted on these models in the opposite direction, as illustrated in Figure 10. The
FE models based on a fixed crack constitutive law also presented locking and overstrength once they reached the
maximum load capacity. On the other hand, the FE model with a rotating crack constitutive law and the
macroelement model experienced a softening postpeak behavior, which is in accordance to the quasi‐brittle response
of URM structures. Because of the difference of strength of the main gable wall and the return walls related to the
direction of the load, the models presented a significant reduction of the maximum load capacity as expected. The
in‐plane response of the FE models corresponded to horizontal and diagonal concentration of damage from the bot-
tom part of the opening and horizontal cracks at the top part of the tympanum. In the case of the macroelement
model, horizontal cracks are identified in the lower part of the window opening, whereas in the upper part, there
```
are vertical cracks (similar to the experimental collapse mechanism). The out‐of‐plane response related to the FE
```
models is concentrated at the center of the tympanum and at the lower part the main gable wall. On the contrary,
the collapse of the macroelement model consists on the partial collapse of the main gable wall, and some concen-
tration of damage near the center of the tympanum. It is worth to note that all the pushover curves show a large
ductility, which plays a crucial role in the modern vulnerability assessment procedures relying on displacement‐
based strategies. However, such procedures usually limit the displacement capacity according to a reduction of
the base shear with respect to the peak load. In this regard, the proposed macromodel and the FE rotating model
```
(both investigated also in the dynamic field) show a pronounced softening in the postpeak branch. Thus, the push-
```
over curves to be considered in a displacement based seismic vulnerability assessment would not correspond to the
entire curves but just a smaller part of them.
FIGURE 9 Pushover analysis of the
brick masonry finite element and
macroelement models when applying a
pushing lateral load [Colour figure can be
viewed at wileyonlinelibrary.com]
FIGURE 10 Pushover analysis of the
brick masonry finite element and
macroelement models when applying a
pulling lateral load [Colour figure can be
viewed at wileyonlinelibrary.com]
CHÁCARA ET AL . 2435
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
3.2 | Dynamic nonlinear analysis
```
The numerical (FE and macroelement) models were also subjected to dynamic nonlinear analyses with direct time inte-
```
gration. These analyses were performed using the same input used in the shaking table tests to investigate the effective-
ness of numerical models in the simulation of the out‐of‐plane response of the prototype subjected to dynamic loading.
The numerical procedure for the solution of the dynamic equilibrium consisted on the Newmark method based on con-
stant acceleration. 42 A lumped distribution of mass has been assumed in the macroelement model leading to a diagonal
mass matrix. In addition, a Rayleigh viscous damping criterion was taken into consideration for the structural damping
assuming a 5% of damping ratio together with natural frequencies of 18.8 and 75.4 Hz. The coefficient βt that character-
izes the cyclic response in tension is equal to 1 for tension whereas the compressive and shear‐diagonal responses were
```
characterized by an unloading with initial stiffness (βc and βd equal to 0).
```
Based on the response of the static nonlinear analyses, the comparison of the dynamic response was conducted con-
sidering the FE model governed by the rotating crack constitutive law and the corresponding macroelement model. The
FE model subjected to a dynamic loading reaches a maximum displacement of approximately 18 mm, presenting dam-
age at the center of the tympanum and at the lower part of the main gable wall. In addition, there is concentration of
damage at the corner that connects the main gable wall and the return wall with opening, and some vertical and diag-
onal cracks in the latter wall. In the case of the macroelement model, a lower maximum displacement of 15 mm was
achieved. In this case, the collapse because of the dynamic solicitation consisted on the out‐of‐plane overturning of tym-
panum. Horizontal cracks at the lower part of the opening and additional vertical cracks at the top part of the opening
corresponded to the in‐plane mechanism of the return wall. The difference in displacement may be related to the small
```
overstrength (2.5% more) obtained with the macroelement model when comparing it to the FE rotating one because the
```
nonlinear response in the dynamic field is strongly susceptible to the maximum load capacity. However, it can be noted
that there is a good agreement in hysteretic response. Figure 11A illustrates the hysteretic response together with the
failure mechanism or principal strains of the FE and macroelement models. In addition, a comparison of the displace-
ment history throughout the dynamic analyses is depicted in Figure 11B. An overall resemblance was obtained between
these 2 models, and the slight difference may be related to the different mechanical schemes.
A comparison in collapse mechanism was conducted between the experimental campaign and the macroelement
```
model (see Figure 12). As it was previously described, the experimental failure mechanism consisted on the collapse
```
of the tympanum at the main gable wall and the upper part of the return wall with opening. Additional horizontal
cracks at the lower part of both window openings were identified, as illustrated in Figure 12A. It was observed that
```
FIGURE 11 Time history analysis of the brick masonry finite element (rotating) and macroelement models: (A) hysteretic response and
```
```
(B) displacement history [Colour figure can be viewed at wileyonlinelibrary.com]
```
2436 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
the collapse mechanism of the macroelement presented some similarities in in‐plane and out‐of‐plane failure. The main
gable wall presented the out‐of‐plane overturning of the tympanum, as well as a horizontal crack that propagated from
the lower part of the opening up to the corner. In addition, in‐plane failure of the return wall with window opening
presented horizontal cracks at the lower part of the opening and vertical crack at the upper part of the opening. Two
configurations corresponding to the maximum displacements achieved in the positive and negative directions of the
macroelement model subjected to dynamic loadings are illustrated in Figure 12B, in which the gray color map repre-
sents the normal plastic deformations, and the red lines indicate the sliding motions along the in‐plane and out‐of‐plane
```
(A) (B)
```
```
FIGURE 12 Collapse mechanisms of the brick masonry prototype corresponding to (A) experimental campaign and (B) macroelement
```
model [Colour figure can be viewed at wileyonlinelibrary.com]
```
(A) (B)
```
```
(C) (D)
```
```
(E) (F) (G)
```
```
FIGURE 13 Compilation of collapse mechanisms of brick masonry prototype: positive (pushing) direction of (A) finite element (FE)
```
```
models and (B) macromodel; negative (pulling) direction of (C) FE models and (D) macromodel; and time history of (E) FE, (F)
```
```
macromodels, and (G) experimental campaign [Colour figure can be viewed at wileyonlinelibrary.com]
```
CHÁCARA ET AL . 2437
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
directions. A summary of the different collapse mechanisms obtained by means of FE models, macromodel, and exper-
imental campaign related to this brick masonry prototype is illustrated in Figure 13.
3.3 | Influence of the mesh size
Aiming at assessing the influence of the mesh discretization on the out‐of‐plane response of the brick masonry proto-
type, a more finely discretized macroelement model was taken into consideration. As illustrated in Figure 14A, the
refined model, denoted as MeshB, was composed of 201 elements with a total of 1407 DOFs, and it was subjected to
```
static nonlinear analysis in the weakest direction (pulling the main gable wall) and dynamic nonlinear analysis. The
```
results of these analyses were subsequently compared to the ones obtained with the less refined macroelement model
composed of 88 elements, denoted as MeshA. Figure 14B presents the pushover curves, deformed shapes, and principal
strains of the macroelement models with a different mesh discretization. It was observed that the model MeshB experi-
enced a slight increment of maximum load capacity. Despite this, both macroelement models were characterized by
very similar softening behavior and residual force. In addition, the in‐plane and out‐of‐plane collapse mechanisms of
these models are in good agreement: vertical damage in the upper part of the window opening of the return wall, hor-
izontal damage at the lower height of the window opening of the same wall, and the partial overturning of the main
gable wall, and additional damage in the center of the tympanum. The response of the model MeshB subjected to a uni-
axial accelerogram by means of history of displacement is illustrated in Figure 14C. It can be observed that there is an
acceptable agreement between the 2 models with different mesh discretization. The different positive displacements
obtained at the top of the tympanum may be associated as a consequence of a residual displacement in model MeshA.
In addition, it is worth noting that this behavior was also influenced by the cyclic behavior associated to the out‐of‐plane
sliding links together with the mesh discretization. From these analyses, it was evidenced that the discretization of the
macroelement model did not influence significantly the out‐of‐plane response of this masonry prototype.
The application of dynamic nonlinear analyses based on this macroelement modeling approach presented a signif-
icant reduction of the computational effort. In the case of the FE model, an approximate time required for the applica-
tion of the time history analysis corresponded to 18 hours, whereas for the macroelement model MeshA and MeshB, this
value was reduced to approximately 40 and 90 minutes respectively. The computation effort for each numerical model is
reported in Table 2.
```
(A) (B)
```
```
(C)
```
```
FIGURE 14 Comparison between basic model MeshA and (A) refined model MeshB: (B) pushover curves, deformed shapes, and principal
```
```
plastic strains and (C) history of displacement due to the application of a uniaxial accelerogram [Colour figure can be viewed at
```
wileyonlinelibrary.com]
2438 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
3.4 | Displacement assessment based on experimental campaign
As reported by Candeias et al,18 the brick masonry prototype was subjected to 8 consecutive and incremental shaking
table tests. It was presented that the application of the first 7 seismic events did not produce significant damage or par-
tial collapse of the structure. In this regard, the macroelement model of the brick masonry prototype was subjected to
the seismic inputs registered throughout the first 7 shaking table tests aiming at comparing the experimental history of
displacements to the ones obtained numerically. Even though such comparison was conducted throughout the 7 seismic
events, a significant attention was considered for the last 2 because the structure exceeded the elastic branch. A first set
of analyses was conducted taking into account the same mechanical properties and damping ratio defined in the FE
model and reported in the previous section. Nevertheless, it was observed that the response of the macroelement MeshA
model was characterized by an elastic behavior during all the seismic events. For this reason, it was decided to assume a
different value of damping ratio equal to 3% and to assess the influence of the tensile strength on the response of the
macroelement model in displacements. It is worth noting that even though the value of tensile strength was obtained
by means of a mechanical characterization of square specimens, this value was not suitable for the simulation of the
experimental results. For this assessment, the values used for tensile strength ranged between 0.065 and 0.1 MPa. It
was noted that a 30% reduction of tensile strength was required for reaching a nonlinear dynamic behavior, as experi-
mentally observed. Figure 15A illustrates the history of displacements of the brick masonry prototype because of the
application of shaking table tests, as well as the numerical response of the macroelement with tensile strengths of
0.07 and 0.065 MPa. On the other hand, Figure 15B depicts the experimental and numerical responses associated with
the last seismic input. A reasonable agreement was determined when comparing these results. The difference was
mainly related to the residual displacement obtained by the shaking table tests. These results stressed the complex
dynamic behavior of URM structures which is strongly influenced by the mechanical properties but also by the damping
ratio. This difference may also be partially related to the assumption of small displacements adopted for the nonlinear
dynamic analyses.
TABLE 2 Computational effort for dynamic analysis of the brick masonry structure
FE Model Macroelement model—MeshA Macroelement model—MeshB
```
Duration Duration (reduction) Duration (reduction)
```
```
18 hours 40 minutes (96%) 90 minutes (92%)
```
```
(A)
```
```
(B)
```
```
FIGURE 15 History of displacement of the brick masonry prototype associated with the application of (A) 7 seismic inputs and (B) the
```
seventh seismic input [Colour figure can be viewed at wileyonlinelibrary.com]
CHÁCARA ET AL . 2439
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
4 | STONE M ASONRY PR OTOTYPE
The second case study corresponds to a stone masonry structure also subjected to shaking table tests at the National
Laboratory for Civil Engineering to assess its out‐of‐plane response because of dynamic loading. 18 Similarly to the pre-
vious case, the stone masonry prototype corresponded to a U‐shape structure composed by a main gable wall and 2
```
return walls with a thickness of 0.50 m (see Figure 16A). In this case, the main gable wall, with a height of 2.75 m at
```
the top of the tympanum and a length of 3.5 m, presented a door opening. Both return walls, 1 of them with a window
opening, presented a height and length of 2.25 and 2.5 m respectively. The stone masonry prototype was loaded near to
collapse reaching a PGA of 1.07 g. The collapse of this structure was related to the failure of the mortar joints at the
```
main gable wall and the return wall (see Figure 16B, C). In addition, the structure experienced the partial collapse of
```
the top right corner of the return wall with opening because of the last seismic input as illustrated in Figure 16C. There
was additional failure at the mortar joints in the return wall, close to the connection to the main gable wall. Additional
information related to the experimental campaign was presented by Candeias et al. 18
The stone masonry prototype was also numerically investigated by Chácara et al, 21 by means of FEM in which the
```
constitutive laws were based on the same total strain crack approach used in the previous section (2 fixed crack models
```
```
with shear retention factors of 0.2 and 0.05 and 1 rotating crack model). The FE and macroelement models presented
```
exponential and parabolic curves for the behavior in tension and compression respectively. Similar assumptions as in
the brick masonry macroelement model were considered for the definition of the additional shear‐diagonal and
shear‐sliding mechanical parameters for the macroelement model. Table 3 presents the mechanical properties used
for the FE and macroelement models.
```
(A) (B) (C)
```
```
FIGURE 16 Stone masonry prototype (A) and collapse mechanism from shaking table tests: (B) main gable wall and (C) return wall with
```
window opening18 [Colour figure can be viewed at wileyonlinelibrary.com]
TABLE 3 Mechanical properties of the stone masonry prototype FE and macroelement models
FE Model Macroelement Model
Linear parameters Young's modulus E GPa 2.08 2.08
Poisson's ratio ν ‐ 0.2 ‐
Shear modulus G GPa 0.87 0.87
Specific weight γ kN/m3 23.6 23.6
Tensile parameters Tensile strength f t MPa 0.22 0.22
Fracture energy Gft N/mm 0.048 0.048
Compressive parameters Compressive strength f c MPa 5.44 5.44
Fracture energy Gfc N/mm 8.70 8.70
Shear‐diagonal parameters Shear strength f s0 MPa ‐ 0.15
Friction coefficient μd ‐ ‐ 0.60
Shear‐sliding parameters Cohesion c MPa ‐ 0.22
Friction coefficient μs ‐ ‐ 0.70
Fracture energy Gfs N/mm ‐ 0.072
2440 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
Figure 17 illustrates the FE and macroelement models used for the seismic assessment of the stone masonry proto-
type. It is possible to observe the large difference in elements, and therefore the number of DOFs. The FE model pre-
sented 81 090 DOFs, whereas the macroelement model presented 714 DOFs, corresponding to 102 macroelements.
4.1 | Static nonlinear analysis
A mass distributed lateral force was applied to the numerical models in the perpendicular direction of the main gable
```
wall. Figure 18 illustrates the load factor vs displacement (at the top of the tympanum) curves as well as the correspond-
```
ing principal strains maps and the collapse mechanisms obtained by means of the pushover analyses when pushing the
main gable wall. The overstrength of the capacity of the FE models was still governed by the definition of the constitu-
```
tive law (fixed crack models). On the other hand, it was possible to observe that the pushover curve from the FE rotating
```
model and the macroelement model presented a response, characterized by a softening postpeak behavior. A slight dif-
ference in the maximum load capacity, corresponding to 9%, can be observed that can still be considered an acceptable
value for this purpose. However, the macroelement model is able to take the analysis further in the postpeak regime. A
similar ductility can be observed for the other 2 FE models based on a fixed crack approach. For the latter FE models,
concentrated damage propagating from the window opening at the return wall is observed. In the case of the main gable
wall, these models present horizontal crack in the main gable wall as well as concentration of damage propagating from
the corner, at the center of the tympanum, and at the base. The response of the FE rotating model was mainly related to
```
the in‐plane failure of the return (damage at the window opening). The collapse mechanism of the macroelement model
```
is in reasonable agreement with the corresponding response of both FE fixed models.
```
Figure 19 presents the load factor vs displacement (at the top of the tympanum) curves, and the collapse mecha-
```
nisms of the numerical models subjected to a pulling mass distributed lateral load. There is a good agreement in max-
imum load capacities between the FE models and the macroelement model. In addition, it could also be observed that
the postpeak behavior of the macroelement models is similar to that predicted by the fixed 0.05 FE models until the dis-
placement of 8 mm and then reaches a value of residual force close to those predicted by the rotating model. The return
wall of the FE model presented a vertical and horizontal concentration of strains in the upper part of the window open-
ing. In addition, these walls experienced horizontal and diagonal cracking in the lower part of the window opening. The
behavior of the macroelement model in the upper part of the window opening is in good agreement with all the FE
models. The diagonal crack at the lower part of the window was replaced by a horizontal crack in the macroelement
model. A different behavior can be observed in the out‐of‐plane response between the FE and the macroelement
models. In the case of the FE fixed models, there is a significant concentration of damage in the center of the
FIGURE 17 Numerical models for the
seismic assessment of the stone masonry
```
prototype: (A) finite element model and
```
```
(B) macroelement model [Colour figure
```
```
can be viewed at wileyonlinelibrary.com] (A) (B)
```
FIGURE 18 Pushover analysis of the
stone masonry finite element and
macroelement models when applying a
pushing lateral load [Colour figure can be
viewed at wileyonlinelibrary.com]
CHÁCARA ET AL . 2441
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
tympanum. This behavior was not observed in the macroelement model because there is a complete detachment of the
main gable wall and the return wall without opening.
4.2 | Dynamic nonlinear analysis
The time history analyses conducted on the FE and macroelement models of the stone masonry prototype followed the same
approach as the brick masonry one. The hysteretic response was also characterized by an unloading oriented to the origin in
```
tension (βt equal to 1), and an initial stiffness for compression and shear diagonal (βc and βd equal to 0). The comparison of the
```
dynamic response was also conducted taking into consideration the FE rotating model. It is worth mentioning that a prelim-
inary analysis was conducted on the macroelement model using the same input registered during the test, obtaining basically
an elastic response. Such response was not coherent to the one obtained from the experimental campaign or the FE numer-
ical simulations, and it may be related to the sensitivity of the model because of the brittle behavior associated with the lack of
a rigid diaphragm. In this sense, an increase of 10% was applied to the experimental input, according to the overstrength of the
macromodel, when compared to the FE rotating model registered during the pushover analyses.
Even though the macromodel and the FE model with 5% of shear retention presented a good resemblance in the
static field, the corresponding FE model with rotating cracks appeared to be closest to the macromodel in results for
the brick and stone prototypes. Additionally, despite the limited ductility, the FE model with rotating cracks and
macromodel presented a similar damage pattern. Figure 20A presents the hysteretic response of both models, the
FIGURE 19 Pushover analysis of the
stone masonry finite element and
macroelement models when applying a
pulling lateral load [Colour figure can be
viewed at wileyonlinelibrary.com]
```
FIGURE 20 Time history analysis of the stone masonry finite element (rotating) and macroelement models: (A) hysteretic response and
```
```
(B) displacement history [Colour figure can be viewed at wileyonlinelibrary.com]
```
2442 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
corresponding collapse mechanism, and principal strains maps. In the case of the FE rotating model, a maximum dis-
placement of approximately 11 mm was obtained, presenting damage propagating from the window opening, as well as
at the base and at the tympanum of the main gable wall. The maximum displacement obtained with the macroelement
model was approximately 9 mm. The collapse mechanism corresponded to horizontal cracks and an additional vertical
crack at the return wall, and the detachment of the main gable wall from the return wall with no opening. It can be
observed that the hysteretic behavior from these 2 models presented a similar response. Figure 20B illustrates the good
agreement regarding the displacement history of the FE rotating and macroelement models.
Figure 21 illustrates the comparison of collapse mechanisms of the stone masonry model obtained in the experimen-
tal campaign and by means of a macroelement modeling approach. Even though the collapse mechanism from the
shaking table tests corresponded mainly to the failure at the mortar joints, a simplified scheme of the overall response
can be depicted in Figure 21A. Such response consisted on the detachment of the main gable wall from both return
walls, the collapse of the center part of the tympanum, and additional horizontal cracks along the connection of this
wall and the return one with opening. The in‐plane failure corresponded to the collapse of the top corner of the return
wall, and additional diagonal and vertical cracks. In the case of the macroelement model, the detachment of the main
gable wall occurred only at the return wall with no opening. Additional damage in the center of the tympanum and
horizontal cracks at the level of the window opening were identified. In general, it can be stated that the macroelement
model also presents some similarities regarding in‐plane and out‐of‐plane collapse mechanisms of the stone masonry
prototype. In the case of the stone masonry prototype, the summary of the different collapse mechanisms obtained
by means of FE model, macromodel, and experimental campaign is illustrated in Figure 22.
In the case of the stone masonry prototype, there is also a significant reduction of the computational effort related to
the application of nonlinear dynamic analysis. In the case of the FE model, the required computational effort
corresponded to approximate 21 hours, whereas for the macroelement model, it was reduced to approximately
```
45 minutes (see Table 4).
```
5 | FINAL CONSIDERATIONS
A numerical validation on the applicability of a macroelement modeling approach for the assessment of the seismic per-
formance of 2 masonry structures is presented in this paper. For this purpose, a spatial macroelement model, originally
formulated in the static field 13,26 and recently extended to the dynamic field, is used. Even though this macroelement
model is based on a simplified approach, it is capable of simulating the main in‐plane and out‐of‐plane mechanisms
of URM structures. The seismic response of 2 URM prototypes composed by a main gable wall and 2 return orthogonal
walls was obtained by means of the macroelement model through static and dynamic nonlinear analyses. The results
are compared to the results from FE models and from an experimental campaign based on shaking table tests. Good
agreement was obtained for the brick masonry prototype in load factor vs displacement hysteresis curves, whereas a rea-
sonable resemblance was identified regarding failure mechanisms, especially in the in‐plane direction. It is worth noting
that the differences associated with failure mechanisms may have a significant impact when retrofitting structures based
on localized damage. In addition, an assessment of the mesh discretization evidenced that it did present a strong influ-
ence on the out‐of‐plane response of the brick masonry prototype. A comparison of the history of displacements
obtained from the experimental campaign and the macroelement model was also conducted. A reduction of approxi-
mately 35% of tensile strength was required to obtain a reasonable agreement between these 2 approaches. It was noted
```
(A) (B)
```
```
FIGURE 21 Collapse mechanisms of the stone masonry prototype corresponding to (A) experimental campaign and (B) macroelement
```
model [Colour figure can be viewed at wileyonlinelibrary.com]
CHÁCARA ET AL . 2443
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
that the dynamic nonlinear response of the brick masonry prototype was strongly influenced by tensile strength and
damping ratio. In the case of the stone model, a slight but acceptable difference in the maximum load capacity of the
structure was found. In addition, the collapse mechanism in the outward direction of the main gable wall presented
```
a different response (detachment of the main gable wall and the return wall with no opening). Nevertheless, it was pos-
```
sible to identify a high similarity in hysteretic behavior. Overall, it can be concluded that the macroelement modeling
approach represents an effective tool for the seismic assessment of masonry structures. A significant reduction of the
```
computational effort (96%) was evidenced when performing nonlinear dynamic analyses based on this simplified
```
macroelement modeling approach because there is a reduced number of DOFs. Nevertheless, additional
implementations are being conducted aiming at the optimization of the numerical procedures. It is worth noting that
this modeling approach also extends for practical applications because of the low computational demand, and opens
a new perspective toward an extensive application of nonlinear dynamic analyses for practical and engineering pur-
poses, as well as for the next generation of seismic assessment codes based on fragility curves.
TABLE 4 Computational effort for dynamic analysis of the stone masonry structure
FE Model Macroelement Model
```
Duration Duration (reduction)
```
```
21 hours 45 minutes (96%)
```
```
(A) (B)
```
```
(D)
```
```
(G)(F)(E)
```
```
(C)
```
```
FIGURE 22 Compilation of collapse mechanisms of stone masonry prototype: positive (pushing) direction of (A) finite element (FE)
```
```
models and (B) macromodel; negative (pulling) direction of (C) FE models and (D) macromodel; and time history of (E) FE, (F)
```
```
macromodels, and (G) experimental campaign [Colour figure can be viewed at wileyonlinelibrary.com]
```
2444 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
ACKNO WLEDGEMENT
The first author gratefully acknowledges the financial support of the Peruvian Institution Innovate Perú‐Fondo para la
Innovación, Ciencia y Tecnología through the PhD grant BECA‐1‐P‐078‐13. This work was also partly financed by
FEDER funds through the Competitivity Factors Operational Programme and by national funds through Foundation
for Science and Technology within the scope of the project POCI‐01‐0145‐FEDER‐007633.
ORCID
César Chácara http://orcid.org/0000-0001-5367-7435
Francesco Cannizzaro http://orcid.org/0000-0001-8698-1329
Bartolomeo Pantò http://orcid.org/0000-0002-3340-228X
Ivo Caliò http://orcid.org/0000-0002-8063-8359
Paulo B. Lourenço http://orcid.org/0000-0001-8459-0199
R EF E RE N C E S
1. Mendes N, Lourenço PB. Sensitivity analysis of the seismic performance of existing masonry buildings. Eng Struct. 2014;80:137‐146.
2. de Felice G, De Santis S, Lourenço PB, Mendes N. Methods and challenges for the seismic assessment of historic masonry structures. Int J
```
Archit Herit. 2017;11:143‐160.
```
3. Restrepo Vélez LF, Magenes G, Griffith M. Dry stone masonry walls in bending—part I: Static tests. Int J Archi Herit. 2014;8(1):1‐28.
```
https://doi.org/10.1080/15583058.2012.663059
```
4. Vaculik J, Griffith M, Magenes G. Dry stone masonry walls in bending—part II: Analysis. Int J Archit Herit. 2014;8(1):29‐48. https://doi.
org/10.1080/15583058.2012.663060
5. Mele E, De Luca A, Giordano A. Modelling and analysis of a basilica under earthquake loading. J Cult Herit. 2003;4(4):355‐367.
6. Milani G, Valente M. Comparative pushover and limit analyses on seven masonry churches damaged by the 2012 Emilia‐Romagna (Italy)
```
seismic events: Possibilities of non‐linear finite elements compared with pre‐assigned failure mechanisms. Eng Fail Anal. 2015;47(Part
```
```
A):129‐161.
```
7. Pantò B, Cannizzaro F, Caddemi S, Caliò I. 3D macro‐element modelling approach for seismic assessment of historical masonry churches.
```
Adv Eng Softw. 2016;97:40‐59.
```
8. Magenes G, Della Fontana A. Simplified non‐linear seismic analysis of masonry buildings. Proc Br Masonry Soc. 1998;8:190‐195.
9. Kappos AJ, Penelis GG, Drakopoulos CG. Evaluation of simplified models for lateral load analysis of unreinforced masonry buildings. J
```
Struct Eng. 2002;128(7):890‐897.
```
10. Penna A, Lagomarsino S, Galasco A. A nonlinear macroelement model for the seismic analysis of masonry buildings. Earthq Eng Struct
```
Dyn. 2014;43(2):159‐179. https://doi.org/10.1002/eqe.2335
```
11. D'Asdia P, Viskovic A. Analyses of a masonry wall subjected to horizontal actions on its plane, employing a non‐linear procedure using
```
changing shape finite elements. Trans Model Comput Simul. 1995;10:519‐526.
```
12. Casolo S, Peña F. Rigid element model for in‐plane dynamics of masonry walls considering hysteretic behaviour and damage. Earthq Eng
```
Struct Dyn. 2007;36(8):1029‐1048.
```
13. Caliò I, Marletta M, Pantò B. A new discrete element model for the evaluation of the seismic behaviour of unreinforced masonry build-
```
ings. Eng Struct. 2012;40:237‐338.
```
14. Marques R, Lourenço PB. Possibilities and comparison of structural component models for the seismic assessment of modern unrein-
```
forced masonry buildings. Comput Struct. 2011;89(21‐22):2079‐2091.
```
15. De Felice G, Giannini R. Out‐of‐plane seismic resistance of masonry walls. J Earthq Eng. 2001;5(2):253‐271.
16. D'Ayala D, Speranza E. Definition of collapse mechanisms and seismic vulnerability of historic masonry buildings. Earthq Spectra.
```
2003;19(3):479‐509.
```
17. Milani G, Lourenço PB, Tralli A. 3D homogenized analysis of masonry buildings under horizontal loads. Eng Struct. 2007;80:137‐146.
18. Candeias PX, Campos Costa A, Mendes N, Costa AA, Lourenço PB. Experimental assessment of the out‐of‐plane performance of masonry
```
buildings through shaking table tests. Int J Archit Herit. 2017;11:31‐58.
```
19. Mendes N, Costa AA, Lourenço PB, et al. Methods and approaches for blind test predictions of out‐of‐plane behavior of masonry walls:
```
An experimental comparative study. Int J Archit Herit. 2017;11:59‐71.
```
20. Derakhshan H, Nakamura Y, Ingham JM, Griffith MC. Simulation of shake table results on out‐of‐ plane masonry buildings. Part (I): Dis-
```
placement‐based approach using simple failure mechanisms. Int J Archit Herit. 2017;11:72‐78.
```
CHÁCARA ET AL . 2445
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```
21. Chácara C, Mendes N, Lourenço PB. Simulation of shake table tests on out‐of‐plane masonry buildings. Part (IV): Macro and micro FEM
```
based approaches. Int J Archit Herit. 2017;11:103‐116.
```
22. Gams M, Anžlin A, Kramara M. Simulation of shake table results on out‐of‐plane masonry buildings. Part (III): Two‐step FEM approach.
```
Int J Archit Herit. 2017;11:94‐102.
```
23. Lemos JV, Campos Costa A. Simulation of shake table results on out‐of‐plane masonry buildings. Part (V): Discrete element approach. Int
```
J Archit Herit. 2017;11:117‐124.
```
24. AlShawa O, Sorrentino L, Liberatore D. Simulation of shake table tests on out‐of‐plane masonry buildings. Part (II): Combined finite‐dis-
```
crete elements. Int J Archit Herit. 2017;11:79‐93.
```
25. Cannizzaro F, Lourenço PB. Simulation of shake table tests on out‐of‐plane masonry buildings. Part (VI): Discrete element approach. Int J
```
Archit Herit. 2017;11:125‐142.
```
26. Pantò B, Cannizzaro F, Caliò I, Lourenço PB. Numerical and experimental validation of a 3D macro‐model for the in‐plane and out‐of‐
plane behaviour of unreinforced masonry walls. Int J Archit Herit. 2017. https://doi.org/10.1080/15583058.2017.1325539
27. TNO, DIANA ‐ DIsplacement method ANAlyser. Delft, Netherlands, 2013.
28. Caliò I, Cannizzaro F, Marletta M. A discrete element for modeling masonry vaults. Adv Mat Res. 2010;133‐134:447‐452.
29. Cannizzaro F. The seismic behavior of historical buildings: A macro‐element approach. PhD Thesis, Department of Civil and Environ-
mental Engineering, University of Catania, Catania, Italy, 2010.
30. Gruppo Sismica s.r.l., 3DMacro (3D Computer program for seismic assessment of masonry buildings). Catania, Italy, Release 3.0, 2014
```
http://www.3dmacro.it.
```
31. Gruppo Sismica s.r.l., HiStrA (historical structure analysis). Catania, Italy, Release 17.2.3, 2015 http://www.histra.it.
32. Takeda T, Sozen MA, Nielsen NN. Reinforced concrete response to simulated earthquakes. J Struct Div. 1970;96:2557‐2573.
33. Mazzoni S, Mckenna F, Scott MH, Fenves GL. OpenSees User Manual. University of California, Berkeley, U.S.A, 2000.
34. Pantò B. The seismic modeling of masonry structure, an innovative macroelement approach. PhD Thesis, Department of Civil and Envi-
ronmental Engineering, University of Catania, Catania, Italy, 2007.
35. Turnsek V, Cacovic F. Some experimental result on the strength of brick masonry walls in 2nd International Brick Masonry Conference,
Stoke‐on‐Trent, UK 1971.
36. Turnsek V, Sheppard P. The shear and flexural resistance of masonry walls. in International research conference on earthquake engineer-
```
ing, Skopje, 1981;517–573.
```
37. Corradi M, Borri A, Vignoli A. Experimental study on the determination of strength of masonry walls. Construct Build Mater.
```
2003;17(5):325‐337.
```
38. Chácara C, Lourenço PB, Pantò B, Cannizzaro F, Caliò I. Macro‐element mass matrix for the dynamic assessment of unreinforced
masonry structures. in Congreso de Métodos Numéricos en Ingeniería, Valencia, Spain 2017.
39. Lourenço PB. Recent advances in masonry modelling: Micromodelling and homogenisation. In: Galvanetto U, Ferri Aliabadi MH, eds.
```
Multiscale modeling in solid mechanics: Computational approaches. London, UK: Imperial College Press; 2009.
```
40. Milosevic J, Sousa Gago A, Lopes M, Bento R. Experimental assessment of shear strength parameters on rubble stone masonry specimens.
```
Construct Build Mater. 2013;47:1372‐1380.
```
41. Calderini C, Cattari S, Lagomarsino S. The use of the diagonal compression test to identify the shear mechanical parameters of masonry.
```
Construct Build Mater. 2010;24(5):677‐685.
```
42. Newmark NM. A method of computation for structural dynamics. ASCE J Eng Mech Div. 1959;85:67‐94.
How to cite this article: Chácara C, Cannizzaro F, Pantò B, Caliò I, Lourenço PB. Assessment of the dynamic
response of unreinforced masonry structures using a macroelement modeling approach. Earthquake Engng Struct
```
Dyn. 2018;47:2426–2446. https://doi.org/10.1002/eqe.3091
```
2446 CHÁCARA ET AL .
```
10969845, 2018, 12, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/eqe.3091 by Universidade Do Minho, Wiley Online Library on [19/01/2024]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
```