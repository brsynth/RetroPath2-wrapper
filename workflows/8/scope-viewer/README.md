# scope-viewer -- Simple viewer for RetroPath suite results

The scope viewer provides a simple interface to consult metabolic graph
such as the scope graph outputted by RetroPath2.0 and RetroPath3.0.

RetroPath tools are retrosynthesis tools to build reaction networks
from a set of source compounds to a set of sink compounds. More details:

- RetroPath2.0 at [https://www.myexperiment.org/workflows/4987.html](https://www.myexperiment.org/workflows/4987.html)
- RetroPath3.0 at [https://github.com/brsynth/RetroPath3](https://github.com/brsynth/RetroPath3)

### Installation

Just download the complete repository.

### Usage

1. Open `scope_viewer.html` in your favorite web browser (e.g. Firefox, Safari, ..)
2. Load the scope network
    - load any `.json` scope file using the "Browse to JSON" input
    - example of scope file is provided in the `example` folder
3. Load the depiction of compounds (optional)
    - for better visualization experience, load `.svg` depiction of compounds
    using the "Browse to SVGs" input
    - example of `.svg` depictions are provided in the `example` folder
    - to load all depictions at once, browse to the folder containing `.svg`
    files, then select all files using [CTRL] + [A] or [CMD] + [A] keyboard
    shortcuts
    
### Notice

- In case the scope viewer become unresponsive -- which is possible when trying
to load a second scope file -- refresh the HTML page.

## Release

- 20190926: adding compatibility with RetroPath3.0 (optional chemical score)
- 20170524: first release for RetroPath2.0
