document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.materialboxed');
    M.Materialbox.init(elems);

    // Carousel
    var carouselElems = document.querySelectorAll('.carousel');
    M.Carousel.init(carouselElems);

    // Autocomplete for game input
    var gameInput = document.getElementById('game_name');
    var autocompleteInstance = M.Autocomplete.init(gameInput, {
        data: {},
        onAutocomplete: function (selected) {
            gameInput.value = selected;
        }
    });

    // Fetch suggestions for games
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

    // Sidenav
    var sidenavElems = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenavElems, {
        edge: 'right' // Ustawienie bocznego menu po prawej stronie
    });

    // Modal for avatars
    var modalElems = document.querySelectorAll('.modal');
    M.Modal.init(modalElems);
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

    // Add to favorites form submission
    document.querySelectorAll('.add-to-favorites-form').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('Form submitted'); // Debugging: Form submission event

            var gameIdInput = form.querySelector('input[name="game_id"]');
            var game_id = gameIdInput.value;
            console.log('Game ID:', game_id); // Debugging: Game ID value

            var csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfTokenMeta) {
                var csrfToken = csrfTokenMeta.getAttribute('content');
                console.log('CSRF Token:', csrfToken); // Debugging: CSRF token value

                fetch(addToFavoritesUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({ game_id: game_id })
                })
                .then(response => {
                    console.log('Response status:', response.status); // Debugging: Response status
                    return response.text().then(text => {
                        console.log('Response text:', text); // Debugging: Response text
                        return text;
                    });
                })
                .then(text => {
                    try {
                        const data = JSON.parse(text);
                        console.log('Response data:', data); // Debugging: Response data
                        if (data.error) {
                            console.error('Error:', data.error); // Debugging: Error message
                            alert('Error adding game to favorites: ' + data.error);
                        } else {
                            console.log('Success:', data.message); // Debugging: Success message
                            alert('Game added to favorites!');
                        }
                    } catch (error) {
                        console.error('Error parsing JSON:', error); // Debugging: JSON parsing error
                        alert('Error adding game to favorites: ' + error.message);
                    }
                })
                .catch(error => {
                    console.error('Fetch error:', error); // Debugging: Fetch error
                    alert('Error adding game to favorites: ' + error);
                });
            } else {
                console.error('CSRF token not found'); // Debugging: CSRF token not found
            }
        });
    });
});