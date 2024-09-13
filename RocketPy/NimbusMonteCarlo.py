# This script assigns uncertainties to rocket and environmental parameters and runs Monte Carlo sims accordingly
# Note: Script assumes all necessary files are in the current working directory

# import os
# os.chdir(os.path.dirname(os.path.realpath(__file__)))
# os.chdir("..")

# Import necessary modules
from rocketpy import Environment, Rocket, Flight, CompareFlights, MonteCarlo, GenericMotor
from rocketpy.stochastic import (
    StochasticEnvironment,
    StochasticRocket,
    StochasticFlight,
    StochasticNoseCone,
    StochasticTail,
    StochasticTrapezoidalFins,
)
from Thanos import Thanos_R
import datetime

# Initialising the (deterministic) simulation environment
env = Environment(latitude=39.4751, longitude=-8.3764, elevation=78)
envtime = datetime.date.today()
env.set_date((envtime.year, envtime.month, envtime.day, 12))  # UTC time
env.set_atmospheric_model(type="Ensemble", file="GEFS") # type argument is now "Ensemble" for Monte Carlo sims instead of "Forecast"

# Creating the 'stochastic environment' counterpart
stochastic_env = StochasticEnvironment(
    environment=env,
    ensemble_member=list(range(env.num_ensemble_members)),
)
# Reporting the attributes of the `StochasticEnvironment` object:
# stochastic_env.visualize_attributes()

# Two rocket objects are created for the two different configurations during ascent & descent phases
# NimbusAscent object includes the payload mass
# NimbusDescent object has no payload
# Note: The payload (and its deployment) is not simulated, there will be a separate guided recovery sim

# Creating the (deterministic) rocket objects and flights ----------------------------------------------------
NimbusAscent = Rocket(
    radius=0.097,
    mass=35.793,  # This mass value excludes tank and engine masses
    inertia=(58.1, 58.1, 0.231),
    power_off_drag="dragCurve.csv",
    power_on_drag="dragCurve.csv",
    center_of_mass_without_motor=4.28 - 2.3,
    coordinate_system_orientation="tail_to_nose",
)

NimbusDescent = Rocket(
    radius=0.097,
    mass=32.793,
    inertia=(42.2, 42.2, 0.222),
    power_off_drag="dragCurve.csv",
    power_on_drag="dragCurve.csv",
    center_of_mass_without_motor=4.28 - 2.24,
    coordinate_system_orientation="tail_to_nose",
)

# Adding motor only for ascent rocket
NimbusAscent.add_motor(Thanos_R, position=0)

# Creating nose cone objects for ascent and descent phases
nose_coneA = NimbusAscent.add_nose(length=0.35, kind="von karman", position=4.28)
nose_coneD = NimbusDescent.add_nose(length=0.35, kind="von karman", position=4.28)

# Creating fins for ascent and descent rockets
finsA = NimbusAscent.add_trapezoidal_fins(
    n=3,
    root_chord=0.28,
    tip_chord=0.13,
    sweep_length=0.13,
    span=0.225,
    position=0.32,
    cant_angle=0,
    radius=0.076,
    name="finsA",
)

finsD = NimbusDescent.add_trapezoidal_fins(
    n=3,
    root_chord=0.28,
    tip_chord=0.13,
    sweep_length=0.13,
    span=0.225,
    position=0.32,
    cant_angle=0,
    radius=0.076,
    name="finsD",
)

# Creating canards for ascent and descent rockets
canardsA = NimbusAscent.add_trapezoidal_fins(
    n=3,
    root_chord=0.12,
    tip_chord=0.05,
    sweep_length=0.085,
    span=0.06,
    position=3.04,
    cant_angle=0,
    airfoil=("NACA0012.csv", "degrees"),
    name="canardsA",
)

canardsD = NimbusDescent.add_trapezoidal_fins(
    n=3,
    root_chord=0.12,
    tip_chord=0.05,
    sweep_length=0.085,
    span=0.06,
    position=3.04,
    cant_angle=0,
    airfoil=("NACA0012.csv", "degrees"),
    name="canardsD",
)

# Creating boattails for ascent and descent rockets
boattailA = NimbusAscent.add_tail(top_radius=0.097, bottom_radius=0.076, length=0.302, position=0.302)
boattailD = NimbusDescent.add_tail(top_radius=0.097, bottom_radius=0.076, length=0.302, position=0.302)

