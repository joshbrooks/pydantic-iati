# pydantic-iati
International Aid Transparency Initiative schema in typed python

## Set Up

```python
python -m venv env
. env/bin/activate
pip install pip-tools
pip-sync requirements/*.txt
```

## Testing

```
flake8 .
mypy .
black .
pytest
```
