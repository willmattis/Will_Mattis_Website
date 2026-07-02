"""
============================================================================
 Real-time phototransistor optocoupler physics simulation
 ---------------------------------------------------------------------------
 Petritz photoconductivity theory (as derived in the provided slide) combined
 with the phenomenological CTR behaviour documented in Wuerth Elektronik
 application note ANO007.

 Equations implemented directly from the derivation slide:

     Phi_LED     = eta_LED * I_F / q                    (LED photon flux)
     Phi_useful  = Gamma_oc * eta_path * Phi_LED        (coupled flux)
     eta*        = (1 + B) * eta * tau / tau_t          (apparent QE)
     I_det       = q * Phi_useful * eta*                (photocurrent)
     I_C         = beta * I_det
     CTR         = I_C / I_F
                 = beta * Gamma_oc * eta_path * eta_LED * (1+B) * eta * tau/tau_t

 On top of the ideal Petritz model, the quantitatively important
 nonlinearities from ANO007 are added so the resulting characteristic
 curves look like a real device:

   * LED: eta_LED(I_F) has efficiency droop at high current.
   * Phototransistor: beta(I_C) rises then rolls off (Gummel-Poon-like).
   * Temperature: LED efficiency decreases with T, beta increases with T.
   * VCE: photo-BJT active-region early effect + saturation knee.

 Visualisation is deliberately styled after COMSOL Multiphysics:
     - deep navy background
     - semi-transparent device geometry with phong-shaded faces
     - ray-traced photon streamlines colour-mapped by local intensity
       (viridis/turbo perceptual colour scale)
     - live HUD panel with computed parameters
     - ANO007-style characteristic graphs on the right-hand side
============================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib as mpl

# ----------------------------------------------------------------------------
# Physical constants
# ----------------------------------------------------------------------------
q   = 1.602176634e-19       # elementary charge  [C]
h   = 6.62607015e-34        # Planck constant    [J s]
c0  = 2.99792458e8          # speed of light     [m/s]
kB  = 1.380649e-23          # Boltzmann          [J/K]

# ----------------------------------------------------------------------------
# Nominal device parameters  (WL-OCPT-817-style device, Bin B)
# ----------------------------------------------------------------------------
P = dict(
    # --- drive ---
    I_F        = 5.0e-3,       # LED forward current  [A]
    V_CE       = 5.0,          # collector-emitter V  [V]
    T          = 298.15,       # ambient temperature  [K]

    # --- LED ---
    wavelength = 940e-9,       # IR LED peak          [m]
    eta_LED0   = 0.28,         # LED IQE at low drive
    I_F_droop  = 20e-3,        # droop scale current  [A]
    T_LED_coeff= -0.0035,      # fractional dP/dT 1/K

    # --- optical path ---
    # Gamma_oc captures the fraction of LED photons that (a) exit the LED
    # package, (b) are geometrically aimed at the detector, AND (c) are
    # actually absorbed within the photo-BJT's base region.  For a
    # commercial SO-4 optocoupler this end-to-end efficiency is a few %.
    Gamma_oc   = 0.055,
    eta_path   = 0.82,         # epoxy transmission

    # --- photo-BJT (Petritz / active region) ---
    # eta* = (1+B) * eta * tau/tau_t is the "apparent quantum efficiency"
    # of the photo-absorbing base region (Petritz, 1956).  For a typical
    # optocoupler photo-BJT this term lands near unity - the real current
    # gain comes from the BJT beta that multiplies it.
    eta        = 0.65,         # intrinsic QE of base
    tau        = 2.5e-9,       # effective carrier lifetime [s]
    tau_t      = 2.0e-9,       # base transit time          [s]
    B          = 0.85,         # barrier modulation B

    # --- BJT gain ---
    beta0      = 150.0,        # low-frequency current gain
    IC_knee    = 8.0e-3,       # gain-rolloff knee  [A]
    T_beta_coeff = +0.0060,    # fractional dBeta/dT

    # --- VCE behaviour ---
    V_knee     = 0.22,         # saturation knee    [V]
    V_A        = 55.0,         # Early voltage      [V]
)


# ============================================================================
# Physics model  -- every line below corresponds 1:1 to a slide equation.
# ============================================================================

def photon_energy(wavelength):
    """E = h c / lambda"""
    return h * c0 / wavelength

def eta_LED_effective(I_F, T, p):
    """LED wall-plug efficiency with droop + T coefficient.
       At low I_F -> eta_LED0.  At high I_F the efficiency rolls off."""
    droop = 1.0 / (1.0 + (I_F / p["I_F_droop"])**2)
    T_factor = 1.0 + p["T_LED_coeff"] * (T - 298.15)
    return p["eta_LED0"] * droop * max(T_factor, 0.05)

def Phi_LED(p):
    """Phi_LED = eta_LED * I_F / q   (photons per second)"""
    return eta_LED_effective(p["I_F"], p["T"], p) * p["I_F"] / q

def Phi_useful(p):
    """Phi_useful = Gamma_oc * eta_path * Phi_LED"""
    return p["Gamma_oc"] * p["eta_path"] * Phi_LED(p)

def eta_star(p):
    """Apparent quantum efficiency  eta* = (1+B) * eta * tau / tau_t"""
    return (1.0 + p["B"]) * p["eta"] * p["tau"] / p["tau_t"]

def I_det(p):
    """I_det = q * Phi_useful * eta*     (primary photocurrent in base)"""
    return q * Phi_useful(p) * eta_star(p)

def beta_effective(I_C, T, p):
    """beta(I_C, T).  Rises from a low-current value, peaks near IC_knee,
       then rolls off (high-level injection + webster effect)."""
    x = I_C / p["IC_knee"]
    peak_shape = 2.0 * x / (1.0 + x*x)            # Lorentzian-ish hump
    low_end   = 0.45 + 0.55 / (1.0 + 0.3/max(x, 1e-6))
    base = p["beta0"] * 0.85 * (low_end + 0.35 * peak_shape)
    T_factor = 1.0 + p["T_beta_coeff"] * (T - 298.15)
    return base * max(T_factor, 0.05)

def VCE_factor(V_CE, p):
    """Active-region scaling vs VCE: saturation knee + Early effect."""
    knee    = 1.0 - np.exp(-V_CE / p["V_knee"])
    early   = 1.0 + V_CE / p["V_A"]
    return knee * early

def I_C(p):
    """Full collector current:  beta(I_C) * I_det * VCE_factor.
       Solved iteratively because beta depends on I_C."""
    Id = I_det(p)
    vf = VCE_factor(p["V_CE"], p)
    Ic = Id * p["beta0"] * vf                      # initial guess
    for _ in range(6):                             # fixed-point iteration
        b = beta_effective(Ic, p["T"], p)
        Ic = Id * b * vf
    return Ic, beta_effective(Ic, p["T"], p), Id

def CTR(p):
    Ic, b, Id = I_C(p)
    if p["I_F"] <= 0:
        return 0.0, Ic, b, Id
    return Ic / p["I_F"], Ic, b, Id


# ============================================================================
# COMSOL-like colormap  (navy -> teal -> green -> amber -> red)
# ============================================================================
COMSOL_CMAP = LinearSegmentedColormap.from_list(
    "comsol_rainbow",
    [(0.00, "#1b1464"),
     (0.18, "#1166c6"),
     (0.38, "#12b9b0"),
     (0.58, "#7ed957"),
     (0.78, "#ffb641"),
     (1.00, "#e53935")]
)

BG   = "#0b1020"
AXBG = "#0e1730"
FG   = "#dfe7ff"


# ============================================================================
# 3D streamline generation
# ----------------------------------------------------------------------------
# Photons emitted from the LED surface follow a Lambertian angular
# distribution.  For visual clarity we carve them into a forward fan aimed
# at the phototransistor die, modulated by local intensity (Beer-Lambert in
# the epoxy plus a cos(theta) Lambertian weight).  Each streamline is shaded
# along its length by the remaining power it carries.
# ============================================================================

LED_POS = np.array([-0.9, 0.0, 0.0])
DET_POS = np.array([ 0.9, 0.0, 0.0])
DET_HALF = 0.22            # half-size of detector face
EPOXY_ALPHA = 0.25         # optical absorption per unit length in epoxy

def sample_lambertian_rays(N, rng):
    """Lambertian emission cone biased toward +x.  Returns N unit vectors."""
    # cos-weighted hemisphere
    u1 = rng.random(N)
    u2 = rng.random(N)
    cos_t = np.sqrt(u1)
    sin_t = np.sqrt(1 - u1)
    phi   = 2 * np.pi * u2
    # local frame: z is the LED normal direction (+x in world)
    lx = sin_t * np.cos(phi)
    ly = sin_t * np.sin(phi)
    lz = cos_t
    # rotate (lz -> +x)
    dirs = np.stack([lz, lx, ly], axis=1)
    return dirs

def build_streamlines(n_rays, rng):
    """Trace rays from LED to detector plane.  Return list of polylines
       each with an attenuation-scaled intensity per vertex."""
    dirs = sample_lambertian_rays(n_rays, rng)
    lines = []
    intensities = []
    hits = 0
    for d in dirs:
        if d[0] <= 0.02:
            continue
        # parametric march toward detector x-plane
        t_end = (DET_POS[0] - LED_POS[0]) / d[0]
        if t_end <= 0:
            continue
        ts = np.linspace(0, t_end, 28)
        pts = LED_POS[None, :] + ts[:, None] * d[None, :]

        # Beer-Lambert attenuation along the ray
        I = np.exp(-EPOXY_ALPHA * ts) * (d[0] ** 1.2)   # Lambertian weight
        hit = (abs(pts[-1, 1]) < DET_HALF) and (abs(pts[-1, 2]) < DET_HALF)
        if hit:
            hits += 1
            I *= 1.0
        else:
            I *= 0.35   # dim the rays that miss the detector
        lines.append(pts)
        intensities.append(I)
    return lines, intensities, hits


# ============================================================================
# 3D device geometry (COMSOL-style translucent solids)
# ============================================================================
def box_faces(cx, cy, cz, sx, sy, sz):
    """Return six quadrilateral faces for a box centred at (cx,cy,cz)."""
    x0, x1 = cx - sx/2, cx + sx/2
    y0, y1 = cy - sy/2, cy + sy/2
    z0, z1 = cz - sz/2, cz + sz/2
    v = np.array([
        [x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
        [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1],
    ])
    faces = [
        [v[0],v[1],v[2],v[3]],
        [v[4],v[5],v[6],v[7]],
        [v[0],v[1],v[5],v[4]],
        [v[2],v[3],v[7],v[6]],
        [v[1],v[2],v[6],v[5]],
        [v[0],v[3],v[7],v[4]],
    ]
    return faces

def epoxy_dome_mesh():
    """A capped cylinder along x connecting LED and detector - represents
       the clear coupling medium."""
    u = np.linspace(0, 2*np.pi, 40)
    x = np.linspace(LED_POS[0], DET_POS[0], 24)
    R = 0.55
    U, X = np.meshgrid(u, x)
    Y = R * np.cos(U) * (1 - 0.25*np.cos(np.pi*(X-LED_POS[0])/(DET_POS[0]-LED_POS[0])))
    Z = R * np.sin(U) * (1 - 0.25*np.cos(np.pi*(X-LED_POS[0])/(DET_POS[0]-LED_POS[0])))
    return X, Y, Z


# ============================================================================
# Figure layout
# ============================================================================
mpl.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor"  : AXBG,
    "axes.edgecolor"  : "#3a4d7a",
    "axes.labelcolor" : FG,
    "xtick.color"     : FG,
    "ytick.color"     : FG,
    "text.color"      : FG,
    "font.family"     : "DejaVu Sans",
    "axes.titleweight": "bold",
    "axes.titlesize"  : 10.5,
    "axes.labelsize"  : 9,
    "xtick.labelsize" : 8,
    "ytick.labelsize" : 8,
    "legend.facecolor": "#152045",
    "legend.edgecolor": "#3a4d7a",
    "legend.fontsize" : 8,
})

fig = plt.figure(figsize=(17, 9.3))
fig.canvas.manager.set_window_title(
    "Optocoupler Photoconductivity Simulation - Petritz model / ANO007"
)

# Title bar
fig.text(0.012, 0.965,
         "OPTOCOUPLER  ::  REAL-TIME PHOTOCONDUCTIVITY SIMULATION",
         fontsize=15, weight="bold", color="#9fd0ff")
fig.text(0.012, 0.942,
         "Petritz photoconductivity model  -  WL-OCPT-style device  -  ANO007 characteristics",
         fontsize=9.5, color="#7a90c8", style="italic")

# 3D field view (left, large - top half of left column)
ax3d = fig.add_axes([0.01, 0.36, 0.54, 0.56], projection="3d")
ax3d.set_facecolor(AXBG)

# HUD / metrics panel (bottom-left, below the sliders)
ax_hud = fig.add_axes([0.02, 0.04, 0.52, 0.22])
ax_hud.set_facecolor("#081025")
ax_hud.set_xticks([]); ax_hud.set_yticks([])
for s in ax_hud.spines.values():
    s.set_color("#3a4d7a"); s.set_linewidth(1.2)

# Four ANO007-style graphs on the right (2x2)
ax_ctr_if   = fig.add_axes([0.57, 0.54, 0.195, 0.38])
ax_ctr_T    = fig.add_axes([0.79, 0.54, 0.195, 0.38])
ax_pd_iv    = fig.add_axes([0.57, 0.08, 0.195, 0.38])
ax_pt_iv    = fig.add_axes([0.79, 0.08, 0.195, 0.38])

# Operating-point markers
op_marker_ctr_if, = ax_ctr_if.plot([], [], 'o', ms=8,
                                   mfc='#ffd447', mec='#ff6f00', mew=1.5, zorder=10)
op_marker_ctr_T,  = ax_ctr_T.plot([], [], 'o', ms=8,
                                   mfc='#ffd447', mec='#ff6f00', mew=1.5, zorder=10)

# Controls row (slim strip between 3D view and HUD panel)
ax_sl_IF = fig.add_axes([0.08, 0.325, 0.42, 0.017])
ax_sl_VCE= fig.add_axes([0.08, 0.300, 0.42, 0.017])
ax_sl_T  = fig.add_axes([0.08, 0.275, 0.42, 0.017])

s_IF  = Slider(ax_sl_IF , "I_F  [mA]", 0.1, 30.0, valinit=P["I_F"]*1e3,
               color="#ffb74d", track_color="#223060")
s_VCE = Slider(ax_sl_VCE, "V_CE  [V]", 0.05, 10.0, valinit=P["V_CE"],
               color="#64b5f6", track_color="#223060")
s_T   = Slider(ax_sl_T  , "T  [degC]", -20.0, 85.0, valinit=P["T"]-273.15,
               color="#81c784", track_color="#223060")

for sl in (s_IF, s_VCE, s_T):
    sl.label.set_color(FG); sl.valtext.set_color("#9fd0ff")

# Reset button (at end of slider row)
ax_btn = fig.add_axes([0.505, 0.275, 0.035, 0.065])
btn_reset = Button(ax_btn, "reset",
                   color="#1a2a55", hovercolor="#26407a")
btn_reset.label.set_color(FG); btn_reset.label.set_fontsize(8)


# ============================================================================
# 3D scene setup (called once)
# ============================================================================
def setup_3d():
    ax3d.clear()
    ax3d.set_facecolor(AXBG)
    ax3d.set_xlim(-1.2, 1.2); ax3d.set_ylim(-0.8, 0.8); ax3d.set_zlim(-0.8, 0.8)
    ax3d.set_box_aspect((2.4, 1.6, 1.6))
    ax3d.grid(False)
    # subtle panes
    for pane in (ax3d.xaxis.pane, ax3d.yaxis.pane, ax3d.zaxis.pane):
        pane.set_facecolor((0.06, 0.10, 0.20, 1.0))
        pane.set_edgecolor("#233566")
    ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])
    ax3d.set_title("3D photon transport  (streamlines colored by local intensity)",
                   color="#9fd0ff", pad=8)

    # Epoxy dome mesh
    X, Y, Z = epoxy_dome_mesh()
    ax3d.plot_surface(X, Y, Z,
                      facecolors=np.full(X.shape + (4,), [0.38, 0.70, 0.95, 0.08]),
                      rstride=2, cstride=2, linewidth=0, antialiased=True,
                      shade=False)

    # LED die (red-ish emissive box)
    led_faces = box_faces(LED_POS[0]-0.05, 0, 0, 0.10, 0.35, 0.35)
    ax3d.add_collection3d(Poly3DCollection(
        led_faces, facecolor="#ff3b3b", alpha=0.85,
        edgecolor="#ffb0b0", linewidths=0.8))

    # Phototransistor die
    det_faces = box_faces(DET_POS[0]+0.05, 0, 0, 0.10,
                          2*DET_HALF*1.6, 2*DET_HALF*1.6)
    ax3d.add_collection3d(Poly3DCollection(
        det_faces, facecolor="#25c08a", alpha=0.80,
        edgecolor="#a0ffd0", linewidths=0.8))

    # Detector active window highlight
    win = [[DET_POS[0], -DET_HALF, -DET_HALF],
           [DET_POS[0],  DET_HALF, -DET_HALF],
           [DET_POS[0],  DET_HALF,  DET_HALF],
           [DET_POS[0], -DET_HALF,  DET_HALF]]
    ax3d.add_collection3d(Poly3DCollection(
        [win], facecolor="#ffd447", alpha=0.25,
        edgecolor="#ffd447", linewidths=1.5))

    # Lead frame stubs
    for (y, label) in [(-0.50, "A"), (0.50, "K"), (-0.50, "C"), (0.50, "E")]:
        pass
    # anode/cathode/collector/emitter leads
    leads = [
        ([LED_POS[0]-0.05, LED_POS[0]-0.05], [-0.22,-0.22], [-0.55,-0.18]),
        ([LED_POS[0]-0.05, LED_POS[0]-0.05], [ 0.22, 0.22], [-0.55,-0.18]),
        ([DET_POS[0]+0.05, DET_POS[0]+0.05], [-0.30,-0.30], [-0.55,-0.22]),
        ([DET_POS[0]+0.05, DET_POS[0]+0.05], [ 0.30, 0.30], [-0.55,-0.22]),
    ]
    for xs, ys, zs in leads:
        ax3d.plot(xs, ys, zs, color="#c5cae9", lw=2.5)

    # labels
    ax3d.text(LED_POS[0]-0.1, 0, 0.55, "IR LED", color="#ffb0b0",
              fontsize=10, ha="center")
    ax3d.text(DET_POS[0]+0.1, 0, 0.55, "PHOTO-BJT", color="#a0ffd0",
              fontsize=10, ha="center")

    ax3d.view_init(elev=22, azim=-56)


# State container for animated lines
_line_coll = {"obj": None}
_rng = np.random.default_rng(7)


def update_streamlines(activity):
    """Trace rays, shade by local intensity, draw as a Line3DCollection."""
    if _line_coll["obj"] is not None:
        try:
            _line_coll["obj"].remove()
        except ValueError:
            pass
        _line_coll["obj"] = None
    if activity < 0.02:
        return 0

    n_rays = int(60 + 180 * activity)
    lines, intens, hits = build_streamlines(n_rays, _rng)

    # Convert each polyline into segments so we can colour along its length
    segs = []
    colors = []
    for pts, Iarr in zip(lines, intens):
        for i in range(len(pts)-1):
            segs.append([pts[i], pts[i+1]])
            v = float(np.clip(Iarr[i] * activity, 0, 1))
            rgba = COMSOL_CMAP(0.15 + 0.85*v)
            # boost alpha so bright rays stand out
            colors.append((rgba[0], rgba[1], rgba[2], 0.15 + 0.75*v))

    lc = Line3DCollection(segs, colors=colors, linewidths=1.2)
    ax3d.add_collection(lc)
    _line_coll["obj"] = lc
    return hits


# ============================================================================
# ANO007-style reference graphs (computed from the same model)
# ============================================================================
def draw_ctr_vs_IF():
    """ANO007 Fig 3/4 equivalent: CTR(%) vs I_F for several V_CE."""
    ax_ctr_if.clear()
    ax_ctr_if.set_facecolor(AXBG)
    ax_ctr_if.set_title("CTR vs $I_F$   (at T = 25 degC)", color="#9fd0ff")
    ax_ctr_if.set_xscale("log")
    ax_ctr_if.set_xlabel("$I_F$  (mA)"); ax_ctr_if.set_ylabel("CTR  (%)")

    I_range = np.logspace(-1, 1.5, 200) * 1e-3
    for Vce, col, lbl in [(5.0, "#64b5f6", "$V_{CE}$ = 5 V (active)"),
                          (1.0, "#81c784", "$V_{CE}$ = 1 V"),
                          (0.4, "#ffb74d", "$V_{CE}$ = 0.4 V (sat)")]:
        pp = dict(P); pp["V_CE"] = Vce; pp["T"] = 298.15
        ctr_arr = np.empty_like(I_range)
        for i, If in enumerate(I_range):
            pp["I_F"] = If
            ctr_arr[i], *_ = CTR(pp)
        ax_ctr_if.plot(I_range*1e3, ctr_arr*100, color=col, lw=2, label=lbl)

    ax_ctr_if.grid(alpha=0.2, color="#3a4d7a")
    ax_ctr_if.legend(loc="lower right", framealpha=0.85)
    ax_ctr_if.set_xlim(0.1, 30)
    ax_ctr_if.set_ylim(0, None)

def draw_ctr_vs_T():
    """ANO007 Fig 7: relative CTR vs Temperature at I_F = 5 mA."""
    ax_ctr_T.clear()
    ax_ctr_T.set_facecolor(AXBG)
    ax_ctr_T.set_title("Relative CTR vs Temperature   ($I_F$ = 5 mA)",
                       color="#9fd0ff")
    ax_ctr_T.set_xlabel("T  (degC)"); ax_ctr_T.set_ylabel("CTR / CTR(25 degC)")
    T_range = np.linspace(-20, 85, 120)
    pp = dict(P); pp["I_F"] = 5e-3; pp["V_CE"] = 5.0
    pp["T"] = 298.15
    c25, *_ = CTR(pp)
    rel = np.empty_like(T_range)
    for i, Tc in enumerate(T_range):
        pp["T"] = Tc + 273.15
        c, *_ = CTR(pp)
        rel[i] = c / c25
    ax_ctr_T.plot(T_range, rel, color="#f06292", lw=2.2)
    ax_ctr_T.axhline(1.0, color="#5f6f96", lw=0.8, ls="--")
    ax_ctr_T.axvline(25,  color="#5f6f96", lw=0.8, ls="--")
    ax_ctr_T.grid(alpha=0.2, color="#3a4d7a")
    ax_ctr_T.set_xlim(-20, 85)

def draw_photodiode_iv():
    """Photodiode-style I-V families (uses same photocurrent generation
       as the phototransistor base)."""
    ax_pd_iv.clear()
    ax_pd_iv.set_facecolor(AXBG)
    ax_pd_iv.set_title("Photodiode-style $I$-$V$ (base junction)",
                       color="#9fd0ff")
    ax_pd_iv.set_xlabel("$V_d$  (V)"); ax_pd_iv.set_ylabel("I  (uA)")
    V = np.linspace(-1.0, 0.7, 300)
    Vt = kB * 298.15 / q
    Is = 2e-12
    for If_mA, col in [(0.0,"#bbbbbb"),(1.0,"#64b5f6"),(5.0,"#81c784"),(10.0,"#ffb74d")]:
        pp = dict(P); pp["I_F"] = If_mA*1e-3
        Iph = I_det(pp) if If_mA > 0 else 0.0
        I = Is * (np.exp(np.clip(V/(1.6*Vt), -40, 25)) - 1.0) - Iph
        lbl = "dark" if If_mA == 0 else f"$I_F$ = {If_mA:g} mA"
        ax_pd_iv.plot(V, I*1e6, color=col, lw=1.8, label=lbl)
    ax_pd_iv.axhline(0, color="#5f6f96", lw=0.8)
    ax_pd_iv.axvline(0, color="#5f6f96", lw=0.8)
    ax_pd_iv.grid(alpha=0.2, color="#3a4d7a")
    ax_pd_iv.legend(loc="lower right", framealpha=0.85)
    ax_pd_iv.set_ylim(-120, 40)

def draw_phototransistor_iv():
    """Phototransistor output characteristics: I_C vs V_CE at several I_F."""
    ax_pt_iv.clear()
    ax_pt_iv.set_facecolor(AXBG)
    ax_pt_iv.set_title("Phototransistor $I_C$ vs $V_{CE}$",
                       color="#9fd0ff")
    ax_pt_iv.set_xlabel("$V_{CE}$  (V)"); ax_pt_iv.set_ylabel("$I_C$  (mA)")
    V = np.linspace(0.01, 5.0, 200)
    for If_mA, col in [(0.0,"#bbbbbb"),(1.0,"#64b5f6"),(2.0,"#26c6da"),
                       (5.0,"#81c784"),(10.0,"#ffb74d"),(20.0,"#ef5350")]:
        pp = dict(P); pp["I_F"] = If_mA*1e-3; pp["T"] = 298.15
        Ic = np.empty_like(V)
        for i, Vce in enumerate(V):
            pp["V_CE"] = Vce
            _, ic, *_ = CTR(pp)
            Ic[i] = ic
        lbl = "dark" if If_mA == 0 else f"{If_mA:g} mA"
        ax_pt_iv.plot(V, Ic*1e3, color=col, lw=1.8, label=lbl)
    ax_pt_iv.grid(alpha=0.2, color="#3a4d7a")
    ax_pt_iv.legend(loc="lower right", framealpha=0.85, ncol=2,
                    title="$I_F$")
    ax_pt_iv.set_xlim(0, 5)
    ax_pt_iv.set_ylim(0, None)


# ============================================================================
# HUD panel
# ============================================================================
_hud_lines = {}
def build_hud():
    ax_hud.clear(); ax_hud.set_facecolor("#081025")
    ax_hud.set_xlim(0,1); ax_hud.set_ylim(0,1)
    ax_hud.set_xticks([]); ax_hud.set_yticks([])
    for s in ax_hud.spines.values():
        s.set_color("#3a4d7a"); s.set_linewidth(1.2)

    ax_hud.text(0.02, 0.88, "LIVE OPERATING POINT",
                color="#9fd0ff", fontsize=12, weight="bold")
    ax_hud.plot([0.02, 0.98], [0.82, 0.82], color="#3a4d7a", lw=1)

    # left column  (drive + optical)
    left_rows = [
        ("I_F",                       "mA",   "if"),
        ("V_CE",                      "V",    "vce"),
        ("T",                         "degC", "t"),
        ("Phi_LED  = eta_LED I_F/q",  "ph/s", "phi_led"),
        ("Phi_useful = Gamma_oc eta_path Phi_LED","ph/s","phi_u"),
        ("eta_LED (I_F, T)",          "",     "eta_led"),
    ]
    # right column (detector + output)
    right_rows = [
        ("eta* = (1+B) eta tau/tau_t","",    "eta_star"),
        ("I_det = q Phi_useful eta*", "A",   "idet"),
        ("beta (I_C, T)",             "",    "beta"),
        ("I_C = beta I_det",          "A",   "ic"),
        ("CTR = I_C/I_F",             "%",   "ctr"),
        ("hv  = hc/lambda",           "eV",  "hv"),
    ]

    y0 = 0.72
    dy = 0.11
    for i,(lbl,unit,key) in enumerate(left_rows):
        y = y0 - i*dy
        ax_hud.text(0.02, y, lbl, color="#b9c7ee", fontsize=9)
        t = ax_hud.text(0.47, y, "---", color="#fff7c2", fontsize=9.5,
                        ha="right", family="DejaVu Sans Mono", weight="bold")
        _hud_lines[key] = (t, unit)
    for i,(lbl,unit,key) in enumerate(right_rows):
        y = y0 - i*dy
        ax_hud.text(0.52, y, lbl, color="#b9c7ee", fontsize=9)
        t = ax_hud.text(0.98, y, "---", color="#fff7c2", fontsize=9.5,
                        ha="right", family="DejaVu Sans Mono", weight="bold")
        _hud_lines[key] = (t, unit)


def fmt_sci(x, unit):
    if abs(x) < 1e-12: return f"  0.000     {unit}"
    exp = int(np.floor(np.log10(abs(x))))
    mant = x / 10**exp
    return f"{mant:6.3f}e{exp:+03d} {unit}"


def update_hud():
    ctr_val, ic, b, idet = CTR(P)
    hv_eV = photon_energy(P["wavelength"]) / q
    vals = {
        "if"      : (P["I_F"]*1e3, "mA"),
        "vce"     : (P["V_CE"],    "V"),
        "t"       : (P["T"]-273.15,"degC"),
        "phi_led" : (Phi_LED(P),   "ph/s"),
        "phi_u"   : (Phi_useful(P),"ph/s"),
        "eta_led" : (eta_LED_effective(P["I_F"], P["T"], P), ""),
        "eta_star": (eta_star(P),  ""),
        "idet"    : (idet,         "A"),
        "beta"    : (b,            ""),
        "ic"      : (ic,           "A"),
        "ctr"     : (ctr_val*100,  "%"),
        "hv"      : (hv_eV,        "eV"),
    }
    for key,(val,unit) in vals.items():
        t,_ = _hud_lines[key]
        if unit in ("mA","V","degC","%","","eV"):
            t.set_text(f"{val:9.3f}  {unit}")
        else:
            t.set_text(fmt_sci(val, unit))


def update_op_markers():
    """Move the orange operating-point dots on the CTR graphs."""
    ctr_val, *_ = CTR(P)
    op_marker_ctr_if.set_data([P["I_F"]*1e3], [ctr_val*100])

    pp = dict(P); pp["I_F"] = 5e-3; pp["V_CE"] = 5.0; pp["T"] = 298.15
    c25, *_ = CTR(pp)
    op_marker_ctr_T.set_data([P["T"]-273.15], [ctr_val/max(c25,1e-12)])


# ============================================================================
# Wire up controls
# ============================================================================
def on_slider(_=None):
    P["I_F"]  = s_IF.val  * 1e-3
    P["V_CE"] = s_VCE.val
    P["T"]    = s_T.val + 273.15

def on_reset(_):
    s_IF.reset(); s_VCE.reset(); s_T.reset()

s_IF.on_changed(on_slider)
s_VCE.on_changed(on_slider)
s_T.on_changed(on_slider)
btn_reset.on_clicked(on_reset)


# ============================================================================
# Initial render
# ============================================================================
setup_3d()
build_hud()
draw_ctr_vs_IF()
draw_ctr_vs_T()
draw_photodiode_iv()
draw_phototransistor_iv()

# re-add the persistent markers (they get wiped by clear())
op_marker_ctr_if, = ax_ctr_if.plot([], [], 'o', ms=9,
                                   mfc='#ffd447', mec='#ff6f00', mew=1.5, zorder=10,
                                   label="operating point")
op_marker_ctr_T,  = ax_ctr_T.plot([], [], 'o', ms=9,
                                   mfc='#ffd447', mec='#ff6f00', mew=1.5, zorder=10)
ax_ctr_if.legend(loc="lower right", framealpha=0.85)


# ============================================================================
# Animation loop
# ============================================================================
_frame_state = {"az": -56.0}

def animate(frame):
    on_slider()

    # Activity level - how brightly the LED is emitting right now
    # (normalized fraction of the slider's maximum current)
    activity = np.clip(P["I_F"] / 30e-3, 0.0, 1.0) ** 0.7

    # Re-draw streamlines - keep geometry, swap the Line3DCollection
    update_streamlines(activity)

    # Very slow auto-orbit for that "live field" feel
    _frame_state["az"] += 0.25
    ax3d.view_init(elev=22, azim=_frame_state["az"])

    update_hud()
    update_op_markers()

    return []

anim = FuncAnimation(fig, animate, interval=60, blit=False,
                     cache_frame_data=False)

plt.show()
