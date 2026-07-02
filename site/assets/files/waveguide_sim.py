"""
============================================================================
 Waveguide-coupled vs free-space-coupled optocoupler
 ---------------------------------------------------------------------------
 Side-by-side simulation showing how inserting a waveguide between the LED
 and the photo-detector increases the injection efficiency Gamma_oc and
 therefore the collector current and CTR.

 Same Petritz physics as optocoupler_sim.py.  The ONLY thing that changes
 between the two devices is how photons get from the LED to the detector:

     Free-space coupling          Waveguide coupling
     -------------------          ------------------
     Lambertian emission into     Only photons within the waveguide
     4*pi sr.  Geometric          numerical aperture cone are captured.
     capture efficiency is        Once guided, light propagates with only
     Omega_det / (2 pi)  for a    material attenuation exp(-alpha L) - no
     Lambertian source, which     1/r^2 spreading.  Mode overlap with the
     for a 440 um detector at     detector is near-unity.
     2 mm standoff is a few %.

     eta_NA  = NA^2               (small-source Lambertian -> fiber/WG)
     eta_att = exp(-alpha_g L)    (material loss inside guide)
     eta_c2d = 1 - exp(-k t)      (WG-to-detector mode overlap; near 1)
     Gamma_oc,wg = eta_NA * eta_att * eta_c2d

 Typical numbers for a polymer or SiN planar waveguide coupling an IR LED
 into a photodiode across 2 mm:
     NA = 0.55   -> eta_NA  = 0.30
     alpha_g = 0.5 dB/mm, L = 2 mm -> eta_att ~ 0.79
     eta_c2d ~ 0.92
     -> Gamma_oc,wg ~ 22%       vs  ~ 5.5% free-space
============================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib as mpl

# -------------------- constants --------------------
q   = 1.602176634e-19
h   = 6.62607015e-34
c0  = 2.99792458e8

# -------------------- base parameters --------------------
# same as optocoupler_sim.py (Petritz / WL-OCPT-style)
BASE = dict(
    I_F        = 5.0e-3,
    V_CE       = 5.0,
    T          = 298.15,
    wavelength = 940e-9,
    eta_LED0   = 0.28,
    I_F_droop  = 20e-3,
    T_LED_coeff= -0.0035,
    eta_path   = 0.82,
    eta        = 0.65,
    tau        = 2.5e-9,
    tau_t      = 2.0e-9,
    B          = 0.85,
    beta0      = 150.0,
    IC_knee    = 8.0e-3,
    T_beta_coeff = +0.0060,
    V_knee     = 0.22,
    V_A        = 55.0,
)

# -------------------- physics (identical to main sim) --------------------
def eta_LED_effective(I_F, T, p):
    droop = 1.0 / (1.0 + (I_F / p["I_F_droop"])**2)
    Tf = 1.0 + p["T_LED_coeff"] * (T - 298.15)
    return p["eta_LED0"] * droop * max(Tf, 0.05)

def Phi_LED(p):
    return eta_LED_effective(p["I_F"], p["T"], p) * p["I_F"] / q

def eta_star(p):
    return (1.0 + p["B"]) * p["eta"] * p["tau"] / p["tau_t"]

def beta_effective(I_C, T, p):
    x = I_C / p["IC_knee"]
    peak_shape = 2.0 * x / (1.0 + x*x)
    low_end   = 0.45 + 0.55 / (1.0 + 0.3/max(x, 1e-6))
    base = p["beta0"] * 0.85 * (low_end + 0.35 * peak_shape)
    Tf = 1.0 + p["T_beta_coeff"] * (T - 298.15)
    return base * max(Tf, 0.05)

def VCE_factor(V_CE, p):
    knee  = 1.0 - np.exp(-V_CE / p["V_knee"])
    early = 1.0 + V_CE / p["V_A"]
    return knee * early

def compute(p, Gamma_oc):
    """Full chain for a given coupling efficiency Gamma_oc."""
    phi_led = Phi_LED(p)
    phi_u   = Gamma_oc * p["eta_path"] * phi_led
    I_det   = q * phi_u * eta_star(p)
    vf      = VCE_factor(p["V_CE"], p)
    I_c     = I_det * p["beta0"] * vf
    for _ in range(6):
        b   = beta_effective(I_c, p["T"], p)
        I_c = I_det * b * vf
    ctr = I_c / p["I_F"] if p["I_F"] > 0 else 0.0
    return dict(phi_led=phi_led, phi_u=phi_u, I_det=I_det, I_C=I_c,
                beta=b, CTR=ctr, Gamma=Gamma_oc)

# -------------------- coupling-efficiency models --------------------
def gamma_free_space(NA_det, distance, det_half):
    """Lambertian source -> planar detector across free space.
       For a Lambertian emitter, the fraction of power captured by a
       detector subtending half-angle theta_d is sin^2(theta_d).  The
       detector's effective half-angle is arctan(det_half/distance)."""
    theta = np.arctan(det_half / distance)
    eta_geom = np.sin(theta)**2
    # epoxy/package absorption already handled by eta_path elsewhere
    # add a small packaging efficiency for the LED output cone
    eta_pkg = 0.70
    return eta_geom * eta_pkg

