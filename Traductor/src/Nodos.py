from MemoryOperations import * 

class AST():
    def __init__(self, root_node):
        self.root_node = root_node

    # Python execution of the source code
    def execute(self, debug=False):
        stack = []
        global_variables = dict()
        root_value = self.root_node.execute(stack, global_variables)[0]

        print("\nProgram finished with exit code "+str(root_value))
        if debug:
            print("\n\n\n***DEBUG INFO***\nVariables in memory:")
            print("Global variables memory state:")
            print(global_variables)
            print("\nStack state:")
            print(stack)

    # Convert the source code to object code (X86)
    def compile(self):
        offset_table = dict()
        object_code = ""
        object_code = self.root_node.compile(offset_table, object_code)

        print("***OBJECT CODE BEGIN***")
        print(object_code)
        print("***OBJECT CODE END***")

class Node():
    def execute(self, stack, global_variables):
        """
        TODO
        Este return None, False se añadió el lunes del puente de la
        Constitución a las 23:46, con todo lo que eso implica,  para
        solucionar el problema de que las funciones sin return dieran error.
        El error era provocado porque al no haber return, se ejecutan
        todos los StatementNodes hasta el final, y el código del último
        StatementNode siempre es Node() dado que así se marca el final
        de un statement_list. Al ejecutarse el execute() de Node, se 
        devolvía un objeto None, cuando lo que normalmente se espera es
        un par (valor, flag) para acceder al primer elemento y recoger
        el valor de retorno de la llamada a la función. Esto es lo que
        provocaba el error, y se ha parcheado de esta forma tan simple.
        """
        return None, False 

class StatementNode(Node):
    def __init__(self, left_node, right_node):
        self.left_node = left_node
        self.right_node = right_node

    def execute(self, stack, global_variables):
        statement_code_output = self.left_node.execute(stack, global_variables)
        statement_code_return_value = statement_code_output[0]
        statement_code_return_flag = statement_code_output[1]

        if statement_code_return_flag:
            return statement_code_return_value, statement_code_return_flag
        else:
            return self.right_node.execute(stack, global_variables)

class FunctionDefinitionNode(Node):
    def __init__(self, function_type_node, function_id_node, parameter_list_node, function_code_block):
        self.function_type_node = function_type_node
        self.function_id_node = function_id_node
        self.parameter_list_node = parameter_list_node
        self.function_code_block = function_code_block

    def execute(self, stack, global_variables):
        function_id = self.function_id_node.execute(stack, global_variables)
        parameter_list = self.parameter_list_node.execute(stack, global_variables)

        global_variables[function_id] = (parameter_list, self.function_code_block)

        return None, False

class FunctionCallNode(Node):
    def __init__(self, function_id_node, argument_list_node):
        self.function_id_node = function_id_node
        self.argument_list_node = argument_list_node

    def execute(self, stack, global_variables):
        function_id = self.function_id_node.execute(stack, global_variables)
        argument_list = self.argument_list_node.execute(stack, global_variables)

        function_definition = global_variables[function_id]
        parameter_list = function_definition[0]
        function_code_block = function_definition[1]

        if len(argument_list) != len(parameter_list):
            raise Exception("Argument list length doesnt match parameter list length")

        local_variables = dict()
        for i in range(len(argument_list)):
            #TODO: check types? they are ignored right now (parameter_list[i][1])
            local_variables[parameter_list[i][1]] = argument_list[i].execute(stack, global_variables)

        # prologue
        stack_copy = stack
        stack = list()
        stack.append(local_variables)

        function_return_value = function_code_block.execute(stack, global_variables)[0]

        # epilogue
        stack = stack_copy

        return function_return_value

class SelectionStatementNode(Node):
    def __init__(self, expr_node, if_code_block_node, else_code_block_node):
        self.expr_node = expr_node
        self.if_code_block_node = if_code_block_node
        self.else_code_block_node = else_code_block_node

    def execute(self, stack, global_variables):
        expr_node_output = self.expr_node.execute(stack, global_variables)
        stack.append(dict())    # creates a new scope

        if expr_node_output:
            code_block_output = self.if_code_block_node.execute(stack, global_variables)
        else:
            code_block_output = self.else_code_block_node.execute(stack, global_variables)

        stack.pop() # deletes variables created in the new scope

        code_block_return_value = code_block_output[0]
        code_block_return_flag = code_block_output[1]

        return code_block_return_value, code_block_return_flag

