import sys
from DictionaryServices import *

def search_dictionary(word):
    result = DCSCopyTextDefinition(None, word, (0, len(word)))
    if result is None:
        return 0
    else:
        return 1

if __name__ == '__main__':
    main()
