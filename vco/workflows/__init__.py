import simple

__implems = {'simple.sleep': simple.Sleep}

def getWorkflowImplementation(id):
    return __implems.get(id)
