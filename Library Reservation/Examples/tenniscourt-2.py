from flask import Flask, flash, render_template, request
#from apscheduler.scheduler import Scheduler
import sqlite3 as sql
import atexit


app = Flask(__name__)
app.secret_key = "random string"

@app.route("/cancel")
def cancel_reservation():
    return render_template("cancel.html")

@app.route("/aftercancelling", methods=["POST", "GET"])
def after_cancelling():
    cancel_time = request.form.get('Available Times')
    cancel_court = request.form.get('Courts')
    cancel_name = request.form['name']
    cancel_location = request.form.get('Location')
    #get the selected values that make up the user's reservation that they want to cancel
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM tennisreservations WHERE name  = ? and court= ?  and times = ? and location =? ", [cancel_name, cancel_court, cancel_time, cancel_location])
    rows = cur.fetchall()
    if len(rows) == 0:
        flash("We did not find a matching reservation. Please check the values you have selected.")
    else:
        cur.execute("DELETE FROM tennisreservations WHERE name  = ? and court= ? and times = ? and location = ?", [cancel_name, cancel_court, cancel_time, cancel_location])
        con.commit()
        flash("You have successfully cancelled your reservation. Come to again to play!")
    return render_template("cancel.html")
    

@app.route("/")
def home():
    conn = sql.connect("database.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tennisreservations (name TEXT, location TEXT, court TEXT, times TEXT, booked_court_index INTEGER, booked_time_index INTEGER)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tennisquestions (useremail TEXT, usermessage TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tennisreviews (userreview TEXT)"
    )
    conn.close()
    return render_template("home.html")


@app.route("/enternew")
def new_reservation():
    return render_template("reservation.html")


@app.route("/reviews")
def view_reviews():
    return render_template("reviews.html")

@app.route('/savereviews', methods = ["POST"])
def save_reviews():
    if request.method == "POST":
        user_review = request.form["theuserreview"]
        conn = sql.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tennisreviews (userreview) VALUES (?)",
            (user_review,)
        )
        conn.commit()
        flash(
            "Thank you for submitting your review! Enjoy the app.")
        return render_template("reviews.html")



#@app.route("/help")
#def get_help():
    #return render_template("help.html")


@app.route("/savequestions", methods=["POST"])
def save_questions():
    if request.method == "POST":
        emailaddr = request.form["email"]
        usermessage = request.form["message"]
        conn = sql.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tennisquestions (useremail,usermessage) VALUES (?,?)",
            (emailaddr, usermessage),
        )
        conn.commit()
        flash(
            "Thank you for submitting your question. We will get back to you shortly!"
        )
        return render_template("help.html")


@app.route("/register", methods=["POST", "GET"])
def addrec():
    if request.method == "POST":
        try:
            name = request.form["name"]
            # school = request.form.get('School')
            select = request.form.get("timeslist")
            selected_value_times = str(select)  # just to see what select is
            times = ["9-11AM", "11-1PM", "1-3PM", "3-5PM", "5-7PM", "7-9PM"]
            locations = ["Dougherty Valley High School", "Central Park"]
            selected_location = str(request.form.get("locationlist"))
            # times = ['9-10AM', '10-11AM', '11-12PM', '12-1PM', '1-2PM', '2-3PM', '3-4PM', '4-5PM', '5-6PM', '6-7PM', '7-8PM', '8-9PM']
            time_index = str(times.index(selected_value_times))
            # now do the same but with the courts
            select_courts = request.form.get("courts")
            selected_value_courts = str(select_courts)  # just to see what select is
            courts = [
                "Court 1",
                "Court 2",
                "Court 3",
                "Court 4",
                "Court 5",
                "Court 6",
                "Court 7",
                "Court 8",
            ]
            court_index = str(courts.index(selected_value_courts))

            with sql.connect("database.db") as con:
                con.row_factory = sql.Row
                cur = con.cursor()
                #check if the name already exists in the DB   
                cur.execute("select * from tennisreservations where name= ?",[name])
                rows = cur.fetchall()
                if len(rows) != 0:
                    msg = ("Sorry, you already have a court reserved. You cannot reserve more than one court.")
                else:
                    cur.execute(
                    "INSERT INTO tennisreservations (name, location, court,times,booked_court_index, booked_time_index) VALUES (?,?,?,?,?, ?)",
                    (
                        name,
                        selected_location,
                        selected_value_courts,
                        selected_value_times,
                        court_index,
                        time_index,
                    ),
                    )
                    con.commit()
                    
                    msg = (
                        "Hi "
                        + name
                        + "! You have successfully reserved "
                        + selected_value_courts
                        + " at time "
                        + selected_value_times
                        + "."
                    )
        except:
           con.rollback()
           msg = "error in insert operation"
        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route("/list")
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute(
        "select name, location, court, times, booked_time_index, booked_court_index from tennisreservations"
    )

    rows = cur.fetchall()
    return render_template("list.html", rows=rows)


