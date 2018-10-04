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
            # process non common fields
            temp_dict = tabletojoin["join_ocn"]
            temp_dict.pop("common_field", True)

            # list of tables names:
            lll =  list(temp_dict.keys())
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
            left_join += str_2_j_on
            main_sql_join += left_join
            # print(left_join)

        print()
        print(main_sql_join)

        exit()