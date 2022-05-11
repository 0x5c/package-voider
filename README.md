# Package Voider
Work-in-Progress auto-labelling for void-linux/void-packages

## Features

- [X] Determination of labels to apply
  - Modifications to xbps-src and `common/`
  - shlib changes
  - Changes to documentation
  - Changes to packages
    - Additions
    - Updates
    - Revbumps
    - Renames
    - Deletions
  - Detection of trivial updates
- [ ] Github Webhook listener
- [ ] Automatic application of labels

## Test it

Setup the environment and dependencies

```
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -Ur requirements.txt
```

You also need to create a file called `tokenfile` in the root of the project, containing a github Personal Access Token on first line.
Any further lines are simply not even read, if present. The PAT requires no special scopes.

To get the labels to apply to a PR:

```
(venv) $ python -m voider labels PR_NUMBER
```

To run the tests, optionally passing a different `.tsv` tests file:

```
(venv) $ python -m voider tests [TESTS_FILE]
```