# Setting rail buttons only for ascent rocket
NimbusAscent.set_rail_buttons(
    upper_button_position = 2.96,
    lower_button_position = 0.36,
    angular_position = 60,
    )

# Defining functions to trigger parachute deployments
def drogue_trigger(p, h, y):
    # activate drogue when vz < -10 m/s.
    return True if y[5] < -10 else False

def main_trigger(p, h, y):
    # activate main when vz < 0 m/s and z < 800 m
    return True if y[5] < 0 and h < 450 else False

# Adding main and drogue parachutes to the descent rocket (reefed chute in two configs)
main = NimbusDescent.add_parachute(
    name="main",
    cd_s=29.128,
    trigger=main_trigger,
    sampling_rate=100,
    lag=0,
    noise = (0, 8.3, 0.5),
)

drogue = NimbusDescent.add_parachute(
    name="drogue",
    cd_s=0.274,
    trigger=drogue_trigger,
    sampling_rate=100,
    lag=0,
    noise = (0, 8.3, 0.5),
)

# # draw rocket
# NimbusAscent.draw()

# Flights
Ascent = Flight(rocket=NimbusAscent, environment=env, rail_length=12, inclination=86, heading=0, terminate_on_apogee=True, name="Ascent")
Descent = Flight(rocket=NimbusDescent, environment=env, rail_length=12, inclination=0, heading=0, initial_solution=Ascent, name="Descent")

# Results
comparison = CompareFlights([Ascent, Descent])
comparison.trajectories_3d(legend=True)

# print("----- ASCENT INFO -----")
# Ascent.info()
# print("----- DESCENT INFO -----")
# Descent.info()

# MONTE CARLO SECTION OF SCRIPT ---------------------------------------------------------
# Note: The uncertainties assigned to the components in this script are arbitrary - will finalise later

# Creating the corresponding 'stochastic rocket' objects -------------------
stochastic_Ascent = StochasticRocket(
    rocket=NimbusAscent,
    radius=0.097 / 2000,
    mass=(35.793, 0.1, "normal"),
    inertia_11=(58.1, 0.01),
    inertia_22=0.01,
    inertia_33=0.01,
)
# Reporting the attributes of the `StochasticRocket` object:
# stochastic_Ascent.visualize_attributes()

stochastic_Descent = StochasticRocket(
    rocket=NimbusDescent,
    radius=0.097 / 2000,
    mass=(32.793, 0.1, "normal"),
    inertia_11=(42.2, 0.01),
    inertia_22=0.01,
    inertia_33=0.01,
)
# Reporting the attributes of the `StochasticRocket` object:
# stochastic_Ascent.visualize_attributes()

# Creating the 'stochastic aerosurface' objects for ascent
stochastic_nose_coneA = StochasticNoseCone(
    nosecone=nose_coneA,
    length=0.001,
)

stochastic_fin_setA = StochasticTrapezoidalFins(
    trapezoidal_fins=finsA,
    root_chord=0.0005,
    tip_chord=0.0005,
    span=0.0005,
)

stochastic_canardsA = StochasticTrapezoidalFins(
    trapezoidal_fins=canardsA,
    root_chord=0.0005,
    tip_chord=0.0005,
    span=0.0005,
)

stochastic_tailA = StochasticTail(
    tail=boattailA,
    top_radius=0.001,
    bottom_radius=0.001,
    length=0.001,
)

# Creating the 'stochastic aerosurface' objects for descent
stochastic_nose_coneD = StochasticNoseCone(
    nosecone=nose_coneD,
    length=0.001,
)

stochastic_fin_setD = StochasticTrapezoidalFins(
    trapezoidal_fins=finsD,
    root_chord=0.0005,
    tip_chord=0.0005,
    span=0.0005,
)

stochastic_canardsD = StochasticTrapezoidalFins(
    trapezoidal_fins=canardsD,
    root_chord=0.0005,
    tip_chord=0.0005,
    span=0.0005,
)

stochastic_tailD = StochasticTail(
    tail=boattailD,
    top_radius=0.001,
    bottom_radius=0.001,
    length=0.001,
)

