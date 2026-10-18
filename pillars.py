import matplotlib
matplotlib.use("QtAgg")          # or "TkAgg"
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ---------- NEW: user inputs ----------
def ask(prompt, default):
    """Ask for a positive number; press Enter to accept the default."""
    while True:
        s = input(f"{prompt} [default {default}]: ").strip()
        if s == "":
            return float(default)
        try:
            v = float(s)
            if v > 0:
                return v
            print("  Value must be greater than 0.")
        except ValueError:
            print("  Please enter a number.")

D = ask("Density of coal (kg/m3)", 1400)
H = ask("Depth of coal seam (m)", 200)
h = ask("Working height (m)", 3)

# ---------- Starting point: top-left corner of the first rectangle (meters) ----------
X0 = -60.0
Y0 = 40.0

# ---------- Stored variables (meters) ----------
a1 = 50.0   # width of every rectangle
a2 = 30.0   # height of every rectangle
b1 = 4.5   # horizontal gap
b2 = 4.5   # vertical gap

# ---------- NEW: calculated results ----------
R = S = W = ST = FOS = 0.0

MIN_SIZE = 0.2
TOL = 0.25

fig, ax = plt.subplots(figsize=(8, 8))
drag = None


# ---------- NEW: F.O.S calculation (from your PDF) ----------
def compute_fos():
    global R, S, W, ST, FOS
    total = (a1 + b1) * (a2 + b2)
    R = (total - a1 * a2) / total                  # extraction ratio
    S = (D * 9.81 * H) / (1 - R) / 1e6             # pillar stress, Pa -> MPa
    W = 4 * a1 * a2 / (2 * (a1 + a2))              # effective pillar width
    ST = 7.17 * W ** 0.46 / h ** 0.66              # pillar strength, MPa
    FOS = ST / S
    return FOS


def rect_origin(row, col):
    """Top-left corner of rectangle at (row, col)."""
    x = X0 + col * (a1 + b1)
    y = Y0 - row * (a2 + b2)
    return x, y


def draw():
    compute_fos()                                   # NEW: recalculate on every redraw
    ax.clear()
    ax.set_aspect("equal")
    ax.set_xlim(X0 - 50, X0 + 200)
    ax.set_ylim(Y0 - 100, Y0 + 50)
    ax.set_xlabel("meters")
    ax.set_ylabel("meters")
    ax.set_title("Drag right edges (a1), bottom edges (a2), or gap edges (b1, b2)")

    for r in range(2):
        for c in range(2):
            x, y = rect_origin(r, c)
            ax.add_patch(Rectangle((x, y - a2), a1, a2,
                                   facecolor="#fff200", edgecolor="black", lw=3))

    # a1 arrow
    ax.annotate("", xy=(X0 + a1, Y0 - 0.8), xytext=(X0, Y0 - 0.8),
                arrowprops=dict(arrowstyle="<->", lw=2))
    ax.text(X0 + a1 / 2, Y0 - 0.6, f"a1 = {a1:.2f} m", ha="center",
            va="bottom", fontweight="bold", color="navy")

    # a2 arrow
    ax.annotate("", xy=(X0 + 0.8, Y0 - a2), xytext=(X0 + 0.8, Y0),
                arrowprops=dict(arrowstyle="<->", lw=2))
    ax.text(X0 + 0.95, Y0 - a2 / 2, f"a2 = {a2:.2f} m", rotation=90,
            va="center", fontweight="bold", color="navy")

    # b1 arrow
    ax.annotate("", xy=(X0 + a1 + b1, Y0 + 0.4), xytext=(X0 + a1, Y0 + 0.4),
                arrowprops=dict(arrowstyle="<->", lw=2))
    ax.text(X0 + a1 + b1 / 2, Y0 + 0.6, f"b1 = {b1:.2f} m", ha="center",
            fontweight="bold")

    # b2 arrow
    ax.annotate("", xy=(X0 - 0.4, Y0 - a2 - b2), xytext=(X0 - 0.4, Y0 - a2),
                arrowprops=dict(arrowstyle="<->", lw=2))
    ax.text(X0 - 0.6, Y0 - a2 - b2 / 2, f"b2 = {b2:.2f} m", ha="right",
            va="center", fontweight="bold")

    # Point labels
    ax.text(X0 + a1, Y0 + 0.1, "R", fontsize=11)
    ax.text(X0 + 2 * a1 + b1, Y0 + 0.1, "Y", fontsize=11)
    ax.text(X0 - 0.5, Y0 - a2 - 0.1, "Q", fontsize=11)
    ax.text(X0 + a1 + 0.1, Y0 - a2 - 0.5, "P", fontsize=11, fontweight="bold")
    ax.text(X0 + a1 + b1 - 0.5, Y0 - a2 - 0.5, "X", fontsize=11)
    ax.text(X0 + 2 * a1 + b1, Y0 - a2 - 0.5, "A", fontsize=11, fontweight="bold")

    # Bottom-left: geometry + inputs
    ax.text(0.02, 0.02,
            f"start=({X0:.2f}, {Y0:.2f})  a1={a1:.2f}  a2={a2:.2f}  "
            f"b1={b1:.2f}  b2={b2:.2f}  (m)\n"
            f"D={D:.0f} kg/m³   H={H:.1f} m   h={h:.2f} m",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(facecolor="white", edgecolor="gray"))

    # NEW: top-right F.O.S box
    ax.text(0.98, 0.98,
            f"Factor of safety = {FOS:.2f}\n"
            f"Stress = {S:.2f} MPa\n"
            f"Strength = {ST:.2f} MPa\n"
            f"extraction ratio = {R:.3f}",
            transform=ax.transAxes, fontsize=12, fontweight="bold",
            ha="right", va="top",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round"))
    fig.canvas.draw_idle()


def find_edge(mx, my):
    for r in range(2):
        for c in range(2):
            x, y = rect_origin(r, c)
            top, bottom = y, y - a2
            left, right = x, x + a1
            in_y = bottom - TOL <= my <= top + TOL
            in_x = left - TOL <= mx <= right + TOL

            if in_y and abs(mx - right) < TOL:
                return ("a1", r, c)
            if in_x and abs(my - bottom) < TOL:
                return ("a2", r, c)
            if c == 1 and in_y and abs(mx - left) < TOL:
                return ("b1", r, c)
            if r == 1 and in_x and abs(my - top) < TOL:
                return ("b2", r, c)
    return None


def on_press(event):
    global drag
    if event.inaxes != ax or event.xdata is None:
        return
    drag = find_edge(event.xdata, event.ydata)


def on_motion(event):
    global a1, a2, b1, b2
    if drag is None or event.inaxes != ax or event.xdata is None:
        return

    mode, r, c = drag
    mx, my = event.xdata, event.ydata

    if mode == "a1":
        a1 = max(MIN_SIZE, (mx - X0 - c * b1) / (c + 1))
    elif mode == "a2":
        a2 = max(MIN_SIZE, (Y0 - my - r * b2) / (r + 1))
    elif mode == "b1":
        b1 = max(0.0, mx - X0 - a1)
    elif mode == "b2":
        b2 = max(0.0, Y0 - my - a2)

    draw()


def on_release(event):
    global drag
    if drag is not None:
        print(f"a1={a1:.3f}, a2={a2:.3f}, b1={b1:.3f}, b2={b2:.3f}, FOS={FOS:.3f}")
    drag = None


fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

draw()
plt.show()

print("Final values:", dict(a1=a1, a2=a2, b1=b1, b2=b2, D=D, H=H, h=h,
                            R=R, S=S, W=W, ST=ST, FOS=FOS))