@app.route("/search", methods=["GET", "POST"])
def search():
    location = str(request.form.get("Location"))
    select = request.form.get("Available Times")
    selected_value_times = str(select)  # just to see what select is
    times = ["9-11AM", "11-1PM", "1-3PM", "3-5PM", "5-7PM", "7-9PM"]
    locations = ["Dougherty Valley High School", "Central Park"]
    # state = {'choice': selected_value_times}
    time_index = str(times.index(selected_value_times))
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    # testing that you are getting the right index value from the database
    cur.execute(
        "select booked_court_index from tennisreservations where booked_time_index=? and location=?",
        [time_index, location],
    )
    rows = cur.fetchall()
    # print (rows)

    times = ["9-11AM", "11-1PM", "1-3PM", "3-5PM", "5-7PM", "7-9PM"]
    courtForTime0list = [
        "Court 1",
        "Court 2",
        "Court 3",
        "Court 4",
        "Court 5",
        "Court 6",
        "Court 7",
        "Court 8",
    ]
    courtForTime1list = [
        "Court 1",
        "Court 2",
        "Court 3",
        "Court 4",
        "Court 5",
        "Court 6",
        "Court 7",
        "Court 8",
    ]
    courtForTime2list = [
        "Court 1",
        "Court 2",
        "Court 3",
        "Court 4",
        "Court 5",
        "Court 6",
        "Court 7",
        "Court 8",
    ]
    courtForTime3list = [
        "Court 1",
        "Court 2",
        "Court 3",
        "Court 4",
        "Court 5",
        "Court 6",
        "Court 7",
        "Court 8",
    ]
    courtForTime4list = [
        "Court 1",
        "Court 2",
        "Court 3",
        "Court 4",
        "Court 5",
        "Court 6",
        "Court 7",
        "Court 8",
    ]
    courtForTime5list = [
        "Court 1",
        "Court 2",
        "Court 3",
        "Court 4",
        "Court 5",
        "Court 6",
        "Court 7",
        "Court 8",
    ]

    courtTimeMasterList = []
    courtTimeMasterList.append(courtForTime0list)
    courtTimeMasterList.append(courtForTime1list)
    courtTimeMasterList.append(courtForTime2list)
    courtTimeMasterList.append(courtForTime3list)
    courtTimeMasterList.append(courtForTime4list)
    courtTimeMasterList.append(courtForTime5list)

    # court_index=7
    # string_booked_courts = " "
    list_courts_to_be_removed = []
    list_of_available_courts = []
    courtList = courtTimeMasterList[int(time_index)]

    updatedcourtlist = []

    for dbrow in rows:
        court_index = dbrow["booked_court_index"]
        list_courts_to_be_removed.append(court_index)

    for index in range(len(courtList)):
        if index in list_courts_to_be_removed:
            continue
        list_of_available_courts.append(courtList[index])
    if (len(list_of_available_courts)) == 0:
        return render_template("choosedifftime.html", state=selected_value_times)
    # courtList.pop(court_index)

    #

    # for value in list_courts_to_be_removed:
    #  string_court_index = str(value)
    # string_booked_courts = string_booked_courts + string_court_index
    # return string_booked_courts
    # return str(len(rows))

    # get the correct court list

    return render_template(
        "availablecourtsandname.html",
        courts=list_of_available_courts,
        state=selected_value_times,
        selected_location=location,
        timeslist=times,
        locationlist=locations,
    )

#cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
#cron.start()

#@cron.interval_schedule(hours=24)
#def clear_database():
 #   conn = sql.connect("database.db")
#    cur = conn.cursor()
 #   cur.execute(
 #           "DELETE FROM tennisreservations")
 #   conn.commit()
 #   print("Deleted reservations")

# Shutdown your cron thread if the web process is stopped
#atexit.register(lambda: cron.shutdown(wait=False))


if __name__ == "__main__":
    app.run(debug=True)

