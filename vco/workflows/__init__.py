import simple

__implems = {'simple.sleep': simple.Sleep,
             'simple.wait': simple.Wait}

def getWorkflowImplementation(_id):
    return __implems.get(_id)()
