var app = angular.module('myApp', []);

app.service('collapse', function () {
    document.querySelector("html").classList.add('js');

    var fileInput = document.querySelector(".input-file"),
        button = document.querySelector(".input-file-trigger"),
        the_return = document.querySelector(".input-file-trigger");

    button.addEventListener("keydown", function (event) {
        if (event.keyCode == 13 || event.keyCode == 32) {
            fileInput.focus();
        }
    });
    button.addEventListener("click", function (event) {
        fileInput.focus();
        return false;
    });
    fileInput.addEventListener("change", function (event) {
        var filename = (this.value).replace(/^.*[\\\/]/, '')
        if (filename != "") {

            //console.log(filename);
            the_return.innerHTML = filename;
        }
    });

    var treeData;

    this.drawTree = function (tree) {
        //console.log(tree);
        treeData = tree;
        constructRoot();
    }

    // Set the dimensions and margins of the diagram
    var margin = { top: 20, right: 90, bottom: 30, left: 90 },
        width = 790 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select("#tree").append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .call(d3.zoom().on("zoom", function () {
            svg.attr("transform", d3.event.transform)
        }))
        .append("g")
        .attr("transform", "translate("
            + margin.left + "," + margin.top + ")");

    // //checkbox activate Constant Propagation
    // d3.select("#checkCstFolding").on("change",activateCF);
    // //checkbox activate Constant Propagation
    // d3.select("#checkCstPropagation").on("change",activateCP);
    //checkbox activate Constant Propagation
    d3.select("#checkRedEta").on("change", activateRE);

    var i = 0,
        duration = 750,
        root;

    // declares a tree layout and assigns the size
    var treemap = d3.tree().size([height, width]);

    function constructRoot() {
        // Assigns parent, children, height, depth
        root = d3.hierarchy(treeData, function (d) { return d.children; });
        root.x0 = height / 2;
        root.y0 = 0;

        // Collapse
        root.children.forEach(collapse);

        update(root);
    }

    // Collapse specific the node and all it's children
    function collapse(d) {
        if (d.children && d.data.collapse == true) {
            d._children = d.children;
            d._children.forEach(collapse);
            d.children = null;
        }
        else if (d.children) {
            d.children.forEach(collapse);
        }
    }

    function update(source) {

        // Assigns the x and y position for the nodes
        var treeData = treemap(root);

        // Compute the new tree layout.
        var nodes = treeData.descendants(),
            links = treeData.descendants().slice(1);

        // Normalize for fixed-depth.
        nodes.forEach(function (d) { d.y = d.depth * 180 });

        // ****************** Nodes section ***************************

        // Update the nodes...
        var node = svg.selectAll('g.node')
            .data(nodes, function (d) { return d.id || (d.id = ++i); });

        // Enter any new modes at the parent's previous position.
        var nodeEnter = node.enter().append('g')
            .attr('class', 'node')
            .attr("transform", function (d) {
                return "translate(" + source.y0 + "," + source.x0 + ")";
            })
            .on('click', click);

        // Add Circle for the nodes
        nodeEnter.append('circle')
            .attr('class', 'node')
            .attr('r', 1e-6)
            .style("fill", function (d) {
                return d._children ? "lightsteelblue" : "#fff";
            });

        // Add labels for the nodes
        nodeEnter.append('text')
            .attr("style", "font-size:18px;font-weight:bold;")
            .attr("dy", "0.35em")
            .attr("x", function (d) {
                return d.children || d._children ? -13 : 13;
            })
            .attr("text-anchor", function (d) {
                return d.children || d._children ? "end" : "start";
            })
            .text(function (d) { return d.data.name; });

        // UPDATE
        var nodeUpdate = nodeEnter.merge(node);

        // Transition to the proper position for the node
        nodeUpdate.transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + d.y + "," + d.x + ")";
            });

        // Update the node attributes and style
        nodeUpdate.select('circle.node')
            .attr('r', 10)
            .style("fill", function (d) {
                return d._children ? "lightsteelblue" : "#fff";
            })
            .attr('cursor', 'pointer');


        // Remove any exiting nodes
        var nodeExit = node.exit().transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + source.y + "," + source.x + ")";
            })
            .remove();

        // On exit reduce the node circles size to 0
        nodeExit.select('circle')
            .attr('r', 1e-6);

        // On exit reduce the opacity of text labels
        nodeExit.select('text')
            .style('fill-opacity', 1e-6);

        // ****************** links section ***************************

        // Update the links...
        var link = svg.selectAll('path.link')
            .data(links, function (d) { return d.id; });

        // Enter any new links at the parent's previous position.
        var linkEnter = link.enter().insert('path', "g")
            .attr("class", "link")
            .attr('d', function (d) {
                var o = { x: source.x0, y: source.y0 }
                return diagonal(o, o)
            });

        // UPDATE
        var linkUpdate = linkEnter.merge(link);

        // Transition back to the parent element position
        linkUpdate.transition()
            .duration(duration)
            .attr('d', function (d) { return diagonal(d, d.parent) });

        // Remove any exiting links
        var linkExit = link.exit().transition()
            .duration(duration)
            .attr('d', function (d) {
                var o = { x: source.x, y: source.y }
                return diagonal(o, o)
            })
            .remove();

        // Store the old positions for transition.
        nodes.forEach(function (d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });

        // Creates a curved (diagonal) path from parent to the child nodes
        function diagonal(s, d) {

            path = `M ${s.y} ${s.x}
                C   ${(s.y + d.y) / 2} ${s.x},
                    ${(s.y + d.y) / 2} ${d.x},
                    ${d.y} ${d.x}`

            return path
        }

        // Toggle children on click.
        function click(d) {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d);
        }
    }

    // function activateCF(){
    //   if(d3.select("#checkCstFolding").property("checked")){
    //     console.log("habilitou CF");
    //   }else{
    //     console.log("desabilitou CF");
    //   }
    // }
    // function activateCP(){
    //   if(d3.select("#checkCstPropagation").property("checked")){
    //     console.log("habilitou CP");
    //   }else{
    //     console.log("desabilitou CP");
    //   }
    // }
    function activateRE() {
        if (d3.select("#checkRedEta").property("checked")) {
            console.log("habilitou RE");
        } else {
            console.log("desabilitou RE");
        }
    }
});

