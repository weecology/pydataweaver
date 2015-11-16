engines = [
    "mysql",
    "postgres",
    "csv",
    "sqlite",
]  # "msaccess",  "download_only"

engine_module_list = [__import__("weaver.engines." + module, fromlist="engines")
                      for module in engines
                      ]

engine_list = [module.engine() for module in engine_module_list]
engines_no_password = {'csv'}