def gamma_waveguide(NA_wg, alpha_g_dB_per_mm, length_mm, mode_overlap):
    """Lambertian source -> NA-limited capture -> guided propagation
       -> mode overlap with detector."""
    eta_NA  = NA_wg**2                               # Lambertian into NA
    alpha_m = alpha_g_dB_per_mm * np.log(10)/10      # dB/mm -> Np/mm
    eta_att = np.exp(-alpha_m * length_mm)
    eta_c2d = mode_overlap
    # small input-coupling alignment penalty
    eta_align = 0.85
    return eta_NA * eta_att * eta_c2d * eta_align

# -------------------- styling (match main sim) --------------------
COMSOL_CMAP = LinearSegmentedColormap.from_list(
    "comsol_rainbow",
    [(0.00,"#1b1464"),(0.18,"#1166c6"),(0.38,"#12b9b0"),
     (0.58,"#7ed957"),(0.78,"#ffb641"),(1.00,"#e53935")])

BG, AXBG, FG = "#0b1020", "#0e1730", "#dfe7ff"

mpl.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": AXBG,
    "axes.edgecolor": "#3a4d7a", "axes.labelcolor": FG,
    "xtick.color": FG, "ytick.color": FG, "text.color": FG,
    "font.family": "DejaVu Sans", "axes.titleweight": "bold",
    "axes.titlesize": 10.5, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.facecolor": "#152045", "legend.edgecolor": "#3a4d7a",
    "legend.fontsize": 8,
})

# -------------------- geometry --------------------
LED_POS  = np.array([-1.0, 0.0, 0.0])
DET_POS  = np.array([ 1.0, 0.0, 0.0])
DET_HALF = 0.22

def sample_lambertian(N, rng):
    u1, u2 = rng.random(N), rng.random(N)
    cos_t, sin_t = np.sqrt(u1), np.sqrt(1-u1)
    phi = 2*np.pi*u2
    return np.stack([cos_t, sin_t*np.cos(phi), sin_t*np.sin(phi)], axis=1)

def trace_free_space(n, rng, det_half):
    """Lambertian rays from LED.  Straight lines to x = DET_POS[0]."""
    d = sample_lambertian(n, rng)
    segs, cols = [], []
    hits = 0
    for v in d:
        if v[0] <= 0.02: continue
        t_end = (DET_POS[0] - LED_POS[0]) / v[0]
        pts = LED_POS[None,:] + np.linspace(0,t_end,22)[:,None]*v[None,:]
        I = np.exp(-0.15*np.linspace(0,t_end,22)) * (v[0]**1.2)
        hit = abs(pts[-1,1]) < det_half and abs(pts[-1,2]) < det_half
        if hit: hits += 1
        else: I *= 0.3
        for i in range(len(pts)-1):
            val = float(np.clip(I[i],0,1))
            rgba = COMSOL_CMAP(0.15 + 0.85*val)
            segs.append([pts[i], pts[i+1]])
            cols.append((rgba[0],rgba[1],rgba[2], 0.10 + 0.7*val))
    return segs, cols, hits

