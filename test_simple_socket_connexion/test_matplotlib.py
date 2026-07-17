import matplotlib.pyplot as plt
import numpy as np

# Apply a cool dark theme
plt.style.use('dark_background')

# our objects example
# Raspberry Pi Zero 2 W A : loc(x=0,y=400)
# Raspberry Pi Zero 2 W B : loc(x=400,y=400)
# Raspberry Pi Zero 2 W C : loc(x=0,y=0)
# Raspberry Pi Zero 2 W D : loc(x=400,y=0)
# Target Z : loc(x=200,y=200)(approximative and calculated)
# take all x values and put to a list 
# ex : x = [0,400,0,400,200]
# same for y : y = [400,400,0,0,200]  

x = []
y = []

x.extend([0,400,0,400,200]) #extend = append for more than 1 value
y.extend([400,400,0,0,200])

# Neon colors for a modern look
beacon_color = '#00d2ff' # Cyan
target_color = '#ff007f' # Neon Pink
arrow_color = '#ffb300'  # Yellow/Orange

colors = [beacon_color, beacon_color, beacon_color, beacon_color, target_color]
sizes = [150, 150, 150, 150, 300] # Bigger dots

# plot
fig, ax = plt.subplots(figsize=(8, 8)) # Make the graph perfectly square
fig.patch.set_facecolor('#12121c')    # Sleek dark background
ax.set_facecolor('#12121c')

# Add a subtle grid
ax.grid(True, color='#2a2a3c', linestyle='--', linewidth=0.5)

# Plot the points with a white outline so they pop
ax.scatter(x, y, s=sizes, c=colors, edgecolor='white', linewidth=1.5, zorder=3)

# Draw the arrow
ax.arrow(0, 400, 190, -190, head_width=15, head_length=15, 
         color=arrow_color, zorder=2, linewidth=2)

ax.set(xlim=(-100, 500), ylim=(-100, 500))

# Title
ax.set_title("Bluetooth Beacon Positioning System", color='white', fontsize=16, pad=20, fontweight='bold')

# Label the beacons (Centered nicely above/below the dots)
ax.text(0, 425, "Pi A", color=beacon_color, fontsize=12, ha='center', fontweight='bold')
ax.text(400, 425, "Pi B", color=beacon_color, fontsize=12, ha='center', fontweight='bold')
ax.text(0, -40, "Pi C", color=beacon_color, fontsize=12, ha='center', fontweight='bold')
ax.text(400, -40, "Pi D", color=beacon_color, fontsize=12, ha='center', fontweight='bold')

# Label the target
ax.text(200, 235, "Target Z", color=target_color, fontsize=14, fontweight="bold", ha='center')

# Label the arrow
ax.text(90, 310, "RSSI value", color=arrow_color, fontsize=12, rotation=-45, fontweight='bold', ha='center', va='center')

# Hide the borders for a cleaner look
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()
plt.show()