/* Diretiva definida para ler o arquivo passado em formato de texto */
app.directive('onReadFile', function ($parse) {
    return {
        restrict: 'A',
        scope: false,
        link: function ($scope, $element, $attrs) {
            var functionToBeCalled = $parse($attrs.onReadFile);
            $element.on('change', function (onChangeEvent) {
                var reader = new FileReader();
                reader.onload = function (onLoadEvent) {
                    $scope.$apply(function () {
                        functionToBeCalled($scope, { $fileContent: onLoadEvent.target.result });
                    });
                };
                reader.readAsText((onChangeEvent.srcElement || onChangeEvent.target).files[0]);
            });
        }
    };
});

app.controller('myCtrl', function ($scope, $http, collapse) {

    /**
     * Função chamada quando a página é criada de inicialização
     */
    $scope.init = function () {
        $scope.value = null;
        $scope.code = "";
        $scope.statusText = "";
        $scope.errorText = "";
        $scope.checkbox_eta = false;
        $scope.checkbox_fold = false;
        $scope.checkbox_memo = false;
        $scope.checkbox_prop = false;
    };

    /**
     * Função chamada para fazer uma requisição http para traduzir o código
     */
    $scope.translateCode = function () {
        $http({
            method: "POST",
            url: "/translateCode",
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                code: $scope.code,
                eta: $scope.checkbox_eta,
                fold: $scope.checkbox_fold,
                memo: $scope.checkbox_memo,
                prop: $scope.checkbox_prop
            },
        }).then(function mySuccess(response) {
            $scope.value = response.data.tree;
            $scope.statusText = "";
            $scope.errorText = "";
            collapse.drawTree($scope.value);
        }, function myError(response) {
            $scope.value = "";
            $scope.statusText = response.statusText;
            $scope.errorText = response.data;
        });
    };

    /**
     * Passa o conteúdo do arquivo para o campo de texto
     * @param $fileContent: conteúdo lido do arquivo
     */
    $scope.showContent = function ($fileContent) {
        $scope.code = $fileContent;
    };

});
