import simple

__implems = {'93909145-b009-11df-8d4e-f92a4bb8cbd5': simple.Sleep}

def getWorkflowImplementation(_id):
    return __implems.get(_id)()
