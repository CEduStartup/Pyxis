
def dict_equals(dict1, dict2):
    """Returns True if 2 dictionaries are equals, otherwise returns False.
    
    :Parameters:
        - dict1 - dict
        - dict2 - dict

    :Returns:
        bool
    """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return False
    if len(dict1) != len(dict2):
        return False
    for k in dict1:
        if k not in dict2:
            return False
        if dict1[k] != dict2[k]:
            return False
    return True
    

if __name__ == "__main__":
    assert dict_equals({}, {})
    assert dict_equals({'a': 1}, dict(a=1))
    assert dict_equals({'a': 1, 'b': 2}, {'a': 1, 'b': 2})
    
    assert not dict_equals(None, None)
    assert not dict_equals(1, 1)
    assert not dict_equals(1, 2)
    assert not dict_equals({}, {'a': 1})
    assert not dict_equals({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': 3})