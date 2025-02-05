'''
Given:
- 6 values (ax, ay, az, gx, gy, gz) denoting the current reading
- 6 values (ax, ay, az, gx, gy, gz) denoting the previous reading
- The time of the previous and current reading

plot the IMU's location
'''

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def track_position(accelerations, initial_velocity=[0, 0, 0], initial_position=[0, 0, 0], time_step=1):
    positions = [list(initial_position)]  # Store positions over time
    velocities = [list(initial_velocity)]  # Store velocities over time
    
    for i in range(1, len(accelerations)):
        ax, ay, az = accelerations[i]
        vx, vy, vz = velocities[-1]
        px, py, pz = positions[-1]
        
        # Update velocity using v = u + at
        new_vx = vx + ax * time_step
        new_vy = vy + ay * time_step
        new_vz = vz + az * time_step
        
        # Update position using s = ut + (1/2)at^2
        new_px = px + vx * time_step + 0.5 * ax * (time_step ** 2)
        new_py = py + vy * time_step + 0.5 * ay * (time_step ** 2)
        new_pz = pz + vz * time_step + 0.5 * az * (time_step ** 2)
        
        velocities.append([new_vx, new_vy, new_vz])
        positions.append([new_px, new_py, new_pz])
    
    return positions

# Example usage:
x_axis_movement = [
    [0, 0, 0],
    [1, 1, 1],
    [2, 2, 2],
    [3, 3, 3],
    [3, 3, 3]
]

positions = track_position(x_axis_movement)

# Extract x, y, z coordinates for plotting
x_vals = [pos[0] for pos in positions]
y_vals = [pos[1] for pos in positions]
z_vals = [pos[2] for pos in positions]

# Plot the trajectory in 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(x_vals, y_vals, z_vals, marker='o')
ax.set_xlabel('X Position')
ax.set_ylabel('Y Position')
ax.set_zlabel('Z Position')
ax.set_title('Object Trajectory in 3D Space')
plt.show()
