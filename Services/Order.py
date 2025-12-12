from platformdirs import user_data_dir, user_config_dir, user_cache_dir
from pandas import DataFrame as Df

app_name = "MyAwesomeApp"
app_author = "MyCompany"

data_dir = user_data_dir(app_name, app_author)
config_dir = user_config_dir(app_name, app_author)
cache_dir = user_cache_dir(app_name, app_author)

class Order:
    class Package:
        pass
    class Log:
        pass