def trace_waveguide(n, rng, NA_wg, length_mm, alpha_dB_per_mm):
    """Rays only couple if their angle with +x is within theta_max=asin(NA).
       Captured rays are guided along the core axis with attenuation.
       Rejected rays are shown as faint scatter escaping sideways."""
    d = sample_lambertian(n, rng)
    theta_max = np.arcsin(np.clip(NA_wg, 0.01, 0.99))
    cos_max = np.cos(theta_max)
    segs, cols = [], []
    captured = 0

    alpha_m = alpha_dB_per_mm * np.log(10)/10
    att_end = np.exp(-alpha_m * length_mm)

    wg_r = 0.14   # visual radius of the waveguide core

    for v in d:
        if v[0] <= 0.0: continue
        # launch phase (from LED to WG entry at x=-0.75, very short)
        entry = np.array([-0.78, 0.0, 0.0])
        t_launch = (entry[0] - LED_POS[0]) / v[0]
        launch_pts = LED_POS[None,:] + np.linspace(0,t_launch,4)[:,None]*v[None,:]

        # captured if angle within NA (dot product with +x axis)
        if v[0] >= cos_max:
            # propagate along the waveguide axis, not along v
            # ray follows a slight helix inside the guide for visual effect
            L = np.linspace(0, 1.0, 30)   # parameter along guide
            # lateral offset inside the core: small, decaying with length
            phase = 2*np.pi*np.random.rand()
            r_off = wg_r * 0.45 * (v[1]**2 + v[2]**2)**0.5 / np.sin(theta_max+1e-3)
            r_off = min(r_off, wg_r*0.85)
            th = np.arctan2(v[2], v[1]) + phase
            xs = np.linspace(entry[0], DET_POS[0]-0.05, 30)
            ys = r_off * np.cos(th + 6*L)
            zs = r_off * np.sin(th + 6*L)
            guided = np.stack([xs, ys, zs], axis=1)
            pts = np.vstack([launch_pts, guided])
            # intensity decays along guide
            I_launch = np.ones(len(launch_pts)) * 0.9
            I_guide = np.exp(-alpha_m * length_mm * L) * 0.95
            I = np.concatenate([I_launch, I_guide])
            captured += 1
        else:
            # rejected: escapes sideways from the guide entry
            # continue ray beyond entry for a short distance, dim
            t_esc = t_launch + 0.4
            pts_esc = LED_POS[None,:] + np.linspace(t_launch, t_esc, 8)[:,None]*v[None,:]
            pts = np.vstack([launch_pts, pts_esc])
            I = np.concatenate([np.ones(len(launch_pts))*0.3,
                                np.linspace(0.25, 0.0, len(pts_esc))])

        for i in range(len(pts)-1):
            val = float(np.clip(I[i], 0, 1))
            rgba = COMSOL_CMAP(0.18 + 0.82*val)
            segs.append([pts[i], pts[i+1]])
            cols.append((rgba[0],rgba[1],rgba[2], 0.10 + 0.75*val))
    return segs, cols, captured

