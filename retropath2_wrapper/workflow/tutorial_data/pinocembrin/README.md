# RetroPath2.0 parameters for Pinocembrin

Below are listed the RetroPath2.0 parameters in order to reproduce the
pinocembrin results. See _"RetroPath2.0_tutorial"_ file for a step-by-step
guide.

## Case A
* Input
    * Pathway length: 4
    * Source: path to _"pinocembrin/source.csv"_ file (pinocembrin)
    * Sink: path to _"pinocembrin/sink_A.csv"_ file (phenylalanine)
    * Rules: path to _"pinocembrin/rules.csv"_ file (see __Rules__ section)
* Output
    * Result folder: path to the desired output folder (should exists before execution)
* Result expected
    * No scope found since side-products of some reactions are not in sink.

## Case B
* Input
    * Pathway length: 4
    * Source: path to _"pinocembrin/source.csv"_ file (pinocembrin)
    * Sink: path to _"pinocembrin/sink_B.csv"_ file (all _E. coli_ compounds)
    * Rules: path to _"pinocembrin/rules.csv"_ file
* Output
    * Result folder: path to the desired output folder (should exists before execution)
* Result expected
    * The generated metabolic graph (_.json_ file in the result folder) can be visualized using the Scope Viewer.

## Rules
Rules have been selected according references. Below enzymes, EC numbers and
associated MNXR IDs for each step:

* Enzyme: PAL
    * EC number(s): 4.3.1.24, 4.3.1.25
    * MetaNetX reactions: MNXR7145, MNXR93681

* Enzyme: 4CL
    * EC number(s): 6.2.1.12
    * MetaNetX reactions: MNXR1041, MNXR2251, MNXR227, MNXR14993, MNXR60189

* Enzyme: CHS
    * EC number(s): 2.3.1.74
    * MetaNetX reactions: MNXR84871, MNXR85701, MNXR85702, MNXR27480

* Enzyme: CHI
    * EC number(s): 5.5.1.6
    * MetaNetX reactions: MNXR60602, MNXR70709, MNXR73989, MNXR84948, MNXR85459, MNXR85703, MNXR76242

## References
* PMID: 25085569
