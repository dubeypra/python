"""
 Following Modules has to be installed
 pip install graphviz . Will be added in case required to export tree structure
 pin install anytree
  pip install requests
"""

from anytree import Node, RenderTree
import requests
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from fre_helper import getChildrenIds, synthesizes_additional_info, get_fre_abstract, get_layer_rate, is_l1_odu_rate


class FreTreeView(object):
    root_node = None
    root_node_json = None

    def __init__(self, search_fre_id, display_name):
        self.root_node = Node(display_name + '(' + search_fre_id + ')')
        self.root_node_json = {'Name': display_name,
                          'fre id': search_fre_id}

    def print_tree(self):

        print '****************************** Relationship Graph ********************************'

        for pre, fill, node in RenderTree(self.root_node):
            print("%s%s" % (pre, node.name))


        print '****************************** Relationship Data in JSON ********************************'
        print json.dumps(self.root_node_json, indent=4,sort_keys=True)

    def add_node(self, parent_node, fre_id, display_name):
        return Node(display_name + '(' + fre_id + ')', parent_node)

    def add_node_json(self, parent_node, fre_id, display_name):
        node = {'Name': display_name,
                'fre id': fre_id
                }

        if parent_node.has_key('participator'):
            child_data = parent_node['participator']
        else:
            child_data = []

        child_data.append(node)
        parent_node['participator'] = child_data

        return node


class DataFetcher(object):
    GET_TOKEN_URL = 'https://{}/tron/api/v1/tokens'
    GET_TOKEN_DATA = {'username': 'admin', 'password': 'adminpw', 'tenant': 'master', 'grant_type': 'password'}
    GET_FRE = 'https://{}/nsi/api/fres/'

    def __init__(self, ip_server):
        #  Get Token functionality
        self.active_token_url = self.GET_TOKEN_URL.format(ip_server)

        header_info = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.active_token = \
            requests.post(self.active_token_url, data=self.GET_TOKEN_DATA, headers=header_info, verify=False).json()[
                'token']

        self.active_header = {'Authorization': "Bearer " + self.active_token, 'Content-Type': 'application/json'}
        self.active_ip = ip_server

        print "active ip", self.active_ip, " active token ", self.active_token

    def get_fre_data(self, fre_id):
        url = self.GET_FRE.format(self.active_ip) + fre_id
        response = requests.get(url, headers=self.active_header, verify=False).json()
        print response

        return response

    def get_fre_data_with_abstract(self, fre_id):
        url = self.GET_FRE.format(self.active_ip) + fre_id + '?include=abstracts'
        response = requests.get(url, headers=self.active_header, verify=False).json()
        print response

        return response


class FreChecker(object):
    def __init__(self, ip_server, search_fre_id, display_name):
        self.ip = ip_server
        self.root_fre_id = search_fre_id
        self.root_display_name = display_name

    def create_fre_child_graph(self):
        fetcher = DataFetcher(self.ip)

        tree_view = FreTreeView(self.root_fre_id, self.root_display_name)
        top_level_fre = fetcher.get_fre_data(self.root_fre_id)
        child_fre_ids = getChildrenIds(top_level_fre)
        self.recursive_add_node(tree_view, tree_view.root_node, fetcher, child_fre_ids, tree_view.root_node_json)

        tree_view.print_tree()

    def recursive_add_node(self, tree_view, parent_fre_node, fetcher, child_fre_ids, parent_node_json=None):
        for child_fre_id in child_fre_ids:
            intermediate_parent_fre = fetcher.get_fre_data(child_fre_id)
            # TODO : Whatever information for FRE required  CHnage in below function
            additional_info = synthesizes_additional_info(intermediate_parent_fre)

            intermediate_parent_node = tree_view.add_node(parent_fre_node, child_fre_id, additional_info)
            intermediate_parent_node_json = tree_view.add_node_json(parent_node_json, child_fre_id, additional_info)

            intermediate_child_fre_ids = getChildrenIds(intermediate_parent_fre)

            if intermediate_child_fre_ids and len(intermediate_child_fre_ids) > 0:
                self.recursive_add_node(tree_view, intermediate_parent_node, fetcher, intermediate_child_fre_ids,
                                        intermediate_parent_node_json)

    def create_fre_abstract_graph(self):
        fetcher = DataFetcher(self.ip)

        tree_view = FreTreeView(self.root_fre_id, self.root_display_name)
        top_level_fre = fetcher.get_fre_data_with_abstract(self.root_fre_id)

        layer_rate = get_layer_rate(top_level_fre)

        if not is_l1_odu_rate(layer_rate):
            encap_id = getChildrenIds(top_level_fre)
            encap_fre = fetcher.get_fre_data(encap_id[0])
            otn_fre_id = getChildrenIds(encap_fre)
            top_level_fre = fetcher.get_fre_data_with_abstract(otn_fre_id[0])

        abstract_fre_id = get_fre_abstract(top_level_fre)

        self.recursive_add_abstract_node(abstract_fre_id, fetcher, tree_view, tree_view.root_node)
        tree_view.print_tree()

    def recursive_add_abstract_node(self, abstract_fre_id, fetcher, tree_view, parent_fre_node):
        if abstract_fre_id:
            intermediate_fre = fetcher.get_fre_data_with_abstract(abstract_fre_id)
            additional_info = synthesizes_additional_info(intermediate_fre)
            intermediate_parent_node = tree_view.add_node(parent_fre_node, abstract_fre_id, additional_info)
            intermediate_abstract_fre_id = get_fre_abstract(intermediate_fre)

            if intermediate_abstract_fre_id:
                self.recursive_add_abstract_node(intermediate_abstract_fre_id, fetcher, tree_view,
                                                 intermediate_parent_node)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help=" server ip", default="")
    parser.add_argument("--fre_id", help="Top Level Fre Id", default="")
    parser.add_argument("--label", help="Name or Label", default="")

    args = parser.parse_args()
    checker = FreChecker(args.server,args.fre_id, args.label)
    # checker.create_fre_abstract_graph()
    checker.create_fre_child_graph()

    #python tree_view_fre.py --server=10.186.1.98  --fre_id=-4151597199480168631 --label=dubey


if __name__ == "__main__":
    main()
