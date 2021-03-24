import psycopg2
from sys import argv, stderr
from os import path


class Database():

    def __init__(self):
        self._connection = None

    def connect(self):
        try:
            self._connection = psycopg2.connect(host="ec2-54-159-175-113.compute-1.amazonaws.com",
                                                database="d27qk32tcn1bc",
                                                user="btpesghzoocreg",
                                                password="c35d066fbff924a2c15d6b2bbb9969078fd4c1cd60f1737dbdef7e717ee903f1")
        except Exception as e:
            print(f'{e}', file=stderr)

    def disconnect(self):
        self._connection.close()

    def reaction_submit(self, data):
        try:
            cursor = self._connection.cursor()

            postgres_insert_query = """INSERT INTO reactions (reaction, userID, dhall, time) VALUES (%s, %d, %s, %s)"""

            cursor.execute(postgres_insert_query, data)
            self._connection.commit()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception(
                'Failed to insert record into PostgreSQL table')

    def get_reactions(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT * FROM reactions WHERE reactions.dhall=?"
            cursor.execute(get_query, [dhall])
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get rows PostgreSQL table')

    def get_names(self, dhall):
        try:
            cursor = self._connection.cursor()
            get_query = "SELECT name FROM food WHERE food.dhall=?"
            cursor.execute(get_query, [dhall])
            ## name, ingredients, numRatings, numStars, description, url, dhall, lastServed
            return cursor.fetchall()
        except Exception as e:
            print(f'{e}', file=stderr)
            raise Exception('Failed to get rows PostgreSQL table')

    def get_food(self, name, ):
        try:
            cursor = self._connection.cursor()

            sql_command1 = "SELECT classes.courseid, classes.days, classes.starttime, classes.endtime, classes.bldg, classes.roomnum, crosslistings.dept, crosslistings.coursenum, courses.area, courses.title, courses.descrip, courses.prereqs FROM classes, crosslistings, courses WHERE classes.courseid = courses.courseid AND crosslistings.courseid = courses.courseid AND classid=? ORDER BY dept ASC, coursenum ASC"

            # fetching professors if any
            sql_command2 = "SELECT profs.profname FROM coursesprofs, profs WHERE coursesprofs.courseid=? AND coursesprofs.profid=profs.profid ORDER BY profname"

            cursor.execute(sql_command1, [class_id])

            results = {}
            row = cursor.fetchone()

            # If reg.py sends a "class details" query specifying a classid that does not exist in the database, then regserver.py must write a descriptive error message to its stderr and continue executing.
            # if classid does not exist, return an empty dictionary
            if row is None:
                return results

            firstrow = row
            courseid = str(row[0])
            results['courseid'] = courseid
            results['days'] = str(row[1])
            results['start'] = str(row[2])
            results['end'] = str(row[3])
            results['building'] = str(row[4])
            results['room'] = str(row[5])

            dept_num_list = []
            dept_num_list.append(str(row[6]) + " " + str(row[7]))
            row = cursor.fetchone()
            while row is not None:
                dept_num_list.append(str(row[6]) + " " + str(row[7]))
                row = cursor.fetchone()

            results['dept_num'] = dept_num_list
            results['area'] = str(firstrow[8])
            results['title'] = str(firstrow[9])
            results['desc'] = str(firstrow[10])
            results['prereq'] = str(firstrow[11])

            cursor.execute(sql_command2, [courseid])

            professors = []
            row = cursor.fetchone()
            while row is not None:
                professors.append(str(row[0]))
                row = cursor.fetchone()
            results['profs'] = professors
            cursor.close()
            return results
        except Exception as e:
            print(f'{argv[0]}: {e}', file=stderr)
            raise Exception(
                'A server error occurred. Please contact the system administrator.')
