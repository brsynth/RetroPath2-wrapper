# RetroPath2.0 parameters for Naringenin

Below are listed the RetroPath2.0 parameters in order to reproduce the
naringenin results. See _"RetroPath2.0_tutorial"_ file for a step-by-step
guide.

## Case A
* Input
    * Pathway length: 5
    * Source: path to _"naringenin/source.csv"_ file (naringenin)
    * Sink: path to _"naringenin/sink_A.csv"_ file (tyrosyne and phenylalanine compounds)
    * Rules: path to _"naringenin/rules.csv"_ file
* Output
    * Result folder: path to the desired output folder (should exists before execution)
* Result expected
    * No scope found since side-products of some reactions are not in sink.

## Case B
* Input
    * Pathway length: 5
    * Source: path to _"naringenin/source.csv"_ file (naringenin)
    * Sink: path to _"naringenin/sink_B.csv"_ file (all _E. coli_ compounds)
    * Rules: path to _"naringenin/rules.csv"_ file
* Output
    * Result folder: path to the desired output folder (should exists before execution)
* Result expected
    * The generated metabolic graph (_.json_ file in the result folder) can be visualized using the Scope Viewer.