class WhileStatementNode(Node):
    def __init__(self, expr_node, code_block):
        self.expr_node = expr_node
        self.code_block = code_block

    def execute(self,stack, global_variables):
        cond_while = self.expr_node.execute(stack, global_variables)
        code_block_output = None

        stack.append(dict())    # creates a new scope
        while cond_while:
            self.code_block.execute(stack, global_variables) 
            code_block_output = self.code_block.execute(stack, global_variables)
            cond_while = self.expr_node.execute(stack, global_variables)

        stack.pop() # deletes variables created in the new scope

        if code_block_output != None:
            code_block_return_value = code_block_output[0]
            code_block_return_flag = code_block_output[1]
        else:
            code_block_return_value = None
            code_block_return_flag = False

        return code_block_return_value, code_block_return_flag


class ReturnNode(Node):
    def __init__(self, expr_node):
        self.expr_node = expr_node

    def execute(self, stack, global_variables):
        expr_value = self.expr_node.execute(stack, global_variables)

        return expr_value, True

# Container class statements formed by just an expressions.
# Returns false because is not a return expression.
class ExpressionNode(Node):
    def __init__(self, expr_node):
        self.expr_node = expr_node

    def execute(self, stack, global_variables):
        expr_value = self.expr_node.execute(stack, global_variables)
        return expr_value, False

class GlobalDefinitionNode(Node):
    def __init__(self, variable_type, variable_id_node, variable_value_node):
        self.variable_type = variable_type  #TODO: no es un node?
        self.variable_id_node = variable_id_node
        self.variable_value_node = variable_value_node

    def execute(self, stack, global_variables):
        # TODO: types are ignored right now. If they were to be included, changes would affect
        # all the memory operations
        variable_identifier = self.variable_id_node.execute(stack, global_variables)
        variable_value = self.variable_value_node.execute(stack, global_variables)

        global_variables[variable_identifier] = variable_value

        return variable_value, False

class MainCallNode(Node):
    def __init__(self, code_block_node):
        self.code_block_node = code_block_node

    def execute(self, stack, global_variables):
        stack.append(dict())
        return_value = self.code_block_node.execute(stack, global_variables)[0]
        stack.pop()

        return return_value, True   # TODO: puede que esto sea cuestionable

class VariableDefinitionNode(Node):
    def __init__(self, variable_type, variable_id_node, variable_value_node):
        self.variable_type = variable_type  #TODO: no es un node?
        self.variable_id_node = variable_id_node
        self.variable_value_node = variable_value_node

    def execute(self, stack, global_variables):
        # TODO: types are ignored right now. If they were to be included, changes would affect
        # all the memory operations
        variable_identifier = self.variable_id_node.execute(stack, global_variables)
        variable_value = self.variable_value_node.execute(stack, global_variables)

        # TODO: types are ignored right now. If they were to be included, changes would affect
        # all the memory operations
        stack[-1][variable_identifier] = variable_value

        return variable_value, False

 #  ___     __   ___  
 # |_ _|   / /  / _ \ 
 #  | |   / /  | (_) |
 # |___| /_/    \___/ 
                    
class IO_OpNode(Node):
    def __init__(self, argument_list_node):
        self.argument_list_node = argument_list_node

    def function_name(self):
        pass

    def execute(self, stack, global_variables):
        arglist = self.argument_list_node.execute(stack, global_variables)
        evaluated_arglist = []

        if len(arglist) == 0:
            raise Exception("error: too few arguments to function {}".format(self.function_name()))
    
        for i in range(len(arglist)):
            evaluated_arglist.append(arglist[i].execute(stack, global_variables))

        self.execute_aux(evaluated_arglist[0], evaluated_arglist[1:], stack, global_variables)
        return None, False

    # Method to be overloaded by its class childs
    def execute_aux(self, string_format, arglist, stack, global_variables):
        pass

    def compile(self, offset_table,execution_variables):   
        string_format = self.left_node.execute(execution_variables)
        arglist = self.right_node.execute(execution_variables)
        
        #print("estoy en compile")
        return self.compile_aux(string_format,arglist,execution_variables)

    # Method to be overloaded by its class childs
    def compile_aux(self, offset_table,execution_variables):
        pass

