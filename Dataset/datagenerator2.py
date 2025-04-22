import csv
import random
import math

# Parameters
num_deliveries = 10000
time_step = 0.05  # seconds
pitch_length = 20.12  # meters
initial_height = 1.0  # bowler release height
gravity = 9.81  # m/s^2

def simulate_delivery(speed_mps, bounce=False):
    positions = []
    t = 0.0
    x = 0.0
    z = initial_height
    v_x = speed_mps  # forward velocity
    v_z = 0.0        # start flat, gravity will pull it down

    while x < pitch_length:
        x = v_x * t
        z = initial_height - 0.5 * gravity * t**2
        y = random.uniform(-0.1, 0.1)  # slight lateral deviation
        if z < 0:
            z = 0
        positions.append((round(x, 2), round(y, 2), round(z, 2)))
        t += time_step
    return positions

# Generate deliveries
deliveries = []
max_columns = 0

for _ in range(num_deliveries):
    speed_kph = random.uniform(120, 150)
    speed_mps = speed_kph / 3.6
    trajectory = simulate_delivery(speed_mps)
    deliveries.append(trajectory)
    max_columns = max(max_columns, len(trajectory))

# Pad rows to same length
for i in range(len(deliveries)):
    while len(deliveries[i]) < max_columns:
        deliveries[i].append(("", "", ""))

# Save to CSV
with open("bowling_trajectories.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    header = [f"t{round(i*time_step, 2)}" for i in range(max_columns)]
    writer.writerow(header)
    for traj in deliveries:
        writer.writerow([f"({x},{y},{z})" if x != "" else "" for x, y, z in traj])

print("Dataset saved to 'bowling_trajectories.csv'")
