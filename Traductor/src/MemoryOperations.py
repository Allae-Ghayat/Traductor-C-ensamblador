def variable_exists_in_memory(variable_identifier, stack, global_variables):
    stack_copy = stack.copy()
    variable_exists = False

    while (len(stack_copy) != 0) and not variable_exists:
        scope_variables = stack_copy.pop()
        if variable_identifier in scope_variables:
            variable_exists = True

    if variable_exists or (variable_identifier in global_variables):
        return True
    else:
        return False

def read_variable_in_memory(variable_identifier, stack, global_variables):
    stack_copy = stack.copy()
    variable_exists = False
    variable_value = None

    while (len(stack_copy) != 0) and not variable_exists:
        scope_variables = stack_copy.pop()
        if variable_identifier in scope_variables:
            variable_exists = True
            variable_value = scope_variables[variable_identifier]

    if variable_exists:
        return variable_value
    elif variable_identifier in global_variables:
        return global_variables[variable_identifier]
    else:
        # TODO: change to a more expressive Exception...
        raise Exception("Variable named {} is not defined.".format(variable_identifier))

# Looks for the variable_identifier, and if its found, modifies it in the scope where it was
# first found.
def modify_variable_in_memory(variable_identifier, new_value, stack, global_variables):
    stack_copy = []
    variable_exists = False

    while (len(stack) != 0) and not variable_exists:
        scope_variables = stack.pop()
        if variable_identifier in scope_variables:
            variable_exists = True
            scope_variables[variable_identifier] = new_value
            stack.append(scope_variables)
        else:
            stack_copy.append(scope_variables)

    # reinsertamos las variables de los ambitos que habiamos ido quitando
    while(len(stack_copy) != 0):
        stack.append(stack_copy.pop())

    if not variable_exists:
        if variable_identifier in global_variables:
            global_variables[variable_identifier] = new_value
        else:
            # TODO: change to a more expressive Exception...
            raise Exception("Variable named {} is not defined.".format(variable_identifier))

