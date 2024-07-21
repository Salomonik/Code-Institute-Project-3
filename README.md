![Am i responsive](./assets/documentation/responsive.png)<br>

### The live link can be found here - [Game Central](https://milestone-project-3-jp-49f0065fdfbf.herokuapp.com/)

# Game Central

## Description

**Game Central Collection** is a comprehensive video game database website designed to allow users to explore and manage video game information. The site integrates with the IGDB API to fetch a vast collection of video games and leverages a PostgreSQL database to store additional user data and interactions. Key functionalities include browsing games, viewing detailed game information, managing user profiles, and maintaining a list of favorite games.

The application is built using Flask for the backend, SQLAlchemy for ORM, and is styled with Materialize CSS. It is deployed on Heroku, ensuring scalability and ease of access.

The main objective of Game Central Collection is to provide gamers with an extensive and easy-to-navigate platform to discover and keep track of their favorite games.


## Site Owner Goals

As the owner of Game Central Collection, the primary goals of the site are:

1. **Provide a Comprehensive Database**: Offer a wide range of video games with detailed information fetched from the IGDB API, ensuring that users have access to up-to-date and accurate data.

2. **Enhance User Engagement**: Create a user-friendly and interactive platform that encourages users to explore, discover, and interact with game information. This includes features such as game browsing, detailed game pages, and user comments.

3. **User Management and Personalization**: Allow users to create accounts, log in, and manage their profiles. Enable users to personalize their experience by adding games to their favorites list and leaving comments on game pages.

4. **Community Building**: Foster a sense of community among users by providing features that allow for interaction and sharing of opinions about different games. The ability to comment on games helps build this community aspect.

5. **Responsive Design**: Ensure the site is accessible and easy to use on both desktop and mobile devices, providing a seamless experience for all users.

6. **Scalability and Performance**: Utilize scalable technologies such as Heroku for deployment and PostgreSQL for data storage to handle growing user numbers and ensure the site performs well under load.

7. **Security**: Implement robust security measures to protect user data, including secure authentication, data encryption, and CSRF protection.


## Development Life Cycle

### Project Planning

During the project planning phase, the following steps were undertaken to ensure a structured and well-organized development process for Game Central Collection:

1. **Requirements Gathering**:
   - Identified the primary goals and objectives of the project.
   - Defined the core features and functionalities required for the application, including game browsing, user authentication, favorites management, and commenting.

2. **Research and Analysis**:
   - Conducted research on available APIs for video game data, selecting the IGDB API for its comprehensive dataset and reliable performance.
   - Analyzed similar existing platforms to identify best practices and potential areas for improvement.

3. **Technical Planning**:
   - Chose the Flask framework for backend development due to its simplicity and flexibility.
   - Selected PostgreSQL as the database system for its robustness and compatibility with Heroku.
   - Decided on using Materialize CSS for frontend design to ensure a responsive and modern user interface.

4. **Wireframing and Prototyping**:
   - Created wireframes and prototypes to visualize the layout and user flow of the application.
   - Gathered feedback on the prototypes to make necessary adjustments before starting development.

5. **Task Breakdown and Timeline**:
   - Broke down the project into manageable tasks and milestones.
   - Established a timeline for development, setting deadlines for each phase of the project.

6. **Setting Up the Development Environment**:
   - Configured version control using Git and set up a repository on GitHub.
   - Established a development environment with necessary tools and libraries, including virtual environments, required Python packages, and database configurations.

### Content Requirements

*Pages and Features*

1. **Home Page**:
   - Introduction to the site and its main features.
   - Search bar for users to search for games by name.
   - Display of popular games.

2. **Game Details Page**:
   - Detailed information about a specific game, including:
     - Name
     - Description
     - Release date
     - Cover image
     - User comments
   - Option to add the game to the user's favorites list (if logged in).

3. **User Profile Page**:
   - Display user information, including username and email.
   - List of the user's favorite games.
   - Option to update profile picture.

4. **Login Page**:
   - Form for users to log in with their email and password.

5. **Registration Page**:
   - Form for new users to sign up with their username, email, and password.
   - Validation for unique usernames and emails.

### Development Life Cycle

## Development

1. **Setting Up Flask Application**:
   - Initialized a Flask application.
   - Configured the app with necessary settings including the database and CSRF protection.
2. **Defining Database Models**:
   - Created SQLAlchemy models for `User`, `Game`, `Comment`, and a many-to-many relationship `favorites`.
3. **API Integration**:
   - Integrated with the IGDB API to fetch and display game data.
4. **Frontend Development**:
   - Created HTML templates using Jinja2 templating engine.
   - Utilized Materialize CSS framework for styling and responsiveness.

## Requirements

### Functional Requirements

1. **User Authentication**:
   - Users should be able to register, log in, and log out.
   - Registered users should have a unique username and email.
   - Passwords should be hashed and stored securely.

2. **User Profile**:
   - Users should be able to view and update their profile, including changing their avatar.
   - Profiles should display the number of favorite games and comments made by the user.
   - Users should be able to view the profiles of other users.

3. **Game Search and Display**:
   - Users should be able to search for games by name.
   - The application should display game details including name, genres, platforms, release dates, and summary.
   - Game data should be fetched from the IGDB API.

