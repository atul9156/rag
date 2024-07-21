# RAG Assessment

Dummy RAG assignemnt

## Features

1. Index docs
2. Ask questions based on the docs provided
3. Get list of docs user has access to

## Future Scope

- Processing document may be a time taking step. In a more production ready setup, this should be handled in the background using frameworks like Celery. This will make the APIs much more performant and scalable
- Currently, authentication and authorisation are handled using user tokens which are generated at the time of creating users. This is a bad decision
  - Authentication should be handled by identity provider services like OAuth or JWT
  - A more robust Authorisation shoould be implemented which allows users to share the documents they upload with other users
- Proper validation on objects that are being stored in the database like name, email etc
- Implement a proper logout functionality. Logout should result in token change (atleast). Currently, logout method does nothing
- register method should ask for password, password should be encrypted and stored
- add abstract classes for filehandler types and data store types
- A lot of functions require user_id. Instead of passing user_id as a parameter everywhere, a context manager can be implemented in the middleware which has user_id as context variable. This can then be used whereever required