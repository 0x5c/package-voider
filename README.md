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

To get the labels to apply to a PR:

```
(venv) $ python -m voider labels PR_NUMBER
```

To run the tests, optionally passing a different `.tsv` tests file:

```
(venv) $ python -m voider tests [TESTS_FILE]
```
