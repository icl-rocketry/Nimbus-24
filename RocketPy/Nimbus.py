# imports
from rocketpy import Environment, Rocket, Flight, CompareFlights
from Thanos import Thanos_R
import datetime

# Environment
env = Environment(latitude=39.4751, longitude=-8.3764, elevation=78)
envtime = datetime.date.today()
env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
env.set_atmospheric_model(type="Forecast", file="GFS")

# Rocket
# Nimbus includes payload and is used on the ascent
# NimbusEmpty has no payload and is used on the descent
# the individual payload is not simulated, that's for the guided recovery sim
Nimbus = Rocket(
    radius=0.097,
    mass=35.793,  # mass is excluding tanks and engine
    inertia=(58.1, 58.1, 0.231),
    power_off_drag="C:/Users/bgbg0/Desktop/ICLR/Nimbus-24/RocketPy/dragCurve.csv",
    power_on_drag="C:/Users/bgbg0/Desktop/ICLR/Nimbus-24/RocketPy/dragCurve.csv",
    center_of_mass_without_motor=4.28 - 2.3,
    coordinate_system_orientation="tail_to_nose",
)

NimbusDescent = Rocket(
    radius=0.097,
    mass=32.793,  # mass is excluding tanks and engine
    inertia=(42.2, 42.2, 0.222),
    power_off_drag="C:/Users/bgbg0/Desktop/ICLR/Nimbus-24/RocketPy/dragCurve.csv",
    power_on_drag="C:/Users/bgbg0/Desktop/ICLR/Nimbus-24/RocketPy/dragCurve.csv",
    center_of_mass_without_motor=4.28 - 2.24,
    coordinate_system_orientation="tail_to_nose",
)

Nimbus.add_motor(Thanos_R, position=0)

nose_cone = Nimbus.add_nose(length=0.35, kind="von karman", position=4.28)
nose_cone2 = NimbusDescent.add_nose(length=0.35, kind="von karman", position=4.28)

fins = Nimbus.add_trapezoidal_fins(
    n=3,
    root_chord=0.322,
    tip_chord=0.15,
    sweep_length=0.1,
    span=0.236,
    position=0.32,
    cant_angle=0,
    radius=0.076,
)

fins2 = NimbusDescent.add_trapezoidal_fins(
    n=3,
    root_chord=0.322,
    tip_chord=0.15,
    sweep_length=0.1,
    span=0.236,
    position=0.32,
    cant_angle=0,
    radius=0.076,
)

canards = Nimbus.add_trapezoidal_fins(
    n=3,
    root_chord=0.12,
    tip_chord=0.05,
    sweep_length=0.085,
    span=0.06,
    position=3.04,
    cant_angle=0,
    airfoil=("C:/Users/bgbg0/Desktop/ICLR/Nimbus-24/RocketPy/NACA0012.csv", "degrees"),
)

canards2 = NimbusDescent.add_trapezoidal_fins(
    n=3,
    root_chord=0.12,
    tip_chord=0.05,
    sweep_length=0.085,
    span=0.06,
    position=3.04,
    cant_angle=0,
    airfoil=("C:/Users/bgbg0/Desktop/ICLR/Nimbus-24/RocketPy/NACA0012.csv", "degrees"),
)

boattail = Nimbus.add_tail(top_radius=0.097, bottom_radius=0.076, length=0.322, position=0.322)
boattail2 = NimbusDescent.add_tail(top_radius=0.097, bottom_radius=0.076, length=0.322, position=0.322)

# rail buttons?

main = NimbusDescent.add_parachute(
    name="main",
    cd_s=16.073,
    trigger=450,  # ejection altitude in meters
    sampling_rate=100,
    lag=0,
)

# add reefing to main parachute with a drogue

# Flights
Ascent = Flight(rocket=Nimbus, environment=env, rail_length=10, inclination=85, heading=0, terminate_on_apogee=True, name="Ascent")
Descent = Flight(rocket=NimbusDescent, environment=env, rail_length=10, inclination=0, heading=0, initial_solution=Ascent, name="Descent")

# Results
comparison = CompareFlights([Ascent, Descent])
comparison.trajectories_3d(legend=True)