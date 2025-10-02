# logic.py
import pyspark
import sklearn
import importlib
import inspect
import pkgutil
import pandas as pd

def for_functions_or_methods(stack_element, choice):
    module = stack_element[0]
    class_name = stack_element[2]
    func_name = stack_element[1]
    if class_name:
        cls = getattr(module, class_name)
        func = getattr(cls, func_name)
    else:
        func = getattr(module, func_name)

    signature = inspect.signature(func)
    dct = {}

    if choice is None:
        sample = []
        for name, param in signature.parameters.items():
            sample.append(name)
        return sample
    for name, param in signature.parameters.items():
        dct[name] = [
            f"kind : {str(param.kind).replace("Parameter.", "")}",
            f"default : {param.default if param.default is not inspect._empty else None}",
            f"annotation : {param.annotation if param.annotation is not inspect._empty else None}"]
    return dct[choice]



def for_classes(stack_element, choice):
    module = stack_element[0]
    cls = getattr(module, stack_element[1])
    if inspect.isfunction(cls):
        return for_functions_or_methods(stack_element, choice)
    
    variables = []
    methods = []
    special_attributes = []
    if choice is None:
        return ["Variable", "Method", "Special_attribute"]
        
    for name in dir(cls):
        if name.startswith("__") and name.endswith("__"):
            special_attributes.append(name)
        elif name.startswith("_"):
            continue
        else:
            attr = getattr(cls, name)
            if inspect.isfunction(attr) or inspect.ismethod(attr) or callable(attr):
                methods.append(name)
            else:
                variables.append(name)

    dct = {
         "Special_attribute" : special_attributes,
         "Variable" : variables,
         "Method" : methods
     }
    return dct[choice]



def for_module(stack_element, choice):
    variables = []
    functions = []
    classes = []
    special_attributes = []

    if choice is None:
        return ["Variable", "Function", "Class", "Special_attribute"]
    for name in dir(stack_element[0]):
        obj = getattr(stack_element[0], name)
        if name.startswith("__") and name.endswith("__"):
            special_attributes.append(name)
        elif name.startswith("_"):
            continue
        elif inspect.isclass(obj):
            classes.append(name)
        elif inspect.isfunction(obj) or inspect.isbuiltin(obj):
            functions.append(name)
        else:
            variables.append(name)

    dct ={
        "Variable" : variables,
        "Function" : functions,
        "Class" : classes,
        "Special_attribute" : special_attributes
    }
    return dct[choice]



def for_package(stack_element, choice):
    imported = stack_element[0]
    if not hasattr(imported, "__path__"):
        return for_module(stack_element, choice)
    package = []
    module = []
    
    if choice is None:
        return ["Package", "Module"]
    for loader, name, is_pkg in pkgutil.iter_modules(imported.__path__):
        if name.startswith("_"):
            continue
        elif is_pkg:
            package.append(name)
        else:
            module.append(name)
    dct = {
        "Package" : package,
        "Module" : module
    }
    return dct[choice]
    


def run_engine(stack_element, choice):
    stack_element[0] = importlib.import_module(stack_element[0])

    if len(stack_element) == 1:
        return for_package(stack_element, choice)
    elif len(stack_element) == 2:
        return for_classes(stack_element, choice)
    elif len(stack_element) == 3:
        return for_functions_or_methods(stack_element, choice)



# UI reset
stack = []
options = [[]]

def get_path():
    global stack
    if len(stack) != 0:
        x = stack[-1]
        l = len(x)
        if l == 1:
            return f"{x[0]}"
        elif l == 2:
            return f"{x[0]} ---> {x[1]}"
        else:
            return f"{x[0]} ---> {x[2]} ---> {x[1]}"
    else:
        return ""


def get_options():
    global options
    return options[-1]

    
def reset():
    global stack
    stack = []
    global options
    options = [[]]
    global helper
    helper = [[], [], []]


def get_input_list(helper):
    input_list = []
    package_module = ".".join(helper[0])
    input_list.append(package_module)

    if len(helper[1]) != 0:
        input_list.append(helper[1][0])
        if len(helper[2]) != 0:
            input_list.append(helper[2][0])
        else:
            input_list.append(None)
    else:
        if len(helper[2]) != 0:
            input_list.append(helper[2][0])
    return input_list


def update_options(choice):
    global options
    x = run_engine(stack[-1].copy(), choice)
    options.append(x)


# globals
helper = [[], [], []]   # package_module, functions/methods, class
index = 0
def new_positive_update(stack_element):
    global index
    global stack
    global helper
    flag = True
    
    if stack_element in ["Package", "Module", "Function", "Method", "Class", "Variable", "Special_attribute"]:
        if (stack_element == "Package") or (stack_element == "Module"):
            index = 0
        elif (stack_element == "Function") or (stack_element == "Method"):
            index = 1
        elif stack_element == "Class":
            index = 2
        else:
            index = -1
        choice = stack_element
    else:
        choice = None
        if index == -1:
            flag = False
        elif index == -2:
            return
        else:
            if len(helper[1]) > 0:
                choice = stack_element
                index = -2
            else:
                helper[index].append(stack_element)
            
    if flag:
        input_list = get_input_list(helper)
        stack.append(input_list)
        update_options(choice)


def new_negative_update():
    global options
    global stack
    global helper
    
    if len(options) > 2:
        options.pop()
        stack.pop()
        x = stack[-1]
        
        helper[0] = x[0].split(".")
        if len(x) == 1:
            helper[1] = []
            helper[2] = []
        elif len(x) == 2:
            helper[1] = [x[1]]
            helper[2] = []
        elif len(x) == 3:
            helper[1] = [x[1]]
            helper[2] = [x[2]]

def start_engine(stack_element):
    global stack
    global helper
    helper[0].append(stack_element)
    stack.append([stack_element])
    update_options(None)
