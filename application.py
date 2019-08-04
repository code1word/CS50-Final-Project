import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///schmaker.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():

    username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])

    # See how many classes are in the user's trimester 1 schedule
    fcnt = db.execute("SELECT count(*) as fcntstar FROM course_schedule WHERE trimester_offered = :t", t='Trimester 1')
    if fcnt[0]["fcntstar"] != 0:
        trif = db.execute("SELECT course_name, meeting_pattern, gpa_weight FROM course_schedule WHERE username = :username AND trimester_offered=:t", username=username[0]["username"], t="Trimester 1")
    else:
        trif=[{'course_name':'', 'meeting_pattern':'', 'gpa_weight':'0'}]

    # See how many classes are in the user's trimester 2 schedule
    scnt = db.execute("SELECT count(*) as scntstar FROM course_schedule WHERE trimester_offered = :t", t='Trimester 2')
    if scnt[0]["scntstar"] != 0:
        tris = db.execute("SELECT course_name, meeting_pattern, gpa_weight FROM course_schedule WHERE username = :username AND trimester_offered=:t", username=username[0]["username"], t="Trimester 2")
    else:
        tris=[{'course_name':'', 'meeting_pattern':'', 'gpa_weight':'0'}]

    # See how many classes are in the user's trimester 3 schedule
    tcnt = db.execute("SELECT count(*) as tcntstar FROM course_schedule WHERE trimester_offered = :t", t='Trimester 3')
    if tcnt[0]["tcntstar"] != 0:
        trit = db.execute("SELECT course_name, meeting_pattern, gpa_weight FROM course_schedule WHERE username = :username AND trimester_offered=:t", username=username[0]["username"], t="Trimester 3")
    else:
        trit=[{'course_name':'', 'meeting_pattern':'', 'gpa_weight':'0'}]

    # GPA Calculator
    ffcnt = db.execute("SELECT count(*) as ffcntstar FROM course_schedule WHERE trimester_offered = :t", t='Trimester 1')
    if ffcnt[0]["ffcntstar"] != 0:
        triff = db.execute("SELECT course_name, meeting_pattern, gpa_weight FROM course_schedule WHERE substr(course_name, 0, 4) != 'SEM' AND substr(course_name, 0, 3) != 'PA' AND substr(course_name, 0, 3) != 'RE' AND username = :username AND trimester_offered=:t", username=username[0]["username"], t="Trimester 1")
    else:
        triff=[{'course_name':'', 'meeting_pattern':'', 'gpa_weight':'0'}]
    add1 = 0
    if len(triff)>0:
        for i in range(len(triff)):
            add1 += float(triff[i]["gpa_weight"])
        un1 = (add1)/(len(triff))
        avg1 = round(un1, 4)
    else:
        avg1 = "TBD"
    sscnt = db.execute("SELECT count(*) as sscntstar FROM course_schedule WHERE trimester_offered = :t", t='Trimester 2')
    if sscnt[0]["sscntstar"] != 0:
        triss = db.execute("SELECT course_name, meeting_pattern, gpa_weight FROM course_schedule WHERE substr(course_name, 0, 4) != 'SEM' AND substr(course_name, 0, 3) != 'PA' AND substr(course_name, 0, 3) != 'RE' AND username = :username AND trimester_offered=:t", username=username[0]["username"], t="Trimester 2")
    else:
        triss=[{'course_name':'', 'meeting_pattern':'', 'gpa_weight':'0'}]
    add2 = 0
    if len(triss)>0:
        for i in range(len(triss)):
            add2 += float(triss[i]["gpa_weight"])
        un2 = (add2)/(len(triss))
        avg2 = round(un2, 4)
    else:
        avg2 = "TBD"
    ttcnt = db.execute("SELECT count(*) as ttcntstar FROM course_schedule WHERE trimester_offered = :t", t='Trimester 3')
    if ttcnt[0]["ttcntstar"] != 0:
        tritt = db.execute("SELECT course_name, meeting_pattern, gpa_weight FROM course_schedule WHERE substr(course_name, 0, 4) != 'SEM' AND substr(course_name, 0, 3) != 'PA' AND substr(course_name, 0, 3) != 'RE' AND username = :username AND trimester_offered=:t", username=username[0]["username"], t="Trimester 3")
    else:
        tritt=[{'course_name':'', 'meeting_pattern':'', 'gpa_weight':'0'}]
    add3 = 0
    if len(tritt)>0:
        for i in range(len(tritt)):
            add3 += float(tritt[i]["gpa_weight"])
        un3 = (add3)/(len(tritt))
        avg3=round(un3, 4)
    else:
        avg3 = "TBD"
    if avg1 == 0.0:
        avg1 = "TBD"
    if avg2 == 0.0:
        avg2 = "TBD"
    if avg3 == 0.0:
        avg3 = "TBD"
    if avg1 != "TBD" and avg2 != "TBD" and avg3 != "TBD":
        unrounded = (add1 + add2 + add3)/(len(triff)+len(triss)+len(tritt))
        cumgpa = round(unrounded, 4)
    else:
        cumgpa = "TBD"
    return render_template("index.html", cumgpa=cumgpa, avg1=avg1, avg2=avg2, avg3=avg3, trif=trif, tris=tris, trit=trit, username=username[0]["username"])

@app.route("/schedule")
@login_required
def schedule():
    return render_template("schedule.html")

@app.route("/info", methods=["GET", "POST"])
@login_required
def display():

    # Display a list of all courses to the user
    courses = db.execute("SELECT DISTINCT course_name FROM course_info")
    selected_course = str(request.form.get("user_selected_course"))

    # Make sure the user selects a class
    if selected_course != "None":
        cnt = db.execute("SELECT count(*) as cntstar FROM course_info WHERE course_name = :name", name=selected_course)
        if cnt[0]["cntstar"] != 0:
            displayed_courses = db.execute("SELECT DISTINCT course_name, trimester_offered, gpa_weight, course_code, meeting_pattern FROM course_info WHERE course_name = :name", name=selected_course)
            return render_template("info.html", displayed_courses=displayed_courses, trimester_offered=displayed_courses[0]["trimester_offered"], courses=courses, selected_course=displayed_courses[0]["course_name"], meeting_pattern=displayed_courses[0]["meeting_pattern"], gpa_weight=displayed_courses[0]["gpa_weight"], course_code=displayed_courses[0]["course_code"])
        else:
            return redirect("/info")
    else:
        return render_template("info.html", courses=courses)

