from flask import redirect, render_template, Flask, request, url_for, send_file
import datetime, json, os, dateutil, requests, subprocess
import glob

os.chdir(os.path.split(__file__)[0])

app = Flask(__name__)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    return (datetime.datetime.strptime(date,"%d/%m/%Y")).strftime('%B %d, %Y')

@app.route('/')
def index():
    projects = []
    for directory in os.listdir('..'):
        with open(f"../{directory}/project.index.json") as jsonfile:
            project = json.loads(jsonfile.read())
            projects.append(project)
    stats = {"completed":0,
             "upcoming":0,
             "total":0}
    for project in projects:
        if project["completed"]=="true":
            stats["completed"]+=1
        else:
            stats["upcoming"]+=1
        stats["total"]+=1
    return render_template('index.html',
                            projects=projects,
                            formatteddate=datetime.datetime.now().strftime("%B %d"),
                            stats=stats)

@app.route('/create',methods=['POST'])
def create():
    name = request.form["title"]
    modules = request.form["modules"].split(',')
    fmodules = []
    for i in modules:
        fmodules.append(i.strip())
    modules = fmodules
    description = request.form["description"]
    code = str(name)[:2].upper()+"-"+(datetime.datetime.now().strftime('%d%m%Y-%H%M%S'))
    project = {
                "name" : name,
                "description" : description,
                "created" : datetime.datetime.now().strftime("%d/%m/%Y"),
                "completed" : "false",
                "modules" : modules,
                "hosting" : {"hosted" : "false"},
                "code" : code
              }
    os.mkdir(f"../{name.replace(' ','_')}_({code})")
    with open(f"../{name.replace(' ','_')}_({code})/project.index.json","w") as jsonfile:
        json.dump(project,jsonfile, indent=4)
    with open(f"../{name.replace(' ','_')}_({code})/index.py","w") as indexpy:
        indexpy.write("import "+str(", ".join(modules))+"\n")
    if "flask" in modules:
        modules.remove("flask")
        with open(f"../{name.replace(' ','_')}_({code})/index.py","w") as indexpy:
            indexpy.write("from flask import redirect, render_template, Flask, request, url_for, send_file\n")
            indexpy.write("import "+str(", ".join(modules))+"\n")
            indexpy.write('''
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")


if __name__=="__main__":
    app.run(
        debug=True,
        use_reloader=True,
        use_debugger=True,
        port=5000,
        host='0.0.0.0',
        use_evalex=True,
        threaded=True,
        passthrough_errors=False
        )''')
        os.mkdir(f"../{name.replace(' ','_')}_({code})/templates")

        os.mkdir(f"../{name.replace(' ','_')}_({code})/static")
        os.mkdir(f"../{name.replace(' ','_')}_({code})/static/scripts")
        with open(f"../{name.replace(' ','_')}_({code})/static/scripts/scripts.js","w") as scriptsjs:
            pass
        with open(f"../{name.replace(' ','_')}_({code})/static/scripts/jquery.min.js","w") as jsfile:
                jsfile.write(str((requests.get('https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js', allow_redirects=True)).text))
        os.mkdir(f"../{name.replace(' ','_')}_({code})/static/styles")
        with open(f"../{name.replace(' ','_')}_({code})/static/styles/styles.css","w") as stylescss:
            pass
        os.mkdir(f"../{name.replace(' ','_')}_({code})/static/images")
        os.mkdir(f"../{name.replace(' ','_')}_({code})/data")

        framework = request.form["framework"]

        if framework=='none':

            with open(f"../{name.replace(' ','_')}_({code})/templates/index.html","w") as indexhtml:
                indexhtml.write('''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <link rel='stylesheet' href="{{url_for('static',filename='styles/styles.css')}}"/>
    '''+f"<title>{name.replace(' ','_')}_({code})</title>"+'''
  </head>
  <body>
  <script src="{{url_for('static',filename='scripts/jquery.min.js')}}"></script>
  <script src="{{url_for('static',filename='scripts/scripts.js')}}"></script>
  </body>
</html>''')
        else:
            links = {"bs": {"js":"https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js",
                            "css":"https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"},
                     "mat":{"js":"https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js",
                            "css":"https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"},
                     "mdl":{"js":"https://code.getmdl.io/1.3.0/material.min.js",
                            "css":"https://code.getmdl.io/1.3.0/material.indigo-pink.min.css"},
                     "mdb":{"js":"https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/3.3.0/mdb.min.js",
                            "css":"https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/3.3.0/mdb.min.css"}}
            files = links[framework]
            jsfilename = files['js'].split('/')[-1]
            cssfilename = files['css'].split('/')[-1]
            with open(f"../{name.replace(' ','_')}_({code})/static/scripts/{jsfilename}","w") as jsfile:
                jsfile.write(str((requests.get(files['js'], allow_redirects=True)).text))
            with open(f"../{name.replace(' ','_')}_({code})/static/styles/{cssfilename}","w") as cssfile:
                cssfile.write(str((requests.get(files['css'], allow_redirects=True)).text))
            with open(f"../{name.replace(' ','_')}_({code})/templates/index.html","w") as indexhtml:
                indexhtml.write('''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <link rel='stylesheet' href="{{url_for('static',filename='styles/styles.css')}}"/>
    <link rel='stylesheet' href="{{url_for('static',filename='styles/'''+cssfilename+'''')}}"/>
    '''+f"<title>{name.replace(' ','_')}_({code})</title>"+'''
  </head>
  <body>
  <script src="{{url_for('static',filename='scripts/jquery.min.js')}}"></script>
  <script src="{{url_for('static',filename='scripts/scripts.js')}}"></script>
  <script src="{{url_for('static',filename='scripts/'''+jsfilename+'''')}}"></script>
  </body>
</html>''')


        
    return redirect(url_for("index"))

