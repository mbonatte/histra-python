"""Analytical Overturning and Sensitivity Analysis Engine for Scoured Walls.

This module provides exact analytical equations, normalized/non-dimensional
formulations, closed-form gradients, elasticities, and global sensitivity
tools for rocking and overturning instability of scoured walls and foundations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np


# =====================================================================
# Data Structures
# =====================================================================

@dataclass(frozen=True)
class RectangularComponent:
    """Rectangular block representing foundation or wall component."""
    name: str
    length_x: float      # dimension along thickness/length [m]
    breadth_y: float     # dimension along rocking plane breadth [m]
    height_z: float      # vertical dimension [m]
    specific_weight: float  # unit weight gamma [kN/m^3]

    @property
    def volume(self) -> float:
        """Volume in m^3."""
        return float(self.length_x * self.breadth_y * self.height_z)

    @property
    def weight(self) -> float:
        """Weight in kN."""
        return float(self.volume * self.specific_weight)


@dataclass(frozen=True)
class WallSystemGeometry:
    """Combined foundation-wall structural system parameters."""
    foundation: RectangularComponent
    pier_wall: RectangularComponent
    load_y: float  # horizontal position of applied load relative to center [m]

    @property
    def total_weight(self) -> float:
        """Total weight W in kN."""
        return self.foundation.weight + self.pier_wall.weight

    @property
    def foundation_breadth(self) -> float:
        """Breadth B in rocking plane [m]."""
        return self.foundation.breadth_y

    @property
    def centroid_h1(self) -> float:
        """Combined center of gravity elevation above foundation base [m]."""
        w_f = self.foundation.weight
        w_w = self.pier_wall.weight
        z_f = 0.5 * self.foundation.height_z
        z_w = self.foundation.height_z + 0.5 * self.pier_wall.height_z
        return (w_f * z_f + w_w * z_w) / (w_f + w_w)

    @property
    def centroid_y_g(self) -> float:
        """Combined center of gravity horizontal offset [m] (typically 0.0)."""
        return 0.0

    @property
    def load_elevation_h2(self) -> float:
        """Load elevation H2 above foundation base [m]."""
        return self.foundation.height_z + self.pier_wall.height_z

    @property
    def aspect_ratio_lambda(self) -> float:
        """Slenderness / Aspect ratio lambda = H2 / B."""
        return self.load_elevation_h2 / self.foundation_breadth

    @property
    def relative_centroid_hg(self) -> float:
        """Relative center of gravity height h_G = H1 / H2."""
        return self.centroid_h1 / self.load_elevation_h2


@dataclass(frozen=True)
class ScourScenarioAnalytical:
    """Analytical parameters for a specific remaining support ratio."""
    support_ratio: float      # r = b/B in (0.5, 1.0]
    foundation_breadth: float # B [m]
    scoured_width: float      # s = B * (1 - r) [m]
    supported_width: float    # b = B * r [m]
    pivot_y: float            # y_p [m]
    d1: float                 # restoring arm [m]
    d2: float                 # load overturning arm [m]
    f_cr: float               # critical load [kN]
    theta_0_rad: float        # zero-load limit rotation [rad]
    theta_0_deg: float        # zero-load limit rotation [deg]
    initial_slope_kn_per_rad: float  # dF/dtheta at theta=0 [kN/rad]
    u_y0: float               # outward displacement at zero load [m]
    u_z0: float               # downward displacement at zero load [m]
    max_energy_kn_m: float    # maximum restoring energy capacity [kN*m]


# =====================================================================
# 1. Dimensional Governing Equations
# =====================================================================

def critical_force(weight_kn: float | np.ndarray, d1_m: float | np.ndarray, d2_m: float | np.ndarray) -> float | np.ndarray:
    """Compute theoretical critical live load capacity F_cr at zero rotation.
    
    F_cr = W * (d1 / d2)
    """
    w = np.asarray(weight_kn, dtype=float)
    d1 = np.asarray(d1_m, dtype=float)
    d2 = np.asarray(d2_m, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where(d2 > 0.0, np.maximum(w * d1 / d2, 0.0), np.nan)
    return float(res) if np.ndim(res) == 0 else res


def limit_rotation_angle(d1_m: float | np.ndarray, h1_m: float | np.ndarray) -> float | np.ndarray:
    """Compute zero-load limit rotation angle theta_0 where F(theta) = 0.
    
    theta_0 = arctan(d1 / H1)
    """
    d1 = np.asarray(d1_m, dtype=float)
    h1 = np.asarray(h1_m, dtype=float)
    res = np.arctan2(d1, h1)
    return float(res) if np.ndim(res) == 0 else res


def post_peak_force(
    theta_rad: float | np.ndarray,
    weight_kn: float,
    d1_m: float,
    d2_m: float,
    h1_m: float,
    h2_m: float,
) -> float | np.ndarray:
    """Compute vertical live load equilibrium path as a function of rotation theta.
    
    F(theta) = W * (d1 * cos(theta) - H1 * sin(theta)) / (d2 * cos(theta) + H2 * sin(theta))
    """
    theta = np.asarray(theta_rad, dtype=float)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    
    restoring_arm = d1_m * cos_t - h1_m * sin_t
    load_arm = d2_m * cos_t + h2_m * sin_t
    
    with np.errstate(divide="ignore", invalid="ignore"):
        force = np.where(
            (restoring_arm >= 0.0) & (load_arm > 0.0),
            weight_kn * restoring_arm / load_arm,
            0.0,
        )
    return float(force) if np.ndim(force) == 0 else force


def initial_softening_slope(
    weight_kn: float | np.ndarray,
    d1_m: float | np.ndarray,
    d2_m: float | np.ndarray,
    h1_m: float | np.ndarray,
    h2_m: float | np.ndarray,
) -> float | np.ndarray:
    """Compute derivative dF/dtheta at theta = 0 [kN/rad].
    
    dF/dtheta|_{theta=0} = -W * (H1 * d2 + H2 * d1) / (d2^2) = -F_cr * (H1/d1 + H2/d2)
    """
    w = np.asarray(weight_kn, dtype=float)
    d1 = np.asarray(d1_m, dtype=float)
    d2 = np.asarray(d2_m, dtype=float)
    h1 = np.asarray(h1_m, dtype=float)
    h2 = np.asarray(h2_m, dtype=float)
    res = -w * (h1 * d2 + h2 * d1) / (d2**2)
    return float(res) if np.ndim(res) == 0 else res


def kinematic_displacements(
    theta_rad: float | np.ndarray,
    d2_track_m: float,
    h2_m: float,
) -> Tuple[float | np.ndarray, float | np.ndarray]:
    """Compute outward (horizontal) and downward (vertical) displacements of load point relative to pivot.
    
    u_y(theta) = H2 * sin(theta) - d2_track * (1 - cos(theta))
    u_z(theta) = d2_track * sin(theta) + H2 * (1 - cos(theta))
    """
    theta = np.asarray(theta_rad, dtype=float)
    sin_t = np.sin(theta)
    cos_t = np.cos(theta)
    
    u_y = h2_m * sin_t - d2_track_m * (1.0 - cos_t)
    u_z = d2_track_m * sin_t + h2_m * (1.0 - cos_t)
    
    if np.ndim(u_y) == 0:
        return float(u_y), float(u_z)
    return u_y, u_z


def overturning_work_capacity(
    weight_kn: float | np.ndarray,
    d1_m: float | np.ndarray,
    h1_m: float | np.ndarray,
) -> float | np.ndarray:
    """Compute total restoring strain energy / overturning work up to limit rotation theta_0 [kN*m].
    
    U_max = W * (sqrt(d1^2 + H1^2) - H1) = W * H1 * (sec(theta_0) - 1)
    """
    w = np.asarray(weight_kn, dtype=float)
    d1 = np.asarray(d1_m, dtype=float)
    h1 = np.asarray(h1_m, dtype=float)
    res = w * (np.sqrt(d1**2 + h1**2) - h1)
    return float(res) if np.ndim(res) == 0 else res


# =====================================================================
# 2. Universal Non-Dimensional / Normalized Formulation
# =====================================================================

def normalized_critical_force(support_ratio: float | np.ndarray) -> float | np.ndarray:
    """Compute normalized critical capacity F_cr / W as function of remaining support ratio r = b/B.
    
    F_cr / W = (r - 0.5) / (1 - r)  for r in (0.5, 1.0)
    """
    r = np.asarray(support_ratio, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where((r > 0.5) & (r < 1.0), (r - 0.5) / (1.0 - r), np.where(r >= 1.0, np.inf, 0.0))
    return float(res) if np.ndim(res) == 0 else res


def normalized_limit_rotation(
    support_ratio: float | np.ndarray,
    aspect_ratio_lambda: float | np.ndarray,
    relative_centroid_hg: float | np.ndarray,
) -> float | np.ndarray:
    """Compute zero-load limit rotation theta_0 [rad] using dimensionless parameters.
    
    theta_0 = arctan((r - 0.5) / (h_G * lambda))
    """
    r = np.asarray(support_ratio, dtype=float)
    lam = np.asarray(aspect_ratio_lambda, dtype=float)
    hg = np.asarray(relative_centroid_hg, dtype=float)
    
    num = r - 0.5
    den = hg * lam
    res = np.where(num > 0.0, np.arctan2(num, den), 0.0)
    return float(res) if np.ndim(res) == 0 else res


def normalized_post_peak_curve(
    theta_rad: float | np.ndarray,
    support_ratio: float,
    aspect_ratio_lambda: float,
    relative_centroid_hg: float,
) -> float | np.ndarray:
    """Compute weight-normalized post-peak force F(theta) / W from dimensionless parameters.
    
    F(theta) / W = ((r - 0.5)*cos(theta) - h_G*lambda*sin(theta)) / ((1 - r)*cos(theta) + lambda*sin(theta))
    """
    theta = np.asarray(theta_rad, dtype=float)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    
    d1_tilde = support_ratio - 0.5
    d2_tilde = 1.0 - support_ratio
    h1_tilde = relative_centroid_hg * aspect_ratio_lambda
    h2_tilde = aspect_ratio_lambda
    
    restoring = d1_tilde * cos_t - h1_tilde * sin_t
    overturning = d2_tilde * cos_t + h2_tilde * sin_t
    
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where((restoring >= 0.0) & (overturning > 0.0), restoring / overturning, 0.0)
    return float(res) if np.ndim(res) == 0 else res


def relative_capacity_degradation(
    theta_rad: float | np.ndarray,
    eta1: float,
    eta2: float,
) -> float | np.ndarray:
    """Compute capacity-normalized degradation function Phi(theta) = F(theta) / F_cr.
    
    Phi(theta) = (1 - eta1 * tan(theta)) / (1 + eta2 * tan(theta))
    where eta1 = H1 / d1 = 1 / tan(theta_0), eta2 = H2 / d2.
    """
    theta = np.asarray(theta_rad, dtype=float)
    tan_t = np.tan(theta)
    
    num = 1.0 - eta1 * tan_t
    den = 1.0 + eta2 * tan_t
    
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where((num >= 0.0) & (den > 0.0), num / den, 0.0)
    return float(res) if np.ndim(res) == 0 else res


def normalized_overturning_energy(
    support_ratio: float | np.ndarray,
    aspect_ratio_lambda: float | np.ndarray,
    relative_centroid_hg: float | np.ndarray,
) -> float | np.ndarray:
    """Compute normalized energy capacity U_max / (W * B).
    
    U_max / (W * B) = h_G * lambda * (sqrt(1 + ((r - 0.5) / (h_G * lambda))^2) - 1)
    """
    r = np.asarray(support_ratio, dtype=float)
    lam = np.asarray(aspect_ratio_lambda, dtype=float)
    hg = np.asarray(relative_centroid_hg, dtype=float)
    
    xi = (r - 0.5) / (hg * lam)
    res = np.where(r > 0.5, hg * lam * (np.sqrt(1.0 + xi**2) - 1.0), 0.0)
    return float(res) if np.ndim(res) == 0 else res


# =====================================================================
# 3. Exact Analytical Sensitivities (Gradients & Elasticities)
# =====================================================================

def sensitivity_critical_force(
    weight_kn: float,
    d1_m: float,
    d2_m: float,
) -> Dict[str, float]:
    """Partial derivatives of critical force F_cr with respect to direct variables."""
    f_cr = weight_kn * d1_m / d2_m
    return {
        "dFcr_dd1": weight_kn / d2_m,
        "dFcr_dd2": -weight_kn * d1_m / (d2_m**2),
        "dFcr_dW": d1_m / d2_m,
        "dFcr_dH1": 0.0,
        "dFcr_dH2": 0.0,
        "elasticity_d1": 1.0,
        "elasticity_d2": -1.0,
        "elasticity_W": 1.0,
        "elasticity_H1": 0.0,
        "elasticity_H2": 0.0,
    }


def sensitivity_limit_rotation(
    d1_m: float,
    h1_m: float,
) -> Dict[str, float]:
    """Partial derivatives and elasticities of limit rotation theta_0 with respect to (d1, H1)."""
    denom = d1_m**2 + h1_m**2
    theta_0 = np.arctan2(d1_m, h1_m)
    
    dtheta_dd1 = h1_m / denom
    dtheta_dH1 = -d1_m / denom
    
    elasticity_d1 = (d1_m / theta_0) * dtheta_dd1 if theta_0 > 0 else 0.0
    elasticity_h1 = (h1_m / theta_0) * dtheta_dH1 if theta_0 > 0 else 0.0
    
    return {
        "theta_0_rad": theta_0,
        "theta_0_deg": float(np.degrees(theta_0)),
        "dtheta_dd1": dtheta_dd1,
        "dtheta_dH1": dtheta_dH1,
        "dtheta_dd2": 0.0,
        "dtheta_dH2": 0.0,
        "dtheta_dW": 0.0,
        "elasticity_d1": elasticity_d1,
        "elasticity_H1": elasticity_h1,
        "elasticity_d2": 0.0,
        "elasticity_H2": 0.0,
        "elasticity_W": 0.0,
    }


def sensitivity_support_ratio(
    support_ratio: float,
    weight_kn: float,
    aspect_ratio_lambda: float,
    relative_centroid_hg: float,
) -> Dict[str, float]:
    """Analytical sensitivity and elasticity of F_cr and theta_0 with respect to support ratio r = b/B."""
    r = support_ratio
    w = weight_kn
    lam = aspect_ratio_lambda
    hg = relative_centroid_hg
    
    # F_cr = W * (r - 0.5) / (1 - r)
    f_cr = w * (r - 0.5) / (1.0 - r)
    dFcr_dr = 0.5 * w / ((1.0 - r)**2)
    elasticity_fcr_r = (r / f_cr) * dFcr_dr
    
    # theta_0 = arctan((r - 0.5) / (hg * lambda))
    xi = (r - 0.5) / (hg * lam)
    theta_0 = np.arctan(xi)
    dtheta_dr = (1.0 / (1.0 + xi**2)) * (1.0 / (hg * lam))
    elasticity_theta0_r = (r / theta_0) * dtheta_dr if theta_0 > 0 else 0.0
    
    return {
        "F_cr": f_cr,
        "dFcr_dr": dFcr_dr,
        "elasticity_Fcr_r": elasticity_fcr_r,
        "theta_0_rad": theta_0,
        "theta_0_deg": float(np.degrees(theta_0)),
        "dtheta_dr": dtheta_dr,
        "elasticity_theta0_r": elasticity_theta0_r,
    }


def sensitivity_post_peak_path(
    theta_rad: float,
    weight_kn: float,
    d1_m: float,
    d2_m: float,
    h1_m: float,
    h2_m: float,
) -> Dict[str, float]:
    """Analytical sensitivities of post-peak force F(theta) at a given rotation theta."""
    cos_t = np.cos(theta_rad)
    sin_t = np.sin(theta_rad)
    
    r_arm = d1_m * cos_t - h1_m * sin_t
    l_arm = d2_m * cos_t + h2_m * sin_t
    
    if l_arm <= 0.0 or r_arm <= 0.0:
        return {
            "F": 0.0,
            "dF_dd1": 0.0, "dF_dd2": 0.0,
            "dF_dH1": 0.0, "dF_dH2": 0.0,
            "dF_dW": 0.0,
            "elasticity_d1": 0.0, "elasticity_d2": 0.0,
            "elasticity_H1": 0.0, "elasticity_H2": 0.0,
            "elasticity_W": 0.0,
        }
    
    f_val = weight_kn * r_arm / l_arm
    
    dF_dd1 = weight_kn * cos_t / l_arm
    dF_dd2 = -weight_kn * r_arm * cos_t / (l_arm**2)
    dF_dH1 = -weight_kn * sin_t / l_arm
    dF_dH2 = -weight_kn * r_arm * sin_t / (l_arm**2)
    dF_dW = r_arm / l_arm
    
    return {
        "F": f_val,
        "dF_dd1": dF_dd1,
        "dF_dd2": dF_dd2,
        "dF_dH1": dF_dH1,
        "dF_dH2": dF_dH2,
        "dF_dW": dF_dW,
        "elasticity_d1": (d1_m / f_val) * dF_dd1,
        "elasticity_d2": (d2_m / f_val) * dF_dd2,
        "elasticity_H1": (h1_m / f_val) * dF_dH1,
        "elasticity_H2": (h2_m / f_val) * dF_dH2,
        "elasticity_W": 1.0,
    }


# =====================================================================
# 4. Geometry Builder & Scenario Evaluator
# =====================================================================

def make_wall_system(
    foundation_length_x_m: float,
    foundation_breadth_y_m: float,
    foundation_height_z_m: float,
    foundation_gamma_kn_m3: float,
    wall_length_x_m: float,
    wall_breadth_y_m: float,
    wall_height_z_m: float,
    wall_gamma_kn_m3: float,
) -> WallSystemGeometry:
    """Build a complete WallSystemGeometry object from physical component dimensions."""
    fnd = RectangularComponent(
        name="Foundation",
        length_x=foundation_length_x_m,
        breadth_y=foundation_breadth_y_m,
        height_z=foundation_height_z_m,
        specific_weight=foundation_gamma_kn_m3,
    )
    wall = RectangularComponent(
        name="Pier/wall",
        length_x=wall_length_x_m,
        breadth_y=wall_breadth_y_m,
        height_z=wall_height_z_m,
        specific_weight=wall_gamma_kn_m3,
    )
    return WallSystemGeometry(
        foundation=fnd,
        pier_wall=wall,
        load_y=-0.5 * foundation_breadth_y_m,
    )


def evaluate_scour_scenario(
    system: WallSystemGeometry,
    support_ratio: float,
) -> ScourScenarioAnalytical:
    """Evaluate all analytical metrics for a given wall geometry and support ratio r = b/B."""
    b_total = system.foundation_breadth
    supported_width = b_total * support_ratio
    scoured_width = b_total - supported_width
    
    pivot_y = system.load_y + scoured_width
    d1 = system.centroid_y_g - pivot_y
    d2 = pivot_y - system.load_y
    
    w = system.total_weight
    h1 = system.centroid_h1
    h2 = system.load_elevation_h2
    
    f_cr = critical_force(w, d1, d2)
    theta_0 = limit_rotation_angle(d1, h1)
    theta_0_deg = float(np.degrees(theta_0))
    slope_0 = initial_softening_slope(w, d1, d2, h1, h2)
    
    u_y0, u_z0 = kinematic_displacements(theta_0, d2, h2)
    energy = overturning_work_capacity(w, d1, h1)
    
    return ScourScenarioAnalytical(
        support_ratio=support_ratio,
        foundation_breadth=b_total,
        scoured_width=scoured_width,
        supported_width=supported_width,
        pivot_y=pivot_y,
        d1=d1,
        d2=d2,
        f_cr=f_cr,
        theta_0_rad=theta_0,
        theta_0_deg=theta_0_deg,
        initial_slope_kn_per_rad=slope_0,
        u_y0=u_y0,
        u_z0=u_z0,
        max_energy_kn_m=energy,
    )


# =====================================================================
# 5. Sensitivity Sweep Utilities
# =====================================================================

def one_at_a_time_sweep(
    baseline_params: Dict[str, float],
    variation_pcts: np.ndarray,
    evaluate_fn: Callable[[Dict[str, float]], Dict[str, float]],
) -> Dict[str, Dict[str, np.ndarray]]:
    """Perform One-At-A-Time (OAT) parameter variations and return metric responses."""
    results: Dict[str, Dict[str, List[float]]] = {}
    
    # Identify output keys from baseline
    base_output = evaluate_fn(baseline_params)
    out_keys = list(base_output.keys())
    
    for p_name in baseline_params:
        results[p_name] = {k: [] for k in out_keys}
        for pct in variation_pcts:
            perturbed = dict(baseline_params)
            perturbed[p_name] = baseline_params[p_name] * (1.0 + pct / 100.0)
            out = evaluate_fn(perturbed)
            for k in out_keys:
                results[p_name][k].append(out[k])
                
    # Convert lists to numpy arrays
    final_results: Dict[str, Dict[str, np.ndarray]] = {}
    for p_name in baseline_params:
        final_results[p_name] = {k: np.asarray(v) for k, v in results[p_name].items()}
    return final_results


def grid_2d_sweep(
    param1_name: str,
    param1_vals: np.ndarray,
    param2_name: str,
    param2_vals: np.ndarray,
    fixed_params: Dict[str, float],
    evaluate_fn: Callable[[Dict[str, float]], float],
) -> np.ndarray:
    """Evaluate a metric over a 2D grid of two parameter variations."""
    grid = np.zeros((len(param2_vals), len(param1_vals)))
    for j, v2 in enumerate(param2_vals):
        for i, v1 in enumerate(param1_vals):
            p = dict(fixed_params)
            p[param1_name] = v1
            p[param2_name] = v2
            grid[j, i] = evaluate_fn(p)
    return grid


def compute_sobol_indices_mc(
    param_bounds: Dict[str, Tuple[float, float]],
    model_fn: Callable[[np.ndarray], np.ndarray],
    n_samples: int = 20000,
    seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """Estimate first-order (S_i) and total-order (S_Ti) Sobol sensitivity indices via Monte Carlo (Saltelli scheme)."""
    rng = np.random.default_rng(seed)
    p_names = list(param_bounds.keys())
    d = len(p_names)
    
    # Generate matrices A and B in [0, 1]^d
    mat_a = rng.random((n_samples, d))
    mat_b = rng.random((n_samples, d))
    
    # Transform to physical domains
    def to_physical(unit_mat: np.ndarray) -> np.ndarray:
        res = np.zeros_like(unit_mat)
        for idx, name in enumerate(p_names):
            low, high = param_bounds[name]
            res[:, idx] = low + unit_mat[:, idx] * (high - low)
        return res
    
    phys_a = to_physical(mat_a)
    phys_b = to_physical(mat_b)
    
    y_a = model_fn(phys_a)
    y_b = model_fn(phys_b)
    
    var_total = np.var(y_a, ddof=1)
    if var_total < 1e-14:
        return {name: {"S1": 0.0, "ST": 0.0} for name in p_names}
    
    sobol_results = {}
    for idx, name in enumerate(p_names):
        # Matrix AB_i: B with column i from A
        mat_ab_i = mat_b.copy()
        mat_ab_i[:, idx] = mat_a[:, idx]
        phys_ab_i = to_physical(mat_ab_i)
        y_ab_i = model_fn(phys_ab_i)
        
        # Saltelli estimator for first order
        # V_i = (1/N) * sum(Y_B * (Y_AB_i - Y_A))
        v_i = np.mean(y_b * (y_ab_i - y_a))
        s1 = v_i / var_total
        
        # Saltelli estimator for total order
        # V_Ti = (1/(2N)) * sum((Y_A - Y_AB_i)^2)
        v_ti = 0.5 * np.mean((y_a - y_ab_i)**2)
        st = v_ti / var_total
        
        sobol_results[name] = {
            "S1": float(np.clip(s1, 0.0, 1.0)),
            "ST": float(np.clip(st, 0.0, 1.0)),
        }
        
    return sobol_results