class PrintfNode(IO_OpNode):
    def function_name(self):
        return "printf"

    def execute_aux(self, string_format, arglist, stack, global_variables):
        if len(arglist) == 0:
            print(string_format)
        else:
            i = 0
            j = 0
            string_to_print = ""

            while i < len(string_format):
                if string_format[i] == '%':
                    string_to_print += str(arglist[j])
                    j += 1
                    i += 1     # ignore character %d
                else:
                    string_to_print += str(string_format[i])
                i += 1
            print(string_to_print)

    def compile_aux(self,string_format, arglist,execution_variables):
        if len(arglist) == 0:
            #print("Variables: "+execution_variables)
            return "push $s0\ncall printf \n"+string_format+"\naddl $8, %esp"
        else:
            cad =""
            cont =1
            i = 0
            while cont < len(arglist):
                ind = list(execution_variables).index(arglist[i])  #primero tenemos que ver en posicion de la pila esta la variable
                ind = (ind+1)*4 #porque siempre empieza en 0, por lo q sumamos un
                cad = cad +"pushl -"+ str(ind)+"(%ebp)\n"
                cont = cont+1
                i=i+1
            aux = 0
            if len(string_format) > 0:
                cad = cad + "pushl $s0\n"
                aux = aux+4
            cad = cad + "call printf\n"
            aux = len(arglist)*4 + aux
            cad = cad + "addl $"+str(aux)+",%esp\n"
            return cad

class ScanfNode(IO_OpNode):
    def function_name(self):
        return "scanf"

    def execute_aux(self, string_format, arglist, stack, global_variables):
        i = 0
        j = 0
        while i < len(string_format):
            if string_format[i] == '%':
                input_value = input("")
                modify_variable_in_memory(arglist[j], input_value, stack, global_variables)
                j += 1
                i += 1
            i += 1

    def compile_aux(self,string_format, arglist,execution_variables):
            cad =""
            cont =1
            i = 0
            while cont < len(arglist):
                ind = list(execution_variables).index(arglist[i])  #primero tenemos que ver en posicion de la pila esta la variable
                ind = (ind+1)*4 #porque siempre empieza en 0, por lo q sumamos un
                cad = cad +"pushl -"+ str(ind)+"(%ebp)\n"
                cont = cont+1
                i=i+1
            aux = 0
            if len(string_format) > 0:
                cad = cad + "pushl $s0\n"
                aux = aux+4
            cad = cad + "call scanf\n"
            aux = len(arglist)*4 + aux
            cad = cad + "addl $"+str(aux)+",%esp\n"
            return cad

 #   ___   _                            
 #  | _ ) (_)  _ _    __ _   _ _   _  _ 
 #  | _ \ | | | ' \  / _` | | '_| | || |
 #  |___/ |_| |_||_| \__,_| |_|    \_, |
 #                                 |__/ 
 #   ___                              _                    
 #  / _ \   _ __   ___   _ _   __ _  | |_   ___   _ _   ___
 # | (_) | | '_ \ / -_) | '_| / _` | |  _| / _ \ | '_| (_-<
 #  \___/  | .__/ \___| |_|   \__,_|  \__| \___/ |_|   /__/
 #         |_|                                             

class BinaryOpNode(Node):
    def __init__(self, left_node, right_node):
        self.left_node = left_node
        self.right_node = right_node

    def execute(self, stack, global_variables):
        left_node_value = self.left_node.execute(stack, global_variables)
        right_node_value = self.right_node.execute(stack, global_variables)

        return self.execute_aux(left_node_value, right_node_value, stack, global_variables)

    # Method to be overloaded by its class childs
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):            
        pass

    def compile(self, offset_table, object_code):
        left_node_code = self.left_node.compile(offset_table, object_code)

        right_node_code = self.right_node.compile(offset_table, object_code)

        return ''.join((left_node_code,
                       "pushl %eax\n\n",
                       right_node_code,
                       self.compile_aux(offset_table, object_code))) 

 #    _               _                                      _   
 #   /_\    ___  ___ (_)  __ _   _ _    _ __    ___   _ _   | |_ 
 #  / _ \  (_-< (_-< | | / _` | | ' \  | '  \  / -_) | ' \  |  _|
 # /_/ \_\ /__/ /__/ |_| \__, | |_||_| |_|_|_| \___| |_||_|  \__|
 #                       |___/                                   

class AssignBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        modify_variable_in_memory(left_node_value, right_node_value, stack, global_variables)
        return right_node_value

#    _           _   _     _                    _     _      
#   /_\    _ _  (_) | |_  | |_    _ __    ___  | |_  (_)  __ 
#  / _ \  | '_| | | |  _| | ' \  | '  \  / -_) |  _| | | / _|
# /_/ \_\ |_|   |_|  \__| |_||_| |_|_|_| \___|  \__| |_| \__|

class AddBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value + right_node_value

    def compile_aux(self, offset_table, object_code):
        return "movl %eax, %ebx\npopl %eax\naddl %ebx, %eax\n\n"

class SubtractBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value - right_node_value

    def compile_aux(self, offset_table, object_code):
        return "movl %eax, %ebx\npopl %eax\nsubl %ebx, %eax\n\n"

class MultiplyBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value * right_node_value

    def compile_aux(self, offset_table, object_code):
        return "movl %eax, %ebx\npopl %eax\nimull %ebx, %eax\n\n"

class DivideBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value / right_node_value

    def compile_aux(self, offset_table, object_code):
        return "movl %eax, %ebx\npopl %eax\ncdq\nidvl %ebx\n\n"

 #   ___                                     _                   
 #  / __|  ___   _ __    _ __   __ _   _ _  (_)  ___  ___   _ _  
 # | (__  / _ \ | '  \  | '_ \ / _` | | '_| | | (_-< / _ \ | ' \ 
 #  \___| \___/ |_|_|_| | .__/ \__,_| |_|   |_| /__/ \___/ |_||_|
 #                      |_|                                      
class LessBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value < right_node_value

class LessEqualBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value <= right_node_value

class GreaterBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value > right_node_value

class GreaterEqualBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value >= right_node_value

class EqualBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value == right_node_value

class NotEqualBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value != right_node_value

 #  _                   _               _ 
 # | |     ___   __ _  (_)  __   __ _  | |
 # | |__  / _ \ / _` | | | / _| / _` | | |
 # |____| \___/ \__, | |_| \__| \__,_| |_|
 #              |___/                     

class OrBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value or right_node_value

class AndBinaryOpNode(BinaryOpNode):
    def execute_aux(self, left_node_value, right_node_value, stack, global_variables):
        return left_node_value and right_node_value


 #  _   _                            
 # | | | |  _ _    __ _   _ _   _  _ 
 # | |_| | | ' \  / _` | | '_| | || |
 #  \___/  |_||_| \__,_| |_|    \_, |
 #                              |__/ 

class UnaryOpNode(Node):
    def __init__(self, node):
        self.node = node

    def execute(self, stack, global_variables):
        node_value = self.node.execute(stack, global_variables)
        return self.execute_aux(node_value, stack, global_variables)
    
    # Method to be overloaded by its class childs
    def execute_aux(self, node_value, stack, global_variables):
        pass

class PlusUnaryOpNode(UnaryOpNode):
    def execute_aux(self, node_value, stack, global_variables):
        return +node_value             

class NegationUnaryOpNode(UnaryOpNode):
    def execute_aux(self, node_value, stack, global_variables):
        return -node_value             

class NotUnaryOpNode(UnaryOpNode):
    def execute_aux(self, node_value, stack, global_variables):
        return not node_value             

class AddressOfUnaryOpNode(UnaryOpNode):
    def execute_aux(self, node_value, stack, global_variables):
        return node_value             

 # __   __         _                   
 # \ \ / /  __ _  | |  _  _   ___   ___
 #  \ V /  / _` | | | | || | / -_) (_-<
 #   \_/   \__,_| |_|  \_,_| \___| /__/
                                     
class ValueNode(Node):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return "ValueNode: " + str(self._value)

    def execute(self, stack, global_variables):
        return self._value

    # Cte (NUM segun diapo 49)
    def compile(self, offset_table, object_code):
        return "movl $" + str(self._value) + ", %eax\n\n"

class IdNode(Node):
    def __init__(self, id):
        self._id = id

    def execute(self, stack, global_variables):
        return self._id

class IdValueNode(Node):
    def __init__(self, id):
        self._id = id

    def __repr__(self):
        return "IdValueNode: " + self._id 

    def get_id(self):
        return self._id

    def execute(self, stack, global_variables):
        return read_variable_in_memory(self._id, stack, global_variables)

    # TODO: corregir esto
    # ID dynamic variable case (por decir alguna)
    def compile(self, offset_table, object_code):
        return "movl -tablaOffset[" + self._id + "](%ebp), %eax\n\n"


if __name__ == '__main__':
    # Ejemplo de 5 * 10 + 20
    sum_node = MultiplyBinaryOpNode(ValueNode(5), ValueNode(10))
    sum_node_2 = AddBinaryOpNode(sum_node, ValueNode(20))
    ast = AST(sum_node_2)
    ast.compile()