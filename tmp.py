import json

from mrdpf.io.general import get_supported_files
from mrdpf.helpers import run_parsers
from mrdpf.parsers import Parsers
from mrdpf.io.plist import DataclassJSONEncoder

items = get_supported_files('../Data/2 - Exit & Restart/', True)

for key in items.keys():
    print(str(key) + ': ' + '\n'.join([str(x.absolute()) for x in items[key]]))

results = run_parsers(items)

print(json.dumps(results[Parsers.PREFERENCES_PLIST][0].preferences, cls=DataclassJSONEncoder, indent=4))