'''
Given:
- 3 values [ax, ay, az] denoting the current reading in (m/s^2)
- velocity of object at previous position [ux, uy, uz] in (m/s)
- The time between the previous and current reading in (s)

Return:
    - the displacement as [sx, sy, sz] in (m)
    - the final (current) velocity as [vx, vy, vz] in (m)
'''
def get_displacement_and_final_vel(current_accel, prev_vel, time):
    # using s = ut + 1/2(a)(t^2)
    displacement_x = prev_vel[0]*time + 0.5*(current_accel[0])*(time**2)
    displacement_y = prev_vel[1]*time + 0.5*(current_accel[1])*(time**2)
    displacement_z = prev_vel[2]*time + 0.5*(current_accel[2])*(time**2)

    # using v = u + at
    final_vel_x = prev_vel[0] + current_accel[0]*time
    final_vel_y = prev_vel[1] + current_accel[1]*time
    final_vel_z = prev_vel[2] + current_accel[2]*time

    return list(displacement_x, displacement_y, displacement_z), list(final_vel_x, final_vel_y, final_vel_z)

'''
Given:
- 3 values [ax, ay, az] denoting the current reading in (m/s^2)
- velocity of object at previous position [ux, uy, uz] in (m/s)
- position at the previous reading [d1x, d1y, d1z]
- The time between the previous and current reading in (s)

Return:
    - the current position [d2x, d2y, d2z]
    - the current velocity [vx, vy, vz]
'''
def get_current_position(current_accel, prev_vel, prev_position, time):
    # get the displacement and final velocity
    displacement, final_velocity = displacement_and_final_velocity(current_accel, prev_vel, time)

    # get position
    current_pos_x = prev_position[0] + displacement[0]
    current_pos_y = prev_position[1] + displacement[1]
    current_pos_z = prev_position[2] + displacement[2]

    return list(current_pos_x, current_pos_y, current_pos_z), final_velocity




import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# def track_position(accelerations, initial_velocity=[0, 0, 0], initial_position=[0, 0, 0], time_step=1):
#     positions = [list(initial_position)]  # Store positions over time
#     velocities = [list(initial_velocity)]  # Store velocities over time
    
#     for i in range(1, len(accelerations)):
#         ax, ay, az = accelerations[i]
#         vx, vy, vz = velocities[-1]
#         px, py, pz = positions[-1]
        
#         # Update velocity using v = u + at
#         new_vx = vx + ax * time_step
#         new_vy = vy + ay * time_step
#         new_vz = vz + az * time_step
        
#         # Update position using s = ut + (1/2)at^2
#         new_px = px + vx * time_step + 0.5 * ax * (time_step ** 2)
#         new_py = py + vy * time_step + 0.5 * ay * (time_step ** 2)
#         new_pz = pz + vz * time_step + 0.5 * az * (time_step ** 2)
        
#         velocities.append([new_vx, new_vy, new_vz])
#         positions.append([new_px, new_py, new_pz])
    
#     return positions

# Example usage:
# imu_accel = [
#     [0, 0, 0],
#     [1, 1, 1],
#     [2, 2, 2],
#     [3, 3, 3],
#     [3, 3, 3]
# ]

# imu_accel = []

# while ()


# displacement, final_velocity = displacement_and_final_velocity(imu_accel, 

# positions = track_position(x_axis_movement)

# # Extract x, y, z coordinates for plotting
# x_vals = [pos[0] for pos in positions]
# y_vals = [pos[1] for pos in positions]
# z_vals = [pos[2] for pos in positions]

# # Plot the trajectory in 3D
# matplotlib.use('TkAgg')
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(x_vals, y_vals, z_vals, marker='o')
# ax.set_xlabel('X Position')
# ax.set_ylabel('Y Position')
# ax.set_zlabel('Z Position')
# ax.set_title('Object Trajectory in 3D Space')
# plt.show()
