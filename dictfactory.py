#The dict factory allows the SQL commands to return a dictionary
def dict_factory(cursor, row):
    #Empty dictionary
    d = {}
    #Iterate through column
    for idx, col in enumerate(cursor.description):
        #Add into dictionary
        d[col[0]] = row[idx]
    return d