# -------------------- 3D scene builders --------------------
def box_faces(cx,cy,cz,sx,sy,sz):
    x0,x1 = cx-sx/2,cx+sx/2; y0,y1 = cy-sy/2,cy+sy/2; z0,z1 = cz-sz/2,cz+sz/2
    v=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
                [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
    return [[v[0],v[1],v[2],v[3]],[v[4],v[5],v[6],v[7]],
            [v[0],v[1],v[5],v[4]],[v[2],v[3],v[7],v[6]],
            [v[1],v[2],v[6],v[5]],[v[0],v[3],v[7],v[4]]]

def setup_scene(ax, title, has_waveguide=False, NA_wg=0.5):
    ax.clear(); ax.set_facecolor(AXBG)
    ax.set_xlim(-1.3,1.3); ax.set_ylim(-0.7,0.7); ax.set_zlim(-0.7,0.7)
    ax.set_box_aspect((2.6,1.4,1.4))
    ax.grid(False)
    for p in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        p.set_facecolor((0.06,0.10,0.20,1.0))
        p.set_edgecolor("#233566")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.set_title(title, color="#9fd0ff", pad=6)

    # LED die
    ax.add_collection3d(Poly3DCollection(
        box_faces(LED_POS[0]-0.05,0,0, 0.10,0.30,0.30),
        facecolor="#ff3b3b", alpha=0.85,
        edgecolor="#ffb0b0", linewidths=0.8))
    # Detector die
    ax.add_collection3d(Poly3DCollection(
        box_faces(DET_POS[0]+0.05,0,0, 0.10,2*DET_HALF*1.6,2*DET_HALF*1.6),
        facecolor="#25c08a", alpha=0.80,
        edgecolor="#a0ffd0", linewidths=0.8))

    if has_waveguide:
        # Waveguide core cylinder
        u = np.linspace(0, 2*np.pi, 40)
        xx = np.linspace(-0.78, DET_POS[0]-0.05, 30)
        r_core = 0.14
        U, X = np.meshgrid(u, xx)
        Y = r_core * np.cos(U); Z = r_core * np.sin(U)
        ax.plot_surface(X, Y, Z,
                        facecolors=np.full(X.shape+(4,), [0.95,0.85,0.20,0.12]),
                        rstride=2, cstride=2, linewidth=0, antialiased=True,
                        shade=False)
        # Cladding cylinder (larger, more transparent)
        r_clad = 0.22
        Y2 = r_clad*np.cos(U); Z2 = r_clad*np.sin(U)
        ax.plot_surface(X, Y2, Z2,
                        facecolors=np.full(X.shape+(4,), [0.40,0.70,0.95,0.05]),
                        rstride=2, cstride=2, linewidth=0, antialiased=True,
                        shade=False)
        # Acceptance cone indicator at input facet
        theta_max = np.arcsin(np.clip(NA_wg,0.01,0.99))
        t = np.linspace(0, 0.25, 2)
        for ph in np.linspace(0, 2*np.pi, 18, endpoint=False):
            xc = -0.78 - t
            yc = np.tan(theta_max) * t * np.cos(ph)
            zc = np.tan(theta_max) * t * np.sin(ph)
            ax.plot(xc, yc, zc, color="#ffd447", lw=0.6, alpha=0.35)
        ax.text(0, 0.30, 0, "WAVEGUIDE", color="#ffd447",
                fontsize=9, ha="center")
    else:
        # Free-space epoxy dome (like main sim)
        u = np.linspace(0, 2*np.pi, 36)
        x = np.linspace(LED_POS[0], DET_POS[0], 22)
        R = 0.55
        U, X = np.meshgrid(u, x)
        shape = (1 - 0.25*np.cos(np.pi*(X-LED_POS[0])/(DET_POS[0]-LED_POS[0])))
        Y = R*np.cos(U)*shape; Z = R*np.sin(U)*shape
        ax.plot_surface(X, Y, Z,
                        facecolors=np.full(X.shape+(4,),[0.38,0.70,0.95,0.06]),
                        rstride=2, cstride=2, linewidth=0, antialiased=True,
                        shade=False)
        ax.text(0, 0.30, 0, "FREE SPACE / EPOXY", color="#7eb8ff",
                fontsize=9, ha="center")

    ax.text(LED_POS[0]-0.1, 0, 0.45, "LED",  color="#ffb0b0",
            fontsize=9, ha="center")
    ax.text(DET_POS[0]+0.1, 0, 0.45, "PD",   color="#a0ffd0",
            fontsize=9, ha="center")
    ax.view_init(elev=20, azim=-58)


# ============================================================
# Figure
# ============================================================
fig = plt.figure(figsize=(17, 9.6))
fig.canvas.manager.set_window_title("Waveguide vs Free-Space Injection Efficiency")

fig.text(0.012, 0.965, "WAVEGUIDE  vs  FREE-SPACE INJECTION EFFICIENCY",
         fontsize=15, weight="bold", color="#9fd0ff")
fig.text(0.012, 0.941,
         "Same LED, same photo-BJT, same Petritz model  -  only the optical "
         "coupling path differs",
         fontsize=9.5, color="#7a90c8", style="italic")

ax_L = fig.add_axes([0.01, 0.50, 0.48, 0.42], projection="3d")
ax_R = fig.add_axes([0.51, 0.50, 0.48, 0.42], projection="3d")

# Dedicated slider strip
ax_sl_IF  = fig.add_axes([0.10, 0.465, 0.36, 0.014])
ax_sl_NA  = fig.add_axes([0.62, 0.465, 0.15, 0.014])
ax_sl_L   = fig.add_axes([0.85, 0.465, 0.13, 0.014])

# Analysis panels (lower half)
ax_bar   = fig.add_axes([0.06, 0.27, 0.42, 0.15])
ax_sweep = fig.add_axes([0.55, 0.06, 0.42, 0.36])
ax_hud   = fig.add_axes([0.06, 0.05, 0.42, 0.17])

s_IF = Slider(ax_sl_IF, "I_F [mA]", 0.1, 30.0, valinit=5.0,
              color="#ffb74d", track_color="#223060")
s_NA = Slider(ax_sl_NA, "waveguide NA", 0.10, 0.90, valinit=0.55,
              color="#ffd447", track_color="#223060")
s_L  = Slider(ax_sl_L,  "length [mm]", 0.5, 20.0, valinit=2.0,
              color="#64b5f6", track_color="#223060")
for sl in (s_IF, s_NA, s_L):
    sl.label.set_color(FG); sl.valtext.set_color("#9fd0ff")

# Free-space geometry (fixed physical scale)
FREE_DIST_MM    = 2.0    # LED-to-detector distance in mm
FREE_DET_HALF_MM = 0.22  # detector half-size in mm
ALPHA_G_DB_PER_MM = 0.5  # waveguide propagation loss
MODE_OVERLAP      = 0.92

# ============================================================
_rng     = np.random.default_rng(11)

def redraw_streamlines(NA, L_mm, activity):
    # setup_scene() is called before this and clears the axes completely,
    # so the collections are already gone - we just need to add new ones.
    if activity < 0.02:
        return

    n_rays = int(60 + 180 * activity)

    # free space
    segs, cols, hits_fs = trace_free_space(n_rays, _rng, DET_HALF)
    lc = Line3DCollection(segs, colors=cols, linewidths=1.2)
    ax_L.add_collection(lc)

    # waveguide
    segs, cols, hits_wg = trace_waveguide(n_rays, _rng, NA, L_mm,
                                          ALPHA_G_DB_PER_MM)
    lc2 = Line3DCollection(segs, colors=cols, linewidths=1.2)
    ax_R.add_collection(lc2)


# ============================================================
# Bar chart: coupling-efficiency breakdown
# ============================================================
def draw_bar_breakdown(NA, L_mm):
    ax_bar.clear(); ax_bar.set_facecolor(AXBG)
    ax_bar.set_title("Coupling-efficiency breakdown  $\\Gamma_{oc}$",
                     color="#9fd0ff")

    # free-space components
    theta = np.arctan(FREE_DET_HALF_MM / FREE_DIST_MM)
    fs_geom = np.sin(theta)**2
    fs_pkg  = 0.70
    fs_total = fs_geom * fs_pkg

    # waveguide components
    wg_NA   = NA**2
    alpha_m = ALPHA_G_DB_PER_MM * np.log(10)/10
    wg_att  = np.exp(-alpha_m * L_mm)
    wg_c2d  = MODE_OVERLAP
    wg_aln  = 0.85
    wg_total = wg_NA * wg_att * wg_c2d * wg_aln

    labels = ["LED output\npackaging", "geometric\ncapture",
              "NA capture\n($\\eta_{NA}=NA^2$)",
              "guided\nattenuation", "mode\noverlap",
              "alignment", "TOTAL $\\Gamma_{oc}$"]
    fs_vals = [fs_pkg, fs_geom, 0, 0, 0, 0, fs_total]
    wg_vals = [0, 0, wg_NA, wg_att, wg_c2d, wg_aln, wg_total]

    x = np.arange(len(labels))
    w = 0.38
    ax_bar.bar(x-w/2, np.array(fs_vals)*100, width=w,
               color="#4a7fd6", edgecolor="#7eb8ff", label="Free space")
    ax_bar.bar(x+w/2, np.array(wg_vals)*100, width=w,
               color="#ffb641", edgecolor="#ffd447", label="Waveguide")
    ax_bar.set_xticks(x); ax_bar.set_xticklabels(labels, fontsize=8)
    ax_bar.set_ylabel("efficiency  (%)")
    ax_bar.set_ylim(0, 105)
    ax_bar.grid(alpha=0.2, color="#3a4d7a", axis="y")
    ax_bar.legend(loc="upper right", framealpha=0.85)

    # annotate TOTALS
    ax_bar.text(x[-1]-w/2, fs_total*100+3, f"{fs_total*100:.1f}%",
                ha="center", color="#7eb8ff", fontsize=9, weight="bold")
    ax_bar.text(x[-1]+w/2, wg_total*100+3, f"{wg_total*100:.1f}%",
                ha="center", color="#ffd447", fontsize=9, weight="bold")
    return fs_total, wg_total


# ============================================================
# Sweep: CTR vs I_F for both
# ============================================================
def draw_ctr_sweep(gamma_fs, gamma_wg, I_F_op):
    ax_sweep.clear(); ax_sweep.set_facecolor(AXBG)
    ax_sweep.set_title("CTR vs $I_F$   (same device, two coupling paths)",
                       color="#9fd0ff")
    ax_sweep.set_xscale("log")
    ax_sweep.set_xlabel("$I_F$  (mA)")
    ax_sweep.set_ylabel("CTR  (%)")

    I_range = np.logspace(-1, 1.5, 180) * 1e-3
    ctr_fs = np.empty_like(I_range); ctr_wg = np.empty_like(I_range)
    for i, If in enumerate(I_range):
        pp = dict(BASE); pp["I_F"] = If
        ctr_fs[i] = compute(pp, gamma_fs)["CTR"]
        ctr_wg[i] = compute(pp, gamma_wg)["CTR"]

    ax_sweep.plot(I_range*1e3, ctr_fs*100, color="#4a7fd6", lw=2.2,
                  label="Free space")
    ax_sweep.plot(I_range*1e3, ctr_wg*100, color="#ffb641", lw=2.2,
                  label="Waveguide")
    ax_sweep.fill_between(I_range*1e3, ctr_fs*100, ctr_wg*100,
                          color="#ffb641", alpha=0.10)

    # Operating-point markers
    pp = dict(BASE); pp["I_F"] = I_F_op
    ctr_fs_op = compute(pp, gamma_fs)["CTR"]*100
    ctr_wg_op = compute(pp, gamma_wg)["CTR"]*100
    ax_sweep.plot(I_F_op*1e3, ctr_fs_op, 'o', ms=9,
                  mfc="#4a7fd6", mec="white", mew=1.5, zorder=10)
    ax_sweep.plot(I_F_op*1e3, ctr_wg_op, 'o', ms=9,
                  mfc="#ffd447", mec="white", mew=1.5, zorder=10)

    ax_sweep.grid(alpha=0.2, color="#3a4d7a")
    ax_sweep.legend(loc="lower center", framealpha=0.85)
    ax_sweep.set_xlim(0.1, 30)
    ax_sweep.set_ylim(0, None)
    return ctr_fs_op, ctr_wg_op


# ============================================================
# Numeric comparison HUD
# ============================================================
def draw_hud(gamma_fs, gamma_wg, I_F_op):
    ax_hud.clear(); ax_hud.set_facecolor("#081025")
    ax_hud.set_xlim(0,1); ax_hud.set_ylim(0,1)
    ax_hud.set_xticks([]); ax_hud.set_yticks([])
    for s in ax_hud.spines.values():
        s.set_color("#3a4d7a"); s.set_linewidth(1.2)

    ax_hud.text(0.02, 0.90, "OPERATING-POINT COMPARISON",
                color="#9fd0ff", fontsize=11, weight="bold")
    ax_hud.plot([0.02, 0.98], [0.85, 0.85], color="#3a4d7a", lw=1)

    pp = dict(BASE); pp["I_F"] = I_F_op
    fs = compute(pp, gamma_fs)
    wg = compute(pp, gamma_wg)

    ax_hud.text(0.36, 0.77, "Free space",
                color="#7eb8ff", fontsize=10, weight="bold", ha="center")
    ax_hud.text(0.66, 0.77, "Waveguide",
                color="#ffd447", fontsize=10, weight="bold", ha="center")
    ax_hud.text(0.92, 0.77, "x gain",
                color="#a0ffd0", fontsize=10, weight="bold", ha="center")

    rows = [
        ("$\\Gamma_{oc}$ (coupling)", fs["Gamma"],   wg["Gamma"],   "%",   100),
        ("$\\Phi_{useful}$ (ph/s)",   fs["phi_u"],   wg["phi_u"],   "sci", 1),
        ("$I_{det}$ (A)",             fs["I_det"],   wg["I_det"],   "sci", 1),
        ("$I_C$ (mA)",                fs["I_C"],     wg["I_C"],     "num", 1e3),
        ("CTR (%)",                   fs["CTR"],     wg["CTR"],     "%",   100),
    ]
    y0 = 0.68; dy = 0.12
    for i,(lbl, a, b, kind, sc) in enumerate(rows):
        y = y0 - i*dy
        ax_hud.text(0.02, y, lbl, color="#b9c7ee", fontsize=10)
        if kind == "sci":
            sa = f"{a:.3e}"; sb = f"{b:.3e}"
        elif kind == "%":
            sa = f"{a*sc:7.2f}"; sb = f"{b*sc:7.2f}"
        else:
            sa = f"{a*sc:7.3f}"; sb = f"{b*sc:7.3f}"
        ratio = (b / a) if a > 1e-20 else float("inf")
        ax_hud.text(0.48, y, sa, color="#7eb8ff", fontsize=10,
                    ha="right", family="DejaVu Sans Mono", weight="bold")
        ax_hud.text(0.78, y, sb, color="#ffd447", fontsize=10,
                    ha="right", family="DejaVu Sans Mono", weight="bold")
        ax_hud.text(0.98, y, f"{ratio:5.1f}x", color="#a0ffd0", fontsize=10,
                    ha="right", family="DejaVu Sans Mono", weight="bold")


# ============================================================
# Animation
# ============================================================
_frame_state = {"azL": -58.0, "azR": -58.0}

def animate(frame):
    I_F_op = s_IF.val * 1e-3
    NA     = s_NA.val
    L_mm   = s_L.val

    gamma_fs = gamma_free_space(None, FREE_DIST_MM, FREE_DET_HALF_MM)
    gamma_wg = gamma_waveguide(NA, ALPHA_G_DB_PER_MM, L_mm, MODE_OVERLAP)

    setup_scene(ax_L, "Free-space coupling   (Lambertian -> epoxy -> detector)",
                has_waveguide=False)
    setup_scene(ax_R, f"Waveguide coupling   (NA = {NA:.2f}, L = {L_mm:.1f} mm)",
                has_waveguide=True, NA_wg=NA)

    activity = np.clip(I_F_op/30e-3, 0.0, 1.0)**0.7
    redraw_streamlines(NA, L_mm, activity)

    _frame_state["azL"] += 0.25
    _frame_state["azR"] += 0.25
    ax_L.view_init(elev=20, azim=_frame_state["azL"])
    ax_R.view_init(elev=20, azim=_frame_state["azR"])

    draw_bar_breakdown(NA, L_mm)
    draw_ctr_sweep(gamma_fs, gamma_wg, I_F_op)
    draw_hud(gamma_fs, gamma_wg, I_F_op)
    return []

# Trigger one immediate render
animate(0)

anim = FuncAnimation(fig, animate, interval=80, blit=False,
                     cache_frame_data=False)
plt.show()