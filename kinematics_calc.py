'''
Given:
- 3 values [ax, ay, az] denoting the current reading in (m/s^2)
- velocity of object at previous position [ux, uy, uz] in (m/s)
- The time between the previous and current reading in (s)

Return:
    - the displacement as [sx, sy, sz] in (m)
    - the final (current) velocity as [vx, vy, vz] in (m)
'''
def get_displacement_and_final_vel(current_accel, prev_vel, delta_time):
    # using s = ut + 1/2(a)(t^2)
    displacement_x = prev_vel[0]*delta_time + 0.5*(current_accel[0])*(delta_time**2)
    displacement_y = prev_vel[1]*delta_time + 0.5*(current_accel[1])*(delta_time**2)
    displacement_z = prev_vel[2]*delta_time + 0.5*(current_accel[2])*(delta_time**2)

    # using v = u + at
    final_vel_x = prev_vel[0] + current_accel[0]*delta_time
    final_vel_y = prev_vel[1] + current_accel[1]*delta_time
    final_vel_z = prev_vel[2] + current_accel[2]*delta_time

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
def get_current_position(current_accel, prev_vel, prev_position, delta_time):
    # get the displacement and final velocity
    displacement, final_velocity = get_displacement_and_final_vel(current_accel, prev_vel, delta_time)

    # get position
    current_pos_x = prev_position[0] + displacement[0]
    current_pos_y = prev_position[1] + displacement[1]
    current_pos_z = prev_position[2] + displacement[2]

    return list(current_pos_x, current_pos_y, current_pos_z), final_velocity
