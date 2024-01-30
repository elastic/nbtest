# nbtest

`nbtest` is Elastic's Search Labs testing and validation tool for Python
notebooks.

## Installation

```bash
pip install elastic-nbtest
```

## Usage

```bash
nbtest my-notebook.ipynb another-notebook.ipynb ...
```

## How it works

`nbtest` runs all the code cells in the notebook in order from top to bottom,
and reports two error situations:

- If any code cells raise an unexpected exception
- If any code cells that have output saved in the notebook generate a different
  output (not counting especially designated sections, as described in the
  "Configuration" section below)

Something to keep in mind when designing notebooks that are testable is that
for any operations that are asynchronous it is necessary to add code that
blocks until these operations complete, so that the entire notebook can
execute in batch mode without errors.

## Configuration

`nbtest` looks for a configuration file named `.nbtest.yml` in the same
directory as the target notebook. If the configuration file is found, it is
imported and applied for all the notebooks in that directory.

There is currently one supported configuration variable, called `masks`. This
variable can be set to a list of regular expresssions that capture details in
the output of code cells that vary from one run to the next and should be
masked when comparing the previously stored output against output from the
current run.

Here is an example `.nbtest.yml` file:

```yaml
masks:
- "'name': '[^']+'"
- "'cluster_name': '[^']+'"
- "'cluster_uuid': '[^']+'"
- "'build_flavor': '[^']+'"
- '[0-9]+\.[0-9]+\.[0-9]+'
- "'build_hash': '[^']+'"
- "'build_date': '[^']+'"
```

## Handling of the `getpass` function

The `nbtest` script installs an alternative version of the `getpass()` function
that looks for requested values in environment variables instead of starting an
interactive prompt.

Consider the following example, which is used in many Elastic notebooks:

```python
CLOUD_ID = getpass("Elastic Cloud ID:")
ELASTIC_API_KEY = getpass("Elastic Api Key:")
```

The `getpass()` function used by `nbtest` takes the prompt given as an
argument and converts it to an environment variable name with the following
rules:

- Spaces are converted to underscores
- Non-alphanumeric characters are removed
- Letters are uppercased

In the above example, the variables that will be used to source these prompts
are `ELASTIC_CLOUD_ID` and `ELASTIC_API_KEY`.

As a convenience, `nbtest` imports all variables defined in a `.env` file if
found. The `--env-file` option can be used to provide an alternative
environment file.

## Set up and tear down procedures

Sometimes it is necessary to perform "set up" and/or "tear down" operations
before and after a notebook runs. `nbtest` will look for notebooks with special
names designated as set up or tear down and execute those notebooks to perform
any necessary actions.

### Set up notebooks

`nbtest` will look for the following notebooks names and execute any that are
found before running the target notebook:

- `_nbtest_setup.ipynb`
- `_nbtest_setup.[notebook-name].ipynb`

The first one can be used for general set up logic that applies to all the
notebooks in the directory. The `NBTEST["notebook"]` expression can be used
inside this notebook to obtain the name of the notebook under test.

The second one should be used for set up actions that are specific to one
notebook.

A global setup notebook can also be provided in the `--setup-notebook` command
line argument. This notebook is executed once, before any tests.

### Tear down notebooks

`nbtest` will look for the following notebooks names and execute any that are
found after running the target notebook, regardless of the testing having
succeeded or failed:

- `_nbtest_teardown.[notebook-name].ipynb`
- `_nbtest_teardown.ipynb`

These notebooks are inteded for cleanup that needs to happen after a text, for
example to delete indexes that were created. As in the set up case,
`NBTEST["notebook"]` is set to the notebook that was tested.

A global teardown notebook can also be provided in the `--teardown-notebook`
command line argument. This notebook is executed once, after all the tests.

## Mocking and/or Monkey-Patching

For specific cases in which it is necessary for tests to alter the behavior of
functions or methods, `nbtest` provides the `--mocks` option. The argument to
this option is a Python module name, exactly as it would be entered in an
`import` statement. The module will be imported in the context of the notebook
and any defined setup and teardown procedures.

The module passed to the `--mocks` option can apply any patching techniques as
needed by the tests. The following example patches the `Elasticsearch` class to
always connect to a locally hosted instance without authentication, regardless
of the connection arguments that are passed:

```python
import elasticsearch

orig_es_init = elasticsearch.Elasticsearch.__init__


def patched_es_init(self, *args, **kwargs):
    return orig_es_init(self, 'http://localhost:9200')


elasticsearch.Elasticsearch.__init__ = patched_es_init
```
