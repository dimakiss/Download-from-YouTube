import os,shutil,sqlite3


class History_db():
    def __init__(self):
        self.data=self.get_history_data_base()

    def get_history_data_base(self):
        path =os.path.expanduser('~')+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\"
        shutil.copyfile(path +"History",
                        path +"History1")

        # Read sqlite query results into a pandas DataFrame
        con = sqlite3.connect(path +"History1")
        c = con.cursor()
        c.execute("SELECT * FROM urls ORDER BY last_visit_time")
        data = c.fetchall()
        con.close()
        os.remove(path +"History1")
        return data
