import sqlite3
import time


class RecordingDatabase:
    def __init__(self):
        self.mydb = sqlite3.connect("MotionInput.db", check_same_thread=False)
        self.mycursor = self.mydb.cursor()

        date = time.strftime("%Y%m%d", time.localtime())  # 20220101

        self.record_table_name = "Records_" + date
        self.gesture_table_name = "Gestures_" + date
        record = "CREATE TABLE IF NOT EXISTS " + self.record_table_name + " (frame_id INT, data TEXT, compress INT, PRIMARY KEY (frame_id));"
        gesture = "CREATE TABLE IF NOT EXISTS " + self.gesture_table_name + " (gesture_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, gesture_name VARCHAR(255), start INT, end INT, FOREIGN KEY (start) REFERENCES " + self.record_table_name + "(frame_id), FOREIGN KEY (end) REFERENCES " + self.record_table_name + "(frame_id));"
        self.mycursor.execute(record)
        self.mycursor.execute(gesture)

    def record(self, frame_id, data, compress=0):
        """
            :param int frame_id: The frame id
            :param str data: The landmark data json string
            :param int compress: how many frames compressed, 0 if not compressed
        """
        sql = "INSERT INTO " + self.record_table_name + " (frame_id, data,compress) VALUES (" + str(
            frame_id) + ", '" + data + "' , " + str(compress) + ")"
        self.mycursor.execute(sql)
        self.mydb.commit()  # commit the change to the database, DO NOT REMOVE

    def record_gesture(self, name, start, end):
        """
            :param str name: The name of a gesture
            :param int start: The starting frame id
            :param int end: The ending frame id
        """
        sql = "INSERT INTO " + self.gesture_table_name + " (gesture_name, start, end) VALUES ('" + name + "' , " + str(
            start) + ", " + str(end) + ")"
        # print(sql)
        self.mycursor.execute(sql)
        self.mydb.commit()  # commit the change to the database, DO NOT REMOVE

    def get_last_line_id(self):
        """
            return the id of the last landmark record, -1 if no values present
        """
        sql = "SELECT MAX(frame_id) FROM " + self.record_table_name
        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()

        if myresult[0][0] is not None:
            return myresult[0][0]
        else:
            return -1

    def get_data(self, date_list, gesture):
        # split the date_string by , if there is more than one day
        frame_sequence = []
        for date in date_list:
            # get all the start and end frame_id of the gesture
            sql = "SELECT start,end FROM " + "Gestures_" + date + " WHERE gesture_name = " + "'" + gesture + "'"
            self.mycursor.execute(sql)
            myresult = self.mycursor.fetchall()
            keyframe_id_list = myresult
            for id in keyframe_id_list:
                # get all the key frame data between start and end
                sql = "SELECT data,compress FROM " + "Records_" + date + " WHERE frame_id BETWEEN " + str(id[0]) + " AND " + str(id[1])
                self.mycursor.execute(sql)
                keyframe_list = self.mycursor.fetchall()
                counter = 1
                for data in keyframe_list:
                    frame_sequence.append(data[0])
                    if counter != len(keyframe_list):
                        for i in range(0, data[1]):
                            # fill sequence with the compress frame
                            frame_sequence.append(data[0])
                        counter = counter + 1
        return frame_sequence

    def close_db(self):
        self.mycursor.close()
        self.mydb.close()


if __name__ == "__main__":
    mysql = RecordingDatabase()
    # print(mysql.get_data("20220323","gun"))

