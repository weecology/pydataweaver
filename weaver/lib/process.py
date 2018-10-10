from __future__ import print_function

from collections import OrderedDict


def make_sql(dataset):
    # 1. For spatial joins,
    # assume that the latitude and longitude fields are in the main file.
    # use ST_PointFromText ST_PointFromText('POINT(-71.064 42.28)', 4326);
    # 2. Refactoring to after raster joins are finalized

    main_table_path = dataset.main_file["path"]
    as_processed_table = OrderedDict([(main_table_path, "T1")])
    query_statement = ""
    all_fields = []
    make_temp = False

    # Process all tables that are to be joined
    # and the fields that are required
    for count, table2join in enumerate(dataset.join):

        as_tables = "as_" + str(count)  # Table references Table as T
        as_tables_dot = as_tables + "."
        as_processed_table[table2join["table"]] = as_tables

        # Create the values for the final select of fields using the
        # references Table name. Select a.t1, b.t1 c.t2 From ..
        # ie. a.t1, b.t1 c.t2
        fields_used = []
        if "fields_to_use" in table2join:
            if table2join["fields_to_use"]:
                all_fields += [as_tables_dot + field_name for field_name in table2join["fields_to_use"]]
                fields_used = table2join["fields_to_use"]
            elif table2join["table_type"] == "raster":
                fields_used = [" * "]
        fields_string = ', '.join(str(e) for e in fields_used)

        if "table_type" in table2join:
            # use the longitude ()and latitude to calculate the the_geom in a temp table
            # Note x is longitude and y is latitude
            # the_geom = ST_MakePoint(double precision x, double precision y) or
            # the_geom = ST_PointFromText('POINT(-71.064544 42.28787)', 4326);
            if table2join["table_type"] == "vector":

                make_temp = True  # Used to create a temp table with a geom
                left_join = "\nLEFT JOIN {table_i} {tablei_as} " \
                            "\nON ST_Within(t1.geom, {tablei_as}.geom) " \
                            "\n".format(table_i=table2join["table"], tablei_as=as_tables)

                query_statement += left_join
            elif table2join["table_type"] == "raster":
                pass
            else:
                # "table_type" is tabular
                left_join = "\nLEFT OUTER JOIN " \
                            "\n\t(SELECT {fields_used} " \
                            "\n\tFROM {table_j}) AS {table_j_as} " \
                            "".format(table_j=table2join["table"],
                                      table_j_as=as_tables,
                                      fields_used=fields_string)
                left_join += "\nON \n"

                # Process "ON" statements, having either similar
                # or different field/column names
                on_common_stmt = []
                if table2join["join_ocn"]["common_field"]:
                    for item_field in table2join["join_ocn"]["common_field"]:
                        on_common_stmt += ["{table_i}.{common_name}={table_j}.{common_name}".format(
                            table_i=as_processed_table[dataset.main_file["path"]],
                            table_j=as_processed_table[table2join["table"]],
                            common_name=str(item_field))]

                # process non common fields
                temp_dict = table2join["join_ocn"]
                temp_dict.pop("common_field", True)

                # Two lists whose index each match the field to use
                # when creating the conditional statement
                # Use index of one to obtain the value of the other
                tab_field_index = list(temp_dict.keys())
                on_diff_stmt = []
                for num, items in enumerate(temp_dict[tab_field_index[0]]):
                    new_on = "{tab_i}.{field_i}={tab_j}.{field_j}".format(
                        tab_i=as_processed_table[str(tab_field_index[0])],
                        field_i=items,
                        tab_j=as_processed_table[str(tab_field_index[1])],
                        field_j=temp_dict[tab_field_index[0]][num])
                    on_diff_stmt.append(new_on)

                all_on_stmts = on_diff_stmt + on_common_stmt

                on_condition = " AND ".join(str(etr) for etr in all_on_stmts)
                left_join += on_condition
                query_statement += left_join

    # Process the main file and create the query string for all the required fields
    if "fields" in dataset.main_file:
        if not dataset.main_file["fields"]:
            pivot_query = "\nSELECT {al} INTO {res} " \
                          "\nFROM {main_table} AS {table_m} " \
                          "".format(main_table=dataset.main_file["path"],
                                    al=', '.join(str(e) for e in all_fields),
                                    res="{result_dbi}.{result_tablei}",
                                    table_m=as_processed_table[main_table_path])
        else:
            # all_fields = dataset.main_file["fields"]
            all_fields = [as_processed_table[main_table_path] + "." + item_f
                          for item_f in dataset.main_file["fields"]]
            pivot_query = "\nSELECT {all_fls} into {res} " \
                          "\nFROM {main_table} AS {table_m} " \
                          "".format(all_fls="{all_flds}",
                                    main_table=dataset.main_file["path"],
                                    res="{result_dbi}.{result_tablei}",
                                    table_m=as_processed_table[main_table_path])
            if make_temp:
                # ["latitude", "longitude"]
                y = dataset.main_file["lat_long"][0]
                x = dataset.main_file["lat_long"][1]

                temp_fields = ["temp." + item_k for item_k in dataset.main_file["fields"]]
                temp_fields_string = ', '.join(str(e) for e in temp_fields) + ", "

                temp_geom_value = temp_fields_string + "ST_PointFromText('POINT(" \
                                                       "cast(temp.{x1} as varchar) " \
                                                       "cast(temp.{y1} as varchar))', " \
                                                       "4326) as the_geom ".format(x1=x, y1=y)

                pivot_query = "\nSELECT {all_flds} into {res} " \
                              "\nFROM (SELECT " + temp_geom_value + \
                              "\nFROM {main_table} temp) {table_m}". \
                                  format(all_flds="{all_flds}", main_table=dataset.main_file["path"],
                                         res="{result_dbi}.{result_tablei}",
                                         table_m=as_processed_table[main_table_path])

    str_4fields = ', '.join(str(e) for e in all_fields)
    stm = query_statement.format(all_flds=str_4fields)
    return pivot_query + " " + stm
