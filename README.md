# era-5g-heartbeat

## Related Repositories

## Installation

The package could be installed via pip:

```bash
pip install era_5g_heartbeat
```

## Contributing, development

- The package is developed and tested with Python 3.8.
- Any contribution should go through a pull request from your fork.
- We use Pants to manage the code ([how to install it](https://www.pantsbuild.org/docs/installation)).
- Before committing, please run locally:
  - `pants fmt ::` - format all code according to our standard.
  - `pants lint ::` - checks formatting and few more things.
  - `pants check ::` - runs type checking (mypy).
  - `pants test ::` - runs Pytest tests.
- The same checks will be run within CI.
- A virtual environment with all necessary dependencies can be generated using `pants export ::`. 
  You may then activate the environment and add `era_5g_heartbeat` to your `PYTHONPATH`, which is equivalent 
  to installing a package using `pip install -e`.
- To generate distribution packages (`tar.gz` and `whl`), you may run `pants package ::`.
- For commit messages, please stick to
  [https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/).
