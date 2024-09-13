# imports
from math import exp
from rocketpy import Fluid, LiquidMotor, CylindricalTank, MassFlowRateBasedTank

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir("..")

# Define fluids
ox_liq = Fluid(name="nitrous_l", density=1220)
ox_gas = Fluid(name="nitrous_g", density=1.977)
fuel_liq = Fluid(name="methanol_l", density=792)
fuel_gas = Fluid(name="methanol_g", density=1.206)
press_liq = Fluid(name="nitrogen_l", density=807)
press_gas = Fluid(name="nitrogen_g", density=1.251)

# Define tanks geometry
# TODO: use custom endcaps if the geometry is not a perfect sphere
ox_shape = CylindricalTank(radius = 0.085, height = 0.635, spherical_caps = False)
fuel_shape = CylindricalTank(radius = 0.085, height = 0.369, spherical_caps = False)
press_shape = CylindricalTank(radius = 0.057, height = 0.455, spherical_caps = True)

# Define tanks
ox_tank = MassFlowRateBasedTank(
    name="oxidizer tank",
    geometry=ox_shape,
    flux_time=5.5,
    initial_liquid_mass=7,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=lambda t: 7 / 5.5 - 1e-6,
    gas_mass_flow_rate_in=lambda t: (7 / 5.5) * 1.251 / 1220, # proportional to the remaining empty space in the tank
    gas_mass_flow_rate_out=0,
    liquid=ox_liq,
    gas=ox_gas,
)

fuel_tank = MassFlowRateBasedTank(
    name="fuel tank",
    geometry=fuel_shape,
    flux_time=5.5,
    initial_liquid_mass=4,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=lambda t: 4 / 5.5 - 1e-6,
    gas_mass_flow_rate_in=lambda t: (4 / 5.5) * 1.251 / 792, # proportional to the remaining empty space in the tank
    gas_mass_flow_rate_out=0,
    liquid=fuel_liq,
    gas=fuel_gas,
)

press_tank = MassFlowRateBasedTank(
    name="nitrogen tank",
    geometry=press_shape,
    flux_time=5.5,
    initial_liquid_mass=0.5,
    initial_gas_mass=0,
    liquid_mass_flow_rate_in=0,
    liquid_mass_flow_rate_out=lambda t: 0.5 / 5.5 - 1e-6,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0,
    liquid=press_liq,
    gas=press_gas,
)

# Define motor
# if the thrust curve is changed, define a specific impulse variable so we can calculate the mass flow rate of the propellants
Thanos_R = LiquidMotor(
    thrust_source="OpenRocket/ThanosR.eng",
    dry_mass=16.2, # mass of engine, not tanks!
    dry_inertia=(0.6050, 0.6094, 0.1004),
    nozzle_radius=0.025,
    center_of_dry_mass_position=1.0824,
    nozzle_position=0,
    burn_time=4.65,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)
Thanos_R.add_tank(tank=ox_tank, position=0.8926)
Thanos_R.add_tank(tank=fuel_tank, position=1.5789)
Thanos_R.add_tank(tank=press_tank, position=2.1745)