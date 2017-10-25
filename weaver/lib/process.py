from __future__ import print_function

import shutil

from weaver.lib.models import *
from weaver.engines import choose_engine
from weaver.lib.defaults import DATA_DIR

from retriever import datasets
from weaver.lib.templates import BasicTextTemplate


class Processor(object):
    def __init__(self, name=None, dictt =None):
        self.name = name
        self.config = dictt
        self.scripts = []

        scripts_needed = set()
        for i in self.config["tables"]:
            scripts_needed.add(i["dataset"])

        # print(scripts_needed)
        # for scripts_i in datasets():
        #     if scripts_i.name in scripts_needed:
        #         # print(scripts_i.name,  scripts_i.tables)
        #         x = scripts_i.__dict__["tables"].items()
        #         for key, value in x:
        #             print(value.__dict__)

    def get_main_table_query(self):
        fields = self.config["main_file"]["fields"]
        table_name = self.config["main_file"]["table"]
        db_name = self.config["main_file"]["dataset"]
        field_from_main_table = field_table_colname(fields, table_name)
        result = self.config["result"]["table"]
        query = "\n(SELECT {atts} \nFROM {db}.{table} \nAS {result})".format(atts=field_from_main_table, db=db_name, table=table_name, result=result)
        print(query)
        return query


    def join_query(self):
        main_table_query_set = False
        for num in self.config['join']:

            #table
            num["tables"]



        query = "SELECT  * FROM"# +  field_string(self.config["main_file"]["fields"]) and its attirubes


def field_string(fields):
    attribute_string = ""
    for atts in fields:
       attribute_string += atts + ", "


def field_table_colname(fields, table_name):
    attribute_string = ""
    for atts in fields:
       attribute_string += "{}.{}, ".format(table_name, atts)
    return attribute_string.strip(", ")
# w = [
#       "comb_mass_g",
#       "continent",
#       "family",
#       "genus",
#       "log_mass_g",
#       "reference",
#       "species",
#       "sporder",
#       "status"
#     ]
#
# v = field_dbstring(w, "henry")
# print(v)

# def create_query(config=os.path.normpath(r"C:\Users\Henry\Documents\GitHub\weaver\manager\config\settings.json")):
#     """
#     returns the sql statement required to join the tables.
#
#     The join flavor used in left outer join and the first table is considered
#     as the base table
#     """
#     import json
#     # read configurations from json settings file
#     with open(config) as json_data_file:
#         data = json.load(json_data_file)
#
#     unique_tables = set()  # avoid repetition on table processing
#     number_of_joins = len(data['tables'])
#
#     processed_tables = 0  # number of processed tables
#     query_string = ""
#
#     item = 0
#
#     for items in data['tables']:
#         # loops through consecutive joins on two considered tables
#         number_of_tables = len(items["join"])
#
#         current_table = 0
#
#         if len(unique_tables) == 0 and processed_tables == 0:
#             query_string += " SELECT * FROM ( "
#         else:
#             query_string += " LEFT OUTER JOIN  "
#             # SQL += "JOIN ("
#         for table in items["join"]:  # look up the tables
#             if table not in unique_tables:
#                 if len(unique_tables) == 0:
#                     query_string += " SELECT "
#                 else:
#                     if current_table == 0:
#                         query_string += " ( SELECT "
#                     else:
#                         query_string += " LEFT OUTER JOIN ( SELECT "
#                 # use the table name to get the values of attributes
#                 # Select <Attributes>
#                 attributes = data[table]["attributes_to_project"]
#
#                 attribute_length = len(data[table]["attributes_to_project"])
#
#                 # select attribute, attribute, ...[,]
#
#                 for attribute in attributes:
#                     if attribute_length == 1:
#                         query_string += (attribute + " ")
#                     else:
#                         query_string += (attribute + ", ")
#                     attribute_length -= 1
#
#                 # Select <Attributes> FROM <Tablename >
#                 query_string += "FROM "
#
#                 query_string += data[table]["database_name"] + "." + table + " "
#
#                 # add a join <JOIN ( SELECT> if there are more expected tables and Using clause
#                 # add alias for the derived tables
#
#                 if len(unique_tables) == 0:
#                     query_string += " ) " + "temp" + str(item)
#                     item += 1
#                 else:
#                     query_string += " ) "
#                 current_table += 1
#                 number_of_tables -= 1  # decrese the nuber of tables
#                 unique_tables.add(table)  # add the table so that we do not join it again
#
#         processed_tables += 1
#         query_string += " temp" + str(item) + " USING ("
#         item += 1
#
#         pivot_len = len(items["join_on"])  # number of attributes used in the join
#         for pivots in items["join_on"]:
#             if pivot_len == 1:
#                 query_string += pivots
#             else:
#                 query_string += pivots + ", "
#             pivot_len -= 1
#         query_string += ")"
#         number_of_joins -= 1
#     return query_string+";"
#
# d = create_query()
# print(d)