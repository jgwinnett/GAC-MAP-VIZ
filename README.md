# GAC-MAP-VIZ

GAC-MAP-VIZ is the supporting package to [GAC-MAP](https://gitlab.com/JGwinnett/GAC-MAP). It transforms the information gathered by GAC-MAP into visualizations, particularly 'Edge Bundling'.

This is in no way to be considered a finished product and will likely need some editing to fit your needs. Most of the code has hard-coded references to the specific outputs required by the project this was created for. You have been warned!


## Expected workflow

* Generate the initial data-set using GAC-MAP or other means.
* Use GAC_Graph_Builder or MIX_Source_Prep to standardize the data / combine it into a single object
* Generate Bar graphs via GAC_Bars
* Create the .json files needed for VEGA visualization






## Dependencies

pandas
numpy
ast
json
matplotlib
forex_python
Graph-Tool (deprecated)
