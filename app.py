from flask import Flask, request, jsonify, abort
import json
from threading import Thread
import time
from datetime import datetime
import xmlrpc.client
import heapq
import requests
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

list_of_valid_requests = []

sm1_execution_rpc = None
mm1_execution_rpc = None
ov1_execution_rpc = None
vgr1_execution_rpc = None
hbw1_execution_rpc = None
wt1_execution_rpc = None

heap_queue_sm1_execution = []
heap_queue_vgr1_execution = []
heap_queue_hbw1_execution = []
heap_queue_ov1_execution = []
heap_queue_mm1_execution = []
heap_queue_wt1_execution = []

sm1_getter_setter_rpc = None
mm1_getter_setter_rpc = None
ov1_getter_setter_rpc = None
vgr1_getter_setter_rpc = None
hbw1_getter_setter_rpc = None
wt1_getter_setter_rpc = None

heap_queue_sm1_getter_setter = []
heap_queue_vgr1_getter_setter = []
heap_queue_hbw1_getter_setter = []
heap_queue_ov1_getter_setter = []
heap_queue_mm1_getter_setter = []
heap_queue_wt1_getter_setter = []

"""
#####################################################################
#####################################################################
################## Initializing Web Server and Queue ################
#####################################################################
#####################################################################
"""


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(404)
def bad_request(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(417)
def precondition_not_fulfilled(e):
    return jsonify(error=str(e)), 417


@app.before_request
def before_request():
    if request.url == "http://127.0.0.1:5000/favicon.ico":
        print(request.url + " was called")
        return
    if request.url == "http://127.0.0.1:5000/apidocs/":
        return
    if request.url == "http://localhost:5000/apidocs/":
        return
    if request.url == "http://192.168.0.5:5000/apidocs/":
        return
    if "/flasgger_static/" in request.url:
        return
    if "apispec" in request.url:
        return

    path = request.path
    path_split = path.split("/")
    machine = path_split[1]
    task = path_split[2]
    dt = datetime.now()
    request.datetime = dt

    if request.args.get('machine'):
        machine_and_factory = request.args.get('machine')
        tmp_arr = machine_and_factory.split("_")
        factory = tmp_arr[1]
        request.factory = factory
    else:
        abort(404, 'No Machine is passed')

    # lower values in the priority queue are preferred over larger ones
    if request.args.get("prio"):
        priority = request.args.get("prio")
    else:
        priority = 3
    if task == "status_of_light_barrier" or \
            task == "get_amount_of_stored_workpieces" or \
            task == "state_of_machine" or \
            task == "set_motor_speed" or \
            task == "reset_all_motor_speeds" or \
            task == "get_motor_speed" or \
            task == "check_position" or \
            task == "get_slot_number_of_workpiece_by_color" or \
            task == "detect_color" or \
            task == "has_capacitive_sensor_registered_workpiece":
        if factory == "1":
            if machine == "sm":
                heapq.heappush(heap_queue_sm1_getter_setter, (priority, dt, request, path))
            elif machine == "vgr":
                heapq.heappush(heap_queue_vgr1_getter_setter, (priority, dt, request, path))
            elif machine == "hbw":
                heapq.heappush(heap_queue_hbw1_getter_setter, (priority, dt, request, path))
            elif machine == "ov":
                heapq.heappush(heap_queue_ov1_getter_setter, (priority, dt, request, path))
            elif machine == "mm":
                heapq.heappush(heap_queue_mm1_getter_setter, (priority, dt, request, path))
            elif machine == "mps":
                heapq.heappush(heap_queue_wt1_getter_setter, (priority, dt, request, path))
            elif machine == "wt":
                heapq.heappush(heap_queue_wt1_getter_setter, (priority, dt, request, path))
    else:
        if factory == "1":
            if machine == "sm":
                heapq.heappush(heap_queue_sm1_execution, (priority, dt, request, path))
            elif machine == "vgr":
                heapq.heappush(heap_queue_vgr1_execution, (priority, dt, request, path))
            elif machine == "hbw":
                heapq.heappush(heap_queue_hbw1_execution, (priority, dt, request, path))
            elif machine == "ov":
                heapq.heappush(heap_queue_ov1_execution, (priority, dt, request, path))
            elif machine == "mm":
                heapq.heappush(heap_queue_mm1_execution, (priority, dt, request, path))
            elif machine == "mps":
                heapq.heappush(heap_queue_wt1_execution, (priority, dt, request, path))
            elif machine == "wt":
                heapq.heappush(heap_queue_wt1_execution, (priority, dt, request, path))

def create_json(req, *args):
    end_dt = datetime.now()
    process_dt = end_dt - req.datetime

    str_start_dt = req.datetime.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    str_end_dt = end_dt.strftime("%d-%b-%Y (%H:%M:%S.%f)")

    json_output = {
        "link": req.base_url,
        "start_time": str_start_dt,
        "end_time": str_end_dt,
        "process_time": str(process_dt),
        "attributes": args
    }

    return json_output


def check_heap_queue_sm1_execution(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_sm1_execution[0][1] and req.path == heap_queue_sm1_execution[0][3]:
            tmp = False


def pop_heap_queue_sm1_execution():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_sm1_execution)


def check_heap_queue_vgr1_execution(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_vgr1_execution[0][1] and req.path == heap_queue_vgr1_execution[0][3]:
            tmp = False


def pop_heap_queue_vgr1_execution():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_vgr1_execution)


def check_heap_queue_hbw1_execution(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_hbw1_execution[0][1] and req.path == heap_queue_hbw1_execution[0][3]:
            tmp = False


def pop_heap_queue_hbw1_execution():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_hbw1_execution)


def check_heap_queue_ov1_execution(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_ov1_execution[0][1] and req.path == heap_queue_ov1_execution[0][3]:
            tmp = False


def pop_heap_queue_ov1_execution():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_ov1_execution)


def check_heap_queue_wt1_execution(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_wt1_execution[0][1] and req.path == heap_queue_wt1_execution[0][3]:
            tmp = False


def pop_heap_queue_wt1_execution():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_wt1_execution)


def check_heap_queue_mm1_execution(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_mm1_execution[0][1] and req.path == heap_queue_mm1_execution[0][3]:
            tmp = False


def pop_heap_queue_mm1_execution():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_mm1_execution)


def check_heap_queue_sm1_getter_setter(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_sm1_getter_setter[0][1] and req.path == heap_queue_sm1_getter_setter[0][3]:
            tmp = False


def pop_heap_queue_sm1_getter_setter():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_sm1_getter_setter)


def check_heap_queue_vgr1_getter_setter(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_vgr1_getter_setter[0][1] and req.path == heap_queue_vgr1_getter_setter[0][3]:
            tmp = False


def pop_heap_queue_vgr1_getter_setter():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_vgr1_getter_setter)


def check_heap_queue_hbw1_getter_setter(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_hbw1_getter_setter[0][1] and req.path == heap_queue_hbw1_getter_setter[0][3]:
            tmp = False


def pop_heap_queue_hbw1_getter_setter():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_hbw1_getter_setter)


def check_heap_queue_ov1_getter_setter(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_ov1_getter_setter[0][1] and req.path == heap_queue_ov1_getter_setter[0][3]:
            tmp = False


def pop_heap_queue_ov1_getter_setter():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_ov1_getter_setter)


def check_heap_queue_wt1_getter_setter(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_wt1_getter_setter[0][1] and req.path == heap_queue_wt1_getter_setter[0][3]:
            tmp = False


def pop_heap_queue_wt1_getter_setter():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_wt1_getter_setter)


def check_heap_queue_mm1_getter_setter(req):
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :param req: Request
    :return: Nothing
    """
    tmp = True
    while tmp:
        if req.datetime == heap_queue_mm1_getter_setter[0][1] and req.path == heap_queue_mm1_getter_setter[0][3]:
            tmp = False


def pop_heap_queue_mm1_getter_setter():
    """
    Checks whether the given request is at the first position of the queue. This is executed until it is the case.
    :return: Nothing
    """
    heapq.heappop(heap_queue_mm1_getter_setter)


"""
#####################################################################
#####################################################################
################## Sorting Machine ##################################
################## Execution Webservices ############################
#####################################################################
#####################################################################
"""

@app.route("/sm/sort")
def sm_sort() -> [None, json]:
    """
        Starts the entire sorting machine process once.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: sm_1
            - name: start
              in: path
              type: string
              required: true
              description: initial
            - name: predefined_ejection_location
              in: path
              type: string
              required: true
              description: none
        description:
                    Starts the entire sorting machine process once. **/sm/sort?machine=sm_1&start=initial&predefined_ejection_location=none**
                    [Example URL](http://192.168.0.5:5000/sm/sort?machine=sm_1&start=initial&predefined_ejection_location=none)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_sm1_execution(request)

        try:
            position = sm1_execution_rpc.sort(
                str(request.args.get('start')),
                bool(request.args.get('use_nfc')),
                str(request.args.get('predefined_ejection_location'))
            )
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_sm1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_sm1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")
    args = {"sink": position}

    if request and request.method == "GET":
        return jsonify(create_json(request,args))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
################## Sorting Machine ##################################
############ Getter and Setter Webservices ##########################
#####################################################################
#####################################################################
"""


@app.route('/sm/state_of_machine')
def sm_state_of_machine() -> [None, json]:
    """
        Indicates the state of a machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: sm_1
        description: 
                    Indicates the state of a machine **sm/state_of_machine?machine=sm_1**
                    [Example URL](http://192.168.0.5:5000/sm/state_of_machine?machine=sm_1)
        responses:
            200:
                description: JSON
    """
    state = None
    if request.factory == "1":
        check_heap_queue_sm1_getter_setter(request)
        try:
            state = sm1_getter_setter_rpc.state_of_machine(1)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_sm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_sm1_getter_setter()

    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"state": state}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/sm/status_of_light_barrier')
def sm_status_of_light_barrier() -> [None, json]:
    """
        Indicates whether a light barrier is broken through or not.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: sm_1
            - name: lb
              in: path
              type: integer
              required: true
              description: Number of light barrier in SM
        description:
                    URL **sm/status_of_light_barrier?machine=sm_1&lb=1**
                    [Example Link](http://192.168.0.5:5000/sm/status_of_light_barrier?machine=sm_1&lb=1)
        responses:
            200:
                description: JSON
    """
    status = None
    if request.factory == "1" and request.args.get('lb'):
        check_heap_queue_sm1_getter_setter(request)
        try:
            status = sm1_getter_setter_rpc.status_of_light_barrier(int(request.args.get('lb')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_sm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_sm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"interrupted": status}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/sm/get_motor_speed')
def sm_get_motor_speed() -> [None, json]:
    """
        Gets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: sm_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
        description: 
                    URL **sm/get_motor_speed?machine=sm_1&motor=1**
                    [Example Link](http://192.168.0.5:5000/sm/get_motor_speed?machine=sm_1&motor=1)
        responses:
            200:
                description: JSON
    """
    motor_speed = None
    if request.factory == "1" and request.args.get('motor'):
        check_heap_queue_sm1_getter_setter(request)
        try:
            motor_speed = sm1_getter_setter_rpc.get_motor_speed(int(request.args.get('motor')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_sm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_sm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"motor_speed": motor_speed}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/sm/set_motor_speed')
def sm_set_motor_speed() -> [None, json]:
    """
        Sets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: sm_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
            - name: speed
              in: path
              type: integer
              required: true
              description: Motor speed
        description: 
                    URL **sm/set_motor_speed?machine=sm_1&motor=1&speed=400**
                    [Example Link](http://192.168.0.5:5000/sm/set_motor_speed?machine=sm_1&motor=1&speed=400)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('motor') and request.args.get('speed'):
        check_heap_queue_sm1_getter_setter(request)
        try:
            sm1_getter_setter_rpc.set_motor_speed(int(request.args.get('motor')), int(request.args.get('speed')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_sm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_sm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/sm/reset_all_motor_speeds')
def sm_reset_all_motor_speeds() -> [None, json]:
    """
        Resets all the motor speeds for the specified machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: sm_1
        description: 
                    Indicates the state of a machine **sm/reset_all_motor_speeds?machine=sm_1**
                    [Example Link](http://192.168.0.5:5000/sm/reset_all_motor_speeds?machine=sm_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_sm1_getter_setter(request)
        try:
            sm1_getter_setter_rpc.reset_all_motor_speeds()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_sm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_sm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)



"""
#####################################################################
#####################################################################
#### MULTI PROCESSING STATION - MILLING MACHINE #####################
################## Execution Webservices ############################
#####################################################################
#####################################################################
"""


@app.route('/mm/calibrate')
def mm_calibrate() -> [None, json]:
    """
        Calibrates the turntable. The turntable only moves to the starting position.
        However, since "calibrate" was always used, this is also done for usability reasons.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
        description: 
                    URL **mm/calibrate?machine=mm_1**
                    [Example Link](http://192.168.0.5:5000/mm/calibrate?machine=mm_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_mm1_execution(request)

        try:
            mm1_execution_rpc.calibrate()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_execution()
    else:
        abort(404)

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")


@app.route('/mm/mill')
def mm_mill() -> [None, json]:
    """
        Starts milling.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
            - name: time
              in: path
              type: integer
              required: false
              description: time
            - name: start
              in: path
              type: string
              required: true
              description: Start Position
            - name: end
              in: path
              type: string
              required: true
              description: End Position
        description: >
                    If the workpiece moves to the milling machine, mills and then moves to the ejection position,
                    pushes the workpiece onto the conveyor belt, starts it for 10 seconds and then returns to the initial position.
                    **mm/mill?machine=mm_1&time=10&start=initial&end=ejection**
                    [Example Link](http://192.168.0.5:5000/mm/mill?machine=mm_1&time=10&start=initial&end=ejection)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('start') and request.args.get('end'):
        time_to_mill = request.args.get('time')
        check_heap_queue_mm1_execution(request)

        try:
            mm1_execution_rpc.mill(
                request.args.get('start'), request.args.get('end'),
                int(time_to_mill) if time_to_mill is not None else 2)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/mm/move_from_to')
def mm_move_from_to() -> [None, json]:
    """
        Moves the turntable to the specified position.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
            - name: start
              in: path
              type: string
              required: true
              description: Start Position
            - name: end
              in: path
              type: string
              required: true
              description: End Position
        description: >
                    If the workpiece moves to the milling machine, mills and then moves to the ejection position,
                    pushes the workpiece onto the conveyor belt, starts it for 10 seconds and then returns to the initial position.
                    **mm/move_from_to?machine=mm_1&start=initial&end=ejection**
                    [Example Link](http://192.168.0.5:5000/mm/move_from_to?machine=mm_1&start=initial&end=ejection)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('start') and request.args.get('end'):
        check_heap_queue_mm1_execution(request)

        try:
            mm1_execution_rpc.move_from_to(request.args.get('start'), request.args.get('end'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/mm/transport_from_to')
def mm_transport_from_to() -> [None, json]:
    """
        Transports the workpiece on the turntable to the specified position.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
            - name: start
              in: path
              type: string
              required: true
              description: Start Position
            - name: end
              in: path
              type: string
              required: true
              description: End Position
        description: >
                    Transports the workpiece on the turntable to the specified position.
                    **mm/transport_from_to?machine=mm_1&start=initial&end=ejection**
                    [Example Link](http://192.168.0.5:5000/mm/transport_from_to?machine=mm_1&start=initial&end=ejection)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('start') and request.args.get('end'):
        check_heap_queue_mm1_execution(request)

        try:
            mm1_execution_rpc.transport_from_to(request.args.get('start'), request.args.get('end'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
#### MULTI PROCESSING STATION - MILLING MACHINE #####################
############ Getter and Setter Webservices ##########################
#####################################################################
#####################################################################
"""


@app.route('/mm/state_of_machine')
def mm_state_of_machine() -> [None, json]:
    """
        Indicates the state of a machine.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
        description: >
                    URL **mm/transport_from_to?machine=mm_1&start=initial&end=ejection**
                    [Example Link](http://192.168.0.5:5000/mm/state_of_machine?machine=mm_1)
        responses:
            200:
                description: JSON
    """
    state = None
    if request.factory == "1":
        check_heap_queue_mm1_getter_setter(request)
        try:
            state = mm1_getter_setter_rpc.state_of_machine(1)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"state": state}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/mm/status_of_light_barrier')
def mm_status_of_light_barrier() -> [None, json]:
    """
        Indicates whether a light barrier is broken through or not.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
            - name: lb
              in: path
              type: integer
              required: false
              description: number of light barrier
        description: >
                    URL **mm/status_of_light_barrier?machine=mm_1&lb=4**
                    [Example Link](http://192.168.0.5:5000/mm/status_of_light_barrier?machine=mm_1&lb=4)
        responses:
            200:
                description: JSON
    """
    status = None
    if request.factory == "1" and request.args.get('lb'):
        check_heap_queue_mm1_getter_setter(request)
        try:
            status = mm1_getter_setter_rpc.status_of_light_barrier(int(request.args.get('lb')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"interrupted": status}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/mm/get_motor_speed')
def mm_get_motor_speed() -> [None, json]:
    """
        Gets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
            - name: motor
              in: path
              type: integer
              required: true
              description: number of motor
        description: >
                    URL **mm/status_of_light_barrier?machine=mm_1&lb=4**
                    [Example Link](http://192.168.0.5:5000/mm/get_motor_speed?machine=mm_1&motor=1)
        responses:
            200:
                description: JSON
    """
    motor_speed = None
    if request.factory == "1" and request.args.get('motor'):
        check_heap_queue_mm1_getter_setter(request)
        try:
            motor_speed = mm1_getter_setter_rpc.get_motor_speed(int(request.args.get('motor')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"motor_speed": motor_speed}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/mm/set_motor_speed')
def mm_set_motor_speed() -> [None, json]:
    """
        Sets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
            - name: motor
              in: path
              type: integer
              required: false
              description: number of motor
            - name: speed
              in: path
              type: integer
              required: false
        description: >
                    URL **mm/set_motor_speed?machine=mm_1&motor=1&speed=400**
                    [Example Link](http://192.168.0.5:5000/mm/set_motor_speed?machine=mm_1&motor=1&speed=400)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('motor') and request.args.get('speed'):
        check_heap_queue_mm1_getter_setter(request)
        try:
            mm1_getter_setter_rpc.set_motor_speed(int(request.args.get('motor')), int(request.args.get('speed')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/mm/reset_all_motor_speeds')
def mm_reset_all_motor_speeds() -> [None, json]:
    """
        Resets all the motor speeds for the specified machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
        description: >
                    URL **mm/reset_all_motor_speeds?machine=mm_1**
                    [Example Link](http://192.168.0.5:5000/mm/reset_all_motor_speeds?machine=mm_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_mm1_getter_setter(request)
        try:
            mm1_getter_setter_rpc.reset_all_motor_speeds()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/mm/check_position')
def mm_check_position() -> [None, json]:
    """
        Checks if the position of the machine matches the queried position
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: mm_1
            - name: position
              in: path
              type: string
              required: true
        description: >
                    URL **mm/check_position?machine=mm_1&position=initial**
                    [Example Link](http://192.168.0.5:5000/mm/check_position?machine=mm_1&position=initial)
        responses:
            200:
                description: JSON
    """
    check = None
    if request.factory == "1" and request.args.get('position'):
        check_heap_queue_mm1_getter_setter(request)
        try:
            check = mm1_getter_setter_rpc.check_position(request.args.get('position'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_mm1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_mm1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"is_at_queried_position": check}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)

"""
#####################################################################
#####################################################################
############### MULTI PROCESSING STATION - Oven #####################
################## Execution Webservices ############################
#####################################################################
#####################################################################
"""


@app.route("/ov/calibrate")
def ov_calibrate() -> [None, json]:
    """
        Calibrates the Oven
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: ov_1
        description: >
                    URL **mm/check_position?machine=ov_1**
                    [Example Link](http://192.168.0.5:5000/mm/check_position?machine=ov_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_ov1_execution(request)

        try:
            ov1_execution_rpc.calibrate()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_ov1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_ov1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route("/ov/burn")
def ov_burn() -> [None, json]:
    """
        This process moves a workpiece into the oven, burns it and then moves it out of the furnace again.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: ov_1
            - name: time
              in: path
              type: integer
              required: false
              description: If no time
        description: >
                    The GET parameter (time) can be transferred and specifies the firing time. If no parameter is passed,
                    the default value is used. **ov/burn?machine=ov_1&time=40**
                    [Example Link](http://192.168.0.5:5000/ov/burn?machine=ov_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        time_to_burn = request.args.get('time')
        check_heap_queue_ov1_execution(request)

        try:
            ov1_execution_rpc.burn(int(time_to_burn) if time_to_burn is not None else 2)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_ov1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_ov1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
############### MULTI PROCESSING STATION - Oven #####################
############ Getter and Setter Webservices ##########################
#####################################################################
#####################################################################
"""


@app.route('/ov/state_of_machine')
def ov_state_of_machine() -> [None, json]:
    """
        Indicates the state of a machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: ov_1
        description: >
                    URL **ov/state_of_machine?machine=ov_1**
                    [Example Link](http://192.168.0.5:5000/ov/state_of_machine?machine=ov_1)
        responses:
            200:
                description: JSON
    """
    state = None
    if request.factory == "1":
        check_heap_queue_ov1_getter_setter(request)
        try:
            state = ov1_getter_setter_rpc.state_of_machine(1)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_ov1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_ov1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"state": state}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/ov/status_of_light_barrier')
def ov_status_of_light_barrier() -> [None, json]:
    """
        Indicates whether a light barrier is broken through or not.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: ov_1
            - name: lb
              in: path
              type: integer
              required: true
              description: number of light barrier
        description: >
                    URL **ov/status_of_light_barrier?machine=ov_1&lb=5**
                    [Example Link](http://192.168.0.5:5000/ov/status_of_light_barrier?machine=ov_1&lb=5)
        responses:
            200:
                description: JSON
    """
    status = None
    if request.factory == "1" and request.args.get('lb'):
        check_heap_queue_ov1_getter_setter(request)
        try:
            status = ov1_getter_setter_rpc.status_of_light_barrier(int(request.args.get('lb')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_ov1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_ov1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"interrupted": status}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/ov/get_motor_speed')
def ov_get_motor_speed() -> [None, json]:
    """
        Gets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: ov_1
            - name: motor
              in: path
              type: integer
              required: true
              description: number of motor
        description: >
                    URL **ov/get_motor_speed?machine=ov_1&motor=1**
                    [Example Link](http://192.168.0.5:5000/ov/get_motor_speed?machine=ov_1&motor=1)
        responses:
            200:
                description: JSON
    """
    motor_speed = None
    if request.factory == "1" and request.args.get('motor'):
        check_heap_queue_ov1_getter_setter(request)
        try:
            motor_speed = ov1_getter_setter_rpc.get_motor_speed(int(request.args.get('motor')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_ov1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_ov1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"motor_speed": motor_speed}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/ov/set_motor_speed')
def ov_set_motor_speed() -> [None, json]:
    """
        Sets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: ov_1
            - name: motor
              in: path
              type: integer
              required: true
              description: number of motor
            - name: speed
              in: path
              type: integer
              required: true
        description: >
                    URL **ov/get_motor_speed?machine=ov_1&motor=1**
                    [Example Link](http://192.168.0.5:5000/ov/set_motor_speed?machine=ov_1&motor=1&speed=400)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('motor') and request.args.get('speed'):
        check_heap_queue_ov1_getter_setter(request)
        try:
            ov1_getter_setter_rpc.set_motor_speed(int(request.args.get('motor')), int(request.args.get('speed')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_ov1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_ov1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/ov/reset_all_motor_speeds')
def ov_reset_all_motor_speeds() -> [None, json]:
    """
        Resets all the motor speeds for the specified machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: ov_1
        description: >
                    URL **ov/reset_all_motor_speeds?machine=ov_1**
                    [Example Link](http://192.168.0.5:5000/ov/reset_all_motor_speeds?machine=ov_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_ov1_getter_setter(request)
        try:
            ov1_getter_setter_rpc.reset_all_motor_speeds()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_ov1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_ov1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
###### MULTI PROCESSING STATION - Workstation Transport #############
################## Execution Webservices ############################
#####################################################################
#####################################################################
"""


@app.route("/wt/calibrate/")
def wt_calibrate() -> [None, json]:
    """
        Calibrates the Workstation Transport.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
        description: >
                    URL **wt/calibrate?machine=wt_1**
                    [Example Link](http://192.168.0.5:5000/wt/calibrate?machine=wt_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_wt1_execution(request)

        try:
            wt1_execution_rpc.wt_calibrate()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route("/wt/move_to")
def wt_move_to() -> [None, json]:
    """
        Moves the crane of the multi-processing station either to the furnace or to the milling machine.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
            - name: position
              in: path
              schema:
                type: string
                enum: [oven,milling_machine]
              required: true
        description: >
                    URL **wt/move_to?machine=wt_1&position=oven**
                    [Example Link](http://192.168.0.5:5000/wt/move_to?machine=wt_1&position=oven)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('position'):
        check_heap_queue_wt1_execution(request)

        try:
            wt1_execution_rpc.wt_move_to(request.args.get('position'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route("/wt/pick_up_and_transport")
def wt_pick_up_and_transport() -> [None, json]:
    """
        The crane picks up the workpiece at the current position and moves it to another position and places it there.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
            - name: start
              in: path
              schema:
                type: string
                enum: [oven,milling_machine]
              required: true
            - name: end
              in: path
              schema:
                type: string
                enum: [oven,milling_machine]
              required: true
        description: >
                    URL **wt/pick_up_and_transport?machine=wt_1&start=milling_machine&end=oven**
                    [Example Link](http://192.168.0.5:5000/wt/pick_up_and_transport?machine=wt_1&start=milling_machine&end=oven)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('start') and request.args.get('end'):
        check_heap_queue_wt1_execution(request)

        try:
            wt1_execution_rpc.wt_pick_up_and_transport(request.args.get('start'), request.args.get('end'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
###### MULTI PROCESSING STATION - Workstation Transport #############
############ Getter and Setter Webservices ##########################
#####################################################################
#####################################################################
"""


@app.route('/wt/state_of_machine')
def wt_state_of_machine() -> [None, json]:
    """
        Indicates the state of a machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
        description: >
                    URL **wt/state_of_machine?machine=wt_1**
                    [Example Link](http://192.168.0.5:5000/wt/state_of_machine?machine=wt_1)
        responses:
            200:
                description: JSON
    """
    state = None
    if request.factory == "1":
        check_heap_queue_wt1_getter_setter(request)
        try:
            state = wt1_getter_setter_rpc.wt_state_of_machine(2)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"state": state}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/wt/get_motor_speed')
def wt_get_motor_speed() -> [None, json]:
    """
        Gets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
        description: >
                    URL **wt/get_motor_speed?machine=wt_1&motor=2**
                    [Example Link](http://192.168.0.5:5000/wt/get_motor_speed?machine=wt_1&motor=2)
        responses:
            200:
                description: JSON
    """
    motor_speed = None
    if request.factory == "1" and request.args.get('motor'):
        check_heap_queue_wt1_getter_setter(request)
        try:
            motor_speed = wt1_getter_setter_rpc.wt_get_motor_speed(int(request.args.get('motor')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"motor_speed": motor_speed}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/wt/set_motor_speed')
def wt_set_motor_speed() -> [None, json]:
    """
        Sets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
            - name: speed
              in: path
              type: integer
              required: true
        description: >
                    URL **wt/set_motor_speed?machine=wt_1&motor=1&speed=400**
                    [Example Link](http://192.168.0.5:5000/wt/set_motor_speed?machine=wt_1&motor=1&speed=400)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('motor') and request.args.get('speed'):
        check_heap_queue_wt1_getter_setter(request)
        try:
            wt1_getter_setter_rpc.wt_set_motor_speed(int(request.args.get('motor')), int(request.args.get('speed')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/wt/reset_all_motor_speeds')
def wt_reset_all_motor_speeds() -> [None, json]:
    """
        Resets all the motor speeds for the specified machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
        description: >
                    URL **wt/reset_all_motor_speeds?machine=wt_1**
                    [Example Link](http://192.168.0.5:5000/wt/reset_all_motor_speeds?machine=wt_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_wt1_getter_setter(request)
        try:
            wt1_getter_setter_rpc.wt_reset_all_motor_speeds()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/wt/check_position')
def wt_check_position() -> [None, json]:
    """
        Checks if the position of the machine matches the queried position
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: wt_1
            - name: position
              in: path
              type: string
              required: true
        description: >
                    URL **wt/check_position?machine=mm_1&position=initial**
                    [Example Link](http://192.168.0.5:5000/wt/check_position?machine=wt_1&position=initial)
        responses:
            200:
                description: JSON
    """
    check = None
    if request.factory == "1" and request.args.get('position'):
        check_heap_queue_wt1_getter_setter(request)
        try:
            check = wt1_getter_setter_rpc.wt_check_position(request.args.get('position'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_wt1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_wt1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"is_at_queried_position": check}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
################## Vacuum Gripper Robot #############################
################## Execution Webservices ############################
#####################################################################
#####################################################################
"""


@app.route('/vgr/calibrate')
def vgr_calibrate() -> [None, json]:
    """
        Pass as get parameter (motor=x) where x must be either 1, 2, or 3. 
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: motor
              in: path
              schema:
                type: integer
                enum: [1,2,3]
              required: true
        description: >
                    If no parameter is passed, all motors are calibrated. **vgr/calibrate?machine=vgr_1&motor=1**
                    [Example Link](http://192.168.0.5:5000/vgr/calibrate?machine=vgr_1&motor=1)
        responses:
            200:
                description: JSON
    """
    if request.args.get('motor'):
        motor = request.args.get('motor')
    else:
        motor = None

    if request.factory == "1":
        check_heap_queue_vgr1_execution(request)

        try:
            if motor is None:
                vgr1_execution_rpc.calibrate()
            else:
                vgr1_execution_rpc.calibrate(int(motor))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/vgr/pick_up_and_transport')
def vgr_pick_up_and_transport() -> [None, json]:
    """
        Transports workpiece from start position to end position.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: start
              in: path
              type: string
              required: true
            - name: end
              in: path
              type: string
              required: true
        description: >
                    URL **vgr/pick_up_and_transport?machine=vgr_1&start=sink_2&end=oven**
                    [Example Link](http://192.168.0.5:5000/vgr/pick_up_and_transport?machine=vgr_1&start=sink_2&end=oven)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('start') and request.args.get('end'):
        check_heap_queue_vgr1_execution(request)

        try:
            vgr1_execution_rpc.pick_up_and_transport(request.args.get('start'), request.args.get('end'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/vgr/stop_vacuum_suction')
def vgr_stop_vacuum_suction() -> [None, json]:
    """
        Stops the vacuum suction of VGR
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
        description: >
                    URL **vgr/stop_vacuum_suction?machine=vgr_1**
                    [Example Link](http://192.168.0.5:5000/vgr/stop_vacuum_suction?machine=vgr_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_vgr1_execution(request)

        try:
            vgr1_execution_rpc.stop_vacuum_suction()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_execution()

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/vgr/move_to')
def vgr_move_to() -> [None, json]:
    """
        Moves to the given position
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: start
              in: path
              type: string
              required: true
              description: Start Position
            - name: position
              in: path
              type: string
              required: true
              description: End Position
        description: >
                    URL **vgr/move_to?machine=vgr_1&start=sink_1&position=oven**
                    [Example Link](http://192.168.0.5:5000/vgr/move_to?machine=vgr_1&start=sink_1&position=oven)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('position'):
        check_heap_queue_vgr1_execution(request)

        try:
            vgr1_execution_rpc.move_to(request.args.get('position'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/vgr/read_color')
def vgr_read_color() -> [None, json]:
    """
        Read the color from the VGR's color sensor at the DPS station.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
        description: >
                    URL **vgr/read_color?machine=vgr_1**
                    [Example Link](http://192.168.0.5:5000/vgr/read_color?machine=vgr_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_vgr1_execution(request)

        try:
            color = vgr1_execution_rpc.read_color()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"current_color": color}
    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
################## Vacuum Gripper Robot #############################
############ Getter and Setter Webservices ##########################
#####################################################################
#####################################################################
"""


@app.route('/vgr/state_of_machine')
def vgr_state_of_machine() -> [None, json]:
    """
        Indicates the state of a machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
        description: >
                    URL **vgr/state_of_machine?machine=vgr_1**
                    [Example Link](http://192.168.0.5:5000/vgr/state_of_machine?machine=vgr_1)
        responses:
            200:
                description: JSON
    """
    state = None
    if request.factory == "1":
        check_heap_queue_vgr1_getter_setter(request)
        try:
            state = vgr1_getter_setter_rpc.state_of_machine(1)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"state": state}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/vgr/get_motor_speed')
def vgr_get_motor_speed() -> [None, json]:
    """
        Gets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
        description: >
                    URL **vgr/get_motor_speed?machine=vgr_1&motor=1**
                    [Example Link](http://192.168.0.5:5000/vgr/get_motor_speed?machine=vgr_1&motor=1)
        responses:
            200:
                description: JSON
    """
    motor_speed = None
    if request.factory == "1" and request.args.get('motor'):
        check_heap_queue_vgr1_getter_setter(request)
        try:
            motor_speed = vgr1_getter_setter_rpc.get_motor_speed(int(request.args.get('motor')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"motor_speed": motor_speed}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/vgr/set_motor_speed')
def vgr_set_motor_speed() -> [None, json]:
    """
        Sets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
            - name: speed
              in: path
              type: integer
              required: true
              description: Number of motor
        description: >
                    URL **vgr/set_motor_speed?machine=vgr_1&motor=1&speed=400**
                    [Example Link](http://192.168.0.5:5000/vgr/set_motor_speed?machine=vgr_1&motor=1&speed=400)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('motor') and request.args.get('speed'):
        check_heap_queue_vgr1_getter_setter(request)
        try:
            vgr1_getter_setter_rpc.set_motor_speed(int(request.args.get('motor')), int(request.args.get('speed')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/vgr/reset_all_motor_speeds')
def vgr_reset_all_motor_speeds() -> [None, json]:
    """
        Resets all the motor speeds for the specified machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
        description: >
                    URL **vgr/reset_all_motor_speeds?machine=vgr_1**
                    [Example Link](http://192.168.0.5:5000/vgr/reset_all_motor_speeds?machine=vgr_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_vgr1_getter_setter(request)
        try:
            vgr1_getter_setter_rpc.reset_all_motor_speeds()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/vgr/check_position')
def vgr_check_position() -> [None, json]:
    """
        Checks if the position of the machine matches the queried position
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: position
              in: path
              type: string
              required: true
        description: >
                    URL **vgr/check_position?machine=vgr_1&position=initial**
                    [Example Link](http://192.168.0.5:5000/vgr/check_position?machine=vgr_1&position=initial)
        responses:
            200:
                description: JSON
    """
    check = None
    if request.factory == "1" and request.args.get('position'):
        check_heap_queue_vgr1_getter_setter(request)
        try:
            check = vgr1_getter_setter_rpc.check_position(request.args.get('position'))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"is_at_queried_position": check}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/vgr/status_of_light_barrier')
def vgr_status_of_light_barrier() -> [None, json]:
    """
        Indicates whether a light barrier is broken through or not.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: lb
              in: path
              type: integer
              required: true
              description: number of the light barrier
        description: >
                    URL **vgr/status_of_light_barrier?machine=vgr_1&lb=7**
                    [Example Link](http://192.168.0.5:5000/vgr/status_of_light_barrier?machine=vgr_1&lb=7)
        responses:
            200:
                description: JSON
    """
    status = None
    if request.factory == "1" and request.args.get('lb'):
        check_heap_queue_vgr1_getter_setter(request)
        try:
            status = vgr1_getter_setter_rpc.status_of_light_barrier(int(request.args.get('lb')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_vgr1_getter_setter()
            abort(400,
                  f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_vgr1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"interrupted": status}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


"""
#####################################################################
#####################################################################
################## High-Bay Warehouse ###############################
################# Execution Webservices #############################
#####################################################################
#####################################################################
"""

def _get_status_of_light_barrier_hbw() -> bool:
    """
    Checks whether the light barrier of hbw is interrupted.
    :return: Bool
    """
    url = f"http://127.0.0.1:5000/hbw/status_of_light_barrier?machine=hbw_1" \
          f"&lb=1"
    response = requests.get(url, auth=('user', 'pass'))
    data = response.json()
    status = data['attributes'][0]['interrupted']
    return status

def _hbw_unload_thread(slot) -> None:
    """
    Represents the unload Process Thread.
    :return: Nothing
    """
    requests.get(f"http://127.0.0.1:5000/hbw/unload?machine=hbw_1&slot={slot}", auth=('user', 'pass'))

@app.route('/hbw/calibrate')
def hbw_calibrate() -> [None, json]:
    """
        Moves HBW to start position
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: vgr_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
        description: >
                    URL **hbw/calibrate?motor=2&machine=hbw_1**
                    [Example Link](http://192.168.0.5:5000/hbw/calibrate?motor=2&machine=hbw_1)
        responses:
            200:
                description: JSON
    """
    if request.args.get('motor'):
        motor = request.args.get('motor')
    else:
        motor = None

    if request.factory == "1":
        check_heap_queue_hbw1_execution(request)

        try:
            if motor is None:
                hbw1_execution_rpc.calibrate()
            else:
                hbw1_execution_rpc.calibrate(int(motor))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/hbw/store')
def hbw_store() -> [None, json]:
    """
        Stores a workpiece at a given slot (0-8) in HBW
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: slot
              in: path
              type: integer
              required: true
              description: Number of slot
        description: >
                    URL **hbw/store?slot=2&machine=hbw_1**
                    [Example Link](http://192.168.0.5:5000/hbw/store?slot=2&machine=hbw_1)
        responses:
            200:
                description: JSON
    """
    slot = None
    if request.args.get('slot'):
        slot = str(request.args.get('slot')).split("_")[1]
    color = request.args.get('color')
    if color:
        if request.factory == "1":
            check_heap_queue_hbw1_execution(request)

            try:
                hbw1_execution_rpc.store(int(slot) if slot is not None else "next", color)
            except xmlrpc.client.Fault as rpc_error:
                pop_heap_queue_hbw1_execution()
                abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
            pop_heap_queue_hbw1_execution()
        else:
            abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/hbw/unload')
def hbw_unload() -> [None, json]:
    """
        Unloads a workpiece at a given slot (0-8) in HBW
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: slot
              in: path
              type: integer
              required: true
              description: Number of slot
        description: >
                    URL **hbw/unload?machine=hbw_1&slot=1**
                    [Example Link](http://192.168.0.5:5000/hbw/unload?machine=hbw_1&slot=1)
        responses:
            200:
                description: JSON
    """
    slot = None
    if request.args.get('slot'):
        slot = request.args.get('slot')
    request.factory = "1"
    if request.factory == "1":
        check_heap_queue_hbw1_execution(request)

        try:
            hbw1_execution_rpc.unload(int(slot) if slot is not None else "next")
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route("/hbw/change_buckets")
def hbw_change_buckets() -> [None, json]:
    """
       Swaps two buckets. The parameters slot_one and slot_two take values between (1 - 9).
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: slot_one
              in: path
              type: integer
              required: true
              description: Number of slot1
            - name: slot_two
              in: path
              type: integer
              required: true
              description: Number of slot2
        description: >
                    URL **hbw/change_buckets?machine=hbw_1&slot_one=1&slot_two=2**
                    [Example Link](http://192.168.0.5:5000/hbw/change_buckets?machine=hbw_1&slot_one=1&slot_two=2)
        responses:
            200:
                description: JSON
    """
    slot_1 = None
    slot_2 = None

    if request.args.get('slot_one'):
        slot_1 = str(request.args.get('slot_one')).split("_")[0]
    if request.args.get('slot_two'):
        slot_2 = str(request.args.get('slot_two')).split("_")[0]
    if request.factory == "1" and request.args.get("slot_one") and request.args.get("slot_two"):
        check_heap_queue_hbw1_execution(request)

        try:
            hbw1_execution_rpc.change_buckets(int(slot_1) - 1,
                                              int(slot_2) - 1)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_execution()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_execution()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)

@app.route("/hbw/get_workpiece_by_color")
def hbw_get_workpiece_by_color() -> [None, json]:
    """
       Unloads workpiece from HBW by workpiece color
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: color
              in: path
              type: string
              required: true
              description: Color of workpiece
        description: >
                    URL **hbw/get_workpiece_by_color?color=red&machine=hbw_1**
                    [Example Link](http://192.168.0.5:5000/hbw/get_workpiece_by_color?color=red&machine=hbw_1)
        responses:
            200:
                description: JSON
    """
    color = request.args.get('color')
    if color:
        requests.get(f"http://127.0.0.1:5000/hbw/calibrate?machine=hbw_1", auth=('user', 'pass'))
        requests.get(f"http://127.0.0.1:5000/vgr/calibrate?machine=vgr_1", auth=('user', 'pass'))
        response = requests.get(f"http://127.0.0.1:5000/hbw/get_slot_number_of_workpiece_by_color?color={color}&machine=hbw_1")
        data = response.json()
        slot = data['attributes'][0]['slot_number']
        if slot == -1:
            error = f"No Workpiece with color {color} available"
            return jsonify(error=str(error)), 500

        Thread(target=_hbw_unload_thread, args=(int(slot),)).start()

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)

@app.route("/hbw/wait_until_light_barrier_is_interrupted")
def hbw_wait_until_light_barrier_is_interrupted() -> [None, json]:
    while not _get_status_of_light_barrier_hbw():
        time.sleep(0.5)
        pass
    return jsonify(create_json(request))


"""
#####################################################################
#####################################################################
################## High-Bay Warehouse ###############################
############ Getter and Setter Webservices ##########################
#####################################################################
#####################################################################
"""


@app.route('/hbw/state_of_machine')
def hbw_state_of_machine() -> [None, json]:
    """
       Indicates the state of a machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
        description: >
                    URL **hbw/state_of_machine?machine=hbw_1**
                    [Example Link](http://192.168.0.5:5000/hbw/state_of_machine?machine=hbw_1)
        responses:
            200:
                description: JSON
    """
    state = None
    if request.factory == "1":
        check_heap_queue_hbw1_getter_setter(request)
        try:
            state = hbw1_getter_setter_rpc.state_of_machine(1)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"state": state}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/hbw/status_of_light_barrier')
def hbw_status_of_light_barrier() -> [None, json]:
    """
       Indicates whether a light barrier is broken through or not.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: lb
              in: path
              type: integer
              required: true
              description: Number of light barrier
        description: >
                    URL **hbw/status_of_light_barrier?machine=hbw_1&lb=1**
                    [Example Link](http://192.168.0.5:5000/hbw/status_of_light_barrier?machine=hbw_1&lb=1)
        responses:
            200:
                description: JSON
    """
    status = None
    if request.factory == "1" and request.args.get('lb'):
        check_heap_queue_hbw1_getter_setter(request)
        try:
            status = hbw1_getter_setter_rpc.status_of_light_barrier(int(request.args.get('lb')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"interrupted": status}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/hbw/get_motor_speed')
def hbw_get_motor_speed() -> [None, json]:
    """
       Gets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
        description: >
                    URL **hbw/get_motor_speed?machine=hbw_1&motor=1**
                    [Example Link](http://192.168.0.5:5000/hbw/get_motor_speed?machine=hbw_1&motor=1)
        responses:
            200:
                description: JSON
    """
    motor_speed = None
    if request.factory == "1" and request.args.get('motor'):
        check_heap_queue_hbw1_getter_setter(request)
        try:
            motor_speed = hbw1_getter_setter_rpc.get_motor_speed(int(request.args.get('motor')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"motor_speed": motor_speed}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)


@app.route('/hbw/set_motor_speed')
def hbw_set_motor_speed() -> [None, json]:
    """
       Sets the motor speed for the specified motor
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: motor
              in: path
              type: integer
              required: true
              description: Number of motor
            - name: speed
              in: path
              type: integer
              required: true
        description: >
                    URL **hbw/set_motor_speed?machine=hbw_1&motor=1&speed=400**
                    [Example Link](http://192.168.0.5:5000/hbw/set_motor_speed?machine=hbw_1&motor=1&speed=400)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1" and request.args.get('motor') and request.args.get('speed'):
        check_heap_queue_hbw1_getter_setter(request)
        try:
            hbw1_getter_setter_rpc.set_motor_speed(int(request.args.get('motor')), int(request.args.get('speed')))
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/hbw/reset_all_motor_speeds')
def hbw_reset_all_motor_speeds() -> [None, json]:
    """
       Resets all the motor speeds for the specified machine
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
        description: >
                    URL **hbw/reset_all_motor_speeds?machine=hbw_1**
                    [Example Link](http://192.168.0.5:5000/hbw/reset_all_motor_speeds?machine=hbw_1)
        responses:
            200:
                description: JSON
    """
    if request.factory == "1":
        check_heap_queue_hbw1_getter_setter(request)
        try:
            hbw1_getter_setter_rpc.reset_all_motor_speeds()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    if request and request.method == "GET":
        return jsonify(create_json(request))
    else:
        abort(404)


@app.route('/hbw/get_amount_of_stored_workpieces')
def hbw_amount_of_stored_workpieces() -> [None, json]:
    """
       Returns the number of stored workpieces.
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
        description: >
                    URL **hbw/get_amount_of_stored_workpieces?machine=hbw_1**
                    [Example Link](http://192.168.0.5:5000/hbw/get_amount_of_stored_workpieces?machine=hbw_1)
        responses:
            200:
                description: JSON
    """
    number = None
    if request.factory == "1":
        check_heap_queue_hbw1_getter_setter(request)
        try:
            number = hbw1_getter_setter_rpc.get_amount_of_stored_workpieces()
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"number": number}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)

@app.route('/hbw/get_slot_number_of_workpiece_by_color')
def hbw_get_slot_number_of_workpiece_by_color() -> [None, json]:
    """
       Returns the number of slot where a workpiece with given color is stored
        ---
        parameters:
            - name: machine
              in: path
              type: string
              required: true
              description: hbw_1
            - name: color
              in: path
              type: string
              required: true
        description: >
                    URL **hbw/get_slot_of_workpiece_by_color?color=red**
                    [Example Link](http://192.168.0.5:5000/hbw/get_slot_of_workpiece_by_color?color=red)
        responses:
            200:
                description: JSON
    """
    slot_number = None
    if request.factory == "1" and request.args.get('color'):
        check_heap_queue_hbw1_getter_setter(request)
        color = request.args.get('color')
        try:
            slot_number = hbw1_getter_setter_rpc.get_slot_number_of_workpiece_by_color(color)
        except xmlrpc.client.Fault as rpc_error:
            pop_heap_queue_hbw1_getter_setter()
            abort(400, f"The machine controller of the addressed machine encountered an error: {rpc_error.faultString}")
        pop_heap_queue_hbw1_getter_setter()
    else:
        abort(404, "Please make sure that the value of the parameter for the machine is 1")

    args = {"slot_number": slot_number}

    if request and request.method == "GET":
        return jsonify(create_json(request, args))
    else:
        abort(404)
"""
#####################################################################
#####################################################################
############## Environment and Camera (SSC) #########################
################# Execution Webservices #############################
#####################################################################
#####################################################################
"""

# TODO: implement

"""
#####################################################################
#####################################################################
############## Environment and Camera (SSC) #########################
############ Getter and Setter Webservices ##########################
#####################################################################
#####################################################################
"""
# TODO: implement

"""
####################################################################
################## favicon handling ################################
########## Browsers like Chrome ask for URL  #######################
######## /favicon.ico when they reload a page ######################
######## this webservice prevents it from raising an 404 error #####
####################################################################
"""


@app.route('/favicon.ico')
def handle_favicon():
    # Whenever a browser enters an URL this function gets called once the webservice finishes
    abort(404)


"""
####################################################################
#################### Start the App #################################
####################################################################
"""


def connect_to_sm1_execution_rpc():
    global sm1_execution_rpc
    try:
        sm1_execution_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:8014/")
        print(sm1_execution_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to sm1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_sm1_execution_rpc()


def connect_to_mm1_execution_rpc():
    global mm1_execution_rpc
    try:
        mm1_execution_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:8011/")
        print(mm1_execution_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to mm1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_mm1_execution_rpc()


def connect_to_ov1_execution_rpc():
    global ov1_execution_rpc
    try:
        ov1_execution_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:8015/")
        print(f"{ov1_execution_rpc.is_connected()} - Oven")
    except ConnectionRefusedError:  # as err:
        print("cannot connect to ov1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_ov1_execution_rpc()


def connect_to_wt1_execution_rpc():
    global wt1_execution_rpc
    try:
        wt1_execution_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:8415/")
        print(f"{wt1_execution_rpc.wt_is_connected()} - WT")
    except ConnectionRefusedError:  # as err:
        print("cannot connect to wt1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_wt1_execution_rpc()


def connect_to_vgr1_execution_rpc():
    global vgr1_execution_rpc
    try:
        vgr1_execution_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:8013/")
        print(vgr1_execution_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to vgr1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_vgr1_execution_rpc()


def connect_to_hbw1_execution_rpc():
    global hbw1_execution_rpc
    try:
        hbw1_execution_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:8012/")
        print(hbw1_execution_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to hbw1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_hbw1_execution_rpc()


def connect_to_sm1_getter_setter_rpc():
    global sm1_getter_setter_rpc
    try:
        sm1_getter_setter_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:7014/")
        print(sm1_getter_setter_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to sm1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_sm1_getter_setter_rpc()


def connect_to_mm1_getter_setter_rpc():
    global mm1_getter_setter_rpc
    try:
        mm1_getter_setter_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:7011/")
        print(mm1_getter_setter_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to mm1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_mm1_getter_setter_rpc()


def connect_to_ov1_getter_setter_rpc():
    global ov1_getter_setter_rpc
    try:
        ov1_getter_setter_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:7015/")
        print(f"{ov1_getter_setter_rpc.is_connected()} - Oven")
    except ConnectionRefusedError:  # as err:
        print("cannot connect to ov1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_ov1_getter_setter_rpc()


def connect_to_wt1_getter_setter_rpc():
    global wt1_getter_setter_rpc
    try:
        wt1_getter_setter_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:7615/")
        print(f"{wt1_getter_setter_rpc.wt_is_connected()} - WT")
    except ConnectionRefusedError:  # as err:
        print("cannot connect to wt1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_wt1_getter_setter_rpc()


def connect_to_vgr1_getter_setter_rpc():
    global vgr1_getter_setter_rpc
    try:
        vgr1_getter_setter_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:7013/")
        print(vgr1_getter_setter_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to vgr1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_vgr1_getter_setter_rpc()


def connect_to_hbw1_getter_setter_rpc():
    global hbw1_getter_setter_rpc
    try:
        hbw1_getter_setter_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:7012/")
        print(hbw1_getter_setter_rpc.is_connected())
    except ConnectionRefusedError:  # as err:
        print("cannot connect to hbw1 rpc server - sleeping for 2 seconds before trying to connect again.")
        time.sleep(2)
        connect_to_hbw1_getter_setter_rpc()

if __name__ == '__main__':
    thread_list = [
        Thread(target=connect_to_hbw1_execution_rpc),
        Thread(target=connect_to_mm1_execution_rpc),
        Thread(target=connect_to_ov1_execution_rpc),
        Thread(target=connect_to_sm1_execution_rpc),
        Thread(target=connect_to_vgr1_execution_rpc),
        Thread(target=connect_to_wt1_execution_rpc),
        Thread(target=connect_to_hbw1_getter_setter_rpc),
        Thread(target=connect_to_mm1_getter_setter_rpc),
        Thread(target=connect_to_ov1_getter_setter_rpc),
        Thread(target=connect_to_sm1_getter_setter_rpc),
        Thread(target=connect_to_vgr1_getter_setter_rpc),
        Thread(target=connect_to_wt1_getter_setter_rpc),
    ]

    [thread.start() for thread in thread_list]
    [thread.join() for thread in thread_list]

    app.run(host='0.0.0.0')
