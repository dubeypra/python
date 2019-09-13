from dict_utils import get_from_dict
from fre_tpe_constants import FreTpeConstants

ODU2 = "ODU2"
ODU2E = "ODU2e"
ODU1 = "ODU1"
ODU3 = "ODU3"
ODU4 = "ODU4"
ODU2e = "ODU2e"

def getChildrenIds(fre):
    childIds = []
    # find the ParitionFreIds and add to the list
    partitionfres = fre.get('data').get('relationships').get('partitionFres')
    if partitionfres:
        data_partitions = partitionfres.get('data')
        for data in data_partitions:
            childIds.append(data.get('id'))

    # Find the decomposedFreIds and add to the list
    decomposedFres = fre.get('data').get('relationships').get('decomposedFres')
    if decomposedFres:
        data_decomposedFres = decomposedFres.get('data')
        for data in data_decomposedFres:
            childIds.append(data.get('id'))
    return childIds


def get_layer_rate(fre):
    if fre.get("data"):
        return get_from_dict(fre, ["data", "attributes", "layerRate"])
    else:
        return get_from_dict(fre, ["attributes", "layerRate"])


def is_l1_odu_rate(layer_rate):
    return layer_rate in [ODU2, ODU2e, ODU3, ODU4]


def get_fre_entity_type(fre):
    fre_attr = fre.get("data").get("attributes")
    if fre_attr:
        fre_additional_attr = fre_attr.get(FreTpeConstants.ADDITIONAL_ATTRIBUTES)
        if fre_additional_attr:
            return fre_additional_attr.get(FreTpeConstants.ENTITY_TYPE)
    return None


def get_network_role(fre):
    if fre.get(FreTpeConstants.DATA):
        return get_from_dict(fre, ["data", "attributes", "networkRole"])
    else:
        return get_from_dict(fre, ["attributes", "networkRole"])


def get_fre_type(fre):
    return get_from_dict(fre, ['data', 'attributes', 'freType'])


def get_fre_expectation(myfre):
    """
    From first FRE, get its expectation
    :param myfre:
    :return:
    """
    if FreTpeConstants.FRE_EXPECTATIONS in myfre[FreTpeConstants.DATA][FreTpeConstants.RELATIONSHIPS]:
        return myfre[FreTpeConstants.DATA][FreTpeConstants.RELATIONSHIPS][FreTpeConstants.FRE_EXPECTATIONS][FreTpeConstants.DATA][0][FreTpeConstants.ID]


def get_fre_abstract(myfre):
    """
    From first FRE, get its expectation
    :param myfre:
    :return:
    """
    if FreTpeConstants.ABSTRACTS in myfre[FreTpeConstants.DATA][FreTpeConstants.RELATIONSHIPS]:
        return myfre[FreTpeConstants.DATA][FreTpeConstants.RELATIONSHIPS][FreTpeConstants.ABSTRACTS][FreTpeConstants.DATA][0][FreTpeConstants.ID]

def synthesizes_additional_info(fre):
    layer_rate = get_layer_rate(fre)
    fre_type = get_fre_type(fre)
    network_role = get_network_role(fre)
    fre_expectations = get_fre_expectation(fre)

    additional_info = ''
    if layer_rate:
        additional_info = additional_info + layer_rate
    if fre_type:
        additional_info = additional_info + '_' + fre_type
    if network_role:
        additional_info = additional_info + '_' + network_role
    if fre_expectations:
        additional_info += '_' + 'Expectation'

    return additional_info
