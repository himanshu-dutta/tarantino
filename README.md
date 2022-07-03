<p align="center">
  <img src="https://raw.githubusercontent.com/himanshu-dutta/tarantino/master/assets/logo.png" alt="Tarantino">
</p>

---

Tarantino is a simple ASGI (Asynchronous Web Server Gateway) web framework intended for learning purposes only.

The idea is to cover 70-80% of usecases by building various featues (mostly from scratch) while exploring various alternative solutions to get a better understanding of different concepts used and choices made in more reliable Python web frameworks today.

---

## Installation

The package can currently be installed through git directly:

```console
$ pip install git+https://github.com/himanshu-dutta/tarantino.git
```

or with one of the two additional sets of dependencies: `test` and `dev`.

```console
$ pip install "tarantino[test] @ git+https://github.com/himanshu-dutta/tarantino.git"
```

---

### Test

The package can further be tested for usage with one of the two examples in the `examples` directory.

Navigating to the root of the example project and running:

```console
$ uvicorn index:app
```

launches the project and is accessible at `localhost:8000`.
