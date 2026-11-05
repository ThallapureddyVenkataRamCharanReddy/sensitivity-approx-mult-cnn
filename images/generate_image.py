import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

fig, ax = plt.subplots(figsize=(15, 5.5), dpi=300)
ax.set_xlim(-0.5, 15.8)
ax.set_ylim(-1.5, 6.2)
ax.axis('off')

c_inp, c_conv, c_pool, c_gap, c_fc, c_edge = '#D4E6F1', '#FADBD8', '#FCF3CF', '#D5F5E3', '#E8DAEF', '#2C3E50'

def draw_cube(ax, x, y, w, h, depth, fc, ec=c_edge):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, lw=1.2, zorder=3))
    ax.add_patch(Polygon([[x, y+h], [x+depth*0.5, y+h+depth*0.5], [x+w+depth*0.5, y+h+depth*0.5], [x+w, y+h]],
                         facecolor=fc, edgecolor=ec, lw=1.2, alpha=0.85, zorder=3))
    ax.add_patch(Polygon([[x+w, y], [x+w+depth*0.5, y+depth*0.5], [x+w+depth*0.5, y+h+depth*0.5], [x+w, y+h]],
                         facecolor=fc, edgecolor=ec, lw=1.2, alpha=0.7, zorder=3))

# Draw blocks
draw_cube(ax, 0.2, 1.2, 0.15, 2.8, 0.1, c_inp)
ax.text(0.3, 0.6, "Input\n28×28×1", ha='center', va='top', fontweight='bold', color='#1B4F72')

ax.annotate("", xy=(1.5, 2.6), xytext=(0.8, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
draw_cube(ax, 1.6, 1.2, 0.5, 2.8, 0.6, c_conv)
ax.text(1.9, 0.6, "conv1\n(3×3, 16)\n28×28×16", ha='center', va='top', fontweight='bold', color='#922B21')

ax.annotate("", xy=(2.9, 2.6), xytext=(2.4, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
draw_cube(ax, 3.0, 1.9, 0.5, 1.4, 0.6, c_pool)
ax.text(3.3, 0.6, "pool1\n(MaxPool 2×2)\n14×14×16", ha='center', va='top', color='#7D6608')

ax.annotate("", xy=(4.3, 2.6), xytext=(3.8, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
draw_cube(ax, 4.4, 1.9, 0.9, 1.4, 0.6, c_conv)
ax.text(4.9, 0.6, "conv2\n(3×3, 32)\n14×14×32", ha='center', va='top', fontweight='bold', color='#922B21')

ax.annotate("", xy=(6.0, 2.6), xytext=(5.6, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
draw_cube(ax, 6.1, 2.25, 0.9, 0.7, 0.6, c_pool)
ax.text(6.6, 0.6, "pool2\n(MaxPool 2×2)\n7×7×32", ha='center', va='top', color='#7D6608')

ax.annotate("", xy=(7.7, 2.6), xytext=(7.3, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
draw_cube(ax, 7.8, 2.25, 1.5, 0.7, 0.6, c_conv)
ax.text(8.6, 0.6, "conv3\n(3×3, 64)\n7×7×64", ha='center', va='top', fontweight='bold', color='#922B21')

ax.annotate("", xy=(10.0, 2.6), xytext=(9.6, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
draw_cube(ax, 10.1, 2.25, 1.5, 0.7, 0.6, c_conv)
ax.text(10.9, 0.6, "conv4\n(3×3, 64)\n7×7×64", ha='center', va='top', fontweight='bold', color='#922B21')

ax.annotate("", xy=(12.3, 2.6), xytext=(11.9, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
draw_cube(ax, 12.4, 1.8, 1.5, 0.15, 0.2, c_gap)
ax.text(13.1, 0.6, "GAP\n(GlobalAvgPool)\n64-dim", ha='center', va='top', color='#0E6251')

ax.annotate("", xy=(14.2, 2.6), xytext=(13.8, 2.6), arrowprops=dict(arrowstyle="->", lw=1.5, color=c_edge))
ax.add_patch(Rectangle((14.3, 1.8), 0.35, 1.6, facecolor=c_fc, edgecolor=c_edge, lw=1.2))
ax.text(14.5, 0.6, "fc1\n(Dense 64)", ha='center', va='top', color='#512E5F')

ax.annotate("", xy=(15.0, 2.6), xytext=(14.75, 2.6), arrowprops=dict(arrowstyle="->", lw=1.2, color=c_edge))
ax.add_patch(Rectangle((15.1, 2.0), 0.25, 1.2, facecolor='#AED6F1', edgecolor='#1B4F72', lw=1.5))
ax.text(15.2, 0.6, "Output\n(10 classes)", ha='center', va='top', fontweight='bold', color='#154360')

# Domains
ax.add_patch(FancyBboxPatch((1.3, -0.4), 10.7, 5.8, boxstyle="round,pad=0.2", fc="none", ec="#C0392B", ls="--", lw=2))
ax.text(6.65, 5.5, "★ Approximate Multiplier (AxM) Domain — Conv Layers (>99.8% MACs) ★",
        ha='center', va='center', fontweight='bold', fontsize=11, color='#922B21',
        bbox=dict(facecolor='#FDEDEC', edgecolor='#C0392B', boxstyle='round,pad=0.4', lw=1.2))

ax.add_patch(FancyBboxPatch((12.1, -0.4), 3.4, 5.8, boxstyle="round,pad=0.2", fc="none", ec="#27AE60", ls=":", lw=1.8))
ax.text(13.8, 5.5, "Exact Floating-Point Domain",
        ha='center', va='center', fontweight='bold', fontsize=10, color='#196F3D',
        bbox=dict(facecolor='#E8F8F5', edgecolor='#27AE60', boxstyle='round,pad=0.4', lw=1))

plt.tight_layout()
plt.savefig("cnn_architecture_paper.png", dpi=300, bbox_inches='tight')
plt.savefig("cnn_architecture_paper.pdf", bbox_inches='tight')
print("Saved cnn_architecture_paper.png and cnn_architecture_paper.pdf")