# Converting Liquid Motor object to a GenericMotor to be compatible with 'Stochastic' objects
# Note: From the docs, apparently this object is less accurate than Liquid/SolidMotor (verify values)
GenericThanos_R = GenericMotor(
    thrust_source="ThanosR.eng",
    burn_time=5.5,
    chamber_radius=0.085,
    chamber_height=0.635 + 0.369,
    chamber_position=1,
    propellant_initial_mass=7+4,
    nozzle_radius=0.025,
    dry_mass=16.2,
    center_of_dry_mass_position=1.0824,
    dry_inertia=(0.6050, 0.6094, 0.1004),
    nozzle_position=0,
    reshape_thrust_curve=False,
    interpolation_method="linear",
    coordinate_system_orientation="nozzle_to_combustion_chamber",
    )

# Adding components to the 'stochastic rocket' objects
# Note: Bug in code (not sure if it's me or Rocketpy) doesn't allow multiple sets of fins to be added to stochastic rocket
#       The omission of canards for the ascent phase should lead to the landing ellipses being smaller than reality,
#       this is due to the destabilising effects of the canards in pitch & yaw not being included.
#       The omission of the canards for the descent phase should have negligible impact on the results,
#       this is due to the canards only developing small aerodynamic forces at low speeds (using parachutes)

# Ascent
stochastic_Ascent.add_motor(GenericThanos_R, position=0.001)
stochastic_Ascent.add_nose(stochastic_nose_coneA, position=(4.28, 0.001))
stochastic_Ascent.add_trapezoidal_fins(stochastic_fin_setA, position=0.32)
# stochastic_Ascent.add_trapezoidal_fins(stochastic_canardsA, position=3.04)
stochastic_Ascent.add_tail(stochastic_tailA)

# Descent
stochastic_Descent.add_nose(stochastic_nose_coneA, position=(4.28, 0.001))
stochastic_Descent.add_trapezoidal_fins(stochastic_fin_setD, position=0.32)
# stochastic_Descent.add_trapezoidal_fins(stochastic_canardsD, position=3.04)
stochastic_Descent.add_tail(stochastic_tailD)
stochastic_Descent.add_parachute(main)
stochastic_Descent.add_parachute(drogue)

# Monte Carlo Flights -----------------------------------------------------------

# Ascent flight
stochastic_flightAscent = StochasticFlight(
    flight=Ascent,
    inclination=(86, 1),  # mean = 86, std = 1
    heading=(0, 2),  # mean = 0, std = 2
)

# Extract the final state at the last timestep from the Ascent flight object
t_final = Ascent.apogee_time
final_state_vectorA = Ascent.get_solution_at_time(t_final)

# Print the final ascent state vector for verification
print("Final State Vector (Initial Solution):", final_state_vectorA)

# Defining another descent flight since 'StochasticFlight' object has to be initialised with a tuple/list and not a 'Flight' object as before
Descent2 = Flight(rocket=NimbusDescent, environment=env, rail_length=12, inclination=0, heading=0, initial_solution=final_state_vectorA, name="Descent2")

# Descent flight
stochastic_flightDescent = StochasticFlight(
    flight=Descent2,                       # Pass the existing flight object
    inclination=0,                         # Define inclination or randomize it
    heading=0,                             # Define heading or randomize it
    initial_solution=final_state_vectorA,  # Use the extracted final ascent state vector
)

# Initialising Monte Carlo objects for the sims
numberOfSims = 10 # Setting the number of Monte Carlo sims to run

# Data for ascent phase
test_dispersionAscent = MonteCarlo(
    filename="ascent",
    environment=stochastic_env,
    rocket=stochastic_Ascent,
    flight=stochastic_flightAscent,
)

# Running the Monte Carlo simulations for the ascent phase
# Note: The result of this call should be multiple ascent flights with ballistic descents and no payload deployment
test_dispersionAscent.simulate(number_of_simulations=numberOfSims, append=False)


# Data for descent phase
test_dispersionDescent = MonteCarlo(
    filename="descent",
    environment=stochastic_env,
    rocket=stochastic_Descent,
    flight=stochastic_flightDescent,
)

# Running the Monte Carlo simulations for the descent phase
# Note: The result of this call should be multiple descent flights, all initialised using the 'nominal' ascent flight (and payload has been deployed)
test_dispersionDescent.simulate(number_of_simulations=numberOfSims, append=False)

# Plotting the simulated apogee and landing zones
test_dispersionAscent.plots.ellipses(xlim=(-1500, 1500), ylim=(-1000, 2500))
test_dispersionDescent.plots.ellipses(xlim=(-1500, 1500), ylim=(-1000, 2500))