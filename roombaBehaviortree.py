"""
*
* Roomba Behavior Tree: models the behavior of a roomba vacuum utilizing a
*                       behavior tree structure
*                       by Chase Bosworth
*                       Version: Python 3.5
* Approach: The behavior tree is a directed graph structure who traversal
*           is dependent on the decorator and composite nodes. This
*           implementation utilizes inheritance.
* NOTE: Task functions are shell functions, no route calculation is implemented.
*       For a record of tree traversal, answer "yes" to the prompt to print the
*       activity log. BE ADVISED - the time library has been used, (different
*       tasks take different amounts of time).
*
"""

import time

class BehaviorTree:

    def __init__(self):
        self.head = None
        self.blackboard = Blackboard()

    def set_head(self, head):
        self.head = head

    def run_tree(self, num):
        string = "\nCYCLE: " + str(num+1) + "\n"
        chars = "---------------------------" + "\n"
        self.blackboard.log += string
        self.blackboard.log += chars
        self.head.run()

"""
* Wrapper for the behavior trees (trivial)
"""

class Roomba(BehaviorTree):
    pass

"""
* A class which stores current states of the agent
* an instantiation prompts the user for input in order to initialize the first state
"""
class Blackboard:

    def __init__(self):

        self.battery_level = int(input("Enter battery level: "))
        self.spot = return_tf(input("Enter spot (T/F): "))
        self.general = return_tf(input("Enter general (T/F): "))
        self.dusty_spot = return_tf(input("Enter dusty spot (T/F): "))
        self.home_path = "This is a home path"
        self.running = None
        self.failed = None
        self.success = None
        self.log = str()

"""
* A base class for composite, decorator, condition and task nodes
"""

class BaseNode:

    def __init__(self, kid_list, blackboard):
        self.children = []
        self.children = kid_list.copy()
        self.blackboard = blackboard
        self.name = None

    def update_running(self):
        self.blackboard.running = self
        string = "RUNNING: " + self.name + "\n"
        self.blackboard.log += string

    def update_failed(self):
        self.blackboard.failed = self
        string = "FAILED: " + self.name + "\n"
        self.blackboard.log += string

    def update_success(self):
        self.blackboard.success = self
        string = "SUCCESS: " + self.name + "\n"
        self.blackboard.log += string

    def zap_battery(self, num = None):
        if num == None:
            self.blackboard.battery_level -= 2
            string = "BATTERY LEVEL: " + str(self.blackboard.battery_level) + "\n"
            self.blackboard.log += string
        else:
            self.blackboard.battery_level -= num
            string = "BATTERY LEVEL: " + str(self.blackboard.battery_level) + "\n"
            self.blackboard.log += string

"""
* a base class for different types of composite nodes
* definition: composite nodes indicate the order in which various sub-nodes are executed
"""
class Composite(BaseNode):
    # list of children: conditions, tasks, more composites
    def __init__(self, kid_list, blackboard):
        self.children = []
        self.children = kid_list.copy()
        self.blackboard = blackboard

    def run(self):
        pass

class Priority(Composite):
    # each object is a tuple. node first, then priority

    def run(self):
        self.name = "Priority"
        self.update_running()
        self.children = sorted(self.children, key=lambda tup: tup[1])
        for i in self.children:
            # inherits the appropriate run function
            i[0].run()
        self.update_success()

class Sequence(Composite):
    # left to right but if one fails, it returns failure

    def run(self):
        self.name = "Sequence"
        self.update_running()
        for i in self.children:
            if i.run() == False:
                self.update_failed()
                return False
        self.update_success()
        return True

class Selection(Composite):
    # left to right, only fails if all children fail

    def run(self):
        self.name = "Selection"
        self.update_running()
        fail_list = []
        for i in self.children:
            fail_list.append(i.run())
        for i in fail_list:
            if i:
                return True
        return False

"""
* Base class of task nodes
* definition: task nodes execute the various functions
"""
class Task(BaseNode):
    # the argument is the task function
    def __init__(self, blackboard):
        self.name = None
        self.blackboard = blackboard

    def run(self):
        self.update_running()
        self.zap_battery()
        self.update_success()
        print("Doing", self.name)
        time.sleep(1)
        return True

class FindHome(Task):

    def run(self):
        self.name = "Find Home"
        self.update_running()
        home_path = self.blackboard.home_path
        self.zap_battery()
        self.update_success()
        print("Doing", self.name)
        time.sleep(1)
        return True

