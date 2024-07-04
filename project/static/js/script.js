document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.materialboxed');
    M.Materialbox.init(elems);

    //carousel
    var elems = document.querySelectorAll('.carousel');
    M.Carousel.init(elems);

    var gameInput = document.getElementById('game_name');
    var autocompleteInstance = M.Autocomplete.init(gameInput, {
        data: {},
        onAutocomplete: function (selected) {
            gameInput.value = selected;
        }
    });
    // query to display suggested games
    gameInput.addEventListener('input', function () {
        var query = gameInput.value;
        if (query.length >= 2) {
            fetch('/suggest_games?query=' + query)
                .then(response => response.json())
                .then(data => {
                    var suggestions = {};
                    data.forEach(function (item) {
                        suggestions[item.name] = null;  // Materialize autocomplete expects { key: null } format
                    });
                    autocompleteInstance.updateData(suggestions);
                    autocompleteInstance.open();
                })
                .catch(error => console.error('Error fetching game suggestions:', error));
        }
    });


    var elems = document.querySelectorAll('.sidenav');
    M.Sidenav.init(elems, {
        edge: 'right' // Ustawienie bocznego menu po prawej stronie
    });

    // Modal for avatars
    var elems = document.querySelectorAll('.modal');
    M.Modal.init(elems);
    document.querySelectorAll('.avatar-option').forEach(function (img) {
        img.addEventListener('click', function () {
            // Remove the border from all other images
            document.querySelectorAll('.avatar-option').forEach(function (otherImg) {
                otherImg.style.border = '2px solid transparent';
            });

            // Add a border to the selected image
            img.style.border = '2px solid #000';

            // Get the selected avatar data attribute
            var selectedAvatar = img.getAttribute('data-avatar');

            // Set the value of the hidden field to the selected avatar
            document.getElementById('selected_avatar').value = selectedAvatar;

            // Debugging output
            console.log("Selected avatar:", selectedAvatar);
        });
    });

    

});
