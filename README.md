# Pantry Pickup Demo

An early prototype for a food pantry's donation intake and pickup workflow. A numbered paper tally can be entered as JSON when connectivity returns. Replaying the same intake record does not count the donation twice. A pickup can be assigned to only one volunteer.

Requires Python 3.10 or later and uses SQLite from the standard library. All sample records are synthetic.

```sh
python3 -m unittest -v
python3 pantry.py demo.sqlite intake fixtures.json
python3 pantry.py demo.sqlite intake fixtures.json
python3 pantry.py demo.sqlite pickup DEMO-001 volunteer-a
```

The second import reports zero new records. A conflicting reuse of a donation ID rejects the entire batch. A different volunteer cannot claim a donation that already has a pickup. This is a local command-line prototype for evaluating the workflow before building a volunteer interface.