@app.route("/submit_meeting_pattern", methods=["GET", "POST"])
@login_required
def action():
    # Get the user's input
    second_input_string = request.form.get("second_input")

    # Make sure it's not blank
    if second_input_string != "":
        data = second_input_string.split(', ')
        username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
        check_exists = db.execute("SELECT COUNT (*) AS cnt1 FROM course_schedule WHERE course_name=:course_name AND username=:username", username=username[0]["username"], course_name=data[0])

        # Make sure they haven't already added it
        if check_exists[0]["cnt1"] == 0:
            schedule_courses = db.execute("INSERT INTO course_schedule(username, course_name, course_code, meeting_pattern, trimester_offered, gpa_weight) VALUES (:username, :course_name, :course_code, :meeting_pattern, :trimester_offered, :gpa_weight)", username=username[0]["username"], course_name=data[0], course_code=data[1], meeting_pattern=data[2], trimester_offered=data[3], gpa_weight=data[4])
        else:
            flash("Course has not been added since it already exists in schedule")
            return redirect("/info")
        return redirect("/info")
    else:
        return redirect("/info")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
    c3nt = db.execute("SELECT count(*) as cnt3star FROM course_schedule WHERE username=:username", username=username[0]["username"])

    # Display a blank row if there are no courses in schedule
    if c3nt[0]["cnt3star"] < 1:
        displayed_courses=[{'course_name':'', 'trimester_offered':'', 'gpa_weight':'', 'course_code':'', 'meeting_pattern':''}]
    else:
        displayed_courses = db.execute("SELECT course_name, trimester_offered, gpa_weight, course_code, meeting_pattern FROM course_schedule WHERE username = :username ORDER BY trimester_offered ASC", username=username[0]["username"])
    return render_template("delete.html", displayed_courses=displayed_courses, meeting_pattern=displayed_courses[0]["meeting_pattern"], course_name=displayed_courses[0]["course_name"], course_code=displayed_courses[0]["course_code"], trimester_offered=displayed_courses[0]["trimester_offered"], gpa_weight=displayed_courses[0]["gpa_weight"])

@app.route("/delete_classes", methods=["GET", "POST"])
@login_required
def delete_classes():
    username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
    third_input_string = request.form.get("third_input")

    # Make sure they selected a class to be deleted
    if third_input_string != "None":
        data = third_input_string.split(', ')
        delete_courses = db.execute("DELETE FROM course_schedule WHERE course_name=:name AND username=:username", username=username[0]["username"], name=data[0])
        return redirect("/delete")
    else:
        return redirect("/delete")

@app.route("/delete_all_classes", methods=["GET", "POST"])
@login_required
def delete_all_classes():
    username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
    delete_courses = db.execute("DELETE FROM course_schedule WHERE username=:username", username=username[0]["username"])
    return redirect("/delete")

