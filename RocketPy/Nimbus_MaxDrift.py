import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# imports
from rocketpy import Environment, Rocket, Flight, CompareFlights
from Nimbus import Nimbus, NimbusDescent
from Thanos import Thanos_R
import datetime


# overwrite main to trigger at apogee
def main_trigger(p, h, y):
    # activate main when vz < 0 m/s (i.e. at apogee)
    return True if y[5] < 0 else False


main = NimbusDescent.add_parachute(
    name="main",
    cd_s=29.128,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise=(0, 8.3, 0.5),
)

# Environment
env = Environment(latitude=39.4751, longitude=-8.3764, elevation=78)
envtime = datetime.date.today()
env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
env.set_atmospheric_model(
    type="custom_atmosphere", wind_u=0, wind_v=8 # set positive wind_v for max drift
)  # for now ive set the max allowable wind as a constant 8 m/s, this can be changed to a altitude profile or another speed

# draw rocket
Nimbus.draw()

# Flights
Ascent = Flight(
    rocket=Nimbus, environment=env, rail_length=12, inclination=86, heading=0, terminate_on_apogee=True, name="Ascent"
)
Descent = Flight(
    rocket=NimbusDescent,
    environment=env,
    rail_length=12,
    inclination=0,
    heading=0,
    initial_solution=Ascent,
    name="Descent",
    max_time=1e4,  # the main at apogee overruns the default max of 600s
)

# Results
comparison = CompareFlights([Ascent, Descent])
comparison.trajectories_3d(legend=True)

print("----- ASCENT INFO -----")
Ascent.all_info()
print("----- DESCENT INFO -----")
Descent.info()
