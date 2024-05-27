# Fixing Some Errors

Edit `/home/dgmastertemple/.local/lib/python3.10/site-packages/nltk/lm/counter.py`
```
from collections import defaultdict
from collections.abc import Sequence
```

Edit `/home/dgmastertemple/.local/lib/python3.10/site-packages/nltk/lm/vocabulary.py`
```
from collections import Counter
from collections.abc import Iterable
```