@app.route("/display_schedule1", methods=["GET", "POST"])
@login_required
def display_schedule1():
    username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
    scheduled_courses = db.execute("SELECT substr(course_name, 0, 6) AS five_chars, meeting_pattern FROM course_schedule WHERE username=:username AND trimester_offered=:tri ORDER BY 2", tri="Trimester 1", username=username[0]["username"])

    banned = ["BI446", "CH446", "IE405", "MU360", "MU370", "PH446", "JA305", "BI442", "BI448", "CH442", "CH448", "EE442", "MU362", "MU372", "JA307", "PH442", "PH448", "BI444", "CH444",
        "EE444", "IE406", "MU364", "MU374", "PH444"]

    elist = []

    for i in range(len(scheduled_courses)):
        if any(scheduled_courses[i]["five_chars"] == thing for thing in banned):
            elist.append("B")
    if len(elist) > 0:
        aemptylist = []
        bemptylist = []
        cemptylist = []
        demptylist = []
        eemptylist = []
        femptylist = []
        gemptylist = []
        hemptylist = []
        iemptylist = []
    else:
        # A block conflict checker
        a_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'A%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if a_course_list[0]["meeting_pattern"] != None:
            aemptylist = list(a_course_list[0]["meeting_pattern"])
        else:
            aemptylist = []

        # B block conflict checker
        b_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'B%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if b_course_list[0]["meeting_pattern"] != None:
            bemptylist = list(b_course_list[0]["meeting_pattern"])
        else:
            bemptylist = []

        # C block conflict checker
        c_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'C%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if c_course_list[0]["meeting_pattern"] != None:
            cemptylist = list(c_course_list[0]["meeting_pattern"])
        else:
            cemptylist = []

        # D block conflict checker
        d_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'D%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if d_course_list[0]["meeting_pattern"] != None:
            demptylist = list(d_course_list[0]["meeting_pattern"])
        else:
            demptylist = []

        # E block conflict checker
        e_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'E%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if e_course_list[0]["meeting_pattern"] != None:
            eemptylist = list(e_course_list[0]["meeting_pattern"])
        else:
            eemptylist = []

        # F block conflict checker
        f_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'F%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if f_course_list[0]["meeting_pattern"] != None:
            femptylist = list(f_course_list[0]["meeting_pattern"])
        else:
            femptylist = []

        # G block conflict checker
        g_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'G%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if g_course_list[0]["meeting_pattern"] != None:
            gemptylist = list(g_course_list[0]["meeting_pattern"])
        else:
            gemptylist = []

        # H block conflict checker
        h_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'H%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if h_course_list[0]["meeting_pattern"] != None:
            hemptylist = list(h_course_list[0]["meeting_pattern"])
        else:
            hemptylist = []

        # I block conflict checker
        i_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'I%' AND username=:username AND trimester_offered=:tri", tri="Trimester 1", username=username[0]["username"])
        if i_course_list[0]["meeting_pattern"] != None:
            iemptylist = list(i_course_list[0]["meeting_pattern"])
        else:
            iemptylist = []

    # Notify the user if there is a conflict. If not, generate schedule
    if aemptylist.count('1') > 1 or aemptylist.count('2') > 1 or aemptylist.count('3') > 1 or aemptylist.count('4') > 1 or aemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block A")
        return redirect("/schedule")
    elif bemptylist.count('1') > 1 or bemptylist.count('2') > 1 or bemptylist.count('3') > 1 or bemptylist.count('4') > 1 or bemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block B")
        return redirect("/schedule")
    elif cemptylist.count('1') > 1 or cemptylist.count('2') > 1 or cemptylist.count('3') > 1 or cemptylist.count('4') > 1 or cemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block C")
        return redirect("/schedule")
    elif demptylist.count('1') > 1 or demptylist.count('2') > 1 or demptylist.count('3') > 1 or demptylist.count('4') > 1 or demptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block D")
        return redirect("/schedule")
    elif eemptylist.count('1') > 1 or eemptylist.count('2') > 1 or eemptylist.count('3') > 1 or eemptylist.count('4') > 1 or eemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block E")
        return redirect("/schedule")
    elif femptylist.count('1') > 1 or femptylist.count('2') > 1 or femptylist.count('3') > 1 or femptylist.count('4') > 1 or femptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block F")
        return redirect("/schedule")
    elif gemptylist.count('1') > 1 or gemptylist.count('2') > 1 or gemptylist.count('3') > 1 or gemptylist.count('4') > 1 or gemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block G")
        return redirect("/schedule")
    elif hemptylist.count('1') > 1 or hemptylist.count('2') > 1 or hemptylist.count('3') > 1 or hemptylist.count('4') > 1 or hemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block H")
        return redirect("/schedule")
    elif iemptylist.count('1') > 1 or iemptylist.count('2') > 1 or iemptylist.count('3') > 1 or iemptylist.count('4') > 1 or iemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block I")
        return redirect("/schedule")
    else:
        A1=""
        A2=""
        A3=""
        A4=""
        A5=""
        Alab=""
        B1=""
        B2=""
        B3=""
        B4=""
        B5=""
        Blab=""
        C1=""
        C2=""
        C3=""
        C4=""
        C5=""
        Clab=""
        D1=""
        D2=""
        D3=""
        D4=""
        D5=""
        Dlab=""
        E1=""
        E2=""
        E3=""
        E4=""
        E5=""
        Elab=""
        F1=""
        F2=""
        F3=""
        F4=""
        F5=""
        Flab=""
        G1=""
        G2=""
        G3=""
        G4=""
        G5=""
        Glab=""
        H1=""
        H2=""
        H3=""
        H4=""
        I1=""
        I2=""
        I3=""
        I4=""

        for thing in scheduled_courses:
            cc = thing["five_chars"]
            mp = thing["meeting_pattern"]

            # The following are some of the exceptions to the normal meeting pattern behavior

            # Japanese AH case
            if mp[0:1] == 'A' and 'H' in mp:
                hindex = mp.index('H')
                aportion = mp[0:hindex]
                hportion = mp[hindex:]

                if "1" in aportion:
                    A1=cc
                if "2" in aportion:
                    A2=cc
                if "3" in aportion:
                    A3=cc
                if "4" in aportion:
                    A4=cc
                if "5" in aportion:
                    A5=cc
                if "L" in aportion:
                    Alab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Japanese BH case
            if mp[0:1] == 'B' and 'H' in mp:
                hindex = mp.index('H')
                bportion = mp[0:hindex]
                hportion = mp[hindex:]

                if "1" in bportion:
                    B1=cc
                if "2" in bportion:
                    B2=cc
                if "3" in bportion:
                    B3=cc
                if "4" in bportion:
                    B4=cc
                if "5" in bportion:
                    B5=cc
                if "L" in bportion:
                    Blab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Orchestra and WE HC case
            if mp[0:1] == 'H' and 'C' in mp:
                cindex = mp.index('C')
                hportion = mp[0:cindex]
                cportion = mp[cindex:]

                if "1" in cportion:
                    C1=cc
                if "2" in cportion:
                    C2=cc
                if "3" in cportion:
                    C3=cc
                if "4" in cportion:
                    C4=cc
                if "5" in cportion:
                    C5=cc
                if "L" in cportion:
                    Clab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Orchestra and WE HF case
            if mp[0:1] == 'H' and 'F' in mp:
                findex = mp.index('F')
                hportion = mp[0:findex]
                fportion = mp[findex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Mentorship FEG case
            if mp[0:1] == 'F' and 'E' in mp and 'G' in mp:
                eindex = mp.index('E')
                gindex = mp.index('G')
                fportion = mp[0:eindex]
                eportion = mp[eindex:gindex]
                gportion = mp[gindex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in eportion:
                    E1=cc
                if "2" in eportion:
                    E2=cc
                if "3" in eportion:
                    E3=cc
                if "4" in eportion:
                    E4=cc
                if "5" in eportion:
                    E5=cc
                if "L" in eportion:
                    Elab=cc
                if "1" in gportion:
                    G1=cc
                if "2" in gportion:
                    G2=cc
                if "3" in gportion:
                    G3=cc
                if "4" in gportion:
                    G4=cc
                if "5" in gportion:
                    G5=cc
                if "L" in gportion:
                    Glab=cc

            # Research FG case
            if mp[0:1] == 'F' and 'G' in mp:
                gindex = mp.index('G')
                fportion = mp[0:gindex]
                gportion = mp[gindex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in gportion:
                    G1=cc
                if "2" in gportion:
                    G2=cc
                if "3" in gportion:
                    G3=cc
                if "4" in gportion:
                    G4=cc
                if "5" in gportion:
                    G5=cc
                if "L" in gportion:
                    Glab=cc

            # The regular A case
            if mp[0:1] == 'A' and 'H' not in mp:
                if "1" in mp:
                    A1=cc
                if "2" in mp:
                    A2=cc
                if "3" in mp:
                    A3=cc
                if "4" in mp:
                    A4=cc
                if "5" in mp:
                    A5=cc
                if "L" in mp:
                    Alab=cc

            # The regular B case
            if mp[0:1] == 'B' and 'H' not in mp:
                if "1" in mp:
                    B1=cc
                if "2" in mp:
                    B2=cc
                if "3" in mp:
                    B3=cc
                if "4" in mp:
                    B4=cc
                if "5" in mp:
                    B5=cc
                if "L" in mp:
                    Blab=cc

            # The regular C case
            if mp[0:1] == 'C' and 'H' not in mp:
                if "1" in mp:
                    C1=cc
                if "2" in mp:
                    C2=cc
                if "3" in mp:
                    C3=cc
                if "4" in mp:
                    C4=cc
                if "5" in mp:
                    C5=cc
                if "L" in mp:
                    Clab=cc

            # The regular D case
            if mp[0:1] == 'D':
                if "1" in mp:
                    D1=cc
                if "2" in mp:
                    D2=cc
                if "3" in mp:
                    D3=cc
                if "4" in mp:
                    D4=cc
                if "5" in mp:
                    D5=cc
                if "L" in mp:
                    Dlab=cc

            # The regular E case
            if mp[0:1] == 'E' and 'F' not in mp and 'G' not in mp:
                if "1" in mp:
                    E1=cc
                if "2" in mp:
                    E2=cc
                if "3" in mp:
                    E3=cc
                if "4" in mp:
                    E4=cc
                if "5" in mp:
                    E5=cc
                if "L" in mp:
                    Elab=cc

            # The regular F case
            if mp[0:1] == 'F' and 'G' not in mp and 'E' not in mp and 'H' not in mp:
                if "1" in mp:
                    F1=cc
                if "2" in mp:
                    F2=cc
                if "3" in mp:
                    F3=cc
                if "4" in mp:
                    F4=cc
                if "5" in mp:
                    F5=cc
                if "L" in mp:
                    Flab=cc

            # The regular G case
            if mp[0:1] == 'G' and 'E' not in mp and 'F' not in mp:
                if "1" in mp:
                    G1=cc
                if "2" in mp:
                    G2=cc
                if "3" in mp:
                    G3=cc
                if "4" in mp:
                    G4=cc
                if "5" in mp:
                    G5=cc
                if "L" in mp:
                    Glab=cc

            # The regular H case
            if mp[0:1] == 'H' and 'A' not in mp and 'B' not in mp and 'C' not in mp and 'F' not in mp:
                if "1" in mp:
                    H1=cc
                if "2" in mp:
                    H2=cc
                if "3" in mp:
                    H3=cc
                if "4" in mp:
                    H4=cc

            # The regular I case
            if mp[0:1] == 'I':
                if "1" in mp:
                    I1=cc
                if "2" in mp:
                    I2=cc
                if "3" in mp:
                    I3=cc
                if "4" in mp:
                    I4=cc
        return render_template("schedule.html", var="1", A1=A1, A2=A2, A3=A3, A4=A4, A5=A5, Alab=Alab, B1=B1, B2=B2, B3=B3, B4=B4, B5=B5, Blab=Blab, C1=C1, C2=C2, C3=C3, C4=C4, C5=C5, Clab=Clab, D1=D1, D2=D2, D3=D3, D4=D4, D5=D5, Dlab=Dlab, E1=E1, E2=E2, E3=E3, E4=E4, E5=E5, Elab=Elab, F1=F1, F2=F2, F3=F3, F4=F4, F5=F5, Flab=Flab, G1=G1, G2=G2, G3=G3, G4=G4, G5=G5, Glab=Glab, H1=H1, H2=H2, H3=H3, H4=H4, I1=I1, I2=I2, I3=I3, I4=I4)

@app.route("/display_schedule2", methods=["GET", "POST"])
@login_required
def display_schedule2():
    username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
    scheduled_courses = db.execute("SELECT substr(course_name, 0, 6) AS five_chars, meeting_pattern FROM course_schedule WHERE username=:username AND trimester_offered=:tri ORDER BY 2", tri="Trimester 2", username=username[0]["username"])
    banned = ["BI446", "CH446", "IE405", "MU360", "MU370", "PH446", "JA305", "BI442", "BI448", "CH442", "CH448", "EE442", "MU362", "MU372", "JA307", "PH442", "PH448", "BI444", "CH444",
        "EE444", "IE406", "MU364", "MU374", "PH444"]
    elist = []
    for i in range(len(scheduled_courses)):
        if any(scheduled_courses[i]["five_chars"] == thing for thing in banned):
            elist.append("B")
    if len(elist) > 0:
        aemptylist = []
        bemptylist = []
        cemptylist = []
        demptylist = []
        eemptylist = []
        femptylist = []
        gemptylist = []
        hemptylist = []
        iemptylist = []
    else:
        a_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'A%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if a_course_list[0]["meeting_pattern"] != None:
            aemptylist = list(a_course_list[0]["meeting_pattern"])
        else:
            aemptylist = []
        b_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'B%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if b_course_list[0]["meeting_pattern"] != None:
            bemptylist = list(b_course_list[0]["meeting_pattern"])
        else:
            bemptylist = []
        c_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'C%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if c_course_list[0]["meeting_pattern"] != None:
            cemptylist = list(c_course_list[0]["meeting_pattern"])
        else:
            cemptylist = []
        d_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'D%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if d_course_list[0]["meeting_pattern"] != None:
            demptylist = list(d_course_list[0]["meeting_pattern"])
        else:
            demptylist = []
        e_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'E%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if e_course_list[0]["meeting_pattern"] != None:
            eemptylist = list(e_course_list[0]["meeting_pattern"])
        else:
            eemptylist = []
        f_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'F%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if f_course_list[0]["meeting_pattern"] != None:
            femptylist = list(f_course_list[0]["meeting_pattern"])
        else:
            femptylist = []
        g_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'G%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if g_course_list[0]["meeting_pattern"] != None:
            gemptylist = list(g_course_list[0]["meeting_pattern"])
        else:
            gemptylist = []
        h_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'H%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if h_course_list[0]["meeting_pattern"] != None:
            hemptylist = list(h_course_list[0]["meeting_pattern"])
        else:
            hemptylist = []
        i_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'I%' AND username=:username AND trimester_offered=:tri", tri="Trimester 2", username=username[0]["username"])
        if i_course_list[0]["meeting_pattern"] != None:
            iemptylist = list(i_course_list[0]["meeting_pattern"])
        else:
            iemptylist = []
    if aemptylist.count('1') > 1 or aemptylist.count('2') > 1 or aemptylist.count('3') > 1 or aemptylist.count('4') > 1 or aemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block A")
        return redirect("/schedule")
    elif bemptylist.count('1') > 1 or bemptylist.count('2') > 1 or bemptylist.count('3') > 1 or bemptylist.count('4') > 1 or bemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block B")
        return redirect("/schedule")
    elif cemptylist.count('1') > 1 or cemptylist.count('2') > 1 or cemptylist.count('3') > 1 or cemptylist.count('4') > 1 or cemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block C")
        return redirect("/schedule")
    elif demptylist.count('1') > 1 or demptylist.count('2') > 1 or demptylist.count('3') > 1 or demptylist.count('4') > 1 or demptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block D")
        return redirect("/schedule")
    elif eemptylist.count('1') > 1 or eemptylist.count('2') > 1 or eemptylist.count('3') > 1 or eemptylist.count('4') > 1 or eemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block E")
        return redirect("/schedule")
    elif femptylist.count('1') > 1 or femptylist.count('2') > 1 or femptylist.count('3') > 1 or femptylist.count('4') > 1 or femptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block F")
        return redirect("/schedule")
    elif gemptylist.count('1') > 1 or gemptylist.count('2') > 1 or gemptylist.count('3') > 1 or gemptylist.count('4') > 1 or gemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block G")
        return redirect("/schedule")
    elif hemptylist.count('1') > 1 or hemptylist.count('2') > 1 or hemptylist.count('3') > 1 or hemptylist.count('4') > 1 or hemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block H")
        return redirect("/schedule")
    elif iemptylist.count('1') > 1 or iemptylist.count('2') > 1 or iemptylist.count('3') > 1 or iemptylist.count('4') > 1 or iemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block I")
        return redirect("/schedule")
    else:
        A1=""
        A2=""
        A3=""
        A4=""
        A5=""
        Alab=""
        B1=""
        B2=""
        B3=""
        B4=""
        B5=""
        Blab=""
        C1=""
        C2=""
        C3=""
        C4=""
        C5=""
        Clab=""
        D1=""
        D2=""
        D3=""
        D4=""
        D5=""
        Dlab=""
        E1=""
        E2=""
        E3=""
        E4=""
        E5=""
        Elab=""
        F1=""
        F2=""
        F3=""
        F4=""
        F5=""
        Flab=""
        G1=""
        G2=""
        G3=""
        G4=""
        G5=""
        Glab=""
        H1=""
        H2=""
        H3=""
        H4=""
        I1=""
        I2=""
        I3=""
        I4=""

        for thing in scheduled_courses:
            cc = thing["five_chars"]
            mp = thing["meeting_pattern"]

            # The following are some of the exceptions to the normal meeting pattern behavior

            # Japanese AH case
            if mp[0:1] == 'A' and 'H' in mp:
                hindex = mp.index('H')
                aportion = mp[0:hindex]
                hportion = mp[hindex:]

                if "1" in aportion:
                    A1=cc
                if "2" in aportion:
                    A2=cc
                if "3" in aportion:
                    A3=cc
                if "4" in aportion:
                    A4=cc
                if "5" in aportion:
                    A5=cc
                if "L" in aportion:
                    Alab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Japanese BH case
            if mp[0:1] == 'B' and 'H' in mp:
                hindex = mp.index('H')
                bportion = mp[0:hindex]
                hportion = mp[hindex:]

                if "1" in bportion:
                    B1=cc
                if "2" in bportion:
                    B2=cc
                if "3" in bportion:
                    B3=cc
                if "4" in bportion:
                    B4=cc
                if "5" in bportion:
                    B5=cc
                if "L" in bportion:
                    Blab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Orchestra and WE HC case
            if mp[0:1] == 'H' and 'C' in mp:
                cindex = mp.index('C')
                hportion = mp[0:cindex]
                cportion = mp[cindex:]

                if "1" in cportion:
                    C1=cc
                if "2" in cportion:
                    C2=cc
                if "3" in cportion:
                    C3=cc
                if "4" in cportion:
                    C4=cc
                if "5" in cportion:
                    C5=cc
                if "L" in cportion:
                    Clab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Orchestra and WE HF case
            if mp[0:1] == 'H' and 'F' in mp:
                findex = mp.index('F')
                hportion = mp[0:findex]
                fportion = mp[findex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Mentorship FEG case
            if mp[0:1] == 'F' and 'E' in mp and 'G' in mp:
                eindex = mp.index('E')
                gindex = mp.index('G')
                fportion = mp[0:eindex]
                eportion = mp[eindex:gindex]
                gportion = mp[gindex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in eportion:
                    E1=cc
                if "2" in eportion:
                    E2=cc
                if "3" in eportion:
                    E3=cc
                if "4" in eportion:
                    E4=cc
                if "5" in eportion:
                    E5=cc
                if "L" in eportion:
                    Elab=cc
                if "1" in gportion:
                    G1=cc
                if "2" in gportion:
                    G2=cc
                if "3" in gportion:
                    G3=cc
                if "4" in gportion:
                    G4=cc
                if "5" in gportion:
                    G5=cc
                if "L" in gportion:
                    Glab=cc

            # Research FG case
            if mp[0:1] == 'F' and 'G' in mp:
                gindex = mp.index('G')
                fportion = mp[0:gindex]
                gportion = mp[gindex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in gportion:
                    G1=cc
                if "2" in gportion:
                    G2=cc
                if "3" in gportion:
                    G3=cc
                if "4" in gportion:
                    G4=cc
                if "5" in gportion:
                    G5=cc
                if "L" in gportion:
                    Glab=cc

            # The regular A case
            if mp[0:1] == 'A' and 'H' not in mp:
                if "1" in mp:
                    A1=cc
                if "2" in mp:
                    A2=cc
                if "3" in mp:
                    A3=cc
                if "4" in mp:
                    A4=cc
                if "5" in mp:
                    A5=cc
                if "L" in mp:
                    Alab=cc

            # The regular B case
            if mp[0:1] == 'B' and 'H' not in mp:
                if "1" in mp:
                    B1=cc
                if "2" in mp:
                    B2=cc
                if "3" in mp:
                    B3=cc
                if "4" in mp:
                    B4=cc
                if "5" in mp:
                    B5=cc
                if "L" in mp:
                    Blab=cc

            # The regular C case
            if mp[0:1] == 'C' and 'H' not in mp:
                if "1" in mp:
                    C1=cc
                if "2" in mp:
                    C2=cc
                if "3" in mp:
                    C3=cc
                if "4" in mp:
                    C4=cc
                if "5" in mp:
                    C5=cc
                if "L" in mp:
                    Clab=cc

            # The regular D case
            if mp[0:1] == 'D':
                if "1" in mp:
                    D1=cc
                if "2" in mp:
                    D2=cc
                if "3" in mp:
                    D3=cc
                if "4" in mp:
                    D4=cc
                if "5" in mp:
                    D5=cc
                if "L" in mp:
                    Dlab=cc

            # The regular E case
            if mp[0:1] == 'E' and 'F' not in mp and 'G' not in mp:
                if "1" in mp:
                    E1=cc
                if "2" in mp:
                    E2=cc
                if "3" in mp:
                    E3=cc
                if "4" in mp:
                    E4=cc
                if "5" in mp:
                    E5=cc
                if "L" in mp:
                    Elab=cc

            # The regular F case
            if mp[0:1] == 'F' and 'G' not in mp and 'E' not in mp and 'H' not in mp:
                if "1" in mp:
                    F1=cc
                if "2" in mp:
                    F2=cc
                if "3" in mp:
                    F3=cc
                if "4" in mp:
                    F4=cc
                if "5" in mp:
                    F5=cc
                if "L" in mp:
                    Flab=cc

            # The regular G case
            if mp[0:1] == 'G' and 'E' not in mp and 'F' not in mp:
                if "1" in mp:
                    G1=cc
                if "2" in mp:
                    G2=cc
                if "3" in mp:
                    G3=cc
                if "4" in mp:
                    G4=cc
                if "5" in mp:
                    G5=cc
                if "L" in mp:
                    Glab=cc

            # The regular H case
            if mp[0:1] == 'H' and 'A' not in mp and 'B' not in mp and 'C' not in mp and 'F' not in mp:
                if "1" in mp:
                    H1=cc
                if "2" in mp:
                    H2=cc
                if "3" in mp:
                    H3=cc
                if "4" in mp:
                    H4=cc

            # The regular I case
            if mp[0:1] == 'I':
                if "1" in mp:
                    I1=cc
                if "2" in mp:
                    I2=cc
                if "3" in mp:
                    I3=cc
                if "4" in mp:
                    I4=cc
        return render_template("schedule.html", var="2", A1=A1, A2=A2, A3=A3, A4=A4, A5=A5, Alab=Alab, B1=B1, B2=B2, B3=B3, B4=B4, B5=B5, Blab=Blab, C1=C1, C2=C2, C3=C3, C4=C4, C5=C5, Clab=Clab, D1=D1, D2=D2, D3=D3, D4=D4, D5=D5, Dlab=Dlab, E1=E1, E2=E2, E3=E3, E4=E4, E5=E5, Elab=Elab, F1=F1, F2=F2, F3=F3, F4=F4, F5=F5, Flab=Flab, G1=G1, G2=G2, G3=G3, G4=G4, G5=G5, Glab=Glab, H1=H1, H2=H2, H3=H3, H4=H4, I1=I1, I2=I2, I3=I3, I4=I4)

@app.route("/display_schedule3", methods=["GET", "POST"])
@login_required
def display_schedule3():
    username = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
    scheduled_courses = db.execute("SELECT substr(course_name, 0, 6) AS five_chars, meeting_pattern FROM course_schedule WHERE username=:username AND trimester_offered=:tri ORDER BY 2", tri="Trimester 3", username=username[0]["username"])
    banned = ["BI446", "CH446", "IE405", "MU360", "MU370", "PH446", "JA305", "BI442", "BI448", "CH442", "CH448", "EE442", "MU362", "MU372", "JA307", "PH442", "PH448", "BI444", "CH444",
        "EE444", "IE406", "MU364", "MU374", "PH444"]
    elist = []
    for i in range(len(scheduled_courses)):
        if any(scheduled_courses[i]["five_chars"] == thing for thing in banned):
            elist.append("B")
    if len(elist) > 0:
        aemptylist = []
        bemptylist = []
        cemptylist = []
        demptylist = []
        eemptylist = []
        femptylist = []
        gemptylist = []
        hemptylist = []
        iemptylist = []
    else:
        a_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'A%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if a_course_list[0]["meeting_pattern"] != None:
            aemptylist = list(a_course_list[0]["meeting_pattern"])
        else:
            aemptylist = []
        b_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'B%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if b_course_list[0]["meeting_pattern"] != None:
            bemptylist = list(b_course_list[0]["meeting_pattern"])
        else:
            bemptylist = []
        c_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'C%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if c_course_list[0]["meeting_pattern"] != None:
            cemptylist = list(c_course_list[0]["meeting_pattern"])
        else:
            cemptylist = []
        d_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'D%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if d_course_list[0]["meeting_pattern"] != None:
            demptylist = list(d_course_list[0]["meeting_pattern"])
        else:
            demptylist = []
        e_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'E%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if e_course_list[0]["meeting_pattern"] != None:
            eemptylist = list(e_course_list[0]["meeting_pattern"])
        else:
            eemptylist = []
        f_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'F%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if f_course_list[0]["meeting_pattern"] != None:
            femptylist = list(f_course_list[0]["meeting_pattern"])
        else:
            femptylist = []
        g_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'G%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if g_course_list[0]["meeting_pattern"] != None:
            gemptylist = list(g_course_list[0]["meeting_pattern"])
        else:
            gemptylist = []
        h_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'H%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if h_course_list[0]["meeting_pattern"] != None:
            hemptylist = list(h_course_list[0]["meeting_pattern"])
        else:
            hemptylist = []
        i_course_list = db.execute("SELECT group_concat(meeting_pattern) as meeting_pattern FROM course_schedule WHERE meeting_pattern LIKE 'I%' AND username=:username AND trimester_offered=:tri", tri="Trimester 3", username=username[0]["username"])
        if i_course_list[0]["meeting_pattern"] != None:
            iemptylist = list(i_course_list[0]["meeting_pattern"])
        else:
            iemptylist = []
    if aemptylist.count('1') > 1 or aemptylist.count('2') > 1 or aemptylist.count('3') > 1 or aemptylist.count('4') > 1 or aemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block A")
        return redirect("/schedule")
    elif bemptylist.count('1') > 1 or bemptylist.count('2') > 1 or bemptylist.count('3') > 1 or bemptylist.count('4') > 1 or bemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block B")
        return redirect("/schedule")
    elif cemptylist.count('1') > 1 or cemptylist.count('2') > 1 or cemptylist.count('3') > 1 or cemptylist.count('4') > 1 or cemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block C")
        return redirect("/schedule")
    elif demptylist.count('1') > 1 or demptylist.count('2') > 1 or demptylist.count('3') > 1 or demptylist.count('4') > 1 or demptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block D")
        return redirect("/schedule")
    elif eemptylist.count('1') > 1 or eemptylist.count('2') > 1 or eemptylist.count('3') > 1 or eemptylist.count('4') > 1 or eemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block E")
        return redirect("/schedule")
    elif femptylist.count('1') > 1 or femptylist.count('2') > 1 or femptylist.count('3') > 1 or femptylist.count('4') > 1 or femptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block F")
        return redirect("/schedule")
    elif gemptylist.count('1') > 1 or gemptylist.count('2') > 1 or gemptylist.count('3') > 1 or gemptylist.count('4') > 1 or gemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block G")
        return redirect("/schedule")
    elif hemptylist.count('1') > 1 or hemptylist.count('2') > 1 or hemptylist.count('3') > 1 or hemptylist.count('4') > 1 or hemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block H")
        return redirect("/schedule")
    elif iemptylist.count('1') > 1 or iemptylist.count('2') > 1 or iemptylist.count('3') > 1 or iemptylist.count('4') > 1 or iemptylist.count('5') > 1:
        flash("Schedule cannot be generated since there is a conflict in Block I")
        return redirect("/schedule")
    else:
        A1=""
        A2=""
        A3=""
        A4=""
        A5=""
        Alab=""
        B1=""
        B2=""
        B3=""
        B4=""
        B5=""
        Blab=""
        C1=""
        C2=""
        C3=""
        C4=""
        C5=""
        Clab=""
        D1=""
        D2=""
        D3=""
        D4=""
        D5=""
        Dlab=""
        E1=""
        E2=""
        E3=""
        E4=""
        E5=""
        Elab=""
        F1=""
        F2=""
        F3=""
        F4=""
        F5=""
        Flab=""
        G1=""
        G2=""
        G3=""
        G4=""
        G5=""
        Glab=""
        H1=""
        H2=""
        H3=""
        H4=""
        I1=""
        I2=""
        I3=""
        I4=""

        for thing in scheduled_courses:
            cc = thing["five_chars"]
            mp = thing["meeting_pattern"]

            # The following are some of the exceptions to the normal meeting pattern behavior

            # Japanese AH case
            if mp[0:1] == 'A' and 'H' in mp:
                hindex = mp.index('H')
                aportion = mp[0:hindex]
                hportion = mp[hindex:]

                if "1" in aportion:
                    A1=cc
                if "2" in aportion:
                    A2=cc
                if "3" in aportion:
                    A3=cc
                if "4" in aportion:
                    A4=cc
                if "5" in aportion:
                    A5=cc
                if "L" in aportion:
                    Alab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Japanese BH case
            if mp[0:1] == 'B' and 'H' in mp:
                hindex = mp.index('H')
                bportion = mp[0:hindex]
                hportion = mp[hindex:]

                if "1" in bportion:
                    B1=cc
                if "2" in bportion:
                    B2=cc
                if "3" in bportion:
                    B3=cc
                if "4" in bportion:
                    B4=cc
                if "5" in bportion:
                    B5=cc
                if "L" in bportion:
                    Blab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Orchestra and WE HC case
            if mp[0:1] == 'H' and 'C' in mp:
                cindex = mp.index('C')
                hportion = mp[0:cindex]
                cportion = mp[cindex:]

                if "1" in cportion:
                    C1=cc
                if "2" in cportion:
                    C2=cc
                if "3" in cportion:
                    C3=cc
                if "4" in cportion:
                    C4=cc
                if "5" in cportion:
                    C5=cc
                if "L" in cportion:
                    Clab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Orchestra and WE HF case
            if mp[0:1] == 'H' and 'F' in mp:
                findex = mp.index('F')
                hportion = mp[0:findex]
                fportion = mp[findex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in hportion:
                    H1=cc
                if "2" in hportion:
                    H2=cc
                if "3" in hportion:
                    H3=cc
                if "4" in hportion:
                    H4=cc

            # Mentorship FEG case
            if mp[0:1] == 'F' and 'E' in mp and 'G' in mp:
                eindex = mp.index('E')
                gindex = mp.index('G')
                fportion = mp[0:eindex]
                eportion = mp[eindex:gindex]
                gportion = mp[gindex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in eportion:
                    E1=cc
                if "2" in eportion:
                    E2=cc
                if "3" in eportion:
                    E3=cc
                if "4" in eportion:
                    E4=cc
                if "5" in eportion:
                    E5=cc
                if "L" in eportion:
                    Elab=cc
                if "1" in gportion:
                    G1=cc
                if "2" in gportion:
                    G2=cc
                if "3" in gportion:
                    G3=cc
                if "4" in gportion:
                    G4=cc
                if "5" in gportion:
                    G5=cc
                if "L" in gportion:
                    Glab=cc

            # Research FG case
            if mp[0:1] == 'F' and 'G' in mp:
                gindex = mp.index('G')
                fportion = mp[0:gindex]
                gportion = mp[gindex:]

                if "1" in fportion:
                    F1=cc
                if "2" in fportion:
                    F2=cc
                if "3" in fportion:
                    F3=cc
                if "4" in fportion:
                    F4=cc
                if "5" in fportion:
                    F5=cc
                if "L" in fportion:
                    Flab=cc
                if "1" in gportion:
                    G1=cc
                if "2" in gportion:
                    G2=cc
                if "3" in gportion:
                    G3=cc
                if "4" in gportion:
                    G4=cc
                if "5" in gportion:
                    G5=cc
                if "L" in gportion:
                    Glab=cc

            # The regular A case
            if mp[0:1] == 'A' and 'H' not in mp:
                if "1" in mp:
                    A1=cc
                if "2" in mp:
                    A2=cc
                if "3" in mp:
                    A3=cc
                if "4" in mp:
                    A4=cc
                if "5" in mp:
                    A5=cc
                if "L" in mp:
                    Alab=cc

            # The regular B case
            if mp[0:1] == 'B' and 'H' not in mp:
                if "1" in mp:
                    B1=cc
                if "2" in mp:
                    B2=cc
                if "3" in mp:
                    B3=cc
                if "4" in mp:
                    B4=cc
                if "5" in mp:
                    B5=cc
                if "L" in mp:
                    Blab=cc

            # The regular C case
            if mp[0:1] == 'C' and 'H' not in mp:
                if "1" in mp:
                    C1=cc
                if "2" in mp:
                    C2=cc
                if "3" in mp:
                    C3=cc
                if "4" in mp:
                    C4=cc
                if "5" in mp:
                    C5=cc
                if "L" in mp:
                    Clab=cc

            # The regular D case
            if mp[0:1] == 'D':
                if "1" in mp:
                    D1=cc
                if "2" in mp:
                    D2=cc
                if "3" in mp:
                    D3=cc
                if "4" in mp:
                    D4=cc
                if "5" in mp:
                    D5=cc
                if "L" in mp:
                    Dlab=cc

            # The regular E case
            if mp[0:1] == 'E' and 'F' not in mp and 'G' not in mp:
                if "1" in mp:
                    E1=cc
                if "2" in mp:
                    E2=cc
                if "3" in mp:
                    E3=cc
                if "4" in mp:
                    E4=cc
                if "5" in mp:
                    E5=cc
                if "L" in mp:
                    Elab=cc

            # The regular F case
            if mp[0:1] == 'F' and 'G' not in mp and 'E' not in mp and 'H' not in mp:
                if "1" in mp:
                    F1=cc
                if "2" in mp:
                    F2=cc
                if "3" in mp:
                    F3=cc
                if "4" in mp:
                    F4=cc
                if "5" in mp:
                    F5=cc
                if "L" in mp:
                    Flab=cc

            # The regular G case
            if mp[0:1] == 'G' and 'E' not in mp and 'F' not in mp:
                if "1" in mp:
                    G1=cc
                if "2" in mp:
                    G2=cc
                if "3" in mp:
                    G3=cc
                if "4" in mp:
                    G4=cc
                if "5" in mp:
                    G5=cc
                if "L" in mp:
                    Glab=cc

            # The regular H case
            if mp[0:1] == 'H' and 'A' not in mp and 'B' not in mp and 'C' not in mp and 'F' not in mp:
                if "1" in mp:
                    H1=cc
                if "2" in mp:
                    H2=cc
                if "3" in mp:
                    H3=cc
                if "4" in mp:
                    H4=cc

            # The regular I case
            if mp[0:1] == 'I':
                if "1" in mp:
                    I1=cc
                if "2" in mp:
                    I2=cc
                if "3" in mp:
                    I3=cc
                if "4" in mp:
                    I4=cc
        return render_template("schedule.html", var="3", A1=A1, A2=A2, A3=A3, A4=A4, A5=A5, Alab=Alab, B1=B1, B2=B2, B3=B3, B4=B4, B5=B5, Blab=Blab, C1=C1, C2=C2, C3=C3, C4=C4, C5=C5, Clab=Clab, D1=D1, D2=D2, D3=D3, D4=D4, D5=D5, Dlab=Dlab, E1=E1, E2=E2, E3=E3, E4=E4, E5=E5, Elab=Elab, F1=F1, F2=F2, F3=F3, F4=F4, F5=F5, Flab=Flab, G1=G1, G2=G2, G3=G3, G4=G4, G5=G5, Glab=Glab, H1=H1, H2=H2, H3=H3, H4=H4, I1=I1, I2=I2, I3=I3, I4=I4)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must enter a username")
            return redirect("/login")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must enter a password")
            return redirect("/login")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username/password")
            return redirect("/login")
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/clear", methods=["GET", "POST"])
@login_required
def clear():
    # Display the unaltered table
    return render_template("schedule.html")

@app.route("/notice")
@login_required
def notice():
    return render_template("notice.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("You have been logged out")
    return redirect("/login")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Make sure user entered a username
        if not request.form.get("username"):
            flash("Must enter a username")
            return redirect("/register")
        # Make sure user entered a password
        elif not request.form.get("password"):
            flash("Must enter a password")
            return redirect("/register")
        # Make sure user re-entered their password
        elif not request.form.get("confirmation"):
            flash("Must confirm your password")
            return redirect("/register")
        # Make sure the passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("Passwords do not match")
            return redirect("/register")
        # Add user to users table
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        new_user = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)

        # Make sure the username is unique
        if not new_user:
            flash("Username already exists")
            return redirect("/register")
        session["user_id"] = new_user

        # Display a sucess message
        flash("Registration successful")

        # Take the user back to the home page
        return redirect("/")

    else:
        return render_template("register.html")




