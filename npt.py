#! /usr/bin/env python

'''
npt.py

   Equilibrate a membrane system in the NPT ensemble.
   Note that this is a sample script. Modify as needed.

'''

# Import OpenMM libraries
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from sys import stdout, exit, stderr

# Output parameters
prefix = sys.argv[1]
iteration = sys.argv[2]
previous = str(int(sys.argv[2]) - 1)
nsteps = 10000000 # 20 ns
report_interval = 50000 # 100 ps; must be a multiple of nsteps

# Input files
psf = CharmmPsfFile('model.psf')

# Force field parameters
forcefield = CharmmParameterSet('parameters/top_all36_prot.rtf', 
                                'parameters/top_all36_na.rtf',
                                'parameters/top_all36_carb.rtf',
                                'parameters/top_all36_lipid.rtf',
                                'parameters/top_all36_cgenff.rtf',
                                'parameters/par_all36m_prot.prm',
                                'parameters/par_all36_na.prm',
                                'parameters/par_all36_carb.prm',
                                'parameters/par_all36_lipid.prm', 
                                'parameters/par_all36_cgenff.prm',
                                'parameters/toppar_water_ions.str',
                                'parameters/stream/lipid/toppar_all36_lipid_cholesterol.str')

# Define the dimesions of the simulation box (need this to create a periodic system)
psf.setBox(55.8*angstroms, 55.8*angstroms, 88.0*angstroms) 

# Set up the system
system = psf.createSystem(forcefield, nonbondedMethod=PME,
                          nonbondedCutoff=10*angstroms,
                          switchDistance=9*angstroms,
                          constraints=HBonds,
                          rigidWater=True,
                          ewaldErrorTolerance=0.0005,
                          removeCMMotion=True)

# Set up a barostat
system.addForce(MonteCarloMembraneBarostat(1*bar, 0*bar*nanometer, 310.15*kelvin,
                                           MonteCarloMembraneBarostat.XYIsotropic,
                                           MonteCarloMembraneBarostat.ZFree))

# Define an integrator
integrator = LangevinIntegrator(310.15*kelvin, 1/picosecond, 0.002*picoseconds)
integrator.setConstraintTolerance(0.00001)

# Define platform
platform = Platform.getPlatformByName('CUDA')
properties = dict(CudaPrecision='mixed')

# Set up the simulation
simulation = Simulation(psf.topology, system, integrator, platform, properties) 

# Set up the positions of every atom in the system (commented out after first iteration)
#simulation.context.setPositions(pdb.positions)

# Load the last check point
simulation.loadState(prefix + '_' + previous + '.xml')
#simulation.loadCheckpoint(prefix + '_' + previous + '.chk')

# Get rid of atomic clashes and bad contacts (commented out after first iteration)
#simulation.minimizeEnergy()

# Set up the outputs of the simulation
#simulation.reporters.append(CheckpointReporter(prefix + '_' + iteration + '.chk', report_interval))
simulation.reporters.append(DCDReporter(prefix + '_' + iteration + '.dcd', report_interval,
                                               enforcePeriodicBox=True))
simulation.reporters.append(StateDataReporter(prefix + '_' + iteration + '.log', report_interval,
                                              step=True, potentialEnergy=True, temperature=True,
                                              volume=True, separator='\t'))

# Run the simulation and save its state every report_interval steps
ncycles = int(nsteps / report_interval)
for i in range(ncycles):
    simulation.step(report_interval)
    simulation.saveState(prefix + '_' + iteration + '.xml')
