# RetroPath2.0 parameters for Carotene

Below are listed the RetroPath2.0 parameters in order to reproduce the
carotene results. See _"RetroPath2.0_tutorial"_ file for a step-by-step
guide.

## Parameters
* Input
    * Pathway length: 5
    * Source: path to _"carotene/source.csv"_ file (beta-carotene)
    * Sink: path to _"carotene/sink.csv"_ file (all _E. coli_ compounds)
    * Rules: path to _"carotene/rules.csv"_ file (see __Rules__ section)
* Output
    * Result folder: path to the desired output folder (should exists before execution)
* Result expected
    * The generated metabolic graph (_.json_ file in the result folder) can be visualized using the Scope Viewer.

## Rules
Rules have been selected according to references. Below enzymes, EC numbers and
associated MNXR IDs for each step:

* Enzyme: GGPP synthase
    * EC number(s): 2.5.1.29
    * MetaNetX reactions: MNXR55435

* Enzyme: phytoene synthase
    * EC number(s): 2.5.1.32
    * MetaNetX reactions: MNXR71200, MNXR70495, MNXR15602, MNXR8603, MNXR87812, MNXR67228

* Enzyme: phytoene desaturase
    * EC number(s): 1.3.99.31, 1.3.99.28
    * MetaNetX reactions: MNXR26357, MNXR26773, MNXR26774

* Enzyme: lycopene cyclase
    * EC number(s): 5.5.1.19
    * MetaNetX reactions: MNXR15454, MNXR16029, MNXR60336, MNXR17616, MNXR9555,

## References:
* PMID: 25403509
* MetaCyc pathway ID: PWY-7393
