//@author: Thomas Duigou (thomas.duigou@inra.fr)
//@last update: 2017/04/13
//licence: Scope Viewer is licensed under the MIT License.
//To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

$(function(){

    putDefaultInfo();

    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        motionBlur: true
    });

    function LoadScope() {
        var reader = new FileReader();
        var file = document.getElementById("jsonFile").files[0];
        var filename = file.name;
        var basename = getBasename(filename);

        reader.readAsText(file);
        reader.onload = function (event)
        {
            var Scope = JSON.parse(event.target.result)['elements'];

            cy.json({elements: {}})
            cy.json({elements: Scope});

            updateTitle(basename);
            cy.minZoom(1e-50)
            LoadImages();
            MakeReactionLabels();
            MakeCompoundLabels();

            /*
            Color scheme:
                red: #B22222
                blue: #235789
                green: #68956D
                dark grey: #575757
                light grey: #E8E8E8
            */
            cy.style(
                cytoscape.stylesheet()
                    .selector('node[type = "reaction"]')
                        .css({
                            'content': 'data(ec)',
                            'text-opacity': 1,
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': '#575757',
                            'border-color': '#BFBFBF',
                            'border-style': 'solid',
                            'border-width': 4,
                            'background-color': 'white',
                            'shape': 'circle',
                            'width': 120,
                            'height': 100
                        })
                    .selector('node[type = "compound"]')
                        .css({
                            'content': 'data(cname)',
                            'text-opacity': 1,
                            'text-valign': 'bottom',
                            'text-halign': 'center',
                            'font-weight': 'bold',
                            'text-margin-y': 8,
                            'text-background-color': 'White',
                            'text-background-opacity': 0.85,
                            'text-background-shape': 'roundrectangle',
                            'shape': 'roundrectangle',
                            'width': 100,
                            'height': 100,
                            'border-width': 6
                        })
                    .selector('node[inSink = 0]')
                        .css({
                            'background-color': '#235789',
                            'border-color': '#235789'
                        })
                    .selector('node[inSink = 1]')
                        .css({
                            'background-color': '#68956D',
                            'border-color': '#68956D'
                        })
                    .selector('node[isSource = 1]')
                        .css({
                            'background-color': '#B22222',
                            'border-color': '#B22222'
                        })
                    .selector('node[img]')
                        .css({
                            'background-image': 'data(img)',
                            'background-fit': 'contain',
                            'background-size': '90%'
                        })
                    .selector('edge')
                        .css({
                            'width': 2,
                            'line-color': '#BFBFBF',
                            'curve-style': 'bezier',
                            'source-arrow-color': '#BFBFBF',
                            'source-arrow-shape': 'triangle',
                        })
                    .selector('.faded')
                        .css({
                            'opacity': 0.15,
                            'text-opacity': 0.25
                        })
            );

            cy.on('tap', 'node', function(e){

                var node = e.cyTarget;

                // Get neighborhood of node
                var neighborhood = node.neighborhood().add(node);
                if (node.is('[type = "compound"]'))
                {
                    //neighborhood = neighborhood.neighborhood().add(neighborhood);
                }
                cy.elements().addClass('faded');
                neighborhood.removeClass('faded');

                // Center view on node and its neighborhood
                if (! document.getElementById('disableAnimation').checked){
                    cy.animate(
                    {
                        fit: {eles: neighborhood},
                        center: {eles: neighborhood}
                    }, {
                        duration: 250
                    });
                }

                // Show compound info
                if (node.is('[type = "compound"]'))
                {
                    putCompoundInfo(node);
                }

                // Show transformation info
                if (node.is('[type = "reaction"]'))
                {
                    putTransformationInfo(node);
                }

            });

            cy.on('tap', function(e){
                if( e.cyTarget === cy ){
                    cy.elements().removeClass('faded');
                    putDefaultInfo();
                }
            });

            cy.on('layoutstop', function(e){
                cy.minZoom(cy.zoom());
                putDefaultInfo();
            });

            cy.layout({
                name: 'breadthfirst',
                directed: false,  // false in order to skip some weird layout
                circle: false,
                avoidOverlap: true,
                animate: false,
                roots: cy.elements("node[isSource = 1]")
            });

            //cy.layout({
                //name: 'cola',
                //fit: false,
                //edgeLength: 300,
                //infinite: true,
            //});

        };
    };

    function MakeReactionLabels()
    {
        var rnodes = cy.nodes().filter('[type = "reaction"]');
        for (var i = 0; i < rnodes.size() ; i++)
        {
            var rnode = rnodes[i];
            var all_ecs = rnode.data('EC number');
            var first_ec = all_ecs.sort()[0];
            var score_short = rnode.data('Score').toFixed(3);
            if (typeof rnode.data('ChemicalScore') !== 'undefined')  // Only with rp3
            {
                var chem_score_short = rnode.data('ChemicalScore').toFixed(3);
            }
            else
            {
                var chem_score_short = 'NA';
            }
            rnode.data('ec', first_ec);
            rnode.data('score_short', score_short);
            rnode.data('chem_score_short', chem_score_short);
        }
    }

    function MakeCompoundLabels()
    {
        var cnodes = cy.nodes().filter('[type = "compound"]');
        for (var i = 0; i < cnodes.size(); i++)
        {
            var cnode = cnodes[i];
            var allnames = cnode.data('Names');
            var cname = allnames[0];
            if ((typeof cname != 'undefined')
                && (cname != 'None')
                && (cname != ''))
            {
                if (cname.length > 12)
                {
                    shortname = cname.substr(0, 10)+'..';
                } else {
                    shortname = cname;
                }

            } else {
                shortname = '';
            }
            cnode.data('cname', shortname);
        }
    }

    function getScope(){
        if (typeof Scope !== 'undefined') {
            return Scope['elements']; // must be in the variable scope
        }else return '';
    };

    function LoadImages(){
        var files = document.getElementById("svgFiles").files;
        for (var i = 0; i < files.length ; i++)
        {
            LoadOneImage(files[i]);
        }
    }

    function LoadOneImage(file)
    {
        var filename = file.name;
        var basename = getBasename(filename);
        node = cy.elements('node[id="' + basename + '"]');
        //if (true)
        if (node.isNode())
        {
            var reader = new FileReader;
            reader.onload = function(e)
            {
                var content = e.target.result;
                var content64 = btoa(content);
                node = cy.elements('node[id="' + basename + '"]');
                node.data('img', 'data:image/svg+xml;charset=utf-8;base64,' + content64);
            }
            reader.readAsText(file, "UTF-8");
        }
    }

    function getBasename(filename)
    {
        return filename.replace(/^(.*[/\\])?/, '').replace(/(\.[^.]*)$/, '');
    }

    function updateTitle(newTitle)
    {
        document.getElementById('title').innerHTML = newTitle;
    }

    function putDefaultInfo()
    {
        var text = [];

        // Legend part
        text.push('<div class="info-title">');
        text.push('Legend');
        text.push('</div>');

        text.push('<div class="help-tip">');
        text.push('Click on a node to visualize information on it');
        text.push('</div>');

        text.push('<div class="info-subtitle">');
        text.push('Node shape');
        text.push('</div>');
        text.push('<div class="help-content">');
        text.push('<p><span class="symbol-compound">&#9634;</span> Compound</p>');
        text.push('<p><span class="symbol-transformation">&#9711;</span> Transformation (in/outgoing arrows show direction)</p>');
        text.push('</div>');

        text.push('<div class="info-subtitle">');
        text.push('Compound color');
        text.push('</div>');
        text.push('<div class="help-content">');
        text.push('<p><span class="symbol-compound symbol-source-color">&#9634;</span> Source</p>');
        text.push('<p><span class="symbol-compound symbol-inter-color">&#9634;</span> Intermediate</p>');
        text.push('<p><span class="symbol-compound symbol-sink-color">&#9634;</span> Sink</p>');
        text.push('</div>');

        // Loading data part
        text.push('<div class="info-title">');
        text.push('Loading data');
        text.push('</div>');

        // How to load data
        text.push('<div class="info-subtitle">');
        text.push('Loading scope');
        text.push('</div>');
        text.push('<div class="help-content">');

        text.push('<div class="load-data">');
        text.push('<span class="symbol-tick">&#8627;</span>');
        text.push('Load a .json file containing the source scope using the "Browse to JSON" input.');
        text.push('</div>');
        text.push('<div class="load-data">');
        text.push('<span class="symbol-tick">&#8627;</span>');
        text.push('Scope files are located in the output folder.');
        text.push('</div>');
        text.push('<div class="load-data">');
        text.push('<span class="symbol-tick">&#8627;</span>');
        text.push('The output folder path is set in the workflow ("Output configuration" metanode, "output dir path" input).');
        text.push('</div>');

        text.push('</div>');
        text.push('<div class="info-subtitle">');
        text.push('Loading depiction of compounds:');
        text.push('</div>');
        text.push('<div class="help-content">');
        text.push('<div class="load-data">');
        text.push('<span class="symbol-tick">&#8627;</span>');
        text.push('For better visualization experience, load .svg depiction of compounds using the "Browse to SVGs" input.');
        text.push('</div>')
        text.push('<div class="load-data">');
        text.push('<span class="symbol-tick">&#8627;</span>');
        text.push('To load all depictions at once, browse to the folder containing .svg files, then select all files using [CTRL]&nbsp;+&nbsp;[A] or [CMD]&nbsp;+&nbsp;[A] keyboard shortcuts.');
        text.push('</div>');
        text.push('<div class="load-data">');
        text.push('<span class="symbol-tick">&#8627;</span>');
        text.push('SVG files are located in the "svg" subfolder of the output folder.');
        text.push('</div>');
        text.push('</div>');

        // Add all info to html page
        $('#info').html(text.join('\n'));
    }

    function putCompoundInfo(node){

        var text = []

        // Get compound info
        var allnames = node.data('Names');
        var svg = node.data('img');
        var smiles = node.data('SMILES');
        var inchi = node.data('InChI');
        var inchikey = node.data('id');
        var inSink = node.data('inSink');

        // Info title
        text.push('<div class="info-title">');
        text.push('  Compound');
        text.push('</div>');

        // Compound name (and link if appropriate)
        text.push('<div class="info-name">');
        for (var i = 0; i < allnames.length; i++)
        {
            var aname = allnames[i]
            // Link to MNX database if appropriate
            if (aname.startsWith('MNXM'))
            {
                text.push('<a target="_blank" href="http://www.metanetx.org/cgi-bin/mnxweb/chem_info?chem=' + aname + '">' + aname + '</a>');
                text.push('<br>');
            } else {
                text.push(aname);
                text.push('<br>');
            }
        }
        text.push('</div>');

        // Spacer
        text.push('<div class="spacer">');
        text.push('</div>');

        // Compound depiction (if any)
        if (typeof svg != 'undefined')
        {
            text.push('<div class="img-box">');
            text.push('<div class="img">');
            text.push('</div>');
            text.push('</div>');
        }

        // Compound in sink?
        if (inSink == 0)
        {
            answer = 'No';
        } else {
            answer = 'Yes';
        }
        text.push('<div class="sink">');
        text.push('<div class="info-subtitle">');
        text.push('Compound in Sink? ');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(answer);
        text.push('</div>');
        text.push('</div>');

        // SMILES
        text.push('<div class="smiles">');
        text.push('<div class="info-subtitle">');
        text.push('SMILES: ');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(smiles);
        text.push('</div>');
        text.push('<div class="link raw-text">');
        text.push('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(smiles) + '">');
        text.push('Look for identical structure using PubChem');
        text.push('</a>');
        text.push('</div>');
        text.push('</div>');

        // InChI
        text.push('<div class="inchi">');
        text.push('<div class="info-subtitle">');
        text.push('InChI: ');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(inchi);
        text.push('</div>');
        text.push('<div class="link raw-text">');
        text.push('<a target="_blank" href="https://pubchem.ncbi.nlm.nih.gov/search/#collection=compounds&query_type=structure&query_subtype=identity&query=' + encodeURI(inchi) + '">');
        text.push('Look for identical structure using PubChem');
        text.push('</a>');
        text.push('</div>');
        text.push('</div>');

        // InChIKey
        text.push('<div class="inchikey">');
        text.push('<div class="info-subtitle">');
        text.push('InChIKey: ');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(inchikey);
        text.push('</div>');
        text.push('<div class="link raw-text">');
        text.push('<a target="_blank" href="http://www.google.com/search?q=' + encodeURI(inchikey) + '">');
        text.push('Look for identical structure using Google');
        text.push('</a>');
        text.push('</div>');
        text.push('</div>');

        // Add all info to html page
        $('#info').html(text.join('\n'));

        // Add depiction as background image
        $('#info > div.img-box > div.img').css('background-image', "url('" + svg + "')");

    }

    function putTransformationInfo(node){

        var text = [];

        // Get transformation info
        var trs_id = node.data('id');
        var rule_ids = node.data('Rule ID');
        var ec_numbers = node.data('EC number');
        var rsmiles = node.data('Reaction SMILES');
        var diameter = node.data('Diameter');
        var score = node.data('score_short');
        var chem_score = node.data('chem_score_short');
        var iteration = node.data('Iteration');

        // Info title
        text.push('<div class="info-title">');
        text.push('Transformation');
        text.push('</div>');

        // Transformation ID
        text.push('<div class="info-name">');
        text.push(trs_id);
        text.push('</div>');

        // Spacer
        text.push('<div class="spacer">');
        text.push('</div>');

        // Rule IDs (and links of appropriate)
        rule_ids = rule_ids.sort();
        text.push('<div class="trs-rule-ids">');
        text.push('<div class="info-subtitle">');
        text.push('Rule ID(s):');
        text.push('</div>');
        text.push('<div class="raw-text">');
        for (var i = 0; i < rule_ids.length; i++)
        {
            var arule_id = rule_ids[i];
            if (arule_id.startsWith('MNXR'))
            {
                var fields = arule_id.split('_');
                text.push('<a target="_blank" href="http://www.metanetx.org/cgi-bin/mnxweb/equa_info?equa=' + fields[0] + '">' + arule_id + '</a>');
                text.push('<br>');
            } else {
                text.push(arule_id);
                text.push('<br>');
            }

        }
        text.push('</div>');
        text.push('</div>');

        // Set EC numbers
        ec_numbers = ec_numbers.sort();
        text.push('<div class="ec-numbers">');
        text.push('<div class="info-subtitle">');
        text.push('EC number(s):');
        text.push('</div>');
        text.push('<div class="raw-text">');
        for (var i = 0; i < ec_numbers.length; i++)
        {
            text.push(ec_numbers[i] + '<br>');
        }
        text.push('</div>');
        text.push('</div>');

        text.push('<div class="two-cols">');
        // Set Diameter
        text.push('<div class="diameter">');
        text.push('<div class="info-subtitle">');
        text.push('Rule diameter:');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(diameter);
        text.push('</div>');
        text.push('</div>');
        // Set Iteration
        text.push('<div class="iteration">');
        text.push('<div class="info-subtitle">');
        text.push('Iteration: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(iteration);
        text.push('</div>');
        text.push('</div>');
        text.push('</div>');

        text.push('<div class="two-cols">');
        // Set biological score (standard)
        text.push('<div class="score">');
        text.push('<div class="info-subtitle">');
        text.push('Biological score:');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(score);
        text.push('</div>');
        text.push('</div>');
        // Set chemical score (optional)
        text.push('<div class="score">');
        text.push('<div class="info-subtitle">');
        text.push('Chemical score:');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(chem_score);
        text.push('</div>');
        text.push('</div>');
        text.push('</div>');

        // Set Reaction SMILES
        text.push('<div class="description">');
        text.push('<div class="info-subtitle">');
        text.push('Reaction SMILES:');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push(rsmiles);
        text.push('</div>');

        // Crosslink to Selenzyme
        text.push('<div class="selenzyme">');
        text.push('<div class="info-subtitle">');
        text.push('Enzyme selection:');
        text.push('</div>');
        text.push('<div class="raw-text">');
        text.push('<a target="_blank" href="http://selenzyme.synbiochem.co.uk/results?smarts=' + encodeURIComponent( rsmiles ) + '">' + 'Crosslink to Selenzyme' + '</a>');
        text.push('</div>');
        text.push('</div>');
        text.push('</div>');

        // Add all info to html page
        $('#info').html(text.join('\n'));

    }

    var jsonFile = document.getElementById('jsonFile');
    var folderPath = document.getElementById('svgFiles');

    jsonFile.addEventListener('change', LoadScope, false);
    svgFiles.addEventListener('change', LoadImages, false);

});
