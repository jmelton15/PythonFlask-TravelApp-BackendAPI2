<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#data-storage-and-safety">Data Storage And Safety</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

### Capstone Project 2 - DTRI (Down To the Route of It) Refactored!
### This Is The Python/Flask Backend API Part of Capstone 2

This is the Python-Flask backend api portion of the project. This API is handles login, register, creating Json tokens, and handling the data algorithms behind creating and saving trips for users. Basically anything that has to do with the user's trips is handled from this API.

The detailed explanation of the application can be found at the link below: 
* [app details](https://github.com/jmelton15/React-TravelApp-Frontend)

### Future Plans
1.) Finish the password reset portion of the API to allow users a secure way to update their passwords.

### Built With - Credits To The Following:

* [Python](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/en/2.0.x/)


<!-- GETTING STARTED -->
## Getting Started

Routes are in the REST api style.
In this API you will find routes all following '/users/'
The only routes that do not follow this are the Login and Register, which are /login and /register respectively
https://jmelton.dev:8001/   -> this will give you back a json value of {"Message":"welcome...."}


<!-- DATA STORAGE AND SAFETY -->
## Authorization and Authentication

All routes are setup for authorization and validation using JWT (json web tokens) 

## Data Storage And Safety

Passwords from users are encrypted with a well-trusted encryption algorithm, not one that I made on my own.

<!-- CONTACT -->
## Contact

Your Name - [John Melton]
Email - [johnmelton.projects@gmail.com]









