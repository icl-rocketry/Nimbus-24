import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# imports
from rocketpy import Environment, Rocket, Flight, CompareFlights
from Nimbus import Nimbus # import the ascent rocket
from Thanos import Thanos_R
import datetime

# Environment
env = Environment(latitude=39.4751, longitude=-8.3764, elevation=78)
envtime = datetime.date.today()
env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
env.set_atmospheric_model(type="Forecast", file="GFS")

# Rocket
# NimbusBallistic includes no payload and no chute deployment, used for the ballistic descent

NimbusBallistic = Rocket(
    radius=0.097,
    mass=32.793,  # mass is excluding tanks and engine
    inertia=(42.2, 42.2, 0.222),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=4.28 - 2.24,
    coordinate_system_orientation="tail_to_nose",
)

Nimbus.add_motor(Thanos_R, position=0)

nose_cone = Nimbus.add_nose(length=0.35, kind="von karman", position=4.28)
nose_cone2 = NimbusBallistic.add_nose(length=0.35, kind="von karman", position=4.28)

fins = Nimbus.add_trapezoidal_fins(
    n=3,
    root_chord=0.28,
    tip_chord=0.13,
    sweep_length=0.13,
    span=0.235,
    position=0.28,
    cant_angle=0,
    radius=0.076,
)


fins2 = NimbusBallistic.add_trapezoidal_fins(
    n=3,
    root_chord=0.28,
    tip_chord=0.13,
    sweep_length=0.13,
    span=0.235,
    position=0.28,
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
    airfoil=("RocketPy/NACA0012.csv", "degrees"),
)

canards2 = NimbusBallistic.add_trapezoidal_fins(
    n=3,
    root_chord=0.12,
    tip_chord=0.05,
    sweep_length=0.085,
    span=0.06,
    position=3.04,
    cant_angle=0,
    airfoil=("RocketPy/NACA0012.csv", "degrees"),
)

boattail = Nimbus.add_tail(top_radius=0.097, bottom_radius=0.076, length=0.302, position=0.302)
boattail2 = NimbusBallistic.add_tail(top_radius=0.097, bottom_radius=0.076, length=0.302, position=0.302)

# rail buttons?
# Nimbus.set_rail_buttons(
#     upper_button_position = 2.96,
#     lower_button_position = 0.36,
#     angular_position = 60,
#     )

# draw rocket
Nimbus.draw()

# Flights
Ascent = Flight(rocket=Nimbus, environment=env, rail_length=12, inclination=86, heading=0, terminate_on_apogee=True, name="Ascent")
Descent = Flight(rocket=NimbusBallistic, environment=env, rail_length=12, inclination=0, heading=0, initial_solution=Ascent, name="Descent")

# Results
comparison = CompareFlights([Ascent, Descent])
comparison.trajectories_3d(legend=True)

print("----- ASCENT INFO -----")
Ascent.all_info()
print("----- DESCENT INFO -----")
Descent.info()