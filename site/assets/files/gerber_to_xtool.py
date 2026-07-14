"""
Gerber copper layer -> xTool-ready SVGs (+DXF).

Usage: python3 gerber_to_xtool.py <copper.gbr> [output_prefix]

Outputs (all mm, exact scale, every shape a simple hole-free contour):
  <prefix>_ENGRAVE_regions.svg  isolation areas to burn (the negative)
  <prefix>_TWO_COLOR.svg        black = keep copper, red = engrave
  <prefix>_copper_flat.svg      positive copper artwork
  <prefix>_copper.dxf           copper as solid hatches (mm)
  <prefix>_preview.png          render for visual verification

Interior holes are removed with 0.03 mm keyhole slits (below laser kerf)
because xTool Creative Space does not reliably render compound-path holes.
"""
import sys, math, os
import gerbonara
from shapely.geometry import LineString, Polygon, Point, box
from shapely.ops import unary_union, nearest_points
from shapely import affinity
from shapely.validation import make_valid

def pick_gerber():
    """Return a Gerber path: use argv[1] if given, else pop up a file picker,
    falling back to a typed path if no GUI is available."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askopenfilename(
            title="Select a copper Gerber file",
            filetypes=[("Gerber files", "*.gbr *.GBR *.gtl *.GTL *.gbl *.GBL *.g*"),
                       ("All files", "*.*")],
        )
        root.destroy()
        return path
    except Exception:
        return input("Path to copper Gerber file: ").strip().strip('"')

SRC = pick_gerber()
if not SRC:
    sys.exit("No Gerber file selected. Exiting.")
if not os.path.isfile(SRC):
    sys.exit("File not found: %s" % SRC)
PREFIX = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(SRC))[0]
OUT = os.environ.get('OUTDIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output_for_xtool'))
os.makedirs(OUT, exist_ok=True)
SLIT = 0.03
ARC_TOL = 0.002

f = gerbonara.rs274x.GerberFile.open(SRC)

def prim_to_shapely(p):
    n = type(p).__name__
    if n == 'Line':
        return LineString([(p.x1,p.y1),(p.x2,p.y2)]).buffer(p.width/2, cap_style='round', quad_segs=32)
    if n == 'Circle':
        return Point(p.x, p.y).buffer(p.r, quad_segs=32)
    if n == 'Rectangle':
        g = box(p.x-p.w/2, p.y-p.h/2, p.x+p.w/2, p.y+p.h/2)
        if getattr(p, 'rotation', 0):
            g = affinity.rotate(g, p.rotation, origin=(p.x,p.y), use_radians=True)
        return g
    if n == 'ArcPoly':
        flat = p.approximate_arcs(max_error=ARC_TOL)
        pts = [(x,y) for x,y in flat.outline]
        if len(pts) >= 3:
            return Polygon(pts)
    return None

order = []
for o in f.objects:
    for p in o.to_primitives(unit='mm'):
        g = prim_to_shapely(p)
        if g is not None and not g.is_empty:
            order.append((make_valid(g), p.polarity_dark))

n_clear = sum(1 for _, d in order if not d)
if n_clear == 0:
    copper = unary_union([g for g,_ in order])
else:
    from itertools import groupby
    copper = None
    for dark_flag, grp in groupby(order, key=lambda t: t[1]):
        g = unary_union([x for x,_ in grp])
        if copper is None:
            copper = g if dark_flag else Polygon()
        else:
            copper = copper.union(g) if dark_flag else copper.difference(g)

copper = copper.buffer(0.005, quad_segs=8).buffer(-0.005, quad_segs=8).simplify(0.002)
b = copper.bounds
board = box(*b)
engrave = board.difference(copper)

def as_polys(g):
    if isinstance(g, Polygon): return [g] if g.area > 1e-6 else []
    return [p for p in getattr(g,'geoms',[]) if isinstance(p, Polygon) and p.area > 1e-6]

def dehole(p):
    out, stack, guard = [], [p], 0
    while stack:
        guard += 1
        if guard > 5000: raise RuntimeError("dehole runaway")
        q = stack.pop()
        if q.is_empty or q.area < 1e-6: continue
        if not q.interiors:
            out.append(q); continue
        hole = Polygon(q.interiors[0])
        a, bp = nearest_points(hole.exterior, LineString(q.exterior.coords))
        dx, dy = bp.x-a.x, bp.y-a.y
        L = math.hypot(dx, dy) or 1.0
        if L < 1e-9: dx, dy, L = 1.0, 0.0, 1.0
        ext = 0.05
        cut = LineString([(a.x-dx/L*ext, a.y-dy/L*ext),
                          (bp.x+dx/L*ext, bp.y+dy/L*ext)]).buffer(SLIT/2, cap_style='flat')
        stack.extend(as_polys(make_valid(q.difference(cut))))
    return out

copper_flat  = [q for p in as_polys(copper)  for q in dehole(p)]
engrave_flat = [q for p in as_polys(engrave) for q in dehole(p)]
assert sum(len(p.interiors) for p in copper_flat + engrave_flat) == 0

minx, miny, maxx, maxy = board.bounds
W, H = maxx-minx, maxy-miny
fx = lambda x: x-minx; fy = lambda y: maxy-y
def pd(p):
    return 'M ' + ' L '.join(f'{fx(x):.4f} {fy(y):.4f}' for x,y in p.exterior.coords) + ' Z'
def svg(groups, fn):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.4f}mm" height="{H:.4f}mm" viewBox="0 0 {W:.4f} {H:.4f}">']
    for gid, color, polys in groups:
        s.append(f'<g id="{gid}" fill="{color}" stroke="none">')
        s += [f'<path d="{pd(p)}"/>' for p in polys]
        s.append('</g>')
    s.append('</svg>')
    open(fn, 'w').write('\n'.join(s))

# Only the black & white ENGRAVE-regions SVG is produced (removed/engraved parts = black).
svg([('engrave','#000000',engrave_flat)], f'{OUT}/{PREFIX}_ENGRAVE_regions.svg')

# --- Other outputs disabled (uncomment a block to re-enable) ---
# svg([('copper_keep','#000000',copper_flat), ('engrave','#ff0000',engrave_flat)], f'{OUT}/{PREFIX}_TWO_COLOR.svg')
# svg([('copper','#000000',copper_flat)], f'{OUT}/{PREFIX}_copper_flat.svg')

# import ezdxf
# doc = ezdxf.new('R2010'); doc.header['$INSUNITS'] = 4
# m = doc.modelspace()
# doc.layers.add('COPPER', color=1); doc.layers.add('COPPER_OUTLINE', color=2)
# for p in copper_flat:
#     h = m.add_hatch(color=1, dxfattribs={'layer':'COPPER'}); h.set_solid_fill()
#     h.paths.add_polyline_path(list(p.exterior.coords), is_closed=True, flags=1)
#     m.add_lwpolyline(list(p.exterior.coords), close=True, dxfattribs={'layer':'COPPER_OUTLINE'})
# doc.saveas(f'{OUT}/{PREFIX}_copper.dxf')

# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# from matplotlib.patches import PathPatch
# from matplotlib.path import Path as MplPath
# def patch(poly, **kw):
#     pts = list(poly.exterior.coords)
#     codes = [MplPath.MOVETO]+[MplPath.LINETO]*(len(pts)-2)+[MplPath.CLOSEPOLY]
#     return PathPatch(MplPath(pts, codes), **kw)
# fig, axes = plt.subplots(2, 1, figsize=(12, 2.2 + 9*H/W), dpi=140)
# axes[0].set_title('ENGRAVE regions (laser burns these)')
# for p in engrave_flat: axes[0].add_patch(patch(p, facecolor='#222'))
# axes[1].set_title('black = keep copper, red = engrave')
# for p in copper_flat: axes[1].add_patch(patch(p, facecolor='#111'))
# for p in engrave_flat: axes[1].add_patch(patch(p, facecolor='#e33'))
# for ax in axes:
#     ax.autoscale_view(); ax.set_aspect('equal'); ax.axis('off')
# fig.tight_layout(); fig.savefig(f'{OUT}/{PREFIX}_preview.png', facecolor='white', bbox_inches='tight')

print(f"board {W:.2f} x {H:.2f} mm | copper {copper.area:.1f} mm2 in {len(copper_flat)} shapes | "
      f"engrave {engrave.area:.1f} mm2 in {len(engrave_flat)} shapes")
iso = sorted(p.distance(max(copper_flat, key=lambda q:q.area)) for p in copper_flat if p.area != max(q.area for q in copper_flat))[:3]
print("smallest isolation gaps to largest island (mm):", [round(x,4) for x in iso])
