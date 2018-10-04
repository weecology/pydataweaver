from __future__ import print_function

import shutil

# from weaver.lib.models import *
from weaver.lib.models import myTables
from weaver.engines import choose_engine
from weaver.lib.defaults import DATA_DIR

from retriever import dataset_names
from weaver.lib.templates import TEMPLATES


class Processor(object):
    def make_sql(dataset):

        processed_as= {}
        processed_as[dataset.main_file["path"]] = "t1"

        # print (dataset.main_file)
        # print (dataset.main_file["fields"])
        # print (processed_as)
        main_sql_join = ""

        if "fields" in dataset.main_file:
            if not dataset.main_file["fields"]:
                main_sql_join = "\nSELECT * INTO {res} \nFROM {main_table}  AS  t1 ".format(main_table=dataset.main_file["path"],
                                                                                            res="{db}.{table_name}")
            else:
                all_fields = dataset.main_file["fields"]
                string_field = ', '.join(str(e) for e in all_fields)
                # todo fake
                # fake_f += "{m_one_}.i" for i in __{all_flds}_
                main_sql_join = "\nSELECT {all_flds} INTO {res} \nFROM {main_table} AS t1 ".format(all_flds=string_field,
                                                                                             main_table=dataset.main_file["path"],
                                                                                                   res="{db}.{table_name}"
                                                                                                        )
        # for counter, tabletojoin in enumerate(dataset.join):
        #     f_fields_used = tabletojoin["fields_to_use"]
        #     str_f_fields_used = ','.join(str(e) for e in f_fields_used)
        #
        #     left_join = "\n\nLEFT OUTER JOIN \n(SELECT {fields_used}  \n\tFROM {t2_j} AS tsb ".format(t2_j=tabletojoin["table"], fields_used=str_f_fields_used)
        #     left_join += "\nON \n"
        #     str_2_j_on = "\nAND \n".join(str(e) for e in tabletojoin["join_on"])

        for counter, tabletojoin in enumerate(dataset.join):
            as_tables = "as_" + str(counter)
            processed_as[tabletojoin["table"]] = as_tables

            if "fields_to_use" in tabletojoin:
                if tabletojoin["fields_to_use"]:
                    f_fields_used = tabletojoin["fields_to_use"]
                else:
                    # Use valuse of fields in tables or *, for now lets use *
                    f_fields_used = ["*"]
            str_f_fields_used = ', '.join(str(e) for e in f_fields_used)

            left_join = "\n\nLEFT OUTER JOIN \n(SELECT {fields_used}  \n\tFROM {t2_j}) AS {tsb} ".format(
                t2_j=tabletojoin["table"],
                tsb=as_tables,
                fields_used=str_f_fields_used)
            left_join += "\nON \n"

            string_b4_list = []
            if tabletojoin["join_ocn"]["common_field"]:
                for item_field in tabletojoin["join_ocn"]["common_field"]:
                    string_b4_list += ["{t11}.{samefield}={t22}.{samefield}".format(
                        t11=processed_as[dataset.main_file["path"]],
                        t22=processed_as[tabletojoin["table"]],
                        samefield=str(item_field))]

            #process non common fields
            temp_dict = tabletojoin["join_ocn"]
            # print (temp_dict)
            # print (type(temp_dict))
            # exit()
            temp_dict.pop("common_field", True)

            # list of tables names:
            lll =  list(temp_dict.keys())
            # These should be two
            #
            # x1 =temp_dict[0]
            # x2 = temp_dict[1]
            string_3_on_list = []
            for counter, items in enumerate(temp_dict[lll[0]]):
                new_on = "{tt1}.{f11}={tt2}.{f22}".format(
                    tt1=processed_as[str(lll[0])],
                    f11=items,
                    tt2=processed_as[str(lll[1])],
                    f22=temp_dict[lll[0]][counter]
                )
                string_3_on_list.append(new_on)

            str_2_j_on = "\nAND \n".join(str(e) for e in string_3_on_list+string_b4_list)

            # for counter, st in enumerate(tabletojoin["join_on"]):
            #     on_state += st
            # if counter < len(tabletojoin["join_on"]) - 1:
            #     on_state += "\nAND \n"

            left_join += str_2_j_on
            main_sql_join += left_join
            # print(left_join)

        print()
        print(main_sql_join)

        exit()
