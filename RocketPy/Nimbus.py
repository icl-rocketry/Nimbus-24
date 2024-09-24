import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# imports
from rocketpy import Environment, Rocket, Flight, CompareFlights
from Thanos import Thanos_R
import datetime


# Rocket
# Nimbus includes payload and is used on the ascent
# NimbusEmpty has no payload and is used on the descent
# the individual payload is not simulated, that's for the guided recovery sim
Nimbus = Rocket(
    radius=0.097,
    mass=35.793,  # mass is excluding tanks and engine
    inertia=(58.1, 58.1, 0.231),
    power_off_drag="RocketPy/dragCurve.csv",
    power_on_drag="RocketPy/dragCurve.csv",
    center_of_mass_without_motor=4.28 - 2.3,
    coordinate_system_orientation="tail_to_nose",
)

NimbusDescent = Rocket(
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
nose_cone2 = NimbusDescent.add_nose(length=0.35, kind="von karman", position=4.28)

# fins = Nimbus.add_trapezoidal_fins(
#     n=3,
#     root_chord=0.322,
#     tip_chord=0.15,
#     sweep_length=0.1,
#     span=0.236,
#     position=0.32,
#     cant_angle=0,
#     radius=0.076,
# )

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

# fins2 = NimbusDescent.add_trapezoidal_fins(
#     n=3,
#     root_chord=0.322,
#     tip_chord=0.15,
#     sweep_length=0.1,
#     span=0.236,
#     position=0.32,
#     cant_angle=0,
#     radius=0.076,
# )

fins2 = NimbusDescent.add_trapezoidal_fins(
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

canards2 = NimbusDescent.add_trapezoidal_fins(
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
boattail2 = NimbusDescent.add_tail(top_radius=0.097, bottom_radius=0.076, length=0.302, position=0.302)

# rail buttons?
Nimbus.set_rail_buttons(
    upper_button_position = 2.92,
    lower_button_position = 0.36,
    angular_position = 60,
    )

def drogue_trigger(p, h, y):
    # activate drogue when vz < -10 m/s.
    return True if y[5] < -10 and h < 3000 else False

def main_trigger(p, h, y):
    # activate main when vz < 0 m/s and z < 800 m
    return True if y[5] < 0 and h < 450 else False

main = NimbusDescent.add_parachute(
    name="main",
    cd_s=29.128,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise = (0, 8.3, 0.5),
)

# add reefing to main parachute with a drogue
drogue = NimbusDescent.add_parachute(
    name="drogue",
    cd_s=0.3936,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=0,
    noise = (0, 8.3, 0.5),
)

# we only want to run this if we are running this file specifically as a nominal sim

if __name__ == "__main__":

    # Environment
    env = Environment(latitude=39.4751, longitude=-8.3764, elevation=0)
    envtime = datetime.date.today() + datetime.timedelta(days = 1)
    env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
    env.set_atmospheric_model(type="Forecast", file="GFS")

    # draw rocket
    Nimbus.draw()

    # Flights
    Ascent = Flight(rocket=Nimbus, environment=env, rail_length=12, inclination=86, heading=0, terminate_on_apogee=True, name="Ascent")
    Descent = Flight(rocket=NimbusDescent, environment=env, rail_length=12, inclination=0, heading=0, initial_solution=Ascent, name="Descent")

    # Results
    comparison = CompareFlights([Ascent, Descent])
    comparison.trajectories_3d(legend=True)

    print("----- ENV INFO -----")
    env.all_info()
    print("----- THANOS INFO -----")
    Thanos_R.all_info()
    print("----- Nimbus INFO -----")
    Nimbus.all_info()
    print("----- ASCENT INFO -----")
    Ascent.all_info()
    print("----- DESCENT INFO -----")
    Descent.info()