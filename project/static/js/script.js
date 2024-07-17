document.addEventListener('DOMContentLoaded', function () {
    // Initialize modals for avatars
    var modalElems = document.querySelectorAll('.modal');
    M.Modal.init(modalElems);

    // Handle avatar selection
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

    // Initialize carousel
    var carouselElems = document.querySelectorAll('.carousel');
    M.Carousel.init(carouselElems);

    // Initialize materialboxed images
    var elems = document.querySelectorAll('.materialboxed');
    M.Materialbox.init(elems, {
        onOpenStart: function() {
            // When the modal opens, set z-index for other elements
            document.querySelectorAll('.carousel').forEach(function(carousel) {
                carousel.style.zIndex = '1030';
            });
        },
        onCloseEnd: function() {
            // When the modal closes, reset z-index
            document.querySelectorAll('.carousel').forEach(function(carousel) {
                carousel.style.zIndex = '';
            });
        }
    });

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

    // Initialize sidenav
    var sidenavElems = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenavElems, {
        edge: 'right' // Set sidenav on the right side
    });

    // Handle add to favorites form submission
    document.querySelectorAll('.add-to-favorites-form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            console.log('Form submitted'); // Debugging: Form submission event

            var gameIdInput = form.querySelector('input[name="game_id"]');
            var game_id = gameIdInput.value;
            console.log('Game ID:', game_id); // Debugging: Game ID value

            var csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfTokenMeta) {
                var csrfToken = csrfTokenMeta.getAttribute('content');
                console.log('CSRF Token:', csrfToken); // Debugging: CSRF token value

                fetch(toggleFavoriteUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({ game_id: game_id })
                })
                    .then(response => {
                        console.log('Response status:', response.status); // Debugging: Response status
                        return response.json();
                    })
                    .then(data => {
                        console.log('Response data:', data); // Debugging: Response data
                        if (data.error) {
                            console.error('Error:', data.error); // Debugging: Error message
                            alert('Error toggling favorite: ' + data.error);
                        } else {
                            console.log('Success:', data.message); // Debugging: Success message
                            var icon = form.querySelector('.material-icons');
                            if (data.action === 'added') {
                                icon.textContent = 'favorite';
                                icon.style.color = 'red';
                            } else if (data.action === 'removed') {
                                icon.textContent = 'favorite_border';
                                icon.style.color = '';
                            }
                            displayFlashMessage(data.message, data.category);
                        }
                    })
                    .catch(error => {
                        console.error('Fetch error:', error); // Debugging: Fetch error
                        alert('Error toggling favorite: ' + error);
                    });
            } else {
                console.error('CSRF token not found'); // Debugging: CSRF token not found
            }
        });
    });

    // Function to hide flash messages after a certain time
    function hideFlashMessage(message) {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 3000); 
    }

    // Function to hide existing flash messages
    function hideFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(hideFlashMessage);
    }

    // Function to display a flash message
    function displayFlashMessage(message, category) {
        console.log('Displaying flash message:', message, category); // Debugging
        const flashMessagesDiv = document.getElementById('flash-messages');
        if (!flashMessagesDiv) {
            console.error('Flash messages container not found'); // Debugging
            return;
        }
        console.log('Flash messages container found:', flashMessagesDiv); // Debugging
        const flashMessageDiv = document.createElement('div');
        flashMessageDiv.className = `flash-message ${category}`;
        flashMessageDiv.textContent = message;
        flashMessagesDiv.appendChild(flashMessageDiv);
        console.log('Flash message added to container:', flashMessageDiv); // Debugging

        hideFlashMessage(flashMessageDiv);
    }

    // Function to handle AJAX response
    function handleResponse(response) {
        console.log('Handling response:', response); // Debugging
        response.json().then(data => {
            console.log('Server response JSON:', data); // Debugging
            if (data.message) {
                displayFlashMessage(data.message, data.category || 'info');
            } else if (data.error) {
                displayFlashMessage(data.error, data.category || 'error');
            }
        }).catch(error => console.error('Error parsing JSON:', error));
    }

    // Function to handle form submission for adding/removing favorites
    function handleFormSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const gameId = form.querySelector('input[name="game_id"]').value;
        const csrfToken = form.querySelector('input[name="csrf_token"]').value;

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ game_id: gameId })
        })
        .then(response => {
            console.log('Response status:', response.status); // Debugging
            handleResponse(response);
        })
        .catch(error => console.error('Error:', error));
    }

    // Attach event listeners to forms
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.add-to-favorites-form').forEach(form => {
            form.addEventListener('submit', handleFormSubmit);
        });
    });

    // Run the function to hide existing flash messages after the page loads
    window.onload = hideFlashMessages;

    // Handle edit comment button click
    document.querySelectorAll('.edit-comment-btn').forEach(button => {
        console.log("Adding event listener to edit button", button); // Debugging
        button.addEventListener('click', event => {
            const commentId = event.target.dataset.commentId;
            console.log("Edit button clicked for comment ID:", commentId); // Debugging
            const commentContent = document.getElementById(`comment-content-${commentId}`);
            const editCommentForm = document.getElementById(`edit-comment-form-${commentId}`);
            if (commentContent && editCommentForm) {
                commentContent.style.display = 'none';
                editCommentForm.style.display = 'block';
            } else {
                console.error(`Element with ID comment-content-${commentId} or edit-comment-form-${commentId} not found.`);
            }
        });
    });

    // Handle cancel edit comment button click
    document.querySelectorAll('.cancel-edit-btn').forEach(button => {
        console.log("Adding event listener to cancel button", button); // Debugging
        button.addEventListener('click', event => {
            const commentId = event.target.dataset.commentId;
            console.log("Cancel button clicked for comment ID:", commentId); // Debugging
            const commentContent = document.getElementById(`comment-content-${commentId}`);
            const editCommentForm = document.getElementById(`edit-comment-form-${commentId}`);
            if (commentContent && editCommentForm) {
                commentContent.style.display = 'block';
                editCommentForm.style.display = 'none';
            } else {
                console.error(`Element with ID comment-content-${commentId} or edit-comment-form-${commentId} not found.`);
            }
        });
    });

    // Handle save comment button click
    document.querySelectorAll('.save-comment-btn').forEach(button => {
        button.addEventListener('click', event => {
            const commentId = event.target.dataset.commentId;
            const content = document.getElementById(`edit-comment-content-${commentId}`).value;
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            fetch(`/update_comment/${commentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ content: content })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    const commentContent = document.getElementById(`comment-content-${commentId}`);
                    const editCommentForm = document.getElementById(`edit-comment-form-${commentId}`);
                    if (commentContent && editCommentForm) {
                        commentContent.textContent = data.content;
                        commentContent.style.display = 'block';
                        editCommentForm.style.display = 'none';
                    } else {
                        console.error(`Element with ID comment-content-${commentId} or edit-comment-form-${commentId} not found.`);
                    }
                }
            })
            .catch(error => console.error('Error updating comment:', error));
        });
    });
});