# "﻿SELECT * FROM mammal_life_hist.species
# LIMIT 100"
#
# "﻿SELECT * FROM mammal_diet.diet ORDER BY taxonid ASC"
#
# """
# SELECT PS1.pilot_name
#   FROM PilotSkills AS PS1
#        LEFT OUTER JOIN
#        Hangar AS H1
#        ON PS1.plane_name = H1.plane_name
#   GROUP BY PS1.pilot_name
# HAVING COUNT(PS1.plane_name) = (SELECT COUNT(plane_name) FROM Hangar)
#    AND COUNT(H1.plane_name) = (SELECT COUNT(plane_name) FROM Hangar);
# """
#
#
# """SELECT r.id, r.name
# FROM Recipes r
# WHERE NOT EXISTS (SELECT * FROM Ingredients i
#                   WHERE name IN ('chocolate', 'cream')
#                   AND NOT EXISTS
#                       (SELECT * FROM RecipeIngredients ri
#                        WHERE ri.recipe_id = r.id
#                        AND ri.ingredient_id = i.id))"""



    # def __init__(self, name=None, dataobj =None):
    #     name = name
    #     config = dataobj
    #
    #     main_table = config["main_file"]
    #     result_table = config["result"]
    #     first_table = myTables[main_table["table_type"]](name=main_table["table_name"], **main_table)
    #     for i in config["tables"]:
    #         xx = i["table_type"]
    #         vv = myTables[xx](name=i["table_name"], **i)


    def create_query(self, config):
        """
        returns the sql statement required to join the tables.
        The join flavor used in left outer join and the first table is considered
        as the base table
        """

        # read configurations from json settings file
        with open(config) as json_data_file:
            data = json.load(json_data_file)

        unique_tables = set()  # avoid repetition on table processing
        number_of_joins = len(data['tables'])

        processed_tables = 0  # number of processed tables
        query_string = ""

        item = 0

        for items in data['tables']:
            # loops through consecutive joins on two considered tables
            number_of_tables = len(items["join"])

            current_table = 0

            if len(unique_tables) == 0 and processed_tables == 0:
                query_string += " SELECT * FROM ( "
            else:
                query_string += " LEFT OUTER JOIN  "
                # SQL += "JOIN ("
            for table in items["join"]:  # look up the tables
                if table not in unique_tables:
                    if len(unique_tables) == 0:
                        query_string += " SELECT "
                    else:
                        if current_table == 0:
                            query_string += " ( SELECT "
                        else:
                            query_string += " LEFT OUTER JOIN ( SELECT "
                    # use the table name to get the values of attributes
                    # Select <Attributes>
                    attributes = data[table]["attributes_to_project"]

                    attribute_length = len(data[table]["attributes_to_project"])

                    # select attribute, attribute, ...[,]

                    for attribute in attributes:
                        if attribute_length == 1:
                            query_string += (attribute + " ")
                        else:
                            query_string += (attribute + ", ")
                        attribute_length -= 1

                    # Select <Attributes> FROM <Tablename >
                    query_string += "FROM "

                    query_string += data[table]["database_name"] + "." + table + " "

                    # add a join <JOIN ( SELECT> if there are more expected tables and Using clause
                    # add alias for the derived tables

                    if len(unique_tables) == 0:
                        query_string += " ) " + "temp" + str(item)
                        item += 1
                    else:
                        query_string += " ) "
                    current_table += 1
                    number_of_tables -= 1  # decrese the nuber of tables
                    unique_tables.add(table)  # add the table so that we do not join it again

            processed_tables += 1
            query_string += " temp" + str(item) + " USING ("
            item += 1

            pivot_len = len(items["join_on"])  # number of attributes used in the join
            for pivots in items["join_on"]:
                if pivot_len == 1:
                    query_string += pivots
                else:
                    query_string += pivots + ", "
                pivot_len -= 1
            query_string += ")"
            number_of_joins -= 1
