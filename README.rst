==============
arkia11nmodels
==============

Authorization related ORM models and Pydantic schemas

Configuration
-------------

You need to configure some things even when running the development server locally to avoid accidents.

See dotenv.example on what you need to put into your .env -file.


Docker
------

For more controlled deployments and to get rid of "works on my computer" -syndrome, we always
make sure our software works under docker.

It's also a quick way to get started with a standard development environment.

SSH agent forwarding
^^^^^^^^^^^^^^^^^^^^

We need buildkit_::

    export DOCKER_BUILDKIT=1

.. _buildkit: https://docs.docker.com/develop/develop-images/build_enhancements/

And also the exact way for forwarding agent to running instance is different on OSX::

    export DOCKER_SSHAGENT="-v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock -e SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock"

and Linux::

    export DOCKER_SSHAGENT="-v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK -e SSH_AUTH_SOCK"

Creating a development container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Build image, create container and start it::

    docker build --ssh default --target devel_shell -t arkia11nmodels:devel_shell .
    docker create --name arkia11nmodels_devel -v `pwd`":/app" -it `echo $DOCKER_SSHAGENT` --net host -v /var/run/docker.sock:/var/run/docker.sock arkia11nmodels:devel_shell
    docker start -i arkia11nmodels_devel

pre-commit considerations
^^^^^^^^^^^^^^^^^^^^^^^^^

If working in Docker instead of native env you need to run the pre-commit checks in docker too::

    docker exec -i arkia11nmodels_devel /bin/bash -c "pre-commit install"
    docker exec -i arkia11nmodels_devel /bin/bash -c "pre-commit run --all-files"

You need to have the container running, see above. Or alternatively use the docker run syntax but using
the running container is faster::

    docker run --rm -it -v `pwd`":/app" arkia11nmodels:devel_shell -c "pre-commit run --all-files"

Test suite
^^^^^^^^^^

You can use the devel shell to run py.test when doing development, for CI use
the "tox" target in the Dockerfile::

    docker build --ssh default --target tox -t arkia11nmodels:tox .
    docker run --rm -it -v `pwd`":/app" `echo $DOCKER_SSHAGENT`  --net host -v /var/run/docker.sock:/var/run/docker.sock arkia11nmodels:tox

Production docker
^^^^^^^^^^^^^^^^^

There's a "production" target as well for running the CLI utilities. It runs "alembic upgrade head" by default.
Remember to change that architecture tag to arm64 if building on ARM::

    docker build --ssh default --target production -t arkia11nmodels:amd64-latest .
    docker run --rm -it -v /path/to/dotenv:/app/.env --name arkia11nmodels arkia11nmodels:amd64-latest

Deployments and docker compositions should run it directly from Docker hub::

    docker run --rm -it -v /path/to/dotenv:/app/.env --name arkia11nmodels pvarki/arkia11nmodels:latest


Development
-----------


TLDR:

- Create and activate a Python 3.8 virtualenv (assuming virtualenvwrapper)::

    mkvirtualenv -p `which python3.8` my_virtualenv

- change to a branch::

    git checkout -b my_branch

- install Poetry: https://python-poetry.org/docs/#installation
- Install project deps and pre-commit hooks::

    poetry install
    pre-commit install
    pre-commit run --all-files

- Ready to go.

Remember to activate your virtualenv whenever working on the repo, this is needed
because pylint and mypy pre-commit hooks use the "system" python for now (because reasons).
