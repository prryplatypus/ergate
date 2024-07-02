# Dependencies

**Ergate** has a very similar dependency injection system to **FastAPI**, which is designed to be very simple to use, and to make it very easy for any developer to integrate other components with their application.


## What is dependency injection?

Dependency injection is a way through which your code declares what dependencies it needs to run, and where your code doesn't explicitly create that dependency when it needs to use it, but rather lets the underlying system/application (in this case, **Ergate**) automatically create those dependencies for it.

Dependency injection is an extremely powerful tool, since it allows you to do things like easily having common shared logic in your code and easily sharing common dependencies across different surfaces of your application, amongst other things; all of it while reducing code repetition.