class GoHome(Task):

    def run(self):
        self.name = "Go Home"
        self.update_running()
        self.blackboard.home_path = "I'm Home!"
        self.zap_battery()
        self.update_success()
        print("Doing", self.name)
        time.sleep(1)
        return True

class Dock(Task):

    def run(self):
        self.name = "Dock"
        self.update_running()
        chargetime = int(input("How long would you like to charge? (1% per second): "))
        if self.blackboard.battery_level + chargetime > 100:
            chargetime = 100 - self.blackboard.battery_level
            print("Max charge level is 100%. Let's charge", chargetime, "seconds.")
            self.blackboard.battery_level = 100
        else: self.blackboard.battery_level += chargetime
        self.blackboard.log += "BATTERY LEVEL:"+ str(self.blackboard.battery_level)+ "\n"
        self.update_success()
        print("Charging up!")
        for i in range(0,int(chargetime)):
            time.sleep(1)
            print(".")
        print("All charged up and ready to clean!")
        return True

class SpotCleaning(Task):
    def __init__(self, blackboard):
        self.name = "Spot Cleaning"
        self.blackboard = blackboard

    def run(self):
        self.update_running()
        self.zap_battery()
        self.update_success()
        print("Doing", self.name)
        self.blackboard.spot = False
        return True

class DoneSpot(Task):
    def __init__(self, blackboard):
        self.name = "Done Spot"
        self.blackboard = blackboard

class GeneralCleaning(Task):
    def __init__(self, blackboard):
        self.name = "General Cleaning"
        self.blackboard = blackboard


class DoNothing(Task):
    def __init__(self, blackboard):
        self.name = "Do Nothing"
        self.blackboard = blackboard

class DoneGeneral(Task):
    def __init__(self, blackboard):
        self.name = "Done General"
        self.blackboard = blackboard

    def run(self):
        self.update_running()
        self.zap_battery()
        self.update_success()
        print("Doing", self.name)
        self.blackboard.general = False
        return True

"""
* Base class for Decorator nodes
* definition: decorators determine the duration or number of times
* that a task node is executed
"""

class Decorator(BaseNode):
    def __init__(self, task_node, blackboard):
        self.task = task_node
        self.name = None
        self.blackboard = blackboard

    def run(self):
        self.update_running()
        self.task.run()
        self.update_success()
        print("Doing", self.name)
        return True

class Timer(Decorator):

    def __init__(self, task_node, time, blackboard):
        self.task = task_node
        self.name = "Timer"
        self.time = time
        self.blackboard = blackboard

    def run(self):
        self.update_running()
        print("Doing", self.task.name, "for", self.time, "seconds...")
        zap_amount = int(self.time)
        self.zap_battery(zap_amount)
        time.sleep(self.time)
        self.task.run()

class Logical_Negation(Decorator):
    # executes the node then negates the result
    def __init__(self, task_node, blackboard):
        self.task = task_node
        self.name = "Logical Negation"
        self.blackboard = blackboard

    def run(self):
        self.update_running()
        bool_val = self.task.run()
        if bool_val:
            self.update_failed()
            return False
        else:
            self.update_success()
            return True

class Until_Fail(Decorator):
    # execute until the attached node fails
    def __init__(self, task_node, blackboard):
        self.task = task_node
        self.name = "Until Fail"
        self.blackboard = blackboard

    def run(self):
        self.update_running()
        while self.task.run() == True:
            self.task.run()

        self.update_failed()
        return False

class Conditions(BaseNode):

    def __init__(self):
        self.name = None

    # the return of this function determines if the Task Node is executed
class BatteryCheck(Conditions):
    def __init__(self, blackboard):
        self.blackboard = blackboard
        self.name = "Battery Check"

    def run(self):
        if self.blackboard.battery_level < 30:
            self.update_success()
            print("Battery is low!")
            return True
        else:
            print("Battery level is within acceptable range. ")
            self.update_failed()
            return False

class Spot(Conditions):
    def __init__(self, blackboard):
        self.name = "Spot"
        self.blackboard = blackboard

    def run(self):
        if self.blackboard.spot:
            self.update_success()
            print("You selected spot clean!")
            return True
        else:
            self.update_failed()
            return False

