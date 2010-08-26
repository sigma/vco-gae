import simple

__implems = {'simple.sleep': simple.Sleep}

def getWorkflowImplementation(_id):
    return __implems.get(_id)()
