$ErrorActionPreference = "Stop"

python -m unittest discover -s tests -p "test_*.py"
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

node tests/test_index_logic.js
exit $LASTEXITCODE
