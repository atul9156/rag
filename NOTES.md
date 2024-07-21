# Notes

## Assumptions

- This app may be used by more than one user concurrently
- Name and email are valid

## Modifications

- Most of the requests require authentication. Authentication is handled by token which is generated at the time user is created. To ahndle this, the function signature of all the apis which require authentication have been changed to accept a `user` object as a parameter
- Authentication is handled by middleware
- Instead of using a POST request for updating user details, a PUT request is used