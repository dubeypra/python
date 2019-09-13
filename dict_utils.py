import copy


def get_from_dict(data_dict, keys, default=None):
    if not data_dict:
        return default

    if not keys:
        return default

    for key in keys:
        data_dict = data_dict.get(key)
        if data_dict is None:
            return default
    return data_dict


def nested_set(data_dict, keys, value):
    for key in keys[:-1]:
        data_dict = data_dict.setdefault(key, {})
    data_dict[keys[-1]] = value


def merge_dicts(source, destination, path=None):
    """
    Deep merging of the source dict into the destination dict (overriding overlapping values)
    :param source:      the source instance to merge by priority/preference
    :param destination: the destination instance (base settings to override for all overlaps)
    :return: the merged instance
    """
    merged = copy.deepcopy(destination)
    if path is None:
        path = []
    for key in source:
        if key in destination:
            if isinstance(destination[key], dict) and isinstance(source[key], dict):
                merged[key] = merge_dicts(source[key], destination[key], path + [str(key)])
            elif isinstance(destination[key], list) and isinstance(source[key], list):
                merged[key] = merge_lists(source[key], destination[key])
            elif isinstance(source[key], type(destination[key])):
                # Special handling for boolean attributes where an attribute is disabled in the source yet enabled
                # in destination (e.g. "oamEnabled" is True in profile's content as presented in the destination yet
                # False in the facade resource).  In this case, always takes "True" as the merged result
                if isinstance(source[key], bool):
                    merged[key] = source[key] or merged[key]
                else:
                    merged[key] = source[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            merged[key] = source[key]
    return merged


def merge_lists(source, destination):
    """
    Merging of destination list into source list. Following cases are implemented:
    1. for list of dictionaries, two dictionaries at same index are merged together
    2. for list of lists, recursive call for two lists at same index
    3. for list of other items (simple values), merge is based on a set.update (union) of the two lists
    :param source:
    :param destination:
    :return:
    """
    merged = []
    if (is_list_of_dicts(source) and is_list_of_dicts(destination)) or \
            (is_list_of_lists(source) and is_list_of_lists(destination)):
        for index, value in enumerate(destination):
            if index >= len(source):
                # reach end of source
                merged.extend(destination[index:])
                break
            elif is_list_of_dicts(source):
                merged.append(merge_dicts(source[index], destination[index]))
            else:
                merged.append(merge_lists(source[index], destination[index]))
        if len(source) > len(destination):
            merged.extend(source[len(destination):])
    else:
        merged_set = set(destination)
        merged_set.update(set(source))
        merged = list(sorted(merged_set))
    return merged


def is_list_of_dicts(lst):
    # Evaluation assumption based on first item type - empty list is True
    return isinstance(lst[0], dict) if len(lst) > 0 else True


def is_list_of_lists(lst):
    # Evaluation assumption based on first item type - empty list is True
    return isinstance(lst[0], list) if len(lst) > 0 else True


def find_key_val_in_dict_of_dicts(dict_of_dicts, match_key, match_value, skip_dict_key=None):
    # for dictionary of dictionaries search for matching key and value and return dictionary that has the match
    # skip the dict with dict_key specified
    if not isinstance(dict_of_dicts, dict):
        return None
    # start with first level dictioary (dict)
    for dict_key, dict_value in dict_of_dicts.iteritems():
        if skip_dict_key and dict_key == skip_dict_key:
            continue
        if dict_value:
            # iterate through second level dictionary and look for match
            for key, value in dict_value.iteritems():
                if key == match_key and value == match_value:
                    return dict_value              # return dictionary with matching key and value
    return None


def get_list_of_vals_from_dict_of_dicts(dict_of_dicts, match_key, skip_dict_key=None):
    # from dictionary of dictionaries create a list of values that match given key
    # skip the dict with dict_key specified
    if not isinstance(dict_of_dicts, dict):
        return []
    list_vals = list()
    for dict_key, dict_value in dict_of_dicts.iteritems():
        if skip_dict_key and dict_key == skip_dict_key:
            continue
        if dict_value:
            for key, value in dict_value.iteritems():
                if key == match_key:
                    list_vals.append(value)
    return list_vals

def get_list_of_dicts_rid_of_internal_lists(entities_list):

    refined_entity_list = list()

    for entity in entities_list:
        if entity and len(entity.get("data")) > 0:
            temp = dict()
            temp.setdefault('data', entity.get("data"))
            # add included by removing its list data
            if "included" in entity and len(entity["included"]) > 0:
                temp.setdefault('included', entity.get("included")[0])

            refined_entity_list.append(temp)

    return refined_entity_list