4. **Favorites Management**:
   - Users should be able to add games to their favorites.
   - Users should be able to view their list of favorite games.
   - Users should be able to remove games from their favorites.

5. **Comments**:
   - Users should be able to add comments to game pages.
   - Users should be able to edit and delete their own comments.
   - Comments should be displayed in chronological order on the game detail page.

6. **Home Page**:
   - The home page should display a list of popular games.
   - Each game on the home page should link to its detail page.

7. **Game Details Page**:
   - The game details page should display detailed information about the game.
   - The page should also show user comments and a form to add new comments.
   - Users should be able to toggle a game as a favorite from the game details page.

8. **Responsive Design**:
   - The application should be responsive and work well on both desktop and mobile devices.
   - The layout should adjust to different screen sizes, providing a good user experience on all devices.

9. **Error Handling**:
   - The application should handle errors gracefully.
   - Users should see user-friendly error messages if something goes wrong, such as failing to fetch data from the API or trying to access a page that doesn't exist.

10. **Security**:
    - CSRF protection should be implemented to prevent cross-site request forgery.
    - User input should be validated to prevent SQL injection and other security issues.

### Non-Functional Requirements

1. **Performance**:
   - Database queries should be optimized for fast retrieval of data.

2. **Reliability**:
   - The application should have minimal downtime.

3. **Usability**:
   - The user interface should be intuitive and easy to navigate.
   - Forms and other interactive elements should provide clear feedback to the user.

4. **Security**:
   - Sensitive data, such as user passwords, should be encrypted.
   - The application should be protected against common security threats, such as SQL injection, XSS, and CSRF.

8. **Accessibility**:
   - It should follow accessibility guidelines, such as providing alt text for images and ensuring good contrast between text and background colors.

### Out of Scope

The following features are not included in the current scope of the Game Central Collection project:

1. **Displaying All Comments on User Profiles**:
   - User profiles do not display a list of all comments made by the user.

2. **Liking Comments**:
   - The functionality to like or upvote comments is not available.

## User Experience

### User Stories

1. **As a visitor**, I want to be able to search for video games by name so that I can find information about my favorite games.
2. **As a visitor**, I want to view detailed information about a game, including its description, release date, genres, and platforms.
3. **As a visitor**, I want to be able to register for an account so that I can save my favorite games and leave comments.
4. **As a registered user**, I want to be able to log in and log out of my account.
5. **As a registered user**, I want to update my profile information, including changing my avatar.
6. **As a registered user**, I want to be able to add games to my list of favorites.
7. **As a registered user**, I want to be able to view and manage my list of favorite games.
8. **As a registered user**, I want to leave comments on game detail pages.
9. **As a registered user**, I want to edit and delete my own comments.
10. **As a registered user**, I want to be able to view the profiles of other users to see their favorite games.

**Returning User Experience**

1. **Seamless Login**:
   - Returning users can easily log in to their accounts using their registered email and password.


2. **Profile Management**:
   - Returning users can view and update their avatar.
   - Users can see a summary of their activity, such as the number of favorite games and comments made.

3. **Favorites Management**:
   - Returning users can view their list of favorite games from their profile page.
   - They can add new games to their favorites or remove games they are no longer interested in.

4. **Comment Interaction**:
   - Returning users can view their past comments on game detail pages.
   - They have the ability to edit or delete their own comments, ensuring their feedback stays relevant and accurate.

5. **Game Search and Discovery**:
   - Users can continue to search for new games using the search functionality.
   - Popular games and new additions are displayed on the home page, providing users with new content to explore.

6. **Personalized Experience**:
   - Notifications or flash messages can inform users of successful actions, such as adding a game to favorites or updating profile information.

## Design

### Color Scheme

The color scheme is designed to be visually appealing and easy on the eyes. It uses a combination of primary, secondary, and background colors to create a consistent and cohesive look throughout the application.

- **Primary Color**: `#F1DCBC`
- **Secondary Color**: `#2C6169`
- **Background Color**: `#19242F`
- **Text Color**: `white`

### Typography

The application uses the following fonts:

- **Header Font**: 'Helvetica Neue', sans-serif
- **Body Font**: 'Arial', sans-serif
- **Title Font**: 'Open Sans', sans-serif

These fonts are chosen to ensure readability and a modern look.

### Layout

The layout of the application is responsive and adapts to different screen sizes. The design principles followed include:

- **Max Width**: The maximum width of the container is set to `1200px`.
- **Padding and Margin**: Consistent padding and margin are applied throughout the application for a balanced layout.
- **Border Radius**: Rounded corners are applied to elements using a border radius of `8px`.
- **Box Shadow**: A subtle box shadow is used to add depth to the elements.

## Wireframe

<details>
<summary>Wireframe</summary>

<details>

<summary>Main Page</summary>

![Main Page Wireframe](./assets/documentation/wireframe-main.png)


</details>

<details>
<summary>Game Details</summary>

![Game Details Page Wireframe](./assets/documentation/wireframe-gamedetails.png)

</details>

<details>
<summary>Profile</summary>

![Profile Wireframe](./assets/documentation/wireframe-profile.png)

</details>

</details>


