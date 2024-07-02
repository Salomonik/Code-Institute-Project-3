document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.materialboxed');
    M.Materialbox.init(elems);

    var elems = document.querySelectorAll('.carousel');
    M.Carousel.init(elems);

    var gameInput = document.getElementById('game_name');
    var autocompleteInstance = M.Autocomplete.init(gameInput, {
        data: {},
        onAutocomplete: function(selected) {
            gameInput.value = selected;
        }
    });

    gameInput.addEventListener('input', function() {
        var query = gameInput.value;
        if (query.length >= 2) {
            fetch('/suggest_games?query=' + query)
                .then(response => response.json())
                .then(data => {
                    var suggestions = {};
                    data.forEach(function(item) {
                        suggestions[item.name] = null;  // Materialize autocomplete expects { key: null } format
                    });
                    autocompleteInstance.updateData(suggestions);
                    autocompleteInstance.open();
                })
                .catch(error => console.error('Error fetching game suggestions:', error));
        }
    });
});
