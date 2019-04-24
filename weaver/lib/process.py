from __future__ import print_function

from collections import OrderedDict


def rename_fields(dictionary_object, original, alias):
    if not dictionary_object:
        return None
    for items in dictionary_object.keys():
        if original in dictionary_object[items]:
            dictionary_object[items] = [
                x if not x == original else alias for x in dictionary_object[items]
            ]
    return dictionary_object


def make_sql(dataset):
    # 1. For spatial joins,
    # assume that the latitude and longitude fields are in the main file.
    # use ST_PointFromText ST_PointFromText('POINT(-71.064 42.28)', 4326);
    # 2. Refactoring to after raster joins are finalized

    main_table_path = dataset.main_file["path"]
    processed_tables = {main_table_path: {"name": "T1"}}
    as_processed_table = processed_tables

    if "lat_long" in dataset.main_file and dataset.main_file["lat_long"]:
        as_processed_table[main_table_path]["latitude"] = dataset.main_file["lat_long"][
            0
        ]
        as_processed_table[main_table_path]["longitude"] = dataset.main_file[
            "lat_long"
        ][1]

    query_statement = ""
    all_fields = []  # Remove the geom or rast fields used to calculate feature value.
    unique_f = set()
    rast_values = []

    if "fields" in dataset.main_file:
        if dataset.main_file["fields"]:
            all_fields += [
                as_processed_table[main_table_path]["name"] + "." + item_f.lower()
                for item_f in dataset.main_file["fields"]
            ]
            unique_f |= set(dataset.main_file["fields"])

    # Process all tables that are to be joined
    # and the fields that are required

    for count, table2join in enumerate(dataset.join):
        # Local fields
        make_local_temp = False
        local_raster_fields = set()
        local_vector_fields = set()
        local_tabular_fields = set()
        to_join = OrderedDict(table2join["join_ocn"])

        res_set = set(to_join.keys()) - {"common_field", table2join["table"]}
        join_with = res_set.pop()

        rast_alias = ""
        geom_alias = ""
        where_clause = ""
        left_join = ""
        left_join_on = ""
        original_tabular_fields = []

        vector_table, raster_table, tabular_table = None, None, None

        if table2join["table_type"] == "vector":
            vector_table = True
        elif table2join["table_type"] == "raster":
            raster_table = True
        elif table2join["table_type"] == "tabular":
            tabular_table = True
        elif not table2join["table_type"]:
            # Keep this option.
            # If the table type is not added, assume tabular
            tabular_table = True

        # Create table alias using count
        as_tables = "as_" + str(count)  # Table references Table as T
        as_tables_dot = as_tables + "."

        # Keep table information for lat and long name

        as_processed_table[table2join["table"]] = {"name": as_tables}

        # Get a list of fields from the table or create needed fields.
        # Rasters can have empty fields, `rast` should be added if not in field.
        # Vectors can have empty fields, geom should be included by default.

        local_fields_used = []
        if "fields_to_use" in table2join:
            local_fields_used = [
                field_to_lower.lower() for field_to_lower in table2join["fields_to_use"]
            ]

            if vector_table:
                # Remove 'geom'
                # Rename the geom with respect to the DB and the table names
                # SELECT id, geom as geom_table_name FROM table_name
                local_vector_fields |= set(local_fields_used)
                local_vector_fields.discard("geom")
                # Add fields that do not use alias to all_fields
                all_fields += [
                    as_tables_dot + field_i
                    for field_i in list(local_vector_fields)
                    if field_i not in unique_f
                ]
                geom_alias = "geom_{As_DB}_{Ta}".format(
                    As_DB=table2join["database_name"], Ta=table2join["table_name"]
                )
                local_vector_fields.add(
                    "geom AS {geom_alias}".format(geom_alias=geom_alias)
                )
                local_fields_used = list(local_vector_fields)
                # remove_fields += geom_alias
                # Update the join on dictionary with the new alias
                to_join = rename_fields(to_join, "geom", geom_alias)

            if raster_table:
                # Remove and rename 'rast' with respect to the DB and the table
                # names
                local_raster_fields |= set(local_fields_used)
                local_raster_fields.discard("rast")
                # Add fields that do not use alias to all_fields
                all_fields += [
                    as_tables_dot + field_i for field_i in list(local_raster_fields)
                ]
                rast_alias = "rast_{As_DB}_{Ta}".format(
                    As_DB=table2join["database_name"], Ta=table2join["table_name"]
                )
                local_raster_fields.add(
                    "rast AS {rast_alias}" "".format(rast_alias=rast_alias)
                )
                local_fields_used = list(local_raster_fields)
                # all_fields += [as_tables_dot + rast_alias]

                # Update the join on dictionary with the new alias
                to_join = rename_fields(to_join, "rast", rast_alias)

            if tabular_table:
                local_tabular_fields |= set(local_fields_used)

                # Remove and rename the longitude and the latitude
                if "lat_long" not in table2join:
                    all_fields += [
                        as_tables_dot + field_i
                        for field_i in list(local_tabular_fields)
                        if field_i not in unique_f
                    ]
                else:
                    make_local_temp = True
                    # ["latitude", "longitude"] [y,x]
                    y = table2join["lat_long"][0]
                    x = table2join["lat_long"][1]
                    as_DB = table2join["database_name"]
                    as_Ta = table2join["table_name"]

                    # Original will select longitute and latitude
                    # Using their original names
                    original_tabular_fields = list(local_tabular_fields)

                    local_tabular_fields.discard(y)
                    local_tabular_fields.discard(x)
                    lat_alias = "lat_{as_DB}_{as_Ta}".format(as_DB=as_DB, as_Ta=as_Ta)
                    long_alias = "long_{as_DB}_{as_Ta}".format(as_DB=as_DB, as_Ta=as_Ta)
                    all_fields += [
                        as_tables_dot + field_i
                        for field_i in list(local_tabular_fields)
                        if field_i not in unique_f
                    ]
                    local_tabular_fields.add(
                        "{y} AS {lat_alias}".format(y=y, lat_alias=lat_alias)
                    )
                    local_tabular_fields.add(
                        "{x} AS {long_alias}".format(x=x, long_alias=long_alias)
                    )

                    as_processed_table[table2join["table"]]["latitude"] = lat_alias
                    as_processed_table[table2join["table"]]["longitude"] = long_alias

                    # add alias
                    all_fields += [
                        as_tables_dot + lat_alias,
                        as_tables_dot + long_alias,
                    ]

                    # Update the join on dictionary with the new alias
                    to_join = rename_fields(to_join, "rast", lat_alias)
                    to_join = rename_fields(to_join, "rast", long_alias)

                    # include where statement, use original fields
                    # Rows with no latitude and longitutde values are not considered
                    # If we consider them, we increase the time complexity
                    where_clause = (
                        "\n\tWHERE {latitude} Not LIKE '%NULL%' "
                        "\n\tAND {latitude} IS NOT NULL "
                        "\n\tAND {longitude} Not LIKE '%NULL%' "
                        "\n\tAND {longitude} IS NOT NULL "
                        "".format(latitude=y, longitude=x)
                    )
                local_fields_used = list(local_tabular_fields)

        # Create `LEFT JOIN` and ON statements raster and vector data
        if raster_table or vector_table:
            left_join += (
                "\nLEFT OUTER JOIN "
                "\n\t(SELECT {fields_used} "
                "\n\tFROM {table_j}) AS {table_j_as} "
                "".format(
                    fields_used=", ".join(str(e) for e in local_fields_used),
                    table_j=table2join["table"],
                    table_j_as=as_tables,
                )
            )
            # on statement
            # look for the names of longitude and latitude for the particular join.
            # Get the table to be joined to,
            # set U =  to_join keys known-keys = {"common_field", values for this table}
            # To join with  = U | {"common_field", table2join["table"]}
            res_set = set(to_join.keys()) - {"common_field", table2join["table"]}
            join_with = res_set.pop()

            if join_with in as_processed_table:
                # ["latitude", "longitude"] [y,x]
                y = as_processed_table[join_with]["latitude"]
                x = as_processed_table[join_with]["longitude"]
            else:
                msg = (
                    "The order of the tables in the script needs re-arranging.\n"
                    "Table {a} should be processed first before "
                    "{b}".format(a=join_with, b=table2join["table"])
                )
                print(msg)
                exit()
            T = as_processed_table[join_with]["name"]
            if raster_table:
                left_join_on += (
                    "\nON ST_Intersects("
                    + as_tables_dot
                    + rast_alias
                    + ", ST_PointFromText(FORMAT('POINT(%s %s)',"
                    " cast({T}.{x} as varchar), "
                    "cast({T}.{y} as varchar)),"
                    " 4326))\n".format(T=T, x=x, y=y)
                )

                # now Add the ST_Value for this point , rast value

                rast_value = (
                    "ST_Value("
                    + as_tables_dot
                    + rast_alias
                    + ", 1, ST_PointFromText(FORMAT('POINT(%s %s)', "
                    "cast({T}.{longitude} as varchar), "
                    "cast({T}.{latitude} as varchar)), "
                    "4326)) as feature_{ras}".format(
                        T=T, longitude=x, latitude=y, ras=rast_alias
                    )
                )
                # Add the value to final select statement
                rast_values.append(rast_value)
                all_fields += [rast_value]
            if vector_table:
                geovalue = (
                    "ST_PointFromText(FORMAT('POINT(%s %s)', "
                    "cast({T}.{longitude} as varchar), "
                    "cast({T}.{latitude} as varchar)),"
                    " 4326) ".format(T=T, longitude=x, latitude=y)
                )

                left_join += (
                    " \nON ST_Within({geovalue}, "
                    "{tablei_as}.{geomalias}) ".format(
                        T=T,
                        geovalue=geovalue,
                        tablei_as=as_tables,
                        geomalias=geom_alias,
                    )
                )
                # change the name of field to match the table
                new_geom_value = geovalue + " as feature_{geo}".format(geo=geom_alias)
                all_fields += [new_geom_value]
        if tabular_table and make_local_temp:
            # Create `LEFT JOIN` statements from non pivot tables
            _all_fields = ", ".join(str(e) for e in local_fields_used)
            _local_fields = ", ".join(str(e) for e in original_tabular_fields)
            left_join += (
                "\nLEFT OUTER JOIN  "
                "\n\t(SELECT  {all_flds} "
                "\nFROM (SELECT  {original_fields} "
                "\nFROM {table_j} "
                "\n{where_stm}) temp) "
                "{table_j_as} ".format(
                    all_flds=_all_fields,
                    original_fields=_local_fields,
                    table_j=table2join["table"],
                    where_stm=str(where_clause),
                    table_j_as=as_tables,
                )
            )
        elif tabular_table:
            left_join += (
                "\nLEFT OUTER JOIN "
                "\n\t(SELECT {fields_used} "
                "\n\tFROM {table_i} {where_clause}) AS {tablei_as} "
                "".format(
                    fields_used=", ".join(str(e) for e in local_fields_used),
                    table_i=table2join["table"],
                    where_clause=str(where_clause),
                    tablei_as=as_tables,
                )
            )

        # Create "ON" statement
        on_condition = "\nON "
        if tabular_table:
            # Process "ON" statements, having either similar
            # or different field/column names
            on_common_stmt = []
            if to_join["common_field"]:
                for item_field in to_join["common_field"]:
                    on_common_stmt += [
                        "{table_i}.{common_name}={table_j}.{common_name}".format(
                            table_i=as_processed_table[dataset.main_file["path"]][
                                "name"
                            ],
                            table_j=as_processed_table[table2join["table"]]["name"],
                            common_name=str(item_field),
                        )
                    ]

            # process non common fields
            temp_dict = to_join
            temp_dict.pop("common_field", True)

            # Two lists whose index each match the field to use
            # when creating the conditional statement
            # Use index of one to obtain the value of the other
            tab_field_index = list(temp_dict.keys())
            on_diff_stmt = []
            for num, items in enumerate(temp_dict[tab_field_index[0]]):
                new_on = "{tab_i}.{field_i}={tab_j}.{field_j}".format(
                    tab_i=as_processed_table[str(tab_field_index[0])]["name"],
                    # field_i=items,
                    field_i=temp_dict[tab_field_index[0]][num].lower(),
                    tab_j=as_processed_table[str(tab_field_index[1])]["name"],
                    field_j=temp_dict[tab_field_index[1]][num].lower(),
                )
                on_diff_stmt.append(new_on)

            all_on_stmts = on_diff_stmt + on_common_stmt

            on_condition += " AND ".join(str(etr) for etr in all_on_stmts)
            left_join_on += on_condition

        query_statement += left_join + left_join_on
        # Process the main file and create the query string
        # for all the required fields
        if "fields" in dataset.main_file:
            where_clause = ""
            if "lat_long" in dataset.main_file and dataset.main_file["lat_long"]:
                # ["latitude", "longitude"] [y,x]
                y = dataset.main_file["lat_long"][0]
                x = dataset.main_file["lat_long"][1]
                where_clause = (
                    "WHERE CAST({latitude} AS TEXT) NOT LIKE '%NULL%' "
                    "AND {latitude} IS NOT NULL "
                    "AND CAST({longitude} AS TEXT) NOT LIKE '%NULL%' "
                    "AND {longitude} IS NOT NULL "
                    "".format(latitude=y, longitude=x)
                )
                temp_fields = dataset.main_file["fields"]
                temp_fields_string = ", ".join(str(e) for e in temp_fields)
                pivot_query = (
                    "\nSELECT {all_flds} "
                    "\nINTO {res} "
                    "\nFROM (SELECT  {temp_fields_s}  "
                    "\nFROM {main_table}  "
                    "\n{where_stm} ) "
                    "{table_m} ".format(
                        all_flds=", ".join(str(e) for e in all_fields),
                        temp_fields_s=temp_fields_string,
                        main_table=dataset.main_file["path"],
                        res="{result_dbi}.{result_tablei}",
                        table_m=as_processed_table[main_table_path]["name"],
                        where_stm=where_clause,
                    )
                )
            else:
                pivot_query = (
                    "\nSELECT {all_fls} \ninto {res} "
                    "\nFROM {main_table} {where_stm} AS {table_m} "
                    "".format(
                        all_fls=", ".join(str(e) for e in all_fields),
                        main_table=dataset.main_file["path"],
                        res="{result_dbi}.{result_tablei}",
                        where_stm=where_clause,
                        table_m=as_processed_table[main_table_path]["name"],
                    )
                )

    return pivot_query + query_statement
