# RetroPath2.0 parameters for Violacein

Below are listed the RetroPath2.0 parameters in order to reproduce the
violacein results. See _"RetroPath2.0_tutorial"_ file for a step-by-step
guide.

## Context
The violacein pathway consists of five pathway genes culminating in the produc-
tion of violacein (and deoxyviolacein, due to promiscuity of the VioC enzyme,)
and several additional intermediate and side products proceeding through spon-
taneous or unknown aerobic reactions.

Violacein is produced through a 5-step enzymatic process followed by a single
non-enzymatic step.

## Parameters
* Input
    * Pathway length: 5
    * Source: path to _"violacein/source.csv"_ file (violacein and deoxyviolacein)
    * Sink: path to _"violacein/sink_A.csv"_ file (all _E. coli_ compounds)
    * Rules: path to _"violacein/rules.csv"_ file (see __Rules__ section)
* Output
    * Result folder: path to the desired output folder (should exists before execution)
* Result expected
    * The generated metabolic graph (_.json_ file in the result folder) can be visualized using the Scope Viewer.

## Rules
Rules have been selected according references. Below enzymes, EC numbers and
associated MNXR IDs for each step:

* Enzyme: VioA
    * EC number(s): 1.4.3.-
    * MetaNetX reactions: MNXR2613, MNXR76570

* Enzyme: VioB
    * EC number(s): 1.21.98.-
    * MetaNetX reactions: MNXR85789

* Enzyme: VioE
    * MetaNetX reactions: MNXR87814

* Enzyme: VioD
    * EC number(s): 1.14.13.217
    * MetaNetX reactions: MNXR62938

* Enzyme: VioC
    * EC number(s): 1.14.13.224
    * MetaNetX reactions: MNXR62939, MNXR62941

* Spontaneous
    * MetaNetX reactions: MNXR62940, MNXR62942, MNXR62943, MNXR62944

## References
* PMID: 26062452
* PMID: 21779844
* MetaCyc Pathway ID: PWY-7040
