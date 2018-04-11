var app = angular.module('myApp', []);

/* Diretiva definida para ler o arquivo passado em formato de texto */
app.directive('onReadFile', function ($parse) {
    return {
        restrict: 'A',
        scope: false,
        link: function($scope, $element, $attrs) {
            var functionToBeCalled = $parse($attrs.onReadFile);
            $element.on('change', function(onChangeEvent) {
                var reader = new FileReader();
                reader.onload = function(onLoadEvent) {
                    $scope.$apply(function() {
                        functionToBeCalled($scope, {$fileContent:onLoadEvent.target.result});
                    });
                };
                reader.readAsText((onChangeEvent.srcElement || onChangeEvent.target).files[0]);
            });
        }
    };
});

app.controller('myCtrl', function($scope, $http) {

    /**
     * Função chamada quando a página é criada de inicialização
     */
    $scope.init = function() {
        $scope.value = null;
        $scope.code = "";
        $scope.statusText = "";
        $scope.errorText = "";
    };

    /**
     * Função chamada para fazer uma requisição http para traduzir o código
     */
    $scope.translateCode = function() {
        $http({
            method : "POST",
            url : "/translateCode",
            headers: {
               'Content-Type': 'application/json'
            },
            data: {
                code: $scope.code
            },
        }).then(function mySuccess(response) {
            $scope.value = response.data.tree;
            $scope.statusText = "";
            $scope.errorText = "";
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
    $scope.showContent = function($fileContent){
        $scope.code = $fileContent;
    };

});
