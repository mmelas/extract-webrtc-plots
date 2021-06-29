# KITE Result plotter script

The scirpt will extract the relevant results for our report and plot all the results. It relies on results generated with
the [KITE](https://github.com/webrtc/KITE) framework for automatically testing WebRTC applications.
The script will run through all the files in the results directory and parse all resulting files for the data which is required.
It will parse all folders that are in the form `run*` in the `RESULTDIR` folder (path is specified in the script), with each
folder being one iteration of the experiment. It will then average all the iterations, calculate the standard deviations
and use these for the plots it generates. Plots will be generated in the `PLOTSDIR` (also specified in the script, currently
`results-webcarm`).

The script can be run with

```bash
python3 plotter.py
```