class General(Conditions):
    def __init__(self, blackboard):
        self.name = "General"
        self.blackboard = blackboard

    def run(self):
        if self.blackboard.general:
            self.update_success()
            print("You selected general clean!")
            return True
        else:
            self.update_failed()
            return False

class Dusty_Spot(Conditions):
    def __init__(self, blackboard):
        self.name = "Dusty Spot"
        self.blackboard = blackboard

    def run(self):
        if self.blackboard.spot:
            self.update_success()
            print("There's a dusty spot!")
            return True
        else:
            self.update_failed()
            return False

def return_tf(answer):
    if answer == "T":
        return True
    return False


def build_tree(BT):
    """
    * The build tree function builds the tree to the assigment's specification
    * For assignment details and tree diagram, see file
    """
    # Left subtree
    battery = BatteryCheck(BT.blackboard)
    find_home = FindHome(BT.blackboard)
    go_home = GoHome(BT.blackboard)
    dock = Dock(BT.blackboard)
    kid_list1 = [battery, find_home, go_home, dock]

    # Left subtree sequence node
    left_subtree = Sequence(kid_list1, BT.blackboard)

    # middle left subtree
    spot = Spot(BT.blackboard)
    c_s_task = SpotCleaning(BT.blackboard)
    clean_spot = Timer(c_s_task, 20, BT.blackboard)
    done_spot = DoneSpot(BT.blackboard)
    kid_list2 = [spot, clean_spot, done_spot]

    # middle left subtree sequence node
    mid_left_subtree = Sequence(kid_list2, BT.blackboard)

    # middle right subtree (from left to right, from the bottom up)
    d_spot = Dusty_Spot(BT.blackboard)
    clean = SpotCleaning(BT.blackboard)
    tim = Timer(clean, 35, BT.blackboard)
    kid_list3 = [d_spot, tim]
    seq3 = Sequence(kid_list3, BT.blackboard)
    clean2 = GeneralCleaning(BT.blackboard)
    kid_list4 = [seq3, clean2]
    sel = Selection(kid_list4, BT.blackboard)
    battcheck = BatteryCheck(BT.blackboard)
    log_neg_bcheck = Logical_Negation(battcheck, BT.blackboard)
    kid_list5 = [log_neg_bcheck, sel]
    seq4 = Sequence(kid_list5, BT.blackboard)
    until_fail_seq = Until_Fail(seq4, BT.blackboard)
    done_gen = DoneGeneral(BT.blackboard)
    kid_list6 = [until_fail_seq, done_gen]
    seq5 = Sequence(kid_list6, BT.blackboard)
    gen_check = General(BT.blackboard)
    kid_list7 = [gen_check, seq5]
    mid_right_subtree = Sequence(kid_list7, BT.blackboard)
    mid_tree_list = [mid_left_subtree, mid_right_subtree]

    # Middle subtree selection node
    mid_subtree = Selection(mid_tree_list, BT.blackboard)

    # Right subtree

    do_nothing = DoNothing(BT.blackboard)
    right_subtree = do_nothing

    # Behavior Tree root initialization
    priori_tuple_1 = (left_subtree, 1)
    priori_tuple_2 = (mid_subtree, 2)
    priori_tuple_3 = (right_subtree, 3)

    kidlist = [priori_tuple_1, priori_tuple_2, priori_tuple_3]
    priority_root = Priority(kidlist, BT.blackboard)
    BT.set_head(priority_root)

###### DRIVER #######

print("Roomba says, 'Hello there! Just a few questions and I'll get ready to clean!'")
print("              \/\n"
      " ___________  /\n"
      "|           |/\n"
      "|  O     O  |\n"
      "|  \_____/  |\n"
      "|___________|\n"
)
BT = Roomba()
build_tree(BT)

times = int(input("How many times would you like me to cycle? "))
print("Great! I'll get to work right away!")

for i in range(0, times):
    print("Cycle ", str(i+1))
    BT.run_tree(i)
    if i < times - 1:
        update = input("Would you like to change your blackboard settings?(y/n)")
        if update == "y":
            BT.blackboard.spot = return_tf(input("Enter spot (T/F): "))
            BT.blackboard.general = return_tf(input("Enter general (T/F): "))
            BT.blackboard.dusty_spot = return_tf(input("Enter dusty spot (T/F): "))

answer = input("Would you like to print the activity log? (y/n) ")

answer = answer.lower()

if answer == "y":
    print("\n", BT.blackboard.log)
else: print("Ok enjoy your clean house!")


