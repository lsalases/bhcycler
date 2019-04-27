# bhcycler
Cycler to submit jobs iteratively on BlueHive (with OpenMM templates).

The cycler consists of 2 bash scripts (cycle and cycler.sh) + a python
template file (PREFIX.py) that work together to run an iteration or
cycle of a simulation. Below is a quick description of each of these
files:

1. cycle: the "laucher", this is where all the SLURM-related options
   	  are defined (partition, number of nodes, time
   	  allocation,...).  This script also calls the driver (see
   	  below) to submit the job for the current iteration. For this
   	  reason, it is important to make sure that the variable
   	  'DRIVER' is pointing to where the driver file (cycler.sh)
   	  actually is.

2. cycler.sh: the "driver", this script 1) checks that the previous
   	      iteration was completed correctly, 2) starts the current
   	      work (runs the template script, see below) and 3)
   	      submits a dependent job for the next iteration that will start
	      once the current job is completed.

3. PREFIX.py: the "template", this is where all the OpenMM-related
   	   options are defined. I've included a sample template, so in
   	   this case PREFIX = npt, but it can be anything, really, and
   	   the template file can be modified as needed, depending on
   	   the system that needs to be run. The important thing to
   	   note is that the PREFIX of the job and the current
   	   iteration number are taken from the command line.



a) How to submit jobs

Using the cycler is rather simple. If the three files described above
are in the same directory (along with the input files that are
required for the simulation, e.g. PSF, parameters,...), then just
type:

     ./cycle PREFIX-#iteration

where PREFIX needs to be replaced by the name of the template script
and #iteration by the current iteration number. For example,

     ./cycle npt-10

will run the 10th iteration of the simulation indicated by npt.py.

Whenever you start the cycler, two jobs will appear in the queue. The
one that says '(Dependency)' in the NODELIST column will start the next
iteration once the current job is done. The other job corresponds to the
current iteration.

Note that the cycler does not really handle a "0th" iteration, since
the energy minimization/equilibration phases of a simulation can be
carried out in many different ways and it would be hard to accomodate
all. Instead, the cycler is intended for systems that already have at
least a little bit of production and it requires you to already have a
restart or a checkpoint file from where to continue the simulation
(see below). These files should be named PREFIX_previous.xml or
PREFIX_previous.chk, where previous corresponds to the iteration number
previous to the one you want to run. For example, if you want to start
the cycler in the 2nd iteration using the npt.py template, then
npt_1.xml or npt_1.chk should already exist. Then, you can run the
cycler as,

     ./cycle npt-2

If multiple simulations need be run using the same cyler, it might be
useful to alias it in your ~/.bash profile. To do so, just open
~/.bash_profile in a text editor and add the following line,

     alias cycle='/path-to-cycle/cycle'

Then, the shell will be able to find the cycler even if it's not
present in the working directory of the simulation. In that case, the
cycler can be run like this,

     cycle PREFIX-#iteration

Do not forget to change the path to the driver accordingly in the
script of the laucher.



b) How to stop jobs

If you need to stop a job the first thing you need to do is to cd
into the directory of the corresponding simulation (where you first
lauched the job).

Then, type in the terminal,

     echo "halt" > halt

this command will create a text file called 'halt'. In the next
iteration, the cycler will identify this file when checking for errors
in the previous iteration and the presence of this file will prevent
a new iteration from being launched.

After doing this, go ahead and cancel the jobs that need to be
cancelled like you normally would,

     scancel jobid



c) XML files vs. checkpoint files

Right now, the cycler can use checkpoint files or XML files to restart
the simulations. To use one or the other just comment or comment out
lines 72 and 73 of npt.py as needed.

Note that, even if it might seem easier, using checkpoint files might
not always be the best choice because they are not platform
independent. This means that if you first run a simulation in the CUDA
platform (with GPUs) and then try to restart it in a different
platform (e.g. CPU, OpenCL, Reference), you will get an error and your
simulation will probably not run. This might also happen if you try
using a different computer architecture or even a different version of
OpenMM.

So, I think that the wiser choice is to use XML files whenever
possible, since they are way more portable. The only problem I see
with using XML files is that there is not a built-in reporter for them
in OpenMM. This means that there is not a direct way (that I know) to
generate an XML file every n simulation steps. Alan came up with a way
to go around this issue and I have implemented it and tested it in the
cycler, so it should be functional now. Just make sure to set the
variable nsteps as a multiple of report_interval in PREFIX.py.

Based on these limitations, I am choosing to leave both as an option for now: As
long as the simulation is run with the same version of OpenMM and in
the same architecture, the checkpoint files should work just
fine. However, it is still preferable to have platform independent restart
files, just in case they are needed in the future. So, the lines for checkpoint files
are commented out.



d) Final thoughts

Please note that this cycler is quite simple and that, even if I
tested it, there might be some behavior(s) that I didn't accont
for. So, I would recommend to keep checking on the simulations,
especially at the beginning, to make sure that the cycler is stable.