def checkX(string,negchecks,poschecks):
    checklist = []
    for x in negchecks:
        if x not in string:
            checklist.append(1)
        else:
            checklist.append(0)
    for x in poschecks:
        if x in string:
            checklist.append(1)
        else:
            checklist.append(0)
    if 0 in checklist:
        return False
    return True

def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

@app.route('/toggle/<code>')
def toggle_status(code):
    for directory in os.listdir('..'):
        if code in directory:
            with open(f"../{directory}/project.index.json") as jsonfile:
                project = json.loads(jsonfile.read())
                if project["completed"]=="true":
                    project.update({"completed":"false"})
                else:
                    project.update({"completed":"true"})
            with open(f"../{directory}/project.index.json","w") as jsonfile:
                json.dump(project,jsonfile, indent=4)
            subfolders, files = run_fast_scandir(f"../{directory}", [".py"])

            pymods = []

            for i in files:
                with open(i) as pyfile:
                    project = pyfile.readlines()
                    for line in project:
                        if checkX(line,
                            ["#","*","!","@","$","%","^","&","(",")","-","=","+","~","`","'",'"',"[","]"],
                            ["import "]):
                            if "from " not in line:
                                for x in line.split("import ")[-1].replace("import ","").split(" as ")[0].split(","):
                                    for y in x.strip().split(" "):
                                        pymods.append(y)
                            else:
                                for x in line.split("from ")[-1].split("import  ")[0].replace("from ","").replace("import ","").split(","):
                                    for y in x.strip().split(" "):
                                        pymods.append(y)
            case_filter = []
            python_modules = []
            for i in pymods:
                if i.lower() not in case_filter:
                    case_filter.append(i.lower())
                    python_modules.append(i)

            reqmts = []
            for mod in python_modules:
                result = subprocess.getoutput(f'pip freeze | grep {mod}')
                for out in result.split("\n"):
                    if f"-{mod.lower()}" in out.split("=")[0].lower()\
                    or f"{mod.lower()}-" in out.split("=")[0].lower()\
                    or f"-{mod.lower()}-" in out.split("=")[0].lower()\
                    or f"={mod.lower()}" in out.split("=")[0].lower()\
                    or mod.lower() == out.split("=")[0].lower():
                        reqmts.append(out.replace("\n",""))

            with open(f"../{directory}/requirements.txt","w") as reqmtfile:
                reqmtfile.write("\n".join(reqmts))

    return redirect(url_for("index"))

@app.route('/statistics')
def statistics():
    projects = []
    for directory in os.listdir('..'):
        with open(f"../{directory}/project.index.json") as jsonfile:
            project = json.loads(jsonfile.read())
            projects.append(project)
    monthly = [0,0,0,0,0,0,0,0,0,0,0,0]
    times={}
    for project in projects:
        date = int((datetime.datetime.strptime(project["code"].split('-')[1],"%d%m%Y")).strftime("%m"))
        monthly[date-1] += 1
        time = int(str(int(round((int(str(project["code"].split('-')[2][:2]))+int(str(project["code"].split('-')[2][2:4]))/60),0))))
        if time not in times:
            times.update({time:1})
        else:
            times.update({time:times[time]+1})
    
    thismonth = monthly[int(datetime.datetime.now().strftime("%m"))]
    mostmonth = monthly.index(max(monthly))
    mostmonth = datetime.datetime.strptime(str(int(mostmonth+1)),"%m").strftime("%B")

    times = dict(sorted(times.items()))
    mosttime = 0
    mosttimeee = ''
    for key,value in times.items():
        if value>mosttime:
            mosttime = value
            mosttimeee = datetime.datetime.strptime(str(key),"%H").strftime("%I:00 %p")

    return render_template("statistics.html",monthly=monthly,tvals=list(times.values()),tkeys=list(times.keys()),thismonth=thismonth,mostmonth=mostmonth,mosttime=mosttimeee,totalproj=len(projects),formatteddate=datetime.datetime.now().strftime("%B %d"),year=datetime.datetime.now().strftime("%Y"))




if __name__=="__main__":
    app.run(
        debug=True,
        use_reloader=True,
        use_debugger=True,
        port=3209,
        host='0.0.0.0',
        use_evalex=True,
        threaded=True,
        passthrough_errors=False